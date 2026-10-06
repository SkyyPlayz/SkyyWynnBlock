# Archer Extra Bolts and the Holstered Reload

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `/home/user/SkyyWynnBlock/docs/answered/classes.md` (lines 82-89, 95), `/home/user/SkyyWynnBlock/docs/answered/gear.md` (line 45), `/home/user/SkyyWynnBlock/research/Crossbow-Loaded-Spec.md` (sections 1.1-1.8, 2.5, 2.6, 6.1), `/home/user/SkyyWynnBlock/research/classes/Archer.md`, `/home/user/SkyyWynnBlock/research/cloud/Class-Tree-Paths.md` (Archer trunk T3 / T6), `/home/user/SkyyWynnBlock/research/cloud/Weapon-Speed-Tiers.md` (Crossbow = Slow, w 1.4), `/home/user/SkyyWynnBlock/RESUME.md` line 66. Every number is a placeholder and a Server Setup row (times in seconds). Sizing: **full round** (it touches ammo items and a saved-adjacent state, in SkyySkills).

## 0. Decisions followed (not re-decided)

| Source | Line |
|---|---|
| `/home/user/SkyyWynnBlock/docs/answered/classes.md` line 88 | APPROVED 2026-09-25: Archery level 15+ upgrades raise a crossbow's max bolt capacity, **up to +4 extra bolts**. |
| `/home/user/SkyyWynnBlock/docs/answered/classes.md` line 89 | APPROVED 2026-09-25: **late-game only**, near the top of the Archer tree, a holstered crossbow reloads itself in **about 30 s** while you use another weapon. Not early or mid tier. |
| `/home/user/SkyyWynnBlock/docs/answered/classes.md` lines 83-87 | LOCKED: stay-loaded is Archery 5, Archer only, crossbows only; kept across teleports; sound + chat hint; per-player switches. |
| `/home/user/SkyyWynnBlock/docs/answered/classes.md` line 62 and line 85 | LOCKED: two crossbows share ONE big-arrow meter, kept across a slot switch. |
| `/home/user/SkyyWynnBlock/docs/answered/gear.md` line 45 | LOCKED: the 3rd bolt in a row (Hytale's charged hit) counts for the Charged Attack Damage modifier. |
| `/home/user/SkyyWynnBlock/docs/answered/classes.md` line 95 | LOCKED: crossbows keep the vanilla charged attack as traversal for now (Dodge Roll stays an idea). |

## 1. The key fact: "extra bolts" means a higher cap, not a bigger reload

Vanilla already holds up to **6** bolts (`Ammo` stat cap 6, added while a crossbow is in hand; `/home/user/SkyyWynnBlock/research/Crossbow-Loaded-Spec.md` 1.1). A reload loads one bolt at a time, each costing 1 Crude Arrow, until the stat is full (1.2). So:

- "Extra bolts" = the cap goes **6 -> 6 + k** (max **10**, lock "up to +4").
- It is NOT "bolts per reload 1 -> 2". Vanilla's reload loop keeps going until the cap, so a higher cap simply makes the same loop run longer.
- Firing costs no arrows; loading does. More capacity means more arrows sitting in the magazine, never free ammo.

## 2. Capacity ranks

Level = Archery skill level (the lock says "Archery level 15+"). `/home/user/SkyyWynnBlock/research/cloud/Class-Tree-Paths.md` T3 says "Lv 15, +1 bolt, up to +4 at Lv 55": I turn that into four ranks.

| Rank | Archery Lv | Extra bolts | Cap | Magazine vs vanilla |
|---|---|---|---|---|
| 0 | below 15 | 0 | 6 | - |
| 1 | 15 | +1 | 7 | +17% |
| 2 | 30 | +2 | 8 | +33% |
| 3 | 42 | +3 | 9 | +50% |
| 4 | 55 | +4 | 10 | +67% |

Not the "1 -> 2 at 15, 3 at 40, 4 at 75" shape: vanilla is already 6, and 4 steps match the lock's +4. Tree node cost stays T3 (2 pts) in Class-Tree-Paths; ranks 2-4 would be 3 more upgrade pips. The Server Setup row is a list `15,30,42,55`.

## 3. How a bigger magazine fires and shows

1. **Cap.** While a crossbow is held, SkyySkills adds one named Additive modifier `+k` to the `Ammo` stat (same mechanism as vanilla's `+6`). The vanilla reload loop (`Common_StatAmmoReload_Entry`) already repeats "while Ammo < 100%", so reload fills to the new cap with no new interaction.
2. **Firing.** Unchanged vanilla: each shot spends 1 `Ammo`. No change to the shot, speed or reload animation.
3. **HUD.** The vanilla bolt counter (`DisplayEntityStatsHUD: Ammo`) is the stat, so it shows 7..10 by itself. Whether the bar reads value/max or only a number is UNVERIFIED.
4. **Tooltip.** Item tooltips are shared by all players, so the crossbow tooltip cannot say "+2". Show it instead on the `/skills` Archery page ("Bolt capacity 8") and in the existing chat hint when the bolts go back in ("Reloaded 8 bolts").
5. **Level-up.** The new cap applies on the next crossbow equip or hotbar recalculation; the current load is not topped up for free (reload to fill it).

## 4. Damage per bolt and DPS

Recommended: **damage per bolt is unchanged** (no penalty). Reason: sustained DPS barely moves because the reload also grows. Example with placeholder timings (shot 0.5 s, 0.8 s ready, 0.7 s per bolt loaded; the real values are UNVERIFIED), checked with python:

| Cap | Burst time | Full cycle | Sustained bolts/s |
|---|---|---|---|
| 6 | 3.0 s | 8.0 s | 0.750 |
| 8 | 4.0 s | 10.4 s | 0.769 |
| 10 | 5.0 s | 12.8 s | 0.781 |

Cap 10 gives about **+4% sustained DPS** but **+67% burst** before the player must reload. So the perk is a burst / safety perk: it is fair as is. It pairs with the Slow crossbow tier (`/home/user/SkyyWynnBlock/research/cloud/Weapon-Speed-Tiers.md` section 3). If real timings give much more than +10% sustained, add a small per-extra-bolt damage trim (row `xbow.extraBoltDamagePct`, default 0, e.g. -3% per extra bolt).

## 5. Interaction with the 3rd-bolt bonus

- The charged hit is "the 3rd bolt in a row on the same target" (`/home/user/SkyyWynnBlock/research/Charged-Attack-Research.md` line 50). It is engine behaviour, not ours; we do not touch it.
- Open engine question: is the counter 3 then reset, or every 3rd bolt (3, 6, 9)? And does a reload or a swap reset it? If it repeats, a 10-bolt magazine has 3 charged hits against 2 in 6 (same 33%). Fine either way; no change needed.
- SkyyGear's Charged Attack Damage modifier (LOCKED) keeps working unchanged because it keys off the charged damage class.

## 6. Ammo, quiver and sack pull

- Loading pulls Crude Arrows from the combined hotbar + storage + backpack (vanilla `ModifyInventory`, Adventure only). SkyySacks never pockets arrows, so no sack pull exists and none is added.
- Vault arrows and the daily arrow refill (LOCKED, classes.md line 80) are separate; they feed the same inventory.
- **Bigger cap = more arrows to load** (up to 10 per reload). The daily refill amount may need a bump (question 5).
- T2 Quiver Craft ("10% chance to recover a fired arrow") is awkward because arrows are spent on loading, not firing. Define it as: on each reload step, 10% chance the arrow is not consumed. Needs a hook (question 6).

## 7. Stay-loaded must handle the extra bolts (anti-dupe fix)

Vanilla's switch-away refund ladder only covers up to **6** bolts (`StatsCondition Costs{Ammo:6}..{1}`, 1.3), and leaves `Ammo` untouched. At cap 10 the player is refunded 6, but SkyySkills would remember 10 and charge 10 on return, so 4 arrows would be paid twice. Fix:

1. On switch-away, our handler reads `Ammo` = n (exactly what is loaded), computes `excess = max(0, n - 6)` and gives `excess` Crude Arrows itself (same `addOrDropItemStack`), so total refund = n.
2. On return, pay n 1:1 (`min(n, have)`) as already specified (2.5).
3. Net zero in every path. If the player is in Creative, no refund and no payment (existing rule).

## 8. The holstered reload

**What it does.** A crossbow kept in a hotbar slot, not held, refills to the full cap over **N = 30 s** (LOCKED "about 30 s"), while the player uses another weapon.

**State.** The `Ammo` stat has cap 0 when no crossbow is in hand (1.1), so a holstered load cannot live in the stat. It lives in the existing in-memory `XbowState` (`n[slot]`, stack identity per slot, 2.3). Changes:

1. Keep an entry for a crossbow even when `n = 0` (today only `n > 0` is kept), with a `holsterStart` tick.
2. Each tick (already in `Xbow.tick`), for each entry with `n < cap` and `ticks - holsterStart >= N*TPS`: set `n = cap` and pay the missing bolts in Crude Arrows from the inventory (`pay = min(missing, have)`; partial fill if short). Then the existing return restore sets the stat.
3. The timer starts when the crossbow is put away (or when it was last topped up). A full-time refill, not per bolt: 30 s whatever the size (default). Optional row for a per-bolt trickle (`30 / missing` s each).
4. Stays memory only: relog, death, profile switch drop it (same as stay-loaded). Teleports keep it (LOCKED).
5. Sound + chat hint "Crossbow ready" when it completes (a separate player switch, like the others).

**Node level.** Class-Tree-Paths T6 puts it at Lv 55, which is mid-tree; the lock says near the top and not mid. Recommend Lv **75** (default), 3 pts, with a Server Setup row. This makes `/home/user/SkyyWynnBlock/research/cloud/Class-Tree-Paths.md` T6 need a move (question 2).

**Anti-dupe.** Arrows are taken at completion, never created. If the crossbow is dropped, traded, sold or moved, the entry is cleared (the item carries no hidden data). With 2 crossbows, each has its own entry but there is ONE shared big-arrow meter (LOCKED).

## 9. Engine probes needed (the local session)

See "For the local session (UNVERIFIED)" below.

## 10. Server Setup rows (SkyySkills -> Archery / Crossbows)

| Row | Default | Notes |
|---|---|---|
| `xbow.extraBolts.enabled` | on | off = cap 6 for all |
| `xbow.extraBolts.levels` | 15,30,42,55 | one level per +1, max 4 entries |
| `xbow.extraBolts.max` | 4 | hard cap on the bonus; Ammo never above 6 + this |
| `xbow.extraBoltDamagePct` | 0 | trim per extra bolt, if DPS needs it |
| `xbow.holster.enabled` | on | |
| `xbow.holster.level` | 75 | Archery level |
| `xbow.holster.seconds` | 30 | time to refill |
| `xbow.holster.mode` | whole | whole / per bolt |
| `xbow.holster.sound`, `.hint` | on | player switches in `/settings` too |

## For the local session (UNVERIFIED)

1. Does a second Additive modifier on `Ammo` stack with the vanilla `"*Weapon_"` `+6` and survive `recalculateEntityStatModifiers` (key naming, clearing rules)? Fallback: bump `EntityStatValue` max directly each tick.
2. Does the vanilla reload loop (Common_StatAmmoReload_Entry) really run to a cap above 6, and what are the real per-bolt and ready times (used in section 4)?
3. Does the HUD counter show max, and does a cap of 10 fit the bar?
4. Is the 3rd-bolt counter "3 then reset" or "every 3rd", and does reload or swap reset it?
5. `SwapFrom` ladder refunds at most 6 (VERIFIED in the spec); confirm the engine leaves `Ammo` at 7-10 so our excess refund reads the true value.
6. Does `SignatureEnergy` / the big-arrow meter react to a cap above 6?
7. Can holstered state be kept per slot with `n = 0` without breaking the `pendSlot` restore (2.5)?
8. Is the Archery level checked against the skill, or the class skill (Class-Tree-Paths nodes use the class skill)? Confirm which level the rows use.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Extra bolts means cap 6 -> up to 10 (vanilla already holds 6). Is that what you meant? | Yes, +1 each at 15 / 30 / 42 / 55 |
| 2 | Holstered reload at which level? (Class-Tree-Paths had 55; you said near the top.) | 75 |
| 3 | Holster refill: whole magazine after 30 s, or one bolt at a time? | Whole, 30 s |
| 4 | Keep damage per bolt unchanged (about +4% sustained DPS, +67% burst)? | Unchanged |
| 5 | Raise the daily Archer arrow refill because of the bigger magazine? | Leave; revisit after testing |
| 6 | Quiver Craft: 10% chance a loaded arrow is not consumed? | Yes |
| 7 | Should the holster also work for a held-not-moving crossbow that fell to 0 (e.g. while sneaking)? | No, only holstered |
