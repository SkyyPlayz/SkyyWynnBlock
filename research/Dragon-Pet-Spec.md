# Dragon pet - build spec (SkyyPets, after 0.4.4)

Spec, 2026-10-18. Nothing built. Every number is a PLACEHOLDER and a Server Setup row (SkyWynn Menu -> Server Setup -> Pets -> Dragons,
`tools/CONFIG-CONTRACT.md`; times in seconds) unless marked BUILD-TIME. Where to look next: `INDEX.md`; pet docs `research/Pet-Eggs-Spec.md`
(hatchery), `research/cloud/Pet-Core-Spec.md` (phases 4 fight + 5 mount), `research/Nestkeeper-Pack-Check.md` (pack check), `PACK.md`
(Nestkeeper row). Answers to the questions at the end go to `docs/answered/pets.md` (`python tools/qa_append.py pets ...`).

## 0. Skyy's words this follows (word for word in `docs/answered/pets.md`, newest first)

> 2026-10-18 DRAGON PET DESIGN: "now we just need to make it work with the pet mod so it appears in the pet slot, hatches in the hatchery,
> and only appears when in the summon slot, (when young it fights with you. it getys bigger by leveling, and when leveled up enough, you
> car ride and fly it too. (and we need our elemental dragons.)"

Main-session default (same line): a summoned dragon that falls into the void / dies returns to the pet slot instead of being lost.

Also followed (LOCKED, not re-decided): R8 "ONE DRAGON PER PROFILE for now" + "dragons follow the pet rules (combat XP + 50% of other XP),
grow bigger at set levels, and can be flown from Lv 10 (growth steps and the flight level are settings)"; R6 "a fighting pet at 0 health
retreats into its slot, loses nothing, comes back after a cooldown" (60 s at Lv 1 -> 15 s at Lv 100); R7 only the summon slot fights;
2026-10-06 "for the dragons, make the inventory icon look like the dragons in the mod were using" (original icon until Aures OKs a render);
2026-10-16 "aures already gave the okay" (summon their dragon through our pet slot by id at runtime); 2026-10-18 gear.md ELEMENTS Q3
"most pets have an element" + Plain dragon = Earth, Tundra dragon = Water; 2026-10-07 "dont put any void protection on any traversal."
Elements: Earth, Thunder, Water, Fire, Air + secret Blood, Void, Light, Crystal (`research/Dragon-Pets-Idea.md` 5).

Probe results this builds on (`docs/log/2026-10.md` 2026-10-18 07:49-07:54 PROBE lines + `research/Pet-Probe-Results.md`): Nestkeeper
nests, eggs, hatching, food growth, saddle, riding and flight work in game; a ridden dragon is lost to the void. P4 model swap + extra
scale work; P6 a flock member does not attack by itself (we drive targets); P7 kill credit to the owner works; P9 DOWN (lethal hit
cancelled, clean removal) works; P10 riding comes from the ROLE, any size, code-mount works (one early try needed a retry).

Existing mods checked (PROJECT-RULES 2): Dragon Nestkeeper (packed; read-only study below); DarkMatter Mounts (learn only, not
packable: flying Fire / Frost dragons from VANILLA models, immortal mounts); Kazzy Pets & Mounts (not used here). Nothing does
"pet record + summon slot + level growth + ride"; we build ours on SkyyPets and reuse Aures' dragon look by id.

## 1. What Nestkeeper really is (read from the zip, read only)

| Fact | Where | Means for us |
|---|---|---|
| Pure assets, no Java (`IncludesAssetPack` false, no classes); ServerVersion `>=0.5.1 <0.666.0` | `manifest.json` | nothing to call; all behaviour is in role JSON |
| Stage roles `Nestkeeper_Dragon_Plain_1..4` / `_Tundra_1..4` = Variants of `Template_Nestkeeper_Dragon_1_Weakling / 2_Smalling / 3_Biteling / 4_Flyling` | `Server/NPC/Roles/` | one model id per stage: `Nestkeeper_Dragon_Plain_1..4`, `Nestkeeper_Dragon_Tundra_1..4` (`Server/Models/Beast/`) |
| GROWTH = the role SPAWNS `NextDragonStage` and DESPAWNS itself after food | Weakling template, `"Type": "Spawn", "Kind": {"Compute": "NextDragonStage"}` | their role would replace our creature with an untracked new one -> we never run their roles |
| Stages 1-3: AttitudeGroup Prey, `PlayerDefaultAttitude` Neutral, flee, `Attack` "" (no attack); Plain HP 15 (stage 1) / 40 (stage 3); stage 4: `PredatorsBig`, Revered, `IsMountable`, saddle via `DragonSaddleItemSet`, shears harvest the saddle (`HarvestDropList Drop_Saddle`) | stage roles | their roles do not fight for anyone; shears + death drop loot (`Dragon_Drop_Plain_N`) = a dupe source if we spawned their role each summon |
| Stage scale (model MinScale-MaxScale): 1 Weakling 0.30-0.35, 2 Smalling 0.5-0.6, 3 Biteling 0.8-0.9, 4 Flyling 1.5-1.6 | `Server/Models/Beast/Nestkeeper_Dragon_Plain_N.json` | our scale rows start from these (x model scale on top, P4) |
| Looks use `RandomAttachmentSets`: `Base` (7 texture variants on adults, 12 + 4 Tundra on newborns), `1_Head_Horns` (8), spikes, teeth, `Dragon_Saddle` -> `Saddle` | model JSON | engine `Model.createScaledModel(ModelAsset, float, Map)` takes the attachment ids (VERIFIED by reflect 2026-10-18) -> we PIN one look per pet and switch the saddle on |
| "Flight" = the MOUNT movement config `Nestkeeper_Jumper_Dragon` / `_Long_Jumper_Dragon` (huge jump force, almost no air drag, strong air control); the role's motion controller is Walk only | `Server/Entity/MovementConfig/` | flight is a ridden glide/leap, not a fly controller -> ours needs its own movement config (own numbers) + our fly-follow when nobody rides |
| Attacks exist as assets but are not wired into the Plain / Tundra roles: interaction `Dragon_Breath` (melee arc + `Dragon_Breath_Wind_Burst` projectile), component `Component_Instruction_Attack_Sequence_Dragon_Fire` | `Server/Item/Interactions/NPCs/Intelligent/Nestkeeper_Dragon/` | "use their dragon combat" = reference their interaction id from our role: ask Aures in the same message (section 6) |
| Egg items `Dragon_Egg_Plain` / `_Tundra` (Quality Rare, MaxStack 20): charge-use SPAWNS `Nestkeeper_Dragon_Plain_1`; `Plain_Dragon_Item` (MaxStack 1) does the same | `Server/Item/Items/Eggs/` | the egg keeps its own "hatch in hand" (cannot be removed without editing their files); our Hatchery ACCEPTS these ids too (section 2) |
| Animations per dragon: Idle, Walk, Run, Sprint, Fly, Fly_Idle, Fly_Fast, Jump, Fall, Bite, Greet, Happy, Hurt, Death*, Sleep, Laydown, Swim*, Spawn, ... | `Common/NPC/Beast/Nestkeeper_Dragon_*/Animations/Default/` | Greet / Happy for F = pet it; Bite for our hits |

Vanilla (Assets.zip, read only): `Server/Models/Elemental/Dragon_Fire.json`, `Dragon_Frost.json`, `Dragon_Void.json` (models
`Common/NPC/Elemental/Dragon_<X>/Models/Model.blockymodel` + `Texture.png`, no attachments, scale 1.25 / 1.25 / 1.0) with Fly, Fly_Idle,
Glide, Bite, Roar, breath animations. Vanilla is free to use by id / path; vanilla-derived textures are generated into our jar at build
time (the `tools/skyyart.py` recolor pattern used for the metal tools).

## 2. Egg -> Hatchery -> dragon pet

| Step | Rule |
|---|---|
| Egg items | (1) Aures' `Dragon_Egg_Plain` / `Dragon_Egg_Tundra` (wild nests, their item, used by id at runtime - allowed); (2) OUR elemental eggs `Skyy_PetEgg_Dragon_<Element>` (section 6 sources; own art). Both go in the table `tools/skyyeggs.py` `DRAGON_EGGS` (id -> dragon kind), BUILD-TIME ids, row `pets.dragon.eggs` lists the accepted ids (an owner can drop one) |
| Place | Pets -> Hatchery: dragon eggs appear in the egg grid with the other eggs; placing one uses the existing journaled place flow (`hatchery.<n> = egg|placed ms|hid|inv or void`, counted before / after). Refused with a reason when the profile already owns a dragon or has a dragon egg in the Hatchery ("One dragon per profile.") - R8 |
| Wait | row `pets.dragon.hatchSeconds` 3600 (1 h; vanilla-like "Rare" quality, longer than a Rare pet egg) |
| Hatch | roll 1 is skipped (the kind is fixed by the egg: reel 1 shows the dragon only); roll 2 = rarity from row `pets.dragon.rarity` (C/U/R/E/L/M per 10,000) default `0/0/6000/3000/900/100` (never below Rare, Mythic 1 %). Same atomic hatch (Pet-Eggs-Spec 5.2): egg consumed once, record saved before the first reel frame |
| Record | normal pet record + `pet.<id>.kind = DragonPlain | DragonTundra | DragonFire | ...`, `pet.<id>.look = Base=3;1_Head_Horns=5;...` (the attachment ids rolled ONCE at hatch, kept forever so the dragon always looks the same; missing / unknown set = rerolled and saved), `pet.<id>.dragon = 1` (index for the one-per-profile check). Unknown keys stay readable by older SkyyPets (kept as they are) |
| Hand use of Aures' egg | still spawns THEIR wild-raise dragon (food growth, no pet buffs, no summon slot) - their feature, kept (Nestkeeper-Pack-Check Q2 default). The egg's flavor text cannot be changed by us (their lang key); our Hatchery tab says "Dragon eggs hatch into your pet dragon here. Using one in your hand hatches a wild dragon instead." |

Kind rows (Pet kinds table, data rows like every kind): `DragonPlain | Combat | Rare | str:15,cd:10 + element` (Earth), `DragonTundra |
Combat | Rare | def:15,mp:10 + element` (Water), elemental kinds section 6. Role flags `fighter,mount,dragon`. Never in an egg category
list, never craftable, never fusable (one per profile; `pets.fuse` skips `dragon` kinds), CAN be pet-rebirthed (normal pet rule).
Buffs: pet slot 100 %, summon slot `pets.slot2.buffPercent` (50 %) like every pet. Element line per Wynn-Elements-Build-Spec 4.4.

## 3. Slots: where the dragon shows

| Slot | Shown | Behaviour |
|---|---|---|
| Pet slot | NOTHING in the world (Skyy: "only appears when in the summon slot"); buffs 100 % | a dragon in the pet slot is a buff pet only |
| Summon slot | the dragon creature (summon slot unlock rule unchanged: `pets.slot2.unlock`) | fights (section 4), ridden from the ride level (section 5) |
| Pets page | dragon card: stage name (Weakling / Smalling / Biteling / Flyling / Grown), "Rideable at Lv 10", element line, "Down - back in 42 s" | the summon button is allowed (role has fighter) |

Spawn by stage (PetViews, the world thread, existing reconcile loop): the creature = OUR role (section 4) + the stage MODEL by id +
the pinned attachment map + scale. Stage changes at a level-up = the existing "changed look -> old creature goes, new one comes"
(the P4 swap; a ridden dragon is dismounted first, then remounted on the new one by code - probe D3).

| Stage | Pet level (rows `pets.dragon.stage2/3/4`) | Nestkeeper model | Scale (row `pets.dragon.scale.N`) | Rideable / flies |
|---|---|---|---|---|
| 1 Weakling | 1-3 | `Nestkeeper_Dragon_<T>_1` | x1.0 of the model | no / no (walks; fights) |
| 2 Smalling | 4-6 | `_2` | x1.0 | no / no |
| 3 Biteling | 7-9 | `_3` | x1.0 | no / no |
| 4 Flyling | 10+ (= R8 "flown from Lv 10", row `pets.dragon.rideLevel` 10) | `_4` + attachment `Dragon_Saddle=Saddle` | x1.0 at Lv 10 -> x1.3 at Lv 60 (+0.6 % a level, row `pets.dragon.growPerLevel` 0.6, cap `pets.dragon.maxScale` 1.3) | yes / yes |

Checked: 0.6 % x 50 levels = +30 % -> x1.3 at Lv 60 (python3: `1 + 0.006 * (60 - 10)` = 1.3). Pet level cap 50 + 10 per pet rebirth
(SkyyPets 0.3.0): a 0-rebirth dragon tops out at x1.24 (Lv 50); a rebirth back to Lv 1 = Weakling again (the record's rebirth count
stays; row `pets.dragon.keepStageOnRebirth` true = the stage stays at the highest stage reached, recommended - question 3).

## 4. Fighting ("when young it fights with you")

Needs the generic summon-fight system (Pet-Core-Spec phase 4: Follow / Defend / Hold, DOWN + cooldown, kill credit) - not built yet.
The dragon is a Fighter kind of that system plus dragon rows.

| Part | Rule |
|---|---|
| Role | OUR role `Skyy_Pet_Dragon` (shipped in SkyyPets' jar, generated at build from vanilla templates like `Skyy_Pet_Walk`): Walk + Fly motion controllers, follow the owner, NO tame / food / harvest / drop / spawn-next-stage instructions, `DefaultPlayerAttitude` Ignore, never attacks players (row `pets.pvp` off). Name matches SkyyMobs' `*_Pet*` never-level guard and the ghost sweep. Their role is never spawned (section 1: growth spawn, loot drops, shears saddle, flee) |
| Targets | our code drives the target (P6): Follow = what the owner hits; Defend = also what hits the owner + hostiles within 12 blocks |
| Hit | the model's `Bite` animation + damage by our code = `pets.fight.damagePercent` of the owner's weapon (lock), x stage factor (row `pets.dragon.stageDamage` 0.4 / 0.6 / 0.8 / 1.0), element = the dragon's element (counts as that element's hit when the Wynn-Elements code is live) |
| Breath (Flyling) | PROPOSED: vanilla-look breath = our own interaction (vanilla particle + our damage, every `pets.dragon.breathSeconds` 8 s, cone 6 blocks). Using Aures' `Dragon_Breath` interaction by id only if Aures says yes (section 6 message) |
| Kill credit | `pets:fn:ownerOf` (0.2.5) -> SkyySacks loot + SkyyMobs top-damager credit to the owner (P7) |
| Health | dragon HP = row `pets.dragon.hp` 40 / 80 / 140 / 220 per stage x (1 + level / 100); takes damage from mobs only |
| Pass-through | the 0.2.4 Intangible + ProjectilePassthrough stay on while NOT ridden (owner shots pass); a ridden dragon is normal (probe D3) |

## 5. Ride + fly ("when leveled up enough, you car ride and fly it too")

| Part | Rule |
|---|---|
| Who | only the owner, only from `pets.dragon.rideLevel`; F on your own Flyling = mount (code-mount through `NPCMountComponent`, P10; one retry after 1 s if the component is missing). Others: "That is <owner>'s dragon." (UseEntityEvent$Pre cancel, existing) |
| Saddle | shown automatically from the ride level (pinned attachment `Dragon_Saddle=Saddle`); no saddle item needed (their saddle item stays theirs). Row `pets.dragon.saddleItem` "" = none; an owner may name an item id to require it held once (question 4) |
| Movement | OUR movement config asset `Skyy_Dragon_Glide` (BUILD-TIME; own numbers from vanilla `Mount.json` raised for long glides: JumpForce, AirDrag, AirControl, fly speeds). Never Aures' numbers. 3 presets shipped (`Slow / Normal / Fast`), row `pets.dragon.ride.preset` picks one live (an asset cannot be edited live) |
| True flight | if the glide preset does not feel like flying (probe D3), FALLBACK = our code flight: while ridden, each tick move the dragon along the rider's look (Space up, crouch down, speed row `pets.dragon.fly.speed` 12 blocks/s), the PetFly mover already used for flying pets |
| Riderless | dismount in the air -> the dragon switches to fly-follow (PetFly) and lands next to the owner |
| Stamina | none (rows later if Skyy wants a flight limit - question 5) |
| Blocked | worlds in `pets.dragon.ride.blockedWorlds` (dungeons, zone islands if "no flying on zone islands" is wanted) dismount at once; flying to dragon-only islands is the point elsewhere (`docs/answered/world.md` 2026-10-09) |

## 6. Void / death / persistence / multiplayer

| Case | Result |
|---|---|
| Dragon at 0 HP | DOWN (P9 path: lethal hit cancelled, removed cleanly, no death animation, no drop). It stays in the summon slot, comes back by itself after the R6 cooldown (60 s Lv 1 -> 15 s Lv 100). Never lost, nothing taken. A rider is dismounted first |
| Dragon below the void line | each second: Y < row `pets.dragon.voidY` (world min + 0; 0 = the engine's own void kill) or the engine removes it (out-of-world) -> treated as DOWN: back in its slot after the cooldown, chat "Your dragon flew back to its slot." The RIDER is not saved (Skyy 10-07 "dont put any void protection on any traversal") - question 6 |
| Owner dies / logs out / switches world or profile | creature removed (existing lifecycle); summon state kept; back on the next spawn tick |
| Persistence | the creature is a throwaway view (0.2 rule); everything lives in the pet record (level, stage, look, rarity, element). Ghost sweep removes any `Skyy_Pet_Dragon` loaded from a chunk (P5) |
| Multiplayer | the dragon belongs to the PROFILE; one per profile; never tradeable (pets don't trade); eggs trade (items). Other players cannot mount, pet or hit it (pvp off); its kills credit only the owner. Two players' dragons ignore each other |
| Server crash mid-ride | the rider is a player (saved by the engine); the creature is swept at load; the record never changed |

## 7. What cannot be done at runtime without editing Aures' files

1. Their egg items keep their own "hold to hatch" use (spawns their wild dragon); we can only add our Hatchery path, not remove theirs.
2. Their stage roles cannot be used as our pet: food growth spawns a NEW untracked NPC, death drops `Dragon_Drop_*`, shears drop a saddle,
   stages 1-3 flee (Prey) -> we use their MODELS under our role instead.
3. Their egg / dragon lang texts and item flavor (no tier tag on their egg; the tier-tag rule covers only our items).
4. Their wild dragons' strength / spawns (only SkyyMobs-side level or spawn-list rules by id).
5. A recolour of their textures (licence; section 8 c).
6. Their breath interaction id is technically usable from our role (a runtime id reference) - we do not until Aures agrees.

## 8. Elemental dragons ("and we need our elemental dragons")

Licence (PACK.md Nestkeeper row): All Rights Reserved; NO copied / traced / recoloured model or texture without Aures' OK.

| Option | Works? | Cost | Verdict |
|---|---|---|---|
| (a) Ask Aures for recolour permission (message below) | only if they agree; we would then ship recoloured textures of their dragon | one message, wait | send anyway (also asks breath + model-under-our-role), not the plan of record |
| (b) Our own dragon models (Quirk) | yes, fully ours | big art job: per element 1 base mesh on ONE rig + texture, 4 stage sizes by scale or 2-3 head / horn attachment variants, an animation set (list below), icons, egg art | long-term best for baby stages; later |
| (c) Runtime tint | engine: `Model` has `gradientSet` / `gradientId` (+ per attachment; VERIFIED by reflect + 21 vanilla models use `GradientSet`), BUT a gradient only maps textures painted as gradient masks (UNVERIFIED on Aures' full-colour textures) and it is still a recolour of their look under the licence | small code | NOT recommended (licence + unknown look) |
| (d) NEW, found here: VANILLA dragons | vanilla `Dragon_Fire` (Fire), `Dragon_Void` (secret Void) by id, scaled 0.3 -> 1.0 by level; Thunder / Air / Blood / Light / Crystal = build-time recolours of the vanilla Fire / Frost textures (`tools/skyyart.py recolor`, vanilla model by path - the metal-tools pattern, generated into the jar, nothing vanilla committed). Vanilla rig has Fly / Glide / Bite / Roar animations | small: textures generated, our own Model JSONs | RECOMMENDED now |

RECOMMENDED: (d) now, plus (a) sent in parallel, (b) later for proper baby stages. Element map (no duplicates - PROJECT-RULES 2, one
dragon per element; question 1):

| Element | Dragon | Model | Growth |
|---|---|---|---|
| Earth | Plain dragon (Aures) | `Nestkeeper_Dragon_Plain_1..4` | 4 real stages |
| Water | Tundra dragon (Aures) | `Nestkeeper_Dragon_Tundra_1..4` | 4 real stages (vanilla Dragon_Frost NOT used for Water: duplicate) |
| Fire | Fire dragon | vanilla `Dragon_Fire` | scale only |
| Thunder | Storm dragon | vanilla Fire mesh by path + generated yellow / violet texture | scale only |
| Air | Sky dragon | vanilla Frost mesh by path + generated pale white / teal texture | scale only |
| secret Void | Void dragon | vanilla `Dragon_Void` | scale only |
| secret Blood / Light / Crystal | later | recolours of the vanilla meshes | scale only |

Vanilla dragon young look: x0.30 at Lv 1 -> x1.0 at Lv 10 (linear, rows `pets.dragon.vanilla.scaleLv1` 0.3) then the same +0.6 % / level
growth. Mount anchor for vanilla meshes: row `pets.dragon.anchor.<Kind>` "x,y,z" (probe D7 finds it).

Elemental egg sources (until the Zone 5 dragon boss / quest line of `research/Dragon-Pets-Idea.md`): `Skyy_PetEgg_Dragon_<Element>` drops
from the Fire / Frost dragon bosses (SkyyMobs `bosses.roles` `Dragon_*`, chance row 1 %), never craftable, Bazaar never, Auction House
yes (item). Secret elements: no source yet.

(b) art list for Quirk (for the record; one rig = the VANILLA dragon rig so vanilla animations are reused and nothing of Aures' is traced):
per element 1 mesh fitting the vanilla `Dragon_Fire` bone names + 1 texture (64 or 128 px, the vanilla density) + optional young head /
horn attachments (2-3); animations reused from vanilla (Idle, Walk, Run, Fly, Fly_Idle, Glide, Jump, Fall, Bite, Roar / breath, Hurt,
Sleep) - new ones only for Greet / Happy (F = pet it); a saddle attachment; a 64 px inventory icon per dragon (original, pets.md 30); a
dragon egg item model + texture per element (our round egg model, element colour).

### Message to Aures (Skyy sends; Discord https://discord.gg/aSRPHxHKPg)

> Hi Aures! Thanks again for letting SkyWynn summon your Nestkeeper dragons through our pet slot. We have it planned: your Plain and Tundra
> dragon models show as a player's pet dragon (by id at runtime, nothing copied or re-uploaded, your mod installed from CurseForge).
> Three quick questions:
> 1. Is it OK that we show your dragon MODELS (`Nestkeeper_Dragon_Plain_1..4` / `Tundra_1..4`) under our own pet AI role, so the pet
>    grows by pet level and does not drop loot every time it is summoned?
> 2. May our pet dragon use your `Dragon_Breath` attack interaction by id (again nothing copied)?
> 3. Would you allow recoloured versions of your dragon textures for elemental dragons (Fire, Thunder, Air and a few secret ones),
>    credited to you in our pack? Totally fine if not - we would use our own art.
> Thank you! - Skyy (SkyWynn)

## 9. Builder split (one mod per builder) + rounds

| Round | Mod / file (one builder each) | What | Size (PROJECT-RULES 4) |
|---|---|---|---|
| D0 | main session + Skyy (no build; `/npc` + Server Setup look rows, or a SkyyPetProbe 0.2 lean round) | probes D1, D2, D7, D9 | lean |
| D1 | SkyyPets (Opus) | Pet-Core-Spec PHASE 4 for every Fighter kind: `Skyy_Pet_Fight` role, target driving, Follow / Defend / Hold, DOWN + level cooldown, kill credit | full (several systems; after Pets 0.4.4 elements) |
| D2 | SkyyPets (Opus) + `tools/skyyeggs.py` DRAGON_EGGS (same builder) | dragon kinds (Plain, Tundra), Hatchery accepts dragon eggs, one per profile, dragon rarity row, pinned look, stage by level, `Skyy_Pet_Dragon` role, void / DOWN return, Pets card, Server Setup > Pets > Dragons rows, harness | full (saved data, items) |
| D3 | SkyyPets (Opus; Fable if the code flight is hard) | PHASE 5 riding (Horse / Camel / Ram too) + dragon ride from Lv 10 + `Skyy_Dragon_Glide` presets + code-flight fallback + riderless fly-follow | full |
| D4 | art (cloud, skill `skywynn-art`; files under `art/dragons/` + a `tools/skyyart.py` recipe) | Thunder / Air (+ later secret) textures generated from vanilla Fire / Frost textures; original dragon icons (Plain, Tundra, Fire, Thunder, Air, Void); dragon egg icons | lean (art) |
| D5 | SkyyPets (Opus) | elemental kinds (Fire, Thunder, Air, Void) on vanilla meshes + our Model JSONs + vanilla young scale | full |
| D6 | SkyyMobs (Opus) | elemental dragon egg drop from `Dragon_*` bosses (`pets:fn:give egg` or the item drop path) | lean |

Cross-check after each: `python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py`, smoke test.
Rollback notes for `tools/deploy_set.py` (main session): D2 FLOOR - a dragon pet record is an unknown kind below D2; keep the version
once a dragon is hatched (same as the 0.4.3 note). D2 ships a new role in the jar -> the 0.2 REMOVAL FLOOR applies (pets off first).

## 10. Probes (before D2 / D3 / D5)

| # | Probe | Pass |
|---|---|---|
| D1 | Server Setup > Pets > Pet looks: a summon-slot Wolf with look `Nestkeeper_Dragon_Plain_1 | 1 | walk`, then `_2`, `_3`, `_4` | each stage shows, walks, idles, no flee / food particles (our role), nameplate OK |
| D2 | `createScaledModel(asset, scale, Map)` with a fixed `Base` / horns id and `Dragon_Saddle=Saddle` (probe command) | same look after 3 re-summons; saddle visible only when set |
| D3 | code-mount on `Skyy_Pet_Dragon` + `Skyy_Dragon_Glide`: walk, jump, glide over a gap; compare with Nestkeeper's own ride | feels like flying -> keep; not -> code flight (5) |
| D4 | dismount mid-air -> fly-follow; ride below the void line -> DOWN + return after cooldown | dragon never lost |
| D5 | Fighter target driving + Bite + damage on a Zone 1 mob, kill credit | mob dies, owner gets loot / XP |
| D7 | vanilla `Dragon_Fire` / `Dragon_Void` at x0.3 / x1.0 under our role: animations, hitbox, mount anchor | usable as pets + mounts |
| D9 | view each of the 7 adult `Base` variants (and Tundra) pinned | if a variant reads as another element, it can be that dragon's look AS IS (no recolour) |

## 11. Questions for Skyy (popups; defaults in brackets)

| # | Question | Default |
|---|---|---|
| 1 | Elemental dragons: Earth = Aures' Plain, Water = Aures' Tundra, Fire = vanilla Fire dragon, Thunder / Air = recoloured vanilla dragons, Void = vanilla Void dragon (secret)? | [yes; also send Aures the message] |
| 2 | A dragon that dies or falls into the void: stays in the SUMMON slot and comes back after the pet cooldown (60 s -> 15 s), or moves to the pet slot? | [stays in the summon slot, comes back after the cooldown] |
| 3 | Stages: Weakling Lv 1, Smalling Lv 4, Biteling Lv 7, Flyling + ride + fly Lv 10, then it keeps growing to x1.3; after a pet rebirth it keeps its stage? | [yes, keeps its stage] |
| 4 | Riding needs no saddle item (the saddle just appears at Lv 10)? | [no item needed] |
| 5 | Flight limit (stamina / time) or free flight? | [free flight] |
| 6 | Riding into the void: dragon returns, rider falls (no void protection, your 10-07 rule)? | [yes, rider falls] |
| 7 | Hatch time 1 h and rarity Rare-Mythic (Rare 60 %, Epic 30 %, Legendary 9 %, Mythic 1 %) for every dragon egg? | [yes] |
| 8 | Using Aures' egg in your hand still hatches their wild dragon (no buffs); the Hatchery makes your pet dragon - keep both? | [keep both] |

## 12. UNVERIFIED (checked in the probes above)

Their model ids load under our role (D1); pinned attachments survive re-summons (D2); our glide config flies (D3); vanilla dragon anchors
and young scale (D7); the engine void kill reports a removal we can see (D4); gradient tint on non-mask textures (not planned).
