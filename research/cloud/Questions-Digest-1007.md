# Questions digest 2026-10-07 (what is still open after the 2026-10-06 digest)

Cloud draft, 2026-10-08 (covers drafts dated 2026-10-06 / 2026-10-07). Paper design; nothing built. Inputs read: the "Questions for Skyy" section of every
`research/cloud/` draft dated 2026-10-06 or 2026-10-07 that `research/cloud/Questions-Digest-1006.md` did NOT already list, plus the drafts
that changed on 2026-10-07, `research/Shadow-Step-Spec.md`, `research/Rod-Reel-Look.md`, `OPEN-QUESTIONS.md`, `docs/answered/*.md`.

**How to answer:** reply with the row numbers ("1-10 yes, 4 no"). "yes" = take the default in [brackets]. Silence = the default stays as a placeholder.
**Everything else** (the rows from the 41 older drafts) is still in `research/cloud/Questions-Digest-1006.md`; those rows are unchanged unless a row below says so.

**Dropped as already answered:** `research/cloud/Kunai-Ladder.md` Q1-8 and `research/cloud/Spellbook-Ladder.md` Q1-9 (`docs/answered/gear.md` lines 103 + 105: "defaults are fine"),
`research/cloud/Monk-Colour-Options.md` Q1 (LOCKED Saffron, `docs/answered/gear.md` line 87), `research/cloud/Pets-Spec.md` Q1-4 (`docs/answered/pets.md` R9),
`research/Rod-Reel-Look.md` (no open list; Skyy picked "8 rods with the reel stat", `docs/answered/skills.md` line 90; its UNVERIFIED limits are in-game tests, not questions).
`research/cloud/Tab-Economy.md` Q1-3 repeat `research/cloud/Bank-Tab-Calibration.md` Q2-3 (already in Digest-1006), so they are not listed again.

## A. Top 10 - these block the next builds

| # | Question (short) | Default | Source |
|---|---|---|---|
| 1 | Mana for the five physical classes: +2 Mana per class level, or Stamina costs instead? | [+2 Mana per class level] | `research/cloud/Class-Ability-Spec-Draft.md` Q1 |
| 2 | Ability level cap 15 with 14 points (two modifiers maxed), and Berserker self cap +60%: right size? | [15 / 14 points; +60%] | `research/cloud/Class-Ability-Spec-Draft.md` Q2-3 |
| 3 | Class tree size: 1 point per 3 class levels, 3 paths x 5 nodes + 6-node trunk (21 nodes), respec = coins / rare item / free on a long cooldown? | [1 per 3 levels; 21 nodes; respec costs coins] | `research/cloud/Class-Tree-Paths.md` Q1-3 |
| 4 | Shadow Step: small backstab bonus +10%; works on PvP-on players; all daggers (vanilla too) get it? | [+10%; yes; all daggers] | `research/Shadow-Step-Spec.md` section 6 Q1-3 |
| 5 | Chain premium: Block +4.5% (cumulative 1.1495, under the 15% cap), Enchanted stays +10%; round Enchanted prices DOWN. (Already applied in 4 drafts as a proposal.) | [yes, +4.5%, round down] | `research/cloud/Chain-Premium-Fix.md` Q1-3 |
| 6 | Lower Ember Ore 11,000 -> 4,300 (Mithril x3), keeping Onyxium's slot empty; keep `tab.perHour` 90,000? | [yes, 4,300; keep 90,000] | `research/cloud/Ember-Economy-Check.md` Q1, Q4 |
| 7 | Amberite 30,000 -> 9,300 and Drakonite 75,000 -> 23,000; allow a later Enchanted Drakonite Block (676,825,600 fits 1e9); keep Drake Scale 9,000? | [yes; yes, later; keep] | `research/cloud/Zone-5-Ore-Prices.md` Q1, Q4, Q5; also `research/cloud/Ember-Economy-Check.md` Q2 |
| 8 | Bazaar buy-side floor `bazaar.buyFactorFloor` 0.9 (a dumped ore is never bought below 90% of base) in the next Bazaar round? | [yes, 0.9] | `research/cloud/Bazaar-Drift-Check.md` Q1; also `research/cloud/Ember-Economy-Check.md` Q5 |
| 9 | Ore veins on the shared zone islands grow back; regrow even when a player stands nearby; Ember density 21 -> 7 ore per cell (Z4) / 3.5 (Z5)? | [yes; yes (`ore.regrowNoPlayer` 0); Ember yes, Amberite left alone] | `research/cloud/Ore-Regrow-Spec.md` Q1, Q2, Q6; also `research/cloud/WorldGen-Stage-2-Draft.md` Q1-2 |
| 10 | Fishing: a fish's rarity (Normal..Mythic) is the whole grade (one roll less); too-heavy fish never bite; Fish Cooler list storage; keep HyFishing until stage 2 passes your test? | [yes; never bites; Fish Cooler; yes] | `research/cloud/Fish-Species-Catalog.md` Q1; `research/cloud/SkyyFishing-Spec-Draft.md` Q1, Q6, Q7 |

## B. The rest, by topic

### Classes and Priest

| # | Question (short) | Default | Source |
|---|---|---|---|
| 11 | Soul Orb recipe gem count = half the Binding count? | [yes] | `research/cloud/Soul-Orb-Spec.md` Q1 |
| 12 | Mithril essence (wind / Zephyr) and Onyxium (Voidheart + Void) as proposed? | [yes] | `research/cloud/Soul-Orb-Spec.md` Q2 |
| 13 | Stored healing also works on Sacred Heal (a path node), or only on Wings of Fate? | [only Wings of Fate] | `research/cloud/Soul-Orb-Spec.md` Q3 |

### Economy and Bazaar

| # | Question (short) | Default | Source |
|---|---|---|---|
| 14 | Lower Amberite / Drakonite fit (6,700 / 11,200) so the Tab stays a 100+ hour race for Zone 5 miners? | [no; re-measure first] | `research/cloud/Zone-5-Ore-Prices.md` Q2 |
| 15 | Keep `tab.perHour` 90,000 and re-measure with a Zone 5 test profile? | [keep] | `research/cloud/Zone-5-Ore-Prices.md` Q3 |
| 16 | Or leave the chain at 15.5% and change the written rule instead of Block +4.5%? | [no] | `research/cloud/Chain-Premium-Fix.md` Q2 |
| 17 | Or accept the buy-side drift (about 1% of income per pair) and only watch it? | [no; the floor is cheap] | `research/cloud/Bazaar-Drift-Check.md` Q2 |
| 18 | Alts / profiles share one factor per product (one market)? | [yes, unchanged] | `research/cloud/Bazaar-Drift-Check.md` Q3 |
| 19 | NPC shops: sell-back 25% / buy 3.7x of base; daily buy limit 640 (torches / bread unlimited); sell Crude weapons and tools but not armor? | [yes; 640; weapons yes, armor no] | `research/cloud/NPC-Shops-Spec.md` Q1-3 |
| 20 | Paying Tab milestones unlock real convenience (+1 Pocket Shard slot) or only cosmetics / titles? | [only cosmetics / titles] | `research/cloud/Tab-Economy.md` Q5 |
| 21 | Prestige reset: skills to a floor, coins and progress flags; cosmetics / pets / titles / items kept? | [as written] | `research/cloud/Tab-Economy.md` Q4 |

### Gathering, ore and world

| # | Question (short) | Default | Source |
|---|---|---|---|
| 22 | Small ore pockets (Z3 Mithril, Z5 Drakonite): 900 s timer now, enlarge Mithril if busy? | [900 s; enlarge later] | `research/cloud/Ore-Regrow-Spec.md` Q3 |
| 23 | Regrow timers run while the server is off (wall-clock)? Ore inside claimed plots regrows? | [yes; yes] | `research/cloud/Ore-Regrow-Spec.md` Q4-5 |
| 24 | Vein fatigue (slower swing after many ore from one cell) or no caps? Private mine in profile worlds later? | [no caps; shards only] | `research/cloud/Ore-Regrow-Spec.md` Q7-8 |
| 25 | World gen: Mithril first at the Zone 3 summit; wild crop patches; Zone 2 denser groves; Zone 2 then 3, Zone 4 hidden until Lv 50+ gear? | [yes to all four] | `research/cloud/WorldGen-Stage-2-Draft.md` Q3-6 |
| 26 | Crop armor: Onion takes the old T6 numbers (10 Fortune); 24 Enchanted crops per set; Enchanted Cauliflower + Chilli added; unlock tier VI / V; 2 Enchanted of the previous crop in each recipe? | [yes to all] | `research/cloud/Crop-Armor-Spec.md` Q1-3, Q5-6 |
| 27 | Hearty Gourd (Pumpkin) and Spice (Chilli) food perks if SkyyCooking can do them cheaply? | [try, drop if costly] | `research/cloud/Crop-Armor-Spec.md` Q4 |
| 28 | Mining lamp: reach per helmet 12 / 18 / 24 / 34 / 48 (Mithril and Onyxium = 48, stop there); free (no fuel); `/lamp` toggle + menu button default on; other players see torch glow only? | [yes to all] | `research/cloud/Mining-Lamp-Spec.md` Q1-7 |

### Fishing and food

| # | Question (short) | Default | Source |
|---|---|---|---|
| 29 | 39 species enough to start; five Fabled / Mythic "unclaimed" fish OK; keep a rare fish as a trophy; Z3 / Z5 price nudge later; fillets by band; names keep the jokes? | [as is; yes; yes; leave; by band; keep, sparing] | `research/cloud/Fish-Species-Catalog.md` Q2-7 |
| 30 | Whole fish sell to a dock NPC by weight; fish foods cooked at the Cooking Bench; "hold to reel" helper (Server Setup, off); treasure coins 5-7%; Zone 3 ice hole; vanilla treasure and junk count toward no collection? | [yes; yes; off; as is; break a hole; yes] | `research/cloud/SkyyFishing-Spec-Draft.md` Q2-5, Q8-9 |
| 31 | Fishing UI: bar-fight HUD widget (horizontal); show click rate; grade only after landing; ask before filleting Rare+; Recipes tab list only? | [yes to all] | `research/cloud/Fishing-UI-Mockup.md` Q1-6 |
| 32 | Eating: faster (x0.75), hits still cancel; Sated 25 s; grain = Veggie, eggs / cheese / fish = Meat; potion heal-over-time breaks on hit? | [yes to all] | `research/cloud/Food-Expansion-Draft.md` Q1-3, Q7 |
| 33 | New focused Mana potion (Signature stays); mushroom bonuses Strength / Crit Damage only; NoCube foods keep their own effects, no Grades; fish foods plain Meat? | [yes to all] | `research/cloud/Food-Expansion-Draft.md` Q4-6, Q8 |

### Pets, shards, story and town

| # | Question (short) | Default | Source |
|---|---|---|---|
| 34 | Pet sources: zone and start rarity per pet; a free zone egg on each guardian's first kill; ~35 h per Epic pet; Legendary/Mythic only by Upgrade Stones; Stable bonding free; duplicate = tradable second pet? | [yes to all] | `research/cloud/Pet-Sources.md` Q1-7 |
| 35 | Pocket Shards launch list 12 types first (not 30); items count for collections when collected; auto-sell later with the daily cap? | [12; when collected; later] | `research/cloud/Pocket-Shards-Spec.md` Q1-3 |
| 36 | Story: dragon fight is "prove yourself" (yields at 25%); Camel is the first mount pet; fifth zone-hopping hub item (a form folder) or quest log only? | [prove yourself; Camel; quest log] | `research/cloud/Story-Script-Zones-2-5.md` Q1-3 |
| 37 | Zone 1 town v2: keep layout; spawn on temple outside steps; build-protected, homes later; Pebble leaves in Z1.2; walk times fine; walk-in Bank / Bazaar / AH; Tab Hall sealed "Under Renovation"? | [yes to all] | `research/cloud/Zone-1-Town-Layout.md` Q1-7 |

### Mods, art and process

| # | Question (short) | Default | Source |
|---|---|---|---|
| 38 | NoCube: ship links now (CurseForge modpack later); own watering cans; Culinary / Rare Monsters / Undead Warriors only after a local check; skip Bakehouse, Tavern, Simple Bags, Dragon Nestkeeper? | [A now; own; after check; skip four] | `research/cloud/NoCube-Mods-Survey.md` Q1-6 (some overlap `docs/answered/project.md` lines 37-39) |
| 39 | Art order (accessory icons + lamp first); vanilla texture density if the engine takes no 2x; painted helmet lamp if armor cannot glow; "Boots" = Legs slot; hand-made claw model test first? | [yes to all] | `research/cloud/Art-Checklist-Local.md` Q1-5 |
| 40 | Art review order as listed; give the never-reviewed v1 folders the 2x-4x density pass too? | [as listed; yes] | `research/cloud/ART-INDEX.md` Q1-2 |

## For the local session

- Rows 5-7 are proposals only until Skyy answers; the drafts say "proposed" and keep the old values as the live default. After an answer, apply the file edits listed in `research/cloud/Chain-Premium-Fix.md` and `research/cloud/Consistency-Pass-1007.md`.
- When Skyy answers, close each with `python tools/qa_append.py <topic> <file> --close "<words from the question>"` (or `--no-question`).
