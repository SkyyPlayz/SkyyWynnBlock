# SkyyFishing - our own fishing mod (spec draft)

Cloud draft, 2026-10-06. Paper design; nothing built. Every number is a placeholder and a Server Setup row (section 13; times in seconds).
Inputs read: `CLOUD-RESUME.md` task "SkyyFishing spec draft"; `docs/answered/skills.md` (LOCKED 2026-10-06 FISHING, whole line; LOCKED 2026-10-06
POTIONS "add hyfishing right now ... fishing seasons"); `docs/answered/project.md` (2026-10-06 Dynamic Seasons; Angler's Almanac + HyFishing ideas only);
`docs/answered/economy.md` R3; `docs/answered/mobs.md` R5 (no mob coins, "OCEANS: skip"); `docs/log/2026-10.md` l.127-130 (HyFishing 0.6.8 DEPLOYED
2026-10-06 07:03 as a stopgap); `PACK.md`; `docs/tests/2026-10.md` (pack test); `research/cloud/Economy-Audit.md`, `Loot-Round-Revision.md`,
`Loot-Box-Design.md`, `Collection-Unlocks-Draft.md`, `Gathering-Armor-Mining-Farming.md`, `Zone-4-5-Materials.md`; `research/Collections-Spec.md`
(hidden Fishing / RawFish), `research/Cooking-Skill-Spec.md` (Food_Fish_Raw / Grilled), `research/Durability-Switch-Research.md` ("Fishing does not
exist in this build"), `research/Mob-Levels-Research.md` (vanilla fish NPCs), `research/Hypixel-Accessories-Research.md` (Agarimoo line).

**Decisions followed (not re-decided):** our own mod; Fishing bench; HOOK / LINE / SINKER / ROD / REEL made at the bench and put together in a second
tab; ROD = max fish weight / length; REEL = reeling power per click; line to the bobber + "!" bite sign; OUR click minigame (clicks raise the bar,
the fish pulls it down, fill it to catch, bigger / better fish escape more easily); fish LENGTH + WEIGHT, sell price by weight; rod reforges = base
improvements, most modifiers from hook / line / sinker (SkyBlock style); treasure = coins + unidentified gear; later sea creatures and Zone 4 lava
fishing; fishing book + fishing bag + fish foods; FISH COLLECTIONS unlock fishing armor; rods + reels need a fishing collection AND the metal's
collection; gathering accessories; HyFishing stays in the pack until ours replaces it; Dynamic Seasons' fishing seasons must work with ours; R3; R5.

## 0. Research (ideas only - no code, art or text copied)

| Fact | Source |
|---|---|
| Angler's Almanac: biome-dependent catches, minigames whose difficulty scales with the fish's rarity (a Stardew-style "Tension Bar"), a book that tracks every fish; JSON-driven config | [CurseForge](https://www.curseforge.com/hytale/mods/anglers-almanac) (search snippet; page + the [docs site](https://rm20killer.github.io/Anglers-Almanac-Doc/) blocked here) |
| HyFishing: biome-aware catches (fresh / salt water), bite-and-reel, random size + length, personal / global records, `/hfleaders`, Angler's Bench (rod, Fish Bag, a Recipes tab with 3 meals), 4 rarity tiers Common / Uncommon / Rare / Legendary with per-species weights | [CurseForge](https://www.curseforge.com/hytale/mods/hyfishing) + file pages (snippets) |
| Licences: neither page snippet shows one; both jars carry none (log 2026-10-06) -> **ideas only** | same; UNVERIFIED 1 |
| SkyBlock rod parts: one **Hook** (raises the chance of certain catches, e.g. Common Hook +25% common sea creatures; Treasure Hook), one **Line** (fishing stats, e.g. Titan Line +2 Double Hook), one **Sinker** (gameplay changes: Junk, Icy, Hotspot, Chum, Sponge ...); an NPC (Roddy) adds / removes them | [0.22 Backwater Bayou](https://hypixel.net/threads/5863219), [Stingy Sinker](https://hypixelskyblock.minecraft.wiki/w/Stingy_Sinker) (snippets) |
| SkyBlock stats: Sea Creature Chance (no cap, >100% useless), Fishing Speed, **Treasure Chance**; treasure grades Good 89% / Great 10% / Outstanding 1% | [Fishing Guide](https://hypixelskyblock.minecraft.wiki/w/Tutorial:Fishing_Guide), [Treasure](https://hypixelskyblock.minecraft.wiki/w/Treasure) (snippets) |
| SkyBlock Trophy Fish (lava, Crimson Isle): Bronze / Silver 25% / Gold 2% / Diamond 0.2%; boosted by armor, bait, rod, pet | [Trophy Fish](https://hypixelskyblock.minecraft.wiki/w/Volcanic_Stonefish) (snippet) |
| SkyBlock Raw Fish collection; Fishing Minion at Raw Cod II; Angler armor = Sea Creature Chance set | [Fishing Minion](https://hypixelskyblock.minecraft.wiki/w/Fishing_Minion_V) (snippet) |
| Minecraft: about 85% fish / 10% junk / 5% treasure; Luck of the Sea moves ~2% per level from junk to treasure | [fishing guide](https://xgamingserver.com/blog/minecraft-fishing-guide/) (snippet) |

What we take: Almanac's line + "!" + book; HyFishing's length / weight, bench, bag, meals, records; SkyBlock's 3-part rig, stats and treasure
grades; Minecraft's fish / junk / treasure split. What we drop: tension-bar minigame (Skyy), SkyBlock's NPC rig changes (our bench tab does it).

## 1. The loop in one paragraph

Craft parts at the **Fishing Bench**, rig a rod in its **Rig** tab, cast into water. The bobber floats, the line shows, a "!" pops on a bite. Use
the rod again within the **bite window** to hook it, then **click fast**: the bar rises with every click and the fish drags it down. Fill it to land
the fish (species, grade, weight, length) - or catch junk or **Lost Property** (treasure). Sell whole fish by weight to the **Clerk of Unclaimed
Catches**, fillet them for Cooking and the Bazaar, log records in the **Angler's Ledger** (book), push Fishing XP and the fish collections that
unlock better rods, reels, parts, armor and accessories. Lore: the Void's waters are where the Department of Arrivals' lost luggage ends up.

## 2. Casting and the bite

| Step | Rule | Rows |
|---|---|---|
| Cast | rod Use; bobber lands up to `fish.castRange` 12 blocks out; needs water (lava: section 10) at least 2 blocks deep and 3 wide | `fish.castRange`, `fish.minDepth` |
| Wait | bite after `fish.biteMin` 6 .. `fish.biteMax` 18 s, divided by (1 + Fishing Speed / 100) | `fish.biteMin`, `fish.biteMax` |
| "!" | sign above the bobber + a splash sound; window `fish.biteWindow` 1.2 s to Use the rod again, else the fish leaves (re-wait) | `fish.biteWindow` |
| Roll | at the bite: catch kind (fish / junk / treasure, section 7), then species, grade and weight (section 5) - shown only after landing | |
| Idle | bobber despawns after 60 s with no bite or if you walk > `fish.castRange` + 8 away | `fish.idleSeconds` |

## 3. The minigame (clicks vs pull)

The bar runs 0-100, starts at `fish.barStart` 35. Each click adds **gain = Reel Power / heft**, heft = max(0.6, weight in kg ^ 0.3). Every second
the fish pulls **pull** points off by grade (Common 6, Uncommon 7.5, Rare 9.5, Epic 11.5, Legendary 14) and **surges** to x1.6 for 0.6 s every
3 s. Landed at 100; lost at 0 or after `fish.timeLimit` 12 s. Clicks above `fish.maxCps` 12 per second are ignored (anti-macro).

**Catch odds** (python Monte Carlo, 3,000 tries each; click rate per try ~ normal(6.5, 1) per second; reel matched to the rod tier):

| Weight / grade | Common | Uncommon | Rare | Epic | Legendary |
|---|---|---|---|---|---|
| half the rod's max weight | 100% | 99% | 96% | 88-91% | 70-74% |
| at the rod's max weight | 98% | - | 80-83% | - | 26-30% |
| at max weight, reel **one tier lower** | - | - | - | - | 2-9% |
| at max weight, reel **one tier higher** | - | - | - | - | 56-73% |

Same at every tier (the reel ladder keeps gain constant at the rod's max). Click speed matters a lot (Iron tier, max weight, Legendary):
4 clicks/s 0%, 5/s 3%, 6.5/s 28%, 8/s 77%, 9/s 94%; a Common at max weight: 4/s 46%, 5/s 77%. So slow clickers need parts (all three
section 4 bonuses at IV turn 28% into 60%) and an accessibility row (`fish.holdAssist`, off: holding Use counts as 5 clicks/s - Q4).
Average fight time when landed: ~9 s at max weight.

## 4. Gear: rod, reel, hook, line, sinker

### 4.1 Rod and reel tiers (rod = max weight; reel = power per click)
Reel Power = 2.88 x (rod max kg) ^ 0.3 (keeps gain/click ~3.6 at half weight, so every tier plays the same). Level = Fishing skill level, like tools.

| T | Metal | Fishing Lv | Rod max kg | Reel Power | Rod needs (collections, section 8) | Reel needs |
|---|---|---|---|---|---|---|
| 0 | Bamboo / wood | 1-13 | 3 | 4.0 | start (bench recipe) | start |
| 1 | Copper | 10-18 | 6 | 4.9 | Pond Fish III + Copper IV | Pond Fish IV + Copper IV |
| 2 | Iron | 15-23 | 10 | 5.7 | Pond Fish VI + Iron IV | Pond Fish VII + Iron IV |
| 3 | Thorium | 20-28 | 16 | 6.6 | Dune Fish III + Thorium IV | Dune Fish IV + Thorium IV |
| 4 | Cobalt | 25-38 | 25 | 7.6 | Dune Fish VI + Cobalt IV | Dune Fish VII + Cobalt IV |
| 5 | Adamantite | 35-43 | 40 | 8.7 | Frost Fish III + Adamantite III (E curve gate) | Frost Fish IV + Adamantite III |
| 6 | Mithril | 40-49 | 60 | 9.8 | Frost Fish VI + Mithril III | Frost Fish VII + Mithril III |
| 7 | Onyxium | 40-49 (50+ later) | 90 | 11.1 | Lava Fish III + Onyxium (hidden collection) | Lava Fish IV + Onyxium |
| 8-12 | Cindersteel, Amberite, Drakonite, Voidglass, Aetherium (proposal) | 50-100 | 130 / 180 / 250 / 340 / 450 | 12.4 / 13.7 / 15.1 / 16.5 / 18.0 | Lava / Cave Fish + the metal | later |

Each tier is crafted FROM the previous rod / reel + the new bars (the "upgrade the piece" rule). A fish heavier than the rod's max **never bites**
(the weight is re-rolled), so a better rod = bigger fish = more coins. Rod and reel are separate items so a player can mix tiers (section 3 table).
**Rod reforge** (SkyyRolls, like tools; rarity Normal..Mythic x1.0-1.7): pool Fishing Speed +2-6, Treasure Chance +0.2-0.6, Reel Power +2-5%,
Fishing Wisdom +2-5%. That is all the rod adds - the big modifiers come from the parts.

### 4.2 Parts: one hook, one line, one sinker per rod; four part tiers
Part tier I = rod T0-T1 (Zone 1), II = T2-T3, III = T4-T5, IV = T6-T7 (and V later). Each part variant is a fixed item (no rolls), crafted from the
tier below. Materials "whatever fits" (Skyy): hooks = metal bars, lines = fibres, sinkers = stone.

| Part | Variant | Effect I / II / III / IV | Material (+ collection that unlocks it) |
|---|---|---|---|
| Hook | Barbed Hook | grade luck +5 / 10 / 15 / 20% (scales Uncommon+ odds) | bars of the tier's metal; fish collection II |
| Hook | **Lost Property Hook** | Treasure Chance +1 / 2 / 3 / 4 points | bars + Enchanted bars at IV; fish collection V |
| Hook | Lure Hook | Fishing Speed +5 / 10 / 15 / 20 | bars + any fillet; fish collection II |
| Hook | Monster Hook (stage 3) | Sea Creature Chance +2 / 4 / 6 / 8 | bars + sea creature drops |
| Line | Braided Line | time limit +1 / 1.5 / 2 / 2.5 s | Plant Fibre -> Linen -> Silk -> Cindercloth (Farming / Combat collections) |
| Line | Steady Line | surge pull -15 / 25 / 35 / 45% | same fibres + Slime / Sap (UNVERIFIED ids) |
| Line | Twin Line | double catch 2 / 4 / 6 / 8% (a second fish of the same species, rolled weight) | fibres + fish collection VII |
| Line | Scholar's Line | Fishing Wisdom +2 / 4 / 6 / 8% | fibres + book paper |
| Sinker | Weighted Sinker | bar start +5 / 10 / 15 / 20 | Cobblestone -> Sandstone -> Slate -> Basalt (Mining stone collections) |
| Sinker | Clean Sinker | junk -25 / 50 / 75 / 100% (junk turns into fish) | same stones |
| Sinker | Deep Sinker | weight roll leans heavy: +5 / 10 / 15 / 20% average weight (still <= rod max) | same stones + Enchanted stone |
| Sinker | Ember Sinker (stage 3) | needed for lava fishing; lava fish bite | Ember Shard + Basalt (Zone-4-5-Materials) |

Stacking caps: Fishing Speed +100, Treasure Chance 15%, double catch 20%, bar start 60, time limit 16 s, surge cut 50% (`fish.cap.*`). Parts
come off for free in the Rig tab; nothing is destroyed.

## 5. Fish: species, grade, weight, length

**Water = zone.** Each zone has its own fish table (no oceans - R5 lock): Z1 Emerald Wilds ponds / rivers, Z2 Howling Sands oases, Z3 Whisperfrost
ice holes (break the ice first), Z4 Devastated Lands lava, Z5 dinosaur caves' underground lakes. Fish level for loot = the zone's range (as caves).

| Zone | Species (working names; vanilla fish looks where they exist) | Weight range kg | Season lean (Dynamic Seasons) |
|---|---|---|---|
| Z1 | Minnow 0.05-0.4, Bluegill 0.1-1, Trout 0.5-5, Catfish 1-10, Pondering Pike ("waiting for its number") 2-10 | 0.05-10 | Trout spring, Catfish summer |
| Z2 | Oasis Carp 1-8, Sandskipper 0.5-4, Mirage Eel 2-14, Dune Piranha 1-6, Lost Luggage Grouper 6-25 | 0.5-25 | Eel night, Carp summer |
| Z3 | Frost Cod 2-15, Glass Pike 4-30, Icebound Salmon 3-20, Whisper Sturgeon 15-60 | 2-60 | winter x1.5 for all |
| Z4 lava | Cinderfin 5-30, Slag Ray 10-60, Ashen Eel 8-45, Stamp-Scorched Kingfish 30-90 | 5-90 | season-free |
| Z5 caves | Blind Gar, Fossil Coelacanth, Drake-Eel ... (later) | 20-450 | season-free |

| Roll | Rule | Rows |
|---|---|---|
| Species | weighted per zone; in-season x1.5, off-season x0.5, night / day leans | `fish.species.<id>.weight`, `.season` |
| Grade (HyFishing-style + vanilla's 5 fish tiers) | Common 62 / Uncommon 24 / Rare 10 / Epic 3.5 / Legendary 0.5%, Barbed Hook scales the non-Common share | `fish.grade.odds` |
| Weight | w = min + (max - min) x u ^ 2 (many small, few big), u uniform; Deep Sinker lowers the exponent; > rod max = re-roll | `fish.weightSkew` |
| Length | L cm = (100 x weight in grams / K) ^ (1/3) x (0.95..1.05); K = species shape (eel 0.6, trout 1.0, carp 1.4). 1 kg trout = 46 cm, 90 kg = 208 cm | `fish.species.<id>.k` |
| Item | one item per species + grade; weight / length in the item's metadata, so whole fish **do not stack** (UNVERIFIED 4) | |
| Records | personal + server record per species (weight); a record fish gets a gold name line "Record 7.82 kg" | `fish.records` |

## 6. Selling and the Bazaar loop rule

| Way | Price | Notes |
|---|---|---|
| **Whole fish** -> Clerk of Unclaimed Catches (NPC at every town dock) | weight x zone price per kg x grade (Common 1, Uncommon 1.5, Rare 2.5, Epic 4, Legendary 8) | per-kg: Z1 18, Z2 20, Z3 28, Z4 32, Z5 40. A per-species demand factor like the Bazaar's (each sale lowers it, half-life 7,200 s, floor 0.25) instead of a hard cap |
| **Fillet** at the bench (or Cooking Bench) | 1 Raw Fish fillet per 0.5 kg, max 40 | fillets = a normal Bazaar product per zone; base set so instant sell is ~70% of selling the whole Common fish (Z1 base 7: 12.6 vs 18 per kg) |
| AH | free price | records and Legendaries; player-to-player, no new coins |

Income (python; 21 s per cast = 171 casts/h, 85% fish, 92% landed = 134 fish/h, average weight 0.4 x rod max, grade mix x1.41):
**Z1 ~8,200/h, Z2 ~24,000/h, Z3 ~85,000/h, Z4 ~218,000/h, Z5 ~393,000/h** - about the same as the Economy-Audit active income per phase
(8k early / 90k mid / 360k end), so fishing is "good money" without beating everything. It is a new faucet (Economy-Audit F3-like, row F10).
**Loops:** fish cannot be bought from any NPC, fillets cannot become fish, and every fish food made from fillets follows `bazaar.maxChainPremium`
15% (Economy-Audit C4) - no buy-craft-sell loop. Whole fish are never Bazaar products (unique weights).

## 7. Catch kinds and the treasure table ("Lost Property")

| Kind | Base | Changed by |
|---|---|---|
| Fish | 85% | Clean Sinker moves junk here; sea creatures (stage 3) take from it |
| Junk | 10% | soggy boots, sticks, bones, seaweed, a "Form 27-B (illegible)" note; NPC sell-back pennies; no collection |
| Lost Property (treasure) | 5% | Treasure Chance (hook, rod reforge, armor, accessories; cap 15%) |

| Grade | Odds | Contents (one roll) |
|---|---|---|
| Good | 89% | 40% coin purse 40-120 x zone mult; 35% zone materials (ore, logs, a few Enchanted at Z3+); 15% unidentified gear box Normal / Unique; 10% bait / part scrap |
| Great | 10% | 30% purse 300-700 x zone mult; 40% unidentified box Rare+; 20% Enchanted materials; 10% a drop-only part (e.g. "Clerk's Lucky Hook") |
| Outstanding | 1% | 25% purse 2,000-4,000 x zone mult; 40% box Legendary+ (Mythic 5% of these); 25% a fishing accessory (section 9, bound); 10% a pet egg (Pets-Spec, later) |

Zone coin mult Z1 x1, Z2 x2.5, Z3 x10, Z4 x30, Z5 x60. Python: 8.6 treasures/h; treasure coins = **4.5-6.7% of fishing income** in every zone
(Z1 ~440/h, Z5 ~26,000/h). Coins are allowed here because Skyy locked "money" (R5's no-coins rule is about mobs); they buy nothing locked (R3).
**Gear boxes** follow `Loot-Round-Revision.md`: `src = fish`, source level L = the zone's level (hardest-biome-of-zone rule not needed), range
L-2..L+2, rarity at drop, item decided at identify, re-roll rules unchanged; ids from Loot-Box-Design (option C `Skyy_Unid_<Type>_<Rarity>` or B).

## 8. Collections (fishing category comes out of hiding)

Count = 1 per fish **landed by fishing** (fillets, bought / traded fish and vanilla fish kills never count; the existing hidden RawFish collection keeps
counting kills and opens as a Combat-side extra). Curve **R** (8 tiers: 25 / 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000; at 134 fish/h tier IV
= ~2 h, VI = ~7.5 h). Collections: Pond Fish (Z1), Dune Fish (Z2), Frost Fish (Z3), Lava Fish (Z4), Cave Fish (Z5), Lost Property (treasure, E curve).

| Tier | Pond / Dune / Frost / Lava Fish unlock |
|---|---|
| I | Fishing Bench upgrade page (bigger Fish Cooler) + coins |
| II | Barbed + Lure Hook of the zone's part tier; Fishing XP lump |
| III | **rod** of the zone's first metal (with that metal's tool gate, section 4.1) |
| IV | **reel** of the first metal; Weighted / Clean / Deep Sinker |
| V | Lost Property Hook; Braided / Steady Line |
| VI | **rod** of the second metal + **fishing armor** of the zone's tiers (section 9) |
| VII | **reel** of the second metal; Twin Line; fishing accessory upgrade |
| VIII | capstone: +1% permanent Fishing Speed per collection + Enchanted Fillet recipe |

R3 holds: all recipes come only from collections; no shop sells rods, parts, armor or accessories.

## 9. Fishing armor and accessories

**Angler's gear** follows `Gathering-Armor-Mining-Farming.md`: 4 pieces, low Defense, any class, checks the Fishing level, 8 tiers (T0 start +
Copper..Onyxium echoes), each crafted from the previous piece, unlocked at fish collection VI, never drops unidentified.
Look: oilskin rain-slicker + wide-brim hat + waders; the metal shows as buckles, hat band and a lure pinned to the hat.

| T | Set | Fishing Speed | Treasure Chance | Fishing Wisdom | Signature (2 / 4 pieces) |
|---|---|---|---|---|---|
| 0 | Oilskin | +4 | - | - | 4 pc: bite window +0.3 s |
| 1-2 | Copper / Iron Angler | +6 / +9 | +0.5 / +1 | - | 2 pc **Patient Queue**: "!" also chimes in chat |
| 3-4 | Thorium / Cobalt Angler | +12 / +16 | +1.5 / +2 | +2 / +3% | 4 pc **Steady Hands**: surge pull -15% |
| 5-6 | Adamantite / Mithril Angler | +20 / +25 | +2.5 / +3 | +4 / +6% | 4 pc **Lost and Found**: Great treasure x1.5 |
| 7 | Onyxium Angler | +30 | +3.5 | +8% | 4 pc: lava heat immunity while fishing |

Rarity multiplies like tools (x1.0-1.7). Reforge pool: Fishing Speed, Treasure Chance, Fishing Wisdom, Defense (small).

**Accessories** (Skyy: boosts for fishing, mining, farming, foraging), each tier crafted from the one below (LOCKED 2026-10-03), from collection
VII rows or Outstanding treasure; never from shops: **Bobber Charm** (Talisman / Ring / Artifact: Fishing Speed +2 / +4 / +6), **Lost Property
Tag** (Treasure Chance +0.5 / +1 / +1.5), **Angler's Ledger Page** (Fishing Wisdom +2 / +4 / +6%), **Lava Ward** (stage 3: lava fishing heat).

## 10. Later: sea creatures, lava fishing, events

| Stage | Feature | Rules |
|---|---|---|
| 3 | **Sea creatures** | Sea Creature Chance base 0% (hooks, armor), cap 40%; a levelled SkyyMobs creature (zone range) jumps out at the bobber and attacks; R5: **no coins**, drops = creature parts (Monster Hook material), fish-collection +3, gear box roll like an elite; zone-tied list (vanilla water mobs, ids UNVERIFIED 6) |
| 3 | **Zone 4 lava fishing** | needs an Ember Sinker + Onyxium rod or better; lava fish species (section 5); Trophy-style record tiers per species (Bronze / Silver / Gold / Diamond at 25 / 50 / 75 / 95% of max weight) |
| 4 | Zone 5 cave lakes + tiers 8-12 | with the Cindersteel+ ladder |
| 4 | Fishing Festival | a Zone Special theme ("Unclaimed Baggage Day": treasure +20%, no coin effects - Zone-Specials-Spec rule) |

## 11. Bench, book, bag, foods, HyFishing, Dynamic Seasons

| Thing | Design |
|---|---|
| **Fishing Bench** (crafted at the Workbench) | tabs: **Parts** (craft rods, reels, hooks, lines, sinkers), **Rig** (rod slot + reel / hook / line / sinker slots; shows max weight, Reel Power and the summed stats), **Fillet**, **Recipes** (fish foods - see below). Inline pages, `tools/skyyui.py` vanilla look |
| **Angler's Ledger** (book item + `/fishbook`) | per zone: species found / missing ("???"), where + season + time, best weight / length, grades caught, record holders; Almanac-style look in our UI kit |
| **Fish Cooler** (the "fishing bag") | whole fish do not stack, so a list storage of 27 fish (54 / 81 by collection I upgrades); fillets, parts and junk go to SkyySacks as a 6th "Fishing" bag type (Bag-Restructure-Spec already allows it) |
| **Fish foods** | graded by SkyyCooking, family = MEAT focus (Stamina) per the POTIONS / FOOD lock; fish + veggie / fruit combos get both bonuses. Recipes and numbers: `research/cloud/Food-Expansion-Draft.md` (written in parallel). Proposed dishes: Grilled Fish (exists), Fish Skewer, Fish Sticks, Chowder, Frost Cod Stew, Cinderfin Jerky (Z4) |
| **HyFishing** (pack mod since 2026-10-06, stopgap) | stage 1 runs NEXT to it: our rods have our own item ids, so each mod only reacts to its own rod (UNVERIFIED 2). When stage 2 passes Skyy's test, drop HyFishing from `PACK_THIRD_PARTY` + PACK.md; before that, the Clerk takes HyFishing fish for a flat price (one week) so nothing is stranded (UNVERIFIED 3: what happens to its items once the jar is gone) |
| **Dynamic Seasons** | read its current season through its API / event if it has one (UNVERIFIED 5); else our own fallback = no season lean. Seasons only change species weights, never prices |

## 12. Build stages (each a FULL round: new system, coins, saved data, items)

| Stage | Content |
|---|---|
| 1 | SkyyFishing 0.1: bench (Parts / Rig / Fillet), T0-T2 rods + reels, part tier I-II, cast / bobber / line / "!" / minigame HUD, Z1 species, weight + length + grade, Clerk sell + fillet Bazaar product, junk + Lost Property (coins + materials; gear boxes once SkyyGear 0.2.6 boxes exist), Fishing skill un-hidden (SkySkills), Pond Fish collection, Fish Cooler |
| 2 | Z2-Z3 species, T3-T6, part tier III, Angler's Ledger, armor T0-T4, accessories I-II, Dynamic Seasons link, Recipes tab with SkyyCooking, HyFishing removal |
| 3 | sea creatures, Z4 lava fishing, T7, part tier IV, armor T5-T7, trophy tiers, records leaderboard |
| 4 | Z5, tiers 8-12, Fishing Festival special, Fishing skill tree (Skill-Trees-Spec slot) |

## 13. Server Setup rows (Fishing page)

`fish.castRange` 12, `fish.minDepth` 2, `fish.biteMin` 6, `fish.biteMax` 18, `fish.biteWindow` 1.2, `fish.idleSeconds` 60, `fish.barStart` 35,
`fish.timeLimit` 12, `fish.maxCps` 12, `fish.holdAssist` off, `fish.pull.<grade>` 6 / 7.5 / 9.5 / 11.5 / 14, `fish.surgeMult` 1.6, `fish.surgeEvery` 3,
`fish.surgeLength` 0.6, `fish.rod.<tier>.maxKg`, `fish.reel.<tier>.power`, `fish.part.<id>.<stat>`, `fish.cap.*`, `fish.grade.odds`, `fish.weightSkew` 2,
`fish.species.<id>.{weight,min,max,k,season}`, `fish.kind.odds` 85 / 10 / 5, `fish.treasure.grades` 89 / 10 / 1, `fish.treasure.<grade>.table`,
`fish.treasure.zoneMult`, `fish.price.perKg.<zone>`, `fish.price.gradeMult`, `fish.demand.halfLife` 7,200, `fish.demand.floor` 0.25,
`fish.fillet.kgPer` 0.5, `fish.fillet.max` 40, `fish.records` on, `fish.cooler.sizes`, `fish.seasons.enabled` on, `fish.seaCreature.cap` 40,
`fish.hyfishingTradeIn` on. Times in seconds.

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | Licences of Angler's Almanac and HyFishing pages (CurseForge / GitHub blocked here); the jars have none (log) -> ideas only until checked |
| 2 | How Hytale lets a mod draw a fishing line + bobber (entity, particles, model) and whether two fishing mods' rod interactions clash; `research/Durability-Switch-Research.md` says the base game has no fishing class |
| 3 | What happens to HyFishing items in inventories / bags when its jar is removed (vanish, unknown item, crash?) |
| 4 | Per-stack metadata (weight / length) on a food-like item: does it block stacking and survive bags, AH and SkyySacks? |
| 5 | Dynamic Seasons 6.1.2 API / event for the current season (it has optional Angler's Almanac / HyFishing integrations - read how) |
| 6 | Vanilla fish item / model ids (`Fish`, `Fish_Uncommon..Legendary`, `Food_Fish_Raw`, NPC roles minnow / bluegill / trout / catfish / tropical / lobster) and water-mob ids for sea creatures |
| 7 | Whether every click of Use reaches the server fast enough for a 12 cps bar (or a HUD key input is needed) and HUD bar refresh rate |
| 8 | Fibre / Silk / Cindercloth / Basalt / Slate item ids for parts |
| 9 | Income numbers are paper (Economy-Audit section 8 measure 1 should add a fishing session) |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Should a fish heavier than your rod's max simply never bite (re-rolled), or bite and snap the line? | [never bites - no frustration] |
| 2 | Whole fish sell to a dock NPC by weight; fillets go on the Bazaar. OK? | [yes] |
| 3 | Fish foods: cooked at the Cooking Bench (graded by SkyyCooking) and only listed in the Fishing Bench Recipes tab? | [yes] |
| 4 | Fast clicking is hard for some players: add a "hold to reel" helper (counts as 5 clicks/s) for everyone, off, or Server Setup only? | [Server Setup row, off] |
| 5 | Treasure coins at about 5-7% of fishing income - enough "money", or more? | [as is] |
| 6 | Keep HyFishing until our stage 2 passes your test, then remove it with a one-week fish trade-in? | [yes] |
| 7 | Whole fish don't stack (each has its own weight): a Fish Cooler list storage (27 -> 81 fish), or round weights so fish stack? | [Fish Cooler] |
| 8 | Zone 3 ice fishing: break a hole in the ice, or only open water? | [break a hole] |
