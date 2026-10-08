# Echo options - how Echo stays inside the damage budgets (cloud, 2026-10-08)

Follows `docs/answered/classes.md` L111 (Meteor), L118 (God Killer), L123 (Palm Strike), L124 (Still Water), L132 (Banner), L139 (Whirlwind),
L141 (Sacred Heal), L145 (Martyr's Grace + Shield Bubble), L146-L147. Numbers from `research/cloud/Ability-Refresh-1007.md` section 3,
`research/cloud/Modifier-Pool-Spec.md` (Echo row, section 3.1) and `research/cloud/Class-Ability-Spec-Draft.md` section 5. All maths python3.

## Skyy's words (the part that is locked)
- L111: "i was just looking at the mage class A1- alt Starfall and noticed the modifier, echo.  that should be available on the metro too."
- L118: "for the assassin, id give god killer the echo modification"
- L123: "and i was going to say, give monks palm strike echo too"
- L139: "give berserkers whirlwind ability echo"
- L141: "give the priest ability sacred heal echo too"
- L124 (Still Water, time-based, not a repeat): "when echo activates, it only reactivates the counter mele hits for a few seconds (like 3.)"
Locked: Echo is a second, weaker copy 1 s later, "each level: stronger echo". **Not locked: how strong, or how it is paid for.** That is this page.

## The problem (Lv 15 ability + Power+ 5 + Echo 5, budget rules in the draft section 5)
At the old 30-70% Echo three abilities broke: Meteor **2.50x** staff damage per Mana (cap 2.0x), Palm Strike **65%** and Whirlwind **60%**
of weapon damage (cap 50%). Starfall breaks exactly like Meteor (same ratio). Hundred Fists breaks the Monk **pair** rule (Palm + Fists 91%, cap 80%).
Heals, Bubble, God Killer and the two time-based Echoes (Still Water, Banner) fit even at 70% (Martyr's Grace 5.81%/s is close to the 6% cap).
Where each ability stops fitting (python3): Meteor / Starfall Echo <= **31%**, Whirlwind <= **32%**, Palm Strike <= **37%** (CD floor 5.0 s; 24% at CD 4.6 s).

## The 3 options
| | A. One curve for all (the refresh's proposal) | B. Per-ability caps | C. Keep 30-70%, Echo costs extra |
|---|---|---|---|
| Echo at L1 / L5 | **20% / 30%** everywhere (20 / 22.5 / 25 / 27.5 / 30) | Meteor, Starfall, Palm Strike, Whirlwind: **20% / 30%**. All others: **30% / 70%** (30 / 40 / 50 / 60 / 70) | **30% / 70%** everywhere |
| Meteor per Mana (cap 2.0x) | 1.98x | 1.98x | 2.00x (Echo 5 adds **+7.4 Mana**: 30 -> 37.4; Starfall 36 -> 44.9) |
| Palm Strike (cap 50%) | 48% (CD floor 5.0 s) | 48% (CD floor 5.0 s) | 50% (CD floor **6.0 s** with Echo 5, so no CD gain) |
| Whirlwind (cap 50%) | 49% | 49% | 50% (CD **16.9 s** at Echo 5, was 14 s) |
| God Killer (boss only, 8% of weapon rate) | 7.6% | 10.6% (70%) | 10.6% (70%) |
| Sacred Heal (cap 6%/s group) | 4.88%/s | 5.80%/s (70%) | 5.80%/s |
| Still Water / Banner | time-based, unaffected | unaffected | unaffected |
| Shield Bubble (cap 6%/s) | 1.73%/s | 2.27%/s | 2.27%/s |
| Martyr's Grace (cap 6%/s) | 4.44%/s | 5.81%/s (tight) | 5.81%/s (tight) |
| Hundred Fists, Monk pair with Palm (cap 80%) | 72% | 79% (Fists 70%, Palm 30%) | 81% (Palm 50% + Fists 31%) just **fails**; Fists wave gap 8 s -> 9 s fixes it |
| How it feels in play | Echo is a small bonus everywhere; same idea on every ability, easy to learn | Heals and God Killer get a big, noticeable second hit; the four damage Echoes stay small | Echo is big but you feel the price: a slower Palm Strike, a pricier Meteor, a longer Whirlwind |
| Build complexity | **Lowest**: one row `mods.echo.steps`, already specced | **Medium**: one steps row per ability (`mods.echo.<ability>.steps`), tooltip shows its own numbers | **Highest**: steps row + a Mana / cooldown penalty per ability that scales with the Echo level, shown in the tooltip |

Method: Meteor ratio = (3.0 x 1.28 x 1.25 + 3.0 x 1.28 x e) / Mana / 0.10 (1.28 = Lv 15 / Lv 1). Palm = (1.536 x 1.25 + 1.536 e) / CD. Whirlwind =
(3.84 x 1.5 + 3.84 e) / 14. Option C penalty = whatever Mana or seconds bring the value back to its cap; zero at Echo 30% (L1), growing to the L5 numbers above.

## Recommendation: A [default]
Same numbers on every ability, nothing new to build, and every budget passes with room. B gains very little (the three that break
are most of the damage Echoes anyway) and makes Echo mean different things per ability. C is the most "Hypixel" (power with a price) but
needs extra Mana / cooldown rules on three abilities and only just misses the Monk pair. If Skyy wants heals and God Killer to feel bigger,
take B, not C.

## Questions for Skyy
| # | Question | Default |
|---|---|---|
| 1 | Which Echo option: A (20-30% everywhere), B (70% on heals + God Killer, 30% on the four damage ones), or C (70% with a Mana / cooldown price)? | [A] |
| 2 | If A: should Sacred Heal / Shield Bubble / Martyr's Grace echo still feel weak (30% of a heal)? Or do you want their Echo stronger and only damage held down (that is B)? | [A, test it in game first] |

## For the local session
- Nothing here is verified in game: all budget numbers are the draft's model (1 H/s weapon rate, Meteor 0.10 H per Mana staff shot) - **UNVERIFIED**
  against real SkyyGear base damage.
- Once Skyy picks, update `research/cloud/Modifier-Pool-Spec.md` (Echo row), `research/cloud/Class-Ability-Spec-Draft.md` section 5 and
  the `mods.echo.*` rows listed in the pool spec; A needs no change (it is the current text).
- B and C need new per-ability config rows (`tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`) and Server Setup warnings via `abilities.budget.*`.
