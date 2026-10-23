# Secret dragons (D5b) - build spec: Void, Blood, Light, Crystal

Cloud draft, 2026-10-23. Paper only; nothing built, no game files read. Builds on top of SkyyPets 0.4.13 (riding, being built now) as SkyyPets
0.4.14. Read: `research/cloud/Dragon-Pet-Review.md` (sections 3a-3e = the defaults used here), `research/Dragon-Pet-Spec.md`,
`tools/skyyeggs.py` (DRAGON_EGGS), `tools/pets_0_4_11_patch.py` + `tools/pets_0_4_12_patch.py` (DRAGONS table, DRAGON_CHILD, DRAGON_GRAD),
`tools/balance_model.py` (P5_DRAGONS, p5_pet_power). Stat numbers below were run through `tools/balance_model.py` `p5_pet_power` (read only).

## Decisions followed (word for word in `docs/answered/pets.md`)

| Date | Skyy's words (short) | Used for |
|---|---|---|
| 2026-10-18 | "appears in the pet slot, hatches in the hatchery, and only appears when in the summon slot ... (and we need our elemental dragons.)" | the four kinds are normal dragons: pet slot, Hatchery, summon slot |
| R8 (10-02) | "ONE DRAGON PER PROFILE for now" | every source gives ONE egg per profile; a second is refused |
| 2026-10-16 | pet eggs: "hatchery only", Mythic only from eggs | secret eggs hatch in the Hatchery only; not sold, not craftable |
| 2026-10-20 | "just go with the recommended on all of them." | `research/cloud/Dragon-Pet-Review.md` defaults V1 / B1 / L1 / K1 are in force |
| 2026-10-22 | "we already have aures permission for this" | recolours of Aures' art allowed (not needed for the default route) |
| 2026-10-01 (`research/Dragon-Pets-Idea.md` 5) | "also plan Void, Light and Crystal" (+ Blood); "no quest or explanation - players figure them out" | no hint in any menu |

PROJECT-RULES 2 (duplicates): none of the four exists in a pack mod as a pet or mount; EndgameAndQoL / VoidAsylum (own Void dragon boss) stay OFF.

## 1. What ships (SkyyPets 0.4.14)

Four new rows in the 0.4.11 DRAGONS table and in `tools/skyyeggs.py` DRAGON_EGGS (same order in both - the patch asserts it).

| Kind | Egg item id | Egg name | Admin word | Model id (`MODELS`) | Parent / route | Recolour gradient |
|---|---|---|---|---|---|---|
| DragonVoid | `Skyy_PetEgg_Dragon_Void` | Strange Void Egg | void | `Skyy_Dragon_Void` | Parent `Dragon_Void` (vanilla model, UNVERIFIED it loads); FALLBACK: Parent `Dragon_Fire` + dark violet recolour | `Void` (new) |
| DragonBlood | `Skyy_PetEgg_Dragon_Blood` | Crimson Egg | blood | `Skyy_Dragon_Blood` | Parent `Dragon_Fire` + recolour, drop parent particles | `Blood` (new) |
| DragonLight | `Skyy_PetEgg_Dragon_Light` | Radiant Egg | light | `Skyy_Dragon_Light` | Parent `Dragon_Frost` + recolour | `Light` (new) |
| DragonCrystal | `Skyy_PetEgg_Dragon_Crystal` | Crystal Egg | crystal | `Skyy_Dragon_Crystal` | Parent `Dragon_Frost` + recolour (vanilla route, default) | `Crystal` (new) |

Names are plain (no "Dragon" in the egg name: it is a secret; 40-char limit holds). Portraits `Skyy_PetIcon_DragonVoid` ... generated the 0.4.11 way
(`_SA.recolor_icon` of the vanilla Frost icon). Egg item art + icon: `_SA.recolor_icon` / `_SA.recolor` of our Legendary egg art (same recipe as
Fire / Thunder / Air). Gradient tuples (dark -> light, six steps, like `DRAGON_GRAD`):

| Name | Six steps (RGB) |
|---|---|
| Void | (8,4,20) (24,10,52) (52,20,100) (92,36,150) (140,70,200) (214,170,255) |
| Blood | (22,2,4) (60,6,10) (112,12,20) (168,22,32) (216,52,52) (255,150,140) |
| Light | (96,86,56) (160,146,96) (214,200,140) (244,232,176) (255,246,214) (255,255,255) |
| Crystal | (20,40,70) (40,90,130) (80,150,190) (130,200,226) (190,236,248) (240,252,255) |

Rarity, hatch time, stages, size growth, bite, ride: the existing dragon rules unchanged (start Rare, never below Rare, 0/0/6000/3000/900/100,
3600 s, stages Lv 4 / 7 / 10, +0.6 % a level, ride from the ride level in 0.4.13). Pet fusing, egg fuse, craft: never (same as the other dragons).

### 1.1 Stats and the signature perk (sidegrade, same pet budget)

Lv 100 stats before the rarity factor; P5 pet budget at Rare = 1.546 (+-5 % = 1.51 - 1.58). No Wynn element (the five elements stay Earth /
Thunder / Water / Fire / Air), so no `f<element>` damage line; the perk replaces it. Combat skill, start rarity Rare, role fighter.

| Kind | Stats (Lv 100, before rarity) | `p5_pet_power` | Perk (row, default) |
|---|---|---|---|
| DragonVoid | str:27, cd:26, cc:6 | 1.528 | `pets.dragon.void.pierce` 5 %: bites ignore 5 % of the target's Defence (UNVERIFIED hook) |
| DragonBlood | str:30, cd:25, health:7 | 1.516 | `pets.dragon.blood.steal` 4 %: of the bite damage heals the owner |
| DragonLight | mp:28, health:5, def:6 | 1.556 | `pets.dragon.light.heal` 3 %: of the owner's max Health healed to the owner every 10 s while it is summoned and the owner is hurt |
| DragonCrystal | def:17, health:7, str:14 | 1.549 | `pets.dragon.crystal.reflect` 6 %: of damage that hits the owner is reflected to the attacker |

Perk sizes are tiny on purpose; if a perk turns out to matter, lower it, do not raise stats (four-power-sources rule: pets are one of four).
Bite share (`pets.dragon.fight.share`) per kind: starting values Void 24, Blood 26, Light 18 (caster), Crystal 20 - the builder REFITS them in
`tools/balance_model.py` (`P5_DRAGONS`, `P5_DRAGON_SHARE`) so a summoned dragon at Lv 100 Rare is on the budget and never more than 5 % above the
pet-slot version (the 0.4.12 patch asserts this and stops otherwise). Put the four kinds into `P5_DRAGONS` first, in the same patch.

## 2. One door for every source: `pets:fn:giveSecretEgg`

All four sources call ONE bridge function in SkyyPets (plain java.lang types over `skyy.bridge`, PROJECT-RULES 4):

| Part | Rule |
|---|---|
| Name / args | `pets:fn:giveSecretEgg` (Object[] { String profileKey or player uuid, String word ("void" / "blood" / "light" / "crystal"), String sourceTag }) -> String ("OK", "HAS_DRAGON", "HAS_EGG", "OFF", "BAD_WORD", "BUSY") |
| Refuses | the profile already owns a dragon (any kind) or has a dragon egg in the Hatchery or inventory (R8); `pets.dragon.secret` is off; profile busy (journal lock) |
| Gives | one egg item through the existing journaled give path (inventory, else the mail/stash the pets give path uses; never dropped) and writes `dragonSecretGiven:<word>` on the profile so a second source cannot give a second one |
| Message | one line to the player: the item's own name only ("You found a Strange Void Egg.") - no hint where it came from |
| Log | one line to the server log with `sourceTag` (for admins; never shown to players) |
| Source gating | a source mod calls it only after its own condition; a missing SkyyPets = the source does nothing (no error) |

Server Setup (Server Setup > Pets > Dragons, `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`): `pets.dragon.secret` (bool, default ON - "no dev
gates", finished features default on), `pets.dragon.secret.rates` text `void=30,blood=20` (per 10,000 per roll; see section 3), the four perk
rows above, `pets.dragon.eggs` extended (existing row; add the four pairs so the Hatchery lists them after the other eggs). All live.

Hatchery list: the four eggs appear only when the player OWNS one (no empty "?" rows; Skyy: no hint). The pets list shows the dragon like any other.

## 3. Egg sources (defaults of `research/cloud/Dragon-Pet-Review.md` section 3; each in the mod that owns the trigger)

| Kind | Source (default) | Mod + row | Rate / rule | Notes |
|---|---|---|---|---|
| Void | rare drop from Void-flavoured mobs and Void fishing | SkyyMobs drop row (mob ids UNVERIFIED: the Void slug / Void mobs) + SkyyFishing catch row (Void fish, Fishing Bench) | 0.3 % (30 per 10,000) per kill / per Void catch, via `pets:fn:giveSecretEgg` | one roll per kill, never in a loot bag, never on the Auction House "drop" lists |
| Blood | very rare drop from Zone 4 / 5 elite or boss kills made at NIGHT with a "Heart" item in the bag | SkyyMobs night check + a Heart item = an existing boss material (UNVERIFIED which) | 0.2 % (20 per 10,000) per qualifying kill | Heart is not consumed; night = server world time (UNVERIFIED API) |
| Light | beat all four zone guardians (Zone 1-4 bosses) without dying in between | SkyyMobs: per-profile flag per guardian, all cleared on death; the 4th kill with 4 of 4 flags gives the egg once | 100 % once (then `dragonSecretGiven`) | a death anywhere clears the flags; party kills count for each participant |
| Crystal | complete the Crystal collection (all eight crystal colours, `Ingredient_Crystal_*`) at a high tier | SkyyCollections: one tier reward row = `pets:fn:giveSecretEgg` | once | UNVERIFIED reward hook and tier |

No shop, no Bazaar, no merchant, not craftable, not in a quest log. The egg is an item, so trading it is the normal item rule (auction ok); the
buyer's one-dragon rule still applies. Not-tradeable list: leave off (Skyy's pet rules allow egg trade).

## 4. Build split (builders; Opus for code, no commits/deploys by agents)

| Round | Mod | Version | Change |
|---|---|---|---|
| D5b-1 | SkyyPets | 0.4.14 (derive from the 0.4.13 pin with `tools/pets_0_4_14_patch.py`; edit the patch, never the generated script) | 4 kinds, 4 eggs, 4 models, 4 portraits, gradients, perks, `pets:fn:giveSecretEgg`, rows, harness |
| D5b-2 | SkyyMobs | next after the SET pin | Void rare drop, Blood night rule, Light flags (3 small systems) |
| D5b-3 | SkyyFishing | next after the SET pin | Void catch row |
| D5b-4 | SkyyCollections | next after the SET pin | Crystal reward row |
| tools | `tools/skyyeggs.py`, `tools/balance_model.py` | - | DRAGON_EGGS 5 -> 9 (and the `_dragon_checks` count assert 5 -> 9), `P5_DRAGONS`, `P5_DRAGON_SHARE`, `tools/tier_tags.py` rows for the 4 kinds + eggs (Legendary tag like the other dragon eggs) |

Run D5b-1 first, then D5b-2..4 in one cheap lean round each (each only calls the bridge). Full round for D5b-1 (saved data: new profile key; items
that could be duplicated). Do not touch 0.4.13 riding code; the new models must carry the same attachment set / mount anchor as the Fire / Frost
children (copy `DRAGON_CHILD` handling; add `"Skyy_Dragon_Void": ("Dragon_Void", "Void", False)` etc.).

## 5. Harness (`SkyyPets/test_skyypets_0.4.14.py`, bare JVM, `-Xverify:all`, then all jars in one JVM)

| # | Check |
|---|---|
| 1 | DRAGON_EGGS has 9 ids, unique, none parse as a category egg; kinds start with "Dragon"; names <= 40 chars |
| 2 | `[d[0] for d in DRAGONS] == [e[1] for e in DRAGON_EGGS]` (order) |
| 3 | `balance_model.p5_dragon_rows()` all pass for the 9 kinds (budget +-5 %, never above pet slot by > 5 %) |
| 4 | Each new child model: Parent id set, texture size equals the parent's, gradient has 6 steps |
| 5 | `pets:fn:giveSecretEgg`: OK once; second call HAS_DRAGON; with an egg in the Hatchery HAS_EGG; `pets.dragon.secret` off -> OFF; bad word -> BAD_WORD |
| 6 | Journaled give: crash between journal and give leaves ONE egg after recovery (no dupe, no loss) |
| 7 | Hatchery list: a secret egg shows only for an owner of one; ordering after the other eggs |
| 8 | Perk math: Blood steal = 4 % of the bite, never above the owner's max Health; Crystal reflect never kills the attacker above its Lv rule (SkyyMobs rank), Light heal capped at max Health |
| 9 | `python tools/ci/langdup.py` (one writer per lang key) and `python tools/ci/lint.py` 0 fails; crosscheck `--baseline` |
| 10 | Pet rebirth / restore / `/petadmin give` cannot create a second dragon (existing `PetOps.createR` rule covers the new kinds) |

## 6. In-game test steps (for `TEST-CHECKLIST.md` after the deploy)

1. `/petadmin egg <you> dragon void` (and blood / light / crystal in turn, fresh profile each): the egg is in the inventory with the right name and icon; place it in the Hatchery; after the hatch time a Rare-or-better dragon appears in the pet slot.
2. Give a second egg while owning a dragon: refused, the egg stays where it was.
3. Summon each dragon: it looks right (colour, size by stage), fights (Weakling/Smalling bites 40/60 %), the perk line shows in the pet card tooltip with the right colour code (Style Guide 15).
4. Ride from the ride level (0.4.13): each new model mounts and flies like Fire / Frost (anchor correct, saddle shown).
5. Sources: kill Void mobs / fish Void fish ~100 times (or set `pets.dragon.secret.rates` to `void=10000` to prove the path), Blood at night in Zone 4+ with the Heart, finish the four guardians without dying (then die once and check the flags reset), fill the Crystal collection (admin tier set).
6. `pets.dragon.secret` off: no new secret egg appears from any source; existing ones keep working.
7. Void edge: a summoned secret dragon dropped into the void returns to the slot (existing D2 rule).

## Questions for Skyy (each with a default)

| # | Question | Default |
|---|---|---|
| 1 | Sources: Void from Void mobs / Void fishing, Blood from night elites with a Heart, Light from a no-death four-guardian run, Crystal from the Crystal collection? | [yes, V1 / B1 / L1 / K1] |
| 2 | Rates 0.3 % / 0.2 %, one per profile, editable in Server Setup? | [yes] |
| 3 | Crystal model: vanilla Frost recolour now (works without Nestkeeper), Aures' Tundra recolour later? | [vanilla recolour] |
| 4 | Secret dragons carry a small signature perk (steal / heal / reflect / pierce) instead of an element? Or give them an element line too? | [perk only, no sixth element] |
| 5 | Show secret dragons in the pet card as normal dragons (no "secret" tag)? | [yes, no tag] |
| 6 | Who are the "four zone guardians" for Light? | [the Zone 1-4 final bosses in the SkyyMobs rank list] |
| 7 | Let a second profile on the same account earn its own secret egg (R8 is per profile)? | [yes, per profile] |

## For the local session (UNVERIFIED - needs game files / HytaleServer.jar / Assets.zip)

| # | Check |
|---|---|
| 1 | Vanilla `Dragon_Void` model (`Server/Models/Elemental/Dragon_Void.json`) loads under `Skyy_Pet_Dragon`; same bone / animation names and mount anchor as Fire / Frost (Review C8); else use the Fire-parent fallback |
| 2 | Real ids: Void mobs / Void fish loot tables in SkyyMobs / SkyyFishing; the Heart item; the 4 zone guardians' role ids and SkyyMobs rank list |
| 3 | A night read from the world time on the server thread; SkyyCollections reward hook + whether the crystal colours match `Ingredient_Crystal_*` |
| 4 | A bite-damage hook for steal / pierce in PetFight; a damage-taken hook for reflect; a safe heal-owner call |
| 5 | The 0.4.13 riding code: does `DRAGON_CHILD` still hold the attachment set, and does the pinned saddle attach to the new child models |
| 6 | Hatchery page: how it lists owned eggs (so an unowned secret egg stays hidden) |
| 7 | `tools/tier_tags.py` table shape for the four new kinds and eggs |
