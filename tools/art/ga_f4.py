"""SkyWynn Foraging armor - F4 tier builder (shared by every F4 tree: Redwood, Fir, Cedar, Poisoned, Spiral). ORIGINAL; no
vanilla or Armory pixels.

PROGRESSION RULE (Skyy 2026-10-09: "... so they start simple and get a little cooler each set you get to that's better"):
same family + fit as F1-F3. F4 = everything F3 has (ga_f3.py: angular plates, bigger layered shoulders, gorget, sap up the
arms; and ga_f2.py: pegs, caps, forked sap, belt boss, crest, knee bosses) PLUS, exactly the same for every F4 tree (approved
ladder: "F4 thorn / spike accents, tall pauldrons, a glowing chest knot, double crest"):
  1. THORNS: heartwood thorn spikes - two on each shoulder cap, two sticking out of each bracer plate
  2. TALL PAULDRONS: an upright guard plate standing on the outer end of each pauldron
  3. a GLOWING CHEST KNOT: a carved knot between the breast plates with glowing sap rings
  4. a DOUBLE CREST: two thorny crest ridges over the helmet instead of one
Room is left for F5 (ornate - gold inlay, glowing gem knots, a winged or tall crown, the brightest sap).
"""
import numpy as np
import ga_paint as P
from ga_paint import SAP
import ga_f2 as F2
import ga_f3 as F3

TIER = "F4_Northern"
profile_plates, profile_hem, mask_crown, chamfer, sap_vein = (F3.profile_plates, F3.profile_hem, F3.mask_crown, F3.chamfer,
                                                              F3.sap_vein)


def build(T):
    """T: an F3-style tree spec (see ga_f3.build)."""
    pieces = F3.build(T)
    BARK, DK, WOOD = T.BARK, T.DK, T.WOOD

    def node(piece, name):
        for n in pieces[piece]:
            if n["name"] == name:
                return n
        raise KeyError(name)

    # 1. thorns
    def p_thorn(F):
        """a tapered heartwood thorn: 3 texels wide at the base, a 1-texel tip; dark outline, lit left edge."""
        F.mat[:] = WOOD
        if F.face in ("front", "back", "left", "right"):
            fb = F.ly - F.ly.min() + 0.5                     # 0.5 .. height-0.5 from the base
            hgt = F.ly.max() - F.ly.min() + 1.0
            a = F.lx if F.face in ("front", "back") else F.lz
            F.alpha &= np.abs(a) < 1.5 * (1 - fb / hgt) + 0.5
            F.val[fb > hgt * 0.6] += 0.12                    # pale tip
            F.val[fb < 1.0] -= 0.12                          # dark base
            e = F.alpha & ~(P._shift(F.alpha, 0, 1) & P._shift(F.alpha, 0, -1))
            F.val[e] -= 0.08
        else:
            F.val -= 0.15

    thorn = dict(size=(3, 6, 3), mat=WOOD, paint=p_thorn, skip=("top",), mirror=True)
    pieces["Chest"] += [
        dict(thorn, name="R-CapThornA", bone="R-Arm", parent="R-PauldronCap", pivot=(-2.5, 4.5, 4.5)),
        dict(thorn, name="R-CapThornB", bone="R-Arm", parent="R-PauldronCap", pivot=(-2.5, 4.5, -4.5)),
    ]
    pieces["Hands"] += [
        dict(thorn, name="R-BracerThornA", bone="R-Forearm", parent="R-BracerPlate", pivot=(-4.0, 2.5, 0), rot=(0, 0, 90)),
        dict(thorn, name="R-BracerThornB", bone="R-Forearm", parent="R-BracerPlate", pivot=(-4.0, -2.5, 0), rot=(0, 0, 90)),
    ]

    # 2. tall pauldrons: an upright guard on the outer end of each pauldron
    def p_guard(F):
        T.base(F, seed=31)
        if F.is_side():
            if F.face in ("left", "right"):
                T.plates(F, F.alpha, 4.0, seed=31)
            chamfer(F, 3.0, faces=("left", "right"), top=True)
            F.mat[(F.v > F.fh - 1) & F.alpha] = DK
            F.val[(F.v > F.fh - 1) & F.alpha] = 0.2
            top = (F.v < 1) & F.alpha
            F.mat[top] = WOOD
            F.val[top] += 0.06
            if F.face in ("left", "right"):
                F2.pegs(F, [(0.0, 0.5)], T, local=True, r=0.8)
        elif F.face == "top":
            F2.sap_line_local(F, 0.0, axis="lx", along="lz", lo=-6.0, hi=6.0)

    pieces["Chest"].append(dict(name="R-PauldronGuard", bone="R-Arm", parent="R-Pauldron", pivot=(-6.0, 6.1, 0),
                                rot=(0, 0, -27), size=(2, 10, 16), mat=BARK, paint=p_guard, mirror=True))

    # 3. glowing chest knot
    def p_knot(F):
        F.mat[:] = WOOD
        if F.face == "front":
            cu, cv = F.fw / 2.0, F.fh / 2.0
            r = np.hypot(F.u - cu, F.v - cv)
            F.alpha &= r < cu + 0.3
            glow = ((np.floor(r) % 2) == 0) & (r < cu - 0.6)
            F.mat[glow] = SAP
            F.val[glow] = 0.16 - 0.03 * r[glow]
            F.lockval[glow] = False
            rim = (r >= cu - 0.9) & F.alpha
            F.mat[rim] = DK
            F.val[rim] = 0.18
        else:
            F.val -= 0.1

    pieces["Chest"].append(dict(name="ChestKnot", bone="Chest", pivot=(0, 3.0, 12.0), size=(7, 7, 2), mat=WOOD, paint=p_knot,
                                skip=("back",)))

    # 4. double crest (two thorny ridges)
    crest = node("Head", "HelmCrest")
    old = crest["paint"]

    def p_crest2(F):
        old(F)
        if F.face in ("left", "right"):
            F.alpha &= ~((F.v < 1.5) & (np.mod(F.lz + 8.0, 4.0) < 2.0))
        elif F.face in ("front", "back"):
            F.mat[:] = WOOD

    pieces["Head"] = [n for n in pieces["Head"] if n["name"] != "HelmCrest"]
    pieces["Head"].append(dict(name="R-HelmCrest", bone="Head", pivot=(-3.5, 20.5, -2.0), size=(2, 4, 16), mat=BARK,
                               paint=p_crest2, mirror=True))
    return pieces
