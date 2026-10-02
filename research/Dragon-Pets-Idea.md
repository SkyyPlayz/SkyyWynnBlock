# Dragon pets, Zone 5 and dragon-only islands - IDEA (later game, not planned yet)

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 8.

Skyy's thought dump, 2026-10-01 ("more of a thought dump than a prompt"). Kept here so nothing is lost. Nothing is decided or scheduled.
Dragons are the top tier of the one pet system (research/Pets-Idea.md, agreed 2026-10-01). Related: research/SkyyWorldGen-Plan.md (zone islands, zone bands Z1 1-20, Z2 20-30, Z3 30-45, Z4 45-60, "more past 60").

## Skyy's ideas, in order

1. **Dragon boss and egg.** The final zone boss is a dragon. Beating it (a quest reward) gives a **dragon egg**.
2. **First version: hatch by zone.** Put the egg on a pedestal at the summit of an island; the island's zone picks the element:
   Zone 1 nature, Zone 2 sand / dust / wind (desert), Zone 3 ice / frost, Zone 4 fire / lava.
3. **Zone 5.** The caves under Zone 4 have dinosaurs: take that biome, add content, and make it **Zone 5**, with the dragon as the
   Zone 5 boss (more fitting). Open: Zone 5's element if hatching stays zone-based, or limit dragons to 4 elements.
4. **Second version (Skyy leans this way): a quest line.** Take the egg to a specialist (or a mad scientist). They send you to collect
   items. When you bring them back you **choose the element**; that choice decides the last item and the special place where it hatches:
   find the location, fight through a **mini dungeon**, hatch the dragon there.
5. **Elements = the Wynncraft set:** Earth, Thunder, Water, Fire, Air. **Secret elements** later, with no quest or explanation - players
   figure them out. First idea: **Blood** (a life-steal dragon). **Skyy 2026-10-01: also plan Void, Light and Crystal** as secret
   elements, so the secret set is **Blood, Void, Light, Crystal** (9 dragon elements in all: 5 quest elements + 4 secret ones).
6. **The dragon grows.** It starts small and grows as it levels, helps you in combat, and at about **level 10 you can fly on it**.
7. **Dragon-only islands.** Smaller islands scattered around that you can only reach on dragon back (at least on a server; solo is harder).

## Notes from the main session (2026-10-01)

- **The game already has most of the pieces (checked in Assets.zip, read-only):**
  - Dragon bosses: `Server/NPC/Roles/Boss/Dragon_Fire.json` and `Dragon_Frost.json` - a Fire and a Frost dragon already exist as boss
    roles (models + attacks to reuse for the boss and as the look of fire / frost pets; the other elements need recolours or new models).
  - Dinosaurs for Zone 5: `Rex_Cave`, `Raptor_Cave` (Creature/Reptile), `Pterodactyl`, `Archaeopteryx`, `Tetrabird` (Avian/Raptor),
    `Trillodon` (Creature/Mythic), and the Zone 4 cave jungle spawn lists `Spawns_Zone4_Jungles_Animal.json` / `_Predator.json`.
    So a "lost world" Zone 5 (about Lv 60-75, the "more past 60") can start from vanilla mobs.
- **Quest-line hatching (idea 4) is the stronger path:** the element no longer depends on how many zones exist, every player can pick
  any element from one egg, and the mini dungeon gives each element its own trip. It needs the quest system (not built yet) and
  SkyyDungeons.
- **Elements:** Earth, Thunder, Water, Fire, Air is the whole Wynncraft set - nothing missing (Wynncraft's non-elemental damage is called
  Neutral). Secret element ideas next to Blood: Shadow / Void, Light / Holy, Crystal. SkyyGear already has single-element damage %
  (Equipment only) - a dragon's element could boost the matching element.
- **Hard parts (UNVERIFIED, need research before any plan):** a pet that follows and fights (NPC companion AI), growing in size with its
  level (model scale per level), and especially **flying mounts** - whether Hytale's mount system allows a rideable flying NPC.
- **Solo and dragon-only islands:** with SkyyWorldGen each zone island is its own world, so small sky islands can be generated in the
  void around a zone island inside the same world - reachable only by flying, in solo too. The gate is just "no /fly on zone islands"
  (already in the plan) plus "can fly only on a dragon".

## Open questions (for when this becomes a plan)

1. Zone 5 (the dinosaur cave world) - yes, as the dragon's zone? Level band?
2. Hatching: quest line with a chosen element (recommended), or by zone?
3. How many dragons per player / profile, and can the element be changed later?
4. Dragon level: its own XP (from fighting with you), or tied to a skill?
