# Ability code vs class design - gaps found 2026-10-16

Read-only survey of `SkyyClasses/build_skyyclasses_0.1.29.py` (walking shape) against `research/classes/<Class>.md`, made while
writing the "what does this ability do" texts (round cls0130). Nothing here is decided - each line is a gap to fix in code OR in the
design file. Level scaling everywhere is a multiplicative % with a soft cap (lvlMult), not "+1% per level" as several docs say.

## Not implemented / different behaviour
- **Spellblade Sunder:** Expose (+SU_EXPOSE% crit damage) is defined but never used - only the Weaken cut works.
- **Spellblade Arcane Breach:** AB_STACKCAP = 10 caps the Momentum bonus at +10%; the design says +25%.
- **Spellblade Elemental Imbue:** Momentum scaling is multiplicative (x(1 + n x MO_ELEMPERSTACK%)); design reads "+1% per stack" (additive).
- **Archer Explosive Arrow:** fires on ANY bow / crossbow hit in the window; the design says the next CHARGED shot.
- **Monk Flowing Form:** +1.5% attack speed per stack is shown only (no attack-speed hook).
- **Berserker Blood Frenzy / Warlord's Banner:** the attack-speed part is shown only (no attack-speed hook).
- **Assassin First Strike (Cloak, Vanishing Act):** +CL_STRIKE% (50) plain damage stands in for the design's +100% crit chance (no crit hook in SkyyGear yet).
- **Warrior Rallying Guard:** taunt 6 s (design 4 s), cut cap 40% (design ~30%); players 6 blocks / party 10.
- **Warrior Challenge, Guardian's Oath:** no section in research/classes/Warrior.md - the code comments are the only design (Challenge 12 blocks, 8 s, 30% cut, 20% reflect; Oath 15 blocks, 8 s, 40% share, 15% cut, 30-block leash).

- **Mage Starfall:** each star is 0.3 x hit (10% of a Meteor); design says ~40% of a Meteor (~1.2 x hit).
- **Mage Arcane Beam:** Power+ raises damage only; design says Power+ gives a faster ramp.
- **Priest Guardian Spirit:** each save also costs 1 Stamina (design: Mana only).
- **Priest Sanctuary:** the 60% per-zone heal cap equals 12 s x 5%, so any level above 1 just hits the cap sooner.
- **Priest Shield Bubble:** no explicit projectile block found (design: blocks projectiles).
## Code adds things the design never mentions (doc should catch up)
- Warrior Shield Shockwave: +stun per level (cap +0.6 s); the cone is 90 degrees in total (SS_ANGLE is a half-angle).
- Warrior Iron Chain: also deals IC_POWER x hit; bosses are not dragged unless the Pull modifier is on.
- Berserker Earthsplitter: 2.0 x hit; the "knock-up 1 s" is an upward push with no timer.
- Monk Hundred Fists: at most one shockwave per HF_GAP (8 s); hits only foes Awed by this caster.
- Monk Palm Strike: PS_POWER x hit, reach PS_REACH, cooldown drops PS_CD_LVL a level to PS_CD_FLOOR, +0.01 s stun a level.
- Monk Cyclone Kick: 0.8 x hit.
- Assassin Toxin: 0.25 x hit a second; refused with no aim target.
- Assassin God Killer: 12 s arm window, 80-degree backstab cone.
- Assassin Vanishing Act: smoke lasts VA_TIME x level multiplier; 25% slow.
- Archer Pinning Shot: pierces 2, PN_POWER x hit, +0.02 s root a level; bosses only slowed.
- Archer Arrow Rain: AR_POWER x hit total over the rain, 0.5% slow a level; starts AR_DELAY s after the cast.
- Archer Hunter's Net: HN_POWER x hit once on entry.

Unverified: the end of `facing()` (Still Water SW_FRONT half- or full-angle); Elemental Imbue "ends on swap to a non-class item".
