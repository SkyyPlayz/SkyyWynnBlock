"""SkyWynn Balance P8 - the rebirth pacing model (research/Balance-P8-Rebirth-Spec.md Appendix A + section 5.7).

The P8 spec says to port these functions into tools/balance_model.py; they live HERE instead because balance_model.py had uncommitted P5
edits from another builder when P8a was built (2026-10-21). This file only IMPORTS balance_model (P3 curve CURVES, xp_per_hour,
catchup_mult, cum, SHARE) - a later round may fold it into balance_model.py's "# ===== P8 REBIRTH" section unchanged.

Run:  python tools/balance_rebirth.py --rebirth          the 2.4 table (P8 numbers) + the 1.4 table (today's live numbers)
      python tools/balance_rebirth.py --check            the P8a model check (exit 1 on a miss): greedy ratio 0.97-1.03 for rebirths 1-10,
                                                         all-keep <= 1.15, buy-cheapest <= 1.25
      python tools/balance_rebirth.py --tune 10          re-derive the past-life list (bisection, greedy player)
      --live (today's +200 % class clamp + the P3 list), --past <a,b,...>, --kept <x>, --ceil <x> (rebirth.xpMultMax), --md (markdown rows)
SkyySkills 0.4.59 ships PAST_LIFE_P8 as rebirth.pastLifeXp (tools/skills_0_4_59_patch.py asserts the two are equal).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import balance_model as BM   # noqa: E402

CURVES, SHARE, xp_per_hour, catchup_mult, cum = BM.CURVES, BM.SHARE, BM.xp_per_hour, BM.catchup_mult, BM.cum

# ===== P8 REBIRTH (constants: SkyyRebirth 0.4.1 REB:603-620 + SkyySkills 0.4.58 S58:8546 / 12236)
VP_BASE, VP_PER, VP_SKILL, VP_OVER = 20, 10, 2, 12                     # vp.base / perRebirth / perSkill / overflow
KEEP = 0.25                                                             # nexus.keep, % all XP per held VP
INSIGHT = ([12, 20, 32, 48, 72], [6, 8, 10, 12, 16])
CLASS_ECHO = ([4, 6, 10, 16, 24], [4, 5, 7, 9, 11])
SKILL_ECHO = ([4, 6, 10, 16, 24], [8, 11, 15, 20, 26])
PAST_LIFE_LIVE = list(BM.PAST_LIFE)                                     # SkyySkills 0.4.57 / 0.4.58: 1.2,1.45,1.8,2.25,2.8
PAST_LIFE_P8 = [1.1, 1.35, 1.6, 2.0, 2.45, 2.15, 2.25, 2.4, 2.55, 2.7]  # spec 2.3 = SkyySkills 0.4.59 rebirth.pastLifeXp
CLASS_RB_MAX_LIVE, CLASS_RB_MAX = 2.0, 5.0                              # RbStat MAXPCT 200 (0.4.58) -> CLASSXP_MAX 500 (0.4.59)
XP_BONUS_MAX = 5.0                                                      # SkillBonus.xpBonus clamp 0..5
KEPT_PER_REBIRTH, KEPT_MAX = BM.KEPT_PER_REBIRTH, 0.30                  # GUESS (gear tiers / shards / pets kept)
CAP1, STEP, CAPMAX, RUN1, SHRINK = 50, 10, 100, 45.0, 0.85
SKILLS = ["Class", "Mining", "Foraging", "Farming", "Cooking", "Alchemy", "Fishing"]
CEIL = None                                                             # rebirth.xpMultMax (None = off)
CEIL_HELP = 9.3                                                         # spec 2.5: 2.70 x 3.45 = runs stop shrinking at rebirth 10
CLAMP = CLASS_RB_MAX                                                    # the class rebirth clamp the run uses (--live: 2.0)


def arms():
    """name, costs, % per rank, which XP streams it boosts"""
    return [("Insight", INSIGHT[0], INSIGHT[1], dict((s, 1.0) for s in SKILLS)), ("ClassEcho", CLASS_ECHO[0], CLASS_ECHO[1], {"Class": 1.0}),
            ("MiningEcho", SKILL_ECHO[0], SKILL_ECHO[1], {"Mining": 1.0}), ("ForagingEcho", SKILL_ECHO[0], SKILL_ECHO[1], {"Foraging": 1.0}),
            ("HandFarming", SKILL_ECHO[0], SKILL_ECHO[1], {"Farming": 1.0})]


def arm_value(pct, aff):
    """% of all XP, time-weighted by SHARE"""
    return pct * sum(SHARE.get(s, 0) * f for s, f in aff.items())


def rebirth_run(cap, hours, mult, past_cap, past_mult, dt=0.02):
    """mult[s] = (1 + rebirth bonus, kept power); past-life on levels < past_cap; returns (h to class cap, levels at end, class XP earned)"""
    lv = dict((s, 0) for s in SHARE)
    xp = dict((s, 0.0) for s in SHARE)
    earned, t, t_cap = 0.0, 0.0, None
    while t < hours:
        for s, sh in SHARE.items():
            if sh <= 0:
                continue
            code, kept = mult.get(s, (1.0, 1.0))
            cm = code * (past_mult if lv[s] < past_cap else 1.0)
            if CEIL is not None:
                cm = min(cm, max(CEIL, past_mult if lv[s] < past_cap else 1.0))   # the ceiling never cuts the past-life part (SkyySkills)
            gain = xp_per_hour(s, max(lv[s], 1), lv["Class"]) * sh * dt * cm * kept * catchup_mult(s, lv[s], lv["Class"])
            if s == "Class":
                earned += gain
            if lv[s] >= cap:
                continue
            xp[s] += gain
            while lv[s] < cap and xp[s] >= CURVES[s][lv[s]]:
                xp[s] -= CURVES[s][lv[s]]
                lv[s] += 1
        t += dt
        if t_cap is None and lv["Class"] >= cap:
            t_cap = t
    return t_cap, lv, earned


def vp_earned(n, lv, cap, earned_class):
    """REB:44-48 - VP of rebirth n from the finished run"""
    capped = min(11, sum((3 if s == "Farming" else 1) for s in ("Mining", "Foraging", "Farming", "Cooking", "Alchemy", "Fishing")
                         if lv.get(s, 0) >= cap))
    r = earned_class / cum(CURVES["Class"], cap)
    over = math.floor(VP_OVER * (math.sqrt(min(r, 16)) - 1)) if r >= 1 else 0
    return VP_BASE + VP_PER * n + VP_SKILL * capped + over, capped, r


def rb_mults(ranks, held, n):
    kept = 1 + min(KEPT_MAX, KEPT_PER_REBIRTH * n)
    allb = sum(INSIGHT[1][:ranks["Insight"]]) / 100 + held * KEEP / 100
    out = {}
    for s in SKILLS:
        b = allb + sum(sum(p[:ranks[nm]]) / 100 for nm, c, p, aff in arms() if nm != "Insight" and s in aff)
        b = min(b, CLAMP if s == "Class" else XP_BONUS_MAX)
        out[s] = (1 + b, kept)
    return out


def rb_buy(ranks, bank, policy):
    """greedy = buy while a rank beats keeping; keep = never; cheap = cheapest first"""
    while True:
        best = None
        for nm, cost, pct, aff in arms():
            r = ranks[nm]
            if r >= 5 or cost[r] > bank or policy == "keep":
                continue
            val = arm_value(pct[r], aff) / cost[r]
            if policy == "greedy" and val <= KEEP:
                continue
            key = val if policy == "greedy" else -cost[r]
            if best is None or key > best[0]:
                best = (key, nm, cost[r])
        if not best:
            return bank
        ranks[best[1]] += 1
        bank -= best[2]


def rb_campaign(policy, past, nmax, dt=0.02):
    ranks = dict((a[0], 0) for a in arms())
    bank = total = 0
    t0, lv, ec = rebirth_run(CAP1, RUN1, {}, 0, 1.0, dt)
    vp = vp_earned(1, lv, CAP1, ec)[0]
    rows = [dict(n=0, cap=CAP1, past=1.0, t_cap=t0, target=t0, total=0, held=0, spent=0, ranks=dict(ranks), mult=1.0)]
    for n in range(1, nmax + 1):
        bank += vp
        total += vp
        bank = rb_buy(ranks, bank, policy)
        cap, prev = min(CAPMAX, CAP1 + STEP * n), min(CAPMAX, CAP1 + STEP * (n - 1))
        pm = past[min(n, len(past)) - 1]
        m = rb_mults(ranks, bank, n)
        target, run_target = t0 * SHRINK ** n, RUN1 * SHRINK ** n
        t, _lv, _ec = rebirth_run(cap, max(target * 1.8, 14.0), m, prev, pm, dt)
        _t, lv2, ec2 = rebirth_run(cap, run_target if t is None else max(run_target, t), m, prev, pm, dt)   # VP for the next rebirth
        vp = vp_earned(n + 1, lv2, cap, ec2)[0]
        rows.append(dict(n=n, cap=cap, past=pm, t_cap=t, target=target, total=total, held=bank, spent=total - bank, ranks=dict(ranks),
                         mult=m["Class"][0] * m["Class"][1]))
    return rows


def rb_tune_past(nmax=10):
    """bisection per entry: the greedy player's h to class cap = target"""
    past = [PAST_LIFE_P8[0]]
    for n in range(1, nmax + 1):
        lo, hi = 1.0, 12.0
        for _ in range(22):
            mid = (lo + hi) / 2
            r = rb_campaign("greedy", past[:n - 1] + [mid] * 4, n, dt=0.05)[-1]
            lo, hi = (mid, hi) if (r["t_cap"] is None or r["t_cap"] > r["target"]) else (lo, mid)
        past = past[:n - 1] + [round(hi, 2)]
    return past


def ratio(row):
    return None if row["t_cap"] is None else row["t_cap"] / row["target"]


def rb_table(past, nmax=10, dt=0.02, md=False):
    """the 2.4 rows: greedy / all-keep / buy-cheapest players on the same past-life list; returns the rows (dicts)"""
    g, k, c = rb_campaign("greedy", past, nmax, dt), rb_campaign("keep", past, nmax, dt), rb_campaign("cheap", past, nmax, dt)
    out = []
    head = ("| Rebirth | Cap | Past-life | Class x (VP bonus x kept) | VP total / spent / held | Keep | Class cap h | Target h | Ratio greedy | "
            "all-keep | buy-cheapest |")
    print(head if md else "rebirth cap past  class-x  VP total/spent/held   keep    h-cap  target  greedy  keep  cheap")
    if md:
        print("|" + "---|" * 11)
    for i in range(1, nmax + 1):
        rg, rk, rc = g[i], k[i], c[i]
        e = dict(n=i, cap=rg["cap"], past=rg["past"], mult=rg["mult"], total=rg["total"], spent=rg["spent"], held=rg["held"],
                 keep=rg["held"] * KEEP, t_cap=rg["t_cap"], target=rg["target"], greedy=ratio(rg), allkeep=ratio(rk), cheap=ratio(rc))
        out.append(e)
        f = lambda x: "-" if x is None else "%.2f" % x
        if md:
            print("| %d | %d | x%.2f | x%.2f | %d / %d / %d | +%.1f %% | %s | %.1f | **%s** | %s | %s |" % (
                i, e["cap"], e["past"], e["mult"], e["total"], e["spent"], e["held"], e["keep"], f(e["t_cap"]), e["target"],
                f(e["greedy"]), f(e["allkeep"]), f(e["cheap"])))
        else:
            print("%7d %3d x%.2f  x%.2f   %5d / %4d / %5d  +%6.1f%%  %5s  %5.1f   %5s  %5s %5s" % (
                i, e["cap"], e["past"], e["mult"], e["total"], e["spent"], e["held"], e["keep"], f(e["t_cap"]), e["target"],
                f(e["greedy"]), f(e["allkeep"]), f(e["cheap"])))
    return out


def rb_check(rows, lo=0.97, hi=1.03):
    """the P8a model check; returns the list of misses (empty = OK)"""
    bad = []
    for e in rows:
        if e["greedy"] is None or not (lo <= e["greedy"] <= hi):
            bad.append("rebirth %d greedy ratio %s outside %.2f-%.2f" % (e["n"], e["greedy"], lo, hi))
        if e["allkeep"] is None or e["allkeep"] > 1.15:
            bad.append("rebirth %d all-keep ratio %s > 1.15" % (e["n"], e["allkeep"]))
        if e["cheap"] is None or e["cheap"] > 1.25:
            bad.append("rebirth %d buy-cheapest ratio %s > 1.25" % (e["n"], e["cheap"]))
    return bad


def ceil_cut(rb, past, ceil):
    """SkyySkills 0.4.59 SkillBonus.cutRb twin: the rebirth part rb (a fraction) so that past x (1 + rb) <= ceil; ceil <= 0 / NaN = off"""
    if ceil is None or not (ceil > 0) or not (rb > 0):
        return max(0.0, rb) if rb == rb else 0.0
    p = past if past > 1.0 else 1.0
    m = ceil / p - 1.0
    if m < 0.0:
        m = 0.0
    return rb if rb < m else m


def _arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    global CEIL, CLAMP, KEPT_PER_REBIRTH
    live = "--live" in sys.argv
    if live:
        CLAMP = CLASS_RB_MAX_LIVE
    past = PAST_LIFE_LIVE if live else PAST_LIFE_P8
    if _arg("--past"):
        past = [float(x) for x in _arg("--past").split(",")]
    if _arg("--kept"):
        KEPT_PER_REBIRTH = float(_arg("--kept"))
    if _arg("--ceil"):
        CEIL = float(_arg("--ceil"))
    md = "--md" in sys.argv
    if _arg("--tune"):
        print("tuned past-life list:", rb_tune_past(int(_arg("--tune"))))
        return 0
    if "--rebirth" in sys.argv:
        print("### 2.4 P8 (past-life %s, class clamp +%d %%)" % (",".join("%g" % x for x in past), CLAMP * 100))
        rb_table(past, 10, md=md)
        if not live:
            CLAMP = CLASS_RB_MAX_LIVE
            print("### 1.4 today (past-life %s, class clamp +200 %%)" % ",".join("%g" % x for x in PAST_LIFE_LIVE))
            rb_table(PAST_LIFE_LIVE, 10, md=md)
            CLAMP = CLASS_RB_MAX
    if "--check" in sys.argv:
        assert ceil_cut(3.0, 2.7, 9.3) == 9.3 / 2.7 - 1.0 and ceil_cut(3.0, 2.7, 0) == 3.0 and ceil_cut(3.0, 2.7, float("nan")) == 3.0
        rows = rb_table(past, 10, md=md)
        bad = rb_check(rows)
        print("P8a model check: " + ("OK - rebirths 1-10 within 0.97-1.03 of '15 %% shorter each' (greedy %.2f-%.2f)" % (
            min(e["greedy"] for e in rows), max(e["greedy"] for e in rows)) if not bad else "FAIL\n  " + "\n  ".join(bad)))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
