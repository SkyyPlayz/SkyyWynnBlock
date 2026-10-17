# Armor + weapon set count: do we have 8 per tier per weight class?

*Survey 2026-10-17, read-only (nothing built, deployed or committed). Owner: Skyy (they/them).*

Skyy 2026-10-17: "between all of them do we have enough sets to do 8 per tier in each weight class? 4 normal drop sets, 2 UT, and 2
mythic sets per weight class. so 8 cloth, 8 light, and 8 heavy armor sets per tier?" + "and the weapons too".

**Short answer: NO.** Counting distinct looks (a recolour is NOT a new set) we have about 43 usable full sets for 192 slots
(3 weights x 8 tiers x 8): shortfall about 149. Counting every Armory colourway as a set, only 4 cells reach 8 (they are all the same few looks).
Weapons: enough in total for Warrior / Berserker / Mage, short for Priest, Monk, Assassin, Archer (section 5).

Method: `Assets.zip` (vanilla ids), every `Armor` item in the jars / zips of Skyy's Mods folder (python zipfile, read-only), tier from the
material word in the id, else the item level on our ladder (`tools/tier_tags.py`, `research/Pack-Armor-Plan.md` 2.1). Scratch json in
`tools/dev/scratch/armorcount/` (delete after reading). **Tier calls marked (?) are my guesses** - Skyy / the loot round should confirm them.

## 0. Ground rules used

- **8 tiers:** T1 Crude, T2 Copper, T3 Iron (Bronze shares it), T4 Thorium, T5 Cobalt, T6 Adamantite, T7 Mithril, T8 Onyxium (levels 1-49;
  Prisma / Wyrmscale / Lv 50+ pieces sit above T8 and are not counted).
- **A set = Head + Chest + Hands + Legs.** Partial sets are listed but NOT counted.
- **Looks, not colours:** a recolour (Armory has 8-25 colourways of one model) is the same look. Shown in brackets as `+n colourways`.
- Per Skyy's 2026-10-17 words the 8 per cell are picked FROM the pool: 4 normal drops + 2 UT (flag a set with trade-offs) + 2 Mythic (boss
  drops). So the pool needs 8 usable looks per cell. Today's UT sets (SkyyGear: Filing Cabinet = Heavy, Courier = Light, Intern = Cloth,
  one set per weight at L15) and Mythic (boss only, `docs/answered/gear.md` 2026-10-08/09) are not yet per tier. Note the older UT lock says "UT
  tiers = the 6 zone bands", not 8 ladder tiers: confirm whether T1 and T8 get UT at all.
- Sources marked **Maybe** are in `Pack-Armor-Plan.md` 1.1 as "Maybe" (dungeon / theme mods); counted in a separate column.

## 1. Table: full sets per weight class x tier (sure / + maybe)

| Weight | T1 Crude | T2 Copper | T3 Iron | T4 Thorium | T5 Cobalt | T6 Adamantite | T7 Mithril | T8 Onyxium | Sum |
|---|---|---|---|---|---|---|---|---|---|
| **Cloth** | 3 | 2 | 2 | 3 | 2 | 3 | 0 (+1) | 0 | 15 (+1) |
| **Light** | 1 | 2 | 3 | 1 | 2 | 0 | 0 | 0 | 9 |
| **Heavy** | 2 (+1) | 1 (+3) | 5 (+1) | 4 (+3) | 2 (+3) | 2 (+4) | 1 (+4) | 2 (+2) | 19 (+21) |

Counts are looks. Shortfall to 8 (sure only): **Cloth 49, Light 55, Heavy 45 = 149 of 192.** With all the Maybe mods: Cloth 48, Light 55,
Heavy 24 = 127.

### 1.1 Who is in each cell (name - source)

**Cloth**
| Tier | Full sets | Partial (not counted) |
|---|---|---|
| T1 | vanilla Wool (`Armor_Wool`), vanilla Cloth_Wool (?same look - check), SLVR Wool | |
| T2 | vanilla Linen, SLVR Linen | Armory Scarecrow (head only) |
| T3 | vanilla Cotton, SLVR Cotton | Armory Crowns, Amulets, Potion Bandolier (single pieces) |
| T4 | vanilla Silk, SLVR Silk, Arcane Power Manathread | |
| T5 | SLVR Raven, Armory Priest (+7 colourways) | |
| T6 | vanilla Cindercloth, SLVR Cindercloth, Arcane Power Arcaneweave | Armory Academy (Sellsword hat + Wizened chest / hands, no legs), Grand Lich (head + chest) |
| T7 | none sure. Maybe: MajorDungeons Cultist (L45, their dungeon) | |
| T8 | none | |

**Light**
| Tier | Full sets | Partial / Maybe |
|---|---|---|
| T1 | vanilla Leather Soft | Armory Tribal masks (heads), vanilla Kweebec (head + chest); Maybe TerrariaTools Cactus (?) |
| T2 | vanilla Leather Light, vanilla Trork Warrior (?) | Armory Jester (no hands, 18 chest x 36 legs colourways) |
| T3 | vanilla Leather Medium, Armory Warden (+2 colourways), StonedTurtle Ninja (+3 colours, not in PACK.md, licence unknown) | Armory Skull masks, Bramblekin (heads) |
| T4 | vanilla Leather Heavy (?) | |
| T5 | vanilla Leather Raven, Voidcloak Shadow (Epic L35) | |
| T6 | none | Armory Scorpion helms (heads only) |
| T7 / T8 | none | |

**Heavy**
| Tier | Full sets (sure) | Maybe |
|---|---|---|
| T1 | vanilla Wood, Armory Antique Dragon (1 colourway only) | TerrariaTools Wooden |
| T2 | vanilla Copper | PJ Glowing Copper, TerrariaTools Lead, + Bronze Ornate is 3-piece |
| T3 | vanilla Iron, vanilla Bronze, Armory Calvary (HorseKnight, +24 colourways), Armory Rook (+7), Armory Iron Dragon | PJ Glowing Iron. Armory "Vanilla Recolor Iron" = 20 colourways of vanilla Iron (not a new look) |
| T4 | vanilla Thorium, vanilla Steel (?), vanilla Steel Ancient (?), Armory Elite Rook (+7) | PJ Glowing Thorium, Hylamity Wulfrum (L25), Fullmetal Legion (L25) |
| T5 | vanilla Cobalt, Armory Cobalt Dragon (+1) | PJ Glowing Cobalt, TerrariaTools Crimson, Starblight Mammoth Iron (?) |
| T6 | vanilla Adamantite, Armory Daemon / Demon (+2) | PJ Glowing Adamantite, Marsi Statue (L40) |
| T7 | vanilla Mithril | PJ Glowing Mithril, MajorDungeons DarkSilver (+Charged), Fullmetal Legion Upgrade (L45), Marsi Dormant (L50) |
| T8 | vanilla Onyxium, Armory Rook/Knight L50 (1) | PJ Glowing Onyxium, PJ Prisma. Vanilla Prisma is above T8 |

Not counted anywhere: LOTR (Tolkien theme), Tritale (Zelda), Captain America, StarTale, UnstableRifts (own set bonuses), EndgameAndQoL /
Skyys-HyMax / TheLostWorlds (they OVERRIDE vanilla ids - never), Alicate MageRobes (overrides vanilla Cloth / Wool / Raven ids - never),
Starblight (asset pack for a plugin, overrides vanilla Adamantite / Cobalt / Onyxium / Steel / Silk / Raven ids; its own-id sets
GriffinHunter, Hierophant L50, Solar L45, Priest L35, Rooted Wooden L40 would need the plugin), the Armory's 9 Kanohi props.
Our own: SkyyGear gathering sets (Farming / Foraging / Fishing, 5-7 tiers each) are gathering gear, not combat weights, so not counted;
SkyyArmory has no armor.

### 1.2 If every colourway counts as its own set (not recommended)

| Cell | Count with colourways | Reaches 8? |
|---|---|---|
| Heavy T3 | 5 looks, about 50+ sets (Calvary 25, Iron recolours 20, Rook 8) | yes |
| Heavy T4 | Thorium + Steel + Ancient Steel + Elite Rook 8 = about 11 | yes |
| Cloth T5 | SLVR Raven + Priest 8 = 9 | yes |
| Light T3 | Medium + Warden 3 + Ninja 4 = 8 | borderline |
| Every other cell | under 8 | no |

So colourways help only the Iron / Thorium band, which is exactly where the Armory is already thick.

## 2. Per cell: enough for 8? (shortfall = 8 - sure looks)

| Weight | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | Total |
|---|---|---|---|---|---|---|---|---|---|
| Cloth | 5 | 6 | 6 | 5 | 6 | 5 | 8 | 8 | **49** |
| Light | 7 | 6 | 5 | 7 | 6 | 8 | 8 | 8 | **55** |
| Heavy | 6 | 7 | 3 | 4 | 6 | 6 | 7 | 6 | **45** |

No cell reaches 8 on looks. Closest: Heavy T3 (5 looks). Worst: Light T6 / T7 / T8, Cloth T7 / T8 (nothing at all).
Check on the 3-way split itself: 4 normal + 2 UT + 2 Mythic at T1 means two Mythic boss sets at Crude level - Skyy may want fewer there
(section 4, suggestion S6).

## 3. Licences (what we may do with each source)

Checked with `tools/mod_check.py` (CurseForge page licence; slug guesses can hit the wrong page, so "unverified" = confirm on the page).

| Source | Licence | What we may do |
|---|---|---|
| Vanilla Hytale (Assets.zip) | game files | read only; generated into jars at build time, never committed; our own new ids may reuse vanilla models / textures |
| The Armory 1.23.0 (LadyPaladra) | CC BY-NC 3.0 (CurseForge FAQ, matches PACK.md) | modpack use OK with CREDIT, never sold; runtime ids only; changing stats / recipes is allowed but our public-repo rule still bars copying their files or textures; Mods folder has 1.23.0 (PACK.md row still says 1.22.0) |
| SLVR Arcane Robes & Spells 1.2.0 (SlverSkull) | slug `slvr-arcane-robes-spells` returned HTTP 404; no licence field in its manifest: treat as All Rights Reserved | runtime ids only AFTER the author OKs listing it; ask SlverSkull. Manifest says server ^0.5.4 and no dependencies (items / armor load without Patchly; Patchly is only for its 9 `.patch` mob-drop files) |
| Arcane Power 3.2.1 (Tayko) | tool printed All Rights Reserved (slug unverified) | already "pending Tayko's permission" (`docs/answered/gear.md` 2026-10-09); server >=0.7.0 <0.8.0 so it fits 0.7.2 |
| Voidcloak Armory 1.1.0 (Vortex) | tool printed All Rights Reserved (slug unverified) | ask first; only 1 armor set |
| PJ-HyperGlowingArmors, TerrariaTools, MajorDungeons, Marsi, Fullmetal, Hylamity, StonedTurtle Ninja | not checked | run `mod_check.py` before listing any; "Maybe" only |
| **Patchly 3.6.2** (Riprod) | MIT (page) | MIT allows bundling, but we only list it; in Skyy's Mods folder, not in PACK.md (add a row if SLVR is packed); manifest `server >=0.6.0 <0.8.0` = compatible with 0.7.2; the Armory jar bundles its own Patchly copy per the earlier plan, so check for a double install |

Rules that stay (PROJECT-RULES 2): pack mods are reacted to by id at runtime only; no overriding their ids; never copy their
recipes / numbers / models / textures; ask the author if their data needs editing.

## 4. Ideas to fill the gaps (SUGGESTIONS only - Skyy decides)

- **S1. Recolours we generate from VANILLA sets** (hue-shifted Wool / Linen / Cotton / Silk / Cindercloth, leathers, metals) at build time into
  our jars: each vanilla set gives 2-3 more looks per tier with our own ids. Needs art checks and our own new ids (never the Armory textures:
  its licence is NC and we do not ship their files).
- **S2. UT and Mythic reuse a normal set's LOOK** with different stats (UT = trade-off, Mythic = set bonus, boss-only): then each cell needs
  only 4 distinct looks, not 8, and today's gap drops from 149 to about 54 (4 looks per cell). Cheapest fix. Our own ids pointing at vanilla models only.
- **S3. Mixing pieces:** hands / legs from one set with head / chest of another (Armory Jester, Academy, Grand Lich, Scorpion helms,
  Crowns are all incomplete) - fills T1-T3 Light and T6 Cloth partly, but gives odd-looking sets; use only as UT oddities.
- **S4. Fewer sets at the extremes:** 4 + 2 + 2 at T1 / T2 is overkill (nobody wears Crude armor for long): suggest 4 normal + 1 UT at T1-T2
  and the full 4 + 2 + 2 from T3 up, or 4 + 2 + 2 only where the pool exists. Cuts the target from 192 to about 150.
- **S5. Our own Light / Cloth ladder for T6-T8** (the black-leather Light ladder and Crude Robe already planned in `Pack-Armor-Plan.md`
  section 5 question 8): the real hole is Light T6-T8 and Cloth T7-T8 (nothing exists), about 8 sets we must design.
- **S6. Add "Maybe" mods** after licence checks: PJ Glowing Armors (a glowing set for every heavy tier T2-T8), Fullmetal Legion (T4, T7),
  Marsi / MajorDungeons (T6-T7). These alone cut Heavy's shortfall from 45 to about 24. Dungeon mods may be better left as their own dungeon loot.
- **S7. Ask authors:** SlverSkull and Tayko for permission (3 + 2 + 1 cloth sets depend on it - without them Cloth falls to 9 sets); LadyPaladra
  for an extra Light / Cloth set at Lv 40+.

## 5. Weapons (second table)

Sources: vanilla `Assets.zip`; ours (`SkyyArmory.jar`, 69 weapon items: Bo, Fist Gauntlets / Wraps, Great Shield, Kunai, Spellbook,
Staff, Wand, Soul Cage / Soul Orb wands, 3 UT weapons: Turnstile, Loophole, Second Opinion); The Armory (recolours + specials);
SLVR (5 spellbooks L30-60, 5 spell scrolls, a mana totem; no melee); other pack mods. Class weapon list from `research/classes/README.md`:
Warrior sword / longsword + spear (shield off-hand), Archer shortbow + crossbow, Mage staff + spellbook, Priest wand + soul orb, Berserker
axe / battleaxe + mace / club (flail), Monk bo + fist, Assassin daggers + kunai (Spellblade: two-handed swords, in design).

### 5.1 Distinct weapons per tier per type (core: vanilla + ours; one metal weapon per tier unless noted)

| Type | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | Specials (not on the ladder; vanilla / Armory / pack) |
|---|---|---|---|---|---|---|---|---|---|
| Sword | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 13 vanilla, 2 Armory (Zweihander, Ghost) |
| Longsword | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 10 vanilla, 4 Armory Elemental |
| Spear | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 8 vanilla |
| Shield | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 8 vanilla; ours Great Shield x7 (T2-T8); Armory 85 colourways |
| Shortbow | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 10 vanilla (6 are UT / Mythic candidates), 6 Aegos, 2 Arcane Power |
| Crossbow | 0 | 1 (ours Wynn) | 1 | 0 | 0 | 1* | 1* | 2* | *Crossbow Tiers pack; Voidcloak 1; MajorDungeons 3 |
| Staff | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 18 vanilla, 15 Hexcode, 6 TerrariaAddons, 6 Starblight |
| Spellbook | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 6 vanilla, 9 Arcane Power, 5 SLVR (T5 L30, T6 L40, T7 L45, T8 L50, one above), 5 Hexcode |
| Wand | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 4 vanilla, ours UT 1 |
| Soul orb | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | (ours only) |
| Axe | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 5 vanilla |
| Battleaxe | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 7 vanilla, Armory Hepta + Rune Blade |
| Mace | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 vanilla, 3 Arcane Power, Armory Lahat |
| Club / flail | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 15 vanilla (mostly zombie limbs), 2 Armory flails |
| Dagger | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 8 vanilla, Armory Dual Rune Blade, 6 Wans |
| Kunai | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 vanilla |
| Bo staff | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | ours UT Turnstile |
| Fist | 0 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 Armory Fist, 1 vanilla claws, 1 MG Aspectro |

The Armory adds colourway weapons only at T3-T6: Sword 11 / 10 / 11 / 10, Longsword 10 (T3) + 10 (T5), Dagger 10 / 7+3 / 10 / 10, Mace
11 / 10 / 10, Battleaxe 10 each, Shield 27 / 24 / 18 / 16. They are recolours of 6 models; fine as variety, they do not fill T1-T2 or T7-T8.

### 5.2 Per class: does 4 normal + 2 UT + 2 Mythic per tier work?

Need per class: 8 tiers x 8 = 64 weapons (split over its 2 types: 4 per type per tier). Distinct weapons now (ladder + specials + Armory
specials + eligible pack mods, no recolours; tier of specials is still to be assigned):

| Class | Ladder weapons | Specials pool | Total about | vs 64 | Per-tier problem |
|---|---|---|---|---|---|
| Warrior (sword, longsword, spear) | 28 | about 31 vanilla + 6 Armory + about 25 pack | 90 | enough in total | T1-T2 and T7-T8 have only the 3 metal weapons; specials must be levelled into them |
| Berserker (axe, battleaxe, mace, club) | 32 | about 30 + 7 Armory + 6 Arcane Power | 75 | enough in total | same: thin at the ends |
| Mage (staff, spellbook) | 17 | 24 vanilla + about 45 pack (Hexcode, Arcane Power, SLVR, TerrariaAddons) | 85 | enough (needs the packs' permission) | ours is 1 per tier; the rest is licence-dependent |
| Archer (shortbow, crossbow) | 11 | 10 vanilla + about 12 pack (Aegos, Arcane Power, Voidcloak, MajorDungeons) | 33 | **short about 31** | crossbow empty at T1, T4, T5 |
| Assassin (daggers, kunai) | 17 | 8 vanilla + 1 Armory + about 10 pack (Wans, EEM) | 36 | **short about 28** (recolours would fill T3-T6 only) | everything at T1-T2, T7-T8 |
| Priest (wand, soul orb) | 16 | 4 vanilla + about 2 pack | 22 | **short about 42** | the thinnest class |
| Monk (bo, fist) | 21 | 3 vanilla + 3 | 27 | **short about 37** | both types ours only |

Weapon total shortfall about 138 if every class must reach 64; about 100 if Mythic is 1 per tier per class (suggestion W3).

### 5.3 Weapon suggestions (SUGGESTIONS only)

- **W1.** For weapons "8 per tier" is better per CLASS than per type (two types, so 4 per type); proposal: 4 normal (2 per type: the
  metal weapon plus one recolour or special), 2 UT, 2 Mythic per class per tier, UT and Mythic taken from the specials pools above.
- **W2.** Specials in vanilla and the packs mostly carry no tier: assign each one a tier (`level.item` rows) and they cover the ladder ends.
- **W3.** Mythic is boss-only: 1 Mythic per class per tier from T3 up (not 2, not at T1-T2) is more realistic for Priest, Monk, Assassin.
- **W4.** Priest, Monk, Assassin and Archer need our own specials (the `Pack-Armor-Plan.md` 3.3 fairness plan already says 3-4 each); the table above is
  the argument: write them first.
- **W5.** Armory recolours as the "normal" drops of Warrior / Berserker / Assassin at T3-T6 (10 each), as already planned.

## 6. What this changes for the loot round

- Drop tables must weight by SET (look), as in `Pack-Armor-Plan.md` 2.3; with so few looks at T6-T8 the first drop table should be built for
  T1-T6 and leave T7-T8 to vanilla Mithril / Onyxium + bosses until our own sets exist.
- Ask before building: SlverSkull / Tayko / Vortex permission, Starblight status (unknown plugin), and whether UT tiers are the 6 zone
  bands or all 8 ladder tiers.

## More mods survey (2026-10-17)

Skyy 2026-10-17: "we could also check for more armor mods before we build our own." Survey of CurseForge (Hytale) by search + page reads
(`tools/mod_check.py` for licences; Mods folder listed read-only). Not counted above: everything below. Page text rarely says whether a mod
overrides vanilla ids or what the sets look like - those cells are "unknown, check the jar" and must be scanned (`mod_check.py - <word>`) before any pack decision.
Hytale-version info on most pages is only "Early Access" (stale "Updated 8 months ago" labels are unreliable); 0.7.2 fit is UNVERIFIED for all.

### A. Armor candidates

| Mod (author) | Licence | Full sets / look / tier guess | Overrides vanilla? | In Mods folder? | Verdict |
|---|---|---|---|---|---|
| Fantastic Knight Armor Pack (Fyrrage), upd 2026-09-03 | ARR | 7 sets: Frostbite Warden (Cobalt), Dune Walker (Thorium, fabric + metal = Light/Cloth?), Scorched Heart (Adamantite, Heavy), Neptune's Elite (Thorium, Heavy?), Crystalwood (Thorium, Light?), Soul Cage (above Adamantite, Heavy), Fen Stalker (Thorium, Light). Loot-only (not craftable) = fits our drop idea | unknown | no | BEST armor find. Ask Fyrrage; runtime ids only |
| Outlanders Armor Pack (Fyrrage), v1.3, upd 2026-08-31 | ARR | 6 sets: T2 Berserker (Heavy), Hunter (Light), Priest (Cloth); T3 Marauder (Heavy), Stalker (Light), Sorcerer (Cloth); "alternative to Cobalt" = about T5. Exactly 2 per weight | unknown | no | Ask Fyrrage together with the pack above; fills Light + Cloth at T5 |
| Elemental Knights Pack, v2.0.1 upd 2026-10-09 | ARR | 4 Heavy sets (Frost / Poison / Fire / Electric Knight, Adamantite ~T6) + 4 shields + battleaxe, mace, sword, Knight Bow, daggers | unknown (has an id Migrator plugin = ids changed once) | no | Ask; Heavy T6 + weapons for Archer / Assassin |
| Void Armor & Weapons (Aipoc76), 2.5.6 upd 2026-10-13 | CC BY-NC 3.0 | 5 Heavy-ish sets (Copper, Iron, Thorium, Adamantite, Mithril = T2, T3, T4, T6, T7), 4 shields, Mithril sword / longsword / shortbow / daggers / hammer. Void-corruption look | not stated | no | Same licence class as the Armory = credit, never sold, runtime ids only. Only candidate allowed without asking. Heavy T7 + dagger / bow |
| Yorch's Armory (armor-weapon-variations), game 0.6, upd 2026-09-03 | ARR | 6 variants (Silver, Golden, Druid, Wolf, Runic Gunslinger, Void) + Silver Sword + iron / copper / cobalt weapon variations | unknown | no | Look at the gallery; Druid / Wolf could be Light or Cloth. Ask |
| Wolf Armor Sets (DarkWolf_XP) | ARR | 2 sets (black / white), Copper-made = T2 Light | no | no | T2 only; low value |
| Blood Armor (stonedturtle) | ARR | 1 set, Adamantite, late-game look (T6 Heavy) | unknown | no | Maybe |
| Magical Armor Set (stonedturtle) | ARR | 1 set, Prisma-look (Cloth/magic?) | unknown | no | Maybe (Cloth high tier) |
| Darth Vader Armor Set, Georgian Armor Sets | ARR | 1 set / unknown | - | no | skip (theme clash / tiny) |
| Leather Armor (Parcyval) | ARR | 3 sets light / medium / heavy leather (T1-T3) | probably touches vanilla | no | Duplicate of vanilla leathers: skip |
| Improved Crafting (andzejsw) | ARR | "18 new armor sets, 91 weapons" = recipes for items already in the game but creative-only | vanilla ids | no | Never usable (no id overrides); see vanilla pool |
| Fred's Uncraftable Armor's + (FredMCGamer) | ARR | about 20 existing vanilla armor sets made obtainable (names not on the page) | vanilla ids | no | Not packable; its list is a free vanilla pool |
| Forge Plus Armory | MIT | "all vanilla items not yet craftable" (forge + recipes) | vanilla ids | no | MIT: we may read it to learn which vanilla ids are unused |
| Cosmetic Pack: Modular Armor / ZC Armor Variants | CC 4.0 | cosmetics only (Cobalt-Onyxium retextures needing Lalyan Cosmetic Core / 4 iron helmet + 2 chestplate variants) | - | no | Not item sets; skip |
| Cerion's Tiered Weapons and Armor, Vanilla+ Armors, HyARPG | ARR / ARR / custom | outdated / unread / unread | - | no | skip for now |

**Vanilla pool (no mod needed):** Assets.zip already has armor sets with no recipe or a creative-only recipe (Fred's lists about 20; Improved
Crafting 18). Our drop table can hand out those vanilla ids directly, with no licence at all. Next job: list every `Armor_*` id in Assets.zip
that is in no recipe and not in the section 1 counts, and sort them into the weight / tier grid. This may cover much of the shortfall below.

### B. Weapon candidates (Archer, Assassin, Priest, Monk first)

| Mod | Licence | What | For | Verdict |
|---|---|---|---|---|
| Lost Weapons | slug not found (404), unverified | 5 weapons: Templar Knight longsword, Azure Sorcerer staff, Night Ranger bow / daggers, Undead Viscomancer mace, Arcane Striker fist | Archer, Assassin, Monk, Mage | find the real slug, check licence |
| Better Daggers New | ARR | colour-themed high-speed dual daggers with pounce + angle attacks; colours in a tier share stats | Assassin | ask; recolours by design |
| UniqueBows | ARR (unchecked) | 4 hidden vanilla bows made craftable (bomb arrow, pull, rapid fire) | Archer | vanilla ids = a free pool (UT / Mythic bows) |
| More & Better Crossbows | ARR (unchecked) | copper to Onyxium crossbows | Archer | duplicate of Crossbow Tiers (already installed): keep ONE |
| Shinku's Powerful Weapons, FL's Exotic Weaponry (Wakizashi, Rifted Crimson, Radiant Fists, Radiant Greatblade, Crimson Reaper), Triggerblades | not read | single weapons per type | Assassin, Archer, Monk | small; Radiant Fists = a Monk Mythic candidate |
| Elemental Knights, Void Armor | see A | bow, daggers, sword, battleaxe, mace, hammer | Archer, Assassin | with A |
| Already in Skyy's Mods folder but missing from section 5: Zet's Mystic Weapons 1.2.2 (12 items: Vampiric Daggers, Whirlwinds, Impressio, Dreadreap, Dominus Maul, Aetherflux Blade, Noctivagus, Absolution; manifest server <0.6.0), Reforged Weapons 4.4 (2 daggers, mace, staff, Oath), Void Asylum (Repulsion Bow, Gravity Staff, Abyssal Helix Spear), Steamwrought Tomb (Piston Lance), ShamanTotem (3 totems), Necromancer Spire (Necrotic Blade) | check each | Assassin +3, Archer +1, Mage +3, Warrior +3 | add to the weapons pool; verify the old-server ones on 0.7.2 |

Priest (wand / soul orb) and Monk (bo / fist): no mod found adds wands, soul orbs or bo staves. Those stay ours.

### C. Duplicate / clash notes (PROJECT-RULES 2: keep the BEST, not all)

- Fantastic Knight "Soul Cage" armor vs our SkyyArmory Soul Cage wand: same name, different item - pick one name in the lang.
- Void Armor shields vs Armory shield colourways vs vanilla shields: keep the Armory (already counted); leave Void shields out.
- More & Better Crossbows vs Crossbow Tiers (installed): one only.
- Set bonuses in Void Armor / Elemental Knights overlap our own set-bonus system: use pieces, not their bonuses (check code count in the jar).
- Improved Crafting / Forge Plus / Fred's all unlock the same vanilla items: use none, read the list.

### D. Updated shortfall (Skyy's rules)

Rules applied: 5 zones x 3 weights; per cell "several" normal drop sets (assume 4 distinct looks) + 1 Mythic that is a distinct, coolest look; UT may be recolours
of normal sets, so UT needs no new look. Distinct looks needed = 5 x 3 x (4 + 1) = **75** (25 per weight), versus 192 under the old 8-per-tier ask.
Section 1 has 43 sure looks (Cloth 15, Light 9, Heavy 19), but they sit at tiers not zones, and Light T6-T8 / Cloth T7-T8 are empty:

| Weight | Needed | Have (sec 1) | Short today | Licence-free now (Void Armor) | If Fyrrage + Elemental + stonedturtle + Yorch all agree | Left to design ourselves |
|---|---|---|---|---|---|---|
| Cloth | 25 | 15 | 10 | 0 | +2 Outlanders, +2 Fantastic (guess), +1 Magical, +1 Yorch = about 6 | about 4 |
| Light | 25 | 9 | 16 | 0 | +2 Outlanders, +2 Fantastic, +2 Wolf (T2), +1 Yorch = about 7 | about 9 |
| Heavy | 25 | 19 | 6 | +2-3 (Void, those not duplicating a vanilla look) | +2 Outlanders, +3 Fantastic, +4 Elemental, +1 Blood = about 10 | about 0 |
| **Total** | 75 | 43 | **32** | about 3 | about 23 | **about 13** |

Shortfall: 149 (old ask) / 32 (new rules) -> **about 29 with licence-free sources only, about 13 if the authors agree**. The 13 are almost all
zone 4-5 Light and Cloth (Mythic slots; nothing exists above Adamantite there). Tier calls are from names only: re-count after reading the jars.
The vanilla pool (section A) is not counted here and may shrink the 13 further.
Per-zone caution: Fantastic Knight, Outlanders and Elemental Knights cluster at Cobalt / Adamantite (zones 3-4); zone 5 Light and Cloth Mythic needs our own designs
(Pack-Armor-Plan section 5). Void Armor Mithril (Heavy) is the only candidate at the top.
Weapons after this survey (rough): Assassin short about 28 -> about 13; Archer about 31 -> about 20; Monk about 37 -> about 33; Priest unchanged about 42. Under the new
rule (Mythic per zone, UT recolours) the target per class is about 5 zones x 2 types x (4 + 1) = 50, so these gaps shrink further.

### E. Asks to send (via Skyy)

1. **Fyrrage** (Fantastic Knight + Outlanders): runtime-id use, 13 sets, drop tables only, credit in PACK.md.
2. **Elemental Knights author**: 4 Heavy sets + weapons.
3. **stonedturtle** (Ninja, Blood, Magical): one message for all three (the Ninja licence is still unverified in section 3).
4. Yorch / Better Daggers / Lost Weapons: after Skyy sees the galleries.
Licence-free now: Void Armor (credit, never sold) and the vanilla pool. No downloads were needed, so scratch `tools/dev/scratch/armorsurvey/` was never created.
