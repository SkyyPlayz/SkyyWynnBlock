# Smoke Roll - the Assassin's dagger charged move (idea draft 2026-10-07)

Skyy: "the assain section on the dagger mentions a smoke roll, what is that?" -> "write up the smoke roll idea". Status: **IDEA, not
locked.** Daggers keep the vanilla Pounce until Skyy picks this (docs/answered/classes.md 2026-10-04: "we can change it up later").
Every number is a placeholder and a Server Setup row (SkyyArmory > Daggers; times in seconds).

## 1. Plain words

Hold right-click with daggers, release: you **roll past your target and come up behind it**, leaving a **puff of smoke** where you
started. Mobs in the smoke lose track of you for a moment, and your **next stab counts as a backstab**. It is an attack move, not a
dodge.

Why it is not the dodge roll: everyone already has the quick 8-way dodge roll on a sprint tap (SkyySkills 0.4.20; Skyy 2026-10-06:
a dodge roll as normal movement beats a click-and-hold move for a small hop). Smoke Roll is slower to start (a charge), aims at an
enemy, and pays off with the backstab - the Assassin's job.

## 2. How it works (defaults)

| Step | Default |
|---|---|
| Charge | hold like any charged attack (vanilla charge time of the dagger) |
| Target | the enemy under your crosshair within 6 blocks; no target -> a straight 5-block roll forward (still leaves smoke) |
| Roll | a fast low roll (~0.4 s) along the ground to 1.5 blocks BEHIND the target, facing it; stops at walls / ledges (no rolling off cliffs unless you aimed there) |
| Smoke | a grey cloud, radius 2.5 blocks, 3 s, at the start point; see-through enough not to blind the player (same rule as the Mana Barrier dome: visible, easy to see through) |
| Lose track | mobs inside the smoke, or that were targeting you when you rolled, drop their target for 1.5 s (bosses: no, only a 0.5 s stagger) |
| Backstab window | your next dagger hit within 2 s counts as from behind (vanilla backstab bonus) + 20% damage |
| Safety | you take no damage during the roll's first 0.25 s (the same i-frames as the dodge roll, not more) |
| Cost | Stamina 4 (vanilla Stamina Max is 10); not usable at 0 Stamina |
| Cooldown | 6 s Crude/Copper -> 4 s Onyxium (better daggers = shorter); the class tree can cut it further |
| PvP | works on players where PvP is on; "lose track" does nothing to players (only the smoke + backstab window) |

## 3. Upgrades (class tree ideas, not locked)

- **Thicker Smoke** - bigger / longer cloud; enemies in it are slowed 20%.
- **Double Roll** - a second roll within 1 s (same cost).
- **Poison Smoke** - the cloud deals light damage over time.
- **Vanish** - 1 s of invisibility after the roll (ties into the Assassin's cloak ability; check overlap).

## 4. Server Setup rows (sketch)

`dagger.smokeRoll.enabled`, `.targetRange` 6, `.rollBehind` 1.5, `.noTargetDistance` 5, `.rollSeconds` 0.4, `.smokeRadius` 2.5,
`.smokeSeconds` 3, `.loseTrackSeconds` 1.5, `.bossStaggerSeconds` 0.5, `.backstabWindow` 2, `.backstabBonus` 0.20, `.iframeSeconds`
0.25, `.staminaCost` 4, `.cooldown.<metal>`.

## 5. Engine checks before building (UNVERIFIED)

1. Replacing the dagger's charged interaction (vanilla Pounce) on our dagger ids only - the staff / wand route in SkyyArmory.
2. A server push to a point behind a mob without passing through blocks (reuse the kunai teleport safety check + the dodge roll push).
3. Making a mob drop its target for N seconds (NPC target / aggro API) - the riskiest part.
4. A smoke particle cloud that is visible but see-through (particle alpha), cheap on the server.
5. Forcing the "from behind" backstab flag for one hit (or adding the bonus ourselves on the next damage event).

## 6. Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Roll BEHIND the target (attack move), or a free-direction roll with smoke (escape move)? | behind the target |
| 2 | Mobs lose track of you in the smoke? | yes, 1.5 s (not bosses) |
| 3 | Next stab = backstab + 20%? | yes |
| 4 | Replace Pounce on all daggers, or only our metal daggers (vanilla daggers keep Pounce)? | all daggers |
| 5 | Stamina 4 + cooldown 6 -> 4 s by metal? | yes |
