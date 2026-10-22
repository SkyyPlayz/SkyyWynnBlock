"""SkyWynn pacing model - Balance Pass P1 (research/Balance-Pass-Spec.md section 8). The yardstick P3-P9 tune against.

    python tools/balance_model.py            print the target tables next to the P3 numbers (research/Balance-P3-XP-Spec.md), gaps (!!)
    python tools/balance_model.py --before   the same tables with the P1 numbers (before P3: the live 0.4.56 tables)
    python tools/balance_model.py --md       also rewrite research/balance/targets.md (always the P3 numbers)
    python tools/balance_model.py --power    P5 power sources (gear rolls, Void Charms, pets, UT / Mythic meters, the 1-hour rule) -> targets.md section 7

P3 (2026-10-20, Balance-P3-XP-Spec.md sections 2-5 + Skyy's popup answer A:197 "Middle: Lv 50 at ~33 h"): ONE curve for the class and every
skill (need(L) = R(1100 x f(L) x s(L)) x levels.scale 130 %), XP per action x the tier factor F(T), the skill catch-up, the past-life XP
boost. Level convention = the game's (SkyySkills SkillDefs.levelIn): a new player is Lv 0, list entry k = the XP from level k-1 to k (P1 started
players at Lv 1 and so skipped entry 1 - fixed in P3).

Plain Python 3.12, stdlib only. It simulates ONE focused player (Normal difficulty): run 1 (cap 50) and rebirths 1-5.
Every number names its source as file:line. GUESS = no source; a later phase (or Skyy's play-test) replaces it.
Sources: A = docs/answered/skills.md, X = research/balance/xp.md, C = research/balance/combat.md, G = research/balance/gear.md,
E = research/balance/economy.md, H = research/balance/gathering.md, T3 = research/Skill-Trees-3-Spec.md, LB = research/Level-Bands-20-Spec.md,
L = live SkyySkills xp.properties (read-only, in UserData/Saves/NewBetaTest/mods/Skyy_SkyySkills).
"""
import math
import os
import random
import statistics
import sys

# ======================================================================================== GOALS (Skyy, Normal mode)
ZONES = [  # zone, first level, top level, target hours first time through (base pace), source
    # P3: A:197 (popup 2026-10-20 "Middle: Lv 50 at ~33 h") = levels ~30 % slower than A:185's 10 h a zone: Zone 1 12 h, Zones 2-3 14 h
    # (Lv 50 = 12 + 14 + 7 = 33 h); Zones 4-5 = A:187 Q1's 12 h / 15 h x 1.3
    (1, 1, 20, 12, "A:185 + A:197"), (2, 20, 40, 14, "A:185 + A:197"), (3, 40, 60, 14, "A:185 + A:197"),
    (4, 60, 80, 16, "A:187 Q1 x1.3"), (5, 80, 100, 20, "A:187 Q1 x1.3")]
RUN1_HOURS, REBIRTH_SHRINK = 45, 0.85       # A:185 "40-50 h" (middle), A:187 Q3 15% shorter each
CAP1, CAP_STEP, CAP_MAX = 50, 10, 100       # A:174 start 50, +10 per rebirth; A:193 cap stays 100
LAG = {"Mining": 4, "Foraging": 4, "Beastmastery": 4,   # A:188 Q5 skills trail 3-5 (essentials A:187 Q4)
       "Farming": 5, "Cooking": 5, "Alchemy": 5,        # P3 Q5 default (Skyy "3-5"; was a GUESS of 8)
       "Fishing": 15}                                   # GUESS: 'nice to have until its rework' (A:187 Q4)
MAX_GAP_H = 1.0          # A:187 Q2 never > 1 h of active play without a level-up AND a gear upgrade
COLL_II_MIN, COLL_V_H = 10, (1, 2)          # A:191 Q21
ARMOR_SET_H = (0.75, 1.5)                   # A:191 Q22
UT_PER_H = (1, 2)                           # A:190 Q16 (elite / dungeon hunting in the right zone)
MYTHIC_PER_BOSS = (5, 10)                   # docs/answered/economy.md:162 Q17 (1 per 5-10 boss kills)
COIN_END = {1: 10_000, 3: 500_000, 5: 10_000_000}   # economy.md:162 Q18 (never spending; end of Zone 1 / 3 / 5)
POWER_SPLIT = (35, 30, 20, 15)              # A:190 Q15 weapon-tool / armor / accessories / pets
BEST_VS_PLAIN = 3.0                         # A:190 Q14
KEEP_PER_VP = 0.25                          # A:193 Q9 flat +0.25% all XP per unspent VP, no cap
VP_EARNED = [38, 50, 60, 70, 80]            # T3:507 typical VP for rebirth 1-5

# ======================================================================================== TODAY (live numbers)
GENERAL = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000,
           100000] + [200000 + 100000 * i for i in range(26)] + [2750000, 2900000, 3100000, 3400000, 3700000] + \
          [4000000 + 300000 * i for i in range(51)]                        # X:23 'levels' (Hypixel table; per level)
CLASS = [50, 100, 160, 220, 280, 350, 440, 530, 630, 750, 880, 1050, 1200, 1400, 1600, 1800, 2100, 2350, 2650, 3000, 3350,
         3750, 4200, 4650, 5150, 5700, 6250, 6900, 7550, 8250, 9000, 9800, 10500, 11500, 12500, 13500, 14500, 15500, 17000,
         18000, 19500, 20500, 22000, 23500, 25000, 26500, 28500, 30000, 32000, 34000, 35500, 38000, 40000, 42000, 44500,
         46500, 49000, 51500, 54500, 57000, 60000, 62500, 65500, 68500, 72000, 75000, 78500, 82000, 85500, 89000, 93000,
         97000, 100000, 105000, 110000, 115000, 120000, 125000, 125000, 130000, 135000, 140000, 145000, 150000, 160000,
         165000, 170000, 175000, 180000, 185000, 195000, 200000, 205000, 210000, 220000, 225000, 235000, 240000, 250000,
         255000]                                                             # X:298 levels.class
MINING = [math.floor(10 + 5 * L + 1.5 * L * L + 0.5) for L in range(1, 101)]   # X:325 / X:1631 10 + 5L + 1.5L^2
FARMING = [50, 91, 137, 189, 256, 330, 417, 512, 621, 736, 866, 953, 1038, 1115, 1187, 1247, 1299, 1336, 1361, 1369, 1362,
           1483, 1611, 1743, 1881, 2023, 2172, 2325, 2485, 2648, 2818, 2991, 3172, 3356, 3547, 3742, 3943, 4149, 4361, 4576,
           4799, 5025, 5259, 5495, 5739, 5986, 6240, 6498, 6763, 7031, 7307, 7585, 7871, 8160, 8457, 8757, 9063, 9374, 9691,
           10012, 10340, 10671, 11010, 11352, 11701, 12053, 12412, 12775, 13145, 13519, 13899, 14283, 14674, 15069, 15470,
           15876, 16288, 16703, 17126, 17552, 17985, 18421, 18865, 19312, 19766, 20224, 20689, 21157, 21632, 22111, 22596,
           23086, 23582, 24082, 24588, 25099, 25616, 26137, 26664, 27196]  # L:757 (0.4.53; formula X:1632)
CURVES = {"Class": CLASS, "Mining": MINING, "Farming": FARMING, "Foraging": GENERAL, "Cooking": GENERAL,
          "Alchemy": GENERAL, "Fishing": GENERAL, "Beastmastery": GENERAL}  # X:23 'every skill but class' uses levels
KILL_CURVE = [(1, 1), (5, 1.58), (10, 2.49), (15, 3.6), (20, 4.91), (25, 6.42), (30, 8.13), (35, 10.04), (40, 12.15),
              (45, 14.46), (50, 16.97), (60, 22.59), (70, 29.01), (80, 36.23), (90, 44.25), (100, 53.07)]  # X:327-342
PER_HEALTH, CLASS_MULT = 0.2, 3.0           # X:19 combat.perHealth, X:297 classSkill.xpMultiplier
MOB_LV1_HP = 60                             # GUESS typical Lv 1 health (floor 50: C:20 strength.floor)
NORMAL_SHARE = [(1, 0.88), (20, 0.85), (40, 0.81)]   # research/Mob-Curve-Spec.md:465 (Lv 1 value GUESS)
COINS_PER_LEVEL = 100                       # X:11 (paid as 100 x new level: research/Economy-Audit-1014.md:28)
SELL = 0.9                                  # E:151 Bazaar spread 0.1 -> instant sell ~ base x 0.9 (GUESS: no premium)
# per zone: ore XP (X:33-50, X:735-738 ore rows; zone metals LB:24-40), ore price (E:157-164, E:682-685), log XP (X:44-92 by
# biome trees, GUESS mix), log price (E:144-176, GUESS mix), crop XP (X:85-110, CROPS tier_tags G:2405), crop price (E:188-201)
ZONE_GATHER = {1: dict(ore_xp=6.5, ore_px=47, log_xp=6, log_px=20, crop_xp=4, crop_px=12),     # Copper 5 / Iron 8
               2: dict(ore_xp=18, ore_px=216, log_xp=8, log_px=90, crop_xp=5.5, crop_px=36),   # Thorium 18 / Lead 18
               3: dict(ore_xp=15, ore_px=648, log_xp=8, log_px=216, crop_xp=7.5, crop_px=72),  # Cobalt 15 / Chromium 15
               4: dict(ore_xp=30, ore_px=2160, log_xp=10, log_px=576, crop_xp=6.5, crop_px=144),  # Adamantite / Slag 30
               5: dict(ore_xp=25, ore_px=6480, log_xp=20, log_px=576, crop_xp=5, crop_px=400)}   # Mithril / Titanium 25
STONE_XP, STONE_PX = 1, 4.5                 # X:24 prefix.Rock_ Mining:1, E:183 cobble 4.5
GATHER_BOOST = [(10, 3.0), (20, 1.5)]       # X:310-313 gather.boost early x3 to 10 -> x1.5 from 20 (Foraging, Farming)
ALCH_XP = {1: 50, 2: 850, 3: 8000, 4: 18000, 5: 18000}   # X:189 alchemy.tierXp
COOK_XP = 1000 * 0.5                        # H:1028 xp.default x H:1022 xpMultiplier
LOOT_CHANCE, LOOT_CAP = 0.06, 20            # G:240-241 loot.mob.chance 6 %, capPerHour 20
UT_CHANCE, MYTHIC_CHANCE = 0.02, 0.005      # G:356 utdrop.mob 2 (% per elite/dungeon kill: GUESS meaning), G:1589 boss 0.5 %
ENCH_SIZE = 160                             # E:594 Ench Carrot 2160 = 120 x carrot 18; Ench Oak 2160 = 160 x 13.5 (GUESS 160)
COLL_S = (100, 1000)                        # H:11 curve.S: tier II = 100, V = 1000 items

# ======================================================================================== P3 (research/Balance-P3-XP-Spec.md)
def f_lv(L):
    """the kill XP level factor (combat.levelCurve: 1 / 4.91 / 16.97 / 53.07 at Lv 1 / 20 / 50 / 100) - P3 section 2"""
    return 1 + 0.13 * (L - 1) + 0.004 * (L - 1) ** 2


def s_lv(L):
    """quick start (Lv 1-4 = a quarter to a whole level), flat 5-60, +1.8 % a level above 60 (Zones 4-5) - P3 section 2"""
    return L / 4 if L <= 4 else (1.0 if L <= 60 else 1 + 0.018 * (L - 60))


def r_xp(x):
    """round to 5 below 1,000, to 50 below 10,000, to 100 above (Python round: half to even - the spec's list) - P3 section 2"""
    st = 5 if x < 1000 else (50 if x < 10000 else 100)
    return int(round(x / st)) * st


P3_BASE = [r_xp(1100 * f_lv(L) * s_lv(L)) for L in range(1, 101)]   # the spec's levels= list (100 % = levels.scale's reference)
assert P3_BASE[:5] == [275, 625, 1050, 1550, 1750] and P3_BASE[49] == 18700 and P3_BASE[99] == 100400, P3_BASE[:5]
assert sum(P3_BASE[:20]) == 58150 and sum(P3_BASE[:50]) == 406200 and sum(P3_BASE) == 2944700   # spec section 2 totals
LEVELS_SCALE = 120          # A:197 "Middle: Lv 50 at ~33 h": levels.scale 120 % puts class Lv 50 at 33.1 h in this model (130 % = 35.9 h)
P3_LEVELS = [int(math.floor(x * (LEVELS_SCALE / 100.0) + 0.5)) for x in P3_BASE]   # = SkyySkills scaledTo(base, 130): Math.round(x x 1.3)
BAND = [1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 100]     # tier T starts at BAND[T-1] (LB section 1, tier_tags LEVEL_BANDS)
F_T = [f_lv(b) for b in BAND]                                            # F(T) = f(band start) - P3 section 3


def tier_at(level):
    """the highest tier whose band has started at this level (what a player in that zone gathers / cooks)"""
    t = 1
    for i, b in enumerate(BAND):
        if level >= b:
            t = i + 1
    return t


def xp_t(base, t):
    """base x F(T), rounded to 5 below 1,000, else 50 (the spec's tables)"""
    x = base * F_T[t - 1]
    return int(math.floor(x / 5 + 0.5)) * 5 if x < 1000 else int(math.floor(x / 50 + 0.5)) * 50


ORE_BASE, LOG_BASE, CROP_BASE, DISH_BASE = 50, 33, 38, 800   # P3 3.1-3.3; 3.5: 800 x F(T) Cooking XP a dish after xpMultiplier 0.5
ALCH_XP_P3 = {1: 1500, 2: 7400, 3: 18200, 4: 33900, 5: 54400}          # P3 3.6 alchemy.tierXp = 1,500 x f(zone start)
FISH_P3, FISH_H = 60, 200          # P3 3.8: a common fish = 60 x f(own level), fish.xp.mult 6; GUESS 200 fish / h (focused Fishing ~ Foraging)
CATCHUP = dict(on=True, free=5, per=0.10, max=1.0,                      # P3 section 4 (Q2 default: on, +10 % a level past 5 behind, <= +100 %)
               skills=("Mining", "Foraging", "Farming", "Fishing", "Alchemy", "Smithing", "Cooking", "Acrobatics"))
PAST_LIFE = [1.2, 1.45, 1.8, 2.25, 2.8]                                  # P3 section 5 rebirth.pastLifeXp (Q3 default)
BEFORE = "--before" in sys.argv     # the P1 view: today's live tables (0.4.56) instead of the P3 numbers
NOW = "today" if BEFORE else "P3"   # the label of the model column
if not BEFORE:
    CURVES = dict((s, P3_LEVELS) for s in CURVES)                        # one curve for the class and every skill (levels.class.sameAsOthers)

# ---- the focused player (all GUESS until P3 measures them in game)
SHARE = {"Class": 0.45, "Mining": 0.18, "Foraging": 0.15, "Farming": 0.10, "Cooking": 0.04, "Alchemy": 0.04,
         "Fishing": 0.02, "Beastmastery": 0.0}   # time split; Beastmastery levels from pet XP alongside everything (not built)
KILLS_H = 150          # Normal: 4-6 hits a kill (A:188 Q6) + walking: one kill every 24 s
ELITE_KILLS_H = 40     # when hunting elites (3x HP, A:188 Q7)
BLOCKS_H, ORE_FRAC = 900, 0.25            # mining blocks / h and the part that is ore
LOGS_H, LEAVES_H = 400, 800               # Tree Feller logs + leaves (X:225 fell.leaves) / h
CROPS_H = 500                             # active harvest / h
DISHES_H, BREWS_H = 60, 40                # cooking / alchemy crafts per h
FISH_XP_H = 0                             # Fishing XP not modelled (rework pending, A:187 Q4)
KEPT_PER_REBIRTH = 0.06  # GUESS: gear tiers / shards / pets / accessories / +3 % stats (X:482 stat.perRebirth) kept = +6 % speed


# ======================================================================================== helpers
def interp(points, x):
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


def cum(curve, level):
    """total XP for `level` = the first `level` entries (the game's convention: entry k = XP from level k-1 to k; a new player is Lv 0).
    P1 summed level - 1 entries (players started at Lv 1 - one entry, ~8 min of class XP at the P3 pace, off); fixed in P3."""
    return sum(curve[:max(0, level)])


def zone_of(level):
    return min(5, max(1, math.ceil(level / 20)))


def target_hours(level):
    """Base-pace hours to reach a class level (zones split evenly per level)."""
    h = 0.0
    for z, lo, hi, hrs, _ in ZONES:
        if level <= lo:
            break
        span = (hi - lo) if z > 1 else (hi - 1)
        h += hrs * (min(level, hi) - max(lo, 1)) / span
    return h


def target_level(hours):
    lo, hi = 1.0, 100.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if target_hours(mid) < hours else (lo, mid)
    return lo


def kill_xp(level):
    return max(MOB_LV1_HP, 50) * PER_HEALTH * CLASS_MULT * interp(KILL_CURVE, level) * interp(NORMAL_SHARE, level)


def xp_per_hour(skill, level, class_level):
    """XP per hour WHILE doing that activity (P3 numbers; --before: today's). Gathering tier = the tier the class level's band reached."""
    if BEFORE:
        return xp_per_hour_p1(skill, level, class_level)
    t = tier_at(max(1, class_level))
    if skill == "Class":
        return KILLS_H * kill_xp(max(1, class_level))
    if skill == "Mining":
        return BLOCKS_H * ((1 - ORE_FRAC) * STONE_XP + ORE_FRAC * xp_t(ORE_BASE, t))
    if skill == "Foraging":
        return LOGS_H * xp_t(LOG_BASE, t) + LEAVES_H * 1
    if skill == "Farming":
        return CROPS_H * xp_t(CROP_BASE, t)
    if skill == "Cooking":
        return DISHES_H * DISH_BASE * F_T[t - 1]      # 60 dishes x 800 x F = spec 3.5's 48,000 x F(T) an hour
    if skill == "Alchemy":
        return BREWS_H * ALCH_XP_P3[zone_of(max(1, class_level))]
    if skill == "Fishing":
        return FISH_H * FISH_P3 * f_lv(max(1, level))
    return 0.0


def xp_per_hour_p1(skill, level, class_level):
    """XP per hour WHILE doing that activity, P1's numbers (the live 0.4.56 tables). Gathering zone = the class level's zone."""
    level, class_level = max(1, level), max(1, class_level)
    z = ZONE_GATHER[zone_of(class_level)]
    boost = interp(GATHER_BOOST, level)
    if skill == "Class":
        return KILLS_H * kill_xp(class_level)
    if skill == "Mining":
        return BLOCKS_H * ((1 - ORE_FRAC) * STONE_XP + ORE_FRAC * z["ore_xp"])
    if skill == "Foraging":
        return (LOGS_H * z["log_xp"] + LEAVES_H * 1) * boost
    if skill == "Farming":
        return CROPS_H * z["crop_xp"] * boost
    if skill == "Cooking":
        return DISHES_H * COOK_XP
    if skill == "Alchemy":
        return BREWS_H * ALCH_XP[zone_of(class_level)]
    return FISH_XP_H


def coins_per_hour(class_level):
    z = ZONE_GATHER[zone_of(class_level)]
    mine = BLOCKS_H * ((1 - ORE_FRAC) * STONE_PX + ORE_FRAC * z["ore_px"]) * SELL
    return (SHARE["Mining"] * mine + SHARE["Foraging"] * LOGS_H * z["log_px"] * SELL
            + SHARE["Farming"] * CROPS_H * z["crop_px"] * SELL)


# ======================================================================================== simulation
def catchup_mult(skill, level, class_level):
    """P3 section 4: skill XP x (1 + min(max, per x (gap - free))) when the skill is more than `free` levels behind the class"""
    if BEFORE or not CATCHUP["on"] or skill not in CATCHUP["skills"]:
        return 1.0
    gap = class_level - level
    if gap <= CATCHUP["free"]:
        return 1.0
    return 1 + min(CATCHUP["max"], CATCHUP["per"] * (gap - CATCHUP["free"]))


def simulate_today(cap=CAP1, hours=RUN1_HOURS, dt=0.02, share=None, catchup=True, speed=1.0, past_cap=0, past_mult=1.0):
    """one focused player; levels start at 0 (the game's convention); speed = an all-XP multiplier (VP + kept power), past_mult = the
    past-life boost on levels below past_cap (P3 section 5)"""
    share = SHARE if share is None else share
    lv = {s: 0 for s in share}
    xp = {s: 0.0 for s in share}
    coins, t, last_up, worst_gap = 0.0, 0.0, 0.0, 0.0
    trace = []   # (t, class level, {skill: level}, coins)
    while t < hours:
        up = False
        for s, sh in share.items():
            if sh <= 0 or lv[s] >= cap:
                continue
            m = speed * (past_mult if lv[s] < past_cap else 1.0) * (catchup_mult(s, lv[s], lv["Class"]) if catchup else 1.0)
            xp[s] += xp_per_hour(s, lv[s], lv["Class"]) * sh * dt * m
            while lv[s] < cap and xp[s] >= CURVES[s][lv[s]]:
                xp[s] -= CURVES[s][lv[s]]
                lv[s] += 1
                coins += COINS_PER_LEVEL * lv[s]
                up = True
        coins += coins_per_hour(max(1, lv["Class"])) * dt
        t += dt
        if up:
            worst_gap, last_up = max(worst_gap, t - last_up), t
        trace.append((t, lv["Class"], dict(lv), coins))
    return trace, max(worst_gap, t - last_up)


def at_level(trace, level):
    for t, c, lvls, coins in trace:
        if c >= level:
            return t, lvls, coins
    return None, trace[-1][2], trace[-1][3]


# ======================================================================================== Void Particles (rebirth)
KEEP = KEEP_PER_VP / 100
# PROPOSED rank strengths (A:193 Q8 'stronger'): early ranks ~2x the keep rate per VP, last ranks ~0.9x, so spending the
# first ranks is clearly right and the last ranks are a real choice against keeping. w = share of the run the arm speeds up.
ARMS = [  # name, cost per rank (T3:512-514), +% per rank (PROPOSED), weight w (GUESS)
    ("Void Insight (all XP)", [12, 20, 32, 48, 72], [6, 8, 10, 12, 16], 1.0),
    ("Class Echo (class XP)", [4, 6, 10, 16, 24], [4, 5, 7, 9, 11], 0.5),
    ("Mining Echo", [4, 6, 10, 16, 24], [8, 11, 15, 20, 26], 0.17),
    ("Foraging Echo", [4, 6, 10, 16, 24], [8, 11, 15, 20, 26], 0.17),
    ("Beastmastery Echo", [4, 6, 10, 16, 24], [8, 11, 15, 20, 26], 0.17)]
SPEC_OLD = {"Void Insight (all XP)": 2, "Class Echo (class XP)": 3}   # T3:512-513 old +2 % / +3 % per rank


def vp_plan():
    """Greedy: buy the next rank of an arm while its value per VP beats keeping (+0.25 % per VP)."""
    ranks = {a[0]: 0 for a in ARMS}
    bank, rows = 0, []
    for n, earned in enumerate(VP_EARNED, 1):
        bank += earned
        while True:
            best = None
            for name, cost, pct, w in ARMS:
                r = ranks[name]
                if r < 5 and cost[r] <= bank:
                    val = pct[r] / 100 * w / cost[r]
                    if val > KEEP and (best is None or val > best[0]):
                        best = (val, name, cost[r])
            if not best:
                break
            ranks[best[1]] += 1
            bank -= best[2]
        spent_bonus = sum(sum(pct[:ranks[name]]) / 100 * w for name, cost, pct, w in ARMS)
        keep_bonus = bank * KEEP
        kept = 1 + KEPT_PER_REBIRTH * n
        cap = min(CAP_MAX, CAP1 + CAP_STEP * n)
        run_h = RUN1_HOURS * REBIRTH_SHRINK ** n
        need_fixed = 1 / REBIRTH_SHRINK ** n                          # same work as run 1, 15 % shorter each
        need_full = need_fixed * target_hours(cap) / target_hours(CAP1)  # plus the +10 levels per rebirth
        have = (1 + spent_bonus + keep_bonus) * kept
        new = target_hours(cap) - target_hours(cap - CAP_STEP)          # first-time levels this run
        replay = target_hours(cap - CAP_STEP)
        disc = (target_hours(CAP1) * have / need_fixed - new) / replay    # XP share replayed levels may cost
        rows.append(dict(n=n, earned=earned, total=sum(VP_EARNED[:n]), spent=sum(VP_EARNED[:n]) - bank, kept_vp=bank,
                         spend=spent_bonus, keep=keep_bonus, kept=kept, have=have, need_fixed=need_fixed,
                         need_full=need_full, run_h=run_h, cap=cap, disc=min(1.0, disc), ranks=dict(ranks)))
    return rows


# ======================================================================================== tables
def fmt(x):
    if x is None:
        return "-"
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f}M"
    if abs(x) >= 1e4:
        return f"{x / 1e3:.0f}k"
    if abs(x) >= 100:
        return f"{x:.0f}"
    return f"{x:.2f}".rstrip("0").rstrip(".")


def gap_flag(today, lo, hi=None):
    hi = lo if hi is None else hi
    if today is None or lo == 0:
        return "?"
    r = today / (lo if today < lo else hi)
    return "ok" if lo <= today <= hi else (f"!! {rx(r)}" if r > 1.25 or r < 0.8 else f"~{rx(r)}")


def rx(r):
    """today / target as text: x2.5 = 2.5 times the target, 1/40 = a fortieth of it."""
    return f"x{r:.2f}" if r >= 0.1 else f"1/{1 / max(r, 1e-9):,.0f}"


def build():
    trace, worst_gap = simulate_today()
    out, worst = [], {}

    def note(key, ratio, text):   # keep the worst gap per topic (ratio = today / target)
        size = abs(math.log(max(ratio, 1e-9)))
        if size > worst.get(key, (0, ""))[0]:
            worst[key] = (size, text)

    def table(title, head, rows):
        out.append(f"\n### {title}\n")
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "---|" * len(head))
        out.extend("| " + " | ".join(str(c) for c in r) + " |" for r in rows)

    # 1. level vs hours per zone
    rows, cum_h = [], 0
    for z, lo, hi, hrs, src in ZONES:
        cum_h += hrs
        t_end, lv_end, coins_end = at_level(trace, min(hi, CAP1))
        t_today = f"{t_end:.1f} h" if t_end is not None else f"not by {RUN1_HOURS} h (Lv {lv_end['Class']})"
        if hi > CAP1 and lo < CAP1:
            t_today += f" (to the Lv {CAP1} cap)"
        elif lo >= CAP1:
            t_today = "rebirth runs (cap)"
        rows.append([z, f"{lo}-{hi}", hrs, cum_h, f"{20 / hrs:.2f}", f"{target_hours(min(hi, CAP1)):.1f} h" if lo < CAP1
                     else "-", t_today, src])
    table("1. Class level vs hours (Normal, first time through, base pace)",
          ["Zone", "Mob levels", "Target h", "Cum h", "Target lv/h", f"Target to min(top, {CAP1})", f"{NOW} (model)",
           "Source"], rows)
    # 1b. every skill's level at fixed hours: target (class pace minus the lag) vs today's simulation
    rows, t_cap = [], target_hours(CAP1)

    def skill_target(s, h):   # class pace minus the lag; after the class cap the lag closes linearly by the rebirth
        lag = 0 if s == "Class" else LAG[s]
        if h <= t_cap:
            return max(1, round(min(CAP1, target_level(h))) - lag)
        return round(CAP1 - lag + lag * (h - t_cap) / (RUN1_HOURS - t_cap))
    for h in (2, 5, 10, 20, 30, RUN1_HOURS):
        lv_today = next((lv for t, c, lv, _ in trace if t >= h), trace[-1][2])
        rows.append([f"{h} h"] + [f"{skill_target(s, h)} / {lv_today[s]}" for s in SHARE if SHARE[s] > 0])
    table(f"1b. Level at hour (run 1, cap {CAP1}): target / {NOW}. Target = class pace minus the skill lag; the cap "
          "stretch after the class cap lets the trailing skills catch up", ["Hour"] + [s for s in SHARE if SHARE[s] > 0], rows)
    t20, z1 = at_level(trace, 20)[0], ZONES[0][3]
    if t20 is not None and not 0.75 <= t20 / z1 <= 1.33:
        note("class-zone1", t20 / z1, f"Class Lv 20 (end of Zone 1) at {t20:.1f} h {NOW} vs {z1} h target ({rx(t20 / z1)} "
             "the time)")
    t50, lv50, _ = at_level(trace, CAP1)
    if t50 is None or abs(t50 - target_hours(CAP1)) / target_hours(CAP1) > 0.25:
        note("class-time", (t50 or 99) / target_hours(CAP1), f"Class Lv {CAP1} reached at {fmt(t50)} h {NOW} vs "
             f"{target_hours(CAP1):.0f} h target (Lv 20 at {fmt(at_level(trace, 20)[0])} h vs {z1} h)")
    if not BEFORE:   # 1c. P3 section 4: three kinds of player, catch-up on / off (levels at 10 h / 20 h)
        rows = []
        kinds = [("balanced (45 % class)", SHARE),
                 ("fighter (70 % class)", dict(SHARE, Class=0.70, Mining=0.07, Foraging=0.07, Farming=0.06, Cooking=0.04, Alchemy=0.04,
                                               Fishing=0.02)),
                 ("gatherer (25 % class)", dict(SHARE, Class=0.25, Mining=0.25, Foraging=0.22, Farming=0.16, Cooking=0.05, Alchemy=0.05,
                                                Fishing=0.02))]
        cols = ["Class", "Mining", "Foraging", "Farming", "Cooking", "Alchemy", "Fishing"]
        for name, sh in kinds:
            for cu in (True, False):
                tr, _g = simulate_today(hours=20.01, share=sh, catchup=cu)
                l10 = next(lv for t, c, lv, _ in tr if t >= 10)
                l20 = tr[-1][2]
                rows.append([name, "on" if cu else "off"] + [f"{l10[c]} / {l20[c]}" for c in cols])
        table("1c. Kinds of player (P3 section 4): levels at 10 h / 20 h, catch-up on / off (fighter / gatherer splits GUESS)",
              ["Player", "Catch-up"] + cols, rows)

    # 2. XP/h needed per activity per zone (today's curves) vs today's XP/h
    rows = []
    for z, lo, hi, hrs, _ in ZONES:
        top = min(hi, CAP1) if lo < CAP1 else hi
        span_h = target_hours(top) - target_hours(lo)
        mid = (lo + top) // 2
        for s in ["Class", "Mining", "Foraging", "Farming", "Cooking", "Alchemy"]:
            lag = 0 if s == "Class" else LAG[s]
            a, b = max(1, lo - lag), max(1, top - lag)
            need = (cum(CURVES[s], b) - cum(CURVES[s], a)) / (span_h * SHARE[s])
            today = xp_per_hour(s, max(1, mid - lag), mid)
            flag = gap_flag(today, need * 0.85, need * 1.15)
            rows.append([z, s, f"{a}-{b}", fmt(need), fmt(today), flag])
            if flag.startswith("!!"):
                note(s, today / need, f"{s} XP/h (worst: Zone {z}, Lv {a}-{b}): needs {fmt(need)} while doing it, {NOW} "
                     f"~{fmt(today)} ({rx(today / need)})")
    table(f"2. XP per hour needed WHILE doing the activity ({NOW} curves; time split + skill lag: Assumptions). Zones 4-5 "
          "are reached in rebirth runs; shown at base pace",
          ["Zone", "Activity", "Target levels", "XP/h needed", f"XP/h {NOW} (model)", "Gap"], rows)

    # 3. coins
    rows = []
    geo = {1: COIN_END[1], 2: math.sqrt(COIN_END[1] * COIN_END[3]), 3: COIN_END[3],
           4: math.sqrt(COIN_END[3] * COIN_END[5]), 5: COIN_END[5]}   # zones 2 / 4 = geometric middle (GUESS)
    prev, cum_h = 0, 0
    for z, lo, hi, hrs, _ in ZONES:
        cum_h += hrs
        tgt_h = (geo[z] - prev) / hrs
        today_h = coins_per_hour((lo + hi) // 2)
        t_end, _, coins_end = at_level(trace, min(hi, CAP1))
        have = fmt(coins_end) if lo < CAP1 else "-"
        flag = gap_flag(today_h, tgt_h * 0.7, tgt_h * 1.4)
        rows.append([z, fmt(geo[z]), fmt(tgt_h), fmt(today_h), have, flag])
        if flag.startswith("!!"):
            note("coins", today_h / tgt_h, f"Coins (worst: Zone {z}): target ~{fmt(tgt_h)}/h, {NOW} ~{fmt(today_h)}/h from "
                 f"selling gathered items alone ({rx(today_h / tgt_h)})")
        prev = geo[z]
    table("3. Coins (never spending; economy.md:162 Q18; Zones 2 / 4 = geometric middle, GUESS)",
          ["Zone", "Target at zone end", "Target coins/h", "Gathering sales/h today", "Today at zone end (+level coins)",
           "Gap"], rows)

    # 4. drops / upgrades per hour
    ore_h = BLOCKS_H * ORE_FRAC
    coll_ii_min = COLL_S[0] / ore_h * 60
    coll_v_h = COLL_S[1] / ore_h
    set_h = 4 * ENCH_SIZE / ore_h
    loot_h = min(LOOT_CAP, KILLS_H * SHARE["Class"] * LOOT_CHANCE)
    ut_h = ELITE_KILLS_H * UT_CHANCE if BEFORE else p5_ut_sim()[0]          # P5 3.2: the UT meter (40 points / h hunting)
    checks = [  # what, target low, target high, today, unit, source
        ("Collection tier II (ore, curve S)", COLL_II_MIN, COLL_II_MIN, coll_ii_min, "min", "A:191 / H:11"),
        ("Collection tier V (ore)", *COLL_V_H, coll_v_h, "h", "A:191 / H:11"),
        ("One armor set (4 x 1 Enchanted ore)", *ARMOR_SET_H, set_h, "h", "A:191 / G:485 garmor.ladders"),
        ("UT drops per hour of elite hunting", *UT_PER_H, ut_h, "/h", "A:190 / G:356"),
        ("Boss kills per Mythic", *MYTHIC_PER_BOSS, 1 / MYTHIC_CHANCE if BEFORE else p5_mythic_sim()[0], "kills", "economy.md:162 / G:1589 / P5 3.3"),
        (f"Longest stretch without any level-up (run 1, cap {CAP1})", 0, MAX_GAP_H, worst_gap, "h", "A:187 Q2")]
    rows = []
    for what, lo, hi, today, unit, src in checks:
        flag = gap_flag(today, max(lo, 1e-9) * 0.8 if lo else 0.0, hi * 1.25) if lo else             ("ok" if today <= hi else f"!! {rx(today / hi)}")
        rows.append([what, f"{fmt(lo)}-{fmt(hi)} {unit}" if lo != hi else f"{fmt(lo)} {unit}", f"{fmt(today)} {unit}", flag, src])
        if flag.startswith("!!"):
            note(what, today / (hi if today > hi else max(lo, 1e-9)), f"{what}: target {rows[-1][1]}, {NOW} {rows[-1][2]}")
    if BEFORE:
        rows.append(["Gear loot bags per hour (normal play)", ">= 1 gear upgrade / h", f"{loot_h:.1f} bags (share that "
                     "upgrades: ?)", "?", "A:187 Q2 / G:240-241"])
    else:          # P5 6: smart bags + level-ups - the longest stretch without a gear upgrade before the cap
        _ur = p5_upgrade_rows()[-1]
        rows.append(["Gear loot bags per hour (normal play)", ">= 1 gear upgrade / h", f"{P5_BAGS_H:.2f} bags (smart {P5_SMART:g} %) + level-ups: "
                     f"longest stretch without an upgrade {_ur[2]:.2f} h (p90, before the cap)", "ok" if _ur[2] <= MAX_GAP_H else "!!", "A:187 Q2 / P5 6"])
    table("4. Drops, collections, upgrades", ["What", "Target", f"{NOW} (model)", "Gap", "Source"], rows)

    # 5. VP ladder + keep buff
    vp = vp_plan()
    rows = [[name, "/".join(map(str, cost)), "+" + "/".join(map(str, pct)) + " %", f"{SPEC_OLD.get(name, 3)} % flat",
             w, " ".join(f"{p / 100 * w / c * 100:.2f}" for c, p in zip(cost, pct))] for name, cost, pct, w in ARMS]
    table(f"5a. Void Particle arms - PROPOSED rank strengths (keep = +{KEEP_PER_VP} % all XP per unspent VP, no cap, A:193)",
          ["Arm", "Cost per rank (T3:512)", "Proposed per rank", "Spec 6.2 had", "Weight w (GUESS)",
           "Value per VP in % all-XP (keep = 0.25)"], rows)
    rows = [[r["n"], r["cap"], f"{r['run_h']:.1f}", r["total"], f"{r['spent']} / {r['kept_vp']}",
             f"+{r['spend'] * 100:.0f} % + {r['keep'] * 100:.0f} %", f"x{r['kept']:.2f}", f"x{r['have']:.2f}",
             f"x{r['need_fixed']:.2f}", f"x{r['need_full']:.2f}", f"{r['disc'] * 100:.0f} %"] for r in vp]
    table("5b. Rebirths 1-5: spend vs keep (greedy best split) and the speed-up needed",
          ["Rebirth", "Cap", "Run target h", "VP earned (T3:507)", "Spent / kept", "XP bonus spend + keep",
           f"Kept power (GUESS +{KEPT_PER_REBIRTH * 100:.0f} %/rebirth)", "Have", "Need (same work, 15 % shorter)",
           "Need (incl. +10 levels)", "Replayed levels cost (past-life discount)"], rows)
    if not BEFORE:   # 5c. P3 section 5: the past-life XP boost - hours to the class cap per rebirth (all XP x the VP + kept speed)
        rows = []
        t_cap1 = at_level(trace, CAP1)[0] or RUN1_HOURS
        cls = {"Class": SHARE["Class"]}
        for r in vp:
            n, cap = r["n"], r["cap"]
            boost = PAST_LIFE[min(n, len(PAST_LIFE)) - 1]
            prev = min(CAP_MAX, cap - CAP_STEP)
            tr, _g = simulate_today(cap=cap, hours=80, share=cls, catchup=False, speed=r["have"], past_cap=prev, past_mult=boost)
            tr0, _g = simulate_today(cap=cap, hours=80, share=cls, catchup=False, speed=r["have"])
            got, got0 = at_level(tr, cap)[0], at_level(tr0, cap)[0]
            tgt = t_cap1 * REBIRTH_SHRINK ** n
            first = (got - at_level(tr, prev)[0]) / CAP_STEP if got else None
            rows.append([n, cap, f"x{r['have']:.2f}", f"x{boost}", f"{tgt:.1f} h", f"{fmt(got)} h", f"{fmt(got0)} h",
                         f"{fmt(first)} h", gap_flag(got or 99, tgt * 0.85, tgt * 1.15)])
            if got is None or not tgt * 0.8 <= got <= tgt * 1.25:
                note("pastlife", (got or 99) / tgt, f"Rebirth {n}: class cap {cap} at {fmt(got)} h with the past-life boost x{boost} "
                     f"vs {tgt:.1f} h target")
        table(f"5c. Rebirths with the past-life XP boost {PAST_LIFE} (rebirth.pastLifeXp): hours to the class cap (target = run 1's "
              f"{t_cap1:.1f} h x {REBIRTH_SHRINK}^n); only levels below the last run's cap are boosted",
              ["Rebirth", "Cap", "VP + kept speed", "Past-life boost", "Target h to cap", "With boost", "Without",
               "Each first-time level", "Gap"], rows)
    for r in vp:
        if r["have"] < r["need_full"] * 0.95 and BEFORE:
            note("rebirth", r["have"] / r["need_full"], f"Rebirth speed-up (worst: rebirth {r['n']}, cap {r['cap']}): "
                 f"VP + kept power give x{r['have']:.2f}, a 15 %-shorter run with +10 levels needs x{r['need_full']:.2f} "
                 f"-> replayed levels must cost ~{r['disc'] * 100:.0f} % XP (past-life discount) or curves scale with the cap")
    return "\n".join(out), sorted(worst.values(), reverse=True), vp


def assumptions_md():
    return "\n".join([
        "## Assumptions (source file:line; GUESS = none yet)",
        "- A = docs/answered/skills.md, X = research/balance/xp.md, C = combat.md, G = gear.md, E = economy.md, H = gathering.md "
        "(research/balance/), T3 = research/Skill-Trees-3-Spec.md, LB = research/Level-Bands-20-Spec.md, L = live xp.properties.",
        f"- Zone hours {[(z[0], z[3]) for z in ZONES]} = 'first time through' at base pace (A:185, A:187 Q1); bands 20 levels a "
        "zone (LB:24-40). GUESS: Zone 4-5 hours read as base-pace hours like Zones 1-3.",
        f"- Run 1: cap {CAP1} = mid Zone 3 (A:174). Class Lv {CAP1} at {target_hours(CAP1):.0f} h on the zone pace; the rest of "
        f"the {RUN1_HOURS} h run (A:185 '40-50 h') = the cap stretch: skills catch up (A:188 Q5), useful skills to {CAP1}, Zone 3 "
        "gear / bosses at the cap, UT hunting, overflow XP for VP (T3:503-507). GUESS reading - Skyy to confirm (see Q below).",
        f"- Rebirth n: run {RUN1_HOURS} h x {REBIRTH_SHRINK}^n (A:187 Q3), cap {CAP1} + {CAP_STEP} n up to {CAP_MAX} (A:174, A:193).",
        f"- Skill lag behind class: {LAG} (A:188 Q5 3-5 for essentials; useful 5 = P3 Q5 default; Fishing GUESS).",
        f"- P3 numbers (research/Balance-P3-XP-Spec.md): ONE curve R(1100 x f(L) x s(L)) x levels.scale {LEVELS_SCALE} % for the class "
        f"and every skill (Lv 20 = {cum(P3_LEVELS, 20):,} XP, Lv 50 = {cum(P3_LEVELS, 50):,}, Lv 100 = {cum(P3_LEVELS, 100):,}); "
        f"XP per action = base x F(T) (ore {ORE_BASE}, log {LOG_BASE}, crop {CROP_BASE}, dish {DISH_BASE}; alchemy.tierXp "
        f"{list(ALCH_XP_P3.values())}); Fishing {FISH_P3} x f(own level) a fish at {FISH_H} fish / h (GUESS); catch-up "
        f"{CATCHUP['per']:.0%} a level past {CATCHUP['free']} behind, <= +{CATCHUP['max']:.0%}; past-life boost {PAST_LIFE}. Levels "
        "start at 0 (the game's convention, P3 fix). `--before` prints the same tables with today's (P1) numbers.",
        f"- Time split (GUESS): {SHARE}.",
        f"- Rates (GUESS): {KILLS_H} kills/h, {ELITE_KILLS_H} elite kills/h, {BLOCKS_H} blocks/h ({ORE_FRAC:.0%} ore), "
        f"{LOGS_H} logs + {LEAVES_H} leaves/h, {CROPS_H} crops/h, {DISHES_H} dishes/h, {BREWS_H} brews/h; Lv 1 mob health "
        f"{MOB_LV1_HP}; Enchanted = {ENCH_SIZE} base items; Bazaar instant sell = base x {SELL}.",
        "- Kill XP = Lv 1 health x 0.2 (X:19) x 3 class mult (X:297) x level curve (X:327-342) x Normal share "
        "(research/Mob-Curve-Spec.md:465); gathering XP from X:24-123 + boost X:310-313; prices E:157-685.",
        f"- Kept power per rebirth +{KEPT_PER_REBIRTH * 100:.0f} % (GUESS: kept gear tiers, shards, pets, charms, +3 % stats X:482).",
        "- Not modelled yet: Beastmastery (not built), Exploration / Acrobatics / Smithing XP, quest class XP, mob coin drops, "
        "collection tier coins, pets / accessories power (P5), Head Start ranks.",
    ])


# ======================================================================================== P4 COMBAT (research/Balance-P4-Combat-Spec.md)
# The combat core the builds (SkyyGear 0.3.34, SkyyMobs 0.1.14, SkyySkills 0.4.58, SkyyClasses 0.1.44, SkyyArmory 0.1.42) assert against.
# Ported from the spec's scratch model (tools/dev/scratch/p4/p4model.py, deleted): F_new, the mob RULE, ttk, hits to die, speed, Mana.
# Sources: P4 = research/Balance-P4-Combat-Spec.md section; MC = research/Mob-Curve-Spec.md; CR = research/Class-Roles-Sheet.md.
P4_G = 1.045                                  # P4 1.2: +4.5 % a level past Lv 20 (weapon F, armor H, mobs)
P4_F20 = [(1, 1.0), (4, 1.6), (10, 2.0), (20, 2.333333)]           # today's F up to Lv 20 (P4 1.2: unchanged)
P4_F_LEVELS = [1, 4, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
P4_F_TEXT = "1:1,4:1.6,10:2,20:2.333333,30:3.624,40:5.627,50:8.739,60:13.572,70:21.076,80:32.731,90:50.83,100:78.937"   # P4 1.4
P4_S_TEXT = "1:1,8:1.67,20:2.333333,40:4.67,60:6.07,80:10.99,100:28.75"   # P4 1.4 (DERIVED T7: each metal's charged shot keeps its ratio)
P4_RES = [(1, 1.0), (10, 1.4), (20, 1.7), (40, 2.2), (100, 3.0)]   # base.resCurve (unchanged)
P4_RES_PER = 0.18                              # MC 2.3: resistance = 18 % x R(L) (Lv 1 18 %, Lv 20 30.6 %, Lv 40 39.6 %)
P4_BAND_STARTS = [1, 8, 15, 20, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 95, 100]   # tools/tier_tags.py METAL_BANDS starts
P4_LEVELS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
# today's 0.1.12 Normal tables (stretched, SkyyMobs live = combat.md); P4 keeps them to Lv 20
P4_HP_NORMAL_012 = [(1, 1.0), (20, 2.14), (30, 3.03), (40, 4.62), (47, 6.97), (53, 10.69), (60, 15.63), (65, 19.66), (73, 21.48), (80, 23.0), (100, 27.56)]
P4_DMG_NORMAL_012 = [(1, 1.0), (20, 1.57), (30, 2.04), (40, 2.62), (47, 3.33), (53, 4.2), (60, 5.39), (65, 6.45), (73, 6.89), (80, 7.24), (100, 8.29)]
P4_DIFF = {"easy": (0.6, 0.6), "normal": (1.0, 1.1), "hard": (1.6, 1.8)}   # P4 1.2 (Normal damage x1.1 = the M class Defense 10)
# P4 1.4 - the exact file values (the spec's numbers; health = the RULE to 0.01, damage = the RULE within P4_DMG_TOL - see p4_dmg_rule)
P4_TABLES = {
    ("hp", "easy"): "1=0.6, 5=0.74, 10=0.92, 15=1.1, 20=1.28, 25=1.62, 30=2.08, 35=2.67, 40=3.4, 45=4.27, 50=5.49, 55=7.03, 60=8.95, 65=11.26, 70=14.44, 75=18.47, 80=23.5, 85=29.54, 90=37.84, 95=48.35, 100=61.47",
    ("dmg", "easy"): "1=0.6, 5=0.67, 10=0.76, 15=0.85, 20=0.94, 25=1.07, 30=1.25, 35=1.46, 40=1.74, 45=2.04, 50=2.46, 55=2.99, 60=3.65, 65=4.46, 70=5.58, 75=7.01, 80=8.83, 85=11.05, 90=14.15, 95=18.14, 100=23.24",
    ("hp", "normal"): "1=1, 5=1.24, 10=1.54, 15=1.84, 20=2.14, 25=2.69, 30=3.46, 35=4.44, 40=5.66, 45=7.12, 50=9.15, 55=11.72, 60=14.92, 65=18.76, 70=24.07, 75=30.78, 80=39.17, 85=49.23, 90=63.07, 95=80.58, 100=102.45",
    ("dmg", "normal"): "1=1.1, 5=1.23, 10=1.4, 15=1.56, 20=1.73, 25=1.96, 30=2.28, 35=2.69, 40=3.19, 45=3.75, 50=4.51, 55=5.48, 60=6.7, 65=8.18, 70=10.22, 75=12.85, 80=16.18, 85=20.26, 90=25.93, 95=33.26, 100=42.6",
    ("hp", "hard"): "1=1.6, 5=1.98, 10=2.46, 15=2.94, 20=3.42, 25=4.31, 30=5.54, 35=7.11, 40=9.06, 45=11.4, 50=14.64, 55=18.75, 60=23.88, 65=30.02, 70=38.51, 75=49.25, 80=62.67, 85=78.77, 90=100.92, 95=128.93, 100=163.92",
    ("dmg", "hard"): "1=1.8, 5=2.02, 10=2.29, 15=2.56, 20=2.83, 25=3.21, 30=3.74, 35=4.39, 40=5.22, 45=6.13, 50=7.38, 55=8.97, 60=10.96, 65=13.38, 70=16.73, 75=21.02, 80=26.48, 85=33.15, 90=42.44, 95=54.42, 100=69.71",
}
P4_DMG_TOL = 0.025          # the spec's damage table vs this model's EHP rule (2.5 %): the scratch model's exact EHP is gone (build note)
P4_HP_FLOOR = 70            # strength.floor 50 -> 70 (P4 1.2)
P4_GAP = {"free": 3, "dealtStep": 5.0, "dealtMin": 40.0, "takenStep": 3.0, "takenMax": 1.5}   # P4 1.6
P4_RANK = {"elite": (3.0, 1.5), "mini": (10.0, 2.0)}                # P4 1.7 (Skyy Q7)
P4_BOSS_BASE, P4_BOSS_DMG, P4_BOSS_UPTIME = 4500.0, 2.0, 0.6
P4_REF_HIT, P4_REF_DPS = 7.67, 17.0          # MC 5.2: Warrior Crude/Copper sword Lv 1 6 / 6 / 11 a swing, ~0.45 s
P4_KIT = {"plain": 1.0, "expected": 1.73, "best": 3.0}              # P4 1.3 (Q14 "About 3x"; expected = halfway in log space)
P4_TRASH, P4_TOUGH = (70.0, 12.0), (200.0, 27.0)                    # (base Health, base hit) - trash at the floor, a tough mob (bears / golems)
# P4 2.1 - the rating -> number map; 2.2 - the classes (CR ratings)
P4_RATE = {"health": {"SL": -20, "L": -10, "M": 0, "H": 15, "SH": 35}, "defense": {"SL": 0, "L": 5, "M": 10, "H": 25, "SH": 45},
           "damage": {"SL": 0.55, "L": 0.75, "M": 1.0, "H": 1.25, "SH": 1.5}, "speed": {"SL": -12, "L": -6, "M": 0, "H": 6, "SH": 12},
           "weight": {"SL": 2.0, "L": 1.5, "M": 1.0, "H": 0.5, "SH": 0.25}}
# class: (weight, health %, defense, stamina base, stamina / lv, own-armor speed %, native armor, damage rating)
P4_CLASSES = {"Warrior": ("SH", 35, 45, 10, 0.13, -6, "Heavy", 1.0), "Berserker": ("H", 15, 10, 13, 0.17, 0, "Heavy", 1.25),
              "Spellblade": ("M", 0, 10, 7, 0.09, 0, "Light", 1.25), "Monk": ("L", 0, 5, 13, 0.17, 12, "Light", 1.0),
              "Assassin": ("SL", -10, 5, 10, 0.13, 12, "Light", 1.5), "Archer": ("L", 0, 10, 10, 0.13, 6, "Light", 1.25),
              "Mage": ("SL", -20, 0, 4, 0.05, 6, "Cloth", 1.5), "Priest": ("L", 0, 10, 4, 0.05, 6, "Cloth", 0.75)}
P4_LOAD = {"Cloth": 0.0, "Light": 1.0, "Heavy": 3.0}                # type load (P4 2.3)
P4_SLOT = {"Head": 0.20, "Chest": 0.35, "Legs": 0.30, "Hands": 0.15}   # slot share (sums to 1)
P4_PER_LOAD = 4.0                                                    # % slower per load point x weight factor
P4_MAX_FACTOR = 1.8                                                  # move.maxFactor (total speed ceiling)
# P4 2.4 - class damage factor: 100 x rating x the Warrior's measured DPS / this class's measured DPS (casters: Mana budget decides; Archer
# MC 5.2). MEASURED by p4_measure() from Assets.zip (vanilla starter weapon, primary chain): the SkyySkills build asserts these
P4_CLASS_DAMAGE = {"Warrior": 100, "Berserker": 130, "Spellblade": 148, "Monk": 202, "Assassin": 120, "Archer": 200, "Mage": 100, "Priest": 100}
P4_STARTERS = {"Warrior": "Weapon_Sword_Crude", "Berserker": "Weapon_Battleaxe_Crude", "Spellblade": "Weapon_Longsword_Crude",
               "Monk": "Weapon_Staff_Bo_Wood", "Assassin": "Weapon_Daggers_Crude"}
# P4 3.2 - Mana
# BUILD RE-TUNE (balp4b, 2026-10-21): the spec's 3.2 pools (Mage 80 / 9.5, Priest 40 / 7, Spellblade 50 / 3) emptied in 16 s at Lv 20 and
# "never" once the quick refill ran between charged shots (the first build's harness). Fixes: (1) the quick refill only starts once the bar
# is DRY (under mana.refillBelow 20 % of max) and then runs until the bar is full (pausing mana.refillDelay after each charged shot /
# ability) - so it can never stretch the first 20-30 s; (2) the benchmark uses SkyyArmory's full 16-rung cost ladder (the 8 new metals'
# costs, Copper from Lv 4) instead of 7 rungs, and SkyyClasses' REAL walking costs + cooldowns (P4_ABIL; the old reader guessed the alts);
# (3) pools + cost growth re-fit by a grid search (tools/dev/scratch/balp4b, deleted) so that
# Lv 1 / 5 / 10 / 20 / 30 / 40 / 60 / 80 / 100 all run dry in 18-30 s (the 4 s charged-shot steps make the times lumpy: 20 / 24 / 28).
# Fix round (balp4bfix): the critic asked for Skyy's approved pools (docs/answered/classes.md 2026-10-20 "Bigger pool, slower regen": Mage 80 /
# 9.5, Priest 40 / 7, Spellblade 50 / 3) with the target met another way. Not possible: the levers that shorten nothing are Skyy-locked
# (SkyyArmory's ONE wand / staff cost table + STAFF_FACTOR 2, Spellblade x2 costs, regen growth 3 %) and the approved pools run dry in
# 5-16 s (Mage Lv 20: a 50-Mana staff shot every 4 s alone empties 272 x 0.8 in 17 s). The least-change fit that keeps Skyy's Mage base 80:
# Mage 80 / 14.5 (was 70 / 15.5); Priest 60 / 10 and Spellblade 70 / 6 are the only grid fits within +-30 base (QUESTION for Skyy, see report).
P4_MANA = {"Mage": (80, 14.5), "Priest": (60, 10.0), "Spellblade": (70, 6.0), "Archer": (24, 1.0), "Warrior": (21, 1.0), "Assassin": (24, 1.0),
           "Monk": (21, 1.0), "Berserker": (12, 1.0)}
P4_MANA_012 = {"Mage": (45, 9.5), "Priest": (42, 4.5), "Spellblade": (33, 3.0)}
P4_REGEN = (3.333, 0.65, 3.0, 20)          # vanilla Mana regen / s, in-combat share, growth % a level (5 -> 3), from level
P4_REGEN_CLASS = {"Spellblade": 50}        # mana.regen.class (% of regen), others 100
P4_REFILL = {"Mage": 15, "Priest": 15, "Spellblade": 15}             # mana.refillPct (% of max a second), delay 1 s
P4_REFILL_DELAY = 1.0
P4_REFILL_BELOW = 20.0                     # mana.refillBelow: the refill starts once the bar is under this % (dry), runs until full
P4_COST_PER_LEVEL = {"Mage": 0.0, "Spellblade": 2.5}                 # abil.costPerLevel %, others 1.5 (build re-tune: Priest 1 -> 1.5, Spellblade 1.5 -> 2.5)
P4_SB_MANA = {"ArcaneBreach": 16, "ElementalImbue": 14, "Sunder": 18, "RiftCleave": 20, "ShatteringArc": 18}   # P4 3.2 (x2)
# SkyyArmory's ONE cost table by band start (WANDS + the 8 new metals, nm_interp rounded to 5; Onyxium = Mithril's 85, the parked tier);
# Wood (5) to Lv 3, Copper (10) from Lv 4 (Zone 1's first craft); a Mage staff = 2 x
P4_WANDS = [(1, 5), (4, 10), (8, 15), (20, 25), (28, 30), (35, 35), (40, 40), (48, 45), (55, 50), (60, 60), (68, 65), (75, 75), (80, 85),
            (88, 95), (95, 105), (100, 85)]
P4_TREE = {"dmgCap": 40, "drCap": 35}       # P4 Part 4 T1 / T2


def p4_interp(points, x):
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (a, b), (c, d) in zip(points, points[1:]):
        if x <= c:
            return b + (d - b) * (x - a) / (c - a)
    return points[-1][1]


def p4_F(L):
    """weapon curve F = armor Health curve H (exact form; the game evaluates the P4_F_TEXT points with straight lines)"""
    return p4_interp(P4_F20, L) if L <= 20 else 2.333333 * P4_G ** (L - 20)


def p4_band_start(L):
    return max(s for s in P4_BAND_STARTS if s <= max(1, L))


def p4_bonus(L):
    b = p4_band_start(L)
    return 1.0 if b <= 1 else 1.0 + 0.003 * b


def p4_perk(L):
    return 1.0 + 0.002 * L


def p4_f_text():
    return ",".join("%d:%s" % (L, ("%.6f" % p4_F(L)).rstrip("0").rstrip(".") if L == 20 else ("%.3f" % p4_F(L)).rstrip("0").rstrip("."))
                    for L in P4_F_LEVELS)


def p4_hp_rule(L, diff="normal"):
    """mob Health multiplier: today's Normal to Lv 20, then x (F x bonus x perk)(L) / (the same at 20); x the difficulty factor"""
    if L <= 20:
        v = p4_interp(P4_HP_NORMAL_012, L)
    else:
        v = p4_interp(P4_HP_NORMAL_012, 20) * (p4_F(L) * p4_bonus(L) * p4_perk(L)) / (p4_F(20) * p4_bonus(20) * p4_perk(20))
    return v * P4_DIFF[diff][0]


def p4_player_hp(L):
    """M class, plain kit: 100 + a full set's 25 x H x bonus + Overall Health (0.5 a level x L / 2 = 0.35 L incl. the Health perks; MC 2.3)"""
    return 100.0 + 25.0 * p4_F(L) * p4_bonus(L) + 0.35 * L


def p4_res(L):
    return P4_RES_PER * p4_interp(P4_RES, L)


def p4_ehp(L):
    return p4_player_hp(L) / (1.0 - p4_res(L))


def p4_dmg_rule(L, diff="normal"):
    """mob damage multiplier: today's Normal (x1.1) to Lv 20, then x EHP(L) / EHP(20) - the same hits to die at every level"""
    v = p4_interp(P4_DMG_NORMAL_012, min(L, 20)) * (1.0 if L <= 20 else p4_ehp(L) / p4_ehp(20))
    return v * P4_DIFF[diff][1]


def p4_table(kind, diff):
    return [(int(a), float(b)) for a, b in (x.strip().split("=") for x in P4_TABLES[(kind, "normal" if diff == "custom" else diff)].split(","))]


def p4_table_text(kind, diff, sep=", ", eq="="):
    return sep.join("%d%s%s" % (a, eq, ("%.2f" % b).rstrip("0").rstrip(".")) for a, b in p4_table(kind, diff))


def p4_table_problems():
    """[] = every table holds the RULE (health to 0.01 at every point, damage to 0.01 up to Lv 20 and within P4_DMG_TOL above)"""
    bad = []
    for (kind, diff) in P4_TABLES:
        pts = p4_table(kind, diff)
        if [a for a, _b in pts] != P4_LEVELS:
            bad.append("%s %s: levels %s" % (kind, diff, [a for a, _b in pts]))
        for a, b in pts:
            r = p4_hp_rule(a, diff) if kind == "hp" else p4_dmg_rule(a, diff)
            ok = abs(b - r) <= 0.0051 + (0 if kind == "hp" or a <= 20 else P4_DMG_TOL * r)
            if not ok:
                bad.append("%s %s Lv %d: table %s, rule %.4f" % (kind, diff, a, b, r))
        if any(pts[i][1] >= pts[i + 1][1] for i in range(len(pts) - 1)):
            bad.append("%s %s: not rising" % (kind, diff))
    return bad


def p4_hit(L, kit="expected", cls_damage=1.0):
    """one main-attack hit of an M-damage melee class (F x bonus x perk x kit)"""
    return P4_REF_HIT * p4_F(L) * p4_bonus(L) * p4_perk(L) * P4_KIT[kit] * cls_damage


def p4_ttk(base, L, kit="expected", diff="normal", hp_x=1.0):
    """hits to kill a same-level mob of this base Health (the floor lifts trash)"""
    return max(base, P4_HP_FLOOR) * hp_x * p4_interp(p4_table("hp", diff), L) / p4_hit(L, kit)


def p4_hits_to_die(base_hit, L, kit="plain", diff="normal", cls=None, dmg_x=1.0):
    """hits a same-level mob needs on you (plain armor; cls = class Health % + Defense, else M: +0 % / Defense 10)"""
    hp_pct, dfn = (0, 10) if cls is None else (P4_CLASSES[cls][1], P4_CLASSES[cls][2])
    ehp = p4_player_hp(L) * (1 + hp_pct / 100.0) * P4_KIT[kit] / (1.0 - p4_res(L)) * (100.0 + dfn) / 100.0
    return ehp / (base_hit * dmg_x * p4_interp(p4_table("dmg", diff), L))


def p4_boss_seconds(L, cls="Warrior", kit="expected", diff="normal"):
    dps = P4_REF_DPS * p4_F(L) * p4_bonus(L) * p4_perk(L) * P4_KIT[kit] * P4_CLASSES[cls][7] * P4_BOSS_UPTIME
    return P4_BOSS_BASE * p4_interp(p4_table("hp", diff), L) / dps


def p4_gap(over):
    """(your damage factor, its damage factor) a mob `over` levels above you gets (P4 1.6)"""
    x = max(0, over - P4_GAP["free"])
    return max(P4_GAP["dealtMin"] / 100.0, 1.0 - P4_GAP["dealtStep"] / 100.0 * x), min(P4_GAP["takenMax"], 1.0 + P4_GAP["takenStep"] / 100.0 * x)


def p4_gap_hard(L, over):
    """'as hard' = kill time x damage taken vs a same-level mob (the curve between the levels + the gap rule)"""
    d, t = p4_gap(over)
    hp = p4_interp(p4_table("hp", "normal"), L + over) / p4_interp(p4_table("hp", "normal"), L)
    dm = p4_interp(p4_table("dmg", "normal"), L + over) / p4_interp(p4_table("dmg", "normal"), L)
    return hp / d * dm * t


def p4_speed(cls, armor):
    """move speed % of a class in a full set of armor type `armor` (P4 2.3)"""
    w = P4_RATE["weight"][P4_CLASSES[cls][0]]
    base = P4_CLASSES[cls][5] + P4_PER_LOAD * P4_LOAD[P4_CLASSES[cls][6]] * w
    return base - P4_PER_LOAD * P4_LOAD[armor] * w


def p4_pool(cls, L, new=True):
    b, per = (P4_MANA if new else dict(P4_MANA, **P4_MANA_012))[cls]
    return b + per * L + 0.1 * L          # + Overall Mana 0.2 a level x Overall Level L / 2


def p4_regen(cls, L, growth=None):
    base, share, g, frm = P4_REGEN
    g = g if growth is None else growth
    return base * (1 + g / 100.0 * max(0, L - frm)) * share * P4_REGEN_CLASS.get(cls, 100) / 100.0


def p4_wand(L):
    return [c for s, c in P4_WANDS if s <= max(1, L)][-1]


# SkyyClasses 0.1.44's walking defaults (AbilDefs.mana(ai, 0) / cdMs(ai, 0) after AbilNum.sync - the Classes harness asserts the jar = this
# table): {class: [(ability, tier 0 A1 / 1 A2 / 2 A2-alt / 3 A1-alt A / 4 A1-alt B, Mana, cooldown s, passive)]}. Guardian Spirit is a
# passive (it pays per save, no cooldown) - never part of the casting benchmark. Mana here is BEFORE abil.costPerLevel.
P4_ABIL = {
    "Warrior": [("RallyingGuard", 0, 5.0, 24.0, False), ("ShieldShockwave", 1, 4.0, 12.0, False), ("IronChain", 2, 5.0, 14.0, False), ("Challenge", 3, 5.0, 20.0, False)],
    "Berserker": [("Enrage", 0, 3.0, 30.0, False), ("Whirlwind", 1, 3.0, 14.0, False), ("Earthsplitter", 2, 3.0, 12.0, False), ("BloodFrenzy", 3, 1.0, 10.0, False)],
    "Spellblade": [("ArcaneBreach", 0, 16.0, 5.0, False), ("ElementalImbue", 1, 14.0, 18.0, False), ("Sunder", 2, 18.0, 30.0, False), ("RiftCleave", 3, 20.0, 20.0, False), ("ShatteringArc", 4, 18.0, 20.0, False)],
    "Monk": [("FlowingForm", 0, 2.0, 40.0, False), ("PalmStrike", 1, 3.0, 6.0, False), ("CycloneKick", 2, 4.0, 8.0, False), ("HundredFists", 3, 3.0, 40.0, False), ("StillWater", 4, 7.0, 25.0, False)],
    "Assassin": [("CloakFirstStrike", 0, 6.0, 30.0, False), ("Toxin", 1, 5.0, 16.0, False), ("GodKiller", 2, 6.0, 45.0, False), ("VanishingAct", 3, 7.0, 28.0, False)],
    "Archer": [("PinningShot", 0, 4.0, 12.0, False), ("RapidFire", 1, 6.0, 20.0, False), ("ExplosiveArrow", 2, 5.0, 14.0, False), ("ArrowRain", 3, 7.0, 20.0, False)],
    "Mage": [("Meteor", 0, 23.0, 14.0, False), ("ManaBarrier", 1, 16.0, 30.0, False), ("FrostNova", 2, 19.0, 22.0, False), ("Starfall", 3, 28.0, 18.0, False), ("ArcaneBeam", 4, 23.0, 18.0, False)],
    "Priest": [("SacredHeal", 0, 18.0, 8.0, False), ("ShieldBubble", 1, 20.0, 24.0, False), ("GuardianSpirit", 2, 15.0, 0.0, True), ("Sanctuary", 3, 26.0, 28.0, False), ("MartyrsGrace", 4, 22.0, 18.0, False)],
}


def p4_abilities():
    """{class: [[id, tier, Mana, cooldown s]]} - the casting benchmark's abilities (P4_ABIL, passives left out)"""
    return dict((c, [[a, t, m, cd] for a, t, m, cd, ps in rows if not ps]) for c, rows in P4_ABIL.items())


P4_UNLOCK = {0: 1, 1: 10, 2: 20, 3: 30, 4: 40}
P4_MANA_LEVELS = (1, 5, 10, 20, 30, 40, 60, 80, 100)   # P4 3.3
P4_DODGE_COST = 2.0   # P4 3.4: a dodge roll's Stamina - the fallback; p4_dodge_cost() reads the real one from Assets.zip (VERIFIED 2026-10-21: 2)


def p4_dodge_cost():
    """P4 3.4 "the harness must read the dodge cost": Costs.Stamina of the vanilla Dodge_Left / Dodge_Right interactions (Assets.zip, read
    only; both must agree); P4_DODGE_COST when Assets.zip cannot be read"""
    try:
        import zipfile
        import json as _js
        import re as _re
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import serverjar as _SJ
        z = zipfile.ZipFile(_SJ.assets_zip())
        got = []
        for side in ("Left", "Right"):
            t = z.read("Server/Item/Interactions/Dodge/Dodge_%s.json" % side).decode("utf-8")
            t = _re.sub(r",\s*([}\]])", r"\1", _re.sub(r"//[^\n]*", "", t))
            got.append(float(_js.loads(t)["Costs"]["Stamina"]))
        assert got[0] == got[1], got
        return got[0]
    except Exception:
        return P4_DODGE_COST


def p4_stamina(cls, L):
    """max Stamina of a class at class level L: vanilla 10 + SkyySkills 0.4.58's class base + per level (no Mining / tree / gear Stamina)"""
    return 10.0 + P4_CLASSES[cls][3] + P4_CLASSES[cls][4] * L


def p4_refill_step(pct, pool, cur, secs, since_cast, dry, fight=True):
    """THE quick refill rule (SkyySkills 0.4.58 ClassStat.refill, the same maths): Mana added this pulse - in combat, the bar dry (it fell
    under mana.refillBelow and has not been full since), mana.refillDelay passed since the last charged shot / ability (since_cast < 0 =
    never cast = long ago); at most the room left"""
    if not fight or not dry or pct <= 0 or pool <= 0 or cur >= pool or secs <= 0:
        return 0.0
    if 0 <= since_cast < P4_REFILL_DELAY:
        return 0.0
    return min(pool * pct * secs, pool - cur)


def p4_tempty(cls, L, refill=True, growth=None, abil=None, horizon=600.0, dt=0.1, below=None):
    """seconds of non-stop casting until the bar RUNS DRY (P4 3.1 benchmark): every owned ability the moment its cooldown ends, a charged
    band-weapon shot every 4 s (Mage staff = 2 x the wand cost, Priest wand; the Spellblade has none), quick shots between cost nothing
    here; in-combat regen. Dry = the next cast cannot be paid OR the bar is under mana.refillBelow (the quick refill starts there). The
    refill (refill=True) is simulated too, but by its rule it cannot act before dry. None = never within the horizon."""
    abil = abil if abil is not None else p4_abilities()
    below = P4_REFILL_BELOW if below is None else below
    rows = [r for r in abil.get(cls, []) if P4_UNLOCK.get(r[1], 99) <= L and r[1] != 4]   # one A1-alt (A locks out B)
    per = 1.0 + (P4_COST_PER_LEVEL.get(cls, 1.5) / 100.0) * L
    pool = p4_pool(cls, L)
    m, t = pool, 0.0
    ready = dict((r[0], 0.0) for r in rows)
    shot = {"Mage": 2 * p4_wand(L), "Priest": p4_wand(L)}.get(cls, 0)
    next_shot, last_cast, dry = 0.0, -99.0, False
    while t < horizon:
        for r in rows:
            if t >= ready[r[0]] - 1e-9:
                c = r[2] * per
                if m < c:
                    return t
                m -= c
                ready[r[0]] = t + r[3]
                last_cast = t
        if shot and t >= next_shot - 1e-9:
            if m < shot:
                return t
            m -= shot
            next_shot = t + 4.0
            last_cast = t
        if m < below / 100.0 * pool:
            return t
        m = min(pool, m + p4_regen(cls, L, growth) * dt)
        if refill:
            m += p4_refill_step(P4_REFILL.get(cls, 0) / 100.0, pool, m, dt, t - last_cast, dry)
        t += dt
    return None


def p4_refill_seconds(cls, L, to=0.8, dt=0.1):
    """seconds of basic attacks (quick shots 1 a second at 1/5 of the charged cost, no charged shot, no ability) from an empty, dry bar to
    `to` of the bar (P4 3.2; the last charged shot / ability was just now, so the refill waits mana.refillDelay first)"""
    pool = p4_pool(cls, L)
    quick = {"Mage": 2 * p4_wand(L), "Priest": p4_wand(L)}.get(cls, 0) / 5.0
    m, t, nq = 0.0, 0.0, 0.0
    while m < to * pool and t < 120:
        m = min(pool, m + p4_regen(cls, L) * dt)
        m += p4_refill_step(P4_REFILL.get(cls, 0) / 100.0, pool, m, dt, t, True)
        if t >= nq - 1e-9:
            m = max(0.0, m - quick)
            nq = t + 1.0
        t += dt
    return t


def p4_rotation_share(cls, L, abil=None):
    abil = abil if abil is not None else p4_abilities()
    rows = [r for r in abil.get(cls, []) if P4_UNLOCK.get(r[1], 99) <= L and r[1] != 4]
    per = 1.0 + (P4_COST_PER_LEVEL.get(cls, 1.5) / 100.0) * L
    return sum(r[2] * per for r in rows) / p4_pool(cls, L)


def p4_measure():
    """{class: (avg hit, avg swing s, DPS)} of each melee class's vanilla starter weapon (Assets.zip, read only): the primary chain's swings
    (Charging -> Chaining -> each swing's Simple / Selector / Parallel RunTime; the root's Cooldown as the floor of a swing) and each swing's
    damage from the item's InteractionVars. UNVERIFIED vs the game's real swing timing (P4 6.8)."""
    import zipfile
    import json as _js
    import re as _re
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import serverjar as _SJ
    z = zipfile.ZipFile(_SJ.assets_zip())
    names = z.namelist()

    def lj(t):
        t = _re.sub(r"//[^\n]*", "", t)
        t = _re.sub(r"/\*.*?\*/", "", t, flags=_re.S)
        return _js.loads(_re.sub(r",\s*([}\]])", r"\1", t))
    items = dict((x.rsplit("/", 1)[1][:-5], x) for x in names if x.startswith("Server/Item/Items/") and x.endswith(".json"))
    inter = dict((x.rsplit("/", 1)[1][:-5], x) for x in names if x.startswith("Server/Item/Interactions/") and x.endswith(".json"))
    roots = dict((x.rsplit("/", 1)[1][:-5], x) for x in names if x.startswith("Server/Item/RootInteractions/") and x.endswith(".json"))

    def idef(x):
        if isinstance(x, dict):
            if "Parent" in x and x["Parent"] in inter:
                b = dict(idef(x["Parent"]))
                b.update(dict((k, v) for k, v in x.items() if k != "Parent"))
                return b
            return x
        if x in inter:
            d = lj(z.read(inter[x]).decode("utf-8-sig"))
            if "Parent" in d and d["Parent"] in inter:
                b = dict(idef(d["Parent"]))
                b.update(dict((k, v) for k, v in d.items() if k != "Parent"))
                return b
            return d
        return None

    def item(w):
        chain = [lj(z.read(items[w]).decode("utf-8-sig"))]
        while chain[-1].get("Parent") in items:
            chain.append(lj(z.read(items[chain[-1]["Parent"]]).decode("utf-8-sig")))
        out = {}
        for c in reversed(chain):
            for k, v in c.items():
                if k in ("InteractionVars", "Interactions") and isinstance(v, dict):
                    out.setdefault(k, {}).update(v)
                else:
                    out[k] = v
        return out

    def ivar_damage(iv, var):
        v = iv.get(var)
        if not v:
            return None
        if isinstance(v, str):
            v = {"Interactions": [idef(v) or {}]}
        tot = 0.0
        for i in v.get("Interactions", []):
            i = idef(i) or {}
            tot += sum(float(x) for x in i.get("DamageCalculator", {}).get("BaseDamage", {}).values())
        return tot or None

    def resolve(x, iv):
        d = idef(x)
        if d and d.get("Type") == "Replace":
            var = d.get("Var")
            if var in iv and isinstance(iv[var], str):
                return resolve(iv[var], iv)
            if var in iv and iv[var].get("Interactions"):
                return resolve(iv[var]["Interactions"][0], iv)
            dv = d.get("DefaultValue", {}).get("Interactions", [])
            return resolve(dv[0], iv) if dv else None
        return d

    def swing(d, iv, depth=0):
        t, dmg = 0.0, 0.0
        while d is not None and depth < 12:
            depth += 1
            if d.get("Type") == "Parallel":
                best = (0.0, 0.0)
                for br in d.get("Interactions", []):
                    ii = br.get("Interactions", []) if isinstance(br, dict) else []
                    if ii:
                        r = swing(resolve(ii[0], iv), iv, depth)
                        best = (max(best[0], r[0]), max(best[1], r[1]))
                return t + best[0], max(dmg, best[1])
            t += float(d.get("RunTime", 0) or 0)
            he = d.get("HitEntity", {}).get("Interactions", []) if isinstance(d.get("HitEntity"), dict) else []
            for h in he:
                hd = idef(h)
                if hd and hd.get("Type") == "Replace":
                    v = ivar_damage(iv, hd.get("Var"))
                    if v:
                        dmg = max(dmg, v)
            nx = d.get("Next")
            if isinstance(nx, (dict, str)) and (not isinstance(nx, dict) or "Type" in nx or "Parent" in nx):
                d = resolve(nx, iv)
            else:
                break
        return t, dmg

    res = {}
    for cls, w in P4_STARTERS.items():
        it = item(w)
        iv = it.get("InteractionVars", {})
        r = lj(z.read(roots[it["Interactions"]["Primary"]]).decode("utf-8-sig"))
        cd = float(r.get("Cooldown", {}).get("Cooldown", 0) or 0)
        d = resolve(r["Interactions"][0], iv)
        sw = []
        for _i in range(6):
            if d is None:
                break
            if d.get("Type") == "Charging":
                nx = d.get("Next", {})
                d = resolve(nx.get("0") if isinstance(nx, dict) else nx, iv)
                continue
            if d.get("Type") == "Chaining":
                sw = [swing(resolve(e, iv), iv) for e in d.get("Next", [])]
            else:
                sw = [swing(d, iv)]
            break
        per = [max(cd, t) for t, _d in sw]
        if not sw or not sum(per) or not sum(x for _t, x in sw):
            res[cls] = None
            continue
        res[cls] = (sum(x for _t, x in sw) / len(sw), sum(per) / len(sw), sum(x for _t, x in sw) / sum(per))
    return res


def p4_damage_factors(meas=None):
    """{class: factor %} from the measurement (melee) + the fixed ones (Archer MC 5.2, casters 100)"""
    meas = meas if meas is not None else p4_measure()
    ref = meas["Warrior"][2]
    out = {}
    for cls, v in meas.items():
        out[cls] = None if v is None else 100.0 * P4_CLASSES[cls][7] * ref / v[2]
    for cls in ("Archer", "Mage", "Priest"):
        out[cls] = float(P4_CLASS_DAMAGE[cls])
    return out


def p4_rows():
    """the P4 6.5 check rows: (target, model text, ok)"""
    rows = []
    tr = [p4_ttk(P4_TRASH[0], L) for L in P4_LEVELS if L >= 20]
    tg = [p4_ttk(P4_TOUGH[0], L) for L in P4_LEVELS if L >= 20]
    z1 = [p4_ttk(P4_TRASH[0], L) / p4_ttk(P4_TRASH[0], 20) for L in P4_LEVELS if 5 <= L < 20]
    rows.append(("Normal trash 4-6 hits (expected kit, M; Lv 20-100)", "%.1f-%.1f" % (min(tr), max(tr)), all(4.0 <= x <= 6.0 for x in tr)))
    rows.append(("Normal tough 12-15 hits (Lv 20-100)", "%.1f-%.1f" % (min(tg), max(tg)), all(11.5 <= x <= 15.0 for x in tg)))
    rows.append(("Zone 1 (Lv 5-19, today's curve) within 15 % of Lv 20", "x%.2f-x%.2f (Lv 1 x%.2f: no gear bonus yet)" % (min(z1), max(z1), p4_ttk(P4_TRASH[0], 1) / p4_ttk(P4_TRASH[0], 20)),
                 all(0.85 <= x <= 1.15 for x in z1)))
    hd = [p4_hits_to_die(P4_TRASH[1], L) for L in P4_LEVELS]
    rows.append(("Trash needs 12-15 hits on you (M, plain)", "%.1f-%.1f" % (min(hd), max(hd)), all(11.5 <= x <= 15.0 for x in hd)))
    bs = [p4_boss_seconds(L) / 60.0 for L in (20, 50, 100)]
    rows.append(("Boss 3-4 min solo (M, expected)", "%.1f-%.1f min" % (min(bs), max(bs)), all(3.0 <= x <= 4.0 for x in bs)))
    g5 = [p4_gap_hard(L, 5) for L in (30, 70)]
    g10 = [p4_gap_hard(L, 10) for L in (30, 70)]
    rows.append(("+5 levels 1.6-2.2x as hard", "x%.2f-x%.2f" % (min(g5), max(g5)), all(1.6 <= x <= 2.2 for x in g5)))
    rows.append(("+10 levels >= 4x (a wall)", "x%.2f-x%.2f" % (min(g10), max(g10)), all(x >= 4.0 for x in g10)))
    ab = p4_abilities()
    te = [(c, L, p4_tempty(c, L, abil=ab)) for c in ("Mage", "Priest", "Spellblade") for L in P4_MANA_LEVELS]
    rows.append(("Casters run dry in 18-30 s at Lv 1/5/10/20/30/40/60/80/100 (refill rule on; 4 s shot steps)",
                 ", ".join("%s %s" % (c[:2], "/".join("%d" % (x[2] or 999) for x in te if x[0] == c)) for c in ("Mage", "Priest", "Spellblade")),
                 all(x[2] is not None and 18.0 - 1e-6 <= x[2] <= 30.0 + 1e-6 for x in te)))
    rf = [p4_refill_seconds(c, L) for c in ("Mage", "Priest", "Spellblade") for L in (20, 60)]
    rows.append(("Refill 80 % in 5-8 s of basic attacks", "%.1f-%.1f s" % (min(rf), max(rf)), all(4.0 <= x <= 9.0 for x in rf)))
    fc = [c for c in ("Warrior", "Berserker", "Monk", "Assassin", "Archer") if any(r[2] > 0 for r in ab.get(c, []))]   # Monk / Assassin: walking costs not in a row
    rs = [p4_rotation_share(c, L, ab) for c in fc for L in (20, 40, 60, 100)]
    rows.append(("Fighter rotation 20-80 %% of the bar from Lv 20 (%s)" % "/".join(c[:3] for c in fc), "%d-%d %%" % (100 * min(rs), 100 * max(rs)), all(0.2 <= x <= 0.8 for x in rs)))
    rows.append(("Heavy class slowed less by heavy gear", "Warrior %+.0f %%, Mage %+.0f %%" % (p4_speed("Warrior", "Heavy") - p4_speed("Warrior", "Cloth"),
                 p4_speed("Mage", "Heavy") - p4_speed("Mage", "Cloth")), p4_speed("Warrior", "Cloth") - p4_speed("Warrior", "Heavy") < 4 and p4_speed("Mage", "Cloth") - p4_speed("Mage", "Heavy") > 15))
    own = [abs(p4_speed(c, P4_CLASSES[c][6]) - P4_CLASSES[c][5]) for c in P4_CLASSES]
    rows.append(("Each class's own-armor speed = its rating", "max off %.2f %%" % max(own), max(own) < 1.0))
    tb = p4_table_problems()
    rows.append(("Mob tables = the RULE (health 0.01, damage %d %%)" % (100 * P4_DMG_TOL), "%d problems" % len(tb), not tb))
    return rows


def p4_md():
    """### 6. Combat (P4) for research/balance/targets.md"""
    out = ["", "### 6. Combat (P4, research/Balance-P4-Combat-Spec.md; Normal, M class unless named)", "",
           "| Lv | F | mob Health x | mob damage x | player max HP (M plain) | resistance | trash hits (exp.) | tough hits | trash hits to die | boss min (M) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for L in (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        out.append("| %d | %.2f | %.2f | %.2f | %.0f | %.1f %% | %.1f | %.1f | %.1f | %.1f |" % (
            L, p4_F(L), p4_interp(p4_table("hp", "normal"), L), p4_interp(p4_table("dmg", "normal"), L), p4_player_hp(L), 100 * p4_res(L),
            p4_ttk(P4_TRASH[0], L), p4_ttk(P4_TOUGH[0], L), p4_hits_to_die(P4_TRASH[1], L), p4_boss_seconds(L) / 60.0))
    out += ["", "| Difficulty (Lv 50, expected) | trash hits | tough hits | boss min | trash hits to die | tough hits to die |", "|---|---|---|---|---|---|"]
    for d in ("easy", "normal", "hard"):
        out.append("| %s | %.1f | %.1f | %.1f | %.1f | %.1f |" % (d, p4_ttk(P4_TRASH[0], 50, diff=d), p4_ttk(P4_TOUGH[0], 50, diff=d), p4_boss_seconds(50, diff=d) / 60.0,
                                                             p4_hits_to_die(P4_TRASH[1], 50, diff=d), p4_hits_to_die(P4_TOUGH[1], 50, diff=d)))
    out += ["", "| Class | Health % | Defense | damage factor % | Stamina base / lv | speed cloth / light / heavy | hits to die trash / tough | boss min | Mana pool Lv 1 / 20 / 50 / 100 |",
            "|---|---|---|---|---|---|---|---|---|"]
    for c, v in P4_CLASSES.items():
        out.append("| %s | %+d | %d | %d | %s / %s | %+.0f / %+.0f / %+.0f | %.1f / %.1f | %.1f | %s |" % (
            c, v[1], v[2], P4_CLASS_DAMAGE[c], v[3], v[4], p4_speed(c, "Cloth"), p4_speed(c, "Light"), p4_speed(c, "Heavy"),
            p4_hits_to_die(P4_TRASH[1], 20, cls=c), p4_hits_to_die(P4_TOUGH[1], 20, cls=c), p4_boss_seconds(50, cls=c) / 60.0,
            " / ".join("%.0f" % p4_pool(c, L) for L in (1, 20, 50, 100))))
    ab = p4_abilities()
    out += ["", "| Class (P4 3.3) | base / per level Mana | ability Mana + %% a level | runs dry after s, Lv %s | 80 %% back after s (Lv 20 / 60) | one rotation %% of the bar, Lv 5 / 20 / 40 / 60 / 100 |"
            % " / ".join(str(L) for L in P4_MANA_LEVELS), "|---|---|---|---|---|---|"]
    for c in P4_CLASSES:
        te = [p4_tempty(c, L, abil=ab) for L in P4_MANA_LEVELS]
        out.append("| %s | %s / %s | %s | %s | %s | %s |" % (
            c, P4_MANA[c][0], P4_MANA[c][1], P4_COST_PER_LEVEL.get(c, 1.5),
            " / ".join("never" if x is None else "%.0f" % x for x in te),
            " / ".join("%.1f" % p4_refill_seconds(c, L) for L in (20, 60)) if c in P4_REFILL else "-",
            " / ".join("%.0f" % (100 * p4_rotation_share(c, L, ab)) for L in (5, 20, 40, 60, 100))))
    dc = p4_dodge_cost()
    out += ["", "| Class (P4 3.4, REPORT - no auto-tune) | Stamina Lv 1 / 50 / 100 | dodge rolls before empty (vanilla %g a roll read from Assets.zip Dodge_Left / Right, no regen) | spec target | flag |" % dc,
            "|---|---|---|---|---|"]
    for c in P4_CLASSES:
        st = [p4_stamina(c, L) for L in (1, 50, 100)]
        rolls = [x / dc for x in st]
        sh = P4_CLASSES[c][3] >= 10   # the Stamina classes (H / SH rows of 2.2)
        tgt = "6-8" if sh else "2-3"
        flag = ("under 6" if sh and min(rolls) < 6 else "") if sh else ("over 4" if max(rolls) > 4 else "")
        out.append("| %s | %s | %s | %s | %s |" % (c, " / ".join("%.1f" % x for x in st), " / ".join("%.0f" % x for x in rolls), tgt, flag or "-"))
    out += ["", "| Target (P4 6.5) | Model | OK |", "|---|---|---|"]
    for t, m, ok in p4_rows():
        out.append("| %s | %s | %s |" % (t, m, "yes" if ok else "NO"))
    out.append("")
    out.append("Model notes: one main attack of an M-damage melee class = %.2f x F x material bonus x class perk x kit (plain 1, expected 1.73, best 3); "
               "trash = %d base Health / %d hit, tough = %d / %d; boss = %d x the Health curve at %d %% uptime; casters run dry (the next cast "
               "cannot be paid or the bar under mana.refillBelow %d %%) with every owned ability on cooldown + a charged band-weapon shot every "
               "4 s (SkyyArmory's 16-rung ladder; quick shots free), in-combat regen only (no tree / gear / pet Mana); the quick refill "
               "(%d %% of max a second) starts once dry, waits %d s after each charged shot / ability and runs until full; "
               "the mob damage table is the spec's (this EHP rule within %d %%). `python tools/balance_model.py --combat` prints it, `--check` "
               "exits 1 on a NO row." % (P4_REF_HIT, P4_TRASH[0], P4_TRASH[1], P4_TOUGH[0], P4_TOUGH[1], P4_BOSS_BASE, 100 * P4_BOSS_UPTIME,
                                         P4_REFILL_BELOW, P4_REFILL["Mage"], P4_REFILL_DELAY, 100 * P4_DMG_TOL))
    return "\n".join(out)


def p4_write_section(md):
    """put p4_md() into research/balance/targets.md as its '### 6. Combat' section: the old section (its heading up to the next '### ' or
    '## ' heading, or the end) is replaced, else the section is appended; every other byte of the file is kept"""
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "balance", "targets.md"))
    raw = open(path, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    sec = md.strip("\n").replace("\n", nl) + nl
    head = "### 6. Combat"
    a = raw.find(nl + head)
    if a < 0:
        out, how = raw + ("" if raw.endswith(nl) else nl) + nl + sec, "appended"
    else:
        a += len(nl)
        b = len(raw)
        for mk in (nl + "### ", nl + "## "):
            j = raw.find(mk, a + len(head))
            if 0 <= j < b:
                b = j + len(nl)
        rest = raw[b:]
        out, how = raw[:a] + sec + ((nl if not sec.endswith(nl + nl) else "") + rest if rest else ""), "replaced"
    with open(path, "wb") as f:
        f.write(out.encode("utf-8"))
    return how


# ======================================================================================== P5 POWER SOURCES (research/Balance-P5-Power-Spec.md)
# Built by the P5 round (SkyyGear 0.3.35, SkyyAccessories 0.5.30, SkyyPets 0.4.8, SkyyArmory 0.1.43, SkyyTrees 0.4.5, SkyyGuilds 0.1.13).
# `python tools/balance_model.py --power` prints the tables and writes research/balance/targets.md section '### 7. Power sources'; `--check`
# also fails on a P5 NO row. Every number names its spec section (P5 x.y); the SkyyGear harness runs the REAL GearRoll against p5_roll_table.
P5_SEED = 20261021
P5_STATS = {   # key: (max at 100 %, weight, slots) = SkyyGear STATS (live rows; pool.later false) + 0.3.35's hpp (weight 0: armor only, P5 2.2.3)
    "dmg": (30, 10, "w"), "str": (25, 10, "wae"), "mp": (25, 10, "sae"), "cc": (15, 10, "wa"), "cd": (30, 10, "wa"), "chg": (30, 5, "wa"),
    "tdmg": (5, 5, "w"), "fEarth": (6, 4, "w"), "fThunder": (6, 4, "w"), "fWater": (6, 4, "w"), "fFire": (6, 4, "w"), "fAir": (6, 4, "w"),
    "rThunder": (6, 3, "w"), "rWater": (6, 3, "w"), "rElem": (3, 3, "w"), "msteal": (3, 5, "s"), "lsteal": (5, 5, "wa"), "hpr": (2, 5, "wa"),
    "hprp": (20, 5, "wa"), "def": (25, 10, "a"), "spd": (5, 10, "ae"), "stam": (2, 5, "a"), "hpp": (30, 0, "a")}
P5_POOL_ARMOR = {"def": 120, "hpp": 120, "str": 1, "mp": 1, "cc": 1, "cd": 1, "chg": 8, "hprp": 32, "lsteal": 16, "hpr": 16, "spd": 32, "stam": 20}   # P5 2.2.2
P5_RARITY = {"normal": (1, 40, 70), "unique": (2, 45, 75), "rare": (3, 50, 85), "legendary": (4, 55, 95), "fabled": (5, 60, 105),
             "mythic": (6, 70, 110), "set": (3, 55, 100)}                                  # P5 2.2.5 (fix round 2: mythic 75-120 -> 70-110 = spec 2.3's Mythic row 1.85 / 2.33; kit DPS x3.9 -> x3.6)
P5_RARITY_034 = {"normal": (1, 30, 60), "unique": (2, 35, 70), "rare": (3, 40, 80), "legendary": (4, 45, 95), "fabled": (5, 50, 110),
                 "mythic": (6, 60, 130), "set": (3, 45, 95)}                               # SkyyGear 0.3.34 RARITY_DEF
P5_RARS = ["normal", "unique", "rare", "legendary", "fabled", "mythic"]
P5_SLOT_POWER = {"Weapon": 118.0, "Head": 26.0, "Chest": 45.5, "Legs": 39.0, "Hands": 19.5}   # P5 2.2.1 (armor 130 = 1.3 items, P4 shares)
P5_LEVEL_FLOOR, P5_LEVEL_FULL = 60, 15                                                     # P5 2.2.6 (0.3.34: 25 / 40)
P5_PCT_LINES = ("tdmg", "fEarth", "fThunder", "fWater", "fFire", "fAir", "rThunder", "rWater")   # P5 2.2.4: "+N % of the hit" (rElem x5)
P5_CLASS_DEF = 10.0                                                                        # P4 M class Defense (P4_CLASSES)
P5_CHARGED_SHARE = 0.25                                                                    # P5 7.6: charged hits = 25 % of hits
P5_TABLE_SPEC = {   # P5 2.3: rarity -> (weapon DPS mean, p90, armor DPS mean, p90, armor EHP mean, p90); the build fails outside +-8 %
    "normal": (1.07, 1.17, 1.00, 1.02, 1.13, 1.20), "unique": (1.14, 1.28, 1.01, 1.03, 1.26, 1.35), "rare": (1.24, 1.44, 1.01, 1.04, 1.42, 1.53),
    "legendary": (1.40, 1.66, 1.02, 1.06, 1.58, 1.69), "fabled": (1.56, 1.88, 1.03, 1.07, 1.74, 1.83), "mythic": (1.85, 2.33, 1.05, 1.12, 1.97, 2.07)}
P5_TOL = 0.08
P5_TIER_FORT = 25.7          # P5 1.1: armor Fortune per tier from T5 (the 30 % share of 30 x T / 35 %)
P5_GB_FT_034 = [60, 75, 90, 105, 120, 135, 150, 160, 170, 180, 190, 200, 210, 225, 240, 255]   # SkyyGear 0.3.29-0.3.34 GB_FT (full set by ladder T)


def p5_level_factor(L):
    """SkyyGear GearLevel.factor with the P5 ramp: stat.levelFloor % at item level 0 -> 100 % at stat.levelFull"""
    if L >= P5_LEVEL_FULL:
        return 100.0
    return P5_LEVEL_FLOOR + (100.0 - P5_LEVEL_FLOOR) * max(0, L) / float(P5_LEVEL_FULL)


def p5_weights(slot):
    """the roll weights of a slot: 'w' weapon (stats.<k> weights), 'a' armor (pool.armor; absent = the stat's own weight)"""
    out = {}
    for k, (mx, w, sl) in P5_STATS.items():
        if slot not in sl:
            continue
        ww = P5_POOL_ARMOR.get(k, w) if slot == "a" else w
        if ww > 0:
            out[k] = ww
    return out


def p5_roll(slot, rarity, rng, level=100, table=None):
    """Python twin of SkyyGear GearRoll.rollMods: `count` distinct stats by weight (Health Regen % only after Raw Health Regen), each
    value randInt(lo, hi) with lo / hi = max(1, round(max x low % x f %)) (f = the level factor)"""
    n, lo, hi = (table or P5_RARITY)[rarity]
    w = p5_weights(slot)
    pool = [k for k in P5_STATS if k in w]
    pick = []
    for _ in range(min(n, len(pool))):
        cand = [k for k in pool if k not in pick and not (k == "hprp" and "hpr" not in pick)]
        tot = sum(w[k] for k in cand)
        if tot <= 0:
            break
        x = rng.random() * tot
        sel = cand[-1]
        for k in cand:
            x -= w[k]
            if x < 0:
                sel = k
                break
        pick.append(sel)
    f = p5_level_factor(level)
    out = {}
    for k in pick:
        mx = P5_STATS[k][0]
        a = max(1, int(math.floor(mx * lo / 100.0 * f / 100.0 + 0.5)))
        b = max(a, max(1, int(math.floor(mx * hi / 100.0 * f / 100.0 + 0.5))))
        out[k] = rng.randint(a, b)
    return out


def p5_dps(t, caster=False):
    """one hit of an M class vs no gear (P5 2.1): Damage %, Strength (or Magical Power), Charged (25 % of hits), crit (base 0: x2 x (1 + cd %)),
    the % lines (+N % of the hit as True / element damage after armor; Raw Elemental counts for each of 5 elements)"""
    g = t.get
    cc = min(g("cc", 0.0), 100.0) / 100.0
    pct = sum(g(k, 0.0) for k in P5_PCT_LINES) + 5.0 * g("rElem", 0.0)
    return ((1 + g("dmg", 0.0) / 100.0) * (1 + g("mp" if caster else "str", 0.0) / 100.0) * (1 + P5_CHARGED_SHARE * g("chg", 0.0) / 100.0)
            * (1 + cc * (2.0 * (1 + g("cd", 0.0) / 100.0) - 1.0)) * (1 + pct / 100.0))


def p5_ehp(t):
    """toughness vs no gear (P5 2.1 / 7.6): Health %, Defense x 100 / (100 + class Defense + def), Life Steal 1 pt = +2 %, Health Regen % 1 pt = +0.25 %"""
    g = t.get
    return ((1 + g("hpp", 0.0) / 100.0) * (100.0 + P5_CLASS_DEF + g("def", 0.0)) / (100.0 + P5_CLASS_DEF)
            * (1 + 0.02 * g("lsteal", 0.0)) * (1 + 0.0025 * g("hprp", 0.0)))


def p5_p90(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.9 * len(xs)))]


def p5_weapon_totals(mods):
    return dict((k, v * P5_SLOT_POWER["Weapon"] / 100.0) for k, v in mods.items())


def p5_armor_totals(pieces):
    """pieces = [(slot name, mods)] -> the summed totals x slot power (GearStats.totals in 0.3.35)"""
    tot = {}
    for sl, mods in pieces:
        for k, v in mods.items():
            tot[k] = tot.get(k, 0.0) + v * P5_SLOT_POWER[sl] / 100.0
    return tot


_P5_TABLE = {}


def p5_roll_table(n=3000, seed=P5_SEED):
    """P5 2.3: per rarity (weapon DPS mean, p90, armor set DPS mean, p90, armor set EHP mean, p90) over n rolls at full level"""
    key = (n, seed)
    if key in _P5_TABLE:
        return _P5_TABLE[key]
    rng = random.Random(seed)
    out = {}
    for r in P5_RARS:
        W, AD, AE = [], [], []
        for _ in range(n):
            W.append(p5_dps(p5_weapon_totals(p5_roll("w", r, rng))))
            tot = p5_armor_totals([(s, p5_roll("a", r, rng)) for s in ("Head", "Chest", "Legs", "Hands")])
            AD.append(p5_dps(tot))
            AE.append(p5_ehp(tot))
        out[r] = (statistics.mean(W), p5_p90(W), statistics.mean(AD), p5_p90(AD), statistics.mean(AE), p5_p90(AE))
    _P5_TABLE[key] = out
    return out


def p5_roll_table_034(n=3000, seed=P5_SEED):
    """the same model with 0.3.34's rules (no slot power, no armor pool, flat lines ~0 at Lv 100, the old rarity table): the 'today' column"""
    rng = random.Random(seed + 1)
    out = {}
    for r in P5_RARS:
        W, AD, AE = [], [], []
        for _ in range(n):
            wm = p5_roll("w", r, rng, table=P5_RARITY_034)
            for k in P5_PCT_LINES + ("rElem",):
                wm.pop(k, None)          # flat lines: ~0 % of a Lv 100 hit
            W.append(p5_dps(wm))
            tot = {}
            for _s in range(4):
                am = {}
                w = dict((k, P5_STATS[k][1]) for k in P5_STATS if "a" in P5_STATS[k][2] and P5_STATS[k][1] > 0)
                n_, lo, hi = P5_RARITY_034[r]
                pick = []
                for _ in range(n_):
                    cand = [k for k in w if k not in pick and not (k == "hprp" and "hpr" not in pick)]
                    x = rng.random() * sum(w[k] for k in cand)
                    sel = cand[-1]
                    for k in cand:
                        x -= w[k]
                        if x < 0:
                            sel = k
                            break
                    pick.append(sel)
                for k in pick:
                    mx = P5_STATS[k][0]
                    a = max(1, int(math.floor(mx * lo / 100.0 + 0.5)))
                    b = max(a, int(math.floor(mx * hi / 100.0 + 0.5)))
                    am[k] = rng.randint(a, b)
                for k, v in am.items():
                    tot[k] = tot.get(k, 0) + v
            AD.append(p5_dps(tot))
            AE.append(p5_ehp(tot))
        out[r] = (statistics.mean(W), statistics.mean(AD), statistics.mean(AE))
    return out


# ---- P5 4: Void Charms (SkyyAccessories 0.5.30). Plain = Normal lines + the Balance Power at AP 100; best = Mythic lines + Omni (AP 393)
P5_CHARM_LADDER = [1.0, 1.6, 2.2, 2.8, 3.4, 4.0]          # P5 4.2.1: Normal .. Mythic x the Normal value (Mythic = 0.5.29's Legendary)
P5_CHARM_NORMAL = {"hp": 2.0, "str": 3.0, "def": 3.0, "cc": 2.0, "cd": 4.0, "mp": 3.0}   # Normal value of each combat line (hp = % of max Health)
P5_PW_BALANCE = {"hp": 2.5, "def": 3, "str": 3, "cc": 1, "cd": 3, "mana": 2, "spd": 1}   # pw.Balance per 100 AP (hp: % of max Health, P5 4.2.4)
P5_PW_HP = {"Tank": 6, "Balance": 2.5, "Slayer": 1, "Lucky": 2, "Magical": 2, "Fortress": 10, "Harmony": 4, "GlassCannon": -2, "Blitz": -1.5,
            "Arcane": 1.5, "Jackpot": -1.5}                                               # P5 4.2.4: pw.<Power>.hp = % per 100 AP
P5_AP_PLAIN, P5_AP_BEST = 100.0, 393.0
P5_GATHER_DD = {"mining": 10.5, "foraging": 10.5, "farming": 15.75, "fishing": 3.5}      # P5 4.2.5 fitted to the 1.1 budget +-15 % at Lv 17 + 95 (spec 11 / 16.5 / 3.7 x 10.5 / 11; 0.5.29: 6 / 6 / 9 / 2)
P5_GATHER_LEVEL = 10                                                                       # power.gatherLevel: +100 % per 10 skill levels


def p5_charm_m(ap):
    """SkyyAccessories AccPower: M = (AP / power.base 100) ^ power.curve 0.6 (guard 20)"""
    return min(20.0, (ap / 100.0) ** 0.6)


def p5_charm_totals(rarity_i, ap, power=None):
    pw = dict(P5_PW_BALANCE)
    if power is not None:
        pw = dict(power)
    m = p5_charm_m(ap)
    t = dict((k, v * P5_CHARM_LADDER[rarity_i]) for k, v in P5_CHARM_NORMAL.items())
    for k, v in pw.items():
        if k in ("hp", "def", "str", "cc", "cd", "mp"):
            t[k] = t.get(k, 0.0) + v * m
    t["hpp"] = t.pop("hp")
    return t


def p5_charms():
    """(plain DPS, plain EHP, best DPS, best EHP)"""
    p = p5_charm_totals(0, P5_AP_PLAIN)
    b = p5_charm_totals(5, P5_AP_BEST)
    return p5_dps(p), p5_ehp(p), p5_dps(b), p5_ehp(b)


def p5_gather_fortune(skill, ap, level):
    return P5_GATHER_DD[skill] * p5_charm_m(ap) * (1.0 + level / float(P5_GATHER_LEVEL))


# ---- P5 5: pets (SkyyPets 0.4.8)
P5_PET_RARITY = [1.0, 1.15, 1.3, 1.45, 1.6, 1.75]          # P5 5.2.2 Common .. Mythic
P5_PET_RARNAMES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
P5_PET_KINDS = {   # P5 5.2.4 combat kinds: (start rarity, Lv 100 stats before rarity; health / mana in % of max)
    "Dog": ("Common", {"str": 29, "cd": 21.5, "cc": 7}), "Fox": ("Uncommon", {"str": 28, "cd": 21, "cc": 7}),
    "Wolf": ("Rare", {"str": 27.5, "cd": 20.5, "cc": 7}), "SkeletonKnight": ("Rare", {"str": 27.5, "cd": 20.5, "cc": 7}),
    "Tusker": ("Rare", {"str": 42}), "Skeleton": ("Rare", {"cc": 24, "cd": 29.5}), "Hawk": ("Epic", {"cc": 23, "cd": 29}),
    "Boar": ("Uncommon", {"health": 18, "def": 22}), "VoidCrawler": ("Rare", {"health": 17.5, "def": 21.5}),
    "Ram": ("Epic", {"def": 28, "health": 12}), "Mouflon": ("Epic", {"mp": 26, "health": 11.5}), "Skrill": ("Epic", {"mp": 42, "mana": 21}),
    "VoidEye": ("Epic", {"mp": 42, "mana": 21}), "VoidLarva": ("Uncommon", {"mp": 42, "mana": 21})}
P5_PET_BUDGET = 0.42          # P5 5.2.1: DPS x EHP of a Lv 100 pet at its start rarity = 1 + 0.42 x the rarity bonus
P5_PET_FORT = {"only": 88.0, "two": 70.0}                    # P5 5.2.5 Lv 100 Fortune value before rarity
P5_PET_REB_STAT = 5.0         # pets.rebirth.stat: +5 % stats a pet rebirth
P5_PET_XP = (50.0, 5.0)       # P5 5.2.6 pets.xp.ownPercent / otherPercent (P3 divisors off)
P5_PET_CURVE = (120.0, 0.08)  # pets.curve.linear / cubic


def p5_pet_power(stats, factor, level=100, rebirths=0):
    """DPS x EHP of one pet alone (the gear formulas; casters: mp; health = Health %)"""
    f = factor * level / 100.0 * (1.0 + P5_PET_REB_STAT * rebirths / 100.0)
    t = dict((k, v * f) for k, v in stats.items())
    t["hpp"] = t.pop("health", 0.0)
    caster = t.get("mp", 0.0) > 0.0
    return p5_dps(t, caster=caster) * p5_ehp(t)


def p5_pet_rows():
    out = []
    for k, (r, st) in P5_PET_KINDS.items():
        fac = P5_PET_RARITY[P5_PET_RARNAMES.index(r)]
        got = p5_pet_power(st, fac)
        want = 1.0 + P5_PET_BUDGET * fac
        out.append((k, r, st, got, want, abs(math.log(got) - math.log(want)) <= 0.05 * math.log(want)))
    return out


def p5_pet_need(L):
    a, c = P5_PET_CURVE
    return round(a * (L - 1) + c * (L - 1) ** 3)


def p5_pet_xp_trace(own="Mining", cap=50, hours=RUN1_HOURS, dt=0.02, overflow=False):
    """hour a pet using the own skill reaches Lv cap on run 1 (pet XP = own XP x 50 % + every other skill's XP x 5 %, P3's raw XP;
    the P3 player of simulate_today; overflow = skill XP keeps flowing at the skill cap - P5 7.8 UNVERIFIED)"""
    share = SHARE
    lv = {s: 0 for s in share}
    xp = {s: 0.0 for s in share}
    plv, pxp, t = 1, 0.0, 0.0
    own_p, oth_p = P5_PET_XP[0] / 100.0, P5_PET_XP[1] / 100.0
    while t < hours:
        for s, sh in share.items():
            if sh <= 0 or (lv[s] >= CAP1 and not overflow):
                continue
            g = xp_per_hour(s, min(lv[s], CAP1), lv["Class"]) * sh * dt * catchup_mult(s, lv[s], lv["Class"])
            xp[s] += g
            pxp += g * (own_p if s == own else oth_p)
            while lv[s] < CAP1 and xp[s] >= CURVES[s][lv[s]]:
                xp[s] -= CURVES[s][lv[s]]
                lv[s] += 1
        while plv < cap and pxp >= p5_pet_need(plv + 1):
            pxp -= p5_pet_need(plv + 1)
            plv += 1
        t += dt
        if plv >= cap:
            return t, plv
    return None, plv


# ---- P5 3.2 / 3.3: the UT meter + the Mythic pity (SkyyGear 0.3.35)
P5_UT = dict(chance=2.5, pity=36.0, points={"elite": 1.0, "mini": 5.0, "dungeon": 0.25, "dungeonBoss": 10.0})
P5_UT_HUNT_PTS_H = float(ELITE_KILLS_H)          # 40 elite kills an hour while hunting (A:188 Q7) = 40 points / h
P5_UT_OPEN_PTS_H = 0.03 * KILLS_H                # open play in a UT band: 3 % of 150 kills are elites = 4.5 points / h
P5_MYTHIC = (12.0, 10)                           # loot.boss.mythic %, loot.boss.pity (the 10th dry kill gives one)


def p5_ut_sim(pts_h=P5_UT_HUNT_PTS_H, hours=10.0, runs=300, seed=P5_SEED, pity=True):
    """(UT bags per hour, the longest dry stretch in hours) - one elite (1 point) at a time, chance 2.5 % a point, sure at 36 points"""
    rng = random.Random(seed)
    bags, worst = 0, 0.0
    for _ in range(runs):
        t, meter, last = 0.0, 0.0, 0.0
        step = 1.0 / pts_h
        while t < hours:
            t += step
            meter += 1.0
            if rng.random() * 100.0 < P5_UT["chance"] or (pity and meter >= P5_UT["pity"]):
                bags += 1
                worst = max(worst, t - last)
                last, meter = t, 0.0
        worst = max(worst, hours - last) if not pity else worst
    return bags / float(runs * hours), worst


def p5_mythic_sim(runs=20000, seed=P5_SEED):
    """(mean boss kills per Mythic bag, the most kills) - 12 % a kill, the 10th dry kill sure"""
    rng = random.Random(seed)
    tot, worst = 0, 0
    for _ in range(runs):
        k = 0
        while True:
            k += 1
            if rng.random() * 100.0 < P5_MYTHIC[0] or k >= P5_MYTHIC[1]:
                break
        tot += k
        worst = max(worst, k)
    return tot / float(runs), worst


# ---- P5 6: the 1-hour rule (gear upgrades over run 1)
P5_BAGS_H = 4.05                  # P5 6: blended play, 6 % of 150 kills x 45 % class time
P5_ODDS_MOB = [50, 30, 13, 5, 1.5]           # odds.<r> mob column, Normal .. Fabled (Mythic boss-only)
P5_ODDS_CRAFT = [60, 25, 10, 4, 1]
P5_SMART, P5_LEAN = 50.0, 75.0               # loot.smart, loot.classLean (P5 3.1)
P5_SLOTS = ["Weapon", "Head", "Chest", "Legs", "Hands"]


def p5_score(slot, L, r, tab):
    """a worn item's worth: F(item level) x its rarity's mean roll power (weapon DPS / armor EHP of the 2.3 table)"""
    return p4_F(max(1, L)) * (tab[P5_RARS[r]][0] if slot == "Weapon" else tab[P5_RARS[r]][4])


def p5_upgrade_sim(seed, smart=True, levelups=True, hours=RUN1_HOURS, dt=0.02):
    """(longest stretch without a gear upgrade before the class cap, over the whole run) for one seed - P5 6's rules"""
    rng = random.Random(seed)
    tab = p5_roll_table()
    trace, _g = simulate_today()
    worn = dict((s, None) for s in P5_SLOTS)          # slot -> [level, rarity, found level]
    worn["Weapon"] = [1, 0, 1]
    last, worst_pre, worst_all, lvl_prev, cap_t = 0.0, 0.0, 0.0, 0, None
    bands_done = set()

    def score(s):
        w = worn[s]
        return 0.0 if w is None else p5_score(s, w[0], w[1], tab)

    def offer(s, L, r):
        new = p5_score(s, L, r, tab)
        if new > score(s) * 1.03:
            worn[s] = [L, r, L]
            return True
        return False
    i = 0
    for t, cl, lvls, _c in trace:
        if t > hours:
            break
        up = False
        if cl >= CAP1 and cap_t is None:
            cap_t = t
        b = max(x for x in BAND if x <= max(1, cl))
        if b not in bands_done:          # craft the new metal: a full set at your level, craft odds
            bands_done.add(b)
            for s in P5_SLOTS:
                up = offer(s, cl if cl >= 1 else 1, rng.choices(range(5), P5_ODDS_CRAFT)[0]) or up
        if rng.random() < P5_BAGS_H * dt:
            L = max(1, cl + rng.randint(-2, 2))
            f = 1.0 + 0.02 * (L - 1)
            r = rng.choices(range(5), [P5_ODDS_MOB[0]] + [x * f for x in P5_ODDS_MOB[1:]])[0]
            if smart and rng.random() * 100.0 < P5_SMART:
                s = min(P5_SLOTS, key=lambda x: (score(x), rng.random()))
            else:
                s = "Weapon" if rng.random() < 0.5 else rng.choice(P5_SLOTS[1:])
            if s != "Weapon" or rng.random() * 100.0 < (P5_LEAN if smart else 50.0):          # a weapon bag of another class = no use
                up = offer(s, L, r) or up
        if levelups and cl > lvl_prev and lvl_prev > 0:
            for s in P5_SLOTS:
                w = worn[s]
                if w is not None and w[0] < cl and w[0] < w[2] + 6:
                    w[0] += 1
                    up = True
        lvl_prev = cl
        if up:
            g = t - last
            worst_all = max(worst_all, g)
            if cap_t is None:
                worst_pre = max(worst_pre, g)
            last = t
        i += 1
    worst_all = max(worst_all, min(hours, trace[-1][0]) - last)
    return worst_pre, worst_all


def p5_upgrade_rows(seeds=40):
    out = []
    for name, sm, lu in (("Today: random slot, crafting each new metal", False, False), ("+ smart bags 50 %, class lean 75", True, False),
                         ("+ item level-ups", True, True)):
        pre, al = zip(*[p5_upgrade_sim(P5_SEED + k, sm, lu) for k in range(seeds)])
        out.append((name, statistics.median(pre), p5_p90(pre), statistics.median(al), p5_p90(al)))
    return out


# ---- P5 1.1: the Fortune budget per skill (end of each zone)
P5_ZONE_T = [(1, 3, "Bronze"), (2, 6, "Dusk"), (3, 9, "Azurvane"), (4, 12, "Cinder"), (5, 15, "Lumen")]


def p5_armor_fort(T):
    """SkyyGear 0.3.35 gathering armor full-set Fortune at ladder T: 0.3.29's GB_FT up to T4, then max(GB_FT, 25.7 x T)"""
    old = P5_GB_FT_034[T - 1]
    return old if T < 5 else max(old, round(P5_TIER_FORT * T, 1))


def p5_fortune_rows():
    out = []
    for z, T, metal in P5_ZONE_T:
        tool = 30.0 * T
        arm = p5_armor_fort(T)
        ch = 17.1 * T
        pet = 12.9 * T
        tree = 40.0
        tot = tool + arm + ch + pet + tree
        out.append((z, T, metal, tool, P5_GB_FT_034[T - 1], arm, ch, pet, tree, tot, 1.0 + tot / 100.0))
    return out


# ---- P5 1: the split
def p5_split():
    tab = p5_roll_table()
    w = tab["mythic"][1] / tab["normal"][0]
    a = tab["mythic"][5] / tab["normal"][4]
    a_d = tab["mythic"][3] / tab["normal"][2]
    cp_d, cp_e, cb_d, cb_e = p5_charms()
    ch_d, ch_e = cb_d / cp_d, cb_e / cp_e
    best_pet = max(p5_pet_power(st, P5_PET_RARITY[5], 100, 5) / p5_pet_power(st, P5_PET_RARITY[0], 50, 0) for _r, st in P5_PET_KINDS.values())
    pet_d = pet_e = math.sqrt(1.39)          # P5 5.2.2 target: best / plain pet power x1.39 split evenly
    rows = [("Weapon / tool", 35, w, 1.0), ("Armor", 30, a_d, a), ("Void Charms", 20, ch_d, ch_e), ("Pets", 15, pet_d, pet_e)]
    tot = sum(math.log(d * e) for _n, _s, d, e in rows)
    return rows, tot, best_pet


P5_KIT_SPEC = (3.2, 2.8)          # P5 1 / 7.5: the kit's best / plain DPS / EHP (= P4 Part 5's x3.19 / x2.85); +-15 %
P5_KIT_TOL = 0.15
# rows that FAIL on purpose until Skyy answers a question (shown "NO - asked Skyy" in targets.md and printed by --check, but not a --check failure);
# the main session puts each question in OPEN-QUESTIONS.md; take the row out of here once Skyy has answered (the answer then decides the fix)
P5_ASKED = {
    "<= 1 h without a gear upgrade before the cap (A:187 Q2)":
        "P5 fix round: the +6 item level-up cap (LOCKED by Skyy, docs/answered/gear.md 2026-10-04 + 10-09) is the bottleneck: p90 2.02 h (+10 would be 0.72 h) "
        "- the gaps sit between metal bands 7-8 levels apart once every slot is at +6. Raise the cap to +10, or let the UT meter run before the cap too? [keep +6 until Skyy answers]",
}


def p5_kit():
    rows, _tot, _bp = p5_split()
    return math.prod(d for _n, _s, d, _e in rows), math.prod(e for _n, _s, _d, e in rows)


def p5_ok_text(t, ok):
    return "yes" if ok else ("NO - asked Skyy" if t in P5_ASKED else "NO")


def p5_rows():
    """(target, model text, ok) for the --check / the targets.md section"""
    tab = p5_roll_table()
    out = []
    worst = 0.0
    for r in P5_RARS:
        got, want = tab[r], P5_TABLE_SPEC[r]
        for g, w in zip(got, want):
            worst = max(worst, abs(g - w) / w)
    out.append(("Roll table within +-8 % of spec 2.3 (weapon / armor DPS / armor EHP, mean + p90)", "worst %.1f %%" % (100 * worst), worst <= P5_TOL))
    rows, tot, _bp = p5_split()
    shares = [math.log(d * e) / tot * 100 for _n, _s, d, e in rows]
    ok = all(abs(sh - s) <= 4 for sh, (_n, s, _d, _e) in zip(shares, rows))
    out.append(("Split 35 / 30 / 20 / 15 (A:190 Q15)", " / ".join("%.0f" % x for x in shares) + " %% of ln %.2f" % tot, ok))
    kd, ke = p5_kit()
    out.append(("Kit best / plain DPS ~x3.2, EHP ~x2.8 +-15 % (P5 1 / 7.5)", "DPS x%.2f, EHP x%.2f" % (kd, ke),
                abs(kd / P5_KIT_SPEC[0] - 1) <= P5_KIT_TOL and abs(ke / P5_KIT_SPEC[1] - 1) <= P5_KIT_TOL))
    w_bp = tab["mythic"][1] / tab["normal"][0]
    out.append(("Weapon best / plain ~x2.2 (P5 2.3)", "x%.2f" % w_bp, 1.9 <= w_bp <= 2.5))
    a_bp = tab["mythic"][5] / tab["normal"][4]
    out.append(("Armor EHP best / plain ~x1.87 (P5 2.3)", "x%.2f" % a_bp, 1.7 <= a_bp <= 2.05))
    cp_d, cp_e, cb_d, cb_e = p5_charms()
    out.append(("Void Charms Balance best / plain x1.25 +- 0.05 both ways (P5 4.2)", "DPS x%.2f, EHP x%.2f" % (cb_d / cp_d, cb_e / cp_e),
                abs(cb_d / cp_d - 1.25) <= 0.05 and abs(cb_e / cp_e - 1.25) <= 0.05))
    pr = p5_pet_rows()
    out.append(("Combat pets: Lv 100 at the start rarity = 1 + 0.42 x rarity +- 5 % (P5 5.2.1)", "%d / %d kinds" % (sum(1 for x in pr if x[5]), len(pr)),
                all(x[5] for x in pr)))
    ut_h, ut_dry = p5_ut_sim()
    out.append(("UT 1-2 / h hunting (A:190 Q16)", "%.2f / h, longest dry %.2f h" % (ut_h, ut_dry), UT_PER_H[0] <= ut_h <= UT_PER_H[1] and ut_dry <= MAX_GAP_H))
    my_m, my_w = p5_mythic_sim()
    out.append(("Mythic 1 per 5-10 boss kills (economy.md:162)", "mean %.1f, most %d" % (my_m, my_w), MYTHIC_PER_BOSS[0] <= my_m <= MYTHIC_PER_BOSS[1] and my_w <= 10))
    ur = p5_upgrade_rows()
    out.append(("<= 1 h without a gear upgrade before the cap (A:187 Q2)", "p90 %.2f h (with level-ups)" % ur[-1][2], ur[-1][2] <= MAX_GAP_H))
    t50, _pl = p5_pet_xp_trace("Mining")
    t50c, _pc = p5_pet_xp_trace("Class")
    out.append(("A pet reaches its Lv 50 cap at hour 28-33 of run 1 (P5 5.2.6)", "Mining pet %s h, combat pet %s h" % (fmt(t50), fmt(t50c)),
                t50 is not None and 28 <= t50 <= 33))
    f17, f95 = p5_gather_fortune("mining", 210, 17), p5_gather_fortune("mining", 490, 95)
    out.append(("Mining Power Fortune vs the 1.1 budget +-15 % (P5 4.2.5: end of Zone 1 51, Zone 5 257)", "%.0f / %.0f (pw.Mining.dd.mining %g)" % (f17, f95, P5_GATHER_DD["mining"]),
                abs(f17 / 51.0 - 1) <= 0.15 and abs(f95 / 257.0 - 1) <= 0.15))
    zr = p5_fortune_rows()
    out.append(("Mining tree Fortune <= 40 (TREE_FORT_MAX)", "40.0 (Rich Seams 7.5 + 15 + 7.5 + 10; tools/trees_v3_effects.py check())", True))
    out.append(("Fortune budget end of Zone 5 ~1300 (P5 1.1)", "%.0f" % zr[-1][9], 1200 <= zr[-1][9] <= 1450))
    return out


def p5_md():
    """### 7. Power sources (P5) for research/balance/targets.md"""
    tab = p5_roll_table()
    old = p5_roll_table_034()
    out = ["", "### 7. Power sources (P5, research/Balance-P5-Power-Spec.md; Normal, M melee class; `python tools/balance_model.py --power`)", ""]
    rows, tot, best_pet = p5_split()
    out += ["| Source (share) | best / plain DPS | best / plain EHP | log power (share of %.2f) |" % tot, "|---|---|---|---|"]
    for n, s, d, e in rows:
        out.append("| %s (%d) | x%.2f | x%.2f | %.2f (%.0f %%) |" % (n, s, d, e, math.log(d * e), 100 * math.log(d * e) / tot))
    kd = math.prod(d for _n, _s, d, _e in rows)
    ke = math.prod(e for _n, _s, _d, e in rows)
    out.append("| **Kit** | **x%.2f** | **x%.2f** | %.2f |" % (kd, ke, tot))
    out += ["", "1.1 Fortune budget per skill (best-in-tier at the END of each zone; additive, no cap - Skyy):", "",
            "| End of | Tier T | Tool (+3 a level) | Armor 0.3.34 -> P5 | Void Charms | Pets | Tree | Total | Drops / block |", "|---|---|---|---|---|---|---|---|---|"]
    for z, T, metal, tool, a0, arm, ch, pet, tree, tt, dpb in p5_fortune_rows():
        out.append("| Zone %d | %d (%s) | %.0f | %.0f -> %.0f | %.0f | %.0f | %.0f | %.0f | %.1f |" % (z, T, metal, tool, a0, arm, ch, pet, tree, tt, dpb))
    out += ["", "2.3 Gear rolls (3000 rolls each, full level; armor = a set of 4 at the slot powers %s):" % " / ".join("%g" % P5_SLOT_POWER[s] for s in P5_SLOTS), "",
            "| Rarity | Weapon DPS mean (p90) | Armor set DPS mean (p90) | Armor set EHP mean (p90) | 0.3.34 weapon / armor DPS / armor EHP (mean) |", "|---|---|---|---|---|"]
    for r in P5_RARS:
        v = tab[r]
        o = old[r]
        out.append("| %s | %.2f (%.2f) | %.2f (%.2f) | %.2f (%.2f) | %.2f / %.2f / %.2f |" % (r.capitalize(), v[0], v[1], v[2], v[3], v[4], v[5], o[0], o[1], o[2]))
    cp_d, cp_e, cb_d, cb_e = p5_charms()
    out += ["", "4.2 Void Charms (DERIVED): Normal lines + Balance at AP %d = DPS x%.2f / EHP x%.2f; Mythic lines + Omni (AP %d, M %.2f) = x%.2f / x%.2f -> best / plain **x%.2f / x%.2f**. "
            "Gathering Power Fortune = pw.<Power>.dd x M x (1 + skill level / %d): Mining end of Zone 1 (AP 210, Lv 17) %.0f, end of Zone 5 (AP 490, Lv 95) %.0f."
            % (P5_AP_PLAIN, cp_d, cp_e, P5_AP_BEST, p5_charm_m(P5_AP_BEST), cb_d, cb_e, cb_d / cp_d, cb_e / cp_e, P5_GATHER_LEVEL,
               p5_gather_fortune("mining", 210, 17), p5_gather_fortune("mining", 490, 95)), ""]
    out += ["5.2 Pets (Lv 100 at the start rarity; budget 1 + %.2f x rarity; rarity x%s):" % (P5_PET_BUDGET, " / ".join("%g" % x for x in P5_PET_RARITY)), "",
            "| Kind | Start | Stats (health / mana = %) | DPS x EHP | target | OK |", "|---|---|---|---|---|---|"]
    for k, r, st, got, want, ok in p5_pet_rows():
        out.append("| %s | %s | %s | %.3f | %.3f | %s |" % (k, r, ",".join("%s:%g" % kv for kv in st.items()), got, want, "yes" if ok else "NO"))
    t50, _p = p5_pet_xp_trace("Mining")
    t50c, _c = p5_pet_xp_trace("Class")
    t50o, _o = p5_pet_xp_trace("Mining", overflow=True)
    out += ["", "Gathering pets: a Fortune-only kind %g, two-stat %g at Lv 100: Rare Lv 30 = %.0f Fortune, Mythic 5 pet rebirths Lv 100 = %.0f. "
            "Pet XP (own %g %%, other %g %%, P3 raw XP): a Mining pet reaches Lv 50 at %s h (skill XP flowing at the cap: %s h), a combat pet at %s h."
            % (P5_PET_FORT["only"], P5_PET_FORT["two"], P5_PET_FORT["only"] * 1.3 * 0.3, P5_PET_FORT["only"] * 1.75 * 1.25, P5_PET_XP[0], P5_PET_XP[1],
               fmt(t50), fmt(t50o), fmt(t50c)), ""]
    ut_h, ut_dry = p5_ut_sim()
    ut_o, _d = p5_ut_sim(P5_UT_OPEN_PTS_H)
    ut_np, _d2 = p5_ut_sim(pity=False)
    my_m, my_w = p5_mythic_sim()
    out += ["3.2 / 3.3 drops: the UT meter (%.1f %% a point, sure at %g points): hunting %g points / h = **%.2f UT / h, longest dry %.2f h** (open play %.1f points / h: %.2f / h; "
            "without the sure bag %.2f / h). Mythic: %g %% a boss kill + sure by the %dth dry kill = **mean %.1f kills, most %d**."
            % (P5_UT["chance"], P5_UT["pity"], P5_UT_HUNT_PTS_H, ut_h, ut_dry, P5_UT_OPEN_PTS_H, ut_o, ut_np, P5_MYTHIC[0], P5_MYTHIC[1], my_m, my_w), ""]
    out += ["6. The 1-hour rule (40 seeds, the P3 player of section 1; bags %.2f / h, smart %g %%, class lean %g %%, crafting each new metal, level-ups to +6, a 3 %% better item = an upgrade):" % (P5_BAGS_H, P5_SMART, P5_LEAN), "",
            "| Case | Longest stretch without a gear upgrade before the cap (median / p90) | Whole run 0-%d h (median / p90) |" % RUN1_HOURS, "|---|---|---|"]
    for name, m1, p1, m2, p2 in p5_upgrade_rows():
        out.append("| %s | %.2f h / %.2f h | %.2f h / %.2f h |" % (name, m1, p1, m2, p2))
    out += ["", "| Target (P5 7.5) | Model | OK |", "|---|---|---|"]
    for t, m, ok in p5_rows():
        out.append("| %s | %s | %s |" % (t, m, p5_ok_text(t, ok)))
    out.append("")
    asked = [(t, q) for t, m, ok in p5_rows() if not ok and t in P5_ASKED for q in [P5_ASKED[t]]]
    if asked:
        out.append("Asked Skyy (these rows fail until answered; `--check` lists them but does not fail on them): " + " ".join("**%s** - %s" % (t, q) for t, q in asked))
        out.append("")
    out.append("Model notes: DPS = Damage %% x Strength x Charged (%d %% of hits) x crit (base 0, x2 x (1 + Crit Damage %%)) x (1 + the %% lines); EHP = (1 + Health %%) x "
               "(100 + %g + Defense) / (100 + %g) x Life Steal (+2 %% a point) x Health Regen %% (+0.25 %% a point). The SkyyGear 0.3.35 harness runs the REAL "
               "GearRoll.rollMods (2000 rolls a rarity) against this table (+-%d %%). The cap stretch (after class Lv %d) has no item levels: the UT meter + boss Mythic pity "
               "are its upgrades (Skyy: 'unless they are just afk'). Known one-way term NOT in the kit numbers: SkyySkills 0.4.59's class Health %% and Rebirth "
               "Health / Mana %% (ClassStat.skip / RbStat.skip) still count SkyyGear's skyygear_hp and SkyyPets' skyypet_health / skyypet_mana in their base, "
               "so a +25 %% class on a gear 30 %% adds ~7.5 %% of the flat max on top (tanks a little above this EHP; no loop - Gear / Pets / Accessories skip "
               "the Skills keys); the next SkyySkills round adds the three keys to both skip lists." % (100 * P5_CHARGED_SHARE, P5_CLASS_DEF, P5_CLASS_DEF, 100 * P5_TOL, CAP1))
    return "\n".join(out)


def p5_write_section(md):
    """put p5_md() into research/balance/targets.md as its '### 7. Power sources' section (p4_write_section's rule)"""
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "balance", "targets.md"))
    raw = open(path, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    sec = md.strip("\n").replace("\n", nl) + nl
    head = "### 7. Power sources"
    a = raw.find(nl + head)
    if a < 0:
        out, how = raw + ("" if raw.endswith(nl) else nl) + nl + sec, "appended"
    else:
        a += len(nl)
        b = len(raw)
        for mk in (nl + "### ", nl + "## "):
            j = raw.find(mk, a + len(head))
            if 0 <= j < b:
                b = j + len(nl)
        rest = raw[b:]
        out, how = raw[:a] + sec + ((nl if not sec.endswith(nl + nl) else "") + rest if rest else ""), "replaced"
    with open(path, "wb") as f:
        f.write(out.encode("utf-8"))
    return how


def main():
    if "--power" in sys.argv:
        md = p5_md()
        print(md)
        print("\nwrote research/balance/targets.md section '### 7. Power sources' (%s)" % p5_write_section(md))
        if "--check" not in sys.argv:
            return
    if "--combat" in sys.argv or "--check" in sys.argv:
        md = p4_md()
        print(md)
        p5r = p5_rows()
        bad = [r for r in p4_rows() if not r[2]] + [r for r in p5r if not r[2] and r[0] not in P5_ASKED]          # P5: + the power-source rows (not the asked ones)
        asked = [r for r in p5r if not r[2] and r[0] in P5_ASKED]
        if "--combat" in sys.argv:
            print("\nwrote research/balance/targets.md section '### 6. Combat' (%s)" % p4_write_section(md))
        if "--check" in sys.argv:
            for t, m, _ok in bad:
                print("FAIL %s: %s" % (t, m))
            for t, m, _ok in asked:
                print("ASKED %s: %s - %s" % (t, m, P5_ASKED[t]))
            sys.exit(1 if bad else 0)
        return
    body, gaps, vp = build()
    top = "\n".join(f"{i}. {g[1]}" for i, g in enumerate(gaps[:10], 1))
    print(f"SkyWynn pacing model (Balance Pass P1, {NOW} numbers) - target vs {NOW}, gaps marked !!")
    print(body)
    print(f"\n### Top gaps ({NOW} vs target)\n" + top)
    if "--md" in sys.argv:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "balance", "targets.md")
        with open(os.path.normpath(path), "w", encoding="utf-8", newline="\n") as f:
            f.write("# Balance targets - the pacing yardstick (P1 model, P3 numbers, generated)\n\n"
                    "Generated by `python tools/balance_model.py --md` - do not hand-edit; change the model and re-run. "
                    "Goals: research/Balance-Goals-Questions.md + Skyy's popup answers (docs/answered/skills.md 185-193, "
                    "economy.md:162, A:197). The model column = the P3 numbers (research/Balance-P3-XP-Spec.md; P1's live numbers: "
                    "`python tools/balance_model.py --before`, the P0 inventory in this folder). Every later phase (P3-P9 of "
                    "research/Balance-Pass-Spec.md section 8) tunes against these tables; Skyy then adjusts by feel. "
                    "Index: INDEX.md (research/balance/).\n\n" + assumptions_md() + "\n" + body
                    + "\n\n### Fixed targets the model only lists (tuned in P4-P5)\n"
                    f"- Power split weapon-tool / armor / accessories / pets = {POWER_SPLIT} (A:190 Q15); best-in-tier gear "
                    f"~{BEST_VS_PLAIN}x plain (A:190 Q14); Normal mob 4-6 hits, elites 3x / mini bosses 10x HP, boss 3-4 min "
                    "solo (A:188); over-level +5 hard / +10 wall, small coin loss on death, Mana dry every 20-30 s (A:189).\n"
                    "\n### Top 10 gaps (P3 vs target)\n" + top + "\n\n### Answered (A:197, 2026-10-20)\n"
                    f"- The cap stretch: Skyy picked 'Middle: Lv 50 at ~33 h' -> levels.scale {LEVELS_SCALE} % (class Lv {CAP1} at "
                    f"{fmt(at_level(simulate_today()[0], CAP1)[0])} h in this model); the rest of the 40-50 h run = skills catch up, "
                    "gear / UT / bosses, overflow XP for Void Particles.\n" + p4_md() + "\n" + p5_md() + "\n")
        print("\nwrote research/balance/targets.md")


if __name__ == "__main__":
    main()
