# SKYWYNN - HANDOFF
*Short version since 2026-10-05 (docs consolidation). Owner: Skyy (GitHub SkyyPlayz, they/them). This file = the current versions, the deploy
rules and the hard-won build rules. Where we are + what is next: `RESUME.md`. Where everything else lives: `INDEX.md`.*

## 1. Versions = `tools/deploy_set.py` SET (all deployed together; last deploy 2026-10-04 00:46, backup `deploy-20261004-0046`)

| Mod | Version | What it does |
|---|---|---|
| SkyyHud | 0.3.13 | HUD widgets + Lunar-style editor (move / scale / toggle), skills + combat widgets |
| SkyySacks | 0.7.12 | Magic Bags (pocket dimension): auto-collect + refill, /sacks, /craft, bags count in bench + inventory crafting |
| SkyyCoins | 0.1.5 | coin purse, /pay, death penalty (merges into SkyyEconomy later) |
| SkyyCollections | 0.2.5 | collections, tiers, recipe unlocks (coins never buy tiers) |
| SkyyParty | 0.1.6 | parties (feeds the HUD party widget) |
| SkyyBank | 0.1.6 | bank + interest |
| SkyyIslands | 0.5.5 | private islands, co-op, visitors, island settings, /hub |
| SkyyBazaar | 0.1.3 | Bazaar market (a tab per bag type + Smithing) |
| SkyyGear | 0.2.2 | gear rarity, item levels, identify, reforge, tooltips, crit popup |
| SkyySkills | 0.4.15 | skills + class weapon skills, XP curves, Mana, Acrobatics |
| SkyyAccessories | 0.5.4 | Accessory Bag, booster accessories, Lantern |
| SkyyClasses | 0.1.11 | class pick, class kits, Priest heal |
| SkyyMenu | 0.3.6 | SkyWynn Menu, player Settings, Server Setup (admin) |
| SkyyEssentials | 0.1.7 | /tpa, /trade and the few commands vanilla lacks |
| SkyyProfiles | 0.1.5 | profiles = full saves (default cap 6), delete + 6 h undo |
| SkyyCooking | 0.1.4 | Cooking dishes + food Grade |
| SkyyTrees | 0.3.1 | skill trees (gathering, Acrobatics, Exploration, Alchemy, Smithing; class trees OFF) |
| SkyyExploration | 0.2.2 | Exploration skill, spots, island checklist |
| SkyyGuilds | 0.1.6 | guilds + guild bank |
| SkyyVault | 0.1.5 | vault pages |
| SkyyAuctions | 0.1.2 | auction house (buy-it-now) |
| SkyyRanks | 0.1.1 | ranks + permissions made in game |
| SkyyUiProbe | 0.4 | dev / test probes, op only (retire later) |
| SkyyMobs | 0.1.3 | mob levels + difficulty |
| SkyyWorldGen | 0.1 | Zone 1 test island (/zone 1, admin) |
| SkyyArmory | 0.1 | our own weapons: metal wands + the staff ladder |
| third-party (`PACK.md`) | - | More Crossbow Tiers (Serj), Saplings From Trees (Helios); SkyyRolls is RETIRED |

Every version's notes: `docs/handoff/versions-history.md`. Every build / deploy / test: `docs/log/<YYYY-MM>.md`.

**Deploy rules** (PROJECT-RULES section 3 is the procedure): `python tools/backup_deploy.py`, then `python tools/deploy_set.py --yes` with the
game closed - the only deploy path. ROLLBACK FLOORS (each with its reason in the comments of `tools/deploy_set.py` - read them before
any rollback): SkyyProfiles 0.1.5 once a profile was deleted; SkyyTrees 0.3 once it saved a player file; SkyyGear 0.2 (unless the config
History copy is restored first); SkyySacks 0.7.7; SkyySkills 0.4.6 (and SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 roll back
together); SkyyCollections 0.2.3 (unless rewards-0.2.properties is restored); never SkyyIslands 0.5 (security hole). HyperEssentials stays DISABLED.

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
