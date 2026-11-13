# Runeteria video notes (Skyy's recordings, 2026-11-12)

Part of `research/Runetaria-Study.md` (read that first). Frames pulled every 6 s with ffmpeg into `tools/dev/scratch/runeteria/` (git-ignored;
the videos stay in Skyy's Videos folder, never in git). Videos are 6880 x 1440 (super-ultrawide): the first pass used whole-width frames where small
text was hard to read; centre crops (`c_<video>`) were made for a second look. Ideas and layout only, never Runeteria's art, text or code.

## Video 1 - 2026-11-12 18:47 (13 min, tutorial start). Frame n = (n-1) x 6 s.

### Timeline
- 0:00 Statue of Gaia cave; objective under the compass with arrow + distance; quest tracker right; red "This land is protected" toasts.
- 0:12-1:48 opens the hub (Overview): My Homes popup (empty, "Set home spot"), hover tooltips on professions ("Lv 1, 0% to next, 0/99"),
  recipes and the mount slot; spends an attribute point.
- 1:36-2:24 Professions (Mining, Woodcutting pages), Classes ("Your Build", talents blurred "Coming soon"), Dungeons (portal medallion,
  "No dungeon selected", party slots); Claims drop-down (Homesteads).
- 2:30-3:12 Quests: story "The Statue of Gaia" (3 steps), 7 dailies with Accept + rewards. 3:18-3:48 Collection: Pets "Menagerie" (3D preview),
  Lootbag Codex, Mounts "The Stables". 3:54-4:06 Hytale HUD edit mode (drag / scale / hide widgets).
- 4:18-4:42 NPC Warden Aldous ("?" marker), full-screen close-up dialogue, quest "Forged by Your Own Hand".
- 4:48-5:36 trail to the smithy camp ("Press X to harvest" on wheat); dwarf smith gives 3 steps: copper ore, 2 logs, craft.
- 5:54-7:30 mine copper ("+1 Copper Ore (3/3)" toasts), chop logs, Sawmill (Carpentry: Crude Handle, Collect), Smelter (timed smelt, Cancel %).
- 7:36-8:36 Forge: timing minigame for Copper Daggers -> "Craft complete" modal (rarity Common on a 5-pip track, stat ranges, +XP, Continue);
  recipe categories (Swords, Longswords, Daggers, Clubs, Battleaxes), rarity chances + bonuses per recipe; "YOU MADE THIS!" banner;
  quest complete banner with particles; next quest "Blade and Spell", a weapon reward.
- 9:00-12:06 Captain Vera: a pulsing arrow points at the Classes tab; abilities (Bleeding Slice Lv 2, Explosive Shot Lv 5) with tooltips
  (damage + scaling, cooldown, mana, unlock level, weapon); training dummies ("IN COMBAT" tag, damage numbers); keybinds in Hytale Settings
  > Controls (Use Ability 1-4); quest complete.
- 12:12-13:06 "Claws on the Shore" (crabs), "Auntie Marrow's Kitchen" (cooking camp), shore road, airship in the sky, "Press X to gather".

### UI style (for our own theme - the idea, not their art)
- Very dark navy panels, thin cool-grey border, small-caps centred titles, GOLD section labels and gold for selected / primary; a small
  ornament diamond at the top centre of each panel; world blurred and dimmed behind.
- Two fonts: clean sans for body, a serif display font for page titles.
- Cells: dark rounded squares, rarity-coloured outline, gold outline when selected. Primary buttons gold-filled with dark text
  (Craft, Accept Quest, Collect, Continue); secondary flat slate. Thin segmented bars. Colour discipline: navy + one gold accent,
  green only for ready / complete, red for danger / cancel.

### Screens seen
- **Hub top bar:** tabs (some with drop-down carets), active = gold with an orange underline; currency chips, trophy, mail, servers,
  gold Store button at the right. A "tutorial hand" arrow can point at a tab.
- **Overview:** left character panel (paper doll with head / body / hands / legs, trinkets incl. mount, 3 utility slots, Vitals, Attributes with
  gold "+" when a point is free, pulsing "Attribute point available", Show combat stats, RTP + Homes buttons); centre top Pocket Crafting
  (filter icons, ~5 x 5 recipe grid, pages, detail card: inputs have / need, big Craft, 10x / Max; can swap to a "More backpack" view);
  centre bottom Inventory (4 action icons, backpack tabs, 9 x 4 grid, hotbar with a bigger first slot, key-hint strip); right Professions
  column ("Total level", 3-wide icon tiles with "1 / 99", grouped, hover tooltip).
- **Profession page:** badge + big name, "Mastered to level N" bar, "Next unlock", Mastery button; "Road to Mastery" 6 ranks (Novice ...
  Master) on a line; Masteries list (icon, name, +% bonus, 5-pip bar, upgrade needs a manual).
- **Classes:** "Your Build" banner (class, level, scaling attribute, Switch class, 4 slot chips: Signature, Ability, Ability, Utility with keys);
  loadout left, abilities per slot middle with stat tooltips, talents right (locked teaser); recommended attributes + set bonuses footer.
- **Dungeons / Party:** dungeon list with difficulty + tabs, party panel (5 seats, Create a party), big portal medallion, info panel.
- **Quests:** log left (All / Story / Dailies / Weeklies / Achievements, progress bars, Followed only), details right (chapter, steps with
  check rings, About, Rewards with icons + XP, gold Accept / Track); chips "Dailies done 0/7", "Daily reset 3h", "Weekly reset 3d"; toasts.
- **Collection:** Pets "Menagerie" (owned list vs greyed "not yet found", 3D model on a lit podium, stat row, gold Summon); Mounts "The Stables"
  (same, speed bar, ground / flying); Lootbag Codex (bag grid with filters, drop table with % and quantity ranges + where to get it).
- **Stations (Sawmill / Smelter / Forge):** one template - title, profession card (level, XP, next unlock, Mastery), searchable collapsible
  categories, big preview, rarity chance bar, possible bonuses, required materials + "Your materials" grid, amount slider + Max, time + XP
  per craft, green "Ready to craft", gold Craft; timed crafts with progress + Cancel, a Collect queue; forging timing minigame; result modal.
- **Dialogue:** camera close-up on the NPC, world dimmed, gold name, 2-3 lines, Continue key chip.
- **HUD:** portrait + level + class + thin XP bar top left; compass + objective + distance + banner top centre; quest tracker right (story vs
  side markers, step counters); currencies / server / online top right; icon column left; ability bar (round ultimate + 3) with locked levels,
  "Attribute point available", 2 quick slots, red / blue bars meeting at an ornament, hotbar, gold full-width class XP bar; "IN COMBAT" tag;
  in-world yellow outline + "Press X" on usable things; "?" / "!" markers with a floor ring; pickup toasts "+1 item (n/m)"; damage numbers.
- Not themed: Hytale Settings, the Whisper modal and My Homes popup (inconsistent - we should theme every page).

### Systems and onboarding
- 4 classes; class level + XP; Signature + 2 Abilities + Utility unlocking by level; scaling attribute; set bonuses; talents later.
- 5 attributes, 1 point a level. ~19 professions 1-99 (gathering, crafting, other) with ranks and masteries (manual upgrades).
- Crafting: pocket crafting anywhere + stations with profession XP, rarity rolls, bonus stats, timed crafts, collect queue, a minigame.
- Quests: story chapters, side, 7 dailies, weeklies, achievements, reset timers. Collection: pets, mounts, lootbag drop tables.
- Onboarding: statue -> class -> NPC -> (hub tour) -> smith: gather, craft, smelt, forge -> class trainer: abilities on dummies -> first
  fights. Teaching tools: waypoint + distance, "Press X" prompts, an arrow on the tab to open, "?" markers, completion banners, locked teasers.

### Borrow for SkyWynn
1. Persistent currency / shortcut strip and the key-hint row under the inventory.
2. Tutorial steps that make you open a tab, with an arrow on that tab.
3. ONE station template for every crafting station; pocket crafting = a small version of it.
4. Craft result modal with rarity + stat ranges (fits our rarity tooltip rule); "Your materials" next to "Required materials".
5. Locked abilities shown with level + key; a locked teaser for future content.
6. Lootbag / drop-table codex with percentages (transparency for our loot, Collections, Bazaar).
7. Quest log: list left, steps + rewards right, reset timers at the top, follow filter, toasts.
8. Pets / mounts: card grid + 3D preview + one Summon button.
9. NPC close-up dialogue; in-world interact outline + prompt.
### Avoid
- Small grey text (our bigger flavour text rule), too many tabs + drop-downs, pocket crafting fighting the inventory for space, a full-size
  locked panel, 4 minutes of menus before any combat, spammy "protected land" toasts, unthemed popups.
