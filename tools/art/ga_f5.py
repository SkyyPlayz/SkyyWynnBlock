"""SkyWynn Foraging armor - F5 tier builder (shared by every F5 Wastes tree). ORIGINAL; no vanilla or Armory pixels.

PROGRESSION RULE (Skyy 2026-10-09: "... so they start simple and get a little cooler each set you get to that's better"):
same family + fit as F1-F4. F5 = the top tier: everything F4 has (ga_f4.py: thorns, tall pauldron guards, a glowing chest
knot, a double crest; ga_f3.py + ga_f2.py below that) PLUS, exactly the same for every F5 tree (approved ladder: "F5
ornate - gold inlay, glowing gem knots, a winged or tall crown, the brightest sap"):
  1. GOLD INLAY: a thin gold line set just inside the edge of the breast plates, gorget, pauldron guards, bracer plates,
     greaves and the helmet brim
  2. GLOWING GEM KNOTS: the chest knot becomes a big faceted gem in a gold setting; smaller gems on the pauldron guards,
     the knees and the brow (each tree its own gem colour, sampled from its wood)
  3. a WINGED, TALLER CROWN: the crown points stand taller and two swept wings rise from the helmet sides
  4. the BRIGHTEST SAP: every sap line / vein glows a brighter, paler green
Still not bulky: 8 small extra pieces on top of F4.
"""
import numpy as np
import ga_paint as P
from ga_paint import SAP, GOLD, SAPB
import ga_f2 as F2
import ga_f3 as F3
import ga_f4 as F4

TIER = "F5_Wastes"
profile_plates, profile_hem, mask_crown, chamfer, sap_vein = (F3.profile_plates, F3.profile_hem, F3.mask_crown, F3.chamfer,
                                                              F3.sap_vein)
INLAY = ("R-Breast", "GorgetPlate", "R-PauldronGuard", "R-BracerPlate", "R-Greave", "HelmBrim")


def _erode(a):
    return a & P._shift(a, 0, 1) & P._shift(a, 0, -1) & P._shift(a, 1, 0) & P._shift(a, -1, 0)


def inlay(F, inset=1):
    """a 1-texel gold line `inset` texels inside the face's cut-out edge; lit on the top / left runs."""
    if F.face not in ("front", "back", "left", "right") or min(F.fw, F.fh) < 5:
        return
    a = F.alpha.copy()
    for _ in range(inset):
        a = _erode(a)
    ring = a & ~_erode(a)
    ring &= F.mat != SAPB
    F.mat[ring] = GOLD
    lit = ring & ~P._shift(a, 1, 0)
    F.val[ring] = 0.02
    F.val[lit] = 0.14
    F.lockval[ring] = True


def gem_face(F, GEM, setting=True):
    """a faceted glowing gem: bright upper-left facet, deeper lower-right facet, a white glint; gold setting rim."""
    cu, cv = F.fw / 2.0, F.fh / 2.0
    du, dv = (F.u - cu) / max(cu, 1), (F.v - cv) / max(cv, 1)
    d = np.abs(du) + np.abs(dv)
    F.alpha &= d < 1.05
    F.mat[:] = GEM
    F.val[:] = 0.0
    F.val[(du + dv) < -0.1] = 0.22
    F.val[(du + dv) > 0.3] = -0.22
    F.val[(np.abs(du) + np.abs(dv) < 0.35)] = 0.1
    g = (np.floor(F.u) == np.floor(cu - max(1.0, cu * 0.4))) & (np.floor(F.v) == np.floor(cv - max(1.0, cv * 0.4)))
    F.val[g & F.alpha] = 0.5
    if setting:
        rim = F.alpha & (d >= 0.78)
        F.mat[rim] = GOLD
        F.val[rim] = np.where((du + dv)[rim] < 0, 0.12, -0.08)
    F.lockval[F.alpha] = True


def build(T):
    """T: an F4-style tree spec plus GEM (the tree's gem ramp)."""
    pieces = F4.build(T)
    GEM, BARK, WOOD, DK = T.GEM, T.BARK, T.WOOD, T.DK

    # 4. brightest sap everywhere + 1. gold inlay on the listed plates
    for part in pieces.values():
        for n in part:
            old = n["paint"]

            def paint(F, old=old, gold=n["name"] in INLAY):
                old(F)
                F.mat[F.mat == SAP] = SAPB
                if gold:
                    inlay(F)
            n["paint"] = paint

    # 2. gem knots
    def p_chestgem(F):
        if F.face == "front":
            gem_face(F, GEM)
        else:
            F.mat[:] = GOLD
            F.val -= 0.1

    def p_gem(F):
        if F.face == "front":
            gem_face(F, GEM, setting=False)
        else:
            F.mat[:] = GOLD
            F.val[:] = -0.05

    def p_sidegem(F):
        """gem on a face that points sideways (pauldron guard): the gem is on the outward face."""
        if F.face in ("left", "right") and F.n[0] * np.sign(F.x.mean()) > 0.5:
            gem_face(F, GEM, setting=False)
        else:
            F.mat[:] = GOLD
            F.val[:] = -0.05

    for n in pieces["Chest"]:
        if n["name"] == "ChestKnot":
            n.update(size=(9, 9, 2), paint=p_chestgem, mat=GEM)
    pieces["Chest"].append(dict(name="R-GuardGem", bone="R-Arm", parent="R-PauldronGuard", pivot=(-1.4, 0.5, 0), size=(1, 5, 5),
                                mat=GEM, paint=p_sidegem, mirror=True))
    pieces["Legs"].append(dict(name="R-KneeGem", bone="R-Calf", parent="R-Knee", pivot=(0, 0, 1.4), size=(5, 5, 1), mat=GEM,
                               paint=p_gem, skip=("back",), mirror=True))
    pieces["Head"].append(dict(name="BrowGem", bone="Head", pivot=(0, 6.5, 17.4), size=(5, 5, 1), mat=GEM, paint=p_gem,
                               skip=("back",)))

    # 3. winged crown: two swept wings on the helmet sides (shared shape; tree bark + heartwood tips, gold edge, gem vein)
    WING = [
        "..........G",
        ".........GW",
        "........GWW",
        ".......GBWW",
        "......GBBW.",
        ".....GBBBW.",
        "....GBBBW..",
        "...GBBgBW..",
        "..GBBgBBW..",
        ".GBBgBBW...",
        "GBBgBBW....",
        "BBgBBW.....",
        "BgBBW......",
        "gBBW.......",
    ]
    WCOL = {"G": (GOLD, 0.12), "B": (BARK, 0.04), "W": (WOOD, 0.06), "g": (GEM, 0.18)}

    def p_wing(F):
        F2._mask_paint(F, WING, WCOL)
        F.lockval[F.alpha & ((F.mat == GOLD) | (F.mat == GEM))] = True

    pieces["Head"].append(dict(name="R-HelmWing", bone="Head", pivot=(-15.5, 12.0, -2.0), rot=(0, -125, 18), size=(12, 17),
                               offset=(0, 8.5, 0), mat=BARK, paint=p_wing, double=True, mirror=True))
    return pieces
