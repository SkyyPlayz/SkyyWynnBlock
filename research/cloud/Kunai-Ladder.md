# Kunai Ladder (Crude to Onyxium, then 5 new tiers)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `/home/user/SkyyWynnBlock/docs/answered/classes.md` (lines 36, 43-44, 47, 96), `/home/user/SkyyWynnBlock/research/classes/Assassin.md`, `/home/user/SkyyWynnBlock/research/SkyyArmory-Spec.md` (1.1 ids, 5.1 recipes), `/home/user/SkyyWynnBlock/research/cloud/SkyyArmory-Roadmap.md` (sections 2, 4), `/home/user/SkyyWynnBlock/research/cloud/Weapon-Speed-Tiers.md` (sections 2-5), `/home/user/SkyyWynnBlock/research/cloud/Spellbook-Ladder.md` (format), `/home/user/SkyyWynnBlock/research/cloud/Class-Tree-Paths.md` (Path C Blink), `/home/user/SkyyWynnBlock/research/Magic-Traversal-Spec.md` (blink safety), `/home/user/SkyyWynnBlock/research/Charged-Attack-Research.md` (vanilla kunai row), `/home/user/SkyyWynnBlock/research/Gear-Levels-Wynn-Spec.md`, `/home/user/SkyyWynnBlock/research/Mob-Curve-Spec.md` (K rule). Every number is a placeholder and a Server Setup row (times in seconds).

## 0. Decisions followed (LOCKED, not re-decided)

| Lock | Source | Used here |
|---|---|---|
| Assassin = daggers (vanilla) + kunai (new); 2 weapon types per class, no sharing | `/home/user/SkyyWynnBlock/docs/answered/classes.md:36` | Class gate (section 8) |
| Kunai: attack = throw. Charged = THROW + TELEPORT to where it lands (within ~20 blocks; out of range -> appear where it left range). Hold right-click = RETURN to where you were, AoE knockback; default window ~8 s | `/home/user/SkyyWynnBlock/docs/answered/classes.md:43`, `/home/user/SkyyWynnBlock/research/classes/Assassin.md` | Sections 2-4. The ~20 blocks and ~8 s are the **Crude / Copper** rung |
| Daggers keep the vanilla charged Pounce for now | `/home/user/SkyyWynnBlock/docs/answered/classes.md:44` | Dagger is the yardstick (section 3) |
| Every traversal costs Mana AND Stamina; physical ones cost more Stamina than Mana; a teleport that does not move you costs nothing | `/home/user/SkyyWynnBlock/docs/answered/classes.md:96` | Section 4 (kunai = physical: Stamina 2 : Mana 1) |
| Metal bands Crude 1-13, Copper 10-18 ... Onyxium 40-49; proposed Cindersteel 50-59 ... Aetherium 86-100 | `/home/user/SkyyWynnBlock/docs/answered/gear.md:43`, `/home/user/SkyyWynnBlock/research/cloud/SkyyArmory-Roadmap.md` section 2 | Both ladders |
| Class tree Path C (Blink) edits this ladder: Kunai Reach +3, Long Throw 20 -> 26, Hard Return, Double Step | `/home/user/SkyyWynnBlock/research/cloud/Class-Tree-Paths.md` (T3, K1-K5) | Range stays **20 at every metal** so the tree has room to add (section 4) |

## 1. Plain words (for Skyy)

- The Kunai is **one reusable weapon, a stack of 1, like every gear item**, with **no durability** (Skyy 2026-10-07: "a single item you hold onto without durability, that shoots kunai projectiles" - never stacks of thrown kunai). The thrown kunai you see is only a flying picture. **Nothing leaves your inventory**, so there is nothing to lose, drop or duplicate.
- A new ladder Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium (same metals as the daggers), later Cindersteel to Aetherium.
- Per hit the kunai hits a little harder than a dagger, but it swings slower and carries range, so its damage per second is **80% of the dagger's**. The teleport is the rest of its value.
- Better metals: cheaper, shorter cooldown, longer return window, wider return knockback. **Range stays about 20 blocks** on every metal (your lock); the class tree is what extends it.
- The teleport never puts you inside a block, through a wall, into someone else's island or out of a locked boss arena. **Over the void is allowed** (Skyy 2026-10-07: "dont put any void protection on any traversal.").

## 2. Items and ids (research/SkyyArmory-Spec.md 1.1 id rules)

Pattern `Weapon_Kunai_<Metal>`: prefix `Weapon_`, family word `Kunai`, then the metal word; **no "skyy" anywhere** (`GearData.skyyItem` would stop it being gear).

| Item id | Name | Band (SkyyGear, by the metal word) | Mirrors |
|---|---|---|---|
| `Weapon_Kunai_Crude` | Crude Kunai | 1-13 | `Weapon_Daggers_Crude` |
| `Weapon_Kunai_Copper` | Copper Kunai | 10-18 | Copper Daggers |
| `Weapon_Kunai_Iron` | Iron Kunai | 15-23 | Iron Daggers |
| `Weapon_Kunai_Thorium` | Thorium Kunai | 20-28 | Thorium Daggers |
| `Weapon_Kunai_Cobalt` | Cobalt Kunai | 25-38 | Cobalt Daggers |
| `Weapon_Kunai_Adamantite` | Adamantite Kunai | 35-43 | Adamantite Daggers |
| `Weapon_Kunai_Mithril` | Mithril Kunai | 40-49 | Mithril Daggers |
| `Weapon_Kunai_Onyxium` | Onyxium Kunai | 40-49 | Onyxium Daggers |
| `Weapon_Kunai_Cindersteel` ... `_Aetherium` (later row) | Cindersteel Kunai ... | 50-59, 58-67, 66-75, 76-88, 86-100 | Roadmap section 2 (Voidglass and Aetherium drop-only) |

- Quality / ItemLevel copy that metal's vanilla Sword (same rule as the wands). `MaxStack` unset = 1 (the engine gives 1 to any item with a `Weapon` section, VERIFIED for wands in 1.1). `Tags` `{"Type": ["Weapon"], "Family": ["Kunai"]}`, `Categories` `["Items.Weapons"]`, `PlayerAnimationsId` `Throwing_Knife` (UNVERIFIED for main-hand use).
- **The vanilla `Weapon_Kunai` stays as it is** (a single item, SkyyGear band 20-27, throw 6, thrown from the off-hand, VERIFIED in `/home/user/SkyyWynnBlock/research/Charged-Attack-Research.md` row "Kunai" and `/home/user/SkyyWynnBlock/research/Class-Roles-Ideas.md:229`). It is a loot item with no teleport. Skyy's lock names the Assassin's kunai; whether the vanilla one also teleports is question 4.
- **Id trap:** SkyyGear's band lookup reads the id words from the left, longest entry first, and the vanilla `Kunai` has its own band (20-27). `Weapon_Kunai_Copper` could resolve to 20-27 instead of 10-18. The build must stop on this unless SkyyGear checks the metal word first (UNVERIFIED, section 9, item 1).
- Asset ids that are not items keep the pack prefix: `SkyyArmory_Kunai_Throw_<Metal>`, `SkyyArmory_Kunai_Teleport_<Metal>`, `SkyyArmory_Kunai_Return_<Metal>`.
- Recipes mirror that metal's **Daggers** recipe (same bench, tab, inputs; `/home/user/SkyyWynnBlock/docs/answered/gear.md:12`). Onyxium has no vanilla recipe, so it takes the Mithril one with Onyxium Bars (the wand answer). New tiers: Smithy, collection-gated (R3), Bar x4 + the zone core x1 placeholder; Voidglass and Aetherium are drops only. A crafted kunai never sells above its inputs plus the 22.2% Bazaar spread, so no craft-and-sell loop.

## 3. Stack size, pickup and "lost kunai" (recommendation)

| Option | What it is | Verdict |
|---|---|---|
| **A. One reusable kunai, stack of 1** | The item stays in your hand. A throw spawns a **projectile entity** (a picture with a hit position). It is never an item | **Recommended** |
| B. A stack of thrown ammo | Each throw consumes one; you pick them up | Rejected |

Why A (item loss and dupes are a full-round topic, `/home/user/SkyyWynnBlock/PROJECT-RULES.md` 4):

- **Gear identity needs a stack of 1.** Level, rarity, rolled stats, reforge and identify live on the stack. SkyyGear treats ammo words as ammo, so a stack could never carry rolls (SkyyArmory 1.1: `GearData.ammoMs`).
- **No item entity is ever created**, so a kunai cannot be dropped to duplicate it, picked up by another player, burn in lava, fall into the void, be caught by a hopper or despawn.
- **Nothing to auto-return.** The "return after N s" idea is not needed; the Return in section 4 is the player's own move back, not the item's.
- Anti-spam: the throw is limited by the Fast cadence (0.35 s), the teleport by its cooldown. The projectile has a `kunai.flightTtl` (default 1.5 s) and removes itself, so no stuck kunai pile in walls.
- Edge cases: you swap or drop the kunai **while it flies** -> the in-flight teleport is cancelled and refunded (the weapon is the authority). You die in flight -> cancelled. You log out in flight -> cancelled. The kunai picture sticks in a wall for 0.5 s as a visual only.
- Cost to Skyy: you cannot "run out" of kunai. That matches Skyy's wording (a weapon, "kunai attack = throw") and the daggers (you never run out of daggers).

## 4. The moves and the ladder numbers

**Attack (tap).** Throws one kunai in a straight line (almost no arc), range 20 blocks, no Mana or Stamina cost. It hits the first mob or player in its path. Weapon speed **Fast** (interval 0.35 s, hit weight w = 0.7, `/home/user/SkyyWynnBlock/research/cloud/Weapon-Speed-Tiers.md` section 3). Backstab does **not** apply (a thrown hit has no "behind"); the Assassin's First Strike crit does.

**Charged (hold, release) = Throw + Teleport.** Needs the charge (0.6 s, `kunai.charge`). The kunai flies up to the range; you appear at the hit position (rules in section 5). Cost: **Stamina 2 : Mana 1** (physical traversal rule; the Assassin's pool is about 10 Mana and Stamina max is 10, `/home/user/SkyyWynnBlock/research/Magic-Traversal-Spec.md` 2.7). The charge does a hit on the target like a tap (no extra "charged" bonus).

**Return (hold right-click).** For `ret.window` seconds after a teleport you can hold right-click to go back to the **exact spot you left**, with an AoE knockback there on arrival. One return per teleport. A return costs nothing. If the spot is no longer safe, the return puts you at the nearest safe spot within 3 blocks or fails with a message and no refund of the window.

Tier numbers (the range 20 is locked; Class Tree Path C adds to it). Mana is half the Stamina, whole numbers:

| Tier (band) | Teleport range | Cooldown (s) | Stamina | Mana | Return window (s) | Return knockback radius (blocks) |
|---|---|---|---|---|---|---|
| Crude (1-13) | 20 | 7.0 | 6 | 3 | 8 | 3.00 |
| Copper (10-18) | 20 | 6.0 | 6 | 3 | 8 | 3.00 |
| Iron (15-23) | 20 | 5.5 | 6 | 3 | 8 | 3.25 |
| Thorium (20-28) | 20 | 5.0 | 6 | 3 | 9 | 3.50 |
| Cobalt (25-38) | 20 | 4.5 | 5 | 2 | 9 | 3.75 |
| Adamantite (35-43) | 20 | 4.0 | 5 | 2 | 10 | 4.00 |
| Mithril (40-49) | 20 | 3.5 | 5 | 2 | 10 | 4.25 |
| Onyxium (40-49) | 20 | 3.5 | 5 | 2 | 10 | 4.25 |
| *Cindersteel (50-59)* | 20 | 3.0 | 4 | 2 | 11 | 4.50 |
| *Amberite (58-67)* | 20 | 3.0 | 4 | 2 | 11 | 4.75 |
| *Drakonite (66-75)* | 20 | 2.5 | 4 | 2 | 12 | 5.00 |
| *Voidglass (76-88)* | 20 | 2.5 | 4 | 2 | 12 | 5.25 |
| *Aetherium (86-100)* | 20 | 2.0 | 4 | 2 | 12 | 5.50 |

- With the class tree (T3 +3, K1 -> 26) the range is 20 / 23 / 26 / 29 at most. K2 Hard Return (window 8 -> 6 s) and K3 Double Step (a second teleport at half Stamina) read these rows, so the tree numbers are deltas on this table.
- A teleport with no Stamina left fails like a dodge does (no throw, no Mana spent). Stamina 6 of 10 at Crude means about one teleport per refill at Lv 1, which is the intent: a traversal, not a flight mode.
- Return knockback pushes hostile mobs and, only where world PvP is on, non-party players. It does **no damage** by default (`ret.damage` 0), as the lock says "knockback".

## 5. Throw damage per tier against the dagger

Python-checked. Units: **H** = one Medium-speed hit at that level (SkyyGear: `kOf x F(L) x material bonus`; F from the `base.curve` in `/home/user/SkyyWynnBlock/research/Mob-Curve-Spec.md:222`, linearly interpolated between its points, which is an assumption; bonus = 1 + 0.3% x band start). The tier is DPS-neutral, so hit = weight x H.

- Dagger: Super Fast, w = 0.5, interval 0.25 s -> **0.5 H per hit, 2.0 H/s**.
- Kunai: Fast, w = 0.7, interval 0.35 s. Rule: kunai hit = dagger hit x (0.7 / 0.5) x `kunai.dpsShare`. With `kunai.dpsShare` = **0.80** the hit is **1.12 x the dagger's (0.56 H)**, DPS **1.6 H/s = 80%** of the dagger's. The 20% buys range and a teleport; a dagger also has backstab and Pounce.
- Vanilla check: the vanilla Kunai throws 6 vs about 4.5 for an average dagger hit (swings 3 / 3, stabs 5 / 7, `/home/user/SkyyWynnBlock/research/Gear-Levels-Wynn-Spec.md:150`) = 1.33 per hit. Our 1.12 is lower on purpose (the vanilla item has no teleport).

| Tier | Band start | F(L) x bonus (= H) | Dagger hit | Kunai hit | Dagger DPS (H x 4) | Kunai DPS |
|---|---|---|---|---|---|---|
| Crude | 1 | 1.00 | 0.50 | 0.56 | 2.0 | 1.6 |
| Copper | 10 | 2.06 | 1.03 | 1.15 | 4.1 | 3.3 |
| Iron | 15 | 2.26 | 1.13 | 1.27 | 4.5 | 3.6 |
| Thorium | 20 | 2.47 | 1.24 | 1.39 | 5.0 | 4.0 |
| Cobalt | 25 | 3.33 | 1.67 | 1.87 | 6.7 | 5.3 |
| Adamantite | 35 | 7.18 | 3.59 | 4.02 | 14.4 | 11.5 |
| Mithril / Onyxium | 40 | 10.75 | 5.38 | 6.02 | 21.5 | 17.2 |
| *Cindersteel* | 50 | 20.12 | 10.06 | 11.27 | 40.2 | 32.2 |
| *Amberite* | 58 | 25.24 | 12.62 | 14.13 | 50.5 | 40.4 |
| *Drakonite* | 66 | 36.66 | 18.33 | 20.53 | 73.3 | 58.6 |
| *Voidglass* | 76 | 59.68 | 29.84 | 33.42 | 119.4 | 95.5 |
| *Aetherium* | 86 | 96.61 | 48.31 | 54.10 | 193.2 | 154.6 |

- Flat per-hit lines (True Damage, flat element) are multiplied by w (Weapon-Speed-Tiers section 4), so the kunai gets 0.7 of a Medium weapon's flat per hit.
- Weapon-Speed-Tiers lists "charged attacks / traversals: not weighted (w = 1)". The kunai's **teleport hit** is the same hit as a tap (0.56 H), not a Medium hit; the charge exists for the move, not for damage (question 3).
- Distance falloff: none by default. Headshots: none.

## 6. Anti-abuse (the teleport safety check)

The landing point is computed on the server from the projectile's hit position, then validated. Any failed check ends the teleport **at the last valid point on the flight path** (never "nothing happens" silently; the Mana and Stamina are refunded in full when you do not move).

| Rule | How |
|---|---|
| No teleport into blocks | Hit on a block: land 0.6 block back along the hit normal; feet and head blocks must be passable (`BlockType.EMPTY` or `!blocksLineOfSight`, the same test as the staff blink, `/home/user/SkyyWynnBlock/research/Magic-Traversal-Spec.md` 2.2) |
| Not through walls | Flight stops at the first solid block (glass, fences and leaves block it like walking); the 0.5-block step scan keeps a one-block wall from being skipped |
| Hit on a mob | Land 1.0 block in front of the mob on the line back toward you, never inside it, never behind it (behind = a free backstab; `kunai.behindMob` off) |
| Out of range | Appear at the last safe point of the flight (the lock: "where it left range") |
| Over void | **No void protection** (Skyy 2026-10-07, `docs/answered/classes.md` line 117): the throw may land over open void; falling is a race to get back out. The old `kunai.floorCheck` ground rule is dropped |
| Other players' islands | A SkyyIslands island you are not on the list for (owner, party, visitors) cannot be entered by the throw: it stops at the island edge. SkyyIslands protects by events and has no border walls (Magic-Traversal-Spec 2.7), so this needs a new bridge check (UNVERIFIED, section 9) |
| Pocket Shards (minions) | A throw may not land on a block inside someone else's claimed island; minions on your own island are fine. No special rule for the shard itself (it is on the island) |
| Locked arenas | Boss arenas and dungeon rooms with locked doors (Capstone, Elites) are not teleported out of, into or past (`kunai.noArena`): the throw stops at the door |
| Combat | **Not blocked by default.** "Teleport in, hit, teleport out" is the Assassin's job (`research/classes/Assassin.md`). `kunai.noCombat` (off) and `kunai.noCombatBoss` (off) exist for Skyy; question 2 |
| PvP | Teleporting next to a player is allowed only where world PvP is on **or** the target is a party member. With PvP off the throw does not land on players (it passes through; no damage, engine rule `PlayerDamageFilterSystem`). Return knockback pushes only PvP-enabled non-party players |
| World | Same world only; no cross-world teleports. Creative mode keeps no special bypass |
| Spam | Cooldown per tier, Stamina; `kunai.maxPerMinute` 12 as a safety net |
| Exploit | No teleport while dead, in a vehicle or while a menu is open; the teleport is cancelled if the kunai leaves your hand mid-flight |

## 7. Art idea (UNVERIFIED)

- **Recolour the vanilla Kunai's model and texture** per metal (the wand art kit `/home/user/SkyyWynnBlock/tools/skyyart.py` generates textures at build time from vanilla files; nothing vanilla is committed, `/home/user/SkyyWynnBlock/PROJECT-RULES.md` 2). Shape unchanged; the blade takes the metal colour, the cord wrap stays. Copper orange, Iron grey, Thorium pale green-grey, Cobalt blue, Adamantite deep red-bronze, Mithril silver-blue, Onyxium black with violet lines; new tiers as in the Roadmap section 2.
- Crude kunai: a plain dark grey stone-and-wood version (reuse the Crude dagger's palette).
- The flying projectile uses the same recoloured model plus a short trail in the tier colour; the arrival and return use the vanilla teleport or smoke particle (name UNVERIFIED).
- Whether a vanilla "throwing knife" model exists besides the Kunai item is UNVERIFIED; the vanilla `Weapon_Kunai` already is that model.

## 8. Class gate and other mods

- `Weapon_Kunai_*` is an **Assassin** weapon (a prefix in SkyyClasses, like `Weapon_Wand_` for the Priest, `C:254`); non-Assassins can hold it but their hits do nothing (the existing hit-block popup). Daggers stay vanilla for now (`docs/answered/classes.md:44`).
- First Strike and God Killer apply to kunai hits; the teleport does not break the cloak (a cloaked arrival is the combo), but the throw hit does (cloak breaks on attack).
- The unidentified item for the kunai type already exists (`Skyy_Unid_Weapon_Kunai`, `/home/user/SkyyWynnBlock/research/Loot-Unid-Spec.md:99`); its representative would become the Crude Kunai or the vanilla Kunai (question 4).

## 9. Server Setup rows (SkyyArmory > Kunai; times in seconds)

| Row | Default | Meaning |
|---|---|---|
| `kunai.enabled` | on | whole kunai ladder |
| `kunai.dpsShare` | 0.80 | kunai DPS as a share of the dagger's (hit = dagger hit x 0.7/0.5 x this) |
| `kunai.range.<metal>` | 20 | teleport range (blocks), one row per metal |
| `kunai.throwRange` | 20 | how far a tap flies |
| `kunai.charge` | 0.6 | hold time before the teleport throw |
| `kunai.cooldown.<metal>` | section 4 | seconds between teleports |
| `kunai.stamina.<metal>` / `kunai.mana.<metal>` | section 4 | cost (Mana shown as half the Stamina) |
| `ret.window.<metal>` | section 4 | seconds the return works |
| `ret.radius.<metal>` / `ret.force` | section 4 / 1.0 | knockback blocks / push strength |
| `ret.damage` | 0 | % of a kunai hit the return knockback deals |
| `kunai.flightTtl` | 1.5 | seconds the thrown picture lives |
| `kunai.floorCheck` | 0 | no void protection (Skyy 2026-10-07): the setting stays at 0 (was 12); drop the row if nothing else needs it |
| `kunai.behindMob` | off | allow landing behind a mob |
| `kunai.noArena` | on | no teleporting across locked arena doors |
| `kunai.noCombat` / `kunai.noCombatBoss` | off / off | block the teleport while in combat / during a boss fight |
| `kunai.pvp` | world rule | land next to non-party players only where PvP is on |
| `kunai.maxPerMinute` | 12 | spam net |
| `kunai.recipe.<metal>` | the Daggers' | like the wand recipe rows |

## For the local session (UNVERIFIED)

1. **Band lookup:** `GearData` BANDS reads id words left to right, longest entry first, and `Kunai` has its own band (20-27, `BASE_NOFAM` Gear:1897-1898). Check `Weapon_Kunai_Copper` resolves to Copper 10-18; if not, change the lookup to prefer the metal word (or name the family word otherwise).
2. **Projectile hit position:** can a mod read the exact hit point and block face of a projectile (and a miss at max range) in a hook (`ProjectileHit` / the launch tracker `GearShotTrack`)? Fallback: a server raycast from the eye (the blink's `getTargetBlock`) with no visible projectile, only a particle trail.
3. **Teleport safety:** the blink's `TravMath` scan (`/home/user/SkyyWynnBlock/research/Magic-Traversal-Spec.md` 2.2) reuse; passability of non-solid materials; world height limits; moving a player in one tick without the client rubber-banding.
4. **Main-hand kunai:** the vanilla Kunai is thrown from the off-hand (Utility, VERIFIED). Can it be a main-hand `Weapon` with `Primary` = throw, `Secondary`-hold = return, and is `Throwing_Knife` the right `PlayerAnimationsId`? Does the vanilla kunai's throw consume an item (stack size of the vanilla item)?
5. **Hold right-click and charge:** the engine supports tap vs charged on the primary (as for wands); a hold on the secondary button with a time window needs a probe (the Return).
6. **Islands and arenas:** which bridge says whether a position is inside another player's protected island or a locked arena (SkyyIslands, `research/cloud/Capstone-Dungeon-Spec.md`)? Needs `class:fn:ally`-style functions.
7. **Dagger and kunai numbers:** the real dagger hit chain (swings 3 / 3, stabs 5 / 7 UNVERIFIED as a cycle) and its K; whether `Weapon_Daggers_*` has every metal from Crude to Onyxium, the exact dagger recipes, and the vanilla Kunai texture path.
8. **Cancel and refund:** how to cancel a charged action when the held item changes, so the Mana and Stamina refund works.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One reusable kunai (stack of 1, nothing dropped or lost) instead of a stack of thrown kunai? | yes, one reusable kunai |
| 2 | Teleport allowed in combat? (It is the Assassin's job; a block would be a setting.) | allowed everywhere except locked arenas |
| 3 | The charged throw hits like a tap (no extra damage)? Or a bonus on the charged hit? | like a tap |
| 4 | Does the vanilla Kunai (Lv 20-27, no teleport) stay a plain loot item, or also get the teleport? | stays plain loot |
| 5 | Range stays 20 on every metal (the class tree adds more), or the metal adds +1 per tier? | stays 20 |
| 6 | Kunai DPS = 80% of the dagger's (range and teleport pay the rest)? | 80% |
| 7 | A Crude Kunai at Lv 1 (so a new Assassin can start with one), or the first one is Copper? | Crude exists |
| 8 | Can you teleport next to another player where PvP is on (a gank tool)? | yes, PvP-on only |
