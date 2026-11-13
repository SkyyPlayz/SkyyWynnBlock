# Runetaria study (input for SkyWynn's own inventory screen)

Spelling: the server is **Runeteria** (runeteria.com, play.runeteria.com, discord.gg/runeteria); this file keeps the name Skyy first typed.

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

## 1c. Their HUD right after the class pick (Skyy's screenshot, 2026-11-12)
- Top left: round portrait frame (player head, level badge 1) + name + a class icon.
- Top centre: compass bar with icons; under it the objective with an arrow and distance ("40m - Go down the cave stairs and speak to Warden Aldous"),
  then a title banner "You are a Rogue" with a small line above ("Your path begins. Warden Aldous waits below.").
- Right: quest tracker (quest name + checkbox objective). Top right: currencies, mail, server name (NA01-HUB), online count, clock; Social + Discord link.
- Left edge: a narrow column of numbered chat / channel buttons.
- Bottom: ability bar above the hotbar - a big round ultimate (Lv 10, Q) and three smaller ability slots locked with their unlock level + key
  (Lv 2 E, Lv 5 R, Lv 8 H); an "Attribute point available" prompt; two quick slots (weapon / consumable); Health 105/105 left and Mana 100/100
  right as long bars meeting at a centre ornament; hotbar 1-9 plus a separate Z utility slot; a full-width class XP bar at the very bottom
  ("Level 1 Rogue 0 / 156 XP 0%").
- Onboarding: class pick leads straight into a guided first quest with an in-world waypoint (statue + NPC below).
- Lessons for us: locked abilities show their unlock level + key on the bar (teaches progression at a glance); one bottom XP bar for the class;
  objective + distance under the compass. Compare with SkyyHud (minimap, skills widget, quest tracker) before copying any idea.

## 2. Public information (web research, 2026-11-12; public info is thin)
- "Hytale Vanilla+ RPG SMP", custom coded, no client mod (content sent on connect). Launched 2026-01-17, run by an unnamed team; NA + EU realms;
  ~120 online, peak 159 (hytale.game, hytaletopservers.net: game 0.7.7). Hypixel's Simon praised it publicly on X.
- Site sections: Rules, Wiki, Dungeons, Guilds, Leaderboards, Market, Store, Tickets, Discord linking (runeteria.com).
- News: 2026-11-01 "Changelog: Professions, Classes, Events, Tutorial Isle and more" (biggest update: classes + abilities, professions overhaul,
  Halloween events, reworked new-player start = the Tutorial Isle / Statue of Gaia flow Skyy saw). Earlier: guild system, skills menu, townhall.
- Dungeons page (runeteria.com/dungeons): Zombie Ruins, Hollow Crypts, Boomshroom Plague - runs, clear rate, best time, drops, recent runs /
  leaderboard. A good model for public dungeon stats.
- Claims = "Homesteads" (wiki title only). Player market (Bravewinds Market). Vote reward every 3 h.
- NOT found publicly: the inventory screen, pocket crafting, backpacks, the profession list / 99 cap, party, quests, collection, how the UI is made.
  Unverified third-party claim of 20 classes / 12 races / 84 augments - do not trust.
- Sources: runeteria.com (/, /news, /dungeons, /wiki), hytale.game/en/servers/runeteria, hytaletopservers.net/servers/runeteria,
  mmohuts.com news article, x.com/Simon_Hypixel posts. Best remaining sources: their Discord announcements, YouTube / TikTok, the full 11-01 changelog.
- Borrow: one hub with a top tab bar + an always-visible currency / shortcut strip; character + stats with a combat-stats toggle; pocket crafting
  in the inventory screen; key-hint strip; skills as an icon grid with a total level; public dungeon stats. Avoid: 12 tabs (our rule: merge menus).

## 3. How the screen is made on Hytale 0.7
(pending - research agent, 2026-11-12)

## 4. Still to study
- Skyy's screenshots of every tab (Races, Professions, Classes, Party, Dungeons, Claims, Quest, Events, Collection, Settings, Help) and a short video of using the screen.
