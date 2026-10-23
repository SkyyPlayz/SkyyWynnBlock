# Dragon pet - spec review (what is still open)

Cloud review, 2026-10-23. Paper only; nothing built, no game files read. Read: `research/Dragon-Pet-Spec.md`, `research/Dragon-Pets-Idea.md`,
`research/cloud/Pet-Core-Spec.md`, `research/cloud/Dragon-Quest-Spec.md`, `research/cloud/Pet-Sources.md`, `docs/answered/pets.md`, the dragon
lines of `docs/log/2026-10.md`, `tools/pets_0_4_11_patch.py` (header only), `tools/skyyeggs.py` (DRAGON_EGGS), TEST-CHECKLIST sections 235 / 236
(`docs/tests/2026-10.md`). State: D0 + D1 + D6 LIVE (SkyyPets 0.4.12, SkyyMobs 0.1.18); D3 riding is being built; D5 secrets open.

## Decisions followed (`docs/answered/pets.md`, word for word there)

| Date | Skyy's words (short) | Used for |
|---|---|---|
| 2026-10-18 | "appears in the pet slot, hatches in the hatchery, and only appears when in the summon slot ... (and we need our elemental dragons.)" | slots, Hatchery, element dragons |
| R8 (10-02) | "ONE DRAGON PER PROFILE for now" | every second source below must hand out ONE egg only |
| R8 | "dragons follow the pet rules ... can be flown from Lv 10" | stages, ride level |
| 2026-10-22 | "we already have aures permission for this" (recolour element dragons; keep both taming systems) | recolours of Aures' art are allowed now |
| 2026-10-16 | "aures already gave the okay." (summon through our slot by id) | Plain / Tundra models by id |
| 2026-10-06 | "make the inventory icon look like the dragons in the mod were using." | dragon icon style |
| 2026-10-16 | Pet-egg popups: "hatchery only", Bazaar C-E / merchants L, "Mythic only from eggs" | egg rules for the secret eggs |
| 2026-10-20 | "just go with the recommended on all of them." | spec section 11 defaults are in force |
| `research/Dragon-Pets-Idea.md` 5 | Skyy 2026-10-01: "also plan Void, Light and Crystal" as secret elements (+ Blood) | secret set; "no quest or explanation - players figure them out" |

PROJECT-RULES 2 also applies: check for an existing mod first; no duplicates between mods (best version only).

## 1. Status of each spec round (what shipped vs `research/Dragon-Pet-Spec.md`)

| Round | Spec says | State |
|---|---|---|
| D0 / D2 + D5 part | 5 kinds, eggs, Hatchery, stages, void return | LIVE (Pets 0.4.11): Plain, Tundra, Fire (vanilla), Storm, Sky (build-time recolours of vanilla Fire / Frost) |
| D1 fighting | bite + breath, flat HP, Follow / Defend | LIVE (0.4.12): bite only; HP and a few numbers differ (section 2) |
| D6 boss eggs | Fire / Frost bosses drop Fire / Thunder / Air eggs | LIVE (Mobs 0.1.18), 1 %, capped by the live Mythic-bag row and 12 % |
| D3 riding + flight | Skyy_Dragon_Glide presets or code flight, riderless fly-follow | BUILDING NOW |
| D4 art | element textures + icons + egg icons | PARTLY: textures generated at build time; icons are placeholders (section 4) |
| D5 secrets | Void / Blood / Light / Crystal | OPEN: no kind, no egg, no source (section 3) |
| Dragon Upgrade Stones (R9) | own stones for dragons | NOT SPECCED in `research/Dragon-Pet-Spec.md`; only in `research/cloud/Dragon-Quest-Spec.md` section 5 |

## 2. Contradictions: spec vs what shipped (and between specs)

| # | Where | Conflict | Suggested fix |
|---|---|---|---|
| C1 | `research/Dragon-Pet-Spec.md` section 4 | HP flat 40 / 80 / 140 / 220 per stage. Shipped: 40 / 60 / 80 / 100 % of the owner's max Health x (1 + Lv/100) (docs/log 10-23 06:15). Spec stage-damage 0.4 / 0.6 / 0.8 / 1.0 matches | Update the spec table to the shipped %; the reason (flat pools one-shot in Zone 3+) is sound |
| C2 | `research/Dragon-Pet-Spec.md` section 8 (a) | Says recolouring Aures' textures is "not the plan of record" and licence-blocked. Skyy 2026-10-22: permission already held | Mark (a) GRANTED. This reopens the Aures-model route for new elements (section 3: Crystal / Light) |
| C3 | `research/Dragon-Pet-Spec.md` section 8 | Aures message Q2 (use `Dragon_Breath` by id) has no recorded answer; 10-22 line covers recolours only | Breath stays OUR interaction until Skyy confirms; see Questions |
| C4 | `research/cloud/Dragon-Quest-Spec.md` | Whole spec assumes ONE egg from the Zone 5 fight, element CHOSEN by quest, hatchling always Mythic, Water = recoloured Frost dragon, growth Lv 1 / 10 / 30 / 60 / 100. Shipped: element fixed by the egg, Rare+ (Mythic 1 %), Water = Aures' Tundra, stages Lv 4 / 7 / 10 | Mark the quest spec SUPERSEDED for model / stage / rarity; keep only its quest-line idea for Earth + Water (section 3b) |
| C5 | `research/cloud/Dragon-Quest-Spec.md` section 3 | Secret triggers are written for a "chosen element" egg (Heart at D3, etc.) - no longer fits eggs that are items | Rebuilt as egg sources in section 3 |
| C6 | `research/Dragon-Pet-Spec.md` section 8 table | "Water = Tundra (Aures)"; but boss map shipped: Dragon_Frost drops only Air. So Earth + Water eggs exist only as wild Nestkeeper nests | Fine, but write it down (Pet-Sources has no Earth / Water egg line) |
| C7 | `tools/skyyeggs.py` | Egg items are Legendary-tier tagged but hatch Rare 60 % / Epic 30 % / Legendary 9 % / Mythic 1 %. A "Legendary egg" mostly giving Rare may read wrong | Flavor text: "Hatches a Rare or better dragon". UNVERIFIED how the tooltip reads in game |
| C8 | `research/Dragon-Pet-Spec.md` section 8 | Void listed as "vanilla `Dragon_Void` by id" - but `research/Beta-Bugs-Triage-2026-10-17.md` line 199: vanilla has the Void dragon MODEL but no NPC role; real Void Dragon roles live only in EndgameAndQoL / VoidAsylum (both disabled) | Void = model only under our Skyy_Pet_Dragon role (fine for a pet). Do not enable those mods just for this (no duplicates) |
| C9 | `research/Dragon-Pet-Spec.md` section 6 vs `research/cloud/Dragon-Quest-Spec.md` section 4 | Spec: rider falls into the void, no protection (10-07 rule). Quest spec: "dragon catches you over void / lava" | Spec wins (newer, matches the lock). Quest-spec line is void |
| C10 | `research/cloud/Pet-Sources.md` line 22 | "never above Legendary, never for dragons" for bumped eggs - consistent with 0.4.12; but its dragon row (Z5 quest only) is stale | Add the shipped boss-drop source |

## 3. D5 secret dragons - egg sources (none exists yet)

Rules every option obeys: the egg is an item `Skyy_PetEgg_Dragon_<Element>` (build-time id, added to `tools/skyyeggs.py` DRAGON_EGGS); hatches only
in the Hatchery (R9 "hatchery only"); ONE dragon per profile (R8) so a duplicate egg is refused and stays in the inventory; no shop sells it (Pet-Sources:
no NPC sells eggs; Bazaar never, Auction House ok as an item); not craftable; no hint in any menu, quest tracker or egg list (Skyy: "no quest or
explanation - players figure them out", only lore books / odd NPC lines); a Server Setup row `pets.dragon.secret` (on) hides them for owners who do not want them.
Balance: sidegrade, same pet budget as the other elements, one signature perk. Model route per kind is in section 3e.

### 3a. Void dragon (element Void)

| Opt | Source | Fit | Cost |
|---|---|---|---|
| V1 DEFAULT | Rare drop (about 0.3 %) from the Void-flavoured content already in the pack: the Void slug / Void mob rare spawns and Void fishing (Fishing Bench Void fish, deploy 10-16). Egg appears as "Strange Void Egg" with no tier text beyond the tag | matches the setting (Isles of the Void), no new world content, discoverable by accident | SkyyMobs drop row + SkyyFishing catch row |
| V2 | Reward for the Receipt / "Paid in Full" end of the main story (`research/Isles-of-the-Void-Lore.md`): "the Void is legally your home" gives a Void Egg | story tie-in | needs the story chain built first; far off |
| V3 | Hatch-in-place idea from `research/cloud/Dragon-Quest-Spec.md` section 3: any dragon egg + a Void Fragment stack at the Void edge of your starter shard re-writes the element to Void | cute; but breaks "egg fixes the element" and lets players spend a boss egg on it | rejected by default |

### 3b. Blood dragon (element Blood, life steal)

| Opt | Source | Fit | Cost |
|---|---|---|---|
| B1 DEFAULT | Very rare drop (0.2 %) from the Zone 4 / 5 elite or boss kills made at NIGHT, only when you kill with a Heart-type item in the bag (the Quest-Spec "Heart" idea, simplified to a drop with a night condition) | keeps Skyy's "darkest egg" feel; no menu hint | SkyyMobs night check; Heart item = an existing boss material or a new Misc item |
| B2 | Slayer reward: finishing the top tier of a blood-themed Slayer (`research/cloud/Slayers-Spec.md`) rolls the egg | fits Slayer grind | Slayers not built |
| B3 | Rare drop from the Fire dragon bosses next to the Fire / Thunder egg (a third roll, 0.1 %) | zero new systems, same code as D6 | too easy to find; no secret |

### 3c. Light dragon (element Light, heals you)

| Opt | Source | Fit | Cost |
|---|---|---|---|
| L1 DEFAULT | A no-death run: beat all four zone guardians without dying (a per-profile flag per boss, reset on death) gives a "Light Shard" ; 8 shards are not needed - one flagged full run drops the Light egg once | rewards skill (Quest-Spec idea) | needs a per-profile flag store; no new world content |
| L2 | A hidden shrine in the Zone 1 temple vault: ring a bell at dawn (daytime-only chest) | explorer reward | needs worldgen placement (SkyyWorldGen), UNVERIFIED engine time-of-day check |
| L3 | Rare drop from sunlit mobs (bees, fireflies) during day | easy | feels random, off-theme |

### 3d. Crystal dragon (element Crystal, reflect)

| Opt | Source | Fit | Cost |
|---|---|---|---|
| K1 DEFAULT | SkyyCollections tie-in: complete the Crystal collection (all eight crystal colours, `research/Collections-Spec.md` row `Ingredient_Crystal_*`) at a high tier and the egg is mailed once as the collection reward | uses an existing, discoverable-but-hidden reward; no new mob | one collection reward row in SkyyCollections |
| K2 | Rare drop (0.5 %) from crystal golems / frost-sand skeleton mages (the same mobs that drop crystal shards) | pure drop, simple | grind-only |
| K3 | Combine 8 crystal colours at the Alchemy / Farmer's bench into a "Crystal Egg" | craftable = breaks "never craftable" | rejected |

### 3e. Model + icon route per secret (no duplicates, vanilla first)

| Kind | Model (cheapest first) | Why |
|---|---|---|
| Void | vanilla `Dragon_Void` model by id (role does not exist - model is enough, UNVERIFIED that it loads under `Skyy_Pet_Dragon` and has the same bone names) | free, already the best Void look |
| Blood | build-time recolour (red / black) of vanilla `Dragon_Fire` texture | same recipe as Storm in `tools/pets_0_4_11_patch.py` |
| Light | build-time recolour (white / gold) of vanilla `Dragon_Frost` texture | same recipe as Sky |
| Crystal | recolour of Aures' Tundra or Plain textures (NOW ALLOWED, C2) = 4 REAL growth stages, or a vanilla recolour with scale-only growth | Aures route is nicer but adds a pack dependency; vanilla route works without Nestkeeper loaded |

Duplicate check (PROJECT-RULES 2): none of Void / Blood / Light / Crystal exists in a pack mod as a pet or mount. DarkMatter Mounts has Fire / Frost
only and is not packed. EndgameAndQoL / VoidAsylum bring a Void dragon boss but are OFF - keep them off so we do not own two Void dragons.

## 4. Blocked on Aures (the pet artist) - and what is NOT blocked

Aures (BlackAures) = author of Dragon Nestkeeper. Permission held: summon by id (10-16), recolours (10-22), keep both taming systems. NOT answered:

| # | Ask | Blocks | Default if no answer |
|---|---|---|---|
| A1 | May our pet dragon call their `Dragon_Breath` interaction by id? (Spec message Q2) | Flyling breath attack | build OUR own breath with vanilla particles (spec 4) - not blocked |
| A2 | May the inventory / egg icon be RENDERED from their dragon model? (`research/cloud/pet-art/README.md` line 51; pets.md 10-06) | proper dragon icons | keep original icons / vanilla-Frost recolours until yes |
| A3 | Credit line + NOTICE wording for recoloured textures (spec "credited to you") | shipping a Crystal / Plain recolour | credit in `PACK.md` + the Dragon tab |
| A4 | Their wild Zone 1 adult dragons are too strong? (`OPEN-QUESTIONS.md` Nestkeeper line - this is Skyy's feel test, not Aures) | nothing | SkyyMobs level rule by id, no Aures needed |

Nothing in D3 riding, D5 secrets via vanilla models, or boss egg drops waits on Aures. Only A2 (render icons) and a Crystal-from-Tundra route do.

## 5. (b) Own-model art list (what must be drawn if Quirk/Cobb do proper models)

Spec rule (`research/Dragon-Pet-Spec.md` section 8 (b)): one rig = the VANILLA dragon rig so vanilla animations are reused and nothing of Aures' is traced.
Current state: nothing of this exists yet; textures are recolours of vanilla. List for a later art round (private art stays outside git until generated into jars).

| # | Asset | Count | Notes |
|---|---|---|---|
| 1 | Dragon mesh fitting the vanilla `Dragon_Fire` bone names | 1 shared (or 1 per element) | 4 growth stages by scale; young head / horn attachments (2-3) so Weakling reads as a baby |
| 2 | Texture 64 or 128 px (vanilla density) | 1 per element: Earth, Thunder, Water, Fire, Air + Void, Blood, Light, Crystal = 9 | Earth / Water already served by Aures' art; own versions only if wanted |
| 3 | Saddle attachment | 1 | shown from the ride level (D3) |
| 4 | New animations | Greet, Happy (F = pet it) | Idle, Walk, Run, Fly, Fly_Idle, Glide, Jump, Fall, Bite, Roar, Hurt, Sleep reused from vanilla |
| 5 | Inventory icon 64 px | 9 (one per element, original, in the Nestkeeper dragon style per pets.md 10-06) | current icons = recolours of the vanilla Frost icon (0.4.11 note, fixer item 6); concept: `research/cloud/pet-art/icon-dragon-128-v2.png` |
| 6 | Dragon egg item model + texture | 9 (our round egg model, element colour) | NEXT list in `RESUME.md` says "dragon egg icon art"; art dir `art/pet-eggs/` only has the Common set |
| 7 | Egg icon 64 px | 9 | follow `art/pet-eggs/README.md` and skill skywynn-art |
| 8 | Breath particle / projectile | 1 per element | optional; vanilla particles tinted first |
| 9 | Pet card element chip + secret "?" hint art | optional | no hint wanted for secrets, so none |

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Secret sources: Void from Void-fishing / Void mob rare drop, Blood from night elite kills, Light from a no-death four-guardian run, Crystal from the Crystal collection reward? | [yes, V1 / B1 / L1 / K1] |
| 2 | Secret egg drop rates (0.2 - 0.5 %, one per profile) and an editable Server Setup row each? | [yes, rows in Server Setup > Pets > Dragons] |
| 3 | Crystal on Aures' Tundra recolour (4 real stages, needs Nestkeeper) or on a vanilla recolour (works without it)? | [vanilla recolour, no pack dependency] |
| 4 | Ask Aures for: breath by id, rendering icons from their model, credit wording? Or skip and use our own? | [send one short message for A2 + A3; build our own breath] |
| 5 | Earth + Water: only wild Nestkeeper nests, or also a Zone 5 quest egg (the old Dragon-Quest idea)? | [nests only until Zone 5 exists] |
| 6 | Mark `research/cloud/Dragon-Quest-Spec.md` SUPERSEDED (kept for the Zone 5 quest-line and mate quest ideas only)? | [yes] |
| 7 | Dragon Upgrade Stones (R9): spec them now or after riding ships? | [after D3 riding is tested] |
| 8 | Egg tooltip: "Legendary Dragon Egg" but it hatches Rare 60 %? Change the tag or keep? | [keep the tag, add "hatches Rare or better"] |

## For the local session (UNVERIFIED - needs game files / Assets.zip / HytaleServer.jar)

| # | Check |
|---|---|
| 1 | Vanilla `Dragon_Void` model (`Server/Models/Elemental/Dragon_Void.json`) loads under `Skyy_Pet_Dragon`; same bone / animation names as Fire / Frost; mount anchor row |
| 2 | Whether a Void fish / Void mob rare-drop hook exists in SkyyFishing / SkyyMobs (names of the existing loot tables) |
| 3 | A time-of-day (night) read on the server for the Blood condition; per-profile flag store for the Light run |
| 4 | SkyyCollections reward hook for a one-time item mail (Crystal) and whether the Crystal collection id list matches `Ingredient_Crystal_*` |
| 5 | The 0.4.12 egg tooltip text and tier tag for `Skyy_PetEgg_Dragon_*` (C7); egg icon/model files actually used for Fire / Thunder / Air eggs |
| 6 | Aures' texture layout (so a Crystal recolour of Tundra can be generated by `tools/skyyart.py` without copying files) |
| 7 | `docs/answered/pets.md` 2026-10-22 wording: confirm "recolour" permission also covers a recoloured ICON render (A2) |
