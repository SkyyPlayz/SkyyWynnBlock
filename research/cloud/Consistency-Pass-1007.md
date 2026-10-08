# Consistency pass 2026-10-07 (drafts vs newer drafts and Skyy's answers)

Cloud draft, 2026-10-08. Paper design; nothing built. Followed: `docs/answered/gear.md` line 87 (Monk Saffron LOCKED), `docs/answered/classes.md` lines 116-117 (no void protection on any traversal),
lines 112, 132-138, 142 (Mana Barrier, Banner, Blood Frenzy, Sanctuary numbers), `docs/answered/gear.md` lines 103-105 (spellbook + kunai defaults, kunai no durability). Method: grep of every
`research/cloud/**/*.md`, then a read of each hit. Newer drafts that are only proposals are written as "proposed X (file)", not as fact.

## Edited (stale line -> now)

| file:line | stale | now | source |
|---|---|---|---|
| `research/cloud/Zone-4-5-Materials.md`:86 | Ember Ore **11,000** shown as the price | kept as the live default, annotated "proposed 4,300" | `research/cloud/Ember-Economy-Check.md` Q1 |
| `research/cloud/Zone-4-5-Materials.md`:87 | Amberite **30,000** | kept, annotated "proposed 9,300" | `research/cloud/Zone-5-Ore-Prices.md` Q1 |
| `research/cloud/Zone-4-5-Materials.md`:88 | Drakonite **75,000** | kept, annotated "proposed 23,000" | `research/cloud/Zone-5-Ore-Prices.md` Q1 |
| `research/cloud/Zone-4-5-Materials.md`:76 | "+0.2% on a 30,000 ore" | adds "+0.65% at the proposed 9,300" | `research/cloud/Zone-5-Ore-Prices.md` side prices |
| `research/cloud/Zone-4-5-Materials.md`:92 | "33k would break the ladder" (Drakonite Block impossible) | adds "proposed 23,000 gives a Block of 676,825,600, under 1e9" | `research/cloud/Zone-5-Ore-Prices.md` Q4 |
| `research/cloud/Ore-Regrow-Spec.md`:112 | "fills the world with 11,000-coin ore" | adds "proposed 4,300" | `research/cloud/Ember-Economy-Check.md` |
| `research/cloud/Ember-Economy-Check.md`:29 | "Amberite (200/h, 30,000)" | adds "proposed 9,300 below, line 70" | `research/cloud/Zone-5-Ore-Prices.md` |
| `research/cloud/Kunai-Ladder.md`:129 | Over void: needs ground within `kunai.floorCheck` 12; "never ends over open void" | no void protection; the throw may land over void (line 22 already said so) | `docs/answered/classes.md` line 117 |
| `research/cloud/Kunai-Ladder.md`:167 | `kunai.floorCheck` default 12 | default 0 (was 12), row can be dropped | `docs/answered/classes.md` lines 116-117 |
| `research/cloud/Monk-Colour-Options.md`:96 | Question 1 still open, default Jade teal `#38c9a8` | CLOSED: LOCKED Saffron `#f08a30` | `docs/answered/gear.md` line 87 |
| `research/cloud/Monk-Colour-Options.md`:68 | "Recommendation: C Jade teal" | prefixed "History - superseded by the LOCKED Saffron" | `docs/answered/gear.md` line 87 |
| `research/cloud/SkyyFishing-Spec-Draft.md`:206 | "if Sushi needs it, it comes from a seaweed plant / the Cooking Skill (question 9)" | Sushi takes vanilla seaweed `Plant_Seaweed_*` or Azure Kelp (proposed), never junk | `research/cloud/Food-Expansion-Draft.md` section 7 |
| `research/cloud/Class-Abilities-Draft.md`:107 | Sanctuary "8 s" | adds LOCKED 12 s, radius 8, 5% max Health per second | `docs/answered/classes.md` line 142 |

## Left as is (why)

| file:line | what | why |
|---|---|---|
| `research/cloud/Zone-5-Ore-Prices.md` (30, 63, 67, 86, 87, 102) | 11,000 / 30,000 / 75,000 | the "old" columns of the re-fit itself |
| `research/cloud/Ember-Economy-Check.md` (1, 3, 8, 40-52, 93-106, 131) | 11,000 and old Amberite / Drakonite | the analysis of why 4,300 is proposed; titles and questions must keep the old value |
| `research/cloud/Bazaar-Drift-Check.md` (42, 54, 73) | Ember 11,000 beside 4,300 | a deliberate side-by-side comparison |
| `research/cloud/Chain-Premium-Fix.md` (1, 17, 27, 31, 37, 60-64, 77, 95-104) | 1.155, Ember 11,000, Amberite 30,000 | section tables, off-limits; they are the "before" columns and the edit list (already applied) |
| `research/cloud/Economy-Audit.md`:86 | "Block = 1.21x" | the historic problem sentence the fix keeps (C4); the rest of the row already says 1.1495 |
| `research/cloud/Enchanted-Materials-Draft.md` (114-135) | ratio 1.15x (1.1495) | already updated 2026-10-07 |
| `research/cloud/Ember-Economy-Check.md` (10, 78, 83) | 1.155 | explains the fix; marked "fixed 2026-10-07" |
| `research/cloud/fish-art/README.md` (12, 84), `research/cloud/Fish-Species-Catalog.md`:192 | seaweed junk icon / item | files say "retired" (README line 84 is the old v1 sheet table; kept to compare) |
| `research/cloud/Food-Expansion-Draft.md` (160-175) | seaweed in Sushi | this is the new source section |
| `research/cloud/Dragon-Quest-Spec.md`:82 | "dismount over void or lava: the dragon catches you" | a mount safety rule, not a traversal; see Questions for Skyy 1 |
| `research/cloud/Dragon-Quest-Spec.md`:45, `research/cloud/Starter-Shard-Layout.md`:92 | no fall death on a floating shard, void respawn without penalty | zone / starter-island rules, not a traversal move (`docs/answered/world.md` line 23 is an open question) |
| `research/cloud/Spellbook-Ladder.md` (63, 152), `research/cloud/Monk-Kit-Spec.md` (87, 108) | no fall damage after Levitate / vault / plunge | fall DAMAGE, not void protection; Skyy's rule is about the void only |
| `research/cloud/Kunai-Ladder.md`:68 | the Return goes to the nearest safe spot within 3 blocks | wall / inside-block safety stays (`docs/answered/classes.md` line 117); it does not mention the void |
| `research/cloud/Soul-Orb-Spec.md` | "tether" wording in a few lines | the file already names them Bindings; nothing numeric changed |
| `research/cloud/Class-Abilities-Draft.md` (62, 77, 93) | Enrage 10 s +30%, War Scream, Teleport "blink 12 blocks" | the 2026-10-03 first draft; the class spec `research/cloud/Class-Ability-Spec-Draft.md` supersedes it. Only the locked Sanctuary line was patched |
| `research/cloud/LOG.md` (62, 97, 111-112, 122) | 11k / 30k / 75k, 1.155, Jade, #ff7a5c | append-only log, off-limits |

## Stale lines in files I was told not to edit

| file:line | stale | now | source |
|---|---|---|---|
| `research/cloud/Class-Ability-Spec-Draft.md`:163 | Sanctuary "32% + 10% DR over 8 s" in the power ledger | 12 s, 5%/s = 60% heal over the zone, 10% DR | `docs/answered/classes.md` line 142 (line 74 of the same file is right) |
| `research/cloud/Class-Ability-Spec-Draft.md`:168 | Blood Frenzy "self 40% / party 20%" | 25 stacks = +37.5% damage, +25% attack speed, +12.5% move speed; allies half | `docs/answered/classes.md` lines 136-138 (line 85 is right) |
| `research/cloud/Class-Ability-Spec-Draft.md`:169 | Warlord's Banner "+15% / +25%, 40 s (15 s on)" | 30 s, +8% / +12% / +16% damage and defence, plus attack speed; kills extend; 40 Mana | `docs/answered/classes.md` lines 132-135 (line 86 is right) |
| `research/cloud/Class-Ability-Spec-Draft.md`:170 | Mana Barrier "30 s" cooldown and "max absorb 100%" in the ledger | check against the 12 s placed dome (line 66 is right) | `docs/answered/classes.md` lines 112-113 |
| `research/cloud/Modifier-Pool-Spec.md`:35 | Knockback+ "never into the Void (target is s..." | this is mob / target knockback, not a traversal, so it may stay; confirm | `docs/answered/classes.md` line 117 |
| `research/cloud/Modifier-Pool-Spec.md`:101, 38 | Follow lists Sanctuary, Shield Bubble | Mana Barrier also has a Follow upgrade (Skyy "Placed dome + Follow") | `docs/answered/classes.md` line 113 |
| `research/cloud/Class-Tree-Paths.md` | not read for edits (off-limits) | - | - |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Does "no void protection on any traversal" also cover the dragon mount's "dismount over void: the dragon catches you" (`research/cloud/Dragon-Quest-Spec.md`:82)? | [yes - remove the catch; the dragon is a flight, falling is the challenge] |
| 2 | Should the knockback modifier (`research/cloud/Modifier-Pool-Spec.md`:35, "never into the Void") also lose its void check, or is that only for your own moves? | [keep: it protects mobs and players from being pushed in, not a traversal] |

## For the local session

- Lines marked "proposed" in `research/cloud/Zone-4-5-Materials.md` become fact only after Skyy answers `research/cloud/Questions-Digest-1007.md` rows 6-7 (Ember 4,300; Amberite 9,300; Drakonite 23,000). Then change the table's Base column and the Block column (Ember 126,536,960; Amberite 273,672,960; Drakonite 676,825,600) and `bazaar.base.*` in one Bazaar round.
- `kunai.floorCheck` was 12 in the draft; SkyyArmory 0.1.7 queues the `blink.floorCheck` removal. Make the kunai default 0 (or drop the row) in the same round.
- The Monk is Saffron `#f08a30`; the build scripts still hold the old `#ff7a5c` (`research/cloud/class-art/README.md` line 49).
- The other agent's files (`research/cloud/Class-Ability-Spec-Draft.md`, `research/cloud/Modifier-Pool-Spec.md`) still need the table fixes above.
