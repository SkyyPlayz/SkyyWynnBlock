# Ability input design - keys, combos and hotbar ability items (flow first)

Cloud draft, 2026-10-08. Design only, no code. It answers "how does a player TRIGGER a class ability so it feels seamless", not what
the abilities do (`research/classes/*.md`, `research/cloud/Class-Ability-Spec-Draft.md`) nor how the engine runs them
(`research/cloud/Class-Ability-Engine-Spec.md`). Marks: **VERIFIED** (read in our scripts / the jar by the local session), **PROBE**
(SkyyKeyProbe 0.1 must confirm it, section 6), **PROPOSED** (a default for Skyy to accept or change).

## 0. Decisions this follows (`docs/answered/classes.md`, newest wins)

| Line | Decision | What this spec does with it |
|---|---|---|
| 151 | Roll stays on the SPRINT TAP; never put the roll on an Ability key; never touch Skyy's own binds | sprint is never an ability trigger; no spec may assume a rebind |
| 152 | No new client keys; Skyy: "combos and hotbar ability items sound good but we will need to carefully design how they work to make the flow easy, and seamless. (this also lets us make changes to how the class abilities work mid air vs crouching." | sections 1-3: combos = the SAME ability behaves differently grounded / crouching / mid-air; hotbar ability items as the second trigger |
| 31, 47, 54 | built on runes; 2 class abilities equipped (the two rune lines); 4 owned, 2 equipped | Ability2 = line 1, Ability3 = line 2; nothing here adds a third equipped slot by default (Question 2) |
| 103-106 | one hold = the charged traversal that is also the attack; every weapon's traversal doubles as its attack | Primary hold stays the traversal; Secondary stays block / grapple; abilities never use clicks |
| 150 | Monk: free air jump by CROUCH (the jump key in mid-air is not seen); Plunge Punch = crouch near the apex | crouch in mid-air belongs to movement, never to abilities (section 4) |
| `docs/answered/ui.md` 66 | servers can catch Ability1-3, Use, Pick, Dodge, SwapTo / SwapFrom + movement states; SkyyKeyProbe 0.1 approved | the probe list in section 6 decides what is reliable |
| `docs/answered/skills.md` 52, 89 | Double Jump = jump again in mid-air (crouch stays an admin override); roll = sprint tap, 8 directions | conflicts in section 4 |
| `research/Hytale-Runes-Research.md` 2.3 | on 0.7 "Use Ability 2 / 3" cast rune line 1 / 2 while holding ANY item; Ability1 stays the Signature; crossbow reload moves to a new Ability4 | the 0.7 route in sections 1 and 7 |

The whole idea in one line: **two keys, three stances.** Ability2 and Ability3 are the only ability keys a player has; what they do
depends on whether you are standing, crouching or in the air. Hotbar ability items are the second way to fire the same things for
players who prefer clicking a slot (few mouse buttons, controller, or a third action that has no key).

## 1. The input map

### 1.1 Keys (what the client can send; VERIFIED list from `docs/answered/ui.md` 66)

| Client action (Skyy's bind) | Meaning in SkyWynn | Owner today |
|---|---|---|
| Primary hold (left mouse) | the weapon's charged TRAVERSAL = its attack; tap = normal hit / quick shot | SkyyArmory (built) |
| Secondary (right mouse) | block / guard; crossbow grapple; Soul Orb binding | SkyyArmory |
| Ability1 (Mouse 5) | the weapon SIGNATURE (vanilla charged meter) - **kept, never a class ability** | vanilla / SkyyGear |
| **Ability2 (Q)** | **class ability line 1** (A1 or the picked A1-alt) | SkyyClasses (this spec) |
| **Ability3 (E)** | **class ability line 2** (A2 or A2-alt) | SkyyClasses (this spec) |
| Use (F) | doors, benches, NPCs - **not used** for abilities (it fires on blocks first) | vanilla |
| Pick (middle mouse) | nothing in adventure mode - **reserved** as an optional extra trigger (loadout swap) once PROBE K8 says it fires | later |
| HotbarSlot1-9 / scroll (SwapTo / SwapFrom) | hotbar ABILITY ITEMS: selecting the slot casts (section 2) | SkyyClasses |
| Sprint (Mouse 4, held) | sprint; a TAP = the roll (SkyySkills 0.4.20) - **never an ability modifier** | SkyySkills |
| Crouch (Left Shift) | stance modifier for abilities on the ground; movement uses it in the air (Plunge, Monk air jump) | shared (section 4) |
| Jump | movement only (double jump); not seen in mid-air by the server | SkyySkills |

### 1.2 Stances (the state the server reads at the moment the key fires)

| Stance | Read as | Rule of thumb for the variant |
|---|---|---|
| **Grounded** | onGround, not crouching (sprinting or rolling counts as grounded) | the STANDARD cast, aimed where you look |
| **Crouching** | onGround + crouching held >= `abil.crouchMinMs` (100 ms) before the press | the SELF / PLACED-HERE / PRECISE version; **never moves you** |
| **Mid-air** | not onGround for >= `abil.airMinMs` (150 ms) (jumping, falling, gliding, after a traversal); crouch in the air is ignored | the BELOW-YOU / ON-LANDING / MOBILE version |
| Swimming, mantling | treated as grounded | no special variant |

Priority when states overlap: **mid-air > crouching > grounded.** A variant that is not designed for an ability falls back to the
grounded cast (so every ability works from day one with one variant, and variants are added class by class - section 7).
Variants are **sidegrades**: same Mana / Stamina, same cooldown, same ability level and modifiers; they change shape, not power
(`research/cloud/Class-Ability-Spec-Draft.md` section 5 budgets stay valid).

### 1.3 Per class (Ability2 = line 1, Ability3 = line 2; A1-alt / A2-alt take the same key when equipped)

| Class | Ability2 (line 1) | Ability3 (line 2) | Primary hold (traversal, built / planned) |
|---|---|---|---|
| Warrior | Rallying Guard (alts: Bulwark Stance / Unbreakable) | Shield Shockwave (alt: Iron Chain) | sword / spear vanilla moves |
| Archer | Pinning Shot (Arrow Rain / Hunter's Net) | Rapid Fire (alt: Explosive Arrow) | bow Escape hop; crossbow Grapple Bolt (right click) |
| Mage | Meteor (Starfall / Arcane Beam) | Mana Barrier (alt: Frost Nova) | staff blink + trail; spellbook Levitate |
| Priest | Sacred Heal (Sanctuary / Martyr's Grace) | Shield Bubble (alt: Guardian Spirit - passive, the key does nothing) | wand hop + orb; Soul Orb Wings of Fate |
| Berserker | Enrage (Blood Frenzy toggle / Warlord's Banner) | Whirlwind (alt: Earthsplitter) | axe Whirlwind Dash; battleaxe Lunge; club Bull Rush; mace Earthshaker |
| Monk | Flowing Form (Hundred Fists / Still Water) | Palm Strike (alt: Cyclone Kick) | Bo Pole-Vault + bounds; fists Rising Strike + Plunge (crouch) |
| Assassin | Cloak + First Strike (Shadow Clone / Vanishing Act) | Toxin (alt: God Killer) | dagger Shadow Step; kunai throw-teleport |

Rune route on 0.7 (`research/cloud/Class-Ability-Engine-Spec.md` 3.2): the engine mirrors the two equipped abilities into rune slots
0 and 3, so the vanilla keys and HUD do the key work. On 0.6.8 the same two keys reach us through an entity-level `Interactions`
override on the player (the Perfect Dodges way, VERIFIED API) - section 7, phase I3. Either way the server sees the stance at the
press and picks the variant; **nothing in this spec needs a third key.**

## 2. Hotbar ability items

An ability item is a soulbound hotbar item that casts one thing when you SELECT its slot, then puts you back on your weapon.

| Rule | Design |
|---|---|
| What it casts | by default a MIRROR of an equipped line ("Meteor" item = the same Meteor as Ability2, same cooldown, same stance variants); plus UTILITY items with no key of their own: **Loadout** (next saved rune loadout, later), **Hints** (replay the class tutorial), later pet / emote calls |
| Select = cast | the slot's `SwapTo` interaction fires -> the engine casts with the stance read at that moment -> the hotbar jumps back to the weapon slot you came from (`abil.items.returnMs` 0 = at once). PROBE K5 / K6 |
| Cooldown on the item | the item's durability bar = the cooldown fill (max 100, refilled every second; PROBE K7); fallback: stack count = whole seconds left and the name reads "Meteor - 4 s"; ready = full bar + the ready ping (section 3) |
| Weapon rule | the cast uses the weapon you came FROM (the vanilla rune rule "a weapon in hand"): no weapon on that slot -> refuse "Hold a class weapon first", stay on the item, no cooldown spent |
| Empty return slot | the engine remembers the LAST WEAPON SLOT; if it is empty now (you dropped the weapon) you stay on the item and get the refusal above |
| In a menu | no cast while any page / inventory is open (a drag in the inventory also raises SwapTo - PROBE K5); after closing a page the first 250 ms are a dead zone |
| One per slot | one ability per item, one item per ability; a second copy is deleted on pickup (count before / after, like the rune mirror guard) |
| How players get them | the Abilities page (inline, vanilla look) has "Put on hotbar" per owned ability + per utility; `/abilityitem <name>` for testing; free, no durability loss, re-issued any time |
| Where they may live | hotbar + inventory only; chests, trades, Bazaar, AH, drops refuse them (`InventoryChangeEvent` guard puts them back); profile switch / class change removes them and re-issues on request; death keeps them |
| Do they count toward the hotbar | yes - they take a real slot each (9 slots total); recommended use is 0-2 items; the Abilities page warns "this takes a hotbar slot" once |
| Arranging | drag like any item; the engine does not care which slot |

When to use an item vs a combo:

| Want | Use |
|---|---|
| the same ability, hands on the mouse, mid-fight | the key (Ability2 / Ability3) + stance |
| a third ACTION with no key (loadout swap, hints, pet, emote) | an ability item |
| a controller or a 3-button mouse, or Ability keys given to another mod by the player | ability items for both lines (`/settings` "cast with items only") |
| a backup cast of an owned-but-not-equipped ability | NOT by default (keeps "2 equipped" true); Question 2 offers it as a server toggle |

## 3. Flow rules (so it feels seamless)

| Rule | Design |
|---|---|
| Rising edge only | one cast per press; holding the key never repeats (vanilla `RequireNewClick`; PROBE K14); a held key that was pressed before the cooldown ended does nothing |
| Stance sampled at the press | the variant is decided at the press, never re-read during the cast (a Meteor cast on the ground stays grounded even if you jump) |
| No accidental crouch casts | the crouch variant **never moves you and never costs more** - so sneaking near a ledge and pressing a key is always the safe version (self heal, barrier on me, rooting palm); a crouch pressed in the same frame as the key counts as grounded (`abil.crouchMinMs`) |
| No accidental air casts | stepping off a ledge counts as grounded for the first 150 ms (`abil.airMinMs`); the roll, mantle and swim never count as air |
| Buffering | a press in the last `abil.bufferMs` (500 ms) of a cooldown, or during a traversal's animation, is queued (queue of ONE, newest wins) and fires the moment it may; the queue clears on death, page open, class / profile switch |
| Refusals | cooldown / no Mana / wrong weapon = the vanilla fail sound + a short notification ("Ready in 4 s", "Not enough Mana"), at most one line per second; never a chat line |
| Feedback on a cast | the ability's own cast sound + particles; the HUD slot (vanilla rune HUD on 0.7, SkyyHud Abilities widget otherwise) starts its fill; the ability item's bar empties |
| Ready indicator | when a cooldown ends: a soft "ready" tick sound + a 0.4 s flash of the HUD slot / item (both per-player toggles); toggles (Blood Frenzy, Flowing Form) show their stacks in the widget text ("Frenzy 17") |
| First use (tutorial hint) | the first time a profile equips an ability: one notification per stance over three casts - "Press your Use Ability 2 key: Meteor", then "Crouch + key: Meteor on yourself", then "In the air: Meteor below you" (the server cannot read the player's binds, so it names the ACTION, and `/keys` lists the actions to look up in Settings -> Controls); shown once per ability, "Hints" toggle |
| Dead keys | the key of a passive (Guardian Spirit) shows "Passive - always on" once, then silent |

### 3.1 Stance variants per class (PROPOSED; 2 per class to start, grounded = the designed ability)

| Class | Ability | Grounded (designed) | Crouching (self / placed here / precise) | Mid-air (below / on landing / mobile) |
|---|---|---|---|---|
| Warrior | Rallying Guard | party circle + taunt | **Hold the Line**: taunt only, 2x the taunt radius, no party reduction (you want the mobs, not the buff) | **Rally on landing**: the circle forms where you land, 1 s later |
| Warrior | Shield Shockwave | 6-block cone stun | **Ring**: 360 degrees, 3 blocks, same stun | **Ground Pound**: cone becomes a 4-block circle under your landing spot |
| Archer | Pinning Shot | piercing arrow where you look | **Steady Aim**: +10 blocks range, +1 pierce, you stand still 0.5 s | **Rain Pin**: 3 arrows fan down, root in a 3-block patch below you |
| Archer | Rapid Fire | 15 arrows in 3 s | **Braced**: 15 arrows in 2 s, you cannot move | **Hover Fire**: slow fall while the arrows go (the bow Escape rhythm) |
| Mage | Meteor | aimed spot within 25 | **On me**: lands on you, you take none of it | **Under me**: lands where you will land |
| Mage | Mana Barrier | dome placed where you look | **Pocket dome**: 4-block dome centred on you | dome placed at your landing spot |
| Priest | Sacred Heal | circle around you | **Kneel**: 1 s channel, +20% heal, you stand still | **Beacon**: the circle drops where you land |
| Priest | Shield Bubble | placed where you look | **Around me** (the Follow modifier still makes it move) | placed below you on landing |
| Berserker | Enrage | party + self buff picked once | **Lone Rage**: self only, +10 points peak, no party | **War Leap**: the buff starts when you land, allies picked then |
| Berserker | Whirlwind | spin 3 s, move freely | **Grinder**: no movement, ticks every 0.4 s | **Spinning Drop**: the spin starts on landing with a 1.0 H slam |
| Monk | Palm Strike | strike + 4-block knockback | **Rooting Palm**: no knockback, stun +0.5 s (keep them for the combo) | **Falling Palm**: strike down, the enemy is knocked DOWN not back |
| Monk | Flowing Form | aura starts at 0 stacks | **Centred**: starts with 3 stacks, aura 4 blocks | starts on landing, the first bound after it is free |
| Assassin | Cloak + First Strike | cloak 8 s | **Still Shadow**: cloak +3 s while you do not move; moving ends the bonus | **Silent Landing**: cloak + no fall damage + no landing sound |
| Assassin | Toxin | vial thrown where you look | **Pool**: cloud at your feet | **Drop**: cloud below you, lands 0.3 s earlier |

Not every ability needs three: an ability without a designed variant uses the grounded one. Skyy picks per class as they test.

## 4. Conflicts

| With | What happens | Rule |
|---|---|---|
| The roll (sprint TAP, SkyySkills 0.4.20) | sprint is held by Skyy; a tap rolls | abilities never read sprint; a key pressed during the roll = grounded cast, the roll is never cancelled; Skyy's binds stay as they are (line 151) |
| Double Jump (jump in mid-air; `acro.doubleJump.trigger` may be `crouch` on some servers) and the Monk's free air jump by crouch, Plunge Punch (crouch near the apex) | all read CROUCH in the air | abilities ignore crouch while airborne (mid-air > crouching), so crouch in the air always belongs to movement; PROBE K11 confirms the airborne flags during the roll and the first 100 ms of a jump |
| Weapon Signature (Ability1) | vanilla charged meter | untouched; never a class ability; SkyWynn keeps it (line 152) |
| Crossbow reload = Ability3 on 0.6.8 (vanilla crossbow JSON; 0.7 moves it to Ability4) | an Archer with a crossbow pressing Ability3 reloads instead of casting line 2 | on 0.6.8 the entity-level override wins if PROBE K15 says so; if not, Archers cast line 2 with the ability item until 0.7; on 0.7 the rune route fixes it |
| Vanilla weapons / pack mods that bind Ability2 / Ability3 on items | on 0.7 "Use Ability 2 / 3 always go to the rune" while any item is held (VERIFIED), so those item bindings go dead for everyone with or without us; on 0.6.8 our player-level override hides them while a class is set | local task: grep every PACK.md mod's item JSON for `Ability2` / `Ability3` before phase I3 and list what breaks; no current SkyWynn item binds them (VERIFIED) |
| Vanilla runes on 0.7 | a classed player slotting a vanilla rune | cancelled + the weapon-lock popup (engine spec Question 2 default) |
| Use key (F) | fires on the block / NPC in front first | never an ability key |
| Pick (middle mouse) | nothing in adventure mode | reserved; PROBE K8 |
| Pages / inventory open | SwapTo from drags, keys pressed in a menu | no casts while a page is open + a 250 ms dead zone after |
| Traversal in flight (blink, hop, vault, grapple pull) | a key during the move | mid-air variant if airborne; buffered if the engine says "busy" (the traversal's animation lock) |
| Profile / class switch, death | stale states | queue + stances reset; ability items re-issued per profile (PROFILES-CONTRACT rule 1) |

## 5. Server Setup and player Settings

Server Setup -> Classes -> Ability input (`tools/skyycfg.py`, times in SECONDS, all live):

| Key | Label | Default | Range |
|---|---|---|---|
| abil.input | Ability input (keys + /cast, keys only, /cast only) | both | choice |
| abil.combos | Stance variants on | on | on / off |
| abil.combos.crouch | Crouch variants | on | on / off |
| abil.combos.air | Mid-air variants | on | on / off |
| abil.crouchMinMs | Crouch held before a press counts (ms) | 100 | 0-500 |
| abil.airMinMs | Airborne before a press counts (ms) | 150 | 0-500 |
| abil.bufferMs | Press buffer (ms) | 500 | 0-1000 |
| abil.items | Hotbar ability items on | on | on / off |
| abil.items.returnMs | Return to the weapon after (ms) | 0 | 0-1000 |
| abil.items.third | Items may cast an unequipped ability (Question 2) | off | on / off |
| abil.items.cdMult | Cooldown x for an unequipped cast | 1.5 | 1-3 |
| abil.readyPing | Ready sound + flash | on | on / off |
| abil.hints | First-use hints | on | on / off |
| abil.refuseMs | Refusal notice at most every (ms) | 1000 | 250-5000 |

Player `/settings` (per profile, under Classes): crouch combos on / off; mid-air combos on / off; ability items on / off; cast with
items only (keys ignored - controller mode); ready sound; ready flash; hints (reset = replay); refusal notices; return to weapon
after an item cast. Each toggle is one line with a default, like the crossbow switches (`docs/answered/classes.md` line 87).

## 6. PROBE list - what SkyyKeyProbe 0.1 must answer (each with the fallback if it fails)

| # | Question | Decides | If it fails |
|---|---|---|---|
| K1 | Which InteractionTypes reach the server from the Key Tester item: Primary, Secondary, Ability1, Ability2, Ability3, Use, Pick, SwapTo, SwapFrom (+ Held / Wielding / Equipped / Dodge) | the whole map | abilities stay on /cast + items |
| K2 | The default bind of each type (client.lang / settings) so hints can say "Q / E" on a stock client | hint wording | hints name the action only |
| K3 | The movement states seen at the moment each type fires (crouching, sprinting, jumping, falling, onGround, rolling, gliding, swimming, mantling) | stances | combos off (`abil.combos`) |
| K4 | Do Ability2 / Ability3 fire while crouching, while sprinting, in the air, during the roll | crouch / air / roll rules | the blocked stance loses its variant |
| K5 | Does SwapTo fire on a number key, on scroll, on a click in the hotbar, AND on an inventory drag | item cast guard | items cast on Primary click instead of select |
| K6 | Can the server change the selected hotbar slot (set it back to the weapon) | auto-return | items stay selected, the cast uses the remembered weapon; a second select returns |
| K7 | Does a server-side durability / stack / name change on a hotbar item show at once | cooldown on the item | the SkyyHud widget shows it; the item name only |
| K8 | Does Pick fire in adventure mode with nothing / a block in view | a free 3rd trigger | Pick unused |
| K9 | Does Use fire when nothing interactable is in view | (information only) | Use stays unused |
| K10 | Ability1 on a weapon without a Signature: does it reach the server | nothing (kept vanilla) | - |
| K11 | onGround / jumping flags during the sprint-tap roll and in the first 100 ms of a jump; falling flag after a blink / hop / vault | airMinMs, roll = grounded | raise airMinMs |
| K12 | Does holding Ability2 repeat the interaction (RequireNewClick behaviour on the override route) | rising edge | the engine de-bounces (one cast per 250 ms) |
| K13 | 0.6.8: an entity-level `Interactions` override on the player receives Ability2 / Ability3 while holding a vanilla sword, a crossbow (reload = Ability3), a staff | phase I3, the crossbow conflict | items until 0.7 |
| K14 | 0.7 (later session): Ability4 exists as a bindable key ("Use Ability 4") and fires to the server with a rune-less item | a real 3rd key (Question 4) | two keys only |
| K15 | 0.7: `InteractionChainStartEvent` for a rune cast exposes the same movement states as K3 | stances on the rune route | read the states from the player entity in the same tick |

## 7. Phased build plan

Owner: **SkyyClasses** owns the input layer (it owns the abilities, the per-profile data and the bridge `class:fn:abil`). SkyyArmory
keeps traversals and only asks the bridge "is a cast / variant running" (`class:fn:busy`); SkyySkills keeps the roll and double jump
untouched. SkyyHud shows the widget. No new mod.

| Phase | Version | What | Needs | Round |
|---|---|---|---|---|
| I0 | SkyyKeyProbe 0.1 (running) | K1-K13 on 0.6.8; K14-K15 after 0.7 | - | probe |
| I1 | SkyyClasses N (with engine E1) | the **stance resolver**: a `Stance` read at the press (grounded / crouch / air with the min-ms rules), variant tables as data (3 entries per ability, missing = grounded), `/cast 1\|2` already carries the stance; Server Setup rows `abil.combos*`, `abil.*Ms`; the press buffer | K3, K11 | full (new system, with E1) |
| I2 | N+1 | **hotbar ability items**: the asset pack (SkyyClasses ships items for the first time), SwapTo cast, auto-return, cooldown on the item, the guards (one per slot, no chests / trades, per-profile re-issue), the Abilities page "Put on hotbar", `/settings` item toggles | K5, K6, K7 | full (items, saved data) |
| I3 | N+2 | **keys on 0.6.8**: the player-level `Interactions` override for Ability2 / Ability3 -> marker effect -> cast (the engine's fallback hook); crossbow reload handling per K13; the PACK.md Ability2/3 survey | K4, K12, K13 | lean (one mod) |
| I4 | N+3 ... | **variants per class**, two abilities per class per version in this order: Mage + Priest (casters test the "on me" / "below me" shapes), Monk + Assassin (crouch = precise), Warrior + Berserker, Archer; each version = the class file's table in 3.1 updated | I1 | lean per class |
| I5 | SkyyHud next + N+4 | ready ping + flash, first-use hints, `/keys`, refusal throttle, per-player `/settings` block | I1 | lean (2 mods) |
| I6 | after 0.7 (engine E2) | the rune route takes over the keys; items and variants unchanged; Ability4 / Pick as extra triggers only if K14 / K8 pass | 0.7 | full (with E2) |

Deploy order rule: SkyyClasses before SkyyHud (widget hides without the bridge). Every version a `tools/classes_<ver>_patch.py` on the
previous generated script, harness `SkyyClasses/test_skyyclasses_<ver>.py` (pure-maths stance resolver + buffer tests).

## 8. Questions for Skyy (each with a recommended default)

1. Stances = the SAME ability in three shapes (grounded / crouch / mid-air), not three different abilities? **[Yes - same ability,
   same cost, same cooldown; shape changes only. Keeps "2 equipped" true and the balance budgets valid.]**
2. May a hotbar ability item cast an OWNED but UNEQUIPPED ability (a backup third slot)? **[No by default; a server toggle
   `abil.items.third` with a 1.5x cooldown for servers that want it.]**
3. Crouch variants never move you and never cost more (the "safe near a ledge" rule)? **[Yes - locked as a design rule.]**
4. If 0.7's Ability4 key reaches the server (K14): use it as a real third key for a third equipped line, or keep it free for the
   crossbow reload only? **[Keep it free until Skyy plays 0.7; design nothing on it yet.]**
5. Ability items: one per owned ability, or only the two equipped + utility? **[Two equipped mirrors + utility items; the owned list
   comes with Question 2.]**
6. Auto-return to the weapon at once, or after a short delay so you see the item flash? **[At once (0 ms); the flash is on the HUD.]**
7. Ready indicator = sound + flash on by default? **[On, both per-player toggles; no chat line.]**
8. First-use hints: one per stance over the first three casts, or all in one notification? **[One per stance; "Hints" toggle,
   `/settings` reset replays them.]**
9. Pick (middle mouse) as a loadout-swap key once loadouts exist? **[Yes if K8 passes; otherwise the Loadout item.]**
10. Which classes get variants first? **[Mage + Priest, then Monk + Assassin, Warrior + Berserker, Archer last (its crossbow key
    conflict clears on 0.7).]**

## For the local session (UNVERIFIED)

- Everything in section 6 (K1-K15) is UNVERIFIED until SkyyKeyProbe 0.1 runs; K14-K15 wait for Hytale 0.7 (ships 2026-10-12 per
  `research/cloud/Hytale-0.7-Watch.md`).
- UNVERIFIED: the entity-level `Interactions` override on the player (engine spec I3, `research/Grapple-Bolt-Spec.md` 2.5 R4) beats the
  held item's Ability3 (crossbow reload) on 0.6.8 - K13.
- UNVERIFIED: whether `acro.doubleJump.trigger` on Skyy's live SkyySkills file is `jump` (new-file default) or still `crouch` (old
  files keep it) - decides how often crouch-in-air collides; read the live file before phase I1.
- UNVERIFIED: a server-side selected-hotbar-slot change exists in the API (K6); no Skyy script uses one today.
- Local task before phase I3: grep every PACK.md mod's item JSON for `"Ability2"` / `"Ability3"` and list what the override hides.
- The engine spec's build steps E1 / E2 and this spec's I1 / I3 / I6 are the same versions; fold the stance resolver into E1 so no
  version lands without it.
