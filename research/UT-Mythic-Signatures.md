# UT + Mythic signatures (Ability 1) - one per weapon

Design spec, 2026-10-23. No code. Lists EVERY Untiered (UT) and Mythic weapon with its own Ability 1. Builds on
`research/Weapon-Signatures-Spec.md` (sections 0-4: how a signature works, the sig1 tooltip, what is proven) and replaces its section 3.1 rule
("UT = mostly the same signature, cheaper") and the "cheaper" rows of its 3.2 table with Skyy's newer answer below. UT-28 rows come from
`research/cloud/UT-28-Build-Sheet.md`; our own Mythic specials from `research/cloud/Own-Specials-Draft.md`; pack ids from `tools/pack_drops.py`.
Where answers go: `docs/answered/gear.md` (`python tools/qa_append.py gear ...`). Build rounds: section 8.

Skyy (2026-10-23, docs/answered/gear.md 324 WEAPON SIGNATURES):
- "both get new ones. the idea of UT items is that they are slightly better but only in some ways or some instances. but only slightly. they
  are UT un tired because they dont fit into the tier system. they are unique weapons. so their normal function might be different, like a
  wand without pierce but more damage. or a weapon the does true damage, ignoring defense, or it might just have a unique ability that
  charges faster or slower than a normal one.    mythic weapons are better in every way. so they should all get their own really cool ability."
- "Ut depends on the item. mythic 40%-60% gets better at higher tiers."
- Also followed: gear.md 322 UT NAMES = "Zone lore names" (not office jokes); gear.md 324 "every weapon family gets a base signature" and
  "the 3 dead-meter pack Mythics get a runtime meter" (live since SkyyGear 0.3.43); `PROJECT-RULES.md` (four power sources, no duplicates,
  pack mods by runtime id only, everything editable in Server Setup).

## 1. Rules used for every row

**UT (orange) - ONE quirk on Ability 1, slightly better in some cases only.**
- The UT's stat trade-off (its `utfx` line - Loophole pierce, Paperweight slow + hard, ...) stays exactly as built / drafted. The Ability 1 quirk
  is the one NEW thing, and it echoes that identity.
- Two kinds of quirk (column "Kind"):
  - **F = function**: the family signature works differently (no bounce but more hits on one, True Damage, a different shape, a status).
  - **C = charge**: the same family move, but it charges by its own rule - faster / slower (`sig.ut.<id>` row, live in SkyyGear 0.3.43) or
    from a different action - sometimes with a matching small bonus.
- "Slightly": over a fight the UT signature does about **-10 % to +10 %** of the family signature's damage; it wins clearly only in its
  niche (one target, a crowd, low Health, a party ...) and has a downside (column "Downside") where it fits. A slower charge always comes with
  a matching bonus (never a pure downside).
- One plain tooltip line (<= 70 characters) in the existing sig1 Ability 1 block; the name shows in the orange UT colour.

**Mythic (purple) - its OWN really cool signature, better in every way.**
- Every Mythic signature does **1.3x-1.6x** the family signature's damage (base benchmark: about 3-5 hits of single-target damage,
  `research/cloud/Signature-Proposals.md` 71) PLUS a unique effect, AND charges faster: the live sig1 formula
  `sig.mythic.low` 40 % at T1 -> `sig.mythic.high` 60 % at T15 by the item's level tier (`GearSigX.mythPct`). Shown here at the drop level:
  Lv 20 = T4 44 %, Lv 30 = T5 46 %, Lv 45 = T7 49 %, Lv 60 = T10 53 %, Lv 70 = T11 54 %, Lv 75-79 = T12 56 %, Lv 82-85 = T13 57 %,
  Lv 94 = T14 59 %, Lv 95+ = T15 60 %.
- A Mythic's drafted passive hook (Own-Specials-Draft, Elemental Blade on the swords) stays - the signature is added on top (Question 1).
- Visuals are ideas for the art / particle pass; particle ids are picked from Assets.zip at build time (UNVERIFIED names, none copied in git).

**Both:**
- A signature never copies a class ability (list in Weapon-Signatures-Spec 3.1: Arcane Beam, Arrow Rain, Pinning Shot, Explosive Arrow,
  Sanctuary, Shield Bubble, Shadow Clone, Earthsplitter, Hundred Fists, Cyclone Kick, Whirlwind (class) ...): it is a weapon move, charged
  only by hits, no Mana, damage told as "x one hit".
- Four power sources: the signature is part of the WEAPON source. Its damage is "x the weapon's own levelled hit", so gear, accessories and
  pets that raise damage raise it the same way - no separate scaling, no lasting stat buff (any buff <= 6 s). Section 7.
- Pack items: runtime id only, never a file (PACK.md). Our player-side stat modifier + our own hit code, like the live `sig.packMeter`.
- Every number = a Server Setup row (`sig.ut.<id>` table for UT rates; `sig.fx.<effect>.*` for effect numbers, times in seconds).

## 2. Engine paths (column "Path")

| Code | Path | Status | Evidence / what is missing |
|---|---|---|---|
| **R** | OUR item id gets its own Ability 1 root -> cast (StatsCondition 100 % -> ChangeStat -100 %) -> launch -> invisible marker -> server effect | **PROVEN, deployed** | SkyyArmory 0.1.14 wand Ricochet, 0.1.45 sig2 (Whirling Staff / Flurry / Kunai Fan / Page Storm, codes 13001-13004) |
| **C** | charge-rate multiplier on every rise of the held meter (`sig.ut.<id>`, `sig.mythic.*`) | **PROVEN, deployed** | SkyyGear 0.3.43 GearSigX |
| **C+** | a charge RULE (conditional rate, or a top-up on one hit type) - `addStatValue` top-up on a hit our damage code already sees | proven parts, **new small code** | the wand's server-side gain (`Rico.add`), Gear's back / front / range / lowhp checks at hit time |
| **W** | "fired window": GearSigX sees the held meter fall from full to ~0 with no swap = the vanilla signature fired; that player's hits in the next N s (the move's length) are its hits -> scale / convert / add an effect | watcher **PROVEN** (0.3.43 rise watcher); fall detect + window **NEEDS PROBE** | needed for vanilla moves on our copies (Vortexstrike, Razorstrike, Whirlwind, Volley, Big Arrow) and pack / dev-bow signatures - no file change |
| **A** | "auto-release" for ROOT-LESS items: meter by the named player modifier (the `skyygear_sig` pattern) + our top-up on their weapon hits; when full, the NEXT landed swing releases our effect and empties the meter | **NEEDS PROBE** | the `sig.packMeter` modifier is live (0.3.43, in-game test 241 pending); unknown: the HUD meter / ready glow on an item with no root, emptying by `addStatValue` |
| **X** | an effect run by SkyyArmory's move engine (ArmorySig2 / Sig2Job) for an item SkyyGear detects (W / A) - new bridge `armory:fn:sigfx` (Object[] {uuid, effect id, item id, level} -> Boolean; plain java.lang) | engine **PROVEN**, bridge **new** | one effect engine, no copy of it in Gear |

Building blocks the effects use (all inside R / X):

| Block | Status | Where |
|---|---|---|
| area pulse around you / a point | PROVEN | Whirling Staff, Page Storm (0.1.45) |
| line / first-on-line pick | PROVEN (all-on-line = small extension) | Kunai Fan (0.1.45), wand pierce continuation (0.1.17) |
| chain jump to nearest unhit enemy (+ allies) | PROVEN | Ricochet (`Rico`, 0.1.14) |
| push away | PROVEN | fist last jab / kunai return push |
| pull in | NEEDS PROBE (negative push) | - |
| Slow / Root / Stun / Freeze (vanilla effects) | PROVEN in SkyyClasses (Frost Nova, Pinning Shot, Hunter's Net); applying from SkyyArmory = same API, NEEDS PROBE | SkyyClasses 0.1.46 |
| Poison DoT / element part | PROVEN | `classes:fn:dot` (0.3.39), elem1 split (0.3.40 GearESw) |
| True Damage (after Defence) | PROVEN | SkyyGear GearTrueSys (`tdmg`) |
| forced crit on a hit | NEW flag on the proven crit roll | GearHit |
| heal a player / ally | PROVEN | heal orb, Second Opinion `heal` line |
| timed ground area | PROVEN for the heal orb circle; damage ground NEEDS PROBE | SkyyArmory heal orb |
| player dash / blink | NEEDS PROBE (also needed by the base spear Skewer Charge) | - |
| projectile homing | UNVERIFIED -> fallback: instant hits on picked targets + a trail visual | - |
| off-hand parry timing | UNVERIFIED | Own-Specials W2 |

## 3. Family base signatures (what each row twists)

| Family | Base signature | Status |
|---|---|---|
| sword / battleaxe / mace / daggers / shortbow / crossbow | Vortexstrike / Whirlwind (battleaxe) / Groundslam / Razorstrike / Volley / Big Arrow | vanilla |
| wand | Ricochet | built (Armory 0.1.14) |
| Bo / wraps + gauntlets / kunai / spellbook | Whirling Staff / Flurry / Kunai Fan / Page Storm | built (Armory 0.1.45, sig2) |
| staff / soul cage / spear / axe / club (incl. flails) / longsword / great shield | Arcane Overload / Soul Release / Skewer Charge / Cleave / Skull Crack / Meridian Cut / Iron Curtain | **not built** - round sig4 (gear.md 324 "Yes, all of them") |
| dual swords (own Mythic A3) | none - designed with A3 | - |
| shield (off-hand) | none - Ability 1 belongs to the main hand | W2 below |

## 4. UT weapons - 28 (12 live + 16 UT-28)

Zone / tier: Z1 Emerald Wilds T3 Bronze 15-23, Z2 Howling Sands T6 Dusk 35-43, Z3 Whisperfrost Frontiers T9 Azurvane 55-63, Z4 Devastated
Lands T12 Cinder 75-83, Z5 Dinosaur Caves T15 Lumen 95-103. "sig.ut" = the `sig.ut.<id>` default (+ faster / - slower, 0 = normal).
Names: the 12 live Zone 1 items keep their built names (UT-28 sheet "The Zone 1 live UTs keep their office names"); the signature names are
plain move names; the UT-28 ones carry their zone lore word.

### 4.1 Zone 1 - Emerald Wilds (live)

| # | Item (id, owner) | Class / family | Ability 1 (name) | Kind | What changes vs the base | sig.ut | Downside | Tooltip line (<= 70) | Path |
|---|---|---|---|---|---|---|---|---|---|
| U1 | The Loophole (`Weapon_Staff_UT_Loophole`, Armory) | Mage staff | **Loophole Lance** | F | instead of Arcane Overload (next 3 shots free + 2x): ONE piercing lance-bolt 24 blocks, 1.5x the charged shot to every enemy on the line | 0 | one target: about 2/3 of Arcane Overload | One piercing bolt flies 24 blocks: 1.5x your charged shot to each. | R + line pick (all-on-line) - needs sig4 staff root |
| U2 | The Paperweight (`Weapon_Sword_UT_Paperweight`, Gear) | Warrior sword | **Weighted Vortex** | C | Vortexstrike hits +35 % | -20 | 20 % slower charge (net about +8 %: big bursts, fewer of them) | Vortexstrike hits 35% harder. Charges 20% slower. | C (live) + W (damage x on the window) |
| U3 | Overtime (`Weapon_Battleaxe_UT_Overtime`, Gear) | Berserker battleaxe | **Last-Hour Whirlwind** | C | fills 35 % faster while you are under half Health | (rule) | 15 % slower above half Health | Whirlwind. Fills 35% faster under half Health, 15% slower above. | C+ (Health check in GearSigX) |
| U4 | The Pocket Knife (`Weapon_Daggers_UT_PocketKnife`, Gear) | Assassin daggers | **Quiet Edge** | C | a backstab hit fills the meter twice | (rule) | a front hit fills half | Razorstrike. Backstabs fill it twice; front hits fill half. | C+ (Gear's back / front cone at hit time) |
| U5 | Short Notice (`Weapon_Shortbow_UT_ShortNotice`, Gear) | Archer shortbow | **Snap Volley** | C | half-drawn arrows that hit fill +0.5 (vanilla: only full draws fill) | 0 | its 12-block cap also limits the Volley | Volley. Half-drawn hits fill it too (+0.5), max 12 blocks. | C+ (its own 4 arrow configs tell the draw) |
| U6 | The Second Opinion (`Weapon_Wand_UT_SecondOpinion`, Armory) | Priest wand | **Second Opinion** | F | the Ricochet also hops through allies in range and heals each for 40 % of a hit (enemies still take theirs, -10 % a bounce) | 0 | ally hops use up the 8 bounces: less enemy damage in a party | Ricochet also hops through allies, healing each 40% of a hit. | R (Rico picks allies) - Spec 3.2 plan, made smaller |
| U7 | The Turnstile (`Weapon_Bo_UT_Turnstile`, Armory) | Monk Bo | **Revolving Door** | F | Whirling Staff first pulls enemies within 4 blocks in to 1.5, the last spin flings them out (knockback x2); bosses neither | 0 | 1 spin hit fewer (3 not 4) | Whirling Staff pulls foes in 4 blocks, then flings them out. | R (sig2 Whirl) + pull (probe) + push |
| U8 | Ricochet bow (`Weapon_Shortbow_Ricochet`, vanilla id) | Archer shortbow | **Ricochet Trishot** | C | the vanilla move, fills 25 % faster | +25 | its 20 % less damage (live trade-off) | Three bouncing arrows. Fills 25% faster. | C (live) |
| U9 | Combat bow (`Weapon_Shortbow_Combat`, vanilla id) | Archer shortbow | **Bashing Trishot** | C | each right-click bash that lands fills +3 | (rule) | arrows fill 25 % less | Three arrows at once. Bash hits fill +3; arrows fill 25% less. | C+ (bash = a melee hit with DamageSequence on the bow) |
| U10 | Test Zoom bow (`Weapon_Shortbow_Test_Zoom`, vanilla id) | Archer shortbow | **Long Volley** | C | each Volley / normal arrow that hits from 25+ blocks refunds 2 energy | 0 | none extra (its 20 % less damage) | Volley. Each arrow hitting from 25+ blocks refunds 2 energy. | C+ (the shooter-distance check of `range+`) |
| U11 | Ghost Sword (`GhostSword`, The Armory, runtime id) | Warrior sword (Z1 extra) | **Grave Chill** | F | no root today: meter 20 by our modifier, filled by its swings (+1 a hit x w); full = the next swing hits 1.5x and Freezes the target 1 s (bosses: no freeze) | 0 | no Ability 1 key - it fires on the next swing | Full meter: your next swing hits 1.5x and freezes the target 1 s. | A (probe) + Freeze |
| U12 | Hepta Axe (`Hepta_Axe`, The Armory, runtime id) | Berserker battleaxe (Z4 band) | **Seven Cuts** | F | its inherited meter 9 already fills; full = the next swing chops 7 times (0.15 s apart) at 0.35x each, every enemy in a 3-block arc in front | 0 | fires on the next swing (no key); 2.45x total, arc only | Full meter: your next swing chops 7 times, 0.35x each, in front. | A (meter exists: best first probe) + X area pulse |

### 4.2 Zone 1 - UT-28 row 13

| # | Item (id, owner) | Class / family | Ability 1 | Kind | What changes | sig.ut | Downside | Tooltip line | Path |
|---|---|---|---|---|---|---|---|---|---|
| 13 | The Azure Arc (`Weapon_Longsword_UT_AzureArc`) | Spellblade longsword | **Azure Crescent** | F | instead of Meridian Cut (2.5 hits in a 160-degree arc, reach 5): one Air wave 10 blocks ahead, 3 wide, 1.6 hits to every enemy it passes (Spellblade.md option "Crescent Wave") | 0 | close crowd: less than Meridian Cut | An Air wave 10 blocks ahead, through every foe: 1.6 hits each. | R (sig4 longsword root) + line pick + Air part |

### 4.3 Zone 2 - Howling Sands

| # | Item | Class / family | Ability 1 | Kind | What changes | sig.ut | Downside | Tooltip line | Path |
|---|---|---|---|---|---|---|---|---|---|
| 14 | The Sandscript Codex (`Weapon_Spellbook_UT_SandscriptCodex`) | Mage spellbook | **Sand Pages** | F | Page Storm also Slows every enemy inside by 20 % (2 s after it ends) | 0 | 15 % less storm damage | Page Storm slows foes inside by 20%. 15% less damage. | R (sig2 Page Storm) + Slow |
| 15 | Steppe Wind Wraps (`Weapon_Fist_UT_SteppeWind`) | Monk wraps | **Steppe Gale** | F | Flurry while dashing 4 blocks forward; each jab hits every enemy you pass | 0 | 10 % less a jab, no last-jab push | Flurry while dashing 4 blocks; jabs every foe you pass. No push. | R (sig2 Flurry) + dash (probe) |
| 16 | Scarak Stinger (`Weapon_Kunai_UT_ScarakStinger`) | Assassin kunai | **Stinger Fan** | F | Kunai Fan poisons each enemy hit (30 % of the dart's hit over `poison.time` 10 s) | 0 | no 3-dart bonus hit | Kunai Fan poisons each foe hit (30% over 10 s). No 3-hit bonus. | R (sig2 Kunai Fan) + `classes:fn:dot` |

### 4.4 Zone 3 - Whisperfrost Frontiers

| # | Item | Class / family | Ability 1 | Kind | What changes | sig.ut | Downside | Tooltip line | Path |
|---|---|---|---|---|---|---|---|---|---|
| 17 | Hotspring Blessing (`Weapon_Wand_UT_HotspringBlessing`) | Priest wand | **Warm Spring** | F | Ricochet leaves a small spring at each bounce for 3 s: allies standing in one heal 3 % max Health a second | 0 | 6 bounces, not 8 | Ricochet leaves a 3 s healing spring at each bounce. 6 bounces. | R (Rico) + timed ground area (heal orb circle) |

### 4.5 Zone 4 - Devastated Lands

| # | Item | Class / family | Ability 1 | Kind | What changes | sig.ut | Downside | Tooltip line | Path |
|---|---|---|---|---|---|---|---|---|---|
| 18 | Magma Lance (`Weapon_Spear_UT_MagmaLance`) | Warrior spear | **Molten Skewer** | F | instead of Skewer Charge (carry + pin one, 2 hits): the 6-block dash hits every enemy you pass once, Fire | 0 | no carry, no pin, 1 hit each | Dash 6 blocks, Fire-hitting every foe you pass. Carries no one. | R (sig4 spear root) + dash (probe) + Fire part |
| 19 | Stormvent (`Weapon_Crossbow_UT_Stormvent`) | Archer crossbow | **Vent Bolt** | F | the armed Big Arrow pierces up to 3 enemies, 0.8x each, Thunder | 0 | 0.8x on the first target; dead past the 20-block cap | Big Arrow pierces up to 3 foes, 0.8x each, Thunder. Max 20 blocks. | W (armed shot = SignatureCharges drop, probe) + line pick |
| 20 | Ashfall Grimoire (`Weapon_Spellbook_UT_AshfallGrimoire`) | Mage spellbook | **Ashfall Finale** | F | Page Storm's 4th tick becomes an ash burst: 1.6x to all inside (total 4.6 vs 4) | 0 | radius 4, not 5 | Page Storm ends in a 1.6x ash burst. Radius 4, not 5. | R (sig2 Page Storm) |
| 21 | Emberroot Wraps (`Weapon_Fist_UT_EmberrootWraps`) | Monk wraps | **Ember Roots** | F | Flurry's last jab Roots the target 1.5 s (bosses: 0.5 s) instead of pushing it | 0 | no push: you cannot make space | Flurry's last jab roots the target 1.5 s instead of pushing it. | R (sig2 Flurry) + Root |
| U12 | Hepta Axe | (row U12 above - band Z4) | | | | | | | |

### 4.6 Zone 5 - Dinosaur Caves

| # | Item | Class / family | Ability 1 | Kind | What changes | sig.ut | Downside | Tooltip line | Path |
|---|---|---|---|---|---|---|---|---|---|
| 22 | Raptorfang (`Weapon_Sword_UT_Raptorfang`) | Warrior sword | **Raptor Bite** | F | Vortexstrike deals True Damage (ignores Defence) - Skyy's example | -15 | 15 % slower charge (soft targets: a loss) | Vortexstrike deals True Damage (ignores Defence). Fills 15% slower. | C (live) + W + True Damage |
| 23 | Bonewhistle (`Weapon_Shortbow_UT_Bonewhistle`) | Archer shortbow | **Bone Fan Volley** | F | the armed Volley fires 5 arrows in a 40-degree fan, 0.7x each (3.5 vs 3) | 0 | one target catches 1-2 of them | Volley fires 5 arrows in a wide fan, 0.7x each. | W (armed shot) + X (2 extra arrows = instant line picks, probe) |
| 24 | Deepcave Shadow (`Weapon_Daggers_UT_DeepcaveShadow`) | Assassin daggers | **Shadow Razor** | F | Razorstrike's 3 cuts always crit (Spec 3.5 idea) | -20 | 20 % slower charge | Razorstrike always crits. Fills 20% slower. | C (live) + W + forced crit (new flag) |
| 25 | Primal Cleaver (`Weapon_Axe_UT_PrimalCleaver`) | Berserker axe | **Primal Cleave** | F | Cleave heals you 2 % max Health per enemy hit (max 5) | 0 | 15 % less Cleave damage | Cleave heals you 2% max Health per foe hit (max 5). 15% less damage. | R (sig4 axe root) + heal |
| 26 | The Stormfossil (`Weapon_Staff_UT_Stormfossil`) | Mage staff | **Fossil Overload** | F | Arcane Overload gives 4 free shots at 1.6x (not 3 at 2x: 6.4 vs 6); with its pierce, better in a crowd | 0 | each shot 20 % weaker | Arcane Overload: 4 free shots at 1.6x (not 3 at 2x). | R (sig4 staff root) |
| 27 | Cavewind (`Weapon_Wand_UT_Cavewind`) | Priest wand | **Narrow Draft** | F | Ricochet never bounces: the bolt strikes its target 5 times, 0.15 s apart, at the first-bounce damage - "a wand without pierce but more damage" on one | 0 | a crowd: 5 hits on one, not 8 spread | Ricochet never bounces: the bolt hits its target 5 times. | R (Rico, same target 5x) |
| 28 | Crushing Tail (`Weapon_Bo_UT_CrushingTail`) | Monk Bo | **Tail Sweep** | F | instead of 4 spin hits: one wide 5-block ring, 2.2 hits, knocks enemies down (Stun 1 s); bosses / mini bosses not stunned | 0 | one pulse: nothing for late arrivals | One wide 5-block ring, 2.2 hits, knocks foes down 1 s. Bosses stand. | R (sig2 Whirl, 1 pulse) + Stun |

UT count: 12 live (7 ours + 3 dev bows + Ghost Sword + Hepta Axe) + 16 UT-28 = **28**. Per class: Warrior 4 (Paperweight, Ghost Sword,
Magma Lance, Raptorfang), Berserker 3 (Overtime, Hepta, Primal Cleaver), Assassin 3, Archer 6 (Short Notice, 3 dev bows, Stormvent,
Bonewhistle), Mage 4, Priest 4, Monk 4, Spellblade 1.

## 5. Mythic weapons - 34 (13 live / pack + 21 of our own drafted)

Owner: **Pack** = The Armory (LadyPaladra, CC BY-NC) by runtime id only; **Vanilla** = the developer bows (vanilla ids, SkyyGear makes them
Mythic); **Ours** = `research/cloud/Own-Specials-Draft.md` items (none built; ids `SkyyArmory_Special_<Name>`). Our 21 get **zone lore names**
(Question 2 - their old working names in brackets). Pack / vanilla item names stay theirs; only the signature name is ours.
Zones for the 3 dev bows are a default here (they have no boss pool yet - the boss round sets it).

### 5.1 Zone 1 - Emerald Wilds

| Item (id, owner) | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| FireWhip (`FireWhip`, Pack) | Berserker club (flail) | Z1 Club Mythic boss pool, Lv 20 -> 44 % | **Ember Lash** | three fast whip cracks in a 90-degree cone, 6 blocks, 0.8x each + Fire; an enemy hit by all three catches Burning (30 % of a crack over 5 s) | an orange fire line traced along the whip, sparks on each crack | A (root-less, probe) + X cone pulse + Fire part / DoT |
| ScorpianFlail (`ScorpianFlail`, Pack) | Berserker club (flail) | Z1 Club Mythic, Lv 20 -> 44 % | **Barbed Chain** | hurl the flail head 10 blocks: it hooks the first enemy, you are pulled TO it (gap closer), 2x hit + Stun 1 s (bosses: no stun) | a dark chain stretching out, a barb flash on the hook | A + line pick + player dash (probe) + Stun |
| Gravewhisper (Ours) [The Fine Print] | Assassin daggers | Burnt Skeleton Praetorian, Lv 20 -> 44 % | **Grave Mark** | Razorstrike x1.3; each cut also marks the target + 2 enemies within 4 blocks for 8 s; your next hit on a marked enemy is a backstab (x1.5) from ANY angle (its passive widens backstabs to the sides already) | a pale skull sigil floating over each marked enemy | R (our id: Razorstrike copy) + W + mark book-keeping (Kunai Fan counter pattern) |
| Mossheart Wand (Ours) [The Courtesy Copy] | Priest wand | Earthen Golem guardian, Lv 20 -> 44 % | **Mossheart Bloom** | Ricochet x1.3 (8 bounces); every enemy bounce heals the most-hurt ally within 16 blocks 3 % max Health (smart heal, you included) | a green moss-light thread from each bounce to the healed ally | R (Rico) + ally pick by lowest Health |
| Thornroot Bow (Ours) [The Filing Spike] | Archer shortbow | Earthen Golem guardian, Lv 20 -> 44 % | **Thornfield** | the armed Volley's 3 arrows each burst into 4 thorn spikes where they land; spikes stay 5 s, an enemy stepping on one takes 0.5x + Slow 20 % 2 s (one spike each) | brown thorn clusters sprouting from the ground | R (our id: Volley copy) + timed ground areas (probe) + Slow |

### 5.2 Zone 2 - Howling Sands

| Item | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| Elemental Poison sword (`Weapon_Elemental_Poison`, Pack) | Spellblade longsword | Z2 Longsword Mythic (Broodmother's zone), Lv 30 -> 46 % | **Venom Tide** | a toxic wave rolls 8 blocks in a 60-degree cone: 1.5x + a full Poison line (60 % of the hit over 10 s) on everyone it touches | a green mist wave, bubbles bursting along it | A + X cone + `classes:fn:dot` |
| Pull bow (`Weapon_Shortbow_Pull`, Vanilla) | Archer shortbow | default Z2 boss pool, Lv 30 -> 46 % | **Hookline Crash** | Pullshot (vanilla, kept) + when the pulled enemy lands next to you, every other enemy within 3 blocks is knocked back 3 blocks and takes 1x | a rope flash, then a dust ring where it lands | W (dev bow signature) + push ring |
| Broodspire Staff (Ours) [The Long Form] | Mage staff | The Broodmother, Lv 30 -> 46 % | **Swarm Overload** | Arcane Overload (4 free shots at 2x); each shot that hits splits into 3 brood motes that strike the 3 nearest other enemies within 5 blocks (0.4x each) | small amber motes zipping out like insects | R (sig4 staff root) + chain pick (Rico) |
| Sandreaver Bo (Ours) [The Long Queue] | Monk Bo | The Broodmother, Lv 30 -> 46 % | **Dune Devil** | Whirling Staff leaves your hands as a sand tornado that travels 8 blocks forward over 2 s, 6 pulses of 0.6x, dragging hit enemies along | a sand funnel with the Bo spinning inside | R (sig2 Whirl, moving centre) + pull (probe) |
| Overseer's Repeater (Ours) [The Rubber Stamp] | Archer crossbow | Scarak Overseer, Lv 30 -> 46 % | **Stampede Bolts** | Big Arrow arms THREE heavy bolts (each 0.8x of a Big Arrow: 2.4x total over the next 3 shots) | three glowing bolt pips on the crossbow while armed | R (our id: Big Arrow copy, SignatureCharges 3 - probe) |

### 5.3 Zone 3 - Whisperfrost Frontiers

| Item | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| Elemental Gravity sword (`Weapon_Elemental_Gravity`, Pack) | Spellblade longsword | Z3 Longsword Mythic (Void Golem's zone), Lv 45 -> 49 % | **Collapse Point** | a gravity well at the target: pulls enemies within 6 blocks to it for 1.5 s, then crushes them for 2x Earth (bosses not pulled) | a purple-black swirl, rocks lifting then slamming | A + X area pulse + pull (probe) + Earth part |
| Vampire bow (`Weapon_Shortbow_Vampire`, Vanilla) | Archer shortbow | default Z3 boss pool, Lv 45 -> 49 % | **Bloodmoon Shot** | Supershot (vanilla, kept) + the hit target carries a blood mark 6 s: every hit you or a party member lands on it heals the hitter 3 % of that hit | a red crescent over the marked enemy | W + mark + heal on hit |
| Rimebound Codex (Ours) [Form 27-B/6, Annotated] | Mage spellbook | The Everfrost Yeti, Lv 45 -> 49 % | **Glacial Margin** | Page Storm x1.3; its ground stays frozen 4 s after: enemies inside are Slowed 40 % and take +20 % from your spells; the last tick Freezes 1 s | white frost spreading in a ring, ice crackle on the last tick | R (sig2 Page Storm) + timed area + Slow / Freeze |
| Whiteout Wand (Ours) [The Interoffice Memo] | Priest wand | The Everfrost Yeti, Lv 45 -> 49 % | **Whiteout** | Ricochet x1.3 with 10 bounces that ignore walls (no line of sight needed), each bounce Slows 25 % 3 s | a snow-white bolt passing through stone | R (Rico, LOS check off) + Slow |
| Outlander's Tether (Ours) [Return to Sender] | Assassin kunai | Outlander Chief, Lv 45 -> 49 % | **Tether Storm** | Kunai Fan of 7 at 1x; each enemy hit is tethered 3 s, then yanked 3 blocks toward you for 1x more (bosses: no yank) | thin red ribbons from you to each tethered enemy | R (sig2 Kunai Fan) + pull (probe) |
| Frostgrip Wraps (Ours) [The Firm Handshake] | Monk wraps | Outlander Chief, Lv 45 -> 49 % | **Glacier Fist** | Flurry x1.3; each jab adds a Chill stack; the last jab shatters them: 0.3x per stack + Freeze 1.5 s (bosses 0.5 s) | ice crust growing on the target, shatter burst | R (sig2 Flurry) + counter + Freeze |
| Colossus Pike (Ours) [The Long Arm] | Warrior spear | Outlander Colossus, Lv 45 -> 49 % | **Boomerang Pike** | throw the spear 12 blocks in a line; it returns to your hand, hitting every enemy on BOTH passes (1.2x each pass) | a blue-steel streak out and back, chain ring glint | R (sig4 spear root) + line pick x2 |

### 5.4 Zone 4 - Devastated Lands

| Item | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| Elemental Ice sword (`Weapon_Elemental_Ice`, Pack) | Spellblade longsword | Z4 Longsword Mythic (Dragon_Frost's zone), Lv 60 -> 53 % | **Frost Crown** | 8 ice shards orbit you for 4 s; each strikes the first enemy that comes within 2 blocks for 0.8x Water + Slow 30 % (6.4x if all land) | a turning crown of blue shards | A + X area pulse around you + Water part + Slow |
| Rune Blade stage 1 (`RuneBladeStage1`, Pack) | Berserker club | Z4 Mythic, Lv 60 -> 53 % | **Runebreak** | the next swing carves a rune under the target; 2 s later it erupts 2.5x in a 4-block radius and everyone inside takes +20 % damage for 5 s | a glowing rune circle, then a pillar of light | A + delayed area (Sig2Job) + damage-taken mark (Awed book-keeping, probe) |
| Dual Rune Blade (`DualRuneBlade`, Pack) | Assassin daggers | Z4 Daggers Mythic, Lv 60 -> 53 % | **Twin Rune Razor** | Razorstrike (vanilla, via the live pack meter) + each cut leaves a rune on its target; at 3 runes it detonates for 1.5x around it (3 blocks) | rune marks stacking, a violet burst | W + counter (Kunai Fan pattern) + area |
| Lahat Chereb (`LahatChereb`, Pack) | Berserker mace | Z4 Mace Mythic, Lv 60 -> 53 % | **Cherub's Judgment** | Groundslam (vanilla, via the pack meter) + flame pillars erupt under the 3 farthest enemies it hit (1.2x Fire each) | three tall fire pillars | W + point areas + Fire part |
| Bomb bow (`Weapon_Shortbow_Bomb`, Vanilla) | Archer shortbow | default Z4 boss pool, Lv 60 -> 53 % | **Cinderburst** | Boomshot (vanilla, kept) + its blast throws 4 bomblets that pop 1 s later around it (0.5x each, 2 blocks) | small ember bombs scattering, 4 pops | W + delayed point areas |
| Embercrown Staff (Ours) [The Forwarding Address] | Mage staff | The Ember Warden, Lv 60 -> 53 % | **Sunflare Beacon** | plant a beacon at your aim (24 blocks): for 3 s it fires a Fire ray at every enemy within 8 of it each 0.5 s (0.5x; 3x total on one) | a floating brass beacon with a sun flare | R (sig4 staff root) + placed area pulse + Fire part |
| Hearthflame Cage (Ours) [Hold Music] | Priest soul cage | The Ember Warden, Lv 60 -> 53 % | **Hearth Release** | Soul Release (pop every Binding) x1.3, and 25 % of the stored healing also flows to every ally within 8 blocks over 5 s | warm gold threads from each popped soul to the allies | R (sig4 soul cage root) + heal over time |
| Wardenfist Gauntlets (Ours) [The Stamp of Approval] | Monk gauntlets | The Ember Warden, Lv 60 -> 53 % | **Caldera Finisher** | Flurry x1.3, then a ground punch: a ring of lava geysers (4 blocks) knocks enemies up, 2x Fire | geysers bursting in a ring | R (sig2 Flurry) + area + knock-up (probe) |
| Rexbone Longbow (Ours) [The Long Distance Call] | Archer shortbow | Cave Rex, Lv 60 -> 53 % | **Horizon Shot** | one flat arrow that pierces everything and gains +3 % damage per block flown (cap +90 %) | a faint amber trail that brightens with distance | R (our id) + line pick + distance at hit |
| Rexhide Bulwark (Ours) [The Counterclaim] | Warrior shield (off-hand) | Cave Rex, Lv 60 -> 53 % | **Rex Roar** | off-hand: no Ability 1 slot. A PERFECT parry (first 0.3 s of a block) while your main-hand meter is full spends that meter instead: a roar shockwave 5 blocks, 1.5x + Stun 1 s (bosses: no stun) | a bone-coloured shock ring, a rex roar sound | parry timing UNVERIFIED (Question 5) |

### 5.5 Zone 5 - Dinosaur Caves

| Item | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| Elemental Flame sword (`Weapon_Elemental_Flame`, Pack) | Spellblade longsword | Z5 Longsword Mythic (Dragon_Fire's zone), Lv 75 -> 56 % | **Dragonfire Wake** | a fire breath cone 6 blocks: 2x Fire, and the ground burns 3 s after (0.3x a second) | a dragon-head flame cone, scorched ground | A + X cone + damage ground (probe) |
| Zweihander (`Zweihander`, Pack) | Warrior big sword (mace kind) | Z5 Mythic, Lv 75 -> 56 % | **Mountainbreaker** | Groundslam (vanilla, via the pack meter) + an aftershock 1 s later: a second ring 1.6x wider, 1.2x | cracks racing outward, dust | W + delayed area |
| Dragonmirror Blades (Ours) [The Carbon Copy] | Assassin dual swords | the Zone 5 Dragon, Lv 75 -> 56 % | **Mirror Dance** | a 6-cut dance moving you 4 blocks forward; every 2nd cut is a 3-block arc (0.75x each, 4.5x total); you take 30 % less damage during it | black-and-pale-blue mirrored slash trails | R (our id, new family) + dash (probe) + short damage-taken buff |

### 5.6 Capstone - The Final Audit floors

| Item | Class / family | Source, Lv -> charge | Signature | What it does | Visuals | Path |
|---|---|---|---|---|---|---|
| Stillvoid Bo (Ours) [Thank You For Waiting] | Monk Bo | The Void Clerk (F1), Lv 79 -> 56 % | **Patient Storm** | Whirling Staff x1.3, +10 % per second you blocked in the last 10 s (cap +60 %); while spinning it turns away arrows and bolts | white void ripples, a bell ring at full Patience | R (sig2 Whirl) + block timer (passive's counter) + projectile block (probe) |
| Unwritten Tome (Ours) [The Unabridged Edition] | Mage spellbook | The Archive Golem (F2), Lv 82 -> 57 % | **Unwritten End** | Page Storm that grows: 5 ticks, each +1 radius and +15 %, then implodes, pulling enemies to the centre for 1.5x | violet pages spiralling wider, then a collapse flash | R (sig2 Page Storm) + pull (probe) |
| Voidbreaker Arbalest (Ours) [The Final Notice] | Archer crossbow | The Landlord (F3), Lv 85 -> 57 % | **Ascending Bolt** | Big Arrow that bounces between up to 4 enemies, +25 % per bounce (1x, 1.25x, 1.5x, 1.75x) | a gold bolt arcing between targets, brighter each hop | R (our id) + chain pick (Rico) |
| Aetherbound Cage (Ours) [Next, Please] | Priest soul cage | Ticket #1 (F6), Lv 94 -> 59 % | **Endless Binding** | Soul Release x1.3, then every enemy it hit is bound again at once (Bindings restart at half stored) | silver chains snapping back onto each enemy | R (sig4 soul cage root) + re-bind (passive's code) |

Mythic count: 13 live / pack (3 dev bows + 10 Armory: 2 flails, 4 Elementals, Rune Blade 1, Dual Rune Blade, Lahat Chereb, Zweihander) + 21
ours = **34**. Not listed: `Weapon_Dualswords_Iron` (pack, pack-meter list, no Mythic role in `tools/pack_drops.py`), Rune Blade stages 2 / 3
(role "off"), Armory armour sets (not weapons).

## 6. No two share an effect

Each row's core effect (the one thing the twist does). Statuses / elements may repeat as a side part; the core never does.

| Core effect | Item |
|---|---|
| piercing bolt line (instant, 24) | Loophole Lance |
| slower charge for bigger hits | Weighted Vortex |
| charge rate by own Health | Last-Hour Whirlwind |
| backstab hits charge double | Quiet Edge |
| half-draw hits charge | Snap Volley |
| ricochet hops allies + heals | Second Opinion |
| pull in, then fling | Revolving Door |
| plain faster charge | Ricochet Trishot |
| melee bash charges | Bashing Trishot |
| long-range hit refund | Long Volley |
| auto-release freeze strike | Grave Chill |
| auto-release 7-chop | Seven Cuts |
| travelling wave through enemies | Azure Crescent |
| slowing storm | Sand Pages |
| mobile flurry dash | Steppe Gale |
| poisoning fan | Stinger Fan |
| heal springs at bounces | Warm Spring |
| dash through all | Molten Skewer |
| armed bolt pierce | Vent Bolt |
| finale burst | Ashfall Finale |
| last jab roots | Ember Roots |
| signature = True Damage | Raptor Bite |
| wide 5-arrow fan | Bone Fan Volley |
| forced crits | Shadow Razor |
| heal per enemy hit | Primal Cleave |
| more, weaker free shots | Fossil Overload |
| no bounce, all hits on one | Narrow Draft |
| one ring knock-down | Tail Sweep |
| triple crack -> Burning | Ember Lash |
| hook and pull YOU to it | Barbed Chain |
| spread marks -> any-angle backstab | Grave Mark |
| bounce heals the most-hurt ally | Mossheart Bloom |
| arrows become spike traps | Thornfield |
| poison wave cone | Venom Tide |
| pulled enemy bowls others over | Hookline Crash |
| shots split into motes | Swarm Overload |
| travelling tornado | Dune Devil |
| three armed bolts | Stampede Bolts |
| gravity well, then crush | Collapse Point |
| mark heals every hitter | Bloodmoon Shot |
| frozen amp zone | Glacial Margin |
| wall-ignoring ricochet | Whiteout |
| multi-tether yank | Tether Storm |
| chill stacks shatter | Glacier Fist |
| out-and-back spear | Boomerang Pike |
| orbiting shards | Frost Crown |
| delayed rune eruption + vulnerability | Runebreak |
| 3-rune stack detonation | Twin Rune Razor |
| pillars on the farthest hit | Cherub's Judgment |
| cluster bomblets | Cinderburst |
| placed turret beacon | Sunflare Beacon |
| release as party heal over time | Hearth Release |
| geyser knock-up ring | Caldera Finisher |
| distance-scaling pierce | Horizon Shot |
| parry-triggered roar | Rex Roar |
| fire cone + burning ground | Dragonfire Wake |
| aftershock second ring | Mountainbreaker |
| moving dance + damage cut | Mirror Dance |
| block-scaled spin + arrow block | Patient Storm |
| growing storm, implosion | Unwritten End |
| bolt bouncing, rising damage | Ascending Bolt |
| release, then re-bind | Endless Binding |

62 rows, 62 different cores. Close pairs checked: Revolving Door (pull + fling, Bo) vs Collapse Point (well + crush, at the target) vs
Unwritten End (implosion at a storm's end); Second Opinion (hops allies) vs Mossheart Bloom (heals the most-hurt ally from enemy hops) vs
Warm Spring (ground springs); Long Volley (refund by distance) vs Horizon Shot (damage by distance); Vent Bolt (flat pierce of 3) vs Ascending
Bolt (bounces, rising). Class-ability checks: Loophole Lance is a bolt (not the Mage's channelled Arcane Beam); Thornfield spikes are traps
where arrows land (not Arrow Rain); Warm Spring springs are 3 s dots at bounce points (not the Priest's Sanctuary zone) - review in build.

## 7. Balance vs the four power sources

- A signature is ~10-15 % of a weapon's sustained damage (base: 3-5 hits per meter of ~8-20 hits). A UT twist moves that share by at most
  about +-10 % of itself (so about +-1.5 % of the weapon's damage) and only in its niche - "only slightly". `utp_net`'s fit (SkyyGear,
  `UT-28-Build-Sheet` section 3) does not count signatures: add them to `_UTP_UNMOD` (no free body power from them).
- Mythic: x1.3-1.6 move damage and 44-60 % faster charge = about x2-2.5 the signature share -> about **+12-20 % weapon-source damage** on top of
  the Mythic stats (x1.10 a Fabled). Weapon source as a whole stays about +25-30 % over a Fabled weapon - still one of four: accessories and
  pets keep their share because every signature scales only with the weapon's own hit (their damage / crit / element lines multiply it like
  any hit), never adds Strength / Mana / crit itself, and the short buffs (Mirror Dance -30 % taken, Runebreak +20 % taken) last <= 6 s.
- Heals in signatures (Second Opinion, Warm Spring, Mossheart Bloom, Primal Cleave, Bloodmoon Shot, Hearth Release) count as the weapon's
  part of sustain; pets / accessories with heal lines stack on top, never replaced. Priest heal totals go through the existing
  `skill:fn:healxp` path (no new XP source).
- Bosses: pulls, stuns, freezes, roots and yanks are off / short on bosses and mini bosses (`bosses.roles`), so a Mythic never trivialises a
  boss through control.
- Check after each round: `python tools/balance_model.py --p9 --check` (unchanged rows) and refresh the Class Balance Workbench (memory rule).
  New GUESS for the model: `sigshare` = 12 % of weapon damage at base, x the Mythic charge factor (research/balance has no source - UNVERIFIED).

## 8. Build split (after sig2, which is live: SkyyArmory 0.1.45)

| Round | Mods (next numbers UNVERIFIED) | Size | What |
|---|---|---|---|
| `sig3` | SkyyGear 0.3.44 + SkyyArmory 0.1.46 | full round (several mods, every tooltip) | the 12 live UT rows: `sig.ut` defaults (Paperweight -20, Ricochet bow +25; the rest 0), the C+ charge rules (Overtime Health, Pocket Knife back / front, Short Notice half draw, Combat bash, Test Zoom range refund), the W fired-window probe + Weighted Vortex; Second Opinion + Revolving Door in Armory; the A auto-release probe on Hepta Axe (meter already exists) then Ghost Sword; bridge `armory:fn:sigfx`; tooltip lines |
| `sig4` | SkyyArmory 0.1.47 (+ Gear table) | full round (engine) | the 7 base family signatures (staff, soul cage, spear, axe, club, longsword, great shield) + Loophole Lance (needs the staff root) + the dash and pull probes |
| `sig5` | SkyyGear 0.3.45 + SkyyArmory 0.1.48 | full round (pack ids, several mods) | the 13 live Mythic signatures: W on Zweihander / Lahat / Dual Rune Blade / 3 dev bows, A on the 4 Elementals / 2 flails / Rune Blade 1 (needs the sig3 probe PASS); no pack file |
| UT-28 round | SkyyGear + SkyyArmory (UT-28 sheet section 7 builders A / B) | full round (as that sheet) | rows 13-28 each ship WITH their signature from section 4 (after sig4: staff / spear / axe / longsword roots) |
| own Mythic rounds | SkyyArmory (+ SkyyMobs pools) | full rounds, in level order | the 21 specials with item + passive + signature; Z1-Z2 first (Gravewhisper, Mossheart, Thornroot, Broodspire, Sandreaver, Overseer's Repeater), Rexhide Bulwark after the parry probe |

Each round: harness (every id in sections 4-5 maps to one signature row; tooltip line <= 70 chars; `sig.ut` defaults; no pack file in the jar;
`langdup` 0 FAIL), crosscheck, lint, smoke - as Weapon-Signatures-Spec 5.2.

## Questions for Skyy

1. Our 21 Mythic specials: keep each drafted passive hook (side backstabs, piercing staff, ...) AND add the new signature? [yes - keep both,
   "better in every way"]
2. Rename our 21 drafted Mythic specials (office working names) to the zone lore names in section 5 (e.g. The Fine Print -> Gravewhisper)?
   [yes]
3. Pack weapons with NO Ability 1 (4 Elemental swords, 2 flails, Rune Blade 1, Ghost Sword, Hepta Axe): their signature fires by itself on
   your next swing once the meter is full (no key, no Armory file touched), or ask LadyPaladra first for a real Ability 1 key at runtime?
   [auto-release now; ask LadyPaladra in parallel and switch if they agree]
4. Pack / developer weapons that already have a vanilla signature (Zweihander, Lahat Chereb, Dual Rune Blade, the 3 Mythic dev bows): keep
   their move and add the Mythic part on top? [yes - add on top]
5. The Mythic shield (Rexhide Bulwark) sits in the off hand, where Ability 1 is not: its move fires on a perfect parry while your main-hand
   meter is full (spending it)? [yes]

## For the local session (UNVERIFIED)

- W path: GearSigX can see the meter fall full -> ~0 within one tick when a vanilla signature fires (not confused with a swap, profile busy or
  the 0.75 s re-baseline); the window length per vanilla move (Vortexstrike, Razorstrike, Whirlwind, Groundslam, Volley, Big Arrow, the dev
  bow shots); whether signature hits are already tagged (SkyySkills 0.4.31 rewrote their Mana-on-hit lines, so the interaction ids are known).
- Armed shots (Volley / Big Arrow / dev bows): telling the armed shot by the `SignatureCharges` drop and its projectile config.
- A path: the HUD meter + ready glow on an item with no Ability 1 root once `skyygear_sig` gives it a max; emptying the meter by
  `addStatValue` without the engine refilling it; Hepta Axe's inherited meter 9 already fills (Weapon-Signatures-Spec 1.2) - probe it first.
- In-game test 241 (sig1: pack meter, rates, tooltip block) - not yet confirmed by Skyy; sections 4-5 build on it.
- `GearSigX` TOP tier = 15 (the % table above assumes it; Onyxium T16 clamps).
- Pull (negative push), player dash / blink, knock-up, damage ground areas, projectile blocking while spinning, homing (fallback = instant
  hits), off-hand perfect-parry timing, a forced-crit flag on GearHit, a damage-taken mark (Awed-style) from SkyyArmory.
- Applying vanilla Slow / Root / Stun / Freeze effects from SkyyArmory directly (SkyyClasses does it today).
- Dev bows have no boss pool yet: the Z2 / Z3 / Z4 picks for Pull / Vampire / Bomb are a default for the boss round.
- Ghost Sword / Hepta Axe swings must count as weapon hits for the top-up (Gear's hit family for The Armory templates - Ghost Sword copies
  `Template_Weapon_Sword`, Hepta `Template_Weapon_Battleaxe`, so likely yes).
- The UT-28 trade-off texts stay as in that sheet; these Ability 1 lines are separate (the sig1 block), no new lang keys.
- Item names in section 5 (and the UT-28 names) are new and UNVERIFIED vs vanilla ids / lang keys and other pack mods (grep before the round);
  "Scarak" is a vanilla faction word (UT-28 sheet note).
- Weapon-Signatures-Spec 3.1 / 3.2 ("UT = cheaper", "pack root-less = none") is superseded by this file - the local session should point
  that spec and `research/classes/*.md` "Weapon signature" sections here (then `python tools/class_pages.py`), and add this file to INDEX.md.
