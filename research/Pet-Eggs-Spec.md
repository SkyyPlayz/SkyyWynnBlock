# Pet eggs + hatching - build spec (SkyyPets 0.4)

Spec, 2026-10-15. Nothing built. Every number is a placeholder and a Server Setup row (SkyWynn Menu -> Server Setup -> Pets -> Eggs,
`tools/CONFIG-CONTRACT.md`; times in seconds) unless marked BUILD-TIME. Arithmetic checked in python (method in each section).
Replaces the egg parts of `research/cloud/Pet-Eggs-v2.md` (zone type eggs, species eggs, the Stable timer) and the "Pet Eggs" rows of
`research/cloud/Pets-Spec.md` 4; keeps their dupe rules, drop-hook notes and trading lock.

## 0. Skyy's words this follows (word for word in `docs/answered/pets.md`, newest first)

> 2026-10-15 PET EGGS + HATCHING: "plan, and finish building the pets. i want eggs. hatching with an animation where it rolls, and chooses
> what pet you get, then a second roll for the rarity. and the pet fusing. (so the way it works is, there are mining eggs, farming eggs,
> combat eggs and so on. pets pets arnt tiered, but generally ordered from best to worst in each category. when hatching an egg, you have
> a high chance to ghet a bad pet, and a low chance to get a good one. same for rarity commons are common, legendry's are extremely rare."
> Popups: eggs from "Rare drop while doing the skill, Collection rewards, Craftable, Shop / Bazaar" + "(eggs come in rarities from
> common to mythic. the better the egg the higher the chance of better pets. a legendary egg will always give an above average pet, and
> never below rare.)"; hatch rarities "Common to Mythic"; animation "Spinning reel, ~3 s each roll".

Also followed: 2026-10-15 PET SYSTEM (rarity = small multiplier x1-x1.5, fusing 4 -> 1, pet levels 50 + pet rebirths, no stones);
2026-10-10 "Eggs trade, pets don't" (eggs are items: Bazaar / AH / merchants; a hatched pet is a bound record); pet roles (pet slot /
summon slot); per profile. The 2026-10-10 "zone + species eggs" lock is older than the 10-15 words: this spec drops the zone axis and
species eggs by default (question 1).

Existing mods checked first (PROJECT-RULES 2): Kazzy's Pets & Mounts (`KazzyPets_Egg_*`, one egg per species, spawn eggs), FPetsPlugin
(spawn eggs), vanilla `Egg_Spawner_*` (spawn an NPC on use). None rolls a pet record, a rarity or a reel - learn only: vanilla
`Egg_Spawner_Lantern` uses the vanilla egg model by path (`Items/Consumables/Food/Egg.blockymodel`), which our world model reuses by
path (nothing copied).

## 1. Egg items

### 1.1 Ids, names, look

| Field | Value |
|---|---|
| Id | `Skyy_PetEgg_<Category>_<Rarity>` - Category Mining, Farming, Foraging, Combat, Exploration (Fishing later, section 2.3); Rarity Common, Uncommon, Rare, Epic, Legendary, Mythic. **30 ids** now (36 with Fishing) |
| Name | "Rare Mining Egg", "Mythic Exploration Egg" (lang `server.items.<id>.name`, written by SkyyPets only) |
| Flavor (tier tag first) | "Rare Egg - Right-click to hatch a random Mining pet. Better eggs give better pets." |
| Quality | vanilla `Common` / `Uncommon` / `Rare` / `Epic` / `Legendary` (slot frame, name colour, drop glow); Mythic = our own quality `Skyy_Pet_Mythic` shipped by SkyyPets (vanilla has no Mythic; same idea as SkyyAccessories' `Skyy_Acc_*` and SkyyCollections' `Skyy_Enchanted`; colour = `SUI.RARITY["Mythic"]`, Value 4 = below SkyyAuctions' technical threshold 8) |
| MaxStack | 25 (= vanilla `Food_Egg`; Skyy: "use Hytale stack numbers") - BUILD-TIME |
| Metadata | none. Plain ids, so the Bazaar / AH list them and an `ItemGridSlot` never sees metadata (HANDOFF 2) |
| Right-click | `"Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyyPetsHatch"}}]}}` + `OpenCustomUIInteraction.registerSimple` (the SkyySacks / SkyyMenu pattern, HANDOFF 2) |
| World / held model | vanilla `Items/Consumables/Food/Egg.blockymodel` by path + our own texture per rarity (6 PNGs) |
| Recipe | Common + Uncommon only (section 6.3), in the item JSON - BUILD-TIME |
| One table | `tools/skyyeggs.py` (NEW, like `tools/skyyench.py`): ids, names, rarity, category, recipe, Bazaar base / AUTO, merchant rows. Imported by SkyyPets (items), SkyyBazaar (products + recipe edges for its loop check), SkyyMerchants (rows), SkyyCollections (reward defaults) |

**Tier tag (standing rule):** eggs are tiered by rarity, so the tag is the rarity + noun, first phrase of the flavor: `Rare Egg - ...`.
No T-number (T1-T8 is the metal ladder; a "T3 Egg" would read as Iron). `research/Tier-Tags-Plan.md` line 74 leaves rarity-only items
untagged; eggs are the exception asked for here. `tools/tier_tags.py` gets `RARITY_NOUNS = ("Egg",)` + `rarity_tag("Rare", "Egg") ->
"Rare Egg"` and the 30 ids (owner SkyyPets) so the rule stays in one table; `tools/test_tier_tags.py` checks them.

### 1.2 Icons (art round A0 - no agents for planning, cloud draws, I review; skill `skywynn-art`)

| Art | Count | How |
|---|---|---|
| Egg icons | 30 (+6 Fishing later) | `tools/art/make_pet_eggs.py` (NEW, original, deterministic, like `make_menu_icons.py`): one egg silhouette; shell colour by category (Mining slate blue, Farming wheat gold, Foraging bark green, Combat red, Exploration teal); speckles + rim glow by rarity (quality colours, Mythic = shimmer). 64x64 PNG -> `art/pet-eggs/` + sheet for Skyy |
| Egg world textures | 6 | same tool, one per rarity, mapped on the vanilla egg model's UVs (UNVERIFIED: the model's texture size - read its UV box at build time) |
| Reel 1 portraits | 31 (one per kind) | icon items `Skyy_PetIcon_<Kind>` (MaxStack 1, no Categories / Recipe / Interactions, never obtainable - the SkyyMenu icon-item pattern). Rendered from the vanilla model at BUILD time into the jar with `tools/art/render_blocky.py` (vanilla-derived = generated, never committed). Fallback while missing: the kind's skill tool icon + its name |
| Reel 2 rarity tokens | 6 | icon items `Skyy_PetRarity_<Rarity>` with that Quality: the ItemSlot's `ShowQualityBackground` gives the rarity colour (kit `SUI` itemslot, `#Id.ItemId` set - the proven setter) |

## 2. Pet order per category

### 2.1 Rule (makes the default of row `pets.egg.order.<category>`, a comma list - an owner can reorder)

1. Kind tier = the kind's start rarity in Pet kinds (since 0.3.1 every kind's value is scaled by it, so it IS the value tier).
2. Kinds that may also go in the summon slot (role fighter / mount) before stat-only kinds of the same tier.
3. Home zone, higher first (harder to reach = better).
4. Main stat value, higher first.
5. Pet kinds table order.

Category = the kind's skill in Pet kinds (Mining, Farming, Foraging, Combat, Exploration). A kind in no row (added later) is placed by
the rule and logged once. A switched-off kind (`pets.kinds.off`) leaves the pool; the others keep their order and are re-weighted. A
category with no enabled kind: its eggs cannot hatch (refused, the egg stays).

### 2.2 Default order (values = Lv 100 before rarity, SkyyPets 0.3.1 `KINDS` after `_boost_stats`; recomputed in python)

| Category (pets) | Best -> worst |
|---|---|
| **Mining** (4) | 1 Goat (Unc, Z3: 13.5 Mining Fortune, 7 swing) - 2 Warthog (Unc, Z2: 9.5 Fortune, 20.5 Defense) - 3 Meerkat (Com, Z2: 7) - 4 Mouse (Com, Z1: 7, starter) |
| **Farming** (5) | 1 Rabbit (Com, Z1: 10 Farming Fortune, starter) - 2 Bunny (10) - 3 Chicken (7 + 10 Stamina) - 4 Corgi (7) - 5 Frog (7) |
| **Foraging** (4) | 1 Bear (Rare, Z3: 16.5 Foraging Fortune, 8.5 swing, 8.5 Str) - 2 Turkey (Unc, Z1: 9.5) - 3 Cat (Com, Z1: 7) - 4 Squirrel (Com, Z1: 7, starter) |
| **Exploration** (4) | 1 Camel (Rare, mount, Z2: 50 Stamina) - 2 Horse (Unc, mount, Z2: 7 Speed, 27.5 Stamina) - 3 Gecko (Com, Z2) - 4 Rat (Com, Z1) |
| **Combat** (14) | 1 Ram (Epic, fighter + mount, Z3) - 2 Skrill (Epic, Z4) - 3 Void Eye (Epic, Z4) - 4 Hawk (Epic, Z2) - 5 Mouflon (Epic, Z2) - 6 Void Crawler (Rare, fighter, Z4) - 7 Wolf (Rare, fighter, Z3) - 8 Tusker (Rare, fighter, Z2) - 9 Skeleton Archer (Rare, fighter, Z1) - 10 Skeleton Knight (Rare, fighter, Z1) - 11 Void Larva (Unc, Z4) - 12 Boar (Unc, Z1) - 13 Fox (Unc, Z1) - 14 Dog (Com, Z1, starter) |
| **Fishing** (0) | none yet - no Fishing egg until Fishing pets exist (2.3) |

Flags: every kind fits a category (none left over). **Farming is flat**: all five are Common-tier kinds (best +10 vs worst +7 Fortune),
so a better Farming egg barely matters. Rabbit and Bunny are the same numbers.

### 2.3 Proposed adds (design only; data rows in Pet kinds, numbers from the archetypes - question 4)

| Category | Add (Pets-Roster row, start rarity, zone) | Why |
|---|---|---|
| Farming | Mosshorn (27, Rare, Z1, tameable) -> new #1; Bison (11, Unc, Z1, mount candidate) -> #2 | gives the Farming egg a real top end |
| Mining | Crystal Golem (115, Epic, Z3) -> #1; Molerat (53, Unc, Z2) -> #3 | 4 -> 6, an Epic top |
| Foraging | Moose (31, Rare, Z3) -> #2; Owl (71, Unc, Z1, flying) -> #3 | 4 -> 6 |
| Exploration | Deer (30, Unc, Z1); Antelope (28, Unc, Z2) | 4 -> 6 |
| Fishing (new egg) | Small fish "Bluegill" (79, Com), Crab (40, Unc), Pufferfish (82, Unc), Moray Eel (83, Rare), Hammerhead (86, Epic) | needs a Fishing pet stat SkyyFishing reads (treasure / double catch) - its own round R5 |

## 3. Roll 1 - which pet

Ordered list of n pets (rank 1 = best). Each pet gets weight `R ^ (-x)`, x = 0 for the worst pet of the pool, 1 for the best (x =
position / (pool size - 1)). R = how many times likelier the worst pet is than the best. The SAME R gives the same best : worst spread
in a 4-pet and a 14-pet list (a plain geometric step per rank would make Combat's best pet 1 in 16,000).

| Egg | R (row `pets.egg.ratio.<rarity>`) | Pool (row `pets.egg.pool.<rarity>`) |
|---|---|---|
| Common | 16 | all |
| Uncommon | 8 | all |
| Rare | 4 | all |
| Epic | 2 | all |
| Legendary | 2 | top half = the best floor(n / 2) pets (min 1) - "always above average" |
| Mythic | 0.5 (best twice as likely as the pool's worst) | top half |

Exact weights (python, worst -> best of the pool): n = 4: Common 1 / 0.397 / 0.157 / 0.0625; Uncommon 1 / 0.5 / 0.25 / 0.125; Rare 1 /
0.630 / 0.397 / 0.25; Epic 1 / 0.794 / 0.630 / 0.5; Legendary 1 / 0.5 (2 pets); Mythic 1 / 2.

### 3.1 % per pet (python; rows sum to 100)

| Mining / Foraging / Exploration (4 pets) | Common | Uncommon | Rare | Epic | Legendary | Mythic |
|---|---|---|---|---|---|---|
| 1 Goat / Bear / Camel | 3.9 | 6.7 | 11.0 | 17.1 | 33.3 | 66.7 |
| 2 Warthog / Turkey / Horse | 9.7 | 13.3 | 17.4 | 21.5 | 66.7 | 33.3 |
| 3 Meerkat / Cat / Gecko | 24.5 | 26.7 | 27.7 | 27.1 | 0 | 0 |
| 4 Mouse / Squirrel / Rat | 61.8 | 53.3 | 43.9 | 34.2 | 0 | 0 |

| Farming (5) | Common | Uncommon | Rare | Epic | Legendary | Mythic |
|---|---|---|---|---|---|---|
| 1 Rabbit | 3.2 | 5.5 | 8.9 | 13.7 | 33.3 | 66.7 |
| 2 Bunny | 6.5 | 9.2 | 12.6 | 16.3 | 66.7 | 33.3 |
| 3 Chicken | 12.9 | 15.5 | 17.8 | 19.4 | 0 | 0 |
| 4 Corgi | 25.8 | 26.0 | 25.2 | 23.1 | 0 | 0 |
| 5 Frog | 51.6 | 43.8 | 35.6 | 27.5 | 0 | 0 |

| Combat (14) | Common | Uncommon | Rare | Epic | Legendary | Mythic |
|---|---|---|---|---|---|---|
| 1 Ram | 1.3 | 2.1 | 3.3 | 4.9 | 9.8 | 19.7 |
| 2 Skrill | 1.6 | 2.4 | 3.6 | 5.2 | 11.0 | 17.5 |
| 3 Void Eye | 1.9 | 2.8 | 4.0 | 5.5 | 12.4 | 15.6 |
| 4 Hawk | 2.4 | 3.3 | 4.5 | 5.8 | 13.9 | 13.9 |
| 5 Mouflon | 3.0 | 3.9 | 5.0 | 6.1 | 15.6 | 12.4 |
| 6 Void Crawler | 3.7 | 4.6 | 5.6 | 6.4 | 17.5 | 11.0 |
| 7 Wolf | 4.5 | 5.4 | 6.2 | 6.8 | 19.7 | 9.8 |
| 8 Tusker | 5.6 | 6.3 | 6.9 | 7.2 | 0 | 0 |
| 9 Skeleton Archer | 7.0 | 7.4 | 7.7 | 7.6 | 0 | 0 |
| 10 Skeleton Knight | 8.6 | 8.7 | 8.5 | 8.0 | 0 | 0 |
| 11 Void Larva | 10.7 | 10.2 | 9.5 | 8.4 | 0 | 0 |
| 12 Boar | 13.2 | 12.0 | 10.5 | 8.9 | 0 | 0 |
| 13 Fox | 16.3 | 14.1 | 11.7 | 9.4 | 0 | 0 |
| 14 Dog | 20.2 | 16.5 | 13.0 | 9.9 | 0 | 0 |

Chance of a top-half pet: Common 14 / 10 / 18 % (4-pet / Farming / Combat), Uncommon 20 / 15 / 25, Rare 28 / 22 / 32, Epic 39 / 30 /
41, Legendary + Mythic 100. "High chance of a bad pet, low chance of a good one" holds for Common-Epic; better eggs shift toward the top.

## 4. Roll 2 - the pet's rarity

Weights per 10,000 (row `pets.egg.rarity.<eggRarity>` = `C/U/R/E/L/M`; python: every row sums to 10,000):

| Egg | Common | Uncommon | Rare | Epic | Legendary | Mythic | Rare or better | Legendary or better |
|---|---|---|---|---|---|---|---|---|
| Common | 70 % | 23 % | 6 % | 0.9 % | 0.09 % | 0.01 % | 7 % | 0.1 % |
| Uncommon | 50 % | 35 % | 12 % | 2.7 % | 0.27 % | 0.03 % | 15 % | 0.3 % |
| Rare | 30 % | 40 % | 23 % | 6 % | 0.9 % | 0.1 % | 30 % | 1 % |
| Epic | 10 % | 35 % | 38 % | 14 % | 2.5 % | 0.5 % | 55 % | 3 % |
| Legendary | 0 | 0 | 65 % | 28 % | 6 % | 1 % | 100 % ("never below Rare") | 7 % |
| Mythic | 0 | 0 | 0 | 65 % | 28 % | 7 % | 100 % (never below Epic) | 35 % |

The Server Setup check refuses a Legendary / Mythic row with a Common or Uncommon weight (Skyy's "never below rare" can't be edited
away by accident) and any row summing to 0. Rolls 1 and 2 are independent (a Rabbit can hatch Legendary). A hatched pet starts at
Lv 1, 0 XP, 0 pet rebirths.

## 5. Hatch flow + animation

### 5.1 Flow

| Step | What happens |
|---|---|
| 1. Right-click an egg | opens page `SkyyPetsHatch` (inline, `tools/skyyui.py`, ~760 x 640): egg icon + name, "Hatch it for a random Mining pet", the roll-1 % list for THIS egg (2.2 order) and the roll-2 line, buttons **Hatch**, **Close**, a toggle **Skip animation** (saved per player in the pet record as `hatch.skipAnim`) |
| 2. Hatch (one press) | re-checks on the world thread: the HELD stack (active hotbar slot) is still that egg id with count >= 1; pets on; `profile:busy` false; owned pets < `pets.owned.max` (120) else "Your pet collection is full (120/120). Fuse pets to make room." and nothing moves; category has an enabled kind; not already hatching (per-player map `HATCHING.putIfAbsent(uuid, hid)` + 1 s click guard) |
| 3. Decide + commit | section 5.2 - the pet is saved BEFORE any animation frame |
| 4. Reel 1 (~3 s) | pet strip spins and slows, stops on the pet (5.3) |
| 5. Reel 2 (~3 s) | rarity strip spins and slows, stops on the rarity |
| 6. Result | big portrait, "Bunny" + "Rare" (rarity token slot colour), "Added to your pets (37 / 120)", its bonus at Lv 1 and at max, buttons **Hatch another** (only while the held stack still has that egg), **Open pets** (runs /pets with this page open - never close-then-open), **Close**. One chat line. Legendary / Mythic: a server chat line (row `pets.hatch.announce`: off / legendary / mythic, default legendary) |
| Skip | **Skip** button on both reels, or Esc / closing the page: jumps to the result (or, if the page is gone, sends the chat line at once). A disconnect mid-reel = the chat line at the next join (`hatch.unseen=<hid>` in the record, cleared when shown) |

### 5.2 One atomic, journaled hatch (the egg consumed exactly once, the pet created exactly once)

All in ONE world-thread task (page events arrive through `world.execute`; the engine's player save snapshots on the same thread, so it
cannot land in between - `research/Auction-House-Spec.md` R8 reasoning, VERIFIED there):

1. Roll 1 + roll 2 (`ThreadLocalRandom`), new hatch id `hid` (`PetStore.newId()`).
2. Ledger `hatch-intent <hid> egg=<id> slot=<n> before=<count of that id in all containers> kind=<k> rarity=<r>` (append + flush).
3. Remove ONE egg from that slot (`removeItemStackFromSlot(slot, 1)`, count the slot before and after - must drop by exactly 1, else
   `hatch-abort take` and stop).
4. `PetOps.createR(rec, null, kind, rarity, 1, 0L, 0, "egg:<eggId>:<hid>", "hatch", true)` = the record's io lock, ONE atomic save
   (tmp + rename = the commit) that also writes `eggdebt.<hid>=<eggId>|<before>|<ms>`. A failed save: put the egg back
   (`addItemStack`, counted), `hatch-abort save-refund` (or `hatch-abort refund-failed` + a "contact an admin" line, like SkyyBazaar).
5. Ledger `hatch-done <hid> <petId>`; release `HATCHING`.
6. After the task: forced player save (`Store.copyEntity(ref)` + `Player.saveConfig(world, holder, true)` - the SkyyAuctions 0.1.8 R8
   code, soft-probed; row `pets.hatch.forceSave` true). When its future completes OK -> clear `eggdebt.<hid>` (next save). No probe /
   it throws -> the debt clears 30 s later (the engine's own 10 s player save tick has run).
7. Only now the page starts the reels (the result is already decided and saved).

| Failure | Result |
|---|---|
| Crash before step 4's rename | the player file was not saved since step 3 -> the egg is still there; no pet. Startup: `hatch-intent` without done / abort and no pet with src `...:<hid>` -> `hatch-abort crash` |
| Crash after step 4, before the player save reaches disk | pet saved + the egg comes back (the only dupe window, milliseconds). Startup / next join: an `eggdebt` whose egg count is still >= `before` -> take one egg (counted) + `hatch-reconcile`; count lower -> just clear it |
| Double click / two right-clicks / two pages | `HATCHING` map + the step-2 re-check of the held stack; a stale page's Hatch re-reads the slot |
| Disconnect mid-animation | nothing pending - pet and egg already settled; the reveal line comes at the next join |
| Profile switch | refused while `profile:busy`; the record is the ACTIVE profile's (`tools/PROFILES-CONTRACT.md`) |
| Pets off / kind switched off mid-hatch | refused at step 2; a kind switched off after the roll is still created (kept, gives nothing - the 0.3 rule for owned off kinds) |
| `/petadmin restore` | unchanged; hatch lines are new ledger reasons (`hatch-intent / done / abort / reconcile`), restore ignores them |
| Mythic | `createR` takes rarity 6 (it has no rarity check; `/petadmin give` still refuses 6 - its message "Mythic is for dragons" changes to "Mythic comes from eggs") |

### 5.3 The reels (cheap)

| | Reel 1 (pet) | Reel 2 (rarity) |
|---|---|---|
| Cells shown | 5 in a row (2 left, the centre in a gold frame, 2 right): `ItemSlot` portrait + name label | 5: rarity token `ItemSlot` (quality colour) + rarity name |
| Strip | 24 cells: random pets of the category drawn with THIS egg's weights (looks honest), the result at cell 22; cell 23 a better pet half of the time (a near miss, cosmetic) | the 6 rarities repeated, result centred at the end |
| Frames | 14, one cell per frame, delays 60 60 70 80 90 110 130 160 190 230 280 340 410 500 ms (sum 2.71 s) + 0.4 s hold | 12, delays 70 80 90 110 130 160 200 250 310 380 460 550 ms (2.79 s) + 0.4 s hold |
| One frame | ONE `sendUpdate` with 10 `b.set` (5 `#Id.ItemId` + 5 `#Id.Text`) - only proven setters | same |
| Sound | a soft vanilla tick every 2nd frame, a reveal sound at the stop (`SUI` sounds; `/settings` mute respected) | same |

~26 page updates per hatch, ~6 s. Driven by `HytaleServer.SCHEDULED_EXECUTOR.schedule(...)` -> `world.execute(...)` (the SkyyHud
timer pattern); every frame checks a token (page instance + hid) and stops when the page closed, a skip happened or the player left.
Row `pets.hatch.reelSeconds` (3, scales the delays), `pets.hatch.frames` (14 / 12, 8-24), `pets.hatch.anim` (reel / quick = one update
straight to the result).

**Rule exception, stated:** HANDOFF / AGENT-BRIEF say "never periodic page updates" because PageManager drops clicks while an update is
unacknowledged. Skyy chose the spinning reel, so this ONE page updates itself, only during a reel, at most ~26 times, never from a hover
handler. A dropped Skip click just means click again; Esc always works. UNVERIFIED in game (check C1) - if frames stutter or clicks
die, the default flips to `quick` with no rebuild.

## 6. Sources

### 6.1 Rare drops while doing the skill

SkyySkills calls a NEW bridge `pets:fn:eggroll` `apply(Object[] { UUID, String category, String source, Double fortune, Integer tier })`
-> String egg id or null, on the world thread, from the places that already decide "natural, not placed": `Perks.breakDouble` (ores /
stone), the crop harvest (`HarvestTask`, final stage only), `Sickle.award`, the felled-tree award, and the kill XP award (`MobXp`,
category Combat). Exploration: SkyyPets' own `pets:fn:onxp` when the skill is Exploration (each award is a discovery). SkyyPets rolls,
GIVES the egg (storage-first, inventory full -> dropped at the feet), shows a SkyyHud feed card "Pet egg! Rare Mining Egg" (or chat, by
the Fortune indicator's message switch) and returns the id for SkyySkills' log. Never rolls: placed blocks, offline smelting, shard /
totem production, creative, `Tamed_*` / baby / `Skyy_Pet_*` roles, other mods' summons.

| Source (row) | 1 in N per action | Placeholder actions / h (UNVERIFIED) | Eggs / h |
|---|---|---|---|
| Natural ore / stone (`pets.egg.drop.mining`) | 5,000 | 1,200 | 0.24 |
| Natural log (`.foraging`) | 5,000 | 1,200 | 0.24 |
| Grown crop / sickle swing (`.farming`) | 5,000 | 1,200 | 0.24 |
| Mob kill (`.combat`) | 2,500 | 240 | 0.10 |
| Exploration award (`.exploration`) | 150 | 20 | 0.13 |
| Fish catch (`.fishing`) | 300 | 40 | later (R5) |

**Luck:** chance x (1 + min(Fortune, `pets.egg.drop.fortuneCap` 2.0) x `pets.egg.drop.fortunePct` 25 %) - Fortune = `Perks.fortune`
of that row (0.6 = 60 %), so at most x1.5. A future Pet Luck stat adds through `pets:luck:<uuid>` (Double %, none today).
**Cap:** `pets.egg.drop.capPerHour` 3 eggs per profile per real hour from all drops together (a capped roll is silent).

Egg rarity of a drop (per 10,000; `tier` = the block's material tier from SkyySkills' tier gate, mob zone for kills; 0 = unknown = low):

| Band (row) | Common | Uncommon | Rare | Epic | Legendary | Mythic | Legendary+ PET per drop egg (python) |
|---|---|---|---|---|---|---|---|
| Low, tier < `pets.egg.drop.highTier` 4 (`.rarityLow`) | 75 % | 20 % | 4.5 % | 0.45 % | 0.05 % | 0 | 0.20 % |
| High, tier >= 4 (`.rarityHigh`) | 55 % | 30 % | 12 % | 2.5 % | 0.45 % | 0.05 % | 0.39 % |

### 6.2 Collection rewards (SkyyCollections `item:<id>:<n>` tokens, 0.2.13+, one item per tier)

| Collection tier | Egg (the collection's category: Mining / Foraging / Farming / Combat) |
|---|---|
| III | Common egg |
| V | Uncommon egg |
| Last tier | Rare egg; Epic for the four flagships (Wheat, Oak Log, Cobblestone, Bone Fragments) |

Tier VI keeps the Unique Sigil (no clash: one item token per tier). About 20 collections per category -> ~20 Common + 20 Uncommon + 20
Rare eggs per category over the whole game. Shipped as built-in defaults + a one-time `rewards.properties` update (CollEggMig, the
CollSigMig pattern: only lines still holding the old default, History copy first, change-log line with Undo, marker). Tiers already
reached are paid out once by the existing owed / retried path (question 5). Exploration has no collections (drops, craft, shops only).

### 6.3 Crafting (Common + Uncommon only - Rare and up are never craftable)

| Egg | Recipe (1 `Food_Egg` + ...) | Input base at the Bazaar (python, factor 1) |
|---|---|---|
| Common Mining | 12 Enchanted Cobblestone | ~1,440 |
| Uncommon Mining | 2 Enchanted Iron Ingot | build computes (Iron Ingot is AUTO) |
| Common Foraging | 4 Enchanted Oak Log | ~1,440 |
| Uncommon Foraging | 6 Enchanted Maple Log | ~5,760 |
| Common Farming | 6 Enchanted Wheat | ~1,440 |
| Uncommon Farming | 12 Enchanted Wheat + 12 Enchanted Carrot | ~5,760 |
| Common Combat | 128 Bone Fragments + 16 Light Leather | build computes |
| Uncommon Combat | 2 Enchanted Iron Ingot + 128 Bone Fragments | build computes |
| Common Exploration | 2 Enchanted Oak Log + 6 Enchanted Cobblestone | ~1,440 |
| Uncommon Exploration | 6 Enchanted Oak Log + 2 Enchanted Copper Ingot | build computes |

Bench: the Workbench, own tab "Pet Eggs" (the `skyyench` runtime tab protocol - UNVERIFIED for a second mod; fallback: the Farmingbench
in an existing category). BUILD-TIME (baked into the item JSON). The build asserts Common ~1,000-2,500 and Uncommon ~4,000-9,000 input
value so the tiers stay apart.

### 6.4 Bazaar, merchants, Auction House - and the coin loops

| Egg | Bazaar (market maker) | Roaming merchant | Auction House |
|---|---|---|---|
| Common / Uncommon | yes, **AUTO** = a processed good from its recipe (inputs x (1 + premium 20 %)), Pets tab | no | yes |
| Rare | yes, fixed base 25,000 | no | yes |
| Epic | yes, fixed base 100,000 | no | yes |
| Legendary | **no** | `pet.<id>` rows, Zones 3-5, 600,000 coins, stock 1, at most `merchant.pets.perVisit` 1 egg row per visit with `merchant.pets.chance` 25 % | yes |
| Mythic | no | no | yes (player to player only) |

Loop checks (SkyyBazaar: instant buy = base x factor x 1.1, instant sell = base x factor x 0.9, factor 0.25-4.0, step =
1.1 ^ (base / 10,000)):
- **Craft -> sell:** AUTO price makes sell = 0.9 x 1.2 x inputs = 1.08 x inputs < buy-inputs 1.1 x inputs (the existing 22 % premium
  rule). SkyyBazaar's build loop check must also read the egg recipes from `tools/skyyeggs.py` (today it only reads Assets.zip + the
  Enchanted table) - it fails the build if one pays.
- **Merchant -> Bazaar:** the merchant sells only Legendary, which the Bazaar never buys -> no loop. Any later merchant row for a
  Bazaar-listed egg must be >= 4 x its Bazaar base (the Bazaar pays at most 4.0 x 0.9 = 3.6 x base) - checked at build + in the row check.
  (`research/cloud/Pet-Eggs-v2.md` 3.2 said 3x: too low with the 4.0 factor clamp.)
- **Buying top eggs with coins:** Epic step = 1.1 ^ 10 = 2.6x per egg bought, so the 2nd Epic costs ~2.6x and the 3rd hits the 4.0
  clamp (440,000); the factor halves back every 120 min. Coins can't mint Legendary / Mythic at all.
- **Collections / drops -> sell:** one-time or rate-capped income, and each sale pushes the factor down (Rare step 1.27x).
- **Hatch / fuse:** pets are bound records - nothing goes back to coins.

## 7. Fusing (unchanged, SkyyPets 0.3.0)

4 pets of the same kind + rarity -> 1 of the next rarity (row `pets.fuse.count` 4), up to `pets.fuse.maxRarity` (Legendary). Notes:
- Eggs never fuse and there is no egg combining (an egg upgrade recipe would be a second fusing).
- Hatching feeds fusing: a Common egg gives the bottom pet 52-62 % of the time in the 4-5 pet lists (Dog 20 % in Combat), so
  duplicates of the worst pets pile up -> fuse them.
  Fusing is the steady way up; eggs are the lottery.
- **Mythic only from eggs** (Common egg 0.01 %, Mythic egg 7 %); fusing stops at Legendary unless the row is set to Mythic (question 3).
  A Legendary pet by fusing alone = 4^4 = 256 Commons of one kind; by Common eggs 1 in 1,000 hatches (any pet of the category).
- Mythic pets: bonus x1.5 (0.3.0 Rarity rows) and `pets.cap.scale` already grows the Fortune / swing caps with rarity, so a Mythic
  gathering pet is not cut (Pets-Spec's "no Mythic gathering pet" note is outdated).
- The pets cap (120) is the limit to watch: fusing 4 -> 1 frees 3 slots; hatching is refused (egg kept) when full.

## 8. Build rounds

| # | Round | Mods / files | Size | Notes |
|---|---|---|---|---|
| A0 | Egg art | `tools/art/make_pet_eggs.py`, `art/pet-eggs/` | cloud draws, I review (memory: visuals autonomy) | 30 icons + 6 textures + sheet for Skyy; portraits are build-time renders (R1) |
| R1 | **SkyyPets 0.4.0** eggs + hatching | `tools/pets_0_4_0_patch.py` from 0.3.1, `tools/skyyeggs.py`, `tools/tier_tags.py` (+ test) | **Ultracode** (new system, items that could be lost / duplicated, saved data) + `simplify: 2` | 30 egg items + `Skyy_Pet_Mythic` quality + 31 portrait + 6 token icon items, lang, tier tags, recipes; hatch page + reels + 5.2 journal + startup recovery + eggdebt reconcile + forced save; `pets:fn:eggroll` + `pets:egg:defs` (ids / names / weights for other mods); Exploration drop in `pets:fn:onxp`; `/petadmin egg <player> <category> <rarity> [n]` and `/petadmin hatchodds <category> <rarity> [n]` (prints a 100,000-roll table, no items) - admin rules (`requirePermission` + empty groups); Server Setup > Pets > Eggs rows (section 9); data rows for the 2.3 adds if Skyy says yes |
| R2 | SkyySkills 0.4.44 egg drops | `tools/skills_0_4_44_patch.py` | Lean round + cross-check | one call to `pets:fn:eggroll` at the 5 natural spots (6.1); null-safe, one WARN; no saved data |
| R3 | SkyyBazaar 0.1.14 + SkyyMerchants 0.1.6 | patches for both | Full round (economy) | Bazaar: Pets tab, Common / Uncommon AUTO from `skyyeggs` recipes, Rare / Epic fixed, loop check over the egg recipes; Merchants: Legendary `pet.` rows + `merchant.pets.perVisit` / `.chance`, the >= 4x row check |
| R4 | SkyyCollections 0.2.20 | `tools/collections_0_2_20_patch.py` | Full round (saved data + migration) | default tokens (6.2) + CollEggMig |
| R5 | Fishing eggs (later) | SkyyPets + SkyyFishing | Full round | Fishing pet kinds + a stat SkyyFishing reads (treasure / double catch) + `.fishing` drop |

Order: A0 and R1 together (R1 falls back to the skill-icon reel cells while portraits are missing), then R2-R4 in parallel (all only
need R1's bridge / ids). Deploy R1 alone first so Skyy can test hatching with `/petadmin egg`.

Checks (every round): harness tests - each weight row sums right, the Legendary / Mythic floors, the top-half rule for n = 1..20,
100,000 seeded rolls within 0.5 % of the 3.1 / 4 tables, a crash simulated between every step of 5.2 (no dupe, no loss), double click,
inventory count before / after, the pets cap, Mythic through page / fuse / caps; `python tools/ci/crosscheck.py --jar <new jars>
--baseline`, `python tools/ci/lint.py` 0 fails, `python tools/smoke_test.py`, SkyyBazaar's loop check. In game (C1-C5): reel smooth
and Skip works (C1), an egg drops while mining (`/petadmin` drop rate x100 test row), crafting at the bench, Bazaar buy / sell, a
collection tier pays its egg.

## 9. Server Setup rows (SkyyPets, category Eggs)

`pets.egg.enabled` (on), `pets.egg.ratio.<rarity>` (16 / 8 / 4 / 2 / 2 / 0.5), `pets.egg.pool.<rarity>` (all x4, top half x2),
`pets.egg.rarity.<rarity>` (table 4), `pets.egg.order.<category>` (table 2.2), `pets.hatch.anim` (reel), `pets.hatch.reelSeconds` (3),
`pets.hatch.frames` (14), `pets.hatch.announce` (legendary), `pets.hatch.forceSave` (on), `pets.egg.drop.enabled` (on),
`pets.egg.drop.<mining|foraging|farming|combat|exploration|fishing>` (5000 / 5000 / 5000 / 2500 / 150 / 300), `pets.egg.drop.rarityLow` /
`.rarityHigh` (table 6.1), `pets.egg.drop.highTier` (4), `pets.egg.drop.fortunePct` (25), `pets.egg.drop.fortuneCap` (2), `pets.egg.drop.capPerHour`
(3). Elsewhere: Bazaar prices (SkyyBazaar products), merchant rows (SkyyMerchants), reward lines (SkyyCollections). BUILD-TIME (not
rows): ids, MaxStack, recipes, icons.

## 10. Questions for Skyy (popups; defaults in brackets)

| # | Question | Default |
|---|---|---|
| 1 | Your 10-10 answer had zone eggs ("a Zone 1 mining egg") + species eggs; your new words have category + rarity eggs. Drop the zone part and species eggs? | [yes - category x rarity only; better zones / materials just drop better egg rarities; species eggs parked] |
| 2 | Where can coins buy eggs? | [Bazaar: Common to Epic; Legendary: rare roaming-merchant row (600k) + Auction House; Mythic: Auction House only, never sold by the server] |
| 3 | Mythic pets: only from eggs, or also fuse 4 Legendary -> 1 Mythic? | [only from eggs; fusing stops at Legendary] |
| 4 | Farming eggs have no strong pet (all five are Common-tier). Add Mosshorn + Bison to Farming (and Crystal Golem / Molerat, Moose / Owl, Deer / Antelope to the others) in the eggs round? | [yes, data rows only; Fishing pets + Fishing egg in their own round] |
| 5 | Collection eggs (Common at tier III, Uncommon at V, Rare at the last tier, Epic for Wheat / Oak / Cobble / Bone): also paid for tiers you already reached? | [yes, once] |

## 11. UNVERIFIED (local checks before / during R1)

1. A page that updates itself ~26 times in 6 s: frame pacing, client acks, Skip clicks (C1). Fallback `quick`.
2. `render_blocky.py` on NPC models for the portraits (else skill-icon cells).
3. A second mod adding a Workbench tab through the `skyyench` protocol (else the Farmingbench).
4. The vanilla egg model's texture size / UVs for our 6 textures.
5. Real actions per hour for each skill (every drop rate is linear in them).
6. SkyySkills' material tier per block at the 5 drop spots (else `tier` 0 = the low band).
