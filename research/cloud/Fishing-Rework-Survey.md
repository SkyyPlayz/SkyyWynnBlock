# Fishing rework survey (SkyyFishing)

Cloud survey, 2026-10-23. Paper only: no game files, no build. Web was reachable (CurseForge search + two page fetches); everything not fetched is UNVERIFIED.
Inputs read: `PROJECT-RULES.md` (section 2 "Check for an existing mod BEFORE building one", "No duplicates"), `CLOUD-RESUME.md` (How this file works), `RESUME.md`,
`research/cloud/SkyyFishing-Spec-Draft.md`, `research/cloud/Fish-Species-Catalog.md`, `research/cloud/Fishing-UI-Mockup.md`, `HANDOFF.md` (SkyyFishing 0.1.12),
`PACK.md`, `docs/log/2026-10.md` (fishing lines), `docs/answered/*.md` (grep fish).

## Decisions followed (not re-decided)

- `docs/answered/project.md` + `docs/answered/skills.md` LOCKED 2026-10-06: fishing is our own system; Angler's Almanac + HyFishing = ideas only (no licence in either jar).
- `docs/answered/project.md` 2026-10-10: HyFishing OFF (PACK_DISABLED, "why do we have anglers bench and my fishing bench?"). It stays OFF even though a 0.7.2 build exists (`PACK.md`).
- `docs/answered/skills.md` LOCKED 2026-10-06: our click-bar minigame (clicks raise the bar, fish pulls it down), "!" bite sign, length + weight, bench with Parts / Rig tabs, all 4 hooks / lines / sinkers x tiers I-IV kept.
- `docs/answered/skills.md` 2026-10-06: junk drops use existing vanilla items (sticks, fibre).
- `docs/answered/skills.md` 2026-10-12: pole is a lifelong tool that levels with the Fishing skill; reel / hooks / line / sinkers are crafted parts; Fishing has its own skill, tree and rebirth branch. 2026-10-15: pole spawns with you and works without tackle; quests teach tackle later; no Wooden Reel (rod has one built in).
- `docs/answered/skills.md` 2026-10-16: line visible over water; fish go to the Fishing bag; bench reads Void fish; Bazaar Fishing tab lists the fish we actually catch (`docs/answered/economy.md`).
- `docs/answered/gear.md` 2026-10-12 / 10-15 / 10-18: Fishing armor levels with the skill; Fortune uncapped (100 percent = guaranteed double); 20 levels per zone; "fishing later" for the tier bands.
- `docs/answered/mobs.md` R5: oceans skipped. `docs/answered/economy.md` R3: no shop sells rods or parts.
- `docs/answered/project.md` 2026-10-07: rod + reel look via a reel stat; rod icons = 3D renders. Rule 2: no duplicates between mods, keep the best.

## 1. What is live (SkyyFishing 0.1.12, `HANDOFF.md` section 1)

Fishing Bench (Parts / Rig / Fillet and Sell), 8 rod ids (T0-T2 live: Wooden / Copper / Iron), reel look stat, hooks / lines / sinkers I-II, cast + bobber + line + bite + HUD fight, Zone 1 species (grade = rarity), sell at the bench, fillets, vanilla junk, Lost Property (coins + items), Pond Fish collection, Void-fish support (0.1.10), pole perks Fortune / Wisdom / Steady Line (Gear 0.3.6), gathering armor sets (Fishing art is a placeholder), Accessory Power fishing readers, Bazaar Fishing tab, Fishing skill XP (Skills), Fishing tree nodes (Trees; row 3 dead links removed in 0.4.8). HyFishing OFF.

## 2. Candidates (Hytale fishing mods)

| Mod | Author | Adds | Licence | Overlap with ours | Verdict |
|---|---|---|---|---|---|
| HyFishing 0.7.2 (`curseforge.com/hytale/mods/hyfishing`) | TheRedlotus | biome-aware catches, bite and reel, random size + length, records, leaderboards, Angler's Bench, Fish Bag, 3 meals | none in jar / page snippet; UNVERIFIED | rod, bench, length / weight, bag, records: all ours | **learn** (already done; stays OFF) |
| Angler's Almanac | (author UNVERIFIED) | biome catches, rarity-scaled tension-bar minigame, fish book, JSON config; DisplayDebug line technique | none in jar; UNVERIFIED | rod, book, minigame, line | **learn** (line + book already used) |
| Cozy Tales - Fishing 1.5.0 (`curseforge.com/hytale/mods/cozy-tales-fishing`) | Hexvane | visible fish shadows to cast at (ponds, rivers, oceans, lava), 5+ rod tiers wooden to adamantite, bobbers, Fishing Bench, Fish Processor, aquariums, boat, Fish Finder, Fishing Journal, trash + treasure (sunken chests, bottle messages); Hytale 0.5-0.7; optional Aetherhaven | **All Rights Reserved** (fetched) | bench, rods, journal, treasure all duplicate ours; shadow-fishing is a different loop | **learn only** (cannot pack alongside ours: duplicate bench / rods; cannot fold) |
| Tiny Fishing 1.0 (`curseforge.com/hytale/mods/tiny-fishing`) | skyru97 | cast and reel loop, biome-exclusive fish, hidden Codex with gaps to fill, rare prize loot, pocket-crafted rod; early access Apr 2026 | **Apache-2.0** (fetched) | Codex ~ our Angler's Ledger + collections; loop ~ ours | **learn** (Apache-2.0 allows reuse with notice, but it is not on Skyy's MIT / PD / CC BY foldable list; ask) |

Not surveyed: other CurseForge fishing add-ons (search showed only these). Nothing here is a clean fit to pack: all four ship their own rod, bench and fish, which duplicates SkyyFishing (rule "No duplicates": keep the best one, ours is locked).

What to learn (ideas only, name in the spec): Cozy Tales' visible fish shadows + Fish Finder (a "see what is in this water" step before casting); Tiny Fishing's Codex with hidden gaps (fits our Angler's Ledger); Cozy Tales' aquarium and processor (fits Fish Cooler / fillets).

## 3. Design vs live: what the rework should cover

| Item (source) | State | Rework? |
|---|---|---|
| Stage 1 (spec section 12) bench, T0-T2, Z1, minigame | LIVE 0.1.12 | no |
| Stage 2: Z2-Z3 species (`research/cloud/Fish-Species-Catalog.md` 39 species), T3-T6 rods, part tier III | not built | **yes** |
| Angler's Ledger book + records | not built | yes |
| Fishing armor art (placeholder), accessories I-II | gear exists, art placeholder | yes |
| Dynamic Seasons link (season list per species) | not built; pack mod DynamicSeasons 7.0.4 live | yes, UNVERIFIED API |
| Recipes tab with SkyyCooking, fish foods | not built | yes |
| Stage 3: sea creatures, Z4 lava fishing, T7, part tier IV, trophy tiers, leaderboard | not built | later |
| Stage 4: Z5, tiers 8-12, Festival, skill tree | tree nodes live (Trees); rest not built | later |
| Fish catalog: grade = species rarity (6 names, one roll less) | proposal, live uses 5 grades | decide (Q2) |
| UI: HUD widget for the fight + bench page (`research/cloud/Fishing-UI-Mockup.md`, v2 section) | partly live | check vs `research/Menu-Pattern.md` |
| 20-level zone bands for fishing tiers (`docs/answered/gear.md` 10-18 "fishing later") | not done | yes (with stage 2) |
| Open Fishing perks: tier tags in `tools/tier_tags.py` for every new fish / rod | rule | yes |

Spec stage-2 line "HyFishing removal" is already done (10-10), so drop it from the list.

## Questions for Skyy

1. Rework scope: build stage 2 as one full round (Z2-Z3 species + T3-T6 + part III + Ledger + seasons + Cooking tab), or split Ledger / seasons off? Default: **one full round, then Ledger as its own lean round**.
2. Fish rarity: use the species' own rarity as the grade (one roll less, catalog proposal)? Default: **yes**.
3. Learn Cozy Tales' visible fish shadows + Fish Finder as an optional Server Setup mode? Default: **no, keep the "!" bite loop (locked); revisit at stage 4**.
4. Tiny Fishing is Apache-2.0: allow folding Apache-2.0 code (with notice) alongside MIT / PD / CC BY, or learn only? Default: **learn only** (nothing there we lack).
5. Fishing armor art: redraw now (placeholder) or with stage 2? Default: **with stage 2**.
6. Trophy / lava fish and sea creatures stay stage 3? Default: **yes**.

## For the local session (UNVERIFIED)

- Licence of HyFishing 0.7.2 and Angler's Almanac (author, licence): no page text fetched; jars had none (log 2026-10-06). Re-check on the CurseForge pages.
- Tiny Fishing / Cozy Tales relations tabs (dependencies) not read; Cozy Tales source repo licence (GitHub) not checked; page says All Rights Reserved.
- Cozy Tales and Tiny Fishing jars not inspected (manifest, asset ids); if learning from them, read from Skyy's Mods folder (read only).
- Dynamic Seasons 7.0.4 fishing-season API vs our species season lists (needs the jar).
- Whether the live 0.1.12 already has Z2-Z3 species or T3 rods (HANDOFF says T0-T2, Z1 only); confirm from the jar's items.
- Fish catalog numbers (price per kg, rarity mult) vs the current balance model (`tools/balance_model.py`): not re-checked here.
