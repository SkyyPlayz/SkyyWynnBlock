# UI queue from Hylterium: HUD hints, quest fold, vanilla feed, ground arrows, dialogue bar, stats by source, heads, picture tiles, zoom scroll (BUILD-READY spec, 2026-10-22)

Where this goes: `research/` (INDEX.md research row). Skyy's answers to section 12 go word for word into `docs/answered/ui.md`
(`python tools/qa_append.py ui <file> --close "<question words>"`); the probe results + builds go into `docs/log/2026-10.md`; passing probe
keys go into `tools/skyyui.py` PROBED. When an idea below becomes a round, note the round here and in `research/UI-Ideas.md`. Owner: Skyy (they/them).

**Sources read (2026-10-22):** `research/UI-Ideas.md` (the 2026-10-22 Hylterium lines), the reference screenshots `research/refs/*hylterium*.webp`
+ `player-head-rpgleveling.webp` (local, git-ignored - LOOK only, never their art or code; RPG Leveling 0.4.2 is All Rights Reserved = ideas
only), `HANDOFF.md` section 2, `research/Menu-Pattern.md`, `research/Vanilla-UI-Style-Guide.md` (15 colour code, 16 node maps),
`research/Radial-Trees-Spec.md` "Probe results", `research/cloud/Ability-Input-Design.md`, `research/SkyyQuests-Tutorial-Spec.md`,
`research/cloud/Stats-Page-Spec.md`, and the SET pins in `tools/deploy_set.py`: SkyyHud 0.3.34, SkyyMenu 0.3.43, SkyyClasses 0.1.45,
SkyyQuests 0.4.2, SkyyTrees 0.5.0, SkyyRebirth 0.5.0, SkyyPets 0.4.9, SkyyGear 0.3.38, SkyyUiProbe 0.7.1. Engine facts = read-only
reflection / bytecode of HytaleServer.jar (`tools/dev/reflect.py`, `bcfull.py`, `cpgrep.py`) + Assets.zip (read-only).

**Feasibility marks:** **PROVEN** = works in our own deployed code (cited) or seen by Skyy; **NEEDS PROBE** = the engine has it but we never
saw it in game -> SkyyUiProbe 0.8 (section 10); **NOT POSSIBLE** = no server API (evidence given).

---

## 0. Summary table

| # | Idea | Feasible? | Mod + version | Round order |
|---|---|---|---|---|
| 1 | HUD key hints: "Alt (menu)" slot + Mouse 5 / Q / E | Alt slot PROVEN parts; ability hints ALREADY LIVE (vanilla Abilities HUD + our rune mirror) | SkyyHud 0.3.35 (Keys widget) | R1 |
| 2 | Quest tracker fold on double crouch + hide | PROVEN parts; double crouch is TAKEN by SkyyMenu today -> one owner, a setting | SkyyHud 0.3.35 + SkyyMenu 0.3.44 | R1 |
| 3 | Our cards in the VANILLA pickup feed | engine route PROVEN (the pickup feed IS `NotificationUtil`); look + merge NEEDS PROBE F1 / F2 | SkyyHud 0.3.35 (feed route) | R1 |
| 4 | Ground guide arrow + "Objective / N blocks" | per-player arrow = particles, NEEDS PROBE G1; a per-player world LABEL is NOT POSSIBLE -> HUD label | SkyyQuests 0.4.3 (+ SkyyHud label) | R3 |
| 5 | NPC dialogue bar (bottom, Skip / Next, n / m) | NEEDS PROBE D1 (transparent page root, bar at the bottom) | SkyyQuests 0.4.3 | R3 |
| 6 | Stats page "by source" table | PROVEN parts (bridge keys exist for Gear / Charms / Pets / Trees; HP / Mana / Stamina by modifier) | SkyyMenu 0.3.44 | R1 |
| 7 | Self-built player heads with hair | delivery PROVEN on the HUD (minimap), on a PAGE NEEDS PROBE H1; the look NEEDS PROBE H1c | kit 1.9 `SUI.head` + SkyyMenu 0.3.45 (+ readers later) | R4 |
| 8 | Picture tiles on the SkyWynn Menu | PROVEN (jar texture as Group Background on pages); sharpness + feel = look check T1 | art (cloud, skywynn-art) -> SkyyMenu 0.3.45 | R5 (art now) |
| 9 | Zoom keeps the scroll position on radial pages | NEEDS PROBE M8 (+ M4 / M5 retest) | kit 1.9 + SkyyTrees 0.5.1 + SkyyRebirth 0.5.1 | R2 |

One probe (SkyyUiProbe 0.8, section 10) covers every NEEDS PROBE above in one ~5 minute session (`/skyprobe tour`).

---

## 1. HUD key hints - "Alt (menu)" beside the hotbar + Mouse 5 / Q / E

**Skyy's words:** UI-Ideas 2026-10-22 GROUND GUIDE ARROWS line: "Other HUD bits in the same shot worth learning: a hotbar side slot 'Alt (menu)'
showing the menu key; ability key hints bottom right (MOUSE 5 / Q / E with ability icons)". Menu on Left Alt: "just pressing Lalt is fine. i
dont know anyone who actually uses a walk key" (VERIFIED in SkyyMenu 0.3.42, TEST-CHECKLIST 218).

**What exists today**
- Left Alt = the client's WALK key; SkyyMenu's `MenuHotkey` opens the Menu on its rising edge (`SkyyMenu/build_skyymenu_0.3.43.py` 13747-13754,
  `walkStep`; setting `menu.walkKey`, player switch `menu.walkmenu`).
- **Ability hints are already the vanilla HUD.** Hylterium's bottom-right "MOUSE 5 / Q / E" boxes are Hytale's own Abilities HUD
  (`HudComponent.Abilities`; it prints each player's REAL bound key). Ours feeds it: Ability1 (Skyy's Mouse 5) = the weapon signature
  (vanilla charged meter, `SkyyArmory` sets `Interactions.Ability1` per weapon, e.g. `build_skyyarmory_0.1.43.py` 4759-4806), Ability2 (Q) /
  Ability3 (E) = the class abilities: SkyyClasses' **rune mirror** (`abil.runeHud`, since 0.1.21) puts the runes of your two primaries into the
  vanilla AbilitySlots 0 / 3 every 2 s, so the vanilla HUD shows our icons + cooldowns with your keys (`build_skyyclasses_0.1.45.py` 748-760;
  the cast hook reads `Ability2` / `Ability3` at 23399). Our own SkyyHud **Abilities** widget (default `br 460,21`,
  `build_skyyhud_0.3.34.py` 963) adds names, cost, cooldown and the crouch alts while you crouch.
- The server never learns a player's binds (Ability-Input-Design 117; probe K2 "default binds" never ran) - only the VANILLA HUD can print the
  real key. The vanilla `InputBindings` HUD + `RootInteraction.HudInputBindingEntry` (used by `Root_Common_StatAmmoReload_Entry` "reload")
  prints real keys for item interactions, but the Walk key is a movement key, not an interaction - it cannot carry a vanilla hint.

**Feasibility**
- Ability hints: **PROVEN / LIVE** (vanilla HUD + rune mirror). Nothing to build. Look check in the probe tour (K1: "with a class on, the
  bottom-right vanilla ability boxes show your class icons + Q / E") - if Skyy has never seen icons there, that is a SkyyClasses bug to chase,
  not a UI round.
- "Alt (menu)" slot: **PROVEN parts** - a SkyyHud widget with a `b` (bottom-centre) anchor + dx (anchors T / L / C / R / B exist since 0.3.9),
  the vanilla key-cap texture `Common/InputBinding.png` (Assets.zip `Common/UI/Custom/Common/InputBinding@2x.png`, the cap vanilla draws in
  `ToolsLegendsCommon.ui` / `ActionButton.ui`; our kit already references `Common/...` vanilla textures, e.g. `Common/SearchIcon.png`). No probe.

**Design (SkyyHud 0.3.35, new widget "Keys")**
- Widget id `Keys`, label "Key hints", default ON, anchor `b` with dx = +330 (right of the hotbar, Hylterium's spot; the hotbar's width
  follows the client's UI scale, so the player drags it in the HUD editor like every widget), size 64 x 56, Background OFF (0.3.28 rule).
- Content: the vanilla key cap (PatchStyle `Common/InputBinding.png`, Border 6, 48 x 26) with "ALT" (Secondary font 14, uppercase,
  `#ccd8e8` - the vanilla `@BindingLabelStyle` values, added to the kit as `SUI.keycap()`), under it "Menu" caption 13 `#96a9be`.
- Shown only while the Walk key really opens the Menu (Server Setup `menu.walkKey` on AND the player's `menu.walkmenu` on - read through a new
  bridge flag `menu:walkkey:<uuid>` "1"/"0" SkyyMenu publishes on change); otherwise hidden. Text is fixed "ALT": the server cannot see a
  rebind (Q11).
- Options (Settings > HUD, per player): show / hide. No ability caps here - the vanilla boxes already show Mouse 5 / Q / E.
- Ids `#SkyyKeysCap`, `#SkyyKeysCapTxt`, `#SkyyKeysTxt` (no underscores); never updated periodically (only on the flag change).

**Order:** R1 (with items 2, 3, 6).

---

## 2. Quest tracker fold / unfold on double crouch + a hide command

**Skyy's words:** "their quest menu uses double crouch to expand to bigger or shrink" (UI-Ideas 2026-10-22 QUEST WIDGET FOLD; footer hints
"/sidebar: hide" and "Crouch x2 to fold"; ref `research/refs/quest-widget-hylterium.webp`). The UI-Ideas line already says: "CHECK FIRST ... a
double crouch must not fire a crouch-cast, or use the Walk key / a Menu setting instead."

**What exists today**
- SkyyHud **Quest Tracker** widget: `tl 8,42`, 300 x 149 / 124 / 99 (header + up to 3 tasks), Background ON, text wraps (0.3.33),
  data only from `quest:fn:hud` when `quest:epoch:<uuid>` changes (`build_skyyhud_0.3.34.py` 1001-1007, 2627-2699).
- **Double-tap crouch is TAKEN:** SkyyMenu 0.3.19+ opens the SkyWynn Menu on two crouch presses within `menu.hotkeyGapMs` (400 ms) while
  standing on the ground (`MenuHotkey.step` / `still()`, `build_skyymenu_0.3.43.py` 13737-13805; player switch `menu.hotkey` "Hub hotkey:
  double-tap crouch" ON by default, 1216-1217; Server Setup rows 1310-1314).
- **Crouch-cast (Ability-Input-Design 1.2):** crouch is a STANCE read at the moment Ability2 / Ability3 fires (crouch held >= `abil.crouchMinMs`
  100 ms); crouch in the AIR belongs to movement (Monk air jump, Plunge, `acro.doubleJump.trigger=crouch` on old files). A double tap alone
  casts nothing.
- `/quests hide` / `/quests show` exist but mean "I know how to play" (hide the TUTORIAL line), not the widget (`build_skyyquests_0.4.2.py` 455,
  3918) - reusing them would change their meaning.

**Clash check**
| Gesture | Who reads it today | Clash with a fold? |
|---|---|---|
| double-tap crouch, on the ground, standing still | SkyyMenu MenuHotkey -> opens the Menu | **YES - same gesture.** Two listeners would fire both (Menu opens AND the widget folds). |
| crouch held + Q / E | SkyyClasses stance | no (a fold needs two short taps and no key; a crouch-cast after a double tap would ALSO fold - harmless, cosmetic) |
| crouch in the air | SkyySkills / SkyyArmory movement | no (`still()` needs `onGround`) |
| Walk (Left Alt) | SkyyMenu -> Menu | would clash; not used |

**Proposal (no new input, one owner):** the gesture keeps ONE detector - SkyyMenu's MenuHotkey (already world-thread, cheap, gated by
`still()`). Since Left Alt now opens the Menu, the player switch `menu.hotkey` changes from a bool to a choice
**"Double-tap crouch: Fold quest tracker | Open the menu | Nothing"**, default **Fold quest tracker** (Q1). A one-time setting migration
(PROJECT-RULES 4) only rewrites players still on the old default ON -> "fold"; OFF stays "Nothing"; History snapshot + Undo line + run-once
marker. On fire, `HotkeyOpen` calls the new SkyyHud bridge `hud:fn:questFold` (`apply(Object[]{UUID, "toggle"})` -> Boolean; missing /
false = falls back to opening the Menu, so nothing silently dies). Extra guard against the crouch-cast double: ignore the gesture for 1 s after
an Ability2 / Ability3 press (SkyyClasses already stamps casts; read `class:lastcast:<uuid>` Long if published, else skip the guard -
UNVERIFIED that key exists; the builder adds it to SkyyClasses only if it is a one-line put, else drops the guard).

**Design (SkyyHud 0.3.35)**
- Two states per player, saved in the player's HUD layout line (new field, old lines = Open): **Open** (today: header + up to 3 tasks) and
  **Folded** (header only: quest icon, line name cut to fit, "1/5", the % in gold `#e8c25a`; 300 x 32). A fold is ONE HUD update of
  `.Visible` + the box Anchor height (proven HUD sets) - never a re-send.
- Footer hint line in Open state (caption 12, `#7f93a6`): "Crouch x2: fold - /quests widget hide" (only while the choice is "Fold quest
  tracker"; otherwise no hint).
- Hide: `/quests widget hide | show | fold` (a sub-command of the existing `/quests`, SkyyQuests 0.4.3 calls `hud:fn:questFold` with
  "hide" / "show" / "toggle"; `setPermissionGroups(hytale:Adventurer)`) - Menu-Pattern 3.5 "replace, never add": no new top-level word, no
  `/sidebar` (Q2). Settings > HUD's per-widget show / hide stays the same switch underneath.

**Order:** R1 (SkyyHud 0.3.35 + SkyyMenu 0.3.44 deploy TOGETHER: Menu calls the Hud function; old Hud = Menu falls back to opening the Menu).

---

## 3. Our feed cards inside the VANILLA pickup feed

**Skyy's words:** "and i like the way they tied their updates into the vanilla feed" (UI-Ideas 2026-10-22; ref `vanilla-feed-hylterium.webp`:
bottom-right cards "[Lifesteal] Effect applied. Healed 1", "You killed: Lizard Sand" (name in gold), "[LEVEL 1] +424.2 XP | ||||||------ |
648.7/1697.1 (38%)", stacked with "2 Medium Hide", "2 Raw Wildmeat").

**What exists today**
- SkyyHud 0.3.20+ **Notification Feed** widget = OUR panel, bottom-left above the chat (`bl 8,488`, 4 cards 280 x 32, 4 s, merges repeats
  "Pumpkin x9"; `build_skyyhud_0.3.34.py` 227, 966, 7713). Senders go through `tools/skyyroute.py` MsgRoute: `msgroute:fn:get` (Chat / Feed /
  Off per message kind), `feed:fn:push {UUID, kind, itemId, text, count}`, `xpflash:fn:push` - SkyySkills 0.4.34+, SkyyClasses 0.1.20+,
  SkyyCollections 0.2.12+ (and SkyySkills 0.4.42's "Fortune! <item> xN" card). So: today our cards are a SEPARATE panel, not the vanilla feed.

**Engine finding (bytecode, HytaleServer.jar):** the vanilla pickup feed IS the notification packet. `Player.notifyPickupItem` does
`NotificationUtil.sendNotification(packetHandler, Message.translation("server.general.pickedUpItem").param("item", stack.getDisplayName()),
null, stack.toPacket())` + the `SFX_Player_Pickup_Item` sound, gated by `GameplayConfig.ShowItemPickupNotifications`. The packet
(`protocol.packets.interface_.Notification`) carries `message`, `secondaryMessage` (FormattedMessage = colours), `icon` (String),
`item` (ItemWithAllMetadata), `style` (Default / Danger / Warning / Success) and a **`tag`** (String) - `NotificationUtil` has 15 per-player
overloads incl. `(PacketHandler, Message, Message, String icon, ItemWithAllMetadata, NotificationStyle, String tag)`.
**We already send it:** SkyyClasses' "You can't use this weapon" popup = `NotificationUtil.sendNotification(pr.getPacketHandler(), title,
body, icon, NotificationStyle.Warning)` with `Message.raw(..).color(..)` and `new ItemStack(id, 1).toPacket()` (`build_skyyclasses_0.1.45.py`
3232, 5585-5600; also SkyyGear GearGate). Hylterium's cards are this same packet.

**Feasibility:** route **PROVEN**. NEEDS PROBE (look only, F1 / F2): how coloured text + a text progress bar look in that feed, how
many lines stack before the oldest goes, whether the client merges repeats, and whether the same `tag` REPLACES the card in place (would give
"Mining +42 XP" that counts up instead of 10 cards).

**Design (SkyyHud 0.3.35 - the senders do not change)**
- New destination value **"Vanilla feed"** for every message kind in Settings > Messages (player) and Server Setup > Messages (default):
  Chat | Feed (our box) | **Vanilla feed** | Off. `msgroute:fn:get` keeps answering "feed" for both feed kinds (senders untouched);
  `feed:fn:push` then either draws our box (today) or sends the notification itself and answers TRUE. Default after F1 PASS: Vanilla feed
  (Q3); our box stays a choice (it also keeps the Skill XP flash).
- Card formats (one colour code, Style Guide 15; Message spans with `.color()`; at most ~60 characters; secondary line only when needed):
  | Kind | Line | Icon |
  |---|---|---|
  | skill XP | `[Mining 23] +42 XP  |||||||---  71%` - "[Mining 23]" gold `#e8c25a`, "+42 XP" green `#7ee08a`, bar 10 cells (filled `#e8c25a`, empty `#7f93a6`), % gold | the skill's icon item |
  | kill | `You killed: [Lv 9] Trork Mauler` - name in its rarity / elite colour | none (or the mob's drop icon) |
  | Fortune | `Fortune! Copper Ore x3` - "Fortune!" gold | the item (count in the card) |
  | heal / lifesteal | `[Lifesteal] Healed 4` - tag green | none |
  | collection | `[Copper Collection III] 1,240 / 2,500  |||||-----` | the collection item |
  | class / quest | as today's chat text, the head word coloured | as today |
- Merge: if F2 shows `tag` replaces in place -> tag = `skyy:<kind>:<key>` (e.g. `skyy:xp:Mining`) and the card shows the running total for
  4 s; else keep SkyyHud's own merge (`MsgRoute.gate`, one new card per key per 1.5 s) before sending.
- Items: icon = `new ItemStack(id, 1).toPacket()` only (never a stack with metadata - HANDOFF 2 ItemGrid rule applies in spirit).
- A burst cap per player (6 notifications a second, Server Setup row `hud.vfeed.perSecond`), cards over it fall back to our box / chat
  (nothing a player chose to see vanishes - skyyroute rule).
- Also worth taking from the same shot (later, not in R1): zone name + level band on the XP line ("Zone 2 Desert Springs (Lvl 8-30)") ->
  the SkyyHud Skills widget's header, a one-line ask for SkyyWorldGen's zone key.

**Order:** R1.

---

## 4. Ground guide arrows for quest objectives ("Objective: ..." + "N blocks")

**Skyy's words:** "they have guide arrows on the ground" (UI-Ideas 2026-10-22 GROUND GUIDE ARROWS; ref `guide-arrows-hylterium.webp`: a big flat
gold arrow on the ground a few blocks ahead, label "Objective: Explanation" + "84 blocks"); the older wish "if we can id like a trail to
follow" (social.md 54 / SkyyQuests spec 14).

**What exists today**
- SkyyQuests 0.4.2: `quest:fn:markers` (`{UUID, world}` -> `{id, kind, x, y, z, label}`), map markers per player (TownProbe #9 PASS), the
  Quest Tracker's 8-way arrow + "NE 42 m - Island 2" (`SkyyQuests-Tutorial-Spec.md` 216, 255, 290-300); its NPC code already spawns particles
  for a viewer list: `ParticleUtil.spawnParticleEffect(id, Vector3dc, List viewers, ComponentAccessor)` (`build_skyyquests_0.4.2.py` 5556;
  same call per player in SkyySkills 0.4.42's Fortune sparkle "for that player only", SkyyExploration 0.3.0 chest sparkles).
- Planned: a particle TRAIL (SkyyQuests spec 6, "later option").

**Engine findings**
- `ParticleUtil.spawnParticleEffect(String, Vector3dc, Rotation3f, List viewers, ComponentAccessor)` exists -> a particle system can be spawned
  **rotated** (yaw toward the target) **for one player**.
- Vanilla particle spawners can be NON-billboard: `"ParticleRotationInfluence": "None"` + `"ParticleRotateWithSpawner": true` (547 vanilla
  spawners, e.g. `Server/Particles/Abilities/GroundSlam/Spawners/Ability_GroundSlam_Crack.particlespawner` = a flat crack decal). Our mods
  already ship their own `.particlesystem` / `.particlespawner` files (SkyyGear 70, SkyyArmory 43 build scripts) - PROVEN packaging.
- **Per-player entities do not exist:** `EntityTrackerSystems$HideFromPlayer` only hides entities that carry a `PlayerRef` (players) via
  `HiddenPlayersManager` (bytecode: `Archetype.contains(playerRefComponentType)` before `isPlayerHidden(uuid)`); `HiddenFromAdventurePlayers`
  hides from ALL adventure players. So an arrow ENTITY or a nameplate label would be seen by everyone -> **a per-player world label is NOT
  POSSIBLE**. A per-player fake block (a block packet to one client) is possible in theory but desyncs (rejected).

**Feasibility:** arrow **NEEDS PROBE G1** (flat orientation, yaw, size, readability, cost). Label in the world: **NOT POSSIBLE** per player ->
the label goes on the HUD.

**Design (SkyyQuests 0.4.3 + a SkyyHud label)**
- Arrow = our own particle system `SkyyQuests_GuideArrow` (one flat gold arrow sprite, our art: a chunky Hytale-style gold arrow with a dark
  outline, 64 x 64 @ 1x, drawn per skywynn-art; lifetime 1.2 s, fade in / out), spawned **4 blocks ahead of the player on the ground** (first
  solid block under that point + 0.05), yaw = toward the next path point, **every 1.0 s** while the tracked task has a `where` target in the
  SAME world farther than 12 blocks, for that player only (viewer list = [player]). Stops within 12 blocks (the map / NPC marker takes over),
  in another world (Tracker shows text only, as today), while gliding / swimming / in a page.
- Path: straight line to the target (no path-finding); over a gap / up a cliff the arrow tilts toward the target height (pitch from dy,
  clamped +-35 deg) - G1 shows whether pitch works; else flat only.
- The "Objective" label: SkyyHud's Quest Tracker task 1 already shows the arrow + distance; add a small **HUD label above the hotbar**
  ("Objective: Talk to Marlow - 84 blocks", 15 px, gold label + white text, shown only while arrows are being drawn; `quest:fn:hud` field
  `dist` already exists) - Q5.
- Cost: one particle packet per tracked player per second; the target + yaw maths reuse the reach poll (1 s, 10 us avg TownProbe #6).
- Server Setup (SkyyQuests): `quests.arrow.enabled` (on), `quests.arrow.everyMs` (1000, 500-3000), `quests.arrow.ahead` (4, 2-8),
  `quests.arrow.minDist` (12); player switch "Guide arrows on the ground" (on).
- Particle trail (spec 6) stays a later option; G1 also shows a 6-dot trail for comparison (Q4).

**Order:** R3 (after the probe; with item 5).

---

## 5. NPC dialogue bar (bottom panel: speaker, line, page n / m, Skip / Next)

**Skyy's words:** UI-Ideas 2026-10-22 HYLTERIUM SERVER line: "NPC DIALOGUE BAR worth learning ... a bottom-centre panel, speaker name top-left
('Borin'), line page top-right (1/1), the line in the middle in cyan, Skip (left) / step count '1 / 6' (centre) / Next (right, blue); the world
stays visible above, camera on the NPC -> fits SkyyQuests NPC talk." (ref `npc-dialogue-hylterium.webp`; the bar is NOT from RPG Leveling -
another Hylterium mod, unknown; QuestLines suite = ARR and not installed - nothing to pack.)

**What exists today:** SkyyQuests 0.4.2 `QDlgPage` = a centred 900 x 430 kit window (`page_shell`): portrait ItemIcon 104 + up to 6 wrapped
lines, sub line "page n of m" or "Reward: ...", status line, Next + Close / Accept + Not now (`build_skyyquests_0.4.2.py` 5696-5745);
opens on the next tick after F (TownProbe #1 / #16 VERIFIED); dialogue files `Skyy_SkyyQuests/dialogue/<npc>.properties`.

**Feasibility: NEEDS PROBE D1.** Page roots may only carry Width / Height (HANDOFF 2) and are centred, so a bottom bar = a TRANSPARENT root
(1600 x 980, no Background) with the bar as a child at its bottom. Unknown: does the client dim / blur the world behind a custom page (then
"the world stays visible" fails), and does a transparent root eat clicks on the world (it should not matter - the page owns the mouse).
Camera on the NPC: the engine has server camera control (`modules/camera/*`, `/camera topdown` commands) but a stuck camera is a real risk ->
not in this round (Q6).

**Design (SkyyQuests 0.4.3, kit 1.9 `SUI.dialogue_bar()`)**
- Root 1600 x 980 transparent; the bar **1100 x 190** at `Left 250, Top 770` (bottom edge ~= the hub page's bottom), kit sky window frame
  (`theme_*`, gold edge like the ref but from our kit), inside:
  - top row (28): speaker name left (tipName 18, gold `#E8A93B`), "line 1 / 6" right (caption 15) - one counter only (Hylterium shows two;
    ours shows the page count once, bottom centre is free for the reward line);
  - the line (centre, 18 px, cyan-white `#d6f1ff`, wraps to 3 lines max - longer text is split into pages at build time of the dialogue
    file, never cut);
  - bottom row (44): **Skip** (Secondary, left; jumps to the LAST page so an Accept is never skipped by accident), centre caption "Reward:
    50 coins" on the last page, **Next** (Primary, right) -> on the last page **Accept** (Primary) + **Not now** (Secondary) or **Close**.
  - optional portrait: the NPC's icon item (ItemIcon 64) in the bar's left end (today's portrait, smaller).
- Same data and handler as `QDlgPage` (pages[], mode, reward); every click = exactly ONE page packet (rebuild for page turns, as today).
- Esc / Close = the dialogue's "close" path (no accept). F again on the NPC while open = ignored (one dialogue at a time).
- Fallback if D1 shows a dim screen: keep the bar look but accept the dim (still better than the centred window) - Skyy decides on the
  screenshot.

**Order:** R3 (with item 4).

---

## 6. Stats page "by source" table (the four power sources)

**Skyy's words:** RPG Leveling study (UI-Ideas 2026-10-22): "a 'Resume' table (Stat / Base / Stats / Class / Total columns) that breaks each stat
down by source - fits our Stats page + the four power sources"; the standing rule "this applies acroos the board. to all skills. and your class.
your weapon is only part of it. your gear is important, but accessory's and pets are essential too!" (PROJECT-RULES 4).

**What exists today:** SkyyMenu 0.3.43 Stats page (Character > Skills > YOUR STATS): one scroll list, rows "name | total | source text"
(`ST_GEAR` 13 gear stats, `ST_ELEM` / `ST_RAW`, Fortune / Wisdom per skill, `ST_GROUPS` Gear / Accessories / Overall / Class / Base Mana /
Skills / Trees for Health / Mana / Stamina read from the EntityStatMap modifiers; `build_skyymenu_0.3.43.py` 2733-2800).
Bridge keys that already split stats by source (no other mod needs a change for phase A):
| Column | Key today (java.lang types) | Owner |
|---|---|---|
| Gear (weapon + armour + tools held) | `gear:stats:<uuid>` totals (GearTick) / `gear:fn:stats` | SkyyGear 0.3.38 |
| Charms (Void Charms) | `gear:extra:<uuid>` "str:40,cc:10,..." | SkyyAccessories 0.5.31 |
| Pets | `pets:stats:<uuid>` Map String -> Number (`build_skyypets_0.4.9.py` 4698) | SkyyPets 0.4.9 |
| Trees (+ Nexus) | `gear:extras:<uuid>` Map source -> "str:N" ("trees", `build_skyytrees_0.5.0.py` 1279) | SkyyTrees 0.5.0 |
| Class | Health / Mana / Stamina class modifiers (classboost*, classstamina), class weapon damage `skill:dmg:<uuid>` | SkyyClasses / SkyySkills |
| Base | the game's base + armour (EntityStatMap) + skill-level bonuses (Overall) | engine / SkyySkills |

UNVERIFIED (the builder checks first): whether `gear:stats:<uuid>` already INCLUDES the Charms / Pets / Trees parts (SkyyGear joins them in
`GearStats.extra`, `build_skyygear_0.3.38.py` 282, 26440-26472). If yes, Gear column = total - (Charms + Pets + Trees); if no, Total = sum.

**Feasibility: PROVEN parts** (reads only; the page and its kit blocks exist). No probe.

**Design (SkyyMenu 0.3.44, phase A = Menu only)**
- YOUR STATS keeps its one scroll list + section heads (Menu-Pattern M4); each stat row becomes a table row:
  `Stat 300 | Base 150 | Gear 150 | Charms 150 | Pets 150 | Trees 150 | Class 150 | Total 180` = 1,380 + 7 x 6 gaps <= 1,552 content width.
  Row height 38 (today's `ST_ROW_H`), name 18 (`#d6e4ee`), cells 16 right-aligned, a cell with 0 shows a dim "-" (`#7f93a6`), positive green
  `#7ee08a`, negative red `#ff7a7a`, Total bold gold `#e8c25a` (Style Guide 15). A header row under each section head (caption 15).
- Units: "%" rows show "+12 %"; Health / Mana / Stamina show whole numbers.
- Hover on a column header (TooltipText if M6 passes, else the caption line under the sub-tabs) explains it: "Charms = your Void Charms",
  "Trees = skill + class trees and the Rebirth Nexus", "Base = the game, your armour's base and your skill levels".
- Footer note row: "Four power sources: tool / weapon + gear + charms + pets" (one line, caption).
- Phase B (later, only if Skyy wants exact Skills / Rebirth columns): the `stats:contrib:<Mod>` contract of `research/cloud/Stats-Page-Spec.md`
  4.1 (one Function per mod) - not needed for this table (Q7).

**Order:** R1 (same SkyyMenu 0.3.44 as item 2).

---

## 7. Self-built player heads with hair

**Skyy's words:** "they found a way to show my player head. though its missing its hair." (UI-Ideas 2026-10-22 PLAYER HEADS - WORKING EXAMPLE)
+ the 2026-10-18 wish "player head for the player list, or for other things in the UI". The study's recommendation (option A): read
`PlayerSkinComponent` / `PlayerSkin`, composite face + hair + accessory from the installed game textures at RUNTIME, cache per UUID + skin
hash, send as CommonAsset to an AssetImage; never a web service (RPG Leveling fetches hyvatar.io by username - third-party, no terms, rejected).

**What exists today (the delivery is ours already)**
- **Runtime PNG -> one player -> AssetImage is PROVEN on the HUD:** SkyyHud's minimap encodes pictures at run time (`MmPng.encode`), names
  each by content hash (`CommonAsset.hash`), sends it to ONE player once per connection as `AssetInitialize` + `AssetPart`(s) +
  `AssetFinalize` (CommonAssetModule.sendAsset's sequence, parts of 2,621,440 bytes) and shows it with
  `AssetImage { AssetPath: "UI/SkyyHud/mm/<kind>-<hash16>.png" }` (`build_skyyhud_0.3.34.py` 5192, 5206, 5859-5900, 6562-6569; Skyy saw the
  minimap 2026-10-06). Content-named pictures need NO `RequestCommonAssetsRebuild`.
- **The trap (2026-10-15 root cause):** a `RequestCommonAssetsRebuild` while a page is open glitches that page (Hud 0.3.27 sends its statics +
  the one rebuild at connect and defers it while a page is open; Profiles waits for `hud:assets:ready`). HyUI 0.9.8 (Mods folder, read only)
  does dynamic page images with 25 FIXED slot paths + a rebuild each time - exactly the trap; we keep content names and no rebuild.
- `PlayerSkin` (protocol) = 20 String parts: bodyCharacteristic, face, eyes, ears, mouth, facialHair, **haircut**, eyebrows, **headAccessory**,
  faceAccessory, earAccessory, skinFeature, underwear, pants, overpants, undertop, overtop, shoes, gloves, cape; `PlayerSkinComponent
  .getPlayerSkin()`; parts are blockymodels + (often greyscale) textures tinted by gradient sets (`Common/Characters/Haircuts/Afro.blockymodel` /
  `AfroPuffs_Greyscale.png`, `Common/Cosmetics/Head/*` 266 files, `server.core.cosmetics.CosmeticRegistry`, `PlayerSkinGradient`).

**Feasibility**
- Delivery to a PAGE: **NEEDS PROBE H1a / H1b** (AssetImage on a page is unproven - M4 never ran; pushing a new picture WHILE a page is open,
  without a rebuild, is unproven).
- The look (does a 2D head from the parts read as "me, with hair"?): **NEEDS PROBE H1c** (a draft).
- No vanilla UI element draws a 3D model / player (study) -> a full-body preview like Hylterium's is NOT POSSIBLE except as a picture we draw.

**Design (kit 1.9 `SUI.head` + a head service; first reader SkyyMenu 0.3.45)**
- Build time (Python, `tools/skyyheads.py`, vanilla-derived output goes INTO THE JAR ONLY, never committed): for every haircut / facial
  hair / head + face accessory / eyes / eyebrows / mouth / face variant, render the FRONT view of its blockymodel head part orthographically
  (front-facing quads, UV-mapped, depth-sorted) into a 32 x 32 layer (greyscale kept greyscale + an alpha mask) - ~400 small layers, ~150 KB.
- Run time (Java, off the world thread): parse the 20 part strings (the exact id / colour format is what H1c dumps), pick the layers, tint
  greyscale layers with the part's gradient colour, composite skin base + face parts + facial hair + hair + head accessory (back hair behind
  the face, front fringe over it), upscale x2 nearest to 64 x 64, encode PNG, name `UI/Skyy/heads/<sha16>.png`, cache per UUID + skin hash
  (memory, 512 entries) and send to a viewer once per connection (the minimap's delivered set). Re-render only when the skin hash changes.
- Owner: the composer lives in SkyyCore (the shared library, `tools/CORE-CONTRACT.md`) as bridge `head:fn:path` (`apply(Object[]{viewerUUID,
  subjectUUID})` -> String asset path, sends it to the viewer first; null = not ready, the page shows the class emblem instead and does NOT
  rebuild when it arrives unless H1b passed).
- Kit `SUI.head(id, size)` = an `AssetImage` 24 / 32 / 48 / 64 px in a thin frame. First uses: SkyyMenu Social > Players list + the Stats
  header (your head + name + level), then party / guild rosters, leaderboards, AH / Bazaar sellers (each its own later round).
- Pre-send at join (after `hud:assets:ready`): your own head + your party members' heads, so the first page never waits.

**Order:** R4 (after H1 passes; a new system = full round / ultracode).

---

## 8. Picture tiles on the SkyWynn Menu

**Skyy's words:** "i like the pictures they have on this menu." (UI-Ideas 2026-10-22 MENU TILE PICTURES; ref `menu-hub-hylterium.webp`: 5 x 3
big painted cards with a blue label bar and gold frame). Direction already written there: "one illustrated tile per hub area ... our own art
via the skywynn-art skill (never their pictures). Needs: the tile size in the Menu-Pattern grid + an AssetImage per tile."

**What exists today:** SkyyMenu 0.3.43 Home = the kit 1.7 hub page 1600 x 980, a **5 x 5 shortcut grid of 120 px slots** (600 x 600,
`SLOT30 = 120`, icon 88, `HG_COLS, HG_ROWS = 5, 5` - Skyy 10-16: "5x5 is big enough for the shortcuts."), side panels 456 each, default pins:
Teleport in the centre + the 7 hubs around it (`BUILTIN_HOME`, `build_skyymenu_0.3.43.py` 1402-1446, 2949-2996). Every tile wears an
`art/menu-icons` item icon today (`MENU_ICON_OF`). Shortcut keys: `hub:<hub>`, `tab:<hub>:<tab>`, `tile:<old key>`, `tp:*`, `warp:*`.

**Where pictures are proven (pages):** jar-shipped PNG as a **Group Background** (`PatchStyle TexturePath` under `Common/UI/Custom/...`,
markup without `@2x`, the client loads the @2x): kit Sky Window art (`Common/UI/Custom/SkyyKit/*@2x.png`, probes k1a / art1 / art2 PASS
2026-10-15), SkyyMenu hub tab icons (`Common/UI/Custom/SkyyHubTabs/*@2x.png`, 48 px behind the tab word, 0.3.30), radial map discs / lines
(SkyyTrees 0.5.0, M2 / M3 crisp), TownProbe #8 Pebble portrait. **AssetImage** on a page = M4 (not needed here: tiles are static per build).

**Feasibility: PROVEN.** T1 in the probe is a LOOK check only (crispness at 120 px, label bar readability, the gold frame on the sky theme).

**Design (art now, SkyyMenu 0.3.45 after Skyy approves the sheet)**
- Tile = the 120 x 120 slot: picture 116 x 116 (@2x 232 x 232 PNG, `Common/UI/Custom/SkyyMenu/Tiles/<key>@2x.png`), a 22 px label bar on its
  bottom (kit selected-bar blue `#4274a5` at 0.9, label 15 bold white, Secondary font like Menu-Pattern 3.2 "tile names"), a 2 px gold edge
  (`#E8A93B`) on hover / selected (kit hover style, no update from hover). The item icon goes away on tiles that have a picture; tiles without
  art keep today's icon (nothing breaks while art is missing).
- Grid stays 5 x 5 at 120 px (Skyy's lock); the picture replaces the icon only.
- Tile list (one picture per shortcut that can sit on Home; 38 + 3 teleports):
  - **Phase 1 - the default Home (8):** Teleport (centre: a sky-island portal), Character (an adventurer with skill icons around), Storage
    (bags + vault door), Market (Bazaar stalls + coins), Crafting (anvil + bench), World (floating islands + compass), Social (three players
    waving), Settings (gears + a key cap).
  - **Phase 2 - every hub tab (31 after merges):** Stats, Skills, Trees, Class, Pets, Void Charms, Collections, Profiles; Pocket, Supplies,
    Requip, Vault, Bank; Bazaar, Auctions, Merchants; Gear (Smithing), Recipes, Reforge, Upgrade, Multitool, Identify; Island, Explore,
    Quests; Players, Party, Guild; HUD, Menu layout, Mods, Server Setup (Teleport is phase 1). Skyy's own list adds Rebirth / Nexus and
    Zones - they get pictures when they become hub tabs (Rebirth opens from Trees' rail; Zones is admin).
  - **Teleport page (3):** My Island, Hub, Spawn (warps keep the generic warp icon).
- Art (skywynn-art skill, cloud draws, local reviews layout): a small painted scene in Hytale's chunky voxel style, our own composition, warm
  sky palette matching the Sky Window kit; one sheet per phase for Skyy; generator script + sheet in `research/cloud/menu-tiles-art/`; the
  final PNGs are OUR art (committable), not vanilla-derived.
- Size budget: 41 x ~40 KB = ~1.6 MB in the SkyyMenu jar, sent at join once (hash-cached).

**Order:** art phase 1 can start now (cloud); SkyyMenu 0.3.45 = R5 (after the sheet is approved; lean round - one mod, no saved data).

---

## 9. Zoom keeps the scroll position on radial pages

**Skyy's words:** "is is posible to add shift scroll for in and out?" (Style Guide 16) + the Radial spec's "their skills menu seems buggy" (ours
must be solid). Known limit logged with SkyyTrees 0.5.0 READY (docs/log 2026-10-22 16:10): "at 150 / 200 % a click rebuilds and the scroll
returns to top-left (needs probe M8: show / hide a picture + move inside a clip)".

**What exists today:** SkyyTrees 0.5.0 + SkyyRebirth 0.5.0 radial pages: zoom 100 / 150 / 200 % = the same layout pre-laid-out
(`skyymap.scaled()`) inside the 2-axis scroll box `map_scroll` (TopScrolling holding LeftScrolling; M7 PROVED wheel + bars both ways). Every
click (node select, Learn, rail) = a full `rebuild()` (one packet - HANDOFF 2) -> the client rebuilds the scroll box at offset 0,0.
**There is no scroll-offset property** in the UI language (166 vanilla `.ui` files: only `ScrollbarStyle` / `PanelScrollbarStyle`), so the
server can never SET a scroll position - it can only avoid destroying it.

**Feasibility: NEEDS PROBE M8** (+ the M4 / M5 retests it builds on).
- M8a "keep the scroll": at 200 %, scroll to the bottom-right, click nodes. The click answers with ONE `sendUpdate(b)` that (1) moves the halo
  (`b.setObject(#Sel.Anchor)` = M5), (2) swaps one node's state picture - BOTH ways tested: `.Visible` false on the old state picture + true on
  a pre-placed next-state picture, and `b.set(#N.AssetPath)` on an AssetImage disc (= M4), (3) sets the right-panel texts. PASS = the view
  does not jump, all three changes show.
- M8b "pan inside a clip" (the fallback): a plain 840 x 774 Group holding the 1680 x 1548 map Group; buttons Left / Right / Up / Down /
  Centre on selected (a '+' is no proven button text) move the map with ONE `b.setObject(#Map.Anchor, Left -x, Top -y)` per click. PASS = the
  map moves AND nothing of it is drawn outside the 840 x 774 box (clipping); "Rebuild" redraws at the same server-kept offset.
- M8c: the same Anchor move on the map INSIDE the scroll box (does the wheel still work after a server pan; does the box clip) - learn only.

**Design (kit 1.9 node-map methods; SkyyTrees 0.5.1 + SkyyRebirth 0.5.1)**
- **If M8a passes (expected):** node select / Learn / Respec on the open map = `sendUpdate` only (halo Anchor, changed node pictures, newly
  lit gold edges `.Visible` (all gold edges pre-placed, hidden), rail + panel texts); `rebuild()` only for a page / tree / zoom change.
  Which picture swap: AssetImage `AssetPath` if M4 passes (1 element per node), else pre-placed `.Visible` pairs for the states a click can
  reach (learnt k -> k + 1, ready -> learnt 1; ~2 extra elements per learnable node; worst page 740 -> ~1,000, M1c opened 1,602).
  Zoom change keeps rebuilding (top-left start) - unchanged.
- **If M8a fails but M8b passes:** drop the scroll box at 150 / 200 %; the map sits in a clip box with pan buttons in the right panel's zoom
  row ("Left / Right / Up / Down / Centre"), the offset kept per player + page in memory; zoom-in CENTRES on the selected node (a win over
  the scroll box, which cannot). The mouse wheel no longer pans (Q10).
- **If both fail:** keep today's behaviour + Focus view note; no further work.
- One packet per click stays (the kit's safety net in `handleDataEvent`).

**Order:** R2 (right after the probe - it fixes a live annoyance on pages Skyy is testing, TEST-CHECKLIST 229 / 230).

---

## 10. THE PROBE - SkyyUiProbe 0.8 (one session, ~5 minutes, op only)

Built by `tools/uiprobe_0_8_patch.py` from the SET pin `SkyyUiProbe/build_skyyuiprobe_0.7.1.py` (keeps M1-M7 + the 0.7.1 one-packet rule
and safety net; data-driven page text resources as 0.7.1). Commands: `/skyprobe tour` (all cases in order, a "Next case" button on every
page) and `/skyprobe <case>`; admin = `requirePermission` + `setPermissionGroups(new String[0])` (HANDOFF 3). No saved data, no config, no
items, **no HUD of its own** (one custom HUD per player - MultipleHUD exists in the Mods folder for that reason; a probe HUD would replace
SkyyHud's). Every case prints "PASS / FAIL / Skyy: look - <what>" to chat + log (the chat mirror copies it). Art generated at build time,
jar only. Smoke test before deploy (`python tools/smoke_test.py --jar SkyyUiProbe/SkyyUiProbe-0.8.jar`).

| # | Case | What it shows | Pass when (Skyy looks / clicks) | Feeds |
|---|---|---|---|---|
| 1 | **M4** map-assetimage (retest) | 0.7.1's three discs: AssetImage @2x path, AssetImage 1x path, Group Background control; "Next state" = `b.set(.AssetPath)` via sendUpdate | the disc picture swaps in place, no "Loading...", no missing-texture look | 9, 7 |
| 2 | **M5** map-anchor (retest) | click nodes: the halo moves by one Anchor update | halo jumps to each clicked node, nothing else redraws | 9 |
| 3 | **M6** map-tooltip (retest) | 3 discs with TooltipText | hover shows name + rank; Esc with a tooltip open is safe | 6, 9 |
| 4 | **M8a** keep-scroll | the Gathering map at 200 % in the 2-axis scroll box; nodes answer with sendUpdate only (halo + picture swap both ways + panel text) | after scrolling to the far bottom-right and clicking 3 nodes the view did NOT jump; halo, picture and text changed | 9 |
| 5 | **M8b** clip-pan | the 200 % map in a plain 840 x 774 Group; Left / Right / Up / Down / Centre / Rebuild buttons | the map moves per click; nothing drawn outside the box; Rebuild keeps the offset | 9 |
| 6 | **M8c** pan-in-scroll (learn) | the M8b Anchor move inside the scroll box | report: wheel still pans after a server pan? box clips? | 9 |
| 7 | **H1a** head-before-open | a picture generated at run time (your name's initials on a coloured square, 64 px) sent BEFORE the page opens, shown in an AssetImage | the picture shows on the page | 7 |
| 8 | **H1b** head-while-open | button "Send a new picture": a NEW content-named PNG is sent while the page is open, then ONE sendUpdate sets the AssetPath | the new picture shows, the page does not flicker / reload, no "Loading..." | 7 |
| 9 | **H1c** your head (draft) | your PlayerSkin's 20 part ids dumped to chat + log; a draft 64 px head composed from build-time front views of the installed haircuts / faces / accessories, tinted at run time | Skyy: "is that me, hair included?" (screenshot) | 7 |
| 10 | **D1** dialogue bar | transparent 1600 x 980 root + the 1100 x 190 bar at the bottom ("Pebble", 3 test lines, Skip / Next / Accept / Close) | the world is visible above (no dark screen), Skip / Next work, each click answers once, Esc closes | 5 |
| 11 | **T1** picture tiles | 4 draft tiles at 120 px (@2x, label bar, gold hover edge) + 1 at 150 px | crisp, label readable, feels like the ref (screenshot) | 8 |
| 12 | **K1** key hints (look) | the page tells Skyy to close it and look bottom-right with a class + 2 abilities equipped | vanilla boxes show Mouse 5 / Q / E with OUR class icons (screenshot) | 1 |
| 13 | **F1** vanilla feed | button "Close + run feed test": 1 s after the page closes, 7 notifications to you: skill XP with a text bar, kill (gold name), Fortune (item icon x3), heal, collection progress, the 4 styles (Default / Success / Warning / Danger) | readable, colours show, stacks with pickups bottom-right (screenshot) | 3 |
| 14 | **F2** feed tag | 5 "+10 XP" notifications with the SAME tag, 300 ms apart | report: ONE card updating or FIVE cards? | 3 |
| 15 | **G1** ground arrow | button "Close + run arrow test": for 20 s, every 1 s, 3 particle variants 4 blocks ahead pointing at world spawn (A flat `RotationInfluence None` + yaw, B upright `BillboardY`, C a 6-dot trail), you only; chat line every 5 s with the distance | Skyy: which reads best, does A lie flat and turn toward the target, does it tilt on slopes (screenshot / words) | 4 |

Order in the tour = page cases 1-11 (each one click to the next), then 12-15 after the page closes (12 is a look, 13-15 run on buttons of the
last page; each button closes the page FIRST and starts its effect on the next tick - never close-then-open). Timing ~5 minutes.

**Results ->** `docs/log/2026-10.md` (one line per case), `skyyui.PROBED` keys: `map-assetimage` (M4), `map-anchor` (M5), `tooltip` (M6),
`map-keepscroll` (M8a), `map-clip` (M8b), `asset-push-page` (H1a + H1b), `dialogue-bar` (D1), `vanilla-feed` (F1, + `vanilla-feed-tag` if F2
merges); ground-arrow variant into the SkyyQuests round notes. Then RETIRE SkyyUiProbe (move to `RETIRED` in `tools/deploy_set.py`).

**Builder notes (probe):** the M8 pages reuse 0.7.1's Gathering layout at 200 % (`skyymap.scaled()` now exists - use `tools/skyymap.py`
instead of the copied layout); the H1c front-view renderer is the first draft of `tools/skyyheads.py` (pure Python, output into the jar only);
G1's particle files + arrow texture follow the path layout of an existing shipped particle (e.g. SkyySkills 0.4.42's sparkle) and its
`spawnParticleEffect(String, Vector3dc, Rotation3f, List, ComponentAccessor)` call is signature-asserted at build time like
`build_skyyquests_0.4.2.py` 1248; F1 / F2 use the `NotificationUtil` overload with the trailing tag (assert its signature).
UNVERIFIED for the builder: the exact particle texture path rule for a jar-shipped particle; Rotation3f axis order; whether
`ParticleRotateWithSpawner` honours the spawn rotation.

---

## 11. Round plan after the probe

| Round | Mods (from the SET pin) | Content | Size (PROJECT-RULES 4) | Needs |
|---|---|---|---|---|
| **R1** | SkyyHud 0.3.35 + SkyyMenu 0.3.44 (+ SkyyQuests 0.4.3's `/quests widget` only if R3 is far off - else in R3) | Keys widget (1); quest tracker fold + the double-tap-crouch choice + one-time migration (2); Vanilla feed destination + card formats + burst cap (3); Stats "by source" table (6) | **full round** (2 mods, a setting migration, permissions on a sub-command) | F1 / F2 for the feed default (the rest is proven) |
| **R2** | kit 1.9 (`tools/skyyui.py` node-map methods) + SkyyTrees 0.5.1 + SkyyRebirth 0.5.1 | no-rebuild clicks (M8a) or clip + pan (M8b) (9); tooltips on nodes if M6 passes | full round (kit + 2 mods), `--simplify 1` | M4, M5, M8a / M8b |
| **R3** | SkyyQuests 0.4.3 (+ SkyyHud 0.3.36 objective label) | ground arrow (4), dialogue bar (5), `/quests widget hide / show / fold` (2) | full round (quests, NPC flow, a Hud bump) | G1, D1 |
| **R4** | `tools/skyyheads.py` + kit 1.9 `SUI.head` + SkyyCore 1.0.2 (`head:fn:path`) + SkyyMenu 0.3.45 (Players list + Stats header) | self-built heads (7) | **ultracode** (new system, several mods) - start with the PROJECT-RULES 2 survey (CurseForge "player head" / "avatar" mods; GlymeraHeads already skipped, RPG Leveling = web render, HyUI = slot + rebuild) | H1a-c |
| **R5** | SkyyMenu 0.3.45 / 0.3.46 | picture tiles phase 1, then phase 2 (8) | lean (one mod, no saved data) | art sheets approved (cloud starts phase 1 now) |

Deploy together: SkyyHud 0.3.35 + SkyyMenu 0.3.44 (Menu calls `hud:fn:questFold`; an older Hud = the gesture opens the Menu as before). Kit
1.9 changes rebuild only the mods named in that round. Each round updates `research/Menu-Pattern.md` / Style Guide (dialogue bar, key cap, head,
tile, feed card formats) the same day (PROJECT-RULES 5 signposts).

---

## 12. Questions for Skyy (default in [brackets])

1. Now that Left Alt opens the Menu, should **double-tap crouch fold the quest tracker** instead? ["Fold quest tracker" by default; "Open the
   menu" and "Nothing" stay choices in /settings]
2. Hiding the quest widget: **`/quests widget hide / show / fold`** (no new `/sidebar` word)? [yes]
3. Move our feed cards (XP, kills, Fortune, heals, collection progress) **into the vanilla feed bottom-right** and make that the default? [yes
   if probe F1 looks good; our bottom-left box stays a choice in Settings > Messages]
4. Guide on the ground: **arrow, particle trail, or both**? [the arrow, every 1 s, 4 blocks ahead, only farther than 12 blocks and in the same
   world; the trail stays a later option]
5. The "Objective / 84 blocks" text cannot float in the world for one player only (the game shows world labels to everyone). Put it **on the
   HUD above the hotbar while the arrow shows**? [yes; the Quest Tracker keeps its own arrow + distance]
6. Quest NPC talk as a **bottom bar** (speaker, line, Skip / Next, line n / m) instead of today's centred window - and **no camera move** on the
   NPC? [bottom bar for every quest NPC; Skip jumps to the last page so Accept is never skipped; no camera move]
7. Stats "by source" columns **Base / Gear / Charms / Pets / Trees / Class / Total** - skill-level bonuses in Base and the Rebirth Nexus in
   Trees? [yes; exact Skills / Rebirth columns only if you want them later]
8. **Self-built player heads** from your skin (hair included, drawn by the server from the game's own textures, no web service) - where
   first? [Players list + your Stats header, then party / guild / leaderboards]
9. Menu **picture tiles**: keep the 5 x 5 grid at 120 px with the picture filling the slot + a blue label bar, phase 1 = the 8 default Home
   tiles? [yes; our own painted scenes via the skywynn-art skill, one sheet per phase for your OK]
10. Zoomed tree pages: if the probe shows the view can't stay put on a click, OK to **pan with buttons** (Left / Right / Up / Down / Centre)
    at 150 / 200 % instead of the mouse wheel - zoom-in then centres on the selected node? [yes]
11. The hotbar hint shows **"ALT - Menu"** even if you rebind Walk (the server can't see binds)? [yes; Settings > HUD can hide it]

---

## 13. UNVERIFIED (the probe or the first build decides)

1. `gear:stats:<uuid>` already includes Charms / Pets / Trees (item 6 column maths) - read SkyyGear GearTick before building.
2. `class:lastcast:<uuid>` exists for the crouch-cast guard (item 2) - else the guard is dropped.
3. Vanilla feed: line length limit, how many cards stack, merge by `tag` (F1 / F2).
4. Particle orientation / Rotation3f / per-viewer arrow look (G1).
5. Custom page over the world without a dim (D1).
6. AssetImage + jar texture / runtime asset on a PAGE, push while open (M4, H1a, H1b).
7. Front-view head render readable at 64 px; the skin part id / colour string format (H1c dump).
8. Scroll kept on sendUpdate; Group clipping (M8a / M8b / M8c).
9. The vanilla Abilities HUD really shows our class icons on Skyy's client (K1).
