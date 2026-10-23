# Powders - spec draft (Wynn-style element powders slotted into weapons and armor)

Cloud draft, 2026-10-23. Paper only, nothing built. Skyy asked for this spec ("Powders next spec", `docs/answered/gear.md` 2026-10-18 Q10).
It sits on the LIVE element system (elem1: SkyyGear 0.3.39+, SkyyMobs 0.1.17, SkyyClasses 0.1.46, SkyyPets 0.4.10, SkyyAccessories 0.5.32).
Numbers are relative bands, not final values: the balance model (`tools/balance_model.py`, `research/balance/targets.md`) must set them.
Code facts were read from specs, not from the live scripts: re-verify at build (see "For the local session").

## Decisions followed

| Source | Line | What it fixes |
|---|---|---|
| `docs/answered/gear.md` | 284 (2026-10-18 Q10) | "Powders (Wynncraft-style gem slots you put element powders into, to add element damage / defence to gear): write their spec right after the element system ships?" -> "Yes, next spec" |
| `docs/answered/gear.md` | 277-283 (Q3-Q4, Q2) | pets add element only if the weapon already deals it; element Defence is live now; charms "start weak but get powerful" (T1-T5) |
| `docs/answered/gear.md` | 166 (2026-10-11 GEMS) | slot idea: most gear 1 slot, Legendary / UT / specials 2-3; slots can be added and removed; flat bonuses, no levels or rarities on the socketed thing (`research/Gems-Ideas.md`) |
| `docs/answered/gear.md` | 123-124, 137 | rarity names, UT = orange, Mythic = boss-only; UTs are trade-offs (so a UT's slot count may be its trade-off) |
| `SkyyGear-Plan.md` lock 17 + 303 (read only) | 60-67, 303 | flat element = weapon only, single-element Defence = armor only, Powders (Wynn's five) locked, slots / tiers / drops open |
| `research/Wynn-Elements-Build-Spec.md` | D11, 3.1-3.4 | "3.1 leaves the per-element split ready for powder lines": `raw_e = W_e + C_e + (W_e>0 ? P_e : 0) + I_e`; Defence `S/(S+D_e)`, S = 100 |
| `PROJECT-RULES.md` section 4 | - | four power sources, tier tags, sort by tier, Server Setup for everything, one-time migrations, no dev gates (default ON), Menu Pattern |
| `docs/answered/skills.md` / `research/Smithing-Smelting-Spec.md` 75 | - | Smithing XP also comes from "reforging and adding powders" through `skill:fn:addxp` (`research/Alchemy-Skill-Spec.md` 7.1, 7.4) |
| `research/Skill-Trees-Spec.md` 26, 99 | - | the word "Powder" is reserved for these gear powders (tree currency is "Dust") |

## 1. What a powder is (one paragraph)

A powder is a plain stackable item of ONE element and ONE tier. It is pressed into a free socket on a weapon or an armor piece at the
Smithing Anvil. On a weapon it adds a flat line of that element (same as a rolled `fFire`); on armor it adds a flat Defence line of that
element (same as a rolled `dFire`). It is NOT a new damage system: it feeds the existing `W_e` and `D_e` sums, so statuses, mob Weak /
Resist, popups per element, pets and charms all keep working untouched. Powders never apply a status (statuses stay ability-only).

## 2. Tiers

Wynncraft has I-VI per element. Ours follow the zone ladder (5 zones) and the charm ladder (T1-T5, already Skyy-approved "start weak
but get powerful"), so a powder tier = the zone it drops in.

| Tier | Name | Drops / is made in | Weapon band (flat, relative) | Armor band (flat Defence, relative) |
|---|---|---|---|---|
| I | `<Element> Powder I` | Zone 1 (Lv 1-20) | 1.0x (base) | 1.0x |
| II | ... II | Zone 2 (Lv 21-40) | ~1.8x | ~1.8x |
| III | ... III | Zone 3 (Lv 41-60) | ~3x | ~3x |
| IV | ... IV | Zone 4 (Lv 61-80) | ~4.5x | ~4.5x |
| V | ... V | Zone 5 (Lv 81-100) | ~6.5x | ~6.5x |

- 5 elements x 5 tiers = 25 items. Ids `Skyy_Powder_<Element>_<n>` (Earth, Thunder, Water, Fire, Air - the live spelling).
- A VI is left out on purpose (Zone 6 / Onyxium is parked). Adding VI later = one more row in the table, no redesign.
- The base unit for "1.0x" is set by the balance model so that a full set of top-tier powders is about the size of the existing
  Imbue part or less (section 6), not more. Flag: the model must set the I value per slot kind (weapon vs each armor slot).
- Tier jump rule inside one fight: a powder is useful at its zone and still decent one zone later; it never competes with a rolled line
  (rolled `fX` max 6 at Lv 40+, `dX` max 10 - `research/Wynn-Elements-Build-Spec.md` 1, 3.4) at the same level.

## 3. Sources (tie to the live economy)

| Source | How | Notes |
|---|---|---|
| Mob drops | Mobs whose `elem.mobs` row names an element drop that element's powder, tier = the mob's zone (`tools/tier_tags.py` `zone_of_level`). Low chance, elites / minibosses better, bosses guarantee 1-2 of a high tier | rows `powder.drop.*`; drop table lives in SkyyMobs (it already owns `elem.mobs` and the Combat drops) |
| Crafting (main route) | Alchemy bench (SkyySacks `/craft`, Alchemy tab): 1 element Essence + 1 Dust-free base (bone / crystal shard) -> 4 Powder I. Tier-up: 4 of tier n + coins -> 1 of tier n+1 | essences already exist: Fire, Ice (= Water), Lightning, Void; Air (Wind / Zephyr) and Earth (green crystal) are UNVERIFIED item ids, see below. Pays Smithing XP via `skill:fn:addxp` ("powder:fire") per `research/Alchemy-Skill-Spec.md` 7.4 |
| Shop | The Traveling Merchant sells tier I only, one element per visit, at a price that is a bit above the Bazaar so crafting stays the better route | the rarer elements rotate, like pet eggs; row `powder.shop.*` |
| Bazaar | Powders are Combat-bag items and tradable: Bazaar tab entry per powder, progression prices x2 per tier (live Bazaar rule, HANDOFF section 1). AH works too (plain item, no metadata) | `Ingredient_*_Essence` already go to Combat in Collections |
| Loot | Chests and mystery bags: rare powder of the chest's zone | one extra roll in the existing loot tables |
| Collections | Craft / first-drop of each powder family can count toward a Combat collection ("Powders") with small rewards | optional; reuse the Collections line format; ask Skyy |

Material mapping (essence -> element): Fire -> `Ingredient_Fire_Essence` (live), Water -> `Ingredient_Ice_Essence` (live), Thunder ->
Lightning essence, Air -> Wind / Zephyr essence, Earth -> Earth Crystal shard. The last three are UNVERIFIED as items in Assets.zip (see
`research/cloud/Element-System-Spec.md` section 2).

## 4. Slots per rarity

Live rarity ladder (`docs/answered/gear.md` 124 + `research/Wynn-Elements-Spec.md`): Normal, Unique, Rare, Legendary, Fabled, Mythic
(boss only); Untiered (UT, orange) sits beside it. Proposal (one socket pool per item; Gems later share it, see Q1):

| Rarity | Weapon sockets | Each armor piece | Total on a 4-piece set |
|---|---|---|---|
| Normal | 1 | 0 | 0 |
| Unique | 1 | 1 | 4 |
| Rare | 2 | 1 | 4 |
| Legendary | 2 | 2 | 8 |
| Fabled | 3 | 2 | 8 |
| Mythic | 3 | 3 | 12 |
| UT | 2 (UT rows may override: the slot count is part of the trade-off) | 1-3 per UT line | per `research/UT-Lines-Draft.md` |

- Matches Skyy's gem line: "most gear 1 slot, legendarys, UTs and specials 2-3".
- Saved on the item as the fields the Gear stage-1 spec already reserved: `pw` (powder list) and `pwMax` (socket count) -
  `research/SkyyGear-Stage1-Spec.md` 121, 158. Check they are still unused in 0.3.4x (UNVERIFIED).
- `pwMax` is set when the item is identified / crafted. Items that already exist get `pwMax` lazily the first time they are opened in
  the Anvil (computed from rarity); no mass rewrite of saved data (the one-time-migration rule).
- Extra socket: Anvil button "Add socket", coins rising with rarity, max `powder.slotsCap` above the rarity count (default +1); needs
  Smithing level. Removing a socket is not offered (a socket can hold its powder forever).
- A rarity upgrade (Sigil) raises `pwMax` to the new rarity's count and keeps filled powders. A level-up or reforge keeps `pw` as it is.

## 5. Four power sources - who takes powders

| Source | Powders? | Why |
|---|---|---|
| Weapon / tool | YES, weapon sockets (flat element damage) | lock 17: flat element is weapon-only |
| Armor (gear) | YES, armor sockets (flat element Defence) | lock 17: single-element Defence is armor-only |
| Accessories (Void Charms) | NO sockets | they already have their own element ladder (single-element charms T1-T5 + Elemental Power, Q2) and a power list; a socket system on top would be a third socket kind, and `gear:extra` is the one pipe for them (`research/Accessory-Pack-Inventory.md` G4) |
| Pets | NO sockets | pets already give element Defence and a weapon-gated element line (Q3); the dragon pet's element follows its type |

So the "four power sources" rule is met by each source having its own element line, not by every source taking powders. Powders are the
GEAR part of the stack; charms and pets are the other two parts. Balance rule for the model: no one source above ~40% of a build's
element damage (`research/Wynn-Elements-Spec.md` section 2).

## 6. Stacking with Imbue and the live element Defence (no double dipping)

Live formula (`research/Wynn-Elements-Build-Spec.md` 3.1-3.2), N = the neutral hit after today's chain:

```
raw_e   = W_e + C_e + (W_e > 0 ? P_e : 0) + I_e
W_e     = rolled weapon lines of e + WEAPON POWDERS of e        <- powders join here, nothing else changes
I_e     = round(N x imbuePct / 100), one chosen element, Spellblade hits only      (stays a % of N, never touched by powders)
mob:     dealt_e = round(raw_e x (1 + mod_e/100))     mod_e in {+25, -25, -50, 0}
player:  dealt_e = round(raw_e x S / (S + D_e))       D_e = armor dX + ARMOR POWDERS of e + pets dX + charms dX
```

Rules (so nothing counts twice):
1. **Powders are flat and join `W_e` / `D_e` once.** They are not multiplied by Imbue, and Imbue is not multiplied by powders.
2. **Imbue stays a % of N; powders stay flat.** At low levels powders matter relatively more, at high levels Imbue grows with N - the same
   shape as rolled lines today. No conversion-style powders (Wynn "convert damage" is NOT copied).
3. **Powder lines count as rolled gear lines** for the pet gate: a Fire powder on a weapon makes `W_Fire > 0`, so the pet's Fire line
   works. This is intended synergy (a cheap way to open a pet's element) - the model must price it (Q4).
4. **Any element can be slotted into any socket**; a powder never needs a matching rolled line (Wynn also lets any element in).
5. **One cap for the flat sum.** Total flat element (`W_e` incl. powders + `C_e` + `P_e`) per element is capped by `powder.capPct` of N
   equivalent (placeholder 40%) so 3 weapon sockets x 3 pets x charms cannot snowball. Defence needs no cap: `S/(S+D)` already has
   diminishing returns and a hard ceiling of 100% cut.
6. **Opposing elements are independent.** Wynn lowers the opposite element's Defence when you add one; we do NOT (no hidden minus). The
   wheel (`Earth>Thunder>Water>Fire>Air`) only affects mobs' Weak / Resist.
7. **Statuses stay with abilities.** A powder never applies Burn / Chill / etc. Poison is a separate line (`poison`), not a powder.

Example (N = 100, S = 100, relative; same weapon as the live worked example in the Build Spec 3.2):

| Case | W_Fire | C | P | I | raw_Fire | vs neutral mob | Weak (+25%) |
|---|---|---|---|---|---|---|---|
| Live today (5 Fire rolled, +4 charm, +10 pet, Imbue 30) | 5 | 4 | 10 | 30 | 49 | 49 | 61 |
| + two Fire Powder III (band 4 each) | 5 + 8 = 13 | 4 | 10 | 30 | 57 | 57 | 71 |
| Same, weapon had NO Fire line before | 8 | 4 | 10 (gate now open) | 30 | 52 | 52 | 65 |

Read: two top-of-zone powders add about +16% of the element part of this build, about +8% of the whole hit's element share - never more
than the Imbue 30 itself. Armor: with S = 100, a chest D_Fire of 20 cuts 17% of a Fire hit; 4 pieces x 1 Powder III (band 4) = +16 D adds
roughly another 9% cut at that level (curve flattens). FLAG for the model: set the Powder I base value per slot, check `powder.capPct`,
and re-run the "unluckiest 1 in 10 players" gear-upgrade clock (`docs/answered/gear.md` 313) since powders are a new upgrade route.

## 7. Tier tags (`tools/tier_tags.py`)

- Powders have their own ladder, so they use `ladder_tag(n, "Powder")` -> `"T3 Powder - <text>"`, the same way Totem / Loot / Bench /
  Talisman / Charm do. That means adding `"Powder"` to `OWN_LADDERS` (bumps nothing else; NOT a renumbering, so `TT_VERSION` stays 3 -
  confirm, since old pins assert the version).
- Flavor text first phrase = the tag, e.g. `T3 Powder - Fire Powder III. Add to a weapon: +4 Fire damage. Add to armor: +4 Fire Defence.`
  (colour-coded per Style Guide section 15: the element name in its colour, values in the stat colour).
- A round that adds a tiered item adds it to that table; `tools/ci/langdup.py` keeps one writer per lang key: SkyyGear owns the powder
  lang keys (it owns the slotting UI), SkyyMobs owns only the drop rows. Slotted powders show on the item tooltip as coloured pips
  `[Fire III] [Fire III] [ ]`; the tier tag of the ITEM does not change.
- Sort by tier: every list of powders (Anvil picker, Bazaar tab, shop) sorts by tier then element in Wynn order, per the sort-by-tier
  rule.

## 8. Server Setup rows (`tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`; times in seconds)

| Mod | Key | Name | Default / range |
|---|---|---|---|
| SkyyGear | `powder.on` | Powders on | true |
| SkyyGear | `powder.slots.weapon` | Weapon sockets by rarity | table, section 4 values |
| SkyyGear | `powder.slots.armor` | Armor sockets by rarity | table, section 4 values |
| SkyyGear | `powder.slotsCap` | Extra sockets a player may add | 1 (0-3) |
| SkyyGear | `powder.slotCost` | Add-socket cost by rarity (coins) | balance model |
| SkyyGear | `powder.value.weapon` / `powder.value.armor` | Tier I value; tiers scale by the section 2 ratios | balance model |
| SkyyGear | `powder.ratio` | Tier ratios II-V | 1.8 / 3 / 4.5 / 6.5 |
| SkyyGear | `powder.capPct` | Cap on the flat element sum (% of N) | 40 (10-100) |
| SkyyGear | `powder.removeRefund` | % of a removed powder returned | 0 (0-100) |
| SkyyMobs | `powder.drop.chance` / `powder.drop.elite` / `powder.drop.boss` | Drop chances | balance model |
| SkyyMobs | `powder.drop.byZone` | Tier drop by zone | zone n -> tier n |
| SkyySacks | `powder.recipe.*` | Craft / tier-up counts and coins (Alchemy tab) | 4 : 1, coins by tier |
| SkyyMerchants | `powder.shop.price` | Tier I price | above the Bazaar |
| SkyyBazaar | (existing price rules) | x2 per tier | no new row |

All are editable in game (SkyyMenu -> Server Setup). The kit's multi-column text table is UNVERIFIED (Build Spec limits), so the slot
tables are best as one row per rarity, or 1-column `|` tables.

## 9. Anti-dupe / anti-loss

| Risk | Rule |
|---|---|
| Powder spent but not added (crash, full inventory) | one operation: remove the powder from the inventory AND write `pw` to the item in the same server tick; verify the count after the remove; abort and give the powder back if the item changed |
| Item changes while the page is open (moved, sold, reforged) | the page re-reads the held item at click time (the Anvil rule for Reforge); refuses if its id / uuid tag differs |
| Stacked gear (stacks of spears, books) | stacks stay whole until the action; slotting splits ONE item off (same as Identify / Reforge, `docs/answered/gear.md` 49); never into the hotbar |
| Powder duplicated by metadata | the powder is a plain stackable item with no metadata; only the slotted item carries data; one writer (SkyyGear) |
| Powders lost when an item is destroyed / sold | Salvage, NPC sale and AH list show a confirm "this item has 2 powders" ; AH / trade carry `pw` intact |
| Remove loses the powder | default: removing destroys it (Wynn rule, a coin sink); `powder.removeRefund` can return a share. Replace asks for a confirm |
| Reforge / Sigil / level-up | keep `pw` (never re-rolled); rarity change only raises `pwMax` |
| Loadouts (Requip), Vault, Wardrobe | item data travels with the item - verify `pw` survives each (UNVERIFIED) |
| Migration | none needed (lazy `pwMax`); a rollback to an older Gear ignores unknown fields (Stage-1 rule: unknown fields are kept) |
| Server restart mid-craft | Alchemy craft outputs are one atomic craft event, as today |

## 10. UI (follows `research/Menu-Pattern.md`)

- No new menu and no new command (rule: "replace commands, never add extra"). Slotting lives in the **Crafting hub > Anvil tab**, as
  its own sub-tab beside Reforge and Identify (M3 of Menu Pattern: Anvil has sub-tabs). `/smithing` and `/reforge` already open that hub.
- Page: 1600 x 980, BIG header + row 2, held item on the left (name, rarity, level, tooltip with the socket pips), the socket row
  (filled sockets coloured by element), the right side a scroll list of the powders in your Magic Bags (sorted by tier, then element;
  not PREV / NEXT), buttons Add, Remove (confirm), Add socket (cost shown). One packet per click (HANDOFF section 2 UI rule).
- Powder crafting / tier-up is a tab inside the existing `/craft` Alchemy list (no new page); the Bazaar gets a tab entry; Server Setup
  rows as in section 8.
- Element colours and the pip tooltip follow the Tooltip colour code (Style Guide section 15). Hits keep the per-element coloured popup.

## 11. No-duplicates check against pack mods

`PACK.md` was grepped for powder / element / rune / socket / gem: the only related pack mod is **Dragon Nestkeeper** (BlackAures), which
brings dragon eggs and stages, no element powders or sockets. No pack mod adds a powder or socket system, so there is nothing to
fold or switch off. The CurseForge survey the project rule asks for (Hytale gem / enchant / socket mods) is NOT done here (no network
survey in this draft): the local session should run it before building (`PROJECT-RULES.md` section 2). Internal duplicates: do not
confuse with Runes (the vanilla ability runes / our class runes, `docs/answered/classes.md` 192), Sigils (rarity upgrades), Gems (later
flat tool gems, `research/Gems-Ideas.md`) or Dust (tree currency).

## 12. BUILD SPLIT (rounds)

| Round | Mods | Size | Content |
|---|---|---|---|
| P0 | none | no agents | CurseForge survey, 4 probes (section 13), balance model rows set the Powder I value and `capPct` |
| P1 | SkyyGear (+ SkyyMobs `elem` read only) | **Full round** (new saved item fields, item loss risk, damage math) | item fields `pw` / `pwMax`, `W_e` / `D_e` sums include powders, tooltip pips, rows, harness identity (no powders = 0.3.40 exactly) |
| P2 | SkyyGear + SkyyMenu | Lean round | Anvil Powders sub-tab (slot, remove, add socket), confirms, Smithing XP via bridge |
| P3 | SkyySacks (+ SkyyCollections items, `tools/tier_tags.py`) | Lean | the 25 items + lang keys, Alchemy recipes, tier-up, Bazaar tab |
| P4 | SkyyMobs + SkyyMerchants + loot tables | Lean | drops by element / zone, shop rotation, chests |
| P5 | docs | no agents | player chart in the Wynn element charts, TEST-CHECKLIST entry |

P1 + P2 deploy together (a socket with no page is useless), P3 first for playtest if Skyy wants powders in hand early. Launch with the
saved workflow `skywynn-round`; put Skyy's own words (section "Decisions followed") in `args.quotes`.

## 13. Probes / checks (before P1)

1. Do the `pw` / `pwMax` metadata fields still exist unused in the 0.3.4x item data, and do they survive Requip, Vault, trade, AH, mystery bag identify?
2. Does `gear:fn:elemDef` already sum from `GearHit` rolled lines only; where do armor `dX` come from for a worn piece (so powders join once)?
3. Is the pet gate computed from `totals(withExtra=false)` (rolled lines) so powders stored in item data are included?
4. Item ids for Air and Earth essences (see section 3).

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | One shared socket pool for powders AND the later Gems, or separate slots? | [shared pool: fewer tooltip slots, one Anvil sub-tab; gems fill the same sockets later] |
| 2 | Powder tiers: 5 (I-V, one per zone) or Wynn's 6? | [5; VI waits for Zone 6] |
| 3 | Removing a powder destroys it (Wynn), or returns it? | [destroys; row `powder.removeRefund` can return a share later] |
| 4 | A powder on a weapon opens the pet's element gate (pet +10 Fire needs the weapon to deal Fire). Allow that? | [yes, it is the intended synergy; priced by the model] |
| 5 | Should armor powders on an element also lower the opposing element's Defence (Wynn does)? | [no, no hidden minus] |
| 6 | Sockets by rarity as in section 4 (Mythic 3, Normal weapon 1 / armor 0)? | [yes] |
| 7 | Can a player add an extra socket (coins + Smithing level, +1 max)? | [yes, small coin sink] |
| 8 | Accessories and pets take no powder sockets (they have own element lines)? | [yes, none] |
| 9 | Powders tradable on Bazaar / AH, plus a Combat collection "Powders"? | [tradable yes; collection optional later] |
| 10 | Wynn powder SPECIALS (fill a charge by hits, fire a Fire/Water/etc. special) later as class-tree nodes? | [later, not v1] |

## For the local session

UNVERIFIED items (need the live scripts, Assets.zip or HytaleServer.jar):
- Air (Wind / Zephyr) and Earth (green crystal) essence item ids in Assets.zip; whether Lightning essence exists as an `Ingredient_*` id.
- `pw` / `pwMax` still reserved and unused in SkyyGear 0.3.4x; how item data is written (Stage-1 spec 110-121 may be out of date).
- That powders join the pet gate and `gear:fn:elemDef` exactly once (Build Spec 3.1-3.4 line numbers are from 0.3.26; elem1 is 0.3.39+).
- `OWN_LADDERS` addition and `TT_VERSION` (3): adding a word should not need a version bump; old pins assert the number.
- `research/UT-Lines-Draft.md` slot counts per UT line; whether UTs get slots from their own rows.
- The Anvil sub-tab layout in Menu Pattern M3 vs the live Gear 0.3.4x Smithing page (Menu Pattern is from 0.3.14).
- The Traveling Merchant stock mechanism (pet egg rotation) can host a rotating powder; SkyyMerchants version.
- CurseForge survey for socket / gem / enchant mods (not done in this draft).
- Balance: Powder I values, `capPct`, drop chances, socket costs, the upgrade-clock re-run - all for `tools/balance_model.py`.
