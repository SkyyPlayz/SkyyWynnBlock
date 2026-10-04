# Class roles - ideas (what Realm of the Mad God teaches us)

*Research and ideas, 2026-10-03. Nothing is built or decided. Owner: Skyy (they/them). Skyy asked: "right now they are basically just
different weapon users ... look into realm of the mad god ... they all have something special they do that makes them valuable to the
team ... come up with a big list of good class ideas, then list the ones that would work well with vanilla vs the ones we would have to
build gear for."*

*Repo sources (read-only): `SkyyClasses/build_skyyclasses_0.1.11.py` (roster, weapon rules, the UNASSIGNED list),
`research/Classes-Berserker-Priest-Spec.md`, `research/cloud/Class-Abilities-Draft.md`, `research/Skill-Trees-2-Spec.md`,
`research/Hytale-Runes-Research.md`, `research/SkyyArmory-Spec.md`, `research/Charged-Attack-Research.md`,
`SkyyGear/build_skyygear_0.2.1.py` (weapon families, `gear.exclude`, ammo ids), `SkyyGear-Stat-Catalog.md`, `HANDOFF.md` section 3,
`OPEN-QUESTIONS.md` (the 2026-10-03 class identity answers), `research/Pets-Idea.md`.*
*VERIFIED = proven in one of those docs or scripts. UNVERIFIED = needs the game or an engine probe. Every number is a placeholder.*

> **Skyy's decisions after this was written (2026-10-03 evening, OPEN-QUESTIONS):**
> - **Shaman -> MONK** ("lets swap shaman out for a monk, that uses a staff ... id rather build our own"): the unplayable Shaman slot becomes
>   the Monk. The **Ascetic** idea below (bo staffs, Flowing Form party attack-speed stance, dodges) is the Monk's starting design. Which
>   staff is still open [default: the melee Bo staffs, so the Mage keeps the magic staffs]. Shaman stays an idea for later.
> - **Wand vs staff** ("swap its charged attack to an AOE ... if you or allies are in that area you heal for a little more (like +10% more)"):
>   Priest wands get a charged BURST (explodes on contact, less damage per enemy, big area, +10% Priest heal for anyone inside); Mage staffs
>   keep the single-target charged shot. Priest **Mend** below would come on top of that.
> - **2026-10-04 traversal = the CHARGED attacks** (Skyy; OPEN-QUESTIONS LOCKED 2026-10-04): staff = teleport in the look direction (10 blocks,
>   tree upgrades + custom distance; a lingering light trail does AoE damage); wand = hop opposite to where you look (look down = straight up) +
>   an exploding orb (AoE 6) leaving a 9-block healing orb (20% of the explosion damage per second, 3-4 s); MONK = Bo staff, charged = pole-vault
>   lunge kicking enemies in the way for 2x, slow 'flowing' fall, and timed bounds on landing that chain like a skipping stone (no damage,
>   extra Stamina); one free MID-AIR jump right after the vault (the first bound needs no ground timing); a timed ground jump takes no fall
>   damage and launches farther the farther you fell.
> - **2026-10-04 Priest 2nd weapon = SOUL ORB** (Skyy, new weapon): hold right-click for life-drain tethers (lock on, look away freely, steady DPS
>   for steady Mana, no Mana regen while active, damage stored as bonus healing; tiers add tethers - Mithril ~8); its traversal = WINGS OF FATE
>   (gliding bounds the way you look, locks onto an ally that way and carries you to them; blue wings + glowing trail). Spellbooks move to
>   the Mage (traversal open - proposed Rune Recall).
> - **2026-10-04 Soul Orb ladder** (Skyy): base Soul Orb (blue, 1 tether) -> Copper Soul Cage (life essence, green, 2 tethers, 1.1x) -> Iron
>   (fire essence, red, 4, 1.1x) -> Thorium (6, 1.5x) -> Cobalt (10, 1.5x) -> ... -> max 20 tethers (a gem on each of a dodecahedron's 20 points).
> - **2026-10-04 more traversals** (Skyy): Mage spellbook = LEVITATE; Assassin kunai = throw-and-teleport (~20 blocks) + hold right-click to
>   return with an AoE knockback; an Assassin class ability = a RotMG-style CLOAK (cloak, teleport in, hit, teleport out).
> - **2026-10-04 FIST traversal** (Skyy): Rising Strike - uppercut leap that knocks enemies up; brief slow hang time for you and them at the
>   top; hits on airborne enemies send them flying; crouch near the top = Plunge Punch dragging them down into the slam (no fall damage, no
>   Acrobatics XP); no plunge = a 15%-slower steerable fall. Both Monk falls: 15% slower, 15% less fall damage.
> - **2026-10-04 weapons** (Skyy): 2 weapon types per class, NO sharing for now - Warrior swords + spears, Archer shortbows + crossbows,
>   Berserker axes + maces / clubs, Priest wands + SOUL ORB, Assassin daggers + kunai, Monk Bo staff + fist weapons (hand wraps, gauntlets,
>   claws), Mage staffs + SPELLBOOKS (traversal open). Section 4's shared-weapon ideas wait until sharing is allowed; later class idea: Martial Artist (kicks + fists).
> - Skyy finds the Priest "a little Op" next to a new Mage (healing caps are being tuned live; a staff asset bug is being checked).

> **Skyy's direction 2026-10-04 (replaces "one ability = one job" in section 1 / rule 2):**
> - Hytale has **2 ability slots** (the two 0.7 rune lines; 3 if Q is made changeable) -> every class gets **2 class abilities**, both changeable
>   in the class skill tree -> 1-3 ability options per class, not RotMG's one.
> - Abilities are built on the **rune system**: unlock 2 skills, then **modifiers** (up to 2 per ability, like vanilla), and later
>   **variations** of each skill (same base ability with a twist - like RotMG's UT abilities).
> - Later: **saved rune loadouts** - up to 3 saved setups per class, swapped with a hotkey / macro (needs SkyyProfiles to save the rune
>   sections - research/Hytale-Runes-Research.md 4.4).
> - OPEN (Skyy): traversal - Wynncraft gives every class a movement skill, and most Hytale weapons already have a traversal charged attack:
>   make the 2nd class ability the traversal, or make every charged attack traversal? Main-session recommendation: ability 1 = the team
>   job, ability 2 = a class MOVEMENT skill that also does a class thing (Warrior charge + taunt, Mage blink + rune, Archer leap back +
>   snare, Priest dash to an ally + heal, Assassin shadowstep, Berserker leap slam, Monk flowing step + party haste), swappable in the tree
>   for a non-movement variant; weapon charged attacks stay weapon attacks (ranged / magic charged shots are their damage, wands get the
>   burst, and forced lunges near island edges mean void deaths); Acrobatics (double jump, roll) stays everyone's base movement; Q stays
>   the weapon's own Signature for now.

## 0. For Skyy

1. Right now a class is mostly "the weapon you're allowed to hold". In RotMG, each class also has ONE ability that does a job for the team.
2. The idea: every class gets its weapons plus ONE **Class Ability** (it costs Mana), a passive, and a way to play solo.
3. The jobs are tank, healer, buffer, debuffer, crowd control, burst, single target, summoner and scout.
4. Our 7 classes would be: Warrior tank, Archer crowd control, Mage burst, Berserker party buffer, Priest healer, Assassin priority killer, Shaman totems.
5. RotMG's best trick is that one weapon type serves 3 classes, each with a different ability. We can copy the trick without copying their classes.
6. Section 4 has 31 new class ideas, all with our own names.
7. How they split: 13 work with vanilla weapons now, 11 need custom gear, and 7 need a big new system (minions, taunt, decoys).
8. Build this first: a small "class ability core" - one button, Mana, party effects, and about 12 shared status effects with icons.
9. Then wave 1: Priest **Mend**, Berserker **War Cry**, Archer **Pinning Shot**, and **Tinker** (a 6th class made only from vanilla items).
10. When Hytale 0.7 ships, each Class Ability becomes that class's rune on line 1, and line 2 is a pick from the class tree. Your decisions are in section 7.

## 1. How RotMG makes classes matter

There are 19 classes; the Druid arrived in February 2026. Every class has 1 weapon type, 1 armor type (heavy, leather or robe) and 1 ability item
that costs Mana. I read RealmEye only through search snippets because its pages block direct fetches, so some numbers may be out of date.
The other sources are the official site and Wikipedia. Links are at the end of this section.

| Class | Weapon | Armor | Ability item - what it does | Role | Why a party wants it |
|---|---|---|---|---|---|
| Rogue | Dagger | Leather | Cloak - invisible for a few seconds, then a Lethal Strike | Scout, solo | Not much - it sneaks past danger |
| Archer | Bow | Leather | Quiver - big piercing arrow that Paralyzes or Slows | Ranged control | Pins enemies in place |
| Wizard | Staff | Robe | Spell - burst of shots at the cursor ("spell bomb") | Burst AoE | Clears packs fast |
| Priest | Wand | Robe | Tome - instant heal + heal-over-time on allies | Healer | Keeps everyone alive |
| Warrior | Sword | Heavy | Helm - Berserk (faster attacks) on the party, Speedy on self | Melee + buffer | Whole party attacks faster |
| Knight | Sword | Heavy | Shield - cone that damages and Stuns | Stun tank | Stops enemies shooting |
| Paladin | Sword | Heavy | Seal - Damaging + Healing on the party | Buffer + healer | Party hits harder and heals |
| Assassin | Dagger | Leather | Poison - thrown vial: hit + damage over time in an area | AoE damage over time | Melts groups |
| Necromancer | Staff | Robe | Skull - drains HP in an area, heals self + nearby allies | Damage + sustain | Heals while it fights |
| Huntress | Bow | Leather | Trap - thrown trap: area damage + Slowed | Area denial | Slows and hurts packs |
| Mystic | Staff | Robe | Orb - Stasis (frozen, untouchable) + Curse (takes more damage) | Debuff + control | Takes enemies out; all hit harder |
| Trickster | Dagger | Leather | Prism - teleport + a Decoy that draws enemy fire | Decoy, utility | Pulls aggro off the group |
| Sorcerer | Wand | Robe | Scepter - chain lightning that jumps between enemies | Multi-target burst | Hits many at once |
| Ninja | Katana | Leather | Star - hold for Speedy (drains Mana), release to throw | Mobile damage | Speed and repositioning |
| Samurai | Katana | Heavy | Wakizashi - slash that inflicts Exposed (lower defence) | Tanky debuffer | Everyone does more to tanky bosses |
| Bard | Bow | Robe | Lute - aura that Inspires allies (weapon range x1.25) | Buffer | Party hits from a safer range |
| Summoner | Wand | Robe | Mace - summons a minion that fights | Summoner | Extra damage + a distraction |
| Kensei | Katana | Heavy | Sheath - channel, then dashes that leave a damaging trail and raise stats | Melee skirmisher | Risky, high damage |
| Druid | Wand | Leather | Sigil - casts and hits fill a meter, then shapeshift into an animal form | Shape-shifter | Adapts: tanky or stealthy form |

Notes: a 2026 public test reworked the Necromancer's skull into raised undead that steal HP, plus a meter for a party burst heal. It is not in the
Season 27 patch notes. New classes unlock by getting two other classes to level 20 (Samurai: Knight + Ninja; Druid: Sorcerer + Huntress).

**Same weapon, different jobs** (the core trick):

| Weapon | Classes and their job |
|---|---|
| Sword | Warrior (party attack speed), Knight (stun tank), Paladin (party damage + heal) |
| Dagger | Rogue (stealth), Assassin (poison AoE), Trickster (decoy) |
| Bow | Archer (paralyze), Huntress (traps, slow), Bard (range buff) |
| Staff | Wizard (burst), Necromancer (drain-heal), Mystic (stasis, curse) |
| Wand | Priest (heal), Sorcerer (chain lightning), Summoner (minion), Druid (shapeshift) |
| Katana | Ninja (speed), Samurai (expose), Kensei (dash) |

Our version could be: bows for Archer (control), Beastwarden (pet) and Wayfinder (scout); swords for Warrior (tank), Templar (holy zone) and
Spellblade (imbue); daggers for Assassin (backstab), Hemomancer (blood buff) and Illusionist (decoy).

**What we take from it (the ideas, not their classes):**
1. **One ability = one job.** Weapons and armor are shared; the ability item is what makes the class. For us: one Class Ability per class.
2. **Same weapon, many jobs.** 6 weapon types carry 19 classes. For us: our ~15 vanilla weapon families plus the ones no class owns yet can carry many classes.
3. **A small, readable set of status effects.** About a dozen named buffs (Damaging, Berserk, Healing, Speedy, Inspired) and debuffs (Curse,
   Exposed, Slowed, Paralyzed, Stunned, Stasis), each with an icon. Different ones stack, so parties mix classes. For us: section 2.3.
4. **Bosses shrug off hard crowd control, but debuffs still land.** A boss that is immune to Stasis can still be Cursed. For us: the boss rule in 2.3.
5. **The ability helps you too.** Priests heal themselves and Warriors get Speedy, so support classes can still solo. For us: rule 4.
6. **Mana is the only limit, and ability items come in tiers and unique versions.** A quiver that slows or one that paralyzes, an orb with a
   longer curse - same class, new twist. For us: item levels and rarity, tree lanes, and rune modifiers.
7. **Armor type and stat caps set the feel.** Robe classes are glass cannons, heavy classes tank. For us: your identity notes (Mage is the glass cannon).
8. **Support has to pay off.** XP is not split between nearby players. RotMG lowered the damage needed to qualify for loot because
   low-damage support classes were missing drops. Newer classes add depth with hold, channel or meter mechanics instead of extra buttons
   (Ninja, Kensei, Druid). For us: rule 7, and the vanilla Signature meter.

**Sources.** [Wikipedia](https://en.wikipedia.org/wiki/Realm_of_the_Mad_God). Official: [Druid design](https://remaster.realmofthemadgod.com/?p=5661),
[Druid + Necromancer test](https://remaster.realmofthemadgod.com/?p=5391), [Season 27 notes](https://remaster.realmofthemadgod.com/?p=5769).
RealmEye wiki: [Paladin](https://www.realmeye.com/wiki/Paladin), [Seal of the Initiate](https://www.realmeye.com/wiki/seal-of-the-initiate),
[Combat Helm](https://www.realmeye.com/wiki/combat-helm), [Knight guide](https://www.realmeye.com/wiki/knight-class-guide),
[Dimensiongate Orb](https://www.realmeye.com/wiki/dimensiongate-orb), [Embellished Quiver](https://www.realmeye.com/wiki/embellished-quiver),
[Depthchaser Trap](https://www.realmeye.com/wiki/depthchaser-trap), [Lightning Scepter](https://www.realmeye.com/wiki/lightning-scepter),
[Cloak of Shadows](https://www.realmeye.com/wiki/cloak-of-shadows), [Fire Spray Spell](https://www.realmeye.com/wiki/fire-spray-spell),
[Remedy Tome](https://www.realmeye.com/wiki/remedy-tome), [Felwasp Toxin](https://www.realmeye.com/wiki/felwasp-toxin),
[Bloodroot Extract](https://www.realmeye.com/wiki/bloodroot-extract), [Specialist Mace](https://www.realmeye.com/wiki/specialist-mace),
[Enforced Wakizashi](https://www.realmeye.com/wiki/enforced-wakizashi), [Samurai guide](https://www.realmeye.com/wiki/samurai-class-guide),
[Kensei guide](https://www.realmeye.com/wiki/kensei-class-guide), [Dynastic Star](https://www.realmeye.com/wiki/dynastic-star),
[Summoner guide](https://realmeye.com/wiki/summoner-class-guide). RealmEye forum: [Bard guide](https://www.realmeye.com/forum/t/bard-class-guide/59565),
[Trickster guide](https://www.realmeye.com/forum/t/trickster-guide/31673), [loot thresholds](https://www.realmeye.com/forum/t/soulbound-thresholds-answered/24047).
Group vs solo discussion: [Steam thread](https://steamcommunity.com/app/200210/discussions/0/343787920134036473).

## 2. SkyWynn class design rules (proposal)

We call the one signature ability the **Class Ability**, so it isn't confused with Hytale's own weapon Signature meter (the Ability 1 key).

### 2.1 The rules

| # | Rule | RotMG lesson |
|---|---|---|
| 1 | **Weapons:** 1-3 families per class. A family may serve up to 3 classes; old classes keep every weapon they have now | 2 |
| 2 | **ONE Class Ability** (costs Mana) = the class's team job. It's the same button all game. Levels, tree lanes and 0.7 rune modifiers change how strong it is or how it works - they never replace it | 1 |
| 3 | **A passive** that is always on, so the class feels different even between button presses | - |
| 4 | **A solo answer:** every Class Ability helps the caster too. VERIFIED lock: "Skyy wants the pack 100 % usable solo" (Classes-Berserker-Priest-Spec 2.4) | 5 |
| 5 | **Stat identity:** your notes (Mage glass cannon, Priest less damage, Warrior / Archer sturdier), plus an optional soft bonus for wearing your class's armor type (cloth, leather or metal). Never a lock | 7 |
| 6 | **Team value comes from one shared status list** (2.3), with icons. Buffs stay around +10-20%, so no class is ever "required" | 3 |
| 7 | **Support gets paid.** Heals already pay Divinity XP (`skill:fn:healxp`, VERIFIED). Buffs and debuffs would pay "assist XP" the same way, and party members near a kill would share kill credit | 8 |
| 8 | **Mana first, short cooldowns.** Mana is the main limit. A buff or debuff also gets a cooldown of about 1.5x its length, so a big Mana pool can't keep it up forever. Costs are fixed in the jar, because the client predicts Mana (VERIFIED, SkyyArmory-Spec) | 6 |
| 9 | **Each ability checks the class itself.** The weapon lock only cancels damage (VERIFIED, SkyyClasses notes), so heals and buffs need their own class check, the way DeployGuard checks the Healing Totem | - |

### 2.2 The roles

| Role | Job in a party | Today | Proposed classes |
|---|---|---|---|
| Tank | takes the hits, holds mobs | Warrior (shield only) | Warrior, Warden, Aegis, Geomancer |
| Healer | restores health | Priest (placeholder heal on hit) | Priest, Apothecary, Lifeweaver, Templar |
| Buffer | makes the party stronger | - | Berserker, Minstrel, Ascetic, Quartermaster, Hemomancer |
| Debuffer | makes enemies weaker | - | Hexer, Sunderer, Blightcaller, Frostbinder |
| Crowd control | stops or moves enemies | - | Archer, Snaresmith, Voidweaver, Galewalker |
| Burst AoE | kills packs fast | Mage | Mage, Bombardier, Stormcaller, Skylancer |
| Single target | kills elites and bosses | - | Assassin, Gunslinger, Duelist, Reaper, Spellblade |
| Summoner | adds extra bodies | - | Shaman (totems), Gravecaller, Beastwarden, Tinker |
| Scout / utility | info, mobility, tricks | - | Wayfinder, Illusionist, Chronomancer, Runesmith |

Example: a 4-player boss party of Warrior (Warded + taunt), Priest (Mend), Hexer (Hex) and Mage (Meteor). Each one brings something the others can't.

### 2.3 One shared list of status effects

| Status | Effect (placeholder) | Given by | Built on |
|---|---|---|---|
| Empowered | +15% damage dealt | Templar, Hemomancer, Shaman War Totem | our damage filter (SkyyGear / SkyyMobs already change damage there, VERIFIED) |
| Haste | +15-20% attack speed | Berserker, Minstrel, Ascetic, Chronomancer | swing-speed effects (SkyyTrees already ships them for tools, VERIFIED) |
| Swift | +10% move speed | Minstrel, Wayfinder | the speed modifier (SkyyAccessories Speed line, VERIFIED) |
| Warded | -20% damage taken | Warrior, Aegis, Runesmith | our damage filter |
| Mending | heal over time | Priest, Apothecary, Templar, Shaman | the Priest heal code (VERIFIED) / the vanilla Healing Totem heal |
| Hexed | +20% damage taken from everyone | Hexer | our damage filter |
| Exposed | every hit on it crits (first 3 s) | Sunderer, Duelist | SkyyGear's crit roll |
| Marked | +10% damage from the party, shows the target to focus | Gunslinger, Beastwarden, Wayfinder | damage filter + a glow (UNVERIFIED) |
| Weakened | deals 10-15% less damage | Hexer, Blightcaller, Minstrel | SkyyGear "Weaken Enemy" (stat catalog: Keep) |
| Slowed | moves slower | Archer, Warden, Snaresmith, Frostbinder, Chronomancer, Shaman | vanilla Slowness Totem (0.6.8), 0.7 frost slow |
| Rooted | can't move, can still attack | Archer, Snaresmith, Runesmith | vanilla Root effect (the Root wand, VERIFIED) |
| Stunned / Frozen | can't move or attack (Frozen breaks on a hit) | Warden, Frostbinder, Stormcaller, Bombardier | vanilla `Weapon_Bomb_Stun` + 0.7 freeze - effect on mobs UNVERIFIED |
| Poisoned / Burning | damage over time | Blightcaller, Apothecary, Mage | SkyyGear Poison stat, vanilla fire and poison bombs, 0.7 poison stacks |

Rules: two copies of the same status don't stack (the strongest wins), but different statuses do. Bosses take half duration from Rooted,
Stunned and Frozen, while soft debuffs always land. Each status shows an icon: Hytale effects have a `StatusEffectIcon` field (VERIFIED,
`research/Cooking-Skill-Spec.md`), but custom icon art is UNVERIFIED in game.

### 2.4 How a Class Ability could be cast

| Way | Works on 0.6.8 today? | Good | Catch |
|---|---|---|---|
| A. Off-hand "class relic" (Utility slot, right-click) | Likely: shields and the Kunai already work from that slot (VERIFIED, SkyyClasses notes) | Closest thing to RotMG's ability slot; relic tiers = rarity and levels | UNVERIFIED: which item gets right-click when the weapon uses it too (wands and staffs use both buttons). The Warrior's shield competes for the slot |
| B. Hotbar class item (thrown or used like the Healing Totem) | Yes (deployables and bombs) | Proven (DeployGuard already checks the totem) | You switch away from your weapon to use it |
| C. Weapon hold, or Hytale's weapon Signature (Ability 1 + SignatureEnergy meter) | Yes (SkyyArmory already rewrites tap / hold) | No new item; the meter could be an "ultimate" layer like the Druid's | Holding is how you deal damage; one override per weapon family |
| D. Hytale 0.7 rune line (keys Use Ability 2 / 3) | No - 0.7 only, and you chose to wait for the release | Real keys, HUD, cooldown, modifiers; the rune's `Weapons` field already acts as a class lock | Only 2 lines (locked by the client) |
| E. A `/cast` command | Yes | Handy for testing | Too slow in a fight |
| F. Crouch + click | The server can see crouch (rolls use it) | - | Breaks your "no click-combos" lock |

**Recommended:** A now (or B if the probe fails), then D once 0.7 is out.

## 3. The 7 classes we have, made distinct

| Class (job) | Class Ability (Mana) | Team value | Passive | Solo answer | Changes from today |
|---|---|---|---|---|---|
| **Warrior** (tank) | **Rallying Guard** (20): you + party within 6 blocks get Warded for 6 s; mobs within 8 blocks turn to you (taunt, UNVERIFIED) | Takes the hits meant for the Mage and Priest | **Iron Hide**: +10% defence; shield blocks reflect 15% (Thorns) | Warded on yourself | The kit shield becomes the class core. If taunt isn't possible: a shield bash that Stuns a cone for 1.5 s |
| **Archer** (crowd control) | **Pinning Shot** (15): a piercing arrow; every enemy hit is Rooted 2 s, then Slowed 2 s | Holds packs still for melee and keeps them off the healer | **Hunter's Focus**: +1% damage per 2 blocks of range (max +20%); crossbows stay loaded (live) | Root, then kite | Arrow Storm / Escape / Arrow Bomb (Wynn draft) become tree picks |
| **Mage** (burst) | **Meteor** (35): after 1 s, a Fire blast with radius 4 | Fastest pack clear; Burning sets up element combos later | **Glass Cannon**: +20% spell damage, -15% health and defence (your lock) | Kill first; Teleport as the 2nd pick for mobility | Staff tap / hold stay the basic attack |
| **Berserker** (party buffer) | **War Cry** (20): party within 8 blocks gets Haste for 8 s; you get Enrage (+30% damage dealt, +20% taken - the vanilla 0.7 rune numbers) | Whole party attacks faster | **Bloodlust**: up to +25% damage as your health drops; charged hits heal 5% of the damage | Enrage + self-heal | Tree lanes: Warbringer = bigger War Cry, Bloodbound = life steal, Smasher = stun slams |
| **Priest** (healer) | **Mend** (20): instant heal for the party within 8 blocks + Mending for 5 s | Keeps the party alive through boss hits | **Faith**: today's heal-on-hit stays as a small trickle | Self-heal 100% (your lock) | The placeholder heal gets smaller; the real heal is the button |
| **Assassin** (priority killer, later) | **Shadowstep** (15): blink behind the target; your next hit is a guaranteed backstab | Kills elites and casters first; pulls mobs off the healer | **Backstab**: +50% damage from behind (vanilla dagger backstab, VERIFIED) | Hit, step, escape | Enable with daggers + kunai (the kunai is thrown from the off-hand, VERIFIED) |
| **Shaman** (zone support, later - REPLACED BY MONK, Skyy 2026-10-03; kept as an idea) | **Totem** (25): plant one totem for 20 s - Slowness (vanilla), War (party Empowered) or Spirit (Mending), chosen in the tree | A buff / debuff zone the party fights in | **Spirit Bond**: +50% Mana regen near your totem | Your totem works for you too | Ship with the vanilla Slowness Totem; your custom weapon comes later |

| Rework | Type (see section 5) | Effort | Note |
|---|---|---|---|
| Priest Mend | A | S/M | the heal, party and heal-XP code is already live |
| Berserker War Cry | A | S | one party effect + Enrage |
| Archer Pinning Shot | B | M | a custom shot + the vanilla Root effect |
| Mage Meteor | B now / A at 0.7 | M | 0.7 has a vanilla Fireball rune |
| Assassin Shadowstep | B | M | a short blink in combat is UNVERIFIED |
| Shaman Totem | A + B | M | 2 new totems copied from the Healing Totem's setup |
| Warrior Rallying Guard | C (taunt) / B (stun fallback) | M-L | taunt depends on engine check 3 |

## 4. The big list - 31 new class ideas

Weapon labels: *shared* = also used by an existing class (needs rule 1); *new* = custom gear; *unowned* = vanilla, but no class owns it yet
(bombs, guns, claws, blowgun, turret, flamethrower - VERIFIED, the UNASSIGNED list in SkyyClasses 0.1.11).

### 4.1 Tanks and protectors
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Warden** | maces (shared) + shields | **Concussion** (20): a slam that Stuns everything in a cone for 2 s | Stops a pack or boss from attacking - free hits for everyone | **Heavy Hand**: charged hits Slow for 2 s | Stun one dangerous mob at a time | mace charged swing, shields, Stunned |
| **Aegis** | wands (shared) + shields | **Dome** (30): a 5 s bubble that deletes enemy projectiles; allies inside are Warded | Shields the group from archers, mages and boss volleys | **Steadfast**: no knockback with a shield up | Fight ranged mobs from inside the bubble | SkyyClasses projectile tracker, damage filter |
| **Geomancer** | earth gauntlets (new) | **Stone Wall** (25): raise a 5-wide stone wall for 8 s | Cover and choke points; splits packs | **Bedrock**: +15% defence while standing still | Wall off half the mobs | temporary blocks, Earth element, island protection |

### 4.2 Healers
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Apothecary** | splash flasks (new) + potions | **Mending Mist** (25): a 4 s cloud - allies get Mending, enemies get Poisoned | A group heal that also hurts | **Brewer**: potions you drink are 25% stronger | Stand in your own cloud | Alchemy skill + tree, vanilla poison potion bomb as the model |
| **Lifeweaver** | wands (shared) + lantern (new, off-hand) | **Lifeline** (20): an 8 s tether - the ally heals 4%/s and 30% of their damage moves to you | Keeps the tank alive (Priest heals the group, this heals one) | **Triage**: +50% healing on allies under 40% health | Tether a mob instead and drain it | Priest heal code, party, heal XP |
| **Templar** | swords (shared) + shields | **Consecrate** (30): a 6 s holy circle - allies are Empowered and heal 2%/s; undead burn | Damage buff and healing in one spot | **Zeal**: kills heal you and nearby allies 3% | Fight inside your circle | Healing-Totem-style deployable, statuses |

### 4.3 Buffers
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Minstrel** | instruments (new: lute, horn, drum) | **Battle Song** (25): an 8 s aura - party Haste + Swift; the tree swaps songs (Mending Song, or Dirge = enemies Weakened) | A party buff you change per fight | **Encore**: buffs you give last 2 s longer | The song buffs you too | party, statuses, sounds (UNVERIFIED) |
| **Ascetic = the MONK** (Skyy 2026-10-03) | bo staffs (vanilla Bo_Bamboo, Bo_Wood) | **Flowing Form** (15): an 8 s stance - each hit gives the party within 6 blocks +3% attack speed (max 5 stacks); you take 30% less from projectiles | Party attack speed that grows as you fight | **Inner Balance**: +10% dodge, faster stamina | Dodges + fast combos | Acrobatics dodge, stamina, Haste |
| **Quartermaster** | cleavers (new) or clubs (shared) | **Field Kitchen** (35): a cookpot for 20 s - allies who use it get a food buff + a 20% heal | Long buffs between fights | **Hearty**: food you eat lasts 50% longer | Buffs yourself | SkyyCooking grades + tree, a deployable |
| **Hemomancer** | daggers (shared) | **Blood Pact** (costs 15% of your HEALTH, not Mana): party Empowered + 5% life steal for 8 s | The biggest damage buff, paid in blood | **Sanguine**: your Life Steal is doubled | Life steal pays the pact back | 0.7 runes can cost Health (VERIFIED), Gear Life Steal |

### 4.4 Debuffers
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Hexer** | spellbooks (shared) | **Hex** (25): curse an area for 6 s - enemies are Hexed (+20% damage taken) | The whole party deals more | **Wither**: your hits Weaken | Weaken keeps you alive | damage filter, Gear Weaken stat |
| **Sunderer** | axes + battleaxes (shared) | **Sunder** (20): a heavy chop - the target is Exposed for 6 s, and every hit on it crits for the first 3 s | A burst window the party saves its big hits for | **Cleave**: charged hits strike everything in front | Sunder, then a charged hit | Gear Crit / Crit Damage / Overcrit, charged attacks |
| **Blightcaller** | blowgun + darts (vanilla, unowned) | **Plague Cloud** (25): a 5 s cloud - Poison stacks and poisoned mobs are Weakened; it jumps to a neighbour when one dies | Softens whole packs, so the tank takes less | **Virulence**: +1 poison stack | Kite while it ticks | Gear Poison, 0.7 poison stacks |
| **Frostbinder** | frost staff, frost spellbook, ice crystal staff (vanilla) + new tiers | **Glacial Prison** (30): freeze radius 3 for 3 s (a hit breaks it after 1 s), then Chill | Emergency hard control; Chill + Lightning = bonus damage | **Cold Snap**: Water damage Chills | Freeze, then reposition | 0.7 frost effects, Water, elemental reactions (built into the engine but unused) |

### 4.5 Crowd control
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Snaresmith** | crossbows (shared) + trap kits (new) | **Snare** (20): throw a trap (3 out at most) - the first enemy is Rooted 3 s and hurt; nearby ones are Slowed | Holds packs off the backline; set up boss arenas | **Prepared**: +25% damage to Rooted or Slowed enemies | Lead mobs into traps | deployables, vanilla Root |
| **Voidweaver** | void orbs (new magic family) | **Singularity** (30): a rift pulls enemies within 6 blocks to one point for 2 s, then pops | Bunches mobs up for the Mage or Bombardier | **Event Horizon**: +15% damage to grouped enemies | Group them, then blast | 0.7 pull + ability entities, SkyyArmory pipeline, Void lore |
| **Galewalker** | claws (vanilla, unowned) | **Updraft** (20): launch you + allies within 4 blocks up and forward; nearby enemies get knocked away | Party mobility (gaps, ledges, escapes) + peel | **Featherfoot**: no fall damage, +10% dodge | Hit and run | Acrobatics push (live), Wind, Feather accessory |

### 4.6 Burst AoE
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Bombardier** | bombs + grenade (vanilla, unowned: Bomb, Fire, Large Fire, Stun, Poison potion, Popberry, Frag) | **Carpet Bomb** (30): throw a line of 5 bombs | The biggest pack burst; Stun bombs add control | **Demolitions**: +20% blast radius; brewed bombs have a 25% chance not to be used up | Farms packs fast | vanilla bombs, Alchemy bomb brewing (live), Gear Exploding |
| **Stormcaller** | storm rods (new magic family) | **Chain Lightning** (25): jumps between up to 5 enemies, each Shocked (0.5 s stun) | Hits many targets + lots of tiny interrupts | **Static**: Lightning crits more on Chilled enemies | Thins packs | 0.7 Lightning + Ricochet / Fork, SkyyArmory pipeline |
| **Skylancer** | spears (shared) | **Skyfall** (20): leap to where you aim and crash down - AoE damage + knock-up | A gap closer that scatters packs | **Wind Rider**: no fall damage after Skyfall; thrown spears +20% | Island hopping, mobile burst | spear throw (vanilla), Acrobatics push, slam AoE |

### 4.7 Single target
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Gunslinger** | guns (vanilla blunderbusses, unowned) + new gun tiers | **Dead Eye** (20): your next 3 shots crit and pierce; the first target is Marked for 6 s | Deletes elites; the Mark helps everyone | **Steady Aim**: more crit chance while standing still | Strong 1v1, weak against packs | blunderbuss Mana gate (live), Gear crit, Charged Attack Damage |
| **Duelist** | longswords (shared) | **Riposte** (15): a 1 s parry - a blocked hit counters for x3 damage and Exposes the attacker | Boss killer; Exposed helps the party | **Momentum**: +4% per hit on the same target (max 5) | Best 1v1 class | blocking, charged attacks |
| **Reaper** | scythes (vanilla Void Scythe + new tiers) | **Harvest** (25): a wide sweep - you + party within 6 blocks heal 10% of the damage dealt | AoE damage that keeps the group topped up | **Soul Reap**: kills stack +3% damage (max 5) | Great sustain | Gear Life Steal, Priest heal code, Void lore |
| **Spellblade** | swords (shared) | **Imbue** (15): for 10 s your hits add element damage + that element's status | Puts elements on mobs so others can trigger combos | **Arcane Edge**: Magical Power also boosts melee | Balanced | 0.7 Imbue / Wind Strike runes, elements |

### 4.8 Summoners
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Gravecaller** | bone tomes (vanilla Rekindle Embers + new tiers) | **Raise the Fallen** (30): 2 skeleton warriors fight for 20 s | Extra bodies that soak hits and deal damage | **Grave Pact**: minions heal you 10% of their damage | Minions tank for you | vanilla SpawnNPC (the book already raises Risen Knights / Gunners, VERIFIED), minion control (new) |
| **Beastwarden** | shortbows (shared) + your class pet | **Sic 'Em** (20): the beast charges; the target is Marked for 8 s | A focus marker + a second body | **Bond**: your pet gets 30% of your stats | The pet tanks | pet system (Pets-Idea: a class pet per class), SkyyMobs levels |
| **Tinker** | turret + flamethrower (vanilla, unowned) | **Deploy Turret** (30): a turret shoots the nearest enemy for 20 s | Extra damage + something for mobs to hit (UNVERIFIED) | **Overclock**: turret +20% while you stand near it | Turret + flamethrower | vanilla `Weapon_Deployable_Turret`, DeployGuard pattern, Goblin Lab theme (0.7) |

### 4.9 Scout and utility
| Class | Weapons | Class Ability (Mana) | Team value | Passive | Solo | Uses |
|---|---|---|---|---|---|---|
| **Wayfinder** | shortbows (shared) + flare kit (new) | **Flare** (20): lights the area and marks enemies within 30 blocks for 10 s; allies under it get Swift | Info (elites, chests) + speed | **Pathfinder**: +15% Exploration XP, no fall damage | Explorer - chests and the map | SkyyExploration, Acrobatics, Lantern light (SkyyAccessories), minimap markers (planned) |
| **Illusionist** | daggers (shared) | **Mirror Image** (25): blink 6 blocks and leave a decoy that mobs attack for 4 s; it bursts and Slows | Pulls aggro off allies, saves the healer | **Sleight**: your next hit after a blink +50% | Escape tool | blink (push), decoy + mob targeting (new) |
| **Chronomancer** | staffs (shared) + hourglass (new, off-hand) | **Time Field** (35): a 6 s dome - allies get Haste, enemies are Slowed 40% | Speeds your side up and slows theirs at the same time | **Rewind**: once a minute, a killing blow sends you back to where you were 3 s ago | Kite in the field; Rewind is your safety net | zone entity, statuses, position snapshot (new) |
| **Runesmith** | rune hammers (new) | **Inscribe** (25): a ground glyph for 15 s - Ward, Haste or Snare (picked in the tree) | Zones you set up ahead of time for boss arenas | **Runebound**: rune casts cost 10% less | Snare glyph, then fight on the ward | 0.7 runes (ability entities + effects), Runebinder's Lattice |

## 5. The split - vanilla vs custom gear vs new systems

- **A** = the weapons already exist in vanilla, and the Class Ability is built from vanilla effects plus our code. "Ladder" = vanilla has a Copper -> Mithril line.
- **B** = needs custom gear (a new item family, projectile, effect, or model + icon). The SkyyArmory pipeline (a recoloured vanilla model, generated
  textures and icons, the metal's shortbow recipe - VERIFIED with the wands) makes a new family roughly one M round.
- **C** = needs a whole new system.
- **Effort:** S = one lean round in one mod; M = one full round; L = several rounds, or a new system. **Every NEW class** also needs the roster plumbing
  once (SkyyClasses roster + kit, a new SkyySkills class-skill slot - appended, so saves stay safe as with Fury / Divinity - plus a SkyyProfiles card, a SkyyTrees
  tree, and the SkyyGear / SkyyGuilds skill lists). That is about one full round, and cheaper per class if 2-3 classes ship together.

### (A) Works with vanilla items now - 13
| Class | Vanilla items | Ladder? | What we still build | Effort |
|---|---|---|---|---|
| Tinker | `Weapon_Deployable_Turret`, flamethrower | no (1 turret) | turret as the Class Ability, class check (DeployGuard), turret damage by level, kill XP credit | S |
| Bombardier | 7 `Weapon_Bomb_*` + `Weapon_Grenade_Frag` | ammo | 5-bomb throw; bomb damage by class level (bombs count as ammo, not gear); no block damage on islands (UNVERIFIED) | S |
| Galewalker | `Weapon_Claws_*` | UNVERIFIED | Updraft (the proven push); claws as gear (remove them from `gear.exclude`, a live Server Setup row) | S/M |
| Skylancer | spears (shared) | yes | leap + landing AoE | S/M |
| Gunslinger | `Weapon_Gun_*` blunderbusses (handgun / assault rifle are minigame guns, UNVERIFIED if obtainable) | no | Dead Eye crit window, Marked, guns as gear; a gun ladder later = B | S/M |
| Hemomancer | daggers (shared) | yes | health-cost cast, party Empowered + life steal | M |
| Ascetic | `Weapon_Staff_Bo_Bamboo`, `_Bo_Wood` (taken from the Mage by the longer name, or shared) | no (2 items) | the stance aura; bo staff tiers later | M |
| Blightcaller | `Weapon_Blowgun_*`, `Weapon_Dart_Tribal` | no | poison cloud + spread; blowgun as gear | M |
| Hexer | spellbooks (shared) | no (6 named books) | Hexed in the damage filter + a cloud visual | M |
| Sunderer | axes, battleaxes (shared) | yes | Exposed crit window in SkyyGear's crit roll | M |
| Warden | maces (shared) + shields | yes | Stunned, based on the vanilla stun bomb or Root effect (do mobs stop attacking? UNVERIFIED) | M |
| Duelist | longswords (shared) | yes | parry window on a blocked hit | M |
| Spellblade | swords (shared) | yes | at 0.7: a class rune built from vanilla Imbue Poison / Wind Strike | S (at 0.7) |

### (B) Needs custom gear - 11
| Class | Custom gear needed | Effort |
|---|---|---|
| Apothecary | a healing splash flask (copy of the vanilla poison potion bomb with a heal cloud) + Alchemy bench recipes | S/M |
| Templar | Consecrate zone = a new deployable like the Healing Totem (new setup + glow), Empowered icon | M |
| Reaper | scythe ladder Copper -> Onyxium (model from the Void Scythe, SkyyArmory pipeline), sweep attack | M |
| Stormcaller | storm rod family (item, model, icon), chain-lightning projectile, Shocked icon | M |
| Voidweaver | void orb family + rift entity + pull (cleanest at 0.7) | M |
| Frostbinder | frost focus tiers (vanilla has only 3 frost items), Frozen / Chilled icons | M |
| Minstrel | instrument family (model, icon, sounds), song aura particles | M |
| Lifeweaver | lantern off-hand item, tether beam visual | M |
| Snaresmith | trap deployables (model, trigger, Root) | M |
| Quartermaster | cleaver family + a cookpot deployable tied to SkyyCooking grades | M |
| Wayfinder | flare item + enemy marks (an outline through walls is client-side, UNVERIFIED; minimap markers later) | M |

### (C) Needs a bigger new system - 7
| Class | New system | Engine question (UNVERIFIED) | Effort |
|---|---|---|---|
| Aegis | a dome that deletes projectiles | can enemy projectiles be removed mid-flight cleanly? | M/L |
| Runesmith | ground glyph zones | needs 0.7 ability entities | M/L |
| Gravecaller | friendly minions: spawn, follow, attack, despawn, XP credit | do the vanilla Risen (Rekindle Embers) fight for the player? | L |
| Beastwarden | combat pets (the planned pet system) | can we control NPC follow / attack? | L |
| Illusionist | decoys that mobs attack | can a mod set a mob's target? | L |
| Geomancer | temporary blocks: place, revert, respect islands and claims | can blocks be placed and reverted safely? | L |
| Chronomancer | time zones + a rewind snapshot | zones before 0.7 (a deployable?) | L |

**Cheapest new classes:** Tinker and Bombardier (S). **Classes with a full vanilla weapon ladder** (shared families): Skylancer, Hemomancer,
Sunderer, Warden, Duelist, Spellblade. Classes on unowned vanilla families have only 1-3 items each, so they'll need a metal ladder later via the SkyyArmory pipeline.

**Engine checks before building** (a small probe build, admin only):
1. Off-hand relic: does right-click use it while a weapon is in hand (wands and staffs use both buttons)? This decides the pre-0.7 trigger.
2. Do Rooted / Stunned / Frozen mobs stop attacking (vanilla Root, `Weapon_Bomb_Stun`, 0.7 freeze)?
3. Can a mod choose a mob's target (taunt, decoys, turrets, minions)?
4. Do custom status icons show in the HUD?
5. Turret / minion / totem kills: who gets class XP and the drops? (Deployables deal damage as themselves - VERIFIED.)
6. Do vanilla bombs break blocks (on islands)?
7. What do the blowgun, darts, claws, handgun, assault rifle and the prototype bows (Bomb / Combat / Pull / Ricochet / Vampire) really do?
   So far we only know their names and charge steps.
8. Does vanilla have instrument items or music sounds (Minstrel)? And is there a slow-fall / glide effect (Galewalker, Skylancer)?

## 6. Recommended order

**Wave 0 - the foundation** (a new system, so one full round with ultracode, per PROJECT-RULES):
- A probe build for engine checks 1-4.
- SkyyClasses "ability core": the Class Ability trigger (relic or hotbar item); the Mana check and spend (vanilla StatsCondition / ChangeStat, proven
  by the wands); a cooldown; party targets (`party:fn:members` + a radius, like the Priest heal); the statuses from 2.3 with icons; the class check (rule 9).
- SkyySkills: an "assist XP" bridge (like `skill:fn:healxp`) and Mana growth for physical classes (question 5).

**Wave 1 - 3 reworks + 1 new class.** That's 4 different jobs: 3 use systems that are already live, and 1 uses only vanilla items.

| # | What | Job | Why first | Effort |
|---|---|---|---|---|
| 1 | Priest **Mend** | healer | heal, party and heal-XP code is live | S/M |
| 2 | Berserker **War Cry** | buffer | one party effect + Enrage | S |
| 3 | Archer **Pinning Shot** | crowd control | vanilla Root effect + a custom shot | M |
| 4 | **Tinker** (6th class) | summoner-style | every item is vanilla; the profile limit grows on its own (`class:list`, VERIFIED) | M (incl. roster plumbing) |

**Wave 2 - every class gets its Class Ability:** Warrior Rallying Guard (taunt if check 3 passes, otherwise the stun bash), Mage Meteor (+ a
Teleport pick), the Shaman release (vanilla Slowness Totem + War Totem) and the Assassin release (Shadowstep).

**Wave 3 - new classes in pairs** (to share the roster plumbing): Bombardier + Gunslinger, Hexer + Sunderer, Galewalker + Ascetic; then the
B list through the SkyyArmory pipeline. The C list waits until engine checks 3 and 5 pass.

**At 0.7** (your "wait for the release" lock):
- Each Class Ability becomes that class's rune on line 1 (Use Ability 2, with `Weapons` = the class's families).
- The tree's A1-A4 slots become the line-2 picks, and the modifier nodes modify the Class Ability.
- Spellblade, Frostbinder, Stormcaller and Voidweaver get cheap, because vanilla rune building blocks cover them.
- SkyyProfiles must save the rune sections first (VERIFIED need, Hytale-Runes-Research 4.4).

**How it fits our systems:**
- **Class trees** (SkyyTrees 0.3, built but OFF): the Class Ability is free from class skill 1 - it is not a tree node. Each lane changes how it works.
  Example for the Priest: the Healer lane gives a bigger radius, the Guardian lane makes Mend also Ward, and the Smiter lane makes Mend hurt undead.
- **Mana:** Class Abilities cost 15-35 Mana. The Priest and Mage pools already grow per level (VERIFIED: +5 and +10). Physical classes need a small growth (question 5).
- **Party:** buffs use `party:fn:members` and a radius, like the Priest heal. Supports earn assist XP, and nearby members get kill credit
  (question 8 - a full round, because it touches loot).

## 7. Questions for Skyy (recommended default in brackets)

1. How should a Class Ability be cast before 0.7? [An off-hand class relic if the probe works, otherwise a hotbar class item; it moves to rune line 1 at 0.7]
2. One fixed Class Ability per class (RotMG), or pick 2 of 4 spells (the Wynn draft)? [One fixed ability; at 0.7 the 2nd rune line is the free pick, and the Wynn spells become tree picks]
3. Should Warrior be the tank (Warded + taunt) and Berserker the party damage buffer? [Yes]
4. Can new classes share a weapon family with an old class (RotMG has 3 classes per weapon)? [Yes, up to 3; old classes keep all their weapons]
5. How should physical classes get Mana? [+2 max Mana per class level for Archer, Warrior, Berserker and Assassin; Class Abilities cost 15-35 Mana]
6. Use the shared status list (2.3) with icons? [Yes]
7. Should bosses take half duration from Rooted / Stunned / Frozen, while debuffs always land? [Yes]
8. Pay supports: assist XP for buffs and debuffs, plus shared kill credit for party members nearby? [Yes - assist XP capped per minute, kill credit within 32 blocks; full round, because it touches loot]
9. A soft armor bonus for wearing your class's armor type, never a lock? [Yes, a small one - e.g. Mage + Magical Power in cloth, Warrior + Defence in metal]
10. More classes means more profiles (the profile limit follows the class list today, VERIFIED), and every profile is an island. [Cap the automatic profile limit at 8; ranks add more]
11. How do new classes unlock? [The base 7 stay open; new ones unlock at class skill 20 on two related classes, or with a quest item (your planned class-change item)]
12. Which classes go in wave 1? [Priest Mend, Berserker War Cry, Archer Pinning Shot, Tinker]
13. Ship Shaman early with vanilla totems? [Yes; its custom weapon comes later]
14. Use Hytale's elemental reactions (built into the engine, unused) as cross-class combos? [Later, once the 0.7 elements are live]
15. All class and ability names are placeholders. [Keep them until you rename them]
