# Consistency pass 1006 (edits to older cloud drafts)

Cloud draft, 2026-10-06. Paper design; nothing built. Folds today's findings back into the older drafts. Inputs read: Archer-Bolts-Holster.md, Prestige-Spec.md, Tab-Prestige-Scripts.md, Economy-Audit.md, Spellbook-Ladder.md, Weapon-Speed-Tiers.md, Bank-Tab-Calibration.md, and the ten files below. Every edit is marked "(updated 2026-10-06: ...)" in place. No numbers were invented; no commits.

## 1. Edits made

| # | File | Section | Old -> New | Reason (source) |
|---|---|---|---|---|
| 1 | Class-Tree-Paths.md | 2 Archer trunk, T6 Holster Reload | Lv 55 -> **Lv 75** | Archer-Bolts-Holster.md Q2 default (75, "near the top"); locked 2026-09-25 "late game". Points still fit (25 of 25 at Lv 75; Lv 55 needs only 15 of 18) |
| 2 | Class-Tree-Paths.md | 2 Archer trunk, T3 Extra Bolts | note added: "extra bolts" = magazine cap 6 -> 10 in four ranks (Lv 15/30/42/55), not a bigger reload | Archer-Bolts-Holster.md section 1-2 |
| 3 | Class-Tree-Paths.md | 1 (level gates row) | note: Archer T6 is Lv 75, other classes' T6 stay 55 | follows edit 1 |
| 4 | Story-Script-Zones-2-5.md | 4.3 Z5.5 Home | Choice B went straight to prestige -> now the dragon sends you to the clerk first; prestige runs from the clerk's page and needs Paid in Full. Added a dragon line | Prestige-Spec.md section 1; Tab-Prestige-Scripts.md 3.1 and Q1 (default "point to the clerk") |
| 5 | Zone-Specials-Spec.md | 2 allowed / forbidden rules | "slayer boss cost %" removed from Allowed; "coin sink cuts" added to Forbidden; allowed list gets "slayer XP %, bounty-bar fill rate %" | Economy-Audit.md C8 (cost cut = coin effect) |
| 6 | Zone-Specials-Spec.md | 3 Hunter's Notice (Zone 4) | slayer cost -20% -> **slayer XP +20%** | C8 |
| 7 | Zone-Specials-Spec.md | 3 Rex Alert (Zone 5) | slayer cost -20% -> **bounty bar fills 25% faster** (kill counts x1.25), elite x1.3 kept | C8; bounty bar in Slayers-Spec.md |
| 8 | Zone-Specials-Spec.md | Clerk Lindqvist, Audit Week | slayer cost -15% -> **slayer XP +15%** | C8 |
| 9 | Zone-Specials-Spec.md | technical table, "Other effects" | key kinds: "slayer cost" -> "slayer XP, bounty-bar rate" | C8 |
| 10 | SkyyArmory-Roadmap.md | per-class table, Mage row | note: spellbooks are a Mage weapon but SkyyClasses gates `Weapon_Spellbook_` as Priest today; gate must move | Spellbook-Ladder.md section 7 |
| 11 | SkyyArmory-Roadmap.md | per-class table, Archer row | holster is a tree node at Lv 75, not an accessory; "extra bolts" = magazine 6 -> 10 | Archer-Bolts-Holster.md |
| 12 | SkyyArmory-Roadmap.md | weapon pace line (section 3) | checked: already points to Weapon-Speed-Tiers.md; stamp added | Weapon-Speed-Tiers.md |
| 13 | SkyyArmory-Roadmap.md | Server Setup rows | `armory.pace.slow/normal/fast` (3 tiers) -> replaced by `speed.*` rows, four tiers (mechanical fix of a stale row name) | Weapon-Speed-Tiers.md section 8 |
| 14 | Tab-Economy.md | top of section 2 | pointer note: read Bank-Tab-Calibration.md first (Void Marks, `tab.perHour` 90,000 = 25% of income not 40-50%, interest per 24 online hours, bank once a day with falling brackets) | Bank-Tab-Calibration.md sections 1-2; audit C1, C2 |
| 15 | Pocket-Shards-Spec.md | Auto-Sell inflation guard + Server Setup rows | own cap `shards.autosell.dailyCoins` 50,000 -> **no own cap**; pays 50% and counts toward the one shared `shops.dailySellCap` (20,000 in Zone 1, x1.5 per zone) | Economy-Audit.md C9 and F9 (audit recommendation; NPC-Shops already said "same cap") |
| 16 | NPC-Shops-Spec.md | 3 Limits, auto-sell row | now says "the same single daily cap, no separate auto-sell cap" | C9 |
| 17 | NPC-Shops-Spec.md | 3 Limits, sell-back cap row | "the Bazaar/AH only move them" -> the AH only moves coins; the Bazaar's instant sell also creates coins (market maker), not capped here | Economy-Audit.md C11, F3 |

No edits were needed in Class-Ability-Spec-Draft.md, Prestige-Spec.md, Elites-Events-Spec.md (grepped for holster, bolts, spellbook, slayer cost, sell-back caps: nothing stale).

## 2. Contradictions noticed, not fixed

| # | Where | What | Why not fixed |
|---|---|---|---|
| 1 | NPC-Shops-Spec.md section 4 price table | uses 0.1.2 Bazaar prices (Iron Ore 8); the audit says 0.1.4 prices differ | needs the live catalogue (local session); ratio checks still hold (C11) |
| 2 | Tab-Economy.md sections 2-5, 7, 8, 10 | many numbers (40-50% calibration, raw 20M coins, interest per in-game day) still read as live design under the new pointer | not mechanical; a rewrite once Skyy answers Bank-Tab-Calibration Q1-Q3 |
| 3 | SkyyArmory-Roadmap.md Mage row / section 6 pool column | still uses 5 Mana per level in places (line 105 already carries a correction note) | table must be re-run from SkyyArmory-Spec 15.4, not a wording fix |
| 4 | Class-Tree-Paths.md T3 / Archer-Bolts-Holster.md | the tree has T3 as one node (2 pts) but the magazine has four ranks | the holster file already says "ranks 2-4 would be 3 more upgrade pips"; Skyy's call (Holster Q1) |
| 5 | Prestige-Spec.md / Tab-Prestige-Scripts.md | Prestige 1 needs Paid in Full (about 2 months for a regular player), so the "Go home" choice in Z5.5 leads to a long detour | design consequence, told to Skyy in Tab-Prestige-Scripts Q1 |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Whether SkyyClasses' Priest handling of `Weapon_Spellbook_` can be moved to Mage without breaking saved Priest profiles (Spellbook-Ladder.md section 7) |
| 2 | Whether the bounty bar can count a kill as x1.25 (Rex Alert) in the SkyyQuests tracker, or the effect should be "bar needs 20% fewer kills" |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Zone specials may not touch coins (slayer cost cut removed). OK, or keep one coin special on purpose (audit C8 option 2)? | OK, no coin specials |
| 2 | One shared daily sell cap for NPC sell-back and Pocket Shard auto-sell? | Yes |
