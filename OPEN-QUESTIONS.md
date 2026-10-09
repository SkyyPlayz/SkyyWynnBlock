# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `docs/archive/DESIGN-STATUS.md` "Open questions".

**ONLY OPEN QUESTIONS LIVE HERE (Skyy, 2026-10-05).** When Skyy answers one, the answer goes word for word into
`docs/answered/<topic>.md` (its "New answers" block) and the question is DELETED from this file - one command does both:
`python tools/qa_append.py <topic> <file with the answer lines> --close "<words from the question>"`. Every answer ever given (word for word,
by topic): [docs/answered/README.md](docs/answered/README.md). Format: one `- ` line per question under its topic, today's default in [brackets].

## Still open (newest at the bottom of each topic)

### project
- allow a SMOKE-TEST SERVER before each deploy (habit 6 'prove it'): start HytaleServer.jar offline on a COPY of the test world in tools/dev/scratch/, check every '[Skyy...] ready' line + errors, stop it - never the real game / world / saves? Today's rule says never start the game. [recommended yes - docs/log/2026-10.md 2026-10-06]

### world

### mobs

### skills
- which of your live Server Setup test values become the pack defaults - Cooking XP multiplier, early gathering XP boost, the
  XP-per-level list, the Copper level band? [today's pack defaults until you say]
- OPEN 2026-10-02 (SkyySkills 0.4.12 review): everyone has 10 base Mana, so Warriors / Archers also get the in-combat Mana refill. Limit it to classes that use Mana (Mage, Priest)? [everyone - harmless today]
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

### gear
- ONYXIUM CROSSBOW recipe (SkyyArmory 0.1.3): today 10 Mithril bars + 2 Voidheart + 3 Storm leather at the tier-3 Weapon Bench (Onyxium bars have no world source in 0.6) - keep it, use Onyxium bars like the Onyxium wand, or make it an upgrade of the Mithril crossbow? [keep the current recipe]
- BOW LEAP on the 6 prototype / developer bows (Combat, Bomb, Pull, Ricochet, Vampire, Test_Zoom - own fire chains, still vanilla): give them the leap too? [no - only the 13 normal shortbows]

- SIGNATURES for the new weapons (research/cloud/Signature-Proposals.md, wands already = ricochet bolt): Bo staff [B Whirling Staff - a timed multi-hit spin]; wraps / gauntlets (+ claws later) [A Flurry - 6 fast jabs]; kunai [A Kunai Fan - 5 kunai in a fan]; spellbooks [A Page Storm - 2 s page swirl around you]; daggers keep vanilla Razorstrike [yes]

- PACK ARMOR (research/Pack-Armor-Plan.md section "Questions for Skyy"): TURN ON The Armory in the world (installed but switched off today) [yes, via deploy_set PACK_THIRD_PARTY]; mods in the pool [The Armory + SLVR Robes + Arcane Power + Voidcloak; no IP-themed mods; dungeon mods keep their own armor]; their crafting [keep for now - changing their recipes needs an override file = a PROJECT-RULES exception for CC BY-NC mods]; money [no paid access to Armory items, ask LadyPaladra first]; drop rate [the locked 4% extra roll, armor half of it, picked by set; special sets 1 in 50 per boss kill]; first special sets [5: Calvary, Warden, Priest, Cobalt Dragon, Academy, 2- and 4-piece bonuses]; colour [random]; crowns / amulets / bandoliers = Cloth [yes]; our own armor [keep Heavy Leather, Crude Robe, the Light metal ladder; pause Dark Leather + mining / foraging armor art]; Lv 40-49 Light / Cloth gap [our Light ladder + vanilla Silk / Cindercloth]; multiplicative-stat pieces [special sets only]; Lahat Chereb [Berserker (mace moveset)]; The Armory "Fist" [Monk boss drop, check in game]

- LOOK SWAPS (research/Recolor-Plan.md): use The Armory's Alteration Table now - our own items join it with our own files, no override of theirs [yes]; our own Wardrobe station only if The Armory breaks on 0.7 or you want swaps from the menu / for coins [later]; get a tree look = craft the key-log set, then swap within the tier [yes]; farming = one design per crop [yes]; vanilla metal mining sets: 8 colours each, metal keeps its tier colour [8]; The Armory's 20 Iron colours = the miner's Iron looks [yes]; combat Armory looks on mining sets [no - different stats]; swap cost = The Armory's Alteration Kit (3 swaps) [yes]; recolour other pack mods' armor ourselves [no - only their own variants]. (Per-tree designs stay HAND-MADE by Quirk, as you asked.)


- OWN SPECIALS (research/cloud/Own-Specials-Draft.md, 21 boss-drop weapons, every class ends at 4): keep all names + hooks [keep]; Monk 4 (not 3) [4]; The Counterclaim parry shield Warrior-only [yes]; drops 5% from their boss with x3 own-class lean, slayer bosses via the RNG meter [yes]; Legendary rarity + modifiers roll, drop as a Mystery Bag [yes]; office-humour names [keep]

- UNTIERED / MYTHIC / SET (research/cloud/Untiered-Mythic-Spec.md section 7, 18 questions): UT tiers = the 6 zone bands (14 weapon types + 3 armor sets each, 156 eventually) [yes]; UTs tradable [yes]; UTs drop identified, orange name, no bag [yes]; level-up caps Mythic +2 / Untiered +3 / others +6 [yes]; first UT batch U1-U10 [keep]; Mythic boss-only (out of random drops + Smithing step-up) [yes]; Mythic 10% per kill (20% Challenge), each participant rolls, own-class lean x3 [yes]; sample boss pools [approve]; Mythic sets: bonus only at the full set [yes]; capstone uniforms become MYTHIC 4-piece sets split across floors [yes]; Set pieces tradable [yes]; gathering set bonus table [as tabled]; boss respawn = "Appeals Desk", boss level x 25 coins (x2 Challenge), 60 s cooldown [coins]; every participant with 15% credit rolls [yes]; desk + pools in SkyyMobs [yes]; world drops list [yes]; names Appeals Desk / Formal Complaint (challenge) / Untiered [keep]

### economy
- Bazaar CLOTH and GEM prices [x2 per tier step, like metals / woods / crops - built into SkyyBazaar 0.1.4: cloth scraps 4 / 16 / 40 / 96 / 256 / 640, Diamond + Voidstone 120]
- which late-game items can never be bought or sold (the market wall)? [list empty until you name items]

### bags
- OPEN 2026-10-02 (from the SkyySacks 0.7.11 review): carried bags of one type now add up with NO limit, so e.g. 54 Normal bags hold more than a Legendary. Keep unlimited (each extra bag costs a slot and a recipe), or a Server Setup cap on bags counted per type (e.g. 3)? [unlimited]
- OPEN 2026-10-02 (same review): an idle partial stack only tops up once you use it. Also top up the stack in your selected hotbar slot even when idle? [only when used]
- the ACCESSORY TABLE (its own crafting table for accessories + bags, LOCKED 2026-10-02) - still wanted now that the Pocket
  Dimension keeps the Workbench tab? [spec paused until you say]

### classes
- CLASS TREES (SkyyTrees 0.3.3, live 2026-10-08): the 13 open choices of research/cloud/Class-Tree-Build-Map.md all use its recommended
  default (page 2 replaced, paths from T1, first owned node locks, whole-tree respec, refund + 1 free respec, flat points, Monk Calm
  Breath waits, capstones retired, same respec price for Monk/Assassin) - change any? [as built]
- CLASS TREES builder choices to confirm: Open Aura hangs off Root (buyable now); Mage Long Blink +2/+3/+4/+5 (21 blocks max); Radiant
  Trail heals you + party only (no Divinity XP); Blink Strike also after a targeted Shadow Step; Long Reach = kunai teleport range only. [as built]
- MONK class skill name: Discipline, Zen, Kenpo, Harmony or Focus? (a small 3-mod rebuild to change) [Discipline]
- the missing ability picks - every class's A2 alternative and its two improved A1 options (the Priest's A2 alternative too).
  The class-ability spec PROPOSES them after the reset, then you pick. [proposals pending; research/classes/<Class>.md]
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]


- ABILITY KEYS follow-up (your 2026-10-08 decision: 2 primary on Ability 2 / 3, 2 alt on crouch + Ability 2 / 3): in MID-AIR a key casts the primary [yes - crouch in the air stays the double jump / Monk air jump / plunge]; hotbar ability items still wanted as a backup way to cast [no for now - keys only]; swap which 2 are primary out of combat only, in the class / tree page [yes]

- CLASS ABILITY SHAPES (research/cloud/Class-Ability-Shapes.md section "Questions for Skyy", 10 questions): sprint shapes may step you ~2 blocks [yes]; costs / cooldowns per shape (most the same, bigger shapes +2-4 Mana / +2 s) [yes]; a mid-roll cast uses the sprinting shape [yes]; Priest Guardian Spirit stays passive first (press / crouch versions later) [yes]; HUD Abilities widget shows 2 rows that switch to the alts while you crouch [yes]; you can swap which key each primary sits on [yes]; with only 3 abilities owned = 2 primary + 1 alt [yes]; toggles (Blood Frenzy) only change how they turn on [yes]; build order Mage + Priest, Monk + Assassin, Warrior + Berserker, Archer last [yes]

- ARCBLADE (research/classes/Arcblade.md "Questions for Skyy", 15): class skill name [Battlemagic]; Momentum 0-20 stacks, rhythm window, decay [yes]; what stacks change + Rolling (7) / Unstoppable (14) [yes]; what breaks Momentum [yes]; Breach next to the Archer Mark: higher + 5% [yes]; kit A1 Arcane Breach / A2 Elemental Imbue / A2-alt Sunder / A1-alt Rift Cleave (first) or Shattering Arc [keep]; elements = the engine five (Fire, Water, Earth, Wind, Lightning), Poison a status, Gravity sword = Earth [yes]; Echo on Sunder + A1-alts [yes]; great shield guard + Bulwark Charge [yes]; traversal costs [yes]; signatures Meridian Cut / Iron Curtain [yes]; medium stats, Light armor [yes]; paths Tempest / Breaker / Vanguard [yes]; Warrior gives up longswords + Zweihander [yes]; build order after the ability engine [yes]

### pets
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]

- PET ROSTER (research/Pets-Roster.md, 111 pet families, Kweebec + Trork already no): other humanoid races as pets (Goblin, Ogre, Feran, Outlander, Slothian, Saurian, Tuluk, Klops, Bramblekin, Elf, Void Necromancer) [no]; pets at launch [about 30, the rest in zone batches]; look variants (Frost / Sand Skeleton, bird kinds, fish kinds) = skins of one pet [skins]; families with a vanilla baby start as the baby [baby until pet Lv 30, then the shrunk adult]; hostile pets use their own vanilla attack [yes, damage as % of your weapon]; a mount pet in slot 1 shows at pet size [yes]; water pets follow only while you swim [yes, buff-only on land]; creatures drop their own egg [yes, 0.1% / elites 1%]; boss creatures as pets [no for now]; Grooble yes, Bee swarm no [yes]

### social
- how a player raises the profile cap above 6 (likely ranks). [parked - no way above 6 yet]
