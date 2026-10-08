# Shadow Step - the Assassin's dagger charged move (draft 2026-10-07)

Skyy picked Shadow Step over the Smoke Roll draft: "id prefer shadow step over shadow roll. shadow step, you just vanish, leaving behind
a fading shadow, and appear behind your enemy facing their back. so your next his is a guaranteed back stab. and do a small bonus on top
of that. (auto targets behind the nearest mob to where you are looking.0 withing like 24 blocks. if no mob is in that direction you
teleport straight to where you are looking, like 18 blocks forward. (can place you in the air, but not over the void. (still teleport,
just not far enough to put you in the void (do the same for mage, if you can.)"

Status: **design locked by Skyy's words above; numbers are placeholders** (Server Setup rows, SkyyArmory > Daggers, times in seconds).
Replaces the vanilla Pounce as the daggers' charged move. Not built yet.

## 1. Plain words

**Hold the attack (charge) with daggers and release**: you vanish, a **fading shadow** of you stays where you stood,
and you appear **behind the enemy nearest to where you are looking** (within 24 blocks), **facing its back**. Your next hit is a
**guaranteed backstab** plus a small bonus. No enemy that way: you step **straight where you look, up to 18 blocks** - you may end up in
the air or over the void (Skyy: no void protection, "its part of the fun/ challenge"; "if you fall, you have to try to quickly get back
out before you die"; "dont put any void protection on any traversal.").

## 2. How it works (defaults)

| Step | Default |
|---|---|
| Input | the daggers' CHARGED attack (hold + release), like every other traversal; right-click stays BLOCK (Skyy's right-click default) |
| Target | the hostile mob (or PvP-enabled player) whose direction is closest to your look direction, within **24 blocks** and inside a 30 deg cone, with line of sight |
| Arrive | 1.5 blocks behind the target, facing its back; if that spot is inside a block, the nearest free spot around the target's back half; none free -> beside it |
| No target | straight along your look (pitch included) up to **18 blocks**: the farthest free spot (2-block body passable), stopping 0.3 short of walls |
| Air / void | may land in the air or over the void - NO void protection (Skyy 2026-10-07: "actually, lets forget void protection, its part of the fun/ challenge") |
| Shadow | a dark, fading copy of your silhouette at the start point, ~1 s fade, purely visual; see-through and not distracting |
| Backstab | your next dagger hit within **3 s** is a guaranteed backstab (vanilla backstab bonus) **+ 10% damage** (the small bonus) |
| Cost | Stamina 4 (vanilla Max 10); not usable at 0 Stamina; a step that cannot move you at least 1 block costs nothing |
| Cooldown | 6 s Crude/Copper -> 4 s Onyxium; the class tree can cut it |
| Safety | the kunai teleport rules: never inside a block, through a wall, into another island, out of a locked arena |

## 3. Void rule for the Mage - DROPPED

Skyy first asked for the same void rule on the Mage teleport, then: "actually, lets forget void protection, its part of the fun/
challenge". The staff blink stays as it is live (`blink.floorCheck` 0 = off, Skyy's value). Old text kept below for the record.

### (dropped) Same void rule for the Mage

The staff TELEPORT (SkyyArmory blink, research/Magic-Traversal-Spec.md 2.2) has `blink.floorCheck` = "ground within N blocks below";
Skyy's live value is 0 = off, so today a blink CAN end over open void. New rule for the blink too: **air is fine, void is not** - a
landing spot is valid when ANY block exists below it (any depth); otherwise the blink is shortened to the last valid spot. Implement as
a new `blink.voidCheck` row (default on) next to `floorCheck` (kept; 0 = off as Skyy set it). Queued into SkyyArmory 0.1.7.

## 4. Server Setup rows (sketch)

`dagger.shadowStep.enabled`, `.targetRange` 24, `.targetCone` 30, `.behind` 1.5, `.noTargetDistance` 18, `.backstabWindow` 3,
`.backstabBonus` 0.10, `.shadowSeconds` 1, `.staminaCost` 4, `.cooldown.<metal>`.

## 5. Engine checks before building (UNVERIFIED)

1. Replace the daggers' charged interaction (vanilla Pounce) on dagger ids - the staff / wand route in SkyyArmory.
2. Pick the target in a cone with line of sight (reuse the kunai / wand target code).
3. Teleport + set yaw to face the target's back (the kunai teleport path + a rotation set).
4. Force the backstab for one hit (vanilla backstab flag) or add the bonus ourselves on the next damage event.
5. A fading shadow: a short-lived ghost model / particle silhouette of the player (cheap, see-through).

## 6. Open (defaults)

| # | Question | Default |
|---|---|---|
| 1 | Small bonus size | +10% on the guaranteed backstab |
| 2 | Works on players where PvP is on? | yes |
| 3 | All daggers (vanilla too) or only our metal daggers? | all daggers |
