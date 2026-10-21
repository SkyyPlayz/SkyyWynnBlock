"""SkyWynn pacing model - Balance Pass P1 (research/Balance-Pass-Spec.md section 8). The yardstick P3-P9 tune against.

    python tools/balance_model.py            print the target tables next to the P3 numbers (research/Balance-P3-XP-Spec.md), gaps (!!)
    python tools/balance_model.py --before   the same tables with the P1 numbers (before P3: the live 0.4.56 tables)
    python tools/balance_model.py --md       also rewrite research/balance/targets.md (always the P3 numbers)

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
    ut_h = ELITE_KILLS_H * UT_CHANCE
    checks = [  # what, target low, target high, today, unit, source
        ("Collection tier II (ore, curve S)", COLL_II_MIN, COLL_II_MIN, coll_ii_min, "min", "A:191 / H:11"),
        ("Collection tier V (ore)", *COLL_V_H, coll_v_h, "h", "A:191 / H:11"),
        ("One armor set (4 x 1 Enchanted ore)", *ARMOR_SET_H, set_h, "h", "A:191 / G:485 garmor.ladders"),
        ("UT drops per hour of elite hunting", *UT_PER_H, ut_h, "/h", "A:190 / G:356"),
        ("Boss kills per Mythic", *MYTHIC_PER_BOSS, 1 / MYTHIC_CHANCE, "kills", "economy.md:162 / G:1589"),
        (f"Longest stretch without any level-up (run 1, cap {CAP1})", 0, MAX_GAP_H, worst_gap, "h", "A:187 Q2")]
    rows = []
    for what, lo, hi, today, unit, src in checks:
        flag = gap_flag(today, max(lo, 1e-9) * 0.8 if lo else 0.0, hi * 1.25) if lo else             ("ok" if today <= hi else f"!! {rx(today / hi)}")
        rows.append([what, f"{fmt(lo)}-{fmt(hi)} {unit}" if lo != hi else f"{fmt(lo)} {unit}", f"{fmt(today)} {unit}", flag, src])
        if flag.startswith("!!"):
            note(what, today / (hi if today > hi else max(lo, 1e-9)), f"{what}: target {rows[-1][1]}, {NOW} {rows[-1][2]}")
    rows.append(["Gear loot bags per hour (normal play)", ">= 1 gear upgrade / h", f"{loot_h:.1f} bags (share that "
                 "upgrades: ?)", "?", "A:187 Q2 / G:240-241"])
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


def main():
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
                    "gear / UT / bosses, overflow XP for Void Particles.\n")
        print("\nwrote research/balance/targets.md")


if __name__ == "__main__":
    main()
