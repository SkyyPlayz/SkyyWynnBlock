# Wardrobe coin prices - the cosmetic coin sink (spec)

Cloud draft, 2026-10-23. Paper only; nothing built, no game files read. Read: `research/cloud/Economy-Sinks-Survey.md` (default pick C2 =
this file), `research/Balance-P7-Economy-Spec.md` Part 1.3 (the coin curve) + Part 6 (the "hours of income" rule), `research/cloud/Wardrobe-Spec.md`
(Looks, section 4), `research/Recolor-Plan.md`, `HANDOFF.md` (SkyyWardrobe 0.2.10), `research/balance/targets.md` section 3.

## Decisions followed (word for word in `docs/answered/`)

| Date | Skyy's words (short) | Used for |
|---|---|---|
| 2026-10-18 (`economy.md` Q19) | coin sinks "Even mix" (upgrades, Bazaar, cosmetics about equal) | this file fills the missing cosmetic third |
| 2026-10-18 (`economy.md` Q18, x10 on 10-21) | coins 100k / 5M / 100M, "never spending" | the curve below is the targets' hourly income |
| 2026-10-16 (`economy.md` line 142) | sink "Yes, after rebirth R3" | rebirth R3 is live, so the sink is allowed now |
| 2026-10-08 / 10-10 (`gear.md`) | Wardrobe: "edit the look of the entire set from in there"; loadouts | Looks = the first thing to price |
| 2026-10-15 (`gear.md`) | "id start with 10 loadouts." | the first 10 loadout slots stay FREE |
| 2026-10-16 (`gear.md`) | Requip salvage "never coins" | no cosmetic can be sold back or looped for coins |
| 2026-10-13 (`economy.md` Q14) | rebirth: "a title each rebirth, a cosmetic every 3rd" | rebirth rewards stay free; not priced here |
| `PROJECT-RULES.md` section 4 | everything editable in Server Setup; four power sources | prices are rows; cosmetics NEVER touch power |

## 1. The one rule (same as every other P7 sink)

Price = hours of income x the income of one hour at the player's level. One hour at Lv 10 = **8,333 coins** (Part 1.2), and
`coins:fn:curve(level)` scales it (1.0 at Lv 10, 36.8 at Lv 50, 466 at Lv 90). SkyyCoins already publishes `coins:fn:curve`
(Object[]{ Integer level } -> Double); a mod with no SkyyCoins uses the built-in copy of the default text (the build asserts they match).

| Level | 1 h of income | 0.06 h | 0.25 h | 0.5 h | 1 h |
|---|---|---|---|---|---|
| 10 (Zone 1) | 8,333 | 500 | 2,100 | 4,200 | 8,300 |
| 30 (Zone 2) | 43k | 2.6k | 10.8k | 21.7k | 43k |
| 50 (Zone 3) | 307k | 18.4k | 77k | 154k | 307k |
| 70 (Zone 4) | 1.083M | 65k | 271k | 542k | 1.08M |
| 90 (Zone 5) | 3.88M | 233k | 970k | 1.94M | 3.9M |

Rounded like `p7_round` (10 / 100 / 500 / 5,000 by size). Which "level": the **highest class level this profile has ever reached** (so a rebirth to
Lv 1 does not make cosmetics cheap; coins reset to 0 on rebirth anyway) - UNVERIFIED stat name; fallback = current class level with a floor of 10.

## 2. What Wardrobe sells (all coins, all optional, no power)

Today SkyyWardrobe 0.2.10 has NO coin rows (Part 6.1 grep, confirmed by the Sinks Survey). Three prices, plus a rule for everything cosmetic added later.

| # | Item | Price (default) | Rule | Built? |
|---|---|---|---|---|
| W1 | **Look change** for a stored set (Looks page, `research/cloud/Wardrobe-Spec.md` section 4) | **0.06 h per set** (500 coins at Lv 10 = the old flat default of that spec) | one payment per set, any number of pieces; price level = the set's highest piece level (SkyyGear item level) | Looks page not built yet (Wardrobe 0.3 stage); price rows ship with it |
| W2 | **Extra loadout slots** beyond the 10 free ones (11 ... 18, max 18) | **0.25 h x (n - 10)** for slot n (slot 11 = 0.25 h, slot 18 = 2 h; all 8 = 9 h) | one-time per profile, price fixed at purchase, kept through rebirth (an unlock, not coins) | slots exist (10 free); the Buy button + rows = Wardrobe 0.2.11 |
| W3 | **Loadout icon / colour tag change** (the small coloured marker on a loadout card) | **0.02 h** per change, first one free | only if the tag is built; else skip | idea; needs the card design |
| W4 | Future cosmetics (dyes, pet name colours, page themes, emblems) | by grade: Basic 0.05 h, Fine 0.15 h, Rare 0.5 h, Epic 1.5 h, Legendary 4 h | one grade per item, shown in the item's tooltip | rule only |

Never sold for coins: gear, stats, pet slots, accessory slots, Requip pool size (power / storage the Skyy design wants earned), the first 10 slots, and
rebirth titles / rebirth cosmetics (free rewards). Looks on gear never change stats (Recolor-Plan 4.1: same family = identical stats + durability).

Armory's Alteration Table (Alteration Kit) stays as the OTHER route for Armory looks; ours charges coins on our page. Duplicate rule: the player picks
one route per look; we do not hide the Armory's (a pack mod cannot be hidden piecemeal, PROJECT-RULES 2); our Looks page defaults to coins only
(`look.useKit=false`, Wardrobe-Spec Q8).

## 3. Size against income (does it fill the cosmetic third?)

Target from Part 6.3: "upgrade everything" = about 4.2 h of income a zone (35 / 30 / 30 / 26 / 21 % of Zones 1-5's coins). Q19 wants cosmetics about
equal. Honest sizing of Wardrobe alone for a player who uses it fully:

| Zone | Look changes (assume 8 changes a zone = 0.48 h) | Slots bought (spread: 1-2 a zone) | Zone total | Share of zone income (12 / 14 / 14 / 16 / 20 h) |
|---|---|---|---|---|
| 1 | 0.48 h | slots 11 + 12 = 0.25 + 0.5 = 0.75 h | 1.2 h | about 10 % |
| 2 | 0.48 h | slots 13 + 14 = 0.75 + 1.0 = 1.75 h | 2.2 h | about 16 % |
| 3 | 0.48 h | slots 15 + 16 = 1.25 + 1.5 = 2.75 h | 3.2 h | about 23 % |
| 4 | 0.48 h | slots 17 + 18 = 1.75 + 2.0 = 3.75 h | 4.2 h | about 26 % |
| 5 | 0.48 h | - | 0.5 h | about 2 % |

So Wardrobe on its own is roughly 10 - 26 % of a zone's income in Zones 1 - 4 for a completionist (the slot buyer), against the 21 - 35 % of upgrades. That is
"about equal" for a player who wants everything, and nothing for a player who ignores cosmetics. The Tab (Economy-Sinks-Survey C1, Zone 4-5) carries the
late cosmetic sink; W4's grades make later cosmetics price themselves. Do not raise W1 / W2 to chase the number - cosmetics that bite feel like a tax.

## 4. Build (SkyyWardrobe, lean round for W2, full round when Looks ship)

| Round | Version | Content | Size |
|---|---|---|---|
| Wardrobe-A | 0.2.11 (derive from the SET pin with `tools/wardrobe_0_2_11_patch.py`; edit the patch, never a generated script) | W2: slots 11 - 18, Buy button on a locked card (kit one-shot confirm: price shown = price charged, one at a time, 1.5 s refuse window), `wardrobe.slot.hours`, `wardrobe.slot.max` rows, `coins:fn:take` before unlock, exact refund on a failed save, journal line | lean + one critic (it moves coins) -> treat as FULL by the rule "coins / economy" |
| Wardrobe-B | with Looks (0.3.x) | W1: `wardrobe.look.hours`, the Looks page price line, take-then-apply, refund on failure; `look.kit` stays the alternative | full round |
| Wardrobe-C | optional | W3 + W4 grade table when a first cosmetic exists | lean |

Server Setup rows (Server Setup > Storage > Requip, `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`; all live): `wardrobe.price.curve` (bool, true; false = flat
coins), `wardrobe.slot.hours` (0.25), `wardrobe.slot.max` (18), `wardrobe.look.hours` (0.06), `wardrobe.tag.hours` (0.02), `wardrobe.free.perm` (permission
`skyywardrobe.free` + Creative skip all prices). Cost display in the page, never a hidden fee. Every payment is `coins:fn:take` (must return TRUE), the unlock is
written atomically, read back, and on any failure the exact coins are refunded (SkyyVault buy rules). No migration: no coin rows exist today; existing
profiles keep their 10 slots; nobody loses a slot.

Dupe / loss checks: a coin sink moves no item; the risk is "paid, not unlocked" and "unlocked twice, paid once" - the harness covers both (below).

### Harness (bare JVM, `-Xverify:all`, then all jars in one JVM)

| # | Check |
|---|---|
| 1 | Price(level, n): matches the table in section 1 within rounding for Lv 10 / 30 / 50 / 70 / 90 |
| 2 | Slot buy: coins taken once, slot unlocked once; double-click inside the refuse window = one charge |
| 3 | Not enough coins: refused, no change; profile busy: refused |
| 4 | Crash between take and unlock: recovery either completes the unlock or refunds (never neither) |
| 5 | Rebirth: purse reset to 0, unlocked slots kept, price level = highest ever |
| 6 | Creative / `skyywardrobe.free`: no charge; Server Setup row changes apply live |
| 7 | `python tools/balance_model.py --econ --check` still passes (add a Wardrobe row to the cosmetic-share report) |

## 5. In-game test steps (after the deploy)

1. New profile: Requip shows 10 free loadouts and a locked card for slot 11 with the price (2,100 coins at Lv 10).
2. Buy slot 11 with enough coins: coins drop by exactly the price, slot opens; try again: slot 12 costs 0.5 h.
3. Buy with too few coins: refused, no change.
4. Server Setup: change `wardrobe.slot.hours` to 1: the next card shows the new price at once.
5. Rebirth (admin): slots stay; the next slot price is not cheaper than before.
6. (Looks round) change a set's look: coins drop by the single-set price, all pieces with that look change, stats / rolls unchanged.

## Questions for Skyy (each with a default)

| # | Question | Default |
|---|---|---|
| 1 | Start the cosmetic sink as coin prices in Wardrobe (extra loadout slots first, Looks price with the Looks page)? | [yes, as in the Sinks Survey] |
| 2 | Extra loadout slots 11 - 18 for coins, 0.25 h x (n - 10)? Or keep all slots free? | [coins, max 18] |
| 3 | Look change 0.06 h per set (500 coins at Lv 10)? | [yes] |
| 4 | Price level = highest class level ever reached (rebirth does not make cosmetics cheap)? | [yes] |
| 5 | Keep the Armory's Alteration Kit as a free-of-coins second route for Armory looks? | [yes, cannot be hidden anyway] |
| 6 | Is it right that Wardrobe alone is only 10 - 26 % of a zone and the Tab / future cosmetics carry the rest? | [yes, do not inflate prices] |

## For the local session (UNVERIFIED - needs the repo's build scripts / game files)

| # | Check |
|---|---|
| 1 | SkyyWardrobe 0.2.10 really has no coin rows and where the loadout limit lives (the "10 free" and any hard cap); can the cap go to 18 without a data migration |
| 2 | `coins:fn:curve` / `coins:fn:take` exact signatures and the SkyyWardrobe -> SkyyCoins bridge status (Requip salvage uses a different bridge) |
| 3 | A "highest class level ever" stat in SkyyClasses / SkyyRebirth; else the floor-10 fallback |
| 4 | Whether the Looks page (Wardrobe-Spec section 4) was built under another name in 0.2.x or is still only a spec (`research/Recolor-Plan.md`) |
| 5 | Kit one-shot confirm helper name in `tools/skyyui.py` and the Server Setup group name for Requip rows |
| 6 | `python tools/balance_model.py --econ` has a cosmetic-share report to extend, or add one in the P7 follow-up |
