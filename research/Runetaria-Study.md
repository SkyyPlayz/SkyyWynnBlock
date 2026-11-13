# Runetaria study (input for SkyWynn's own inventory screen)

Skyy 2026-11-12: "lets do our own version of that. but before we do, we need a full plan on how to work everything in right. lets start by studying there server more."
(Their words + the screenshot note: docs/answered/ui.md 2026-11-12.)

What goes here: what we learn about the Runetaria server (features, screens, how their inventory screen was made) - ideas and layout only,
never their art, text or code. The plan for our own screen comes after this study, in research/Inventory-Screen-Plan.md (not written yet).
Screenshots / videos Skyy sends of Runetaria: describe them here (date + what it shows); images stay out of git.

## 1. Their inventory-key screen (Skyy's screenshot, 2026-11-12)
- Top tab bar: Overview, Races, Professions, Classes, Party, Dungeons, Claims, Quest, Events, Collection, Settings, Help; currencies, trophy, mail, Servers, Store on the right.
- Overview: RTP + Homes buttons; character panel (gear: helmet / chest / gloves / legs, trinkets, a mount slot, 3 utility slots, "Choose a class"),
  Vitals (Health, Mana, Stamina, Defense), Attributes (Strength, Agility, Intellect, Vitality, Spirit), Show combat stats.
- Pocket Crafting: recipe icon grid with pages, a detail panel (inputs with have / need, Craft, 10x, Max).
- Inventory: backpack tabs, 9 x 4 grid, hotbar row, key hints (Take One, Shift Transfer, 1-9 To Hotbar, G Drop One, H Drop Stack, T Sort).
- Professions: total level, ~19 professions each 1 / 99.

## 1b. Character creation (Skyy's 2 screenshots, 2026-11-12)
- Full-screen "Create your character" scene: the player model stands in a lit shrine (a statue behind, a light beam), name plate under it
  (name + current class, "Adventurer" before a pick); game world blurred / dark behind; Later button top right (skip for now).
- Right column: server logo, CHOOSE YOUR CLASS - 4 crest icons (Warrior, Mage, Rogue, Priest); hover a crest to read, click to pick, "You can change class later".
- Picked class panel: name, one-line description, "Scales with <attribute>" (Rogue: Agility), WHAT YOU'LL DO = Weapons / Armour / Difficulty (3 dots + word),
  then the first ability with its icon, unlock level and one line (Rogue: Bleeding Slice, Level 2).
- The crest also shows on the player's chest in the scene; FINISH is greyed until a class is picked; note "Race choices are unavailable" (races are a later step).
- Lesson for us: one calm, readable picker with a live preview beats a list; SkyWynn has 8 classes + profiles (SkyyClasses / SkyyProfiles first-join flow).

## 2. Public information
(pending - research agent, 2026-11-12)

## 3. How the screen is made on Hytale 0.7
(pending - research agent, 2026-11-12)

## 4. Still to study
- Skyy's screenshots of every tab (Races, Professions, Classes, Party, Dungeons, Claims, Quest, Events, Collection, Settings, Help) and a short video of using the screen.
