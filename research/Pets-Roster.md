# Pets roster (every vanilla creature as a pet)

Plan, 2026-10-08. Nothing built. Follows Skyy's locks in `docs/answered/pets.md` (2026-10-08: "a pet for every nutral mob ... and a lot of
the enemys too"; "3, mix them"; "no Kweebecs, or Trorks"). Extends `research/cloud/Pets-Spec.md` (launch list, rarity, XP, slots) and
`research/cloud/Pet-Sources.md` (zones, eggs, bonding). Read from the real game files (Assets.zip `Server/Models`, `Server/NPC/Roles`,
`Common/NPC`; HytaleServer.jar bytecode). Nothing vanilla is copied: pets use the vanilla model **by id at runtime**.

## 0. Short version

- Assets.zip has **187 creature folders** under `Common/NPC/` and **~300 creature model ids** in `Server/Models` (many are colour /
  faction / element variants of one rig).
- They group into **132 families**. **111 families become pets** (208 model ids). **14 families** are a question for Skyy (humanoid races and
  a few odd ones; default "no" except Grooble). **7 are no**: bosses, dragons (dragon tier), and - Skyy's call - every Kweebec and Trork kind.
- One pet per family; the other looks of a family (Burnt / Frost / Sand Skeleton, 7 small birds, 12 small fish ...) are **skins** of that
  pet. That keeps it near ~110 pets, not 200+.
- **Scale works:** the engine spawns an NPC with any model at any scale and keeps it after a save (VERIFIED in the jar, section 2).
- **Mounts:** 3 vanilla mounts (Horse, Camel, Ram) + 18 candidates we can make rideable with our own role (section 4).
- **Chibi list** for Quirk: Skeleton first (ART-RESUME item 16), then Fox, Wolf, Void Eye, Rat ... (section 1.3).

## 1. Roster

### 1.1 How to read the table

- **Model ids**: the `Server/Models` asset id(s) of the family; the folder is under `Common/NPC/`. First id = the default look, the rest =
  skins.
- **Vanilla roles**: `Server/NPC/Roles` files whose Appearance is that model (Tamed_* = the vanilla tamed version).
- **Attitude** (from the role's template): passive = flees / ignores (birds, fish, critters); neutral = fights back if hit
  (Template_Animal_Neutral); tameable = livestock with a vanilla `IsTameable` + `TameRoleChange` (the Tamed role is "Revered"); hostile =
  attacks players (Template_Predator, Flying/Swimming_Aggressive, Template_Intelligent default); no role = a model nothing spawns.
- **Real h** = hitbox height (blocks) x the middle of the model's vanilla MinScale/MaxScale. For reference: Fox 1.10, Wolf ~1.36, player 1.85.
- **Pet scale -> h**: our scale factor and the pet's height. Rule of thumb used: critters 0.7-1.0x; medium beasts so they sit near Fox
  height (1.0-1.2); big humanoids / undead Fox-to-Wolf size (Skeleton 0.6x = 1.08, Fox size, as Skyy asked); huge creatures shrink most
  (Rex 0.3x, Whale 0.2x). Wide / flat creatures (Eye, Slug, Spider, Crab, sharks) are scaled on width so they are about 1 block wide.
  Every scale is a Server Setup row (`pets.<pet>.scale`).
- **Pet?** yes / yes (flying) / water pet / mount pet / ASK [default] / no.
- **Mount?** YES vanilla = rideable today; candidate (size) = could be rideable with our own role (section 4); size kept at 1.0x or more.
- **Baby** = the vanilla baby model of that family (stays as it is, Skyy).
- **Chibi** = Quirk's priority (1 = first). Rows with the same number share one chibi (one rig + skins).
- **Zone / Start rarity** = proposal for section 3 (zones Z1 Emerald Wilds, Z2 Howling Sands, Z3 Whisperfrost, Z4 Devastated Lands,
  Z5 dinosaur caves; "Fishing" = fishing treasure). Zones are by the creature's look / biome name, UNVERIFIED against vanilla spawn files.

### 1.2 The table

| # | Pet (family) | Model ids (folder under Common/NPC/) | Vanilla roles | Attitude | Real h | Pet scale -> h | Pet? | Mount? | Baby | Chibi | Zone | Start rarity | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cat | `Cat` (Pets/Cat) | none | no role | 0.90 | 1x -> 0.90 | yes | no | Kitten |  | Z1 | Common | vanilla pet model, no live role |
| 2 | Kitten | `Kitten` (Pets/Kitten) | none | no role | 0.90 | 1x -> 0.90 | yes (baby) | no | is baby |  | Z1 | Common | baby look of Cat |
| 3 | Dog | `Dog` (Pets/Dog) | none | no role | 1.80 | 1x -> 1.80 | yes | no |  |  | Z1 | Common | vanilla pet model, no live role |
| 4 | Corgi | `Corgi` (Pets/Corgi) | none | no role | 0.80 | 1x -> 0.80 | yes | no |  |  | Z1 | Common | only the test role Test_Pet uses it |
| 5 | Frog | `Frog_Green`, `Frog_Blue`, `Frog_Orange` (Critter/Frog) | Frog_Blue, Frog_Green, Frog_Orange, Temple_Frog_Blue, Temple_Frog_Green +1 more | passive | 0.80 | 1x -> 0.80 | yes | no |  | 14 | Z1 | Common |  |
| 6 | Gecko | `Gecko` (Critter/Gecko) | Gecko | passive | 0.46 | 1x -> 0.46 | yes | no |  |  | Z2 | Common |  |
| 7 | Meerkat | `Meerkat` (Critter/Meerkat) | Meerkat | passive | 0.66 | 0.9x -> 0.60 | yes | no |  |  | Z2 | Common |  |
| 8 | Mouse | `Mouse` (Critter/Mouse) | Mouse | passive | 0.38 | 1x -> 0.38 | yes | no |  |  | Z1 | Common |  |
| 9 | Squirrel | `Squirrel` (Critter/Squirrel) | Squirrel, Temple_Squirrel | passive | 0.66 | 1x -> 0.66 | yes | no |  |  | Z1 | Common |  |
| 10 | Bee swarm | `Model_Bee_Swarm`, `Swarm_Bees` (Characters/Empty_Cube.blockymodel) | none | no role | 1.00 | 1x -> 1.00 | ASK [no] | no |  |  | Z1 | - | a swarm, not one creature |
| 11 | Bison | `Bison` (Livestock/Bison) | Bison, Tamed_Bison | tameable | 2.04 | 0.55x -> 1.12 | yes | candidate (1.0) | Bison_Calf |  | Z1 | Uncommon | not vanilla-mountable |
| 12 | Boar | `Boar` (Livestock/Boar) | Boar, Tamed_Boar | tameable | 1.00 | 0.8x -> 0.80 | yes | no | Boar_Piglet |  | Z1 | Uncommon | Pets-Spec launch pet |
| 13 | Bunny | `Bunny` (Livestock/Bunny) | Bunny, Tamed_Bunny, Temple_Bunny | tameable | 0.90 | 0.8x -> 0.72 | yes | no |  |  | Z1 | Common |  |
| 14 | Rabbit | `Rabbit` (Livestock/Rabbit) | Rabbit, Tamed_Rabbit | tameable | 1.30 | 0.7x -> 0.91 | yes | no |  |  | Z1 | Common | Pets-Spec starter pet |
| 15 | Camel | `Camel` (Livestock/Camel) | Camel, Tamed_Camel | tameable | 2.65 | 1x -> 2.65 | mount pet | YES vanilla | Camel_Calf |  | Z2 | Rare | Tamed_Camel IsMountable |
| 16 | Chicken | `Chicken`, `Chicken_Desert` (Livestock/Chicken) | Chicken, Chicken_Desert, Tamed_Chicken, Tamed_Chicken_Desert | tameable | 0.90 | 0.75x -> 0.68 | yes | no | Chick, Chick_Desert |  | Z1 | Common | Pets-Spec launch pet |
| 17 | Cow | `Cow` (Livestock/Cow) | Cow, Tamed_Cow | tameable | 1.70 | 0.55x -> 0.94 | yes | no | Calf |  | Z1 | Common |  |
| 18 | Goat | `Goat` (Livestock/Goat) | Goat, Tamed_Goat | tameable | 1.72 | 0.7x -> 1.21 | yes | no | Goat_Kid |  | Z3 | Uncommon | Pets-Spec launch pet |
| 19 | Horse | `Horse`, `Horse_Tamed` (Livestock/Horse) | Horse, Tamed_Horse | tameable | 2.50 | 1x -> 2.50 | mount pet | YES vanilla | Horse_Foal |  | Z2 | Uncommon | Tamed_Horse IsMountable; first mount (Stable quest) |
| 20 | Mouflon | `Mouflon` (Livestock/Mouflon) | Mouflon, Tamed_Mouflon | tameable | 1.80 | 0.65x -> 1.17 | yes | candidate (1.0) | Mouflon_Lamb |  | Z2 | Epic | Pets-Spec calls it a mount, but vanilla Mouflon is NOT mountable |
| 21 | Pig | `Pig`, `Pig_Wild` (Livestock/Pig) | Pig, Pig_Wild, Tamed_Pig, Tamed_Pig_Wild | tameable | 0.80 | 0.8x -> 0.64 | yes | no | Piglet, Piglet_Wild |  | Z1 | Common |  |
| 22 | Ram | `Ram` (Livestock/Ram) | Ram, Tamed_Ram | tameable | 1.80 | 1x -> 1.80 | mount pet | YES vanilla | Ram_Lamb |  | Z3 | Epic | Tamed_Ram IsMountable |
| 23 | Sheep | `Sheep` (Livestock/Sheep) | Sheep, Tamed_Sheep | tameable | 1.30 | 0.7x -> 0.91 | yes | no | Lamb |  | Z1 | Common |  |
| 24 | Skrill | `Skrill` (Livestock/Skrill) | Skrill, Tamed_Skrill | tameable | 0.90 | 0.75x -> 0.68 | yes | no | Skrill_Chick |  | Z4 | Epic | Pets-Spec Mage pet |
| 25 | Turkey | `Turkey` (Livestock/Turkey) | Tamed_Turkey, Turkey | tameable | 1.33 | 0.7x -> 0.93 | yes | no | Turkey_Chick |  | Z1 | Uncommon | Pets-Spec launch pet |
| 26 | Warthog | `Warthog` (Livestock/Warthog) | Tamed_Warthog, Warthog | tameable | 1.20 | 0.8x -> 0.96 | yes | no | Warthog_Piglet |  | Z2 | Uncommon | Pets-Spec launch pet (+ Tusker recolour) |
| 27 | Mosshorn | `Mosshorn`, `Mosshorn_Plain` (Wildlife/Mosshorn) | Mosshorn, Mosshorn_Plain, Tamed_Mosshorn, Tamed_Mosshorn_Plain | tameable | 1.87 | 0.55x -> 1.03 | yes | candidate (1.0) |  |  | Z1 | Rare | tameable (Tamed_Mosshorn), not mountable |
| 28 | Antelope | `Antelope` (Wildlife/Antelope) | Antelope | neutral | 2.50 | 0.5x -> 1.25 | yes | candidate (1.0) |  |  | Z2 | Uncommon |  |
| 29 | Armadillo | `Armadillo` (Wildlife/Armadillo) | Armadillo | neutral | 1.40 | 0.6x -> 0.84 | yes | no |  |  | Z2 | Uncommon |  |
| 30 | Deer | `Deer_Doe`, `Model_Deer_Stag` (Wildlife/Deer) | Deer_Doe, Deer_Stag, Temple_Deer_Doe, Temple_Deer_Stag | neutral | 1.93 | 0.55x -> 1.06 | yes | candidate (1.0) |  |  | Z1 | Uncommon | Reindeer_Christmas = event skin |
| 31 | Moose | `Moose_Cow`, `Moose_Bull` (Wildlife/Moose) | Moose_Bull, Moose_Cow | neutral | 1.94 | 0.5x -> 0.97 | yes | candidate (1.1) |  |  | Z3 | Rare |  |
| 32 | Penguin | `Penguin` (Wildlife/Penguin) | Penguin | neutral | 0.80 | 1x -> 0.80 | yes | no |  |  | Z3 | Uncommon |  |
| 33 | Tetrabird | `Tetrabird` (Wildlife/Tetrabird) | Tetrabird | neutral | 1.90 | 0.6x -> 1.14 | yes | no |  |  | Z5 | Rare |  |
| 34 | Tortoise | `Tortoise` (Wildlife/Tortoise) | Tortoise | neutral | 1.20 | 0.6x -> 0.72 | yes | no |  |  | Z1 | Uncommon |  |
| 35 | Trillodon | `Trillodon` (Wildlife/Trillodon) | Trillodon | neutral | 1.80 | 0.5x -> 0.90 | yes | candidate (1.0) |  |  | Z5 | Rare | dino |
| 36 | Flamingo | `Flamingo` (Flying_Wildlife/Flamingo) | Flamingo | neutral | 1.70 | 0.65x -> 1.10 | yes | no |  |  | Z2 | Uncommon |  |
| 37 | Sand Lizard | `Lizard_Sand` (Beast/Lizard_Sand) | Lizard_Sand | neutral | 0.80 | 0.8x -> 0.64 | yes | no |  |  | Z2 | Uncommon |  |
| 38 | Hatworm | `Hatworm` (Beast/Hatworm) | Hatworm | neutral | 0.65 | 1x -> 0.65 | yes | no |  |  | Z1 | Uncommon | model is already Snake_Marsh at 0.5x |
| 39 | Living Spark | `Spark_Living` (Beast/Spark_Living) | Spark_Living | neutral | 0.65 | 1x -> 0.65 | yes | no |  |  | Z4 | Rare |  |
| 40 | Crab | `Crab` (Swimming_Beast/Crab) | Crab | neutral | 0.90 | 0.6x -> 0.54 | yes | no |  |  | Fishing | Uncommon | walks on land |
| 41 | Lobster | `Lobster` (Swimming_Beast/Lobster) | Lobster | neutral | 0.70 | 0.6x -> 0.42 | yes | no |  |  | Fishing | Uncommon | walks on land |
| 42 | Fox | `Fox` (Beast/Fox) | Fox | hostile | 1.10 | 0.8x -> 0.88 | yes | no |  | 2 | Z1 | Uncommon | Skyy named; timid by day |
| 43 | Wolf | `Wolf_Black`, `Wolf_White`, `Wolf_Trork_Hunter`, `Wolf_Trork_Shaman`, `Wolf_Outlander_Priest`, `Wolf_Outlander_Sorcerer` (Beast/Wolf) | Wolf_Black, Wolf_Outlander_Priest, Wolf_Outlander_Sorcerer, Wolf_Trork_Hunter, Wolf_Trork_Shaman +1 more | hostile | 1.36 | 0.75x -> 1.02 | yes | no |  | 3 | Z3 | Rare | Skyy named; the 4 companion wolves use the same model |
| 44 | Hyena | `Hyena` (Beast/Hyena) | Hyena | hostile | 1.19 | 0.8x -> 0.95 | yes | no |  |  | Z2 | Uncommon |  |
| 45 | Bear | `Bear_Grizzly`, `Bear_Polar` (Beast/Bear_Grizzly) | Bear_Grizzly, Bear_Polar | hostile | 1.94 | 0.6x -> 1.16 | yes | candidate (1.0) |  | 7 | Z3 | Rare | Pets-Spec Bear |
| 46 | Sabertooth | `Tiger_Sabertooth` (Beast/Tiger_Sabertooth) | Tiger_Sabertooth | hostile | 1.70 | 0.6x -> 1.02 | yes | candidate (1.0) |  | 10 | Z3 | Epic |  |
| 47 | Snow Leopard | `Leopard_Snow` (Beast/Tiger_Sabertooth) | Leopard_Snow | hostile | 1.70 | 0.65x -> 1.10 | yes | candidate (1.0) |  |  | Z3 | Rare | Sabertooth rig |
| 48 | Emberwulf | `Emberwulf` (Beast/Emberwulf) | Emberwulf | hostile | 1.70 | 0.6x -> 1.02 | yes | candidate (1.0) |  |  | Z4 | Epic |  |
| 49 | Cave Raptor | `Raptor_Cave` (Beast/Raptor_Cave) | Raptor_Cave | hostile | 2.21 | 0.55x -> 1.21 | yes | candidate (1.0) |  | 9 | Z5 | Epic | dino |
| 50 | Cave Rex | `Rex_Cave` (Beast/Rex_Cave) | Rex_Cave | hostile | 4.09 | 0.3x -> 1.23 | yes | candidate (1.0, big) |  | 8 | Z5 | Epic | dino; 4 blocks tall |
| 51 | Yeti | `Yeti` (Beast/Yeti) | Yeti | hostile | 3.90 | 0.32x -> 1.25 | yes | no |  | 15 | Z3 | Epic |  |
| 52 | Rat | `Rat` (Beast/Rat) | Edible_Rat, Rat | hostile | 0.52 | 0.8x -> 0.42 | yes | no |  | 5 | Z1 | Common | Skyy named; also Edible_Rat |
| 53 | Molerat | `Molerat` (Beast/Molerat) | Molerat | hostile | 0.68 | 0.8x -> 0.54 | yes | no |  |  | Z2 | Uncommon |  |
| 54 | Snake | `Snake_Marsh`, `Snake_Cobra`, `Snake_Rattle` (Beast/Snake) | Snake_Cobra, Snake_Marsh, Snake_Rattle | hostile | 1.01 | 0.8x -> 0.81 | yes | no |  |  | Z1 | Uncommon |  |
| 55 | Spider | `Spider`, `Spider_Cave` (Beast/Spider) | Spider, Spider_Cave | hostile | 0.80 | 0.55x -> 0.44 | yes | no |  |  | Z1 | Uncommon |  |
| 56 | Scorpion | `Scorpion` (Beast/Scorpion) | Scorpion | hostile | 1.70 | 0.55x -> 0.94 | yes | no |  |  | Z2 | Rare |  |
| 57 | Silk Larva | `Larva_Silk`, `Wurmling_Frost` (Beast/Larva) | Larva_Silk | hostile | 0.60 | 0.8x -> 0.48 | yes | no |  |  | Z1 | Common | Wurmling_Frost has no role |
| 58 | Magma Slug | `Slug_Magma` (Beast/Slug_Magma) | Slug_Magma | hostile | 1.70 | 0.45x -> 0.77 | yes | no |  |  | Z4 | Rare |  |
| 59 | Snail | `Snail_Magma`, `Snail_Frost` (Beast/Snail) | Snail_Frost, Snail_Magma | passive | 0.90 | 0.8x -> 0.72 | yes | no |  |  | Z3 | Common |  |
| 60 | Rhino Toad | `Toad_Rhino`, `Toad_Rhino_Magma`, `Toad_Rhino_Green` (Beast/Toad_Rhino) | Toad_Rhino, Toad_Rhino_Magma | hostile | 1.70 | 0.6x -> 1.02 | yes | no | Tadpole_Rhino |  | Z1 | Rare | Tadpole_Rhino / Toad_Rhino_Green have no role |
| 61 | Snapdragon | `Snapdragon` (Beast/Snapdragon) | Snapdragon | hostile | 1.70 | 0.6x -> 1.02 | yes | no |  |  | Z1 | Rare | plant |
| 62 | Cactee | `Cactee` (Beast/Cactee) | Cactee | passive | 1.50 | 0.7x -> 1.05 | yes | no |  |  | Z2 | Uncommon | plant |
| 63 | Mushee | `Mushee` (Beast/Mushee/Model/Model.blockymodel) | none | no role | 0.80 | 0.9x -> 0.72 | yes | no |  |  | Z1 | Uncommon | no vanilla role (Cactee rig) |
| 64 | Grooble | `Grooble` (Beast/Grooble) | none | no role | 1.50 | 0.7x -> 1.05 | ASK [yes] | no |  |  | Z1 | Uncommon | no vanilla role |
| 65 | Scarak Louse | `Scarak_Louse` (Beast/Scarak_Louse) | Dungeon_Scarak_Louse, Scarak_Louse | neutral | 0.60 | 0.8x -> 0.48 | yes | no |  |  | Z2 | Uncommon | dungeon bug |
| 66 | Scarak Fighter | `Scarak_Fighter`, `Scarak_Fighter_Royal_Guard` (Beast/Scarak_Fighter) | Dungeon_Scarak_Fighter, Dungeon_Scarak_Fighter_Patrol, Scarak_Fighter, Scarak_Fighter_Patrol, Scarak_Fighter_Royal_Guard | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  |  | Z2 | Rare |  |
| 67 | Scarak Defender | `Scarak_Defender` (Beast/Scarak_Defender) | Dungeon_Scarak_Defender, Dungeon_Scarak_Defender_Patrol, Scarak_Defender, Scarak_Defender_Patrol | neutral | 2.20 | 0.5x -> 1.10 | yes | candidate (1.0) |  |  | Z2 | Rare |  |
| 68 | Scarak Seeker | `Scarak_Seeker` (Flying_Beast/Scarak_Seeker) | Dungeon_Scarak_Seeker, Dungeon_Scarak_Seeker_Patrol, Scarak_Seeker, Scarak_Seeker_Patrol | hostile | 1.80 | 0.6x -> 1.08 | yes (flying) | no |  |  | Z2 | Rare |  |
| 69 | Scarak Broodmother | `Scarak_Broodmother`, `Scarak_Broodmother_Young` (Beast/Scarak_Broodmother) | Dungeon_Scarak_Broodmother, Dungeon_Scarak_Broodmother_Young, Scarak_Broodmother | neutral | 5.76 | 0.3x -> 1.73 | no (boss) | no |  |  | - | - | dungeon queen |
| 70 | Small birds | `Sparrow`, `Bluebird`, `Finch_Green`, `Woodpecker`, `Pigeon`, `Crow`, `Parrot` (Flying_Critter/Sparrow) | Bluebird, Crow, Finch_Green, Parrot, Pigeon +4 more | passive | 0.60 | 1x -> 0.60 | yes (flying) | no |  |  | Z1 | Common | 7 looks, one family |
| 71 | Owl | `Owl_Brown`, `Owl_Snow` (Flying_Critter/Owl) | Owl_Brown, Owl_Snow, Temple_Owl_Brown | passive | 0.90 | 1x -> 0.90 | yes (flying) | no |  | 13 | Z1 | Uncommon |  |
| 72 | Bat | `Bat`, `Bat_Ice` (Flying_Critter/Bat) | Bat, Bat_Ice | passive | 0.90 | 1x -> 0.90 | yes (flying) | no |  |  | Z1 | Uncommon |  |
| 73 | Duck | `Duck` (Flying_Wildlife/Duck) | Duck, Temple_Duck | passive | 0.90 | 1x -> 0.90 | yes | no |  |  | Z1 | Common |  |
| 74 | Hawk | `Hawk` (Flying_Wildlife/Hawk) | Hawk | passive | 0.95 | 0.9x -> 0.85 | yes (flying) | no |  |  | Z2 | Epic | Pets-Spec Archer pet |
| 75 | Raven | `Raven` (Flying_Wildlife/Raven) | Raven | passive | 0.74 | 1x -> 0.74 | yes (flying) | no |  |  | Z4 | Uncommon |  |
| 76 | Vulture | `Vulture` (Flying_Beast/Vulture) | Vulture | passive | 1.50 | 0.7x -> 1.05 | yes (flying) | no |  |  | Z2 | Rare |  |
| 77 | Archaeopteryx | `Archaeopteryx` (Flying_Beast/Archaeopteryx) | Archaeopteryx | passive | 1.70 | 0.65x -> 1.10 | yes (flying) | no |  |  | Z5 | Rare | dino bird |
| 78 | Pterodactyl | `Pterodactyl` (Flying_Beast/Pterodactyl) | Pterodactyl | passive | 2.10 | 0.5x -> 1.05 | yes (flying) | flying, later |  |  | Z5 | Epic | vanilla has no flying mount |
| 79 | Small fish | `Bluegill`, `Minnow`, `Catfish`, `Clownfish`, `Tang_Blue`, `Tang_Chevron`, `Tang_Lemon_Peel`, `Tang_Sailfin`, `Trout_Rainbow`, `Salmon`, `Pike`, `Frostgill` (Swimming_Wildlife/Bluegill) | Bluegill, Catfish, Clownfish, Frostgill, Minnow +7 more | passive | 0.50 | 0.8x -> 0.40 | water pet | no |  |  | Fishing | Common | 12 looks, one family |
| 80 | Piranha | `Piranha`, `Piranha_Black` (Swimming_Beast/Piranha) | Piranha, Piranha_Black | hostile | 0.50 | 0.8x -> 0.40 | water pet | no |  |  | Fishing | Uncommon |  |
| 81 | Jellyfish | `Jellyfish_Blue`, `Jellyfish_Cyan`, `Jellyfish_Green`, `Jellyfish_Red`, `Jellyfish_Yellow`, `Jellyfish_Man_Of_War` (Swimming_Wildlife/Jellyfish) | Jellyfish_Blue, Jellyfish_Cyan, Jellyfish_Green, Jellyfish_Man_Of_War, Jellyfish_Red +1 more | passive | 0.60 | 0.8x -> 0.48 | water pet | no |  |  | Fishing | Uncommon |  |
| 82 | Pufferfish | `Pufferfish` (Swimming_Wildlife/Pufferfish) | Pufferfish | passive | 0.38 | 1x -> 0.38 | water pet | no |  |  | Fishing | Uncommon | vanilla random scale 0.5-2 |
| 83 | Moray Eel | `Eel_Moray` (Swimming_Beast/Eel) | Eel_Moray | passive | 0.67 | 0.7x -> 0.47 | water pet | no |  |  | Fishing | Rare |  |
| 84 | Lava Shellfish | `Shellfish_Lava` (Swimming_Beast/Shellfish_Lava) | Shellfish_Lava | passive | 0.30 | 1x -> 0.30 | water pet | no |  |  | Fishing | Rare |  |
| 85 | Trilobite | `Trilobite`, `Trilobite_Black` (Swimming_Wildlife/Trilobite) | Trilobite, Trilobite_Black | passive | 0.30 | 0.8x -> 0.24 | water pet | no |  |  | Z5 | Uncommon |  |
| 86 | Hammerhead | `Shark_Hammerhead` (Swimming_Beast/Shark_Hammerhead) | Shark_Hammerhead | passive | 1.00 | 0.45x -> 0.45 | water pet | no |  |  | Fishing | Epic |  |
| 87 | Snapjaw | `Snapjaw` (Swimming_Beast/Snapjaw) | Snapjaw | passive | 1.50 | 0.3x -> 0.45 | water pet | no |  |  | Fishing | Epic |  |
| 88 | Humpback Whale | `Whale_Humpback` (Swimming_Wildlife/Whale_Humpback) | Whale_Humpback | passive | 3.24 | 0.2x -> 0.65 | water pet | no |  |  | Fishing | Epic | tiny whale |
| 89 | Crocodile | `Crocodile` (Swimming_Beast/Crocodile) | Crocodile | hostile | 1.25 | 0.5x -> 0.62 | yes | candidate (1.0) |  |  | Z1 | Rare | walks on land |
| 90 | Fen Stalker | `Fen_Stalker` (Swimming_Beast/Fen_Stalker) | Fen_Stalker | hostile | 1.60 | 0.65x -> 1.04 | yes | no |  |  | Z1 | Rare | swamp, walks on land |
| 91 | Skeleton | `Skeleton`, `Skeleton_Fighter`, `Skeleton_Soldier`, `Skeleton_Archer`, `Skeleton_Ranger`, `Skeleton_Scout`, `Skeleton_Knight`, `Skeleton_Mage`, `Skeleton_Archmage` (Undead/Skeleton) | Risen_Knight, Skeleton, Skeleton_Archer, Skeleton_Archer_Patrol, Skeleton_Archer_Wander +21 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Z1 | Rare | Skyy: Skeleton pet = Fox size; first chibi (ART-RESUME 16) |
| 92 | Burnt Skeleton | `Skeleton_Burnt_Soldier`, `Skeleton_Burnt_Archer`, `Skeleton_Burnt_Knight`, `Skeleton_Burnt_Lancer`, `Skeleton_Burnt_Gunner`, `Skeleton_Burnt_Wizard`, `Skeleton_Burnt_Alchemist` (Undead/Skeleton) | Risen_Gunner, Skeleton_Burnt_Alchemist, Skeleton_Burnt_Alchemist_Patrol, Skeleton_Burnt_Alchemist_Wander, Skeleton_Burnt_Archer +17 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Z4 | Rare | chibi Skeleton + skin |
| 93 | Burnt Praetorian | `Skeleton_Burnt_Praetorian` (Undead/Skeleton_Giant) | Skeleton_Burnt_Praetorian, Skeleton_Burnt_Praetorian_Patrol, Skeleton_Burnt_Praetorian_Wander | hostile | 3.33 | 0.4x -> 1.33 | yes | no |  |  | Z4 | Epic | big skeleton |
| 94 | Frost Skeleton | `Skeleton_Frost_Fighter`, `Skeleton_Frost_Soldier`, `Skeleton_Frost_Archer`, `Skeleton_Frost_Ranger`, `Skeleton_Frost_Scout`, `Skeleton_Frost_Knight`, `Skeleton_Frost_Mage`, `Skeleton_Frost_Archmage` (Undead/Skeleton) | Skeleton_Frost_Archer, Skeleton_Frost_Archer_Patrol, Skeleton_Frost_Archer_Wander, Skeleton_Frost_Archmage, Skeleton_Frost_Archmage_Patrol +19 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Z3 | Rare | chibi Skeleton + skin |
| 95 | Sand Skeleton | `Skeleton_Sand_Soldier`, `Skeleton_Sand_Archer`, `Skeleton_Sand_Ranger`, `Skeleton_Sand_Scout`, `Skeleton_Sand_Guard`, `Skeleton_Sand_Assassin`, `Skeleton_Sand_Mage`, `Skeleton_Sand_Archmage` (Undead/Skeleton) | Dungeon_Skeleton_Sand_Archer, Dungeon_Skeleton_Sand_Assassin, Dungeon_Skeleton_Sand_Mage, Dungeon_Skeleton_Sand_Soldier, Skeleton_Sand_Archer +23 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Z2 | Rare | chibi Skeleton + skin |
| 96 | Pirate Skeleton | `Skeleton_Pirate_Captain`, `Skeleton_Pirate_Gunner`, `Skeleton_Pirate_Striker` (Undead/Skeleton) | Skeleton_Pirate_Captain, Skeleton_Pirate_Captain_Patrol, Skeleton_Pirate_Captain_Wander, Skeleton_Pirate_Gunner, Skeleton_Pirate_Gunner_Patrol +4 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Fishing | Epic | chibi Skeleton + skin |
| 97 | Incandescent Skeleton | `Skeleton_Incandescent_Fighter`, `Skeleton_Incandescent_Footman`, `Skeleton_Incandescent_Mage` (Undead/Skeleton) | Skeleton_Incandescent_Fighter, Skeleton_Incandescent_Fighter_Patrol, Skeleton_Incandescent_Fighter_Wander, Skeleton_Incandescent_Footman, Skeleton_Incandescent_Footman_Patrol +4 more | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  | 1 | Z4 | Epic | chibi Skeleton + skin |
| 98 | Incandescent Head | `Skeleton_Incandescent_Head` (Undead/Skeleton_Head) | Skeleton_Incandescent_Head | hostile | 0.60 | 1x -> 0.60 | yes (flying) | no |  |  | Z4 | Rare | floating skull |
| 99 | Skeleton Horse | `Horse_Skeleton`, `Horse_Skeleton_Armored` (Undead/Horse_Skeleton) | Horse_Skeleton, Horse_Skeleton_Armored | neutral | 2.50 | 1x -> 2.50 | mount pet | candidate (1.0) |  |  | Z4 | Epic | vanilla role not mountable; needs our own role |
| 100 | Zombie | `Zombie`, `Zombie_Burnt`, `Zombie_Frost`, `Zombie_Sand`, `Zombie_Aberrant_Small`, `Zombie_Werewolf` (Undead/Zombie) | Zombie, Zombie_Aberrant_Small, Zombie_Burnt, Zombie_Frost, Zombie_Sand | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  |  | Z1 | Uncommon | Zombie_Werewolf has no role |
| 101 | Aberrant Zombie | `Zombie_Aberrant`, `Zombie_Aberrant_Big` (Undead/Zombie_Aberrant) | Zombie_Aberrant, Zombie_Aberrant_Big | hostile | 2.64 | 0.45x -> 1.19 | yes | no |  |  | Z4 | Epic |  |
| 102 | Ghoul | `Ghoul` (Undead/Ghoul) | Ghoul | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  |  | Z4 | Rare |  |
| 103 | Bleached Hound | `Hound_Bleached` (Undead/Hound_Bleached) | Hound_Bleached | hostile | 1.36 | 0.75x -> 1.02 | yes | no |  |  | Z4 | Rare |  |
| 104 | Werewolf | `Werewolf` (Undead/Werewolf) | Werewolf | hostile | 2.60 | 0.5x -> 1.30 | yes | candidate (1.0) |  |  | Z1 | Epic |  |
| 105 | Wraith | `Wraith` (Undead/Wraith) | Wraith | hostile | 1.80 | 0.6x -> 1.08 | yes | no |  |  | Z4 | Rare |  |
| 106 | Wraith Lantern | `Wraith_Lantern` (Undead/Wraith_Lantern) | Wraith_Lantern | hostile | 1.15 | 0.9x -> 1.03 | yes (flying) | no |  |  | Z4 | Rare |  |
| 107 | Shadow Knight | `Shadow_Knight` (Undead/Shadow_Knight) | Shadow_Knight | hostile | 3.25 | 0.4x -> 1.30 | ASK [no] | no |  |  | Z4 | Epic | 3.25 blocks; may be a mini-boss |
| 108 | Undead farm animals | `Chicken_Undead`, `Pig_Undead`, `Cow_Undead` (Undead/Chicken_Undead) | Chicken_Undead, Cow_Undead, Pig_Undead | hostile | 0.90 | 0.75x -> 0.68 | yes | no |  |  | Z4 | Uncommon | skins of the Chicken / Pig / Cow pets (Cow 0.55x) |
| 109 | Void Eye | `Eye_Void` (Void/Eye_Void) | Eye_Void | hostile | 1.96 | 0.35x -> 0.69 | yes (flying) | no |  | 4 | Z4 | Epic | Skyy: the beholder |
| 110 | Void Crawler | `Crawler_Void` (Void/Crawler_Void) | Crawler_Void | hostile | 0.90 | 0.75x -> 0.68 | yes | no |  | 6 | Z4 | Rare | Skyy: void slug things |
| 111 | Void Larva | `Larva_Void` (Beast/Larva) | Larva_Void | hostile | 0.60 | 0.8x -> 0.48 | yes | no |  | 6 | Z4 | Uncommon | Skyy: void slug things (Silk Larva rig) |
| 112 | Void Spawn | `Spawn_Void` (Void/Spawn_Void) | Spawn_Void | hostile | 2.10 | 0.55x -> 1.16 | yes | no |  |  | Z4 | Epic |  |
| 113 | Void Spectre | `Spectre_Void` (Void/Spectre_Void) | Spectre_Void | no template | 0.90 | 0.9x -> 0.81 | yes (flying) | no |  |  | Z4 | Rare |  |
| 114 | Void Necromancer | `Necromancer_Void` (Void/Necromancer_Void) | none | no role | 2.30 | 0.45x -> 1.03 | ASK [no] | no |  |  | Z4 | - | no vanilla role; humanoid caster |
| 115 | Crystal Golem | `Golem_Crystal_Earth`, `Golem_Crystal_Flame`, `Golem_Crystal_Frost`, `Golem_Crystal_Sand`, `Golem_Crystal_Thunder`, `Golem_Firesteel` (Elemental/Golem_Crystal) | Golem_Crystal_Earth, Golem_Crystal_Flame, Golem_Crystal_Frost, Golem_Crystal_Sand, Golem_Crystal_Thunder +1 more | hostile | 2.80 | 0.45x -> 1.26 | yes | candidate (1.0) |  | 11 | Z3 | Epic | 6 elements, one rig |
| 116 | Spirit | `Spirit_Root`, `Spirit_Ember`, `Spirit_Frost`, `Spirit_Thunder` (Elemental/Spirit_Root) | Spirit_Ember, Spirit_Frost, Spirit_Root, Spirit_Thunder | hostile | 0.80 | 0.9x -> 0.72 | yes (flying) | no |  | 12 | Z1 | Rare | 4 elements, one rig |
| 117 | Dragon | `Dragon_Fire`, `Dragon_Frost`, `Dragon_Void` (Elemental/Dragon_Fire) | Dragon_Fire, Dragon_Frost | no role | 3.50 | 1x -> 3.50 | no (dragon tier) | dragon tier |  |  | Z5 | Mythic | dragon quest / Nestkeeper; vanilla roles are placeholders |
| 118 | Void Guardian Golem | `Golem_Guardian_Void` (Boss/Golem_Guardian) | none | no role | 4.80 | 1x -> 4.80 | no (boss) | no |  |  | - | - |  |
| 119 | Kweebec (all kinds) | `Kweebec_Sapling`, `Kweebec_Rootling`, `Kweebec_Sapling_Razorleaf`, `Kweebec_Sapling_Treesinger`, `Kweebec_Seedling`, `Kweebec_Sproutling`, `Kweebec_Sproutling_Blue`, `Kweebec_Sproutling_Lime` (Intelligent/Kweebec_Sapling) | Kweebec_Elder, Kweebec_Merchant, Kweebec_Razorleaf, Kweebec_Razorleaf_Patrol, Kweebec_Rootling +16 more | neutral | 1.40 | 0.6x -> 0.84 | no (Skyy: no Kweebecs / Trorks) | no |  |  | - | - | + 9 colour skins and 3 Christmas skins |
| 120 | Trork (all kinds) | `Trork_Warrior`, `Trork_Brawler`, `Trork_Hunter`, `Trork_Guard`, `Trork_Mauler`, `Trork_Sentry`, `Trork_Shaman`, `Trork_Doctor_Witch`, `Trork_Chieftain` (Intelligent/Trork) | Trork_Brawler, Trork_Chieftain, Trork_Doctor_Witch, Trork_Guard, Trork_Hunter +7 more | hostile | 2.09 | 0.6x -> 1.25 | no (Skyy: no Kweebecs / Trorks) | no |  |  | - | - | + Trork_Christmas skin |
| 121 | Bramblekin | `Bramblekin`, `Bramblekin_Shaman` (Intelligent/Bramblekin) | none | no role | 1.80 | 0.6x -> 1.08 | ASK [no] | no |  |  | - | - | no vanilla role |
| 122 | Feran | `Feran_Civilian`, `Feran_Burrower`, `Feran_Cub`, `Feran_Longtooth`, `Feran_Sharptooth`, `Feran_Windwalker` (Intelligent/Feran) | Feran_Burrower, Feran_Civilian, Feran_Cub, Feran_Longtooth, Feran_Sharptooth +3 more | neutral | 1.71 | 0.6x -> 1.03 | ASK [no] | no | Feran_Cub |  | - | - | villager race |
| 123 | Klops | `Klops_Merchant`, `Klops_Miner`, `Klops_Gentleman` (Intelligent/Klops) | Klops_Gentleman, Klops_Merchant, Klops_Merchant_Patrol, Klops_Merchant_Wandering, Klops_Miner +3 more | neutral | 1.50 | 0.7x -> 1.05 | ASK [no] | no |  |  | - | - | merchant race |
| 124 | Slothian | `Slothian`, `Slothian_Elder`, `Slothian_Kid`, `Slothian_Monk`, `Slothian_Scout`, `Slothian_Villager`, `Slothian_Warrior` (Intelligent/Slothian) | none | no role | 1.90 | 0.6x -> 1.14 | ASK [no] | no | Slothian_Kid |  | - | - | no vanilla roles |
| 125 | Tuluk | `Tuluk`, `Tuluk_Fisherman` (Intelligent/Tuluk) | Tuluk_Fisherman | no role | 1.80 | 0.6x -> 1.08 | ASK [no] | no |  |  | - | - | placeholder role only |
| 126 | Goblin | `Goblin_Scrapper`, `Goblin_Miner`, `Goblin_Lobber`, `Goblin_Hermit`, `Goblin_Thief` (Intelligent/Goblin) | Edible_Goblin_Scrapper, Goblin_Hermit, Goblin_Lobber, Goblin_Lobber_Patrol, Goblin_Miner +8 more | hostile | 1.70 | 0.65x -> 1.10 | ASK [no] | no |  |  | - | - | small hostile folk |
| 127 | Goblin Ogre | `Goblin_Ogre` (Intelligent/Goblin_Ogre/Model.blockymodel) | Goblin_Ogre | hostile | 3.22 | 0.4x -> 1.29 | ASK [no] | no |  |  | - | - |  |
| 128 | Goblin Duke | `Goblin_Duke`, `Goblin_Duke_Large`, `Goblin_Boss` (Intelligent/Goblin_Duke) | Goblin_Duke, Goblin_Duke_Phase_2, Goblin_Duke_Phase_3_Fast, Goblin_Duke_Phase_3_Slow | hostile | 2.50 | 1x -> 2.50 | no (boss) | no |  |  | - | - | 3-phase boss |
| 129 | Outlander | `Outlander_Peon`, `Outlander_Berserker`, `Outlander_Cultist`, `Outlander_Hunter`, `Outlander_Marauder`, `Outlander_Priest`, `Outlander_Sorcerer`, `Outlander_Stalker`, `Outlander_Brute` (Characters/Player_With_Face.blockymodel) | Outlander_Berserker, Outlander_Brute, Outlander_Cultist, Outlander_Hunter, Outlander_Marauder +4 more | hostile | 1.85 | 0.6x -> 1.11 | ASK [no] | no |  |  | - | - | human enemies |
| 130 | Saurian | `Saurian`, `Saurian_Hunter`, `Saurian_Rogue`, `Saurian_Warrior` (Intelligent/Saurian) | none | no role | 1.90 | 0.55x -> 1.04 | ASK [no] | no |  |  | - | - | no vanilla roles |
| 131 | Elf | `NPC_Elf` (Characters/Player.blockymodel) | none | no role | 1.85 | 0.6x -> 1.11 | ASK [no] | no |  |  | - | - | event NPC model |
| 132 | Hedera | `Hedera` (Intelligent/Hedera) | Hedera | hostile | 3.64 | 0.3x -> 1.09 | no (boss-like) | no |  |  | - | - | 3.6 blocks, aggressive |

Not in the table (not creatures): markers (`Encounter_Marker`, `NPC_Spawn_Marker`, `NPC_Path_Marker`, `Objective_Location_Marker`, `Warp`),
player / test models (`Player`, `PlayerTestModel_*`, `Mannequin`, `Warrior_Quest`, `NPC_Santa`, `NPC_Sound_Shoe`), base rigs with no own
look (`Trork`, `Outlander`, `Feran`, `Klops`, `Goblin`), statues / Scifi / MISC folders. Event skins: `Reindeer_Christmas` (Deer),
`Trork_Christmas`, 3 Christmas Kweebecs.

Notes on single rows:
- **Dog** has a loose 1.8 hitbox; the model itself looks dog-sized. Check in game before setting its scale.
- **Babies** (17 models: `Bison_Calf`, `Boar_Piglet`, `Calf`, `Camel_Calf`, `Chick`, `Chick_Desert`, `Goat_Kid`, `Horse_Foal`, `Lamb`,
  `Mouflon_Lamb`, `Piglet`, `Piglet_Wild`, `Ram_Lamb`, `Skrill_Chick`, `Turkey_Chick`, `Warthog_Piglet`, `Kitten`, + `Tadpole_Rhino`) stay
  at 1.0x. Proposal: in a family with a baby, the pet is the BABY until a level (default Lv 30), then the shrunk adult (Q4).
- **Mouflon**: Pets-Spec calls it a mount, but vanilla Mouflon is not mountable (only Tamed_Horse, Tamed_Camel, Tamed_Ram are). It becomes a
  candidate mount with our own role, or stays a plain pet.
- **Shadow Knight, Hedera, Scarak Broodmother, Goblin Duke, Void Guardian Golem** look like bosses (3+ blocks, phases, dungeon queen).
  Bosses are "no"; Shadow Knight is ASK (Template_Predator, may be a normal elite).
- **Dragons** (`Dragon_Fire`, `Dragon_Frost`, `Dragon_Void`) stay the dragon tier (Dragon quest / Aures' Nestkeeper), not roster pets.

### 1.3 Chibi favourites for Quirk (top 15)

One chibi rig covers every skin of its family, so 15 chibis cover about 80 pet looks.

| # | Chibi | Covers | Why |
|---|---|---|---|
| 1 | Skeleton | Skeleton + Burnt / Frost / Sand / Pirate / Incandescent skins (38 looks) | Skyy's example; artist starts here (ART-RESUME item 16) |
| 2 | Fox | Fox | Skyy named it; the size reference |
| 3 | Wolf | Wolf_Black / White + 4 companion wolves (+ Hyena could share) | Skyy named it |
| 4 | Void Eye | Eye_Void | Skyy's "beholder" |
| 5 | Rat | Rat (+ Molerat later) | Skyy named it |
| 6 | Void slug | Larva_Void + Crawler_Void (2 rigs, one look) | Skyy's "void slug things" |
| 7 | Bear | Grizzly + Polar | launch pet (Pets-Spec) |
| 8 | Cave Rex | Rex_Cave | Zone 5 star; a tiny T-rex |
| 9 | Cave Raptor | Raptor_Cave | Zone 5 |
| 10 | Sabertooth | Sabertooth + Snow Leopard | Zone 3 |
| 11 | Crystal Golem | 6 element skins | Zone 3 Epic |
| 12 | Spirit | Root / Ember / Frost / Thunder | flying, simple shape |
| 13 | Owl | Brown + Snow | flying shoulder-size pet |
| 14 | Frog | Green / Blue / Orange | Z1 starter-size cute |
| 15 | Yeti | Yeti | Zone 3 big-to-tiny |

Cat, Dog, Corgi, Kitten and the babies are already pet-sized and cute; they need no chibi.

## 2. How a pet spawns as a shrunk vanilla model

### 2.1 What the server does (read from HytaleServer.jar)

| Fact | Where | Status |
|---|---|---|
| A model asset can have `MinScale` / `MaxScale` (166 vanilla model files use them: Bear 0.9-1.25, Pufferfish 0.5-2, Kweebec Seedling 0.8-1). On spawn the engine rolls a random scale between them. | Assets `Server/Models/*.json`; `RoleBuilderSystem.onEntityAdd` calls `ModelAsset.generateRandomScale()` then `Model.createScaledModel(asset, scale)` | VERIFIED |
| `Model.createScaledModel(ModelAsset, float)` (+ overloads with attachments / bounding box) builds a model at any scale; the scaled Model carries `getScale()` and a scaled hitbox. | `server.core.asset.type.model.config.Model` | VERIFIED |
| `NPCPlugin.spawnEntity(Store, roleIndex, position, rotation, Model, TriConsumer[, TriConsumer])` takes the Model to use. If a Model is given it calls `NPCEntity.setInitialModelScale(model.getScale())`, adds `ModelComponent(model)` and `PersistentModel(model.toReference())`. `RoleBuilderSystem` only picks its own random scale when the entity has NO ModelComponent, so our scale wins. | `NPCPlugin.spawnEntity` bytecode 184-246; `RoleBuilderSystem.onEntityAdd` 624-760 | VERIFIED |
| The scale is saved: `PersistentModel` stores a `ModelReference`, and `ModelReference.toModel()` rebuilds it with `createScaledModel(..., scale, ...)`. | `Model$ModelReference.toModel` | VERIFIED |
| The role's model and scale can be changed later (growth with level): `NPCEntity.setAppearance(Ref, ModelAsset, accessor)` (uses `createScaledModel(asset, scale)`), or put a new `ModelComponent`. | `NPCEntity` | VERIFIED (method exists); growth in play UNVERIFIED |
| A second, separate way: `EntityScaleComponent(float)` (getScale / setScale, sent to clients). The creative spawn page (`EntitySpawnPage.spawnNPC`) spawns with `spawnNPC(...)` and then puts an `EntityScaleComponent`. | `EntityScaleComponent`, `EntitySpawnPage` | VERIFIED (exists, vanilla uses it on NPCs) |
| The admin command `/npc spawn` has a `scale` argument (`server.commands.npc.spawn.scale.desc`) and uses `createScaledModel`. `/model set` also has a `scale` argument. | `NPCSpawnCommand`, `ModelCommand` | VERIFIED (args exist); exact syntax UNVERIFIED |
| Animations at a scale: the client scales the whole model. Vanilla already plays every animation at random scales 0.5-2 (Pufferfish, Bear, Goblin Ogre 1.4, Praetorian 1.45). | vanilla data | VERIFIED for 0.5-2; very small scales (0.2-0.35: Whale, Rex, Yeti, Void Eye) UNVERIFIED |
| A small pet that runs at a full-size walking speed may "skate" (legs move slowly for the distance). The walk speed is the role's `MaxSpeed`; the animation speed comes from the model asset `AnimationSets ... Speed`. | role / model data | UNVERIFIED look; fix by our own model asset (below) |

**Verdict: VERIFIED** - we can spawn any vanilla creature as a pet at our own scale: `NPCPlugin.spawnEntity(store, roleIndex, pos, rot,
Model.createScaledModel(ModelAsset.getAssetMap().getAsset("<id>"), scale), null)`. Nothing vanilla is copied. In-game look at very small
scales is UNVERIFIED (first test below).

**Option B (later, for skating or chibis):** our mod ships its own model asset, e.g. `SkyyPet_Fox` with `"Parent": "Fox"`,
`MinScale` = `MaxScale` = 0.8 and faster walk `Speed`. 243 vanilla model files use `Parent`, so inheriting the vanilla model / texture /
animations by id works the same way (no vanilla file copied). A Quirk chibi later is just a new model asset id in the pet's row.
UNVERIFIED: that a mod asset pack may add `Server/Models` entries that use a vanilla Parent.

### 2.2 Followers and pets in vanilla

| Fact | Where | Status |
|---|---|---|
| `Pets/Cat`, `Dog`, `Corgi`, `Kitten` models exist, but no live role spawns them. Only test roles use Corgi (`_Core/Tests/Test_Pet.json`, `Test_Dog_Tame.json`): Test_Pet = invulnerable, walks to the nearest player within 15 (Seek, stop at 3) and Teleports when far. | Assets | VERIFIED (data); test roles are not shipped content |
| `Template_Summoned_Ally` = a real vanilla follower: it joins the nearest player's FLOCK (`JoinFlock`, ForceJoin), follows the flock leader (Seek, stop 4), turns hostile to whatever the leader hits or is hit by, despawns on a timer or when it leaves the player's flock. Used by `Risen_Knight` (Skeleton_Knight model) and `Risen_Gunner` (Burnt Gunner model). | `_Core/Templates/Template_Summoned_Ally.json` | VERIFIED (data); this is our combat-pet base |
| Taming: wild livestock roles have `IsTameable: true` + `TameRoleChange: "Tamed_<X>"`; the tamed role is "Revered" (friendly). 18 tameable kinds (Bison, Boar, Bunny, Camel, Chicken, Chicken_Desert, Cow, Goat, Horse, Mosshorn, Mosshorn_Plain, Mouflon, Pig, Pig_Wild, Rabbit, Ram, Sheep, Skrill, Turkey, Warthog, + their babies). | `Roles/Creature/Livestock/*.json`, `Tamed/` | VERIFIED |
| Per-player owner on a tamed animal: `NPCMountComponent.getOwnerPlayerRef()` exists for mounts; a general "tamed by X" field UNVERIFIED. | jar | partial |

**Plan for our pet NPC:** our mod ships one small role per behaviour (not per pet), as `Variant`s of vanilla templates by name:
`SkyyPet_Follow` (invulnerable, ignores everyone, follows its owner like Test_Pet, teleports when far), `SkyyPet_Fight` (like
Template_Summoned_Ally: flock with the owner, attacks what the owner hits), `SkyyPet_Fly` / `SkyyPet_Swim` (same with a Fly / Swim motion
controller), `SkyyPet_Mount` (section 4). The Appearance is replaced by the scaled Model we pass at spawn. Per player: one pet out (slot 1)
+ one summon (slot 2). Despawn on logout / world change, respawn on PlayerReadyEvent. Kills count as the owner's (Pets-Spec 6).
UNVERIFIED: a role whose default Appearance differs from the Model we pass (should be fine - `spawnEntity` sets the ModelComponent
first); the owner link for a non-flock pet (fallback: our own component / map ref -> owner UUID).

### 2.3 First test (one lean round, before any pet code)

1. Skyy in creative: `/npc spawn Skeleton_Fighter` with scale 0.6 (exact argument syntax from `/npc spawn` help), then Fox at 0.8,
   Eye_Void at 0.35, Rex_Cave at 0.3, Whale_Humpback at 0.2. Look at walking, attacking and the hitbox / nameplate.
2. Same for one bird (Owl) and one fish (Bluegill) out of water.
Result decides the smallest allowed scale (`pets.scale.min`, default 0.3) and whether Option B is needed for skating.

## 3. Sources and rarity (fits Pet-Sources and Pets-Spec)

### 3.1 Rules (proposal; numbers are rows)

| Source | Which pets | Rarity | Link |
|---|---|---|---|
| Starter | Rabbit (Common) | Common | Pets-Spec 4 |
| **Bond** at the Stable | the 18 vanilla-tameable kinds (tame by feeding, vanilla) | their start rarity, Common / Uncommon only (Rare+ tameables like Mosshorn, Camel, Mouflon, Ram stay egg / quest) | Pet-Sources 3 |
| **Zone eggs** (chests, elites, events, guardians, slayers) | every pet whose Zone is Z1-Z5; the zone table rolls the rarity, then a pet of that zone and rarity | zone table | Pet-Sources 2, 4 (pools grow from 4-5 pets per zone to 15-30) |
| **Creature egg** (NEW) | each hostile / neutral family: killing that creature has a tiny chance to drop ITS egg (default 0.1% per kill, 1% from its elite) | the pet's start rarity | gives "I want a Fox pet -> hunt foxes" |
| **Fishing treasure** | every "Fishing" row (fish, crabs, Pirate Skeleton, sharks, whale) | rolled like a zone egg | Pet-Sources 4 "a pet egg later" |
| **Quest** | Horse (Stable quest, first mount), Dragon (dragon line) | fixed | locked |
| Upgrade Stones | raise rarity, per skill (R9) | up to Legendary; Mythic = dragons | locked |

No pet starts Legendary (Pet-Sources Q4). Start rarity (table column): Common = critters, small birds, farm animals; Uncommon = wildlife,
small vermin, common fish; Rare = predators, common undead, mid bugs; Epic = big or elite creatures (Yeti, Rex, Raptor, Golems, Void Eye,
Void Spawn, Werewolf, Praetorian, Aberrant Zombie, Pirate / Incandescent Skeleton, sharks, whale, Ram, Mouflon, Hawk, Skrill).

### 3.2 ~110 pets without bloat

- **Families + skins:** one pet per family (111). Other looks are skins you collect (find the Frost Skeleton = unlock the Frost skin of your
  Skeleton). Skins never change stats. (Q3)
- **Perk archetypes, not 111 perk lists:** each pet maps to ONE archetype; the archetype holds the perks and numbers (Pets-Spec 5):
  Farming, Mining, Foraging, Fishing, Melee, Ranged, Magic, Tank, Speed / Mount. Each pet adds at most one small flavour line (e.g. Fox:
  +loot from foxes; Void Eye: sees elites through walls). Balance work = 9 archetypes, not 111 pets. The 14 Pets-Spec pets keep their
  hand-made perks as the archetype templates.
- **Same XP table for all** (Pets-Spec 3); rarity changes stats only. Pet XP rule R6 (own skill + 50% of others) unchanged.
- **Pet Album** (collection book, a page in the Pets window): one page per zone, a silhouette for every pet not found yet, skins as small
  dots. Pet score (Pets-Spec 4) = unique pets x rarity; milestones give the small bonuses (magic find / health) - Collections-Spec style.
- **Server Setup:** one row block per pet (`pets.<id>.enabled / model / skins / scale / zone / rarity / archetype / sources`), so an owner
  can switch any pet off.

## 4. Mounts

| What | Status |
|---|---|
| Vanilla mountable roles: `Tamed_Horse` (anchor Y 1.6), `Tamed_Camel`, `Tamed_Ram` (`IsMountable: true`). Wild Horse / Camel / Ram and Mouflon are NOT mountable. | VERIFIED |
| How: `Template_Livestock` has a block enabled by `IsMountable`: when a Revered / Friendly player interacts (and the animal is not asleep) it plays a Status animation and runs the role action `Mount` (AnchorX/Y/Z + `MountMovementConfig`, default "Mount"). | VERIFIED |
| Engine side: `builtin.mounts` (MountPlugin, NPCMountComponent with owner PlayerRef + original role index + anchor, MountedComponent with MountController, MountedByComponent, MountInteraction, ActionMount, `/mount` and `/mountcheck` commands). | VERIFIED (classes); calling a mount from our code UNVERIFIED |
| Any creature can be a mount if its role has the Mount action: our `SkyyPet_Mount` role = Variant of `Template_Livestock` with `IsMountable: true` and a per-model anchor. The rider uses the creature's own walk / run animations. | likely; per-model anchors UNVERIFIED |
| Mount anchor at a non-1.0 scale (bigger mounts) | UNVERIFIED (anchor may not scale) |
| Flying mounts: vanilla has none (`MountController` types not checked). Pterodactyl / dragons later. | UNVERIFIED |

Mount list (size kept at 1.0x unless noted):
- **Launch (vanilla):** Horse (first mount, Stable quest), Camel, Ram.
- **Candidates (our own mount role):** Skeleton Horse (+ Armored), Mouflon, Bison, Mosshorn, Deer (Stag), Antelope, Moose (1.1x), Trillodon,
  Bear, Sabertooth, Snow Leopard, Emberwulf, Cave Raptor, Cave Rex (big), Scarak Defender, Crystal Golem, Werewolf, Crocodile.
- **Later flying:** Pterodactyl, dragons.
A mount pet in the summon slot is shown at mount size; in the pet slot (slot 1) it could show at its pet scale (Q6).

## 5. Build phases (PROJECT-RULES 4)

| # | Phase | Round size | Needs |
|---|---|---|---|
| 0 | This roster; Skyy answers section 6 | no agents | - |
| 1 | Scale test (2.3) - creative command test by Skyy, or a tiny test command | no agents / lean | - |
| 2 | Pet core: pet items, slot 1, XP, archetype buffs, Pets window + Pet Album, per-pet Server Setup rows, the 14 Pets-Spec pets + first roster batch as data | **Ultracode** (new system, saved data, items that could be lost) | 0 |
| 3 | Visible follower: spawn the shrunk vanilla model (2.1), `SkyyPet_Follow` role, despawn / respawn rules | Full round | 1, 2 |
| 4 | Sources: bond at the Stable, zone egg pools for the whole roster, creature eggs, fishing eggs, hatching | Full round (items, economy) | 2 |
| 5 | Summon slot + combat pets (`SkyyPet_Fight`, Summoned_Ally style) | Full round | 3 |
| 6 | Mounts: vanilla 3 first, then the candidates with `SkyyPet_Mount` + anchors | Full round | 5 |
| 7 | Flying + water pets (`SkyyPet_Fly` / `SkyyPet_Swim`) | Full round | 3 |
| 8 | Roster batches by zone (data only: rows + skins) | Lean round each | 2-4 |
| ongoing | Quirk's chibis swap in as new model ids (Option B), Skeleton first | art + lean | 3 |

## 6. Questions for Skyy (recommended default in brackets)

| # | Question | Default |
|---|---|---|
| 1 | Other humanoid races as pets (Goblin, Goblin Ogre, Feran, Outlander, Slothian, Saurian, Tuluk, Klops, Bramblekin, Elf, Void Necromancer)? Kweebecs and Trorks are already no. | [no, none of them] |
| 2 | How many pets at launch? | [the 14 Pets-Spec pets + the ones you named (Fox, Rat, Skeleton, Void Eye, Void slugs) + Cat / Dog / Corgi + small critters = about 30; the rest in zone batches] |
| 3 | Variants (Frost / Sand / Burnt Skeleton, bird and fish colours, golem elements) = skins of one pet, not separate pets? | [skins] |
| 4 | Families with a vanilla baby (Cow -> Calf, Pig -> Piglet ...): the pet looks like the baby, then grows into the shrunk adult at a level? | [baby until Lv 30, then shrunk adult] |
| 5 | Hostile pets' attacks: do combat pets use the creature's own vanilla attack (bite, bow, spell) with our damage numbers? | [yes, own animation, damage = % of your weapon (Pets-Spec 6)] |
| 6 | A mount pet in the pet slot (slot 1, never ridden): show it at pet size or mount size? | [pet size; mount size only in the summon slot] |
| 7 | Water pets: fish follow only while you swim, and are buff-only on land? | [yes] |
| 8 | Creature eggs: a tiny chance that a creature drops its own egg (0.1%, elites 1%)? | [yes] |
| 9 | Boss-like creatures (Shadow Knight, Hedera, Broodmother, Goblin Duke, Void Guardian Golem) as rare boss pets later? | [no for now; Shadow Knight ask again later] |
| 10 | Grooble and Bee swarm (no vanilla role / a swarm)? | [Grooble yes, Bee swarm no] |

## 7. UNVERIFIED list (for the build rounds)

1. Look of very small scales (0.2-0.35) and of walk "skating" (2.3 test).
2. `/npc spawn` scale argument syntax.
3. A mod asset pack adding `Server/Models` entries with a vanilla `Parent` (Option B / chibis).
4. Owner link for a non-flock follower; flock join from code for combat pets.
5. Mount anchors per model; mount anchor at scale; starting a mount from code; flying mount controllers.
6. Zones per creature vs the vanilla spawn files (`Server/NPC/Spawn`-style data not read).
7. Vanilla "tamed by player X" storage (for Stable bonding).
