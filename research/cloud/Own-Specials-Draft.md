# Our own special weapons - boss drops per class (draft)

Cloud draft, 2026-10-08. Paper design, no code. 21 specials of our own so every class ends with 4-6 boss specials next to The Armory's.
Every engine note is **UNVERIFIED** (no game files in the cloud). Names are working names in the SkyWynn voice (`research/cloud/Barks-Signs-Tips.md`).

## 0. Decisions this follows (`docs/answered/gear.md`, newest wins)

| Line | Lock | Used here |
|---|---|---|
| 2026-10-08 (112) | The Armory's specials are BOSS DROPS; "we can make our own specals too, so we dont have some classes with a ton more weapons than others" | the whole file |
| 2026-10-08 (113-114) | Zweihander = Warrior, Dual Swords = Assassin (loose fit, temporary) | Assassin gets real dual swords of our own (section 2) |
| 2026-10-08 (119) | The 4 Elemental swords are SHELVED until our element system; Warrior's Armory specials drop to 2 | Warrior gets 2 of ours; no special here uses an element |
| 2026-10-08 (122) | "yes to all ... draft our own ~18 specials (Assassin, Mage, Priest, Archer, Monk + Warrior)" | the per-class counts below |
| 2026-10-08 (108-110) | every weapon keeps its vanilla signature on Ability 1; wands ricochet; new families get proposals | a special never replaces a signature - its hook is a passive twist of the weapon |
| `docs/answered/classes.md` 36, 42 | 2 weapon types per class, no sharing: Mage staffs + spellbooks, Priest wands + soul orb / cage, Archer bows + crossbows, Monk Bo + fists, Assassin daggers + kunai, Warrior swords (+ longswords) + spears | each special sits in one of its class's families |
| `research/Pack-Armor-Plan.md` 3.3 c | target: 4-6 boss specials per class; our own to make: Assassin 3, Mage 4, Priest 4, Archer 4, Monk 3-4 (+ Warrior 2 after the Elementals were shelved) | the counts |
| `research/classes/Mage.md`, `research/classes/Priest.md` | Skyy's own ideas for later: "special staffs whose quick shots pierce", "a special wand whose shots pass through blocks" | Mage 1 and Priest 2 are those ideas |

## 1. Rules used for every special

- **One hook each.** A special is a normal weapon of its family (same moveset, same traversal, same signature) plus ONE passive twist. No new keys.
- **Not a class ability, not a signature.** Nothing here repeats Meteor / Starfall / Arcane Beam / Mana Barrier / Frost Nova, Sacred Heal / Sanctuary / Martyr's Grace / Shield Bubble / Guardian Spirit, Pinning Shot / Arrow Rain / Hunter's Net / Rapid Fire / Explosive Arrow, Flowing Form / Hundred Fists / Still Water / Palm Strike / Cyclone Kick, Cloak / Shadow Clone / Vanishing Act / Toxin / God Killer, Rallying Guard / Bulwark Stance / Unbreakable / Shield Shockwave / Iron Chain - nor the proposed signatures (Whirling Staff, Flurry, Kunai Fan, Page Storm) or any Echo / Follow modifier.
- **No elements** (the element system is not designed; the Armory Elementals wait for it).
- **Drop rules** (same as the Armory specials, `research/Pack-Armor-Plan.md` 3.3 b): Legendary rarity, **drop only** (no recipe), item level = the boss's level, modifiers roll through SkyyGear like any gear, arrives **unidentified** in a Mystery Bag (Loot round). Drop chance per kill default **5%** with the loot picker's class lean (your own class's special x3 weight); a slayer boss uses the slayer RNG meter instead (`research/cloud/Slayers-Spec.md` section 5). Server Setup rows: `special.<id>.boss`, `special.<id>.chance`.
- **Level spread per class:** one early (Lv 20-30), one mid (Lv 45), one late (Lv 60-70), one capstone (Lv 79+), so a class always has a special to chase.
- **Art:** our own models + textures (SkyyArmory, `.claude/skills/skywynn-art/SKILL.md` rules); a special is the family's top look with one odd detail, never a recolour of a pack item.

## 2. Assassin (3 of ours + Dual Rune Blade = 4)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| A1 | **The Fine Print** | daggers | Burnt Skeleton Praetorian (Zone 1 slayer boss "The Late Fee") | 20 | a backstab counts from the **sides** too: any hit that is not from the front gets the vanilla backstab bonus | thin grey blades with tiny stamped text along the edge | LOW-MEDIUM: the backstab check is vanilla's facing test; we widen the angle for this id (where that test lives is UNVERIFIED) |
| A2 | **Return to Sender** | kunai | Outlander Chief (Zone 3 dungeon boss) | 45 | the hold-right-click RETURN also **drags the enemy you hit with the throw** back with you (one target, lands beside you, 1 s stun) | a kunai with a short red ribbon and a wax-seal pommel | MEDIUM: teleport the hit mob with the player (same code as the Grapple "Hooks the mob" pull, UNVERIFIED); boss / mini-boss immune |
| A3 | **The Carbon Copy** | dual swords (our own, real dual-wield) | the Zone 5 Dragon | 70 | hits alternate hands; **every 3rd hit is a cross-slash** that hits everything in a 3-block arc (the single-target class's crowd answer) | two short black blades with pale blue "copy" lines; the off-hand one is the mirror image | HIGH: a dual-wield look needs a model with both blades on one item (The Armory's dual swords show one sword); the 3-hit counter + arc hit is LOW |

Why dual swords: Skyy called the Armory's dual swords "only kinda fit" and they are unfinished; A3 is the finished version in our own art, so the Assassin's loose fit is fixed by us (Pack-Armor-Plan 3.3 e).

## 3. Mage (4 of ours + 0 = 4)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| M1 | **The Long Form** | staff | The Broodmother (Zone 2 guardian) | 30 | quick shots **pierce** every enemy in a line (Skyy's own idea; staff damage, wand range stays shorter) | a staff whose head is a long rolled scroll, glowing from inside | LOW: the wand's pierce shot already exists (SkyyArmory), reuse it on a staff id |
| M2 | **Form 27-B/6, Annotated** | spellbook | The Everfrost Yeti (Zone 3 guardian; Archivist Frostwick's hall) | 45 | the book's spell leaves a **margin** on the ground for 3 s; enemies inside take **+25% from all your spells** (an amp zone for the burst class) | a frost-blue book with pencil notes in the margins, pages crackle | MEDIUM: a timed ground area + a damage-taken multiplier per mob (same bookkeeping as the Awed debuff) |
| M3 | **The Forwarding Address** | staff | The Ember Warden (Zone 4 guardian) | 60 | quick shots **home** on the enemy nearest your aim (curve up to 30 degrees, 24 blocks) | a dark steel staff with a brass envelope-shaped head and a small spinning arrow | MEDIUM: per-tick steering of our orb projectile (UNVERIFIED whether a projectile's velocity can be set in flight) |
| M4 | **The Unabridged Edition** | spellbook | The Archive Golem (The Final Audit floor 2) | 82 | the spell does **+10% per extra enemy in its area** (cap +50%) - the opposite of falloff; a crowd makes the book stronger | a fat violet Voidglass tome with too many bookmarks | LOW: count targets at cast time, scale the hit |

## 4. Priest (4 of ours + 0 = 4)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| P1 | **The Courtesy Copy** | wand | The Second-Page Guardian (Zone 1 guardian, Earthen Golem) | 20 | the piercing quick shot **heals every ally it passes through** for 10% of its damage (poke the mob, heal the tank in the line) | a mossy wood wand with a green stone and a paper tag on a string | LOW: the pierce shot already lists what it passes; add players as heal targets |
| P2 | **The Interoffice Memo** | wand | The Everfrost Yeti (Zone 3 guardian) | 45 | quick shots **pass through blocks** (Skyy's own idea; range stays 16, vanishes after 2 blocks of solid) | a white wand with an ice-blue tip and a tiny pneumatic-tube ring | HIGH: a projectile that ignores block hits for a short distance (UNVERIFIED; fallback = a short ray cast that skips blocks) |
| P3 | **Hold Music** | soul cage | The Ember Warden (Zone 4 guardian) | 60 | hold right-click on an **ally** to Bind them: your stored soul healing **flows to them per second** along the line (one ally Binding at a time; it counts against the cap; no enemy drain while it runs) | a dark cage whose soul hums orange; the ally line is a warm gold thread | MEDIUM: a Binding whose target is a player; reuses the line visual + the stored-healing pool (Soul-Orb-Spec) |
| P4 | **Next, Please** | soul cage | Ticket #1 (The Final Audit floor 6) | 94 | when a bound enemy **dies, its Binding jumps** to the nearest enemy within 8 blocks (the stored healing keeps growing) | a silver Aetherium cage with a paper ticket stuck to one point | LOW-MEDIUM: on death of a bound mob, re-target the Binding (line of sight rule applies) |

## 5. Archer (4 of ours + 0 = 4)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| R1 | **The Filing Spike** | shortbow | The Second-Page Guardian (Zone 1 guardian) | 20 | arrows that miss **stick in the ground as spikes** for 5 s; an enemy walking over a spike takes one arrow hit (a trap bow for kiting) | a dark wood bow strung with red tape, arrows with paper flights | MEDIUM: a tiny trigger area where an arrow lands (like the heal orb circle, UNVERIFIED for arrows) |
| R2 | **The Rubber Stamp** | crossbow | Scarak Overseer (Zone 2 slayer boss) | 30 | every bolt that **hits reloads one bolt** into the magazine - it never runs dry while you keep landing hits | a stubby brass crossbow with a stamp-shaped stock | LOW-MEDIUM: SkyySkills already keeps crossbows loaded; add +1 ammo on hit (UNVERIFIED how the magazine count is written) |
| R3 | **The Long Distance Call** | shortbow | Cave Rex (Zone 4 dungeon boss) | 60 | arrows **fly flat** (no drop) and gain **+1% damage per block flown** (cap +40%) - the sniper bow | a long, thin bone-and-amber bow with a string that glows faintly | MEDIUM: cancel gravity on the arrow + read its flight distance on hit (UNVERIFIED) |
| R4 | **The Final Notice** | crossbow | The Landlord (The Final Audit floor 3) | 85 | **hold instead of tap** to fire the whole magazine at once as a tight burst (6 bolts, -15% each); a tap still fires one | a heavy Voidglass crossbow with a coin-slot stock and a gold trigger | MEDIUM: a hold-release on a weapon whose signature is BigArrow - must not collide with Ability 1 (the hold is the attack key, UNVERIFIED) |

## 6. Monk (4 of ours + 0 = 4; drop one if 3 is enough)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| K1 | **The Long Queue** | Bo staff | The Broodmother (Zone 2 guardian) | 30 | **skipping-bound landings hit** everything within 3 blocks for one hit (the bounds normally do no damage) | a sand-coloured Bo with a chitin cap and a dangling queue-ticket tassel | LOW: the timed-landing event exists (Monk-Kit); add an area hit |
| K2 | **The Firm Handshake** | hand wraps | Outlander Chief (Zone 3 dungeon boss) | 45 | the combo's **power hit heals you 5% max Health** (sustain for the glass-fisted class) | white wraps with a thin blue knot at the wrist | LOW: hook the power-hit step of the wraps chain |
| K3 | **The Stamp of Approval** | gauntlets | The Ember Warden (Zone 4 guardian) | 60 | the 4th-jab **finisher slams the ground**: a 3-block ring knockback, and the gap after the finisher is halved | dark steel gauntlets with a round stamp face on each knuckle plate | LOW-MEDIUM: area knockback on the finisher step + a shorter recovery (if the recovery is an animation length, UNVERIFIED) |
| K4 | **Thank You For Waiting** | Bo staff | The Void Clerk (The Final Audit floor 1) | 79 | holding **block builds Patience**: each second blocked adds +10% to your next 3 hits (cap +50%); hitting spends it | a white Voidglass Bo with a tiny bell on one end that rings at max Patience | LOW: block-time counter + a damage buff on the next hits (right-click block exists, SkyyArmory 0.1.11) |

Claws: no special until claws exist (a later claw special = "slashes bleed", one line, when the family is built).

## 7. Warrior (2 of ours + Ghost Sword + Zweihander = 4)

| # | Name | Family | Drops from | Lv | The hook | Look (one line) | Engine risk |
|---|---|---|---|---|---|---|---|
| W1 | **The Long Arm** | spear | Outlander Colossus (Zone 3 slayer boss) | 45 | the thrown spear **returns to your hand by itself** after 2 s, hitting enemies on the way back (no walk to pick it up) | a long blue-steel spear with a chain-link ring below the head | MEDIUM: despawn the thrown projectile + re-add the item + a hit sweep on the return path (UNVERIFIED whether the vanilla throw is a projectile we can track) |
| W2 | **The Counterclaim** | shield | Cave Rex (Zone 4 dungeon boss) | 60 | a **parry window**: a block taken in the first 0.3 s refunds its Stamina and your next sword hit within 2 s does +50% | a tall amber shield with a bone rim and a stamped "DENIED" boss | MEDIUM: needs the block-hit event with timing (the Still Water counter uses a similar hook, UNVERIFIED) |

Shields are free for every class today (off-hand); W2 as a special should be **Warrior-only** (Q7) so it counts for the Warrior.

## 8. Totals per class (Armory specials + ours)

| Class | Armory specials | Ours | Total | In target (4-6)? |
|---|---|---|---|---|
| Warrior | 2 (Ghost Sword, Zweihander; 4 Elementals shelved) | 2 (W1, W2) | 4 | yes |
| Berserker | 5 (Rune Blade 1-3, Hepta Axe, Lahat Chereb) + 2 flails / whips until the new class | 0 | 5 (+2) | yes |
| Assassin | 1 (Dual Rune Blade; Armory dual swords stay out) | 3 (A1-A3) | 4 | yes |
| Mage | 0 | 4 (M1-M4) | 4 | yes |
| Priest | 0 | 4 (P1-P4) | 4 | yes |
| Archer | 0 | 4 (R1-R4) | 4 | yes |
| Monk | 0 (the Armory "Fist" item is unassigned) | 4 (K1-K4) | 4 | yes |

## 9. Who drops what (so no boss carries too much)

| Boss | Lv | Drops (ours) | Armory specials already there |
|---|---|---|---|
| Second-Page Guardian (Zone 1) | 20 | P1, R1 | - |
| Burnt Skeleton Praetorian (Zone 1 slayer) | 20 | A1 | Rune Blade stage 1 (Skeleton elite) |
| The Broodmother (Zone 2) | 30 | M1, K1 | - |
| Scarak Overseer (Zone 2 slayer) | 30 | R2 | - |
| The Everfrost Yeti (Zone 3) | 45 | M2, P2 | Dual Rune Blade |
| Outlander Chief (Zone 3 dungeon) | 45 | A2, K2 | - |
| Outlander Colossus (Zone 3 slayer) | 45 | W1 | - |
| The Ember Warden (Zone 4) | 60 | M3, P3, K3 | - |
| Cave Rex (Zone 4 dungeon) | 60 | R3, W2 | - |
| The Zone 5 Dragon | 70 | A3 | - |
| The Void Clerk (Final Audit F1) | 79 | K4 | - |
| The Archive Golem (F2) | 82 | M4 | - |
| The Landlord (F3) | 85 | R4 | - |
| Ticket #1 (F6) | 94 | P4 | - |
Trork Chieftain (Hepta Axe), Goblin Duke (Lahat Chereb), Golem_Firesteel (Zweihander) and the night undead elite (Ghost Sword) keep their Armory drops and get none of ours.

## 10. Build notes (for the round that makes them)

- One SkyyArmory item per special (own id `SkyyArmory_Special_<Name>`), the family's moveset / traversal / signature by the same prefix rules as the family, class gate through the SkyyClasses weapon table (Pack-Armor-Plan 3.3 a).
- Hooks are small per-id listeners in SkyyArmory (hit, landing, block, death, projectile tick); every number above is a Server Setup row (`special.<id>.*`, times in seconds).
- Build in level order (Lv 20-30 first: P1, R1, A1, M1, K1, R2 = 6 items, mostly LOW risk), capstone ones last with the dungeon.

## Questions for Skyy (approve / swap per item; default = keep)

1. Assassin A1 The Fine Print (side backstabs) / A2 Return to Sender (RETURN drags your target) / A3 The Carbon Copy (real dual swords, cross-slash every 3rd hit)? [keep all 3]
2. Mage M1 The Long Form (piercing staff) / M2 Annotated (amp margin) / M3 Forwarding Address (homing staff) / M4 Unabridged (more enemies = more damage)? [keep all 4]
3. Priest P1 Courtesy Copy (shots heal allies they pass) / P2 Interoffice Memo (shots through blocks) / P3 Hold Music (bind an ally) / P4 Next, Please (Binding jumps on kill)? [keep all 4]
4. Archer R1 Filing Spike (ground spikes) / R2 Rubber Stamp (hits reload) / R3 Long Distance Call (flat flight, range damage) / R4 Final Notice (magazine dump)? [keep all 4]
5. Monk K1 Long Queue (bound landings hit) / K2 Firm Handshake (power hit heals) / K3 Stamp of Approval (finisher slam) / K4 Thank You For Waiting (block builds Patience)? [keep all 4; if only 3: drop K4]
6. Warrior W1 Long Arm (spear returns) / W2 Counterclaim (parry shield)? [keep both]
7. W2 is a shield: Warrior-only as a special, or free for all like other shields? [Warrior-only]
8. Drop chance 5% per boss kill with a x3 lean to your own class, slayer bosses through the RNG meter? [yes]
9. Specials roll modifiers like normal gear (Legendary, unidentified Mystery Bag)? [yes]
10. The names (cosmic-office tone) - keep, or plainer weapon names? [keep]

## For the local session (UNVERIFIED)

- Where vanilla's backstab facing test lives and whether it can be widened per item id (A1).
- Teleporting a mob with the player on the kunai RETURN (A2) - reuse the Grapple "Hooks the mob" pull.
- A one-item dual-wield model (A3): can an item show a second blade in the off hand, or does it need an off-hand companion item?
- Projectile steering in flight (M3) and a projectile that ignores blocks for 2 blocks (P2); fallback for P2 = a block-skipping ray.
- A Binding whose target is a player (P3) and re-targeting a Binding on the target's death (P4) in the Soul Orb code.
- A trigger area where an arrow lands (R1); writing the crossbow magazine count (R2); cancelling arrow gravity + reading flight distance (R3); a hold-release on the crossbow attack key next to the BigArrow signature (R4).
- Whether the gauntlet finisher recovery is an animation length we can shorten (K3); the block-hit event with timing (W2); tracking the vanilla spear throw projectile (W1).
- `python tools/docs_check.py` printed FAIL on main before this file was added (pre-existing broken links in `art/hotbar-items/README.md`, `INDEX.md`, `RESUME.md` and the October log, all pointing at a missing backups readme or a bare file name); this file adds no new ones.
