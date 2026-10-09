# SKYWYNN - HANDOFF
*Short version since 2026-10-05 (docs consolidation). Owner: Skyy (GitHub SkyyPlayz, they/them). This file = the current versions, the deploy
rules and the hard-won build rules. Where we are + what is next: `RESUME.md`. Where everything else lives: `INDEX.md`.*

## 1. Versions = `tools/deploy_set.py` SET (all deployed together; last deploy 2026-10-04 00:46, backup `deploy-20261004-0046`)

| Mod | Version | What it does |
|---|---|---|
| SkyyHud | 0.3.17 | HUD widgets + Lunar-style editor (move / scale / toggle), skills + combat widgets; minimap widget (needs BetterMap); moves the Dynamic Seasons widget; minimap island / arrow / spot fixes |
| SkyySacks | 0.7.16 | Magic Bags (pocket dimension): auto-collect + refill, /sacks, /craft, bags count in bench + inventory crafting; take bridge for other mods |
| SkyyCoins | 0.1.5 | coin purse, /pay, death penalty (merges into SkyyEconomy later) |
| SkyyCollections | 0.2.8 | collections, tiers, recipe unlocks (coins never buy tiers); Lantern recipes at Tree Sap 1/3/5/8 |
| SkyyParty | 0.1.7 | parties (feeds the HUD party widget); TPA / Accept TPA buttons |
| SkyyBank | 0.1.7 | bank + interest; interest once a day, account brackets 2/1/0.5% |
| SkyyIslands | 0.5.5 | private islands, co-op, visitors, island settings, /hub |
| SkyyBazaar | 0.1.6 | Bazaar market (a tab per bag type + Smithing); progression prices x2 per tier; sells from Magic Bags, Hytale stack buttons |
| SkyyGear | 0.2.13 | gear rarity, item levels, identify, reforge, tooltips, crit popup, Smithing XP for crafted gear; traversal tooltip words; level curves, Reforge level-up (+6), vanilla armor box hidden; weapon speed tiers (weapons only); Charged trust for the _Wynn crossbows |
| SkyySkills | 0.4.27 | skills + class weapon skills, XP curves (Mining has its own list), Mana, Acrobatics; kill XP by mob level, Mana regen per class level; 8-way Dodge Roll; dodge move gate, no Acro XP cap; roll on a sprint-key tap |
| SkyyAccessories | 0.5.9 | Accessory Bag, booster accessories, Lantern (recipes known via SkyyCollections) |
| SkyyClasses | 0.1.15 | class pick, class kits, Priest heal; class:fn:heal (heal orb, party more) |
| SkyyMenu | 0.3.13 | SkyWynn Menu, player Settings, Server Setup (admin) |
| SkyyEssentials | 0.1.9 | /tpa, /trade and the few commands vanilla lacks; ess:fn:tpa bridge |
| SkyyProfiles | 0.1.9 | profiles = full saves (default cap 6), delete + 6 h undo |
| SkyyCooking | 0.1.6 | Cooking dishes + food Grade; XP by craft difficulty |
| SkyyTrees | 0.3.5 | skill trees (gathering, Acrobatics, Exploration, Alchemy, Smithing; class trees ON) |
| SkyyExploration | 0.2.5 | Exploration skill, spots, island checklist |
| SkyyGuilds | 0.1.6 | guilds + guild bank |
| SkyyVault | 0.1.5 | vault pages |
| SkyyAuctions | 0.1.3 | auction house (buy-it-now) |
| SkyyRanks | 0.1.1 | ranks + permissions made in game |
| SkyyUiProbe | 0.4 | dev / test probes, op only (retire later) |
| SkyyFishing | 0.1.2 | our fishing, stage 1: Fishing Bench (Parts / Rig / Fillet and Sell), rods + reels T0-T2, parts I-II, cast / bite / fight HUD, Zone 1 fish (HyFishing stays until stage 2) |
| SkyyMerchants | 0.1 | roaming merchants (one per zone, move 20 min, rumours, special-weapon shop); floor: switch part.merchants off before removing |
| SkyyPets | - | slot pets phase 1: per-profile pet records + ledger, pet slot (full buffs) + summon slot (50%), pet XP + levels, /pets page, /petadmin, starter Rabbit, 30 launch kinds |
| SkyyTownProbe | 0.1 | Zone 1 town probe, op only, test island (run /townprobe undo until 'Nothing to undo', then remove) |
| SkyyKeyProbe | 0.2 | key probe, op only: /keyprobe give, press keys, /keyprobe report (remove after Skyy's test) |
| SkyyMobs | 0.1.5 | mob levels + difficulty; level curves + level gap (mob:fn:info) |
| SkyyWorldGen | 0.1 | Zone 1 test island (/zone 1, admin) |
| SkyyArmory | 0.1.14 | our own weapons: metal wands + the staff ladder; staff blink + trail, wand hop / burst / heal orb, pierce; crossbow Grapple Bolt; bow leap + blast, Copper / Onyxium crossbows; blink 16 + floorCheck 0 defaults |
| third-party (`PACK.md`) | - | More Crossbow Tiers (Serj), Saplings From Trees (Helios); SkyyRolls is RETIRED |

Every version's notes: `docs/handoff/versions-history.md`. Every build / deploy / test: `docs/log/<YYYY-MM>.md`.

**Deploy rules** (PROJECT-RULES section 3 is the procedure): `python tools/backup_deploy.py`, then `python tools/deploy_set.py --yes` with the
game closed - the only deploy path. `deploy_set.py` refuses a SET that splits SkyyArmory from SkyySkills 0.4.15+ / SkyyClasses 0.1.11+.
ROLLBACK FLOORS + STEPS (each with its reason in the comments of `tools/deploy_set.py` - read them before any rollback):
- Floors: SkyyProfiles 0.1.5 once a profile was deleted; SkyyTrees 0.3 once it saved a player file; SkyyGear 0.2 (unless the config
  History copy 'before the 0.2 level bands' is restored first); SkyySacks 0.7.7; SkyyTrees 0.2.4; SkyyCollections 0.2.3 (unless
  rewards-0.2.properties is restored); SkyySkills 0.4.6 (switch Base Mana + Overall Level OFF and let players log in once first);
  never SkyyIslands 0.5 (security hole).
- SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 deploy and roll back TOGETHER: before SkyySkills goes below 0.4.15 switch
  Base Mana off and let players log in once; rolling SkyyArmory back = out of SET, into RETIRED, and SkyySkills back to 0.4.14 in the
  same deploy.
- Removing SkyyWorldGen after /zone 1 ran: stop the server and delete `Saves/HUD mod/universe/worlds/skywynn_z1` FIRST (else void is
  saved into the island), then out of SET, into RETIRED.
- Removing SkyyMobs: out of SET, into RETIRED (to strip level plates first: Server Setup > Mobs > Never level these = `*`, reload chunks).
- SkyyAuctions back to 0.1.1: restore `48h:1200` in its config.properties by hand first.
- HyperEssentials stays DISABLED (it crashes the world on any player death) unless a newer release exists.

## 2. THE TWO RULES THAT COST 30 BUILDS (READ BEFORE WRITING ANY UI)

0. **UI LOOK = VANILLA (Skyy, 2026-09-28):** every UI added to the game (pages, menus, HUD widgets, popups, item tooltips) must look and feel as close to the original Hytale UI as possible - vanilla colours, fonts, panel frames, button styles, spacing and sounds, copied from the game's own UI assets rather than our own custom styling. Before styling a page, look up the vanilla
   look in Assets.zip (the client UI documents and their style values) and mirror it; our dark-blue custom panels are the old style.

1. **Element IDs must not contain underscores.** `#w_coords_t` → client says "Failed to parse or resolve document" (inline) or "Selected element not found" (file). 26,850 IDs across every reference mod and vanilla: zero underscores. Use `#SkyyWCoordsTxt`, `#SkyySRow0`, `#SkyyEInfoDir`.
2. **Never ship `.ui` files; build every HUD/page inline.** On Skyy's client a `.ui` document is only resolvable when it was delivered over the wire during the *first* world load of a client process; anything already in the disk cache is "Could not find document" forever. Pattern (copied from EndlessLeveling `DungeonQueueHud`):
   ```java
   b.appendInline((String) null, "Group #SkyyRoot { Anchor: (Full: 0); }");
   b.appendInline("#SkyyRoot", "Group #SkyyWCoords { Anchor: (Top: 8, Left: 8, Width: 180, Height: 26); Background: #0b1524(0.72); Label #SkyyWCoordsTxt { Anchor: (Full: 0); Text: \"\"; Style: (FontSize: 12, RenderBold: true, TextColor: #eaf6ff, HorizontalAlignment: Center, VerticalAlignment: Center); } }");
   b.set("#SkyyWCoordsTxt.Text", "X 1 Y 2 Z 3");
   ```
   Buttons are `TextButton #Id { Anchor: (...); Text: "..."; Style: TextButtonStyle(Default: (Background: #.., LabelStyle: (...)), Hovered: (...), Pressed: (...)); }` bound with `ev.addEventBinding(CustomUIEventBindingType.Activating, "#Id", EventData.of("a", "payload"))`; `handleDataEvent(ref, store, data)` receives JSON containing the payload (match with `data.indexOf("payload\"")`).
   Commas/colons inside inline `Text` are NOT proven to break anything (the crashes blamed on them were an `Anchow:` typo in the Sacks page); the Sacks page sanitizes `, : ; { } "` anyway. When an inline append fails, dump the page class's string constants first and read them for typos; `set("#Id.Text", v)` is safe for anything.
   **Never send a page update from a MouseEntered/MouseExited handler** — the client process crashes ("Collection was modified"). Click handlers may rebuild()/sendUpdate freely.
   **Never put an ItemStack that may carry METADATA into an `ItemGridSlot`** (2026-09-25, SkyyAuctions 0.1 disconnect): the UI codec sends
   metadata as a JSON object and the client fails with "Failed to convert JSON value (Object) to specified type (ClientItemMetadata)" and
   disconnects. Use `new ItemGridSlot(new ItemStack(s.getItemId(), s.getQuantity()))` and show rolls/grades as text or via setName/setDescription.
   Because nothing depends on `.ui` files any more, **Reconnect is enough after a redeploy** (no client restart).

**Data folders are stable across versions**: every mod stores under `<world>/mods/Skyy_<Mod>/` via `getDataDirectory().resolveSibling("Skyy_<Mod>")` (the default dir carries the version and would orphan data). **Cross-mod data** (no dependency): a JVM-global map in `System.getProperties().get("skyy.bridge")`; Coins writes `coins:<uuid>` -> Long, the HUD Coins widget reads it. **Page roots** are a Group with only Width/Height in the Anchor (the page system centres it).

Other proven facts: HUD attach = `new HudMain(pr).show()` on `PlayerReadyEvent` (0.2.4 delays 1.5s + checks the WorldMap channel is writable, like EndlessLeveling; harmless, keep). Pages: `player.getPageManager().openCustomPage(ref, store, page)`; `CustomUIPage.build(...)` must be **public**. Commands: `AbstractPlayerCommand(name, desc)`, `withOptionalArg/withRequiredArg(name, desc, ArgTypes.X)` (arg classes live in `command.system.arguments.system`), `ctx.provided(arg)`, `ctx.get(arg)`, `requirePermission("node")`, `addAliases(String[])`. Plugin lifecycle: `setup()` and `protected void shutdown()` (call `super.shutdown()`). Inventory: `ItemContainer.removeItemStackFromSlot(slot, qty)` → `ItemStackSlotTransaction.succeeded()/getRemainder()`; `addItemStack(stack)` → `ItemStackTransaction`. Disconnect: `PlayerDisconnectEvent.getPlayerRef()` returns `PlayerRef`. Right-click item -> page: item JSON `"Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "X"}}]}}` + `OpenCustomUIInteraction.registerSimple(plugin, Plugin.class, "X", java.util.function.Function)` (`PlayerInteractEvent` is dead code; `PlayerMouseButtonEvent` is the manual alternative).

## 3. COMMAND RULES (every Skyy mod; `tools/ci/lint.py` checks them)

**COMMAND RULES (verified 2026-09-23, apply to EVERY Skyy mod):**
1. Auto permission nodes: any command without requirePermission() gets '<group>.<name>.command.<cmd>' (version inside the node), which
   ordinary players (hytale:Adventurer) do not have -> player commands need setPermissionGroups(new String[] { "hytale:Adventurer" }) in the
   constructor of the command AND of every subcommand/usage variant (SkyyEssentials pattern). Never on admin commands (requirePermission).
2. Optional args are not positional: token count must equal the required-arg count (acceptCall0). Every documented positional form needs a
   usage variant (description-only ctor + withRequiredArg, parent addUsageVariant) or a subcommand with withRequiredArg.

## Where the rest of the old HANDOFF went (2026-10-05, word for word)
| Old part | Now |
|---|---|
| Gear locks + section 1 (goal, locked decisions, design locks, focus calls) | `docs/handoff/design-locks.md` |
| Section 3 (versions with every step's notes) | `docs/handoff/versions-history.md` |
| Section 3 rest (verified lists, repository, toolchain, 09-23 builds) + section 4 (old next steps) | `docs/handoff/state-2026-09.md` |
| Section 5 (design + build notes) | `docs/handoff/design-notes-2026-09.md` |
| Section 6 running log | `docs/log/2026-09.md`, `docs/log/2026-10.md` (new lines go at the end of the newest month) |
