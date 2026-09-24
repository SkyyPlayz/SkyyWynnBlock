# SKYWYNN — HANDOFF
*Rewritten 2026-09-22 21:00, restructured 2026-09-23 20:45 (session 4): section 3 = current state (always current), section 6 = running log (append-only). Read this first; every other doc in this folder is detail. Owner: Skyy (skylordplayz@gmail.com).*

---

## 1. THE GOAL

Build **SkyWynn**: a public Hytale server that fuses Hypixel SkyBlock (economy, sacks, collections, bazaar/AH, minions, islands, slayers) with Wynncraft (classes, quests, map, party) — plus a Lunar/Wynntils-style QoL layer (customizable HUD, map+minimap, party widget, quest nav).

It is built as a **family of standalone mods** ("Skyy*" mods). Each one must:
- Work alone with **zero external dependencies** (bundle anything needed into the jar — never "requires HyUI").
- Carry its version at the **start of the display name**: `"0.2.4 SkyyHud"` (so they sort together in the mod list).
- Be designed to **integrate with the future SkyWynn systems** (map, party, quests, coins, collections) even if those don't exist yet.
- Be **clean-room our own code**. Existing mods are reference only — but **Skyy's rule: "never build new when you can steal what already works"**: find a working mod in the Mods folder that does the thing and mirror its exact calls.

### Locked decisions (Skyy) — don't re-ask
| Topic | Decision |
|---|---|
| Server type | Public |
| World | Hand-built (team later); build all mods first |
| Classes | Archer / Warrior / Mage on Hytale ability keys; build on the coming **rune system** (Chapter 1) — WAIT tier |
| Death penalty | Lose a % of coins. **Editable in-game**: `/deathpenalty 5%` (fixed) or `/deathpenalty 5%-10%` (random in range) |
| Name | "SkyWynn" is a placeholder |
| UI build freeze | No inventory-screen work until the **NoesisGUI rework** ships; then all facility buttons live inside the inventory screen |
| HUD | Lunar-style editor for OUR widgets (move/scale/toggle), layout export/import codes; rebindable edit hotkey (engine-limited today) |
| Party widget | Name + HP + stamina + mana per member; same party system feeds map positions |
| Map | ONE renderer for full map + minimap, party + quest layers. **Not built yet — design for integration only** |
| Quest nav | Compass marker default; on-demand beacon/particle trail toggle |
| Voiceovers | Later |
| Hotkeys (F5/F6/F7 recipe/AH/uses) | Wait for engine keybind support; rebindable normal keys |
| Research | Always use cheap models (sonnet) for research/review agents |
| **Bench accessories** (Skyy 2026-09-23) | Inventory crafting = OUR crafting page (`/craft`, also a Craft tab in `/pd`): shows the basic Fieldcraft recipes by default; carrying a **bench accessory** (one item per bench: Workbench, Forge, ...; later lives in the SkyBlock-style accessory bag) unlocks that bench's full recipe list in the page. Materials are counted from inventory + bags; the engine's `CraftingManager.craftItem` consumes and gives output. Vanilla pocket crafting stays vanilla (client-gated, cannot see bags). **Collections unlock recipes** that also appear in this page (SkyyCollections publishes `coll:recipes:<uuid>` = comma-separated recipe ids through the JVM bridge). End state (Skyy): everything is inventory crafting through this page, no benches needed |
| Multiplayer | Everything per player (Skyy 2026-09-23): pools, bag pages, sweep exemptions, crafting feed, coins, layouts are keyed by player UUID; a player may only craft from their own pocket dimension. Verify with 2 accounts (TEST-CHECKLIST) |
| **Magic Bags** (was "sacks", 2026-09-22 late) | Items are "Magic Bags" opening onto the player's **pocket dimension** (flavor text). Strict access: you must carry a bag of the category to open/withdraw it; the pool itself persists per player (never lost). Bag rarity caps **each item** (Small 640 / Medium 2,240 / Large 20,160), best bag carried counts; works from storage, hotbar or backpack. `/sacks` = `/pd` = `/bags`. Next: workbench + inventory crafting pull from the bags |

Full rationale: `SkyWynn-Decisions.md` (rows 10.17–10.28 locked), `SkyWynn-Master-Plan.md`, `SkyWynn-QoL-Catalog.md`, `SkyWynn-Mod-Roster.md` (28 mods, tiers, build order).

---

## 2. THE TWO RULES THAT COST 30 BUILDS (READ BEFORE WRITING ANY UI)

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
   Because nothing depends on `.ui` files any more, **Reconnect is enough after a redeploy** (no client restart).

**Data folders are stable across versions**: every mod stores under `<world>/mods/Skyy_<Mod>/` via `getDataDirectory().resolveSibling("Skyy_<Mod>")` (the default dir carries the version and would orphan data). **Cross-mod data** (no dependency): a JVM-global map in `System.getProperties().get("skyy.bridge")`; Coins writes `coins:<uuid>` -> Long, the HUD Coins widget reads it. **Page roots** are a Group with only Width/Height in the Anchor (the page system centres it).

Other proven facts: HUD attach = `new HudMain(pr).show()` on `PlayerReadyEvent` (0.2.4 delays 1.5s + checks the WorldMap channel is writable, like EndlessLeveling; harmless, keep). Pages: `player.getPageManager().openCustomPage(ref, store, page)`; `CustomUIPage.build(...)` must be **public**. Commands: `AbstractPlayerCommand(name, desc)`, `withOptionalArg/withRequiredArg(name, desc, ArgTypes.X)` (arg classes live in `command.system.arguments.system`), `ctx.provided(arg)`, `ctx.get(arg)`, `requirePermission("node")`, `addAliases(String[])`. Plugin lifecycle: `setup()` and `protected void shutdown()` (call `super.shutdown()`). Inventory: `ItemContainer.removeItemStackFromSlot(slot, qty)` → `ItemStackSlotTransaction.succeeded()/getRemainder()`; `addItemStack(stack)` → `ItemStackTransaction`. Disconnect: `PlayerDisconnectEvent.getPlayerRef()` returns `PlayerRef`. Right-click item -> page: item JSON `"Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "X"}}]}}` + `OpenCustomUIInteraction.registerSimple(plugin, Plugin.class, "X", java.util.function.Function)` (`PlayerInteractEvent` is dead code; `PlayerMouseButtonEvent` is the manual alternative).

---

## 3. CURRENT STATE (always kept current - last update 2026-09-23 20:45)

### Versions: live in the "HUD mod" test world vs newest built
| Mod | Live (enabled in Saves/HUD mod/config.json) | Newest built, NOT deployed |
|---|---|---|
| SkyyHud | 0.3.5 | 0.3.6 (Adventurer perms + /skyyhud export/import/reset/profile subcommands) |
| SkyySacks | 0.6.8 | 0.7.1 (Crafting/Alchemy/Furnace/Tannery tabs, timed Furnace+Tannery page, perms) |
| SkyyCoins | 0.1.3 | 0.1.4 (perms, /deathpenalty <spec>) |
| SkyyCollections | 0.1.3 | 0.1.4 (perms, /collections unlocks, reload) |
| SkyyParty | 0.1.1 | 0.1.2 (perms) |
| SkyyBank | 0.1 | 0.1.1 (perms, /bank deposit/withdraw <amt>) |
| SkyyBazaar | 0.1 | 0.1.1 (perms, /bazaaradmin subcommands) |
| SkyyEssentials | 0.1 | - (tpa/msg/reply/fly; already had perms) |
| SkyyRolls | 0.1 | 0.1.1 (admin-only spike, positional args) |
| SkyySkills | 0.1 | 0.3 (Acrobatics, cap 100, Stats page, perks, class combat) - 0.2 superseded |
| SkyyAccessories | 0.2 | 0.4 (5 rarities, % talismans, OMNI, shared movement protocol) - 0.3 superseded |
| SkyyIslands | 0.4.2 | 0.4.3 (perms, /island info/visit/invite) |
| SkyyClasses | not deployed | 0.1.1 (NEW: Archer/Warrior/Assassin/Berserker/Mage, weapon lock) |
| SkyyMenu | not deployed | 0.1.1 (NEW: /skymenu + menu item, teleports/warps, mods list) |
HyperEssentials 0.1.0 is DISABLED (crashes the world on any player death - built for an older API).
**Deploy rule (Skyy):** build without --deploy, list the changes, deploy only after Skyy OKs.
**Deploy together:** SkyySkills 0.3 + SkyyAccessories 0.4 + SkyyClasses 0.1.1 (shared movement protocol + class bridge).

### Verified in game by Skyy (2026-09-23)
- SkyyHud: editor live previews + screen-edge frame (0.3.3), Widgets and per-widget Settings pages ("beautiful").
- SkyyIslands: /island creates + teleports, /sethub, /hub. Black grass traced to biome tint (fix in 0.4.2, not yet re-checked).
- SkyyAccessories 0.2: bag, equip/unequip, tiered bench accessories -> tiered /craft tabs.
- SkyySacks: crafting outputs go to the inventory (0.6.5; earlier builds hid them in the backpack section), wrapped tabs, bigger pages.
- SkyySkills 0.1: /skills page renders. HyperEssentials death crash diagnosed and removed.

### Open decisions for Skyy
1. Deploy approval for the built set above.
2. Endurance/Intelligence talismans: % of vanilla base (Stamina 10, Mana 0) is nearly useless - make them flat until armor adds base stats?
3. Accessory power: six [SKYY?] questions in SkyyAccessories-Plan.md (AP values, bench accessories count?, class crystals, slot sources/prices, Mage crystal).

### Repository
Git repo in this folder, branch main, pushed to https://github.com/SkyyPlayz/SkyyWynnBlock (remote origin). WARNING 2026-09-23 20:58: the repo was created PUBLIC - Skyy asked to switch it to Private (Settings > Danger Zone); verify with an anonymous API call (404 = private) before pushing more.
Commits use the GitHub noreply address 73867804+SkyyPlayz@users.noreply.github.com (repo-local git config) because Skyy's account blocks
publishing his Gmail. Commit + push after each meaningful change (git add -A; git commit; git push).
.gitignore keeps out build_classes/, __pycache__/, all mod jars (build output) except tools/javassist.jar, and any game files/other mods.
.gitattributes `* -text` keeps line endings byte-exact. Engine inspection helpers live in tools/dev/.

### Where things live
Project folder: `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\`
```
HANDOFF.md, TEST-CHECKLIST.md, SkyWynn-*.md, SkyyHUD-Plan.md, SkyySacks-Plan.md
tools/skyybuild.py        shared build bootstrap (JVM, javassist, assemble, deploy, enable_in_world)
tools/javassist.jar       javassist 3.30.2-GA (Maven Central, sha1 284580b5…)
tools/inline_pages_patch.py  one-off patch that converted the Sacks/Collections pages to inline
SkyyHud/build_skyyhud_0.3.2.py (0.3.0 by tools/hud_0_3_patch.py, 0.3.1 by tools/hud_0_3_1_patch.py; current; 0.2.4 = first render, 0.2.5 centred editor, 0.2.6 Coins widget, 0.2.7 preview, 0.2.8 text arrows/no compass, 0.2.9 clock fix; older kept for history)
SkyySacks/build_skyysacks_0.6.0.py (deployed; derived by tools/sacks_0_6_patch.py from 0.5.2; 0.2 derived by tools/sacks_0_2_patch.py; 0.1.4 = last button-list page), SkyyCoins/build_skyycoins_0.1.2.py, SkyyCollections/build_skyycollections_0.1.2.py, SkyyParty/build_skyyparty_0.1.1.py (+ their jars)
tools/page_root_patch.py, tools/coins_bridge_patch.py  one-off derivation scripts (how 0.2.5/0.2.6/0.1.2 were produced)
```
Deployed jars: `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods\{SkyyHud,SkyySacks,SkyyCoins,SkyyCollections,SkyyParty}.jar`.
Logs: `UserData\Logs\<timestamp>_client.log` (grep `Disconnecting with error`, `Enabled plugin Skyy`), `UserData\Saves\HUD mod\logs\<timestamp>_server.log`.

### Toolchain (Windows, this machine)
No javac anywhere. Java source lives as strings in `build_<mod>_<ver>.py`, compiled with **javassist via jpype** (`pip install jpype1 jdk4py` already done). Run from the mod folder:
```
python build_skyyhud_0.2.4.py            # builds SkyyHud-0.2.4.jar
python build_skyyhud_0.2.4.py --deploy   # + copies to Mods/SkyyHud.jar + flips the world config key to "Skyy:0.2.4 SkyyHud"
```
javassist gotchas (all handled in the scripts): no lambdas/generics/varargs/autoboxing/enhanced-for/inner classes/String-switch/try-with-resources; explicit arrays (`new LinkOption[0]`); **methods must be added in dependency order, also within one class** (no forward references); f-string braces doubled `{{ }}`; Java `\"` inside an f-string is written `\\"`. API verification: `scratchpad reflect.py` pattern = jpype + `Class.forName` on `HytaleServer.jar` (see tools/skyybuild.py `probe()`). Reference-mod archaeology without javap: dump class constant-pool strings with Python (see the session's scans) and disassemble with `javassist.bytecode.InstructionPrinter(PrintStream).print_(ctMethod)`.

---

### Deployed while Skyy was at work (2026-09-23 afternoon, all untested, none touch the join path)
| Mod | Version | What / how to test |
|---|---|---|
| SkyyCoins | **0.1.3** | adds bridge FUNCTIONS `coins:fn:get` (apply(UUID)->Long), `coins:fn:add` (apply(Object[]{UUID,Long})->Long), `coins:fn:take` (->Boolean). Behaviour otherwise identical to 0.1.2. |
| SkyyBank | **0.1 (new)** | `/bank` status, `/bank deposit 500|2k|1.5m|all`, `/bank withdraw ...`, `/bankconfig <pct> <min> [maxPrincipal]` (perm `skyybank.admin`). Interest default 2% every 60 real min on up to 10,000,000, paid to every account file (offline too), catch-up capped at 24 periods. Death penalty cannot touch bank coins (it only touches the purse). Data: `Skyy_SkyyBank/accounts`, `config.properties` (lastInterestMillis). Bridge `bank:<uuid>` -> Long. |
| SkyyCollections | **0.1.3** | publishes recipe unlocks to the bridge `coll:recipes:<uuid>` = "id,id" (auto rule: recipe unlocked when an input hits tier I and no started input is below tier I; plus explicit `Skyy_SkyyCollections/unlocks.properties` `<CollId>.<tier>=RecipeId,..`). `/collections unlocks`, `/collections reload` (perm skyycollections.admin). Milestone message now says how many recipes unlocked. The Sacks craft page Collections tab reads this. |
| SkyyRolls | **0.1 (new spike)** | `/rolls give [itemId]` (random reforge/dmg/str/crit/quality in ItemStack metadata key `SkyyRolls`), `/rolls read` (item in hand + raw metadata JSON), `/rolls reroll`. Test = relog and read again. |
| SkyyAccessories | **0.1 (new)** | Accessory Bag item (Fieldcraft: 4 wood + 4 cotton scrap; right-click or `/accessories`/`/acc`) with 6 slots persisted in `Skyy_SkyyAccessories/bags/<uuid>.properties`; Equip/Unequip buttons move items between inventory and bag. 30 bench accessories `Skyy_Accessory_<BenchId>_T<n>` (T1 = bench item + 4 copper bars at a Workbench; T(n+1) = T(n) + the real bench's upgrade materials). One per bench in the bag; higher tier replaces lower and hands it back. Bridge `acc:has:<uuid>` = "id,id", `acc:fn:has` Function. Pattern copied from TerrariaAddons (see SkyySacks-Plan.md). |
| SkyySacks | **0.6.8** (0.6.8: craft tabs merged -> Crafting (all Fieldcraft + every equipped non-Processing bench up to tier) | Processing (Furnace/Campfire/Tannery/Salvage, only if equipped) | Collections; helper benchRecipes(u, processing) checks BenchRequirement.type. 0.6.7: Farming also takes Ingredient_Life_Essence* + Ingredient_Poop; NEW Combat bag (Small/Medium/Large, recipe 3 wool bolts + 4 bone fragments, page SkyySacksCombat) for bones, hides, chitin, venom sacs, feathers, fabric scraps, voidhearts, boom powder, elemental essences - list from Server/Drops/NPCs; raw meat stays Farming; arrows never pooled. 0.6.6: craft page sorts craftable first, then material progression Crude>Copper>Bronze>Iron>Thorium>Cobalt>Adamantite>Mithril>Onyxium, then name; 'Craftable only' toggle in the nav row. 0.6.5 VERIFIED by Skyy 09-23: crafted items now land in the inventory. 0.6.5 ROOT CAUSE FOUND: nothing was ever lost - crafted items went into the player's BackpackInventory first (getCombinedBackpackStorageHotbar order); Skyy's save held 165 copper bars + campfire + torches there. Outputs now use getCombinedStorageHotbarBackpack (storage first). NO /give refund needed. 0.6.4 CRAFT LOSS FIX 09-23: Skyy crafted all copper ore into bars from the Furnace tab and got nothing - the page only paid when removeMaterials().succeeded() yet still deducted bag items; now pays by counted removal (before/after per input), returns excess, logs every craft to Skyy_SkyySacks/crafts.log; (the 'lost' copper was in the backpack section - see 0.6.5). 0.6.3: craft tabs wrap onto rows + craft page scaled ~35%, '< Back to bags' tab. 0.6.2: bag page scaled ~35%; CraftPage ignores non-bench ids in acc:has; /pd still opens with the empty ContainerWindow experiment, right-click does not - Skyy to compare) | 0.6.1: craft page bench tabs come ONLY from accessories equipped in the accessory bag (bridge `acc:has`; loose accessories in the inventory do not count, per Skyy), one tab per bench at the highest tier held (label e.g. "Workbench II"), recipes filtered by `BenchRequirement.requiredTierLevel <= tier`. Tab id `B:<Bench>:<tier>`. |
| SkyyIslands | **0.4.1** (0.4.1 HOTFIX 09-23: 0.4 failed to load - one system per class; GuardSystem split into GuardDamage/Break/Place/Pickup subclasses. 0.3.1: /island visit open to everyone, invite = build rights; 0.4: starter kit in the chest once per island - workbench, 10 oak logs, 8 dirt, 8 sticks, 5 bread, Accessory Bag - via `WorldChunk.getBlockComponentEntity` -> `ItemContainerBlock.getItemContainer().addItemStack`, world thread; pre-0.4 islands get it on the next arrival. Void: engine kills below y=-32 (hardcoded `DamageSystems$OutOfWorldDamage`), respawn via the island SpawnProvider, items are lost like any death) | 0.2.1: login routing only on the first PlayerReady per session (the event fires on every world switch - it was kicking players off their island 3s after arriving; verified in log). 0.2.2: blocks placed by code rendered black (light update lost during world start) -> relight of chunks (-1..1)^2 scheduled 4s after every arrival (`ChunkLightingManager.invalidateLightInChunk`); template Environment `Env_Default_Void`. **0.3: island protection** - Damage/Break/PlaceBlock + item pickup cancelled for non-members in island worlds (owner, members, perm skyyislands.admin allowed), throttled message; world->owner map from islands/*.properties. VERIFIED 09-23: create, /sethub, /hub, /island. UNVERIFIED: relight fixes the black grass, reload after unload, protection (needs 2 players). 0.2: | `/sethub` (perm skyyislands.admin) saves the hub point (`Skyy_SkyyIslands/hub.properties`); `/hub` (`/lobby`) warps to it from any world (falls back to the default world spawn); logins inside an island world are routed to the hub 1.5s after PlayerReady; `/island` alias `home` removed (vanilla + HyperEssentials own `/home`); island world names registered on disk for the routing check. **Server setup (2026-09-23):** HyperEssentials 0.1.0 ENABLED in the HUD mod world (homes/warps/named spawns/tpa/back/fly/vanish/motd/kits/moderation; it has NO hub command; note it bundles Sentry crash telemetry); nhulston Essentials 1.8.0 left disabled (would double-register the same commands; duplicate command names silently last-wins in CommandManager). Vanilla already has spawn/warp/home/back/teleport/kick/ban/whitelist/op/perm groups; Skyy is in group hytale:Admin in permissions.json. No claims/protection mod is installed (SimpleClaims is only referenced). Old 0.1 row: | `/island` (aliases `/is` `/home`) creates + teleports to a private void-world island (12x12 grass/dirt/stone, oak tree, chest) built by code in chunk (0,0); `/hub` (`/lobby`) returns; `/island invite <player>`, `/island visit <player>`, `/island info`. Uses the engine InstancesPlugin (spawnInstance -> copy template `Server/Instances/SkyyIsland` -> teleportPlayerToLoadingInstance); world name stored in `Skyy_SkyyIslands/islands/<uuid>.properties`, reloaded with `Universe.addWorld(name)` after the engine unloads the empty world. **Unverified**: folder survives unload, reload keeps blocks, login while unloaded, void death. |


### Built by the 4-mod workflow (2026-09-23 evening: build -> cheap review -> fix, then deployed one by one; none tested in game)
| Mod | Version | What |
|---|---|---|
| SkyyAccessories | **0.2** | 15 stat talismans `Skyy_Talisman_<Vitality|Endurance|Intelligence|Regeneration|Speed>_<Talisman|Ring|Artifact>` (+5/10/20 max Health, +1/2/4 Stamina, +10/20/40 Mana, heal 1/2/4 HP per 2s, +4/8/12% move speed), work while in the bag; one per family (highest tier). Bag 6 -> 9 slots, "Bonuses - ..." line. Effects: `AccEffects` EntityTickingSystem (Player query), 1s sync, `StaticModifier(MAX, ADDITIVE)` keys skyyacc_health/stamina/mana (saved with the player - unequip before uninstalling), speed via MovementManager settings (pattern from TerrariaAddons). Bridge: `acc:has` = bench accessories only (Sacks-compatible), NEW `acc:tal:<uuid>` = talismans. Refused equips never leave the inventory; per-player locks. Fixed a 0.1 bug: Farming Bench accessory T2-T7 used wood ResourceTypes as ItemIds. Source of truth: tools/acc_0_2_patch.py. |
| SkyySkills | **0.1 (new)** | Mining / Foraging / Farming / Combat, levels 0-50, XP from block breaks (xp.properties defaults on first run), F-harvest of crops (per-block gate, no spam XP), NPC kills; level-up coins via coins:fn:add (owed and paid later if SkyyCoins is missing). `/skills` (`/skill`) page. Data `Skyy_SkyySkills/players/<uuid>.properties`. Bridge `skill:<uuid>` = "Mining:12,...", `skill:fn:level`. Follow-up: an unreadable player file falls back to zeros and would be overwritten on the next save. |
| SkyyBazaar | **0.1 (new)** | `/bazaar` (`/bz`): 36 verified commodities in 4 categories, instant buy/sell against a market maker (base price x spread x demand factor 0.25-4.0, decays to 1.0), Buy 1/64, Sell 1/64/all, Sell inventory (10s confirm). Coins only via the bridge; coins taken before items, refunds for what did not fit, items removed before paying; bridge errors refuse the trade and log TAKE/REFUND/PAY-ERROR. Build-time check proves no buy->craft->sell money loops across 2161 recipes. `/bazaaradmin` (perm skyybazaar.admin). Files `Skyy_SkyyBazaar/products.properties`, `market.properties`, `trades.log`. Bridge `bazaar:sell:<id>`, `bazaar:buy:<id>`, `bazaar:products`. 0.2 = player buy orders / sell offers (design in the script docstring). |
| SkyyEssentials | **0.1 (new)** | Only what vanilla lacks (checked against HytaleServer.jar): `/tpa`, `/tpahere`, `/tpaccept [p]`, `/tpdeny [p]`, `/tpacancel` (60s expiry, 10s cooldown, cross-world incl. islands, sets the engine instance return point so vanilla `/instances exit` returns visitors correctly), `/msg` (`/tell` `/w` `/whisper`), `/reply`, `/fly` (perm skyyessentials.fly). Replaces the HyperEssentials gaps. Memory-only state. |

**Review pass (cheap agent, 2026-09-23):** fixed before Skyy tests: accessory Unequip/return now also tries the backpack (item could be destroyed when storage+hotbar were full); island reload guarded against a double `Universe.addWorld` (IllegalArgumentException) and double creation (60s per-player guard); island file read-modify-write made atomic; bank maxPrincipal capped at 1e12.

**HyperEssentials 0.1.0 is INCOMPATIBLE with this server build (2026-09-23 18:34): any player death crashes the world - `NoSuchMethodError TransformComponent.getPosition()` in `com.hyperessentials.ecs.PlayerDeathTrackingSystem` (built against an older API). DISABLED again. Do not re-enable unless a newer HyperEssentials release exists. Gaps it was covering (tpa, fly, vanish, backups) -> build a tiny SkyyEssentials later if Skyy wants them.**

**Server commands policy (Skyy, 2026-09-23): VANILLA FIRST, add only what is missing.** (HyperEssentials was briefly enabled but its
config in `Saves/HUD mod/mods/com.hyperessentials_HyperEssentials/config/*.json` (pre-seeded from the old "Endless leveling" save) has
`enabled=false` for the modules vanilla already covers: warps, spawns, homes, moderation, kits, announcements; Sentry telemetry off;
updateCheck off. Left ON: teleport (/tpa /tpaccept /tpdeny /rtp; its /back replaces vanilla /back, same job), utility (/fly /heal /god
/motd /rules /near /repair), vanish, backup (hourly world backups), warmup. Vanilla cheat sheet: `/warp set <name>`, `/warp <name>` or
`/warp go <name>`, `/warp remove <name>`, `/warp list`; `/spawn`, `/spawn set`; `/back`; `/teleport`; `/kick /ban /unban /whitelist`;
`/op`, `/perm group|user`, `/setgroup`. Hub = SkyyIslands `/sethub` + `/hub`. If HE modules ignore the pre-seeded config on first run, re-apply.


**Movement bonus rule (Skyy, 2026-09-23, final):** LAYERED. Skills raise the BASE, gear adds % of that base: final = default x (1 + skill base bonus) x (1 + sum of gear %). **Skill cap (Skyy): max level 100 for ALL skills** (extend the XP table to 100; rescale per-level rewards so level-100 targets hold). **Acrobatics targets (Skyy):** linear per level: speed base +1% per level (x2.0 vanilla at 100), jump +0.015 blocks per level (+1.5 blocks at 100 - convert blocks to the engine's jump force/velocity, v = sqrt(2 g h), using the verified gravity + default jump), fall damage -0.5% per level (-50% at 100). All tunable in xp.properties (acro.*). Example: Acrobatics 100 + Speed talisman +10% = 2.0 x 1.10 = 2.2x vanilla. Shared protocol: each source registers under move:<uuid> with a layer (base | gear); every applier computes default x (1 + sum base) x (1 + sum gear). The first SkyySkills 0.2 / SkyyAccessories 0.3 build used a plain product and 50-level scaling - adjust before deploying. **Future armor/weapons (Skyy):** gear will ADD or REDUCE any of these stats, always with a tradeoff - so the protocol must be a generic signed stat system: move:<uuid> -> source -> {layer: base|gear, stat -> signed value}, stats speed / jump / fallDamage (extensible). Clamp results (speed floor e.g. 0.3x default, jump >= 0, fall damage multiplier 0..2, never healing). Idempotent stats (speed, jump: every applier sets the same default-derived value) may have several appliers; damage stats (fallDamage) need ONE applier - elect it with bridge putIfAbsent('stat:owner:fallDamage', mod) and that mod sums all sources. **Layer model (Skyy, final):** FLAT layer = skills + armor add or subtract flat amounts to the default; PERCENT layer = accessories add % on top: final = (default + sum of flat) x (1 + sum of accessory %). Only ONE accessory per kind/family counts (no stacking 6 speed rings; already enforced: one per family, best one wins). Accessories have RARITY tiers Common -> Uncommon -> Rare -> Epic -> Legendary (item Quality field), replacing the Talisman/Ring/Artifact naming in SkyyAccessories 0.2.


**Skills + classes design (Skyy, 2026-09-23):** gathering skills Mining, Foraging, Farming (+ Acrobatics); Fishing later - Hytale has no fishing
rod yet, only Tool_Fishing_Trap and 31 fish items (a Fishing skill could reward emptying traps); pets later. COMBAT IS CLASS-BASED: your combat
skill is your class's skill, you can only use your class's weapons and cannot level any other combat. -> new mod SkyyClasses (class choice,
weapon lock by cancelling damage/usage with non-class weapons, bridge class:<uuid>); SkyySkills reads class:<uuid> to name/restrict Combat.
CONFIRMED class roster (Skyy, 2026-09-23): Archer=Archery (Shortbow, Crossbow); Warrior=Swordsmanship (Sword, Longsword, Spear); Assassin=Assassination (Daggers, Kunai = throwing knife); Berserker=Berserking (Axe, Battleaxe, Mace, + Club as a blunt weapon - my call); Mage = ENABLED (Skyy, 2026-09-23: 'use the staff for the mage, it hits and casts magic') -> Mage=Sorcery (Staff); Wand and Spellbook stay unassigned for now. DONE in SkyyClasses 0.1.1 (Mage enabled, skill Sorcery). Defaults (my calls, changeable): shields, tools and fists usable by all; classless players may use any weapon but earn no combat XP; class picker opens on first join; switching costs coins, each class keeps its own combat level. SkyySkills Combat becomes the class skill after the Acrobatics build lands. Weapon folders from Assets.zip Server/Item/Items/Weapon/.

**Packaging decision (Skyy, 2026-09-23):** one combined pack is fine for the server-only mods, BUT SkyyHud and SkyySacks must stay publishable as standalone jars. Current design (separate jars + `skyy.bridge`) already satisfies both; a merged "SkyWynn Core" jar (one plugin main calling each sub-setup) is a later packaging step, not a rewrite.

## 4. WHAT TO DO NEXT (in order)

1. **Skyy approves deploys** -> deploy the approved set, watch the first join in the server log (plugin load errors, 'already registered'),
   then Skyy runs TEST-CHECKLIST.md (newest sections at the bottom). Fix what fails.
2. **Finish the GitHub setup** (push to the private SkyyWynnBlock repo) - see the running log.
3. **Skyy's open decisions** (section 3) -> SkyyAccessories 0.5 (accessory power + slot unlocks) and the Endurance/Intelligence values.
4. **Islands**: confirm the grass tint fix, the reload-after-unload test, the starter chest, void respawn; then island upgrades.
5. **HUD**: party widget (SkyyParty data), bank + skill widgets (bridge keys bank:<uuid>, skill:<uuid>).
6. **Roster next** (SkyWynn-Mod-Roster.md): SkyyBazaar 0.2 (player buy/sell orders), SkyyAuctions (needs the Rolls metadata test),
   SkyyMinions (islands), SkyyWardrobe, SkyyNav; armor/weapon stat items with tradeoffs (flat layer, signed values - movement protocol ready).

## 5. DESIGN NOTES + DECISIONS (added during 2026-09-23; newest decisions win)

**Pending HUD tweaks (Skyy, 2026-09-23) - apply on top of 0.3.4 after its workflow:** widget Settings page button 'Back to editor' -> 'Back' opening WidgetsPage; Widgets page button -> 'Back' (to the editor); scale both pages up A LOT (Skyy: 'a lot bigger' - ~1.8x: bigger fonts, rows, buttons).

**Accessory power (Skyy, 2026-09-23):** unlocking more accessory bag slots + a Hypixel 'Magical Power'-like stat (Skyy: 'look into hypixel skyblock's accessory power, i want to use something similar') - research requested, design later.

**Skills Stats page (Skyy, 2026-09-23):** replace the 'Top 10' button on each skill row with 'Stats' -> a page listing the boosts that skill gives now and what the next level adds. Needs per-skill perks (flat layer): propose configurable defaults for Mining/Foraging/Farming (e.g. double-drop chance + a flat stat) and class combat; Acrobatics per the level-100 targets. Do it in the SkyySkills 0.2 adjustment pass.

**Crafting layout + OMNI (Skyy, 2026-09-23, supersedes 0.6.8 tabs):** Crafting tab = Fieldcraft + ALL equipped bench accessories EXCEPT
Alchemy, Furnace, Tannery (Workbench, Armor, Weapon, Cooking, Farming, Furniture, Loom, Arcane, Campfire, Salvage all merged, instant);
Alchemy = its own tab; Furnace + Tannery accessories open a TIMED processing screen (load items, takes the normal time, like a real
furnace - not instant); Collections tab unchanged. OMNI craft accessory (Skyy_Accessory_Omni) = every bench accessory at once (max tier),
crafted from the other bench accessories; build it in SkyyAccessories after the Acrobatics workflow's 0.3 lands (expand Omni into the
acc:has bridge value so SkyySacks needs no parsing change).

**SkyyHud 0.3.4 + 0.3.5 (deployed 2026-09-23):** 0.3.4 editor = live previews at TRUE positions behind invisible 1 px handles (SlotIconSize 1 + setSkipItemQualityBackground), 32x18 grid of 40 px, handle at the preview centre (collision -> nearest free cell), drag moves by the dragged distance (Widgets.moveByCells), Select row of widget buttons, < > ^ v with Step 1/5/10/25, Size-/Size+, Hide, Settings, clamps to screen; /skyyhud preview is now a no-op. 0.3.5 = Widgets + Settings pages ~1.8x bigger, '< Back' buttons (Settings -> Widgets list -> editor). Source: tools/hud_0_3_4_patch.py + tools/hud_0_3_5_patch.py.
**SkyyIslands 0.4.2:** black grass = biome TINT 0 in the void world; template Tint #5b9e28, FillTask + every arrival re-tint loaded chunks within 2 (BlockChunk.setTint + markNeedsSaving). The existing island's universe/worlds/skyy-island-<uuid>/config.json should also get "Tint": "#5b9e28" in WorldGen while the server is STOPPED (for chunks generated later).

**COMMAND RULES (verified 2026-09-23, apply to EVERY Skyy mod):**
1. Auto permission nodes: any command without requirePermission() gets '<group>.<name>.command.<cmd>' (version inside the node), which
   ordinary players (hytale:Adventurer) do not have -> player commands need setPermissionGroups(new String[] { "hytale:Adventurer" }) in the
   constructor of the command AND of every subcommand/usage variant (SkyyEssentials pattern). Never on admin commands (requirePermission).
2. Optional args are not positional: token count must equal the required-arg count (acceptCall0). Every documented positional form needs a
   usage variant (description-only ctor + withRequiredArg, parent addUsageVariant) or a subcommand with withRequiredArg.
Status: workflow 'skywynn-perms-args' is building (NO deploy) SkyyHud 0.3.6, SkyyCoins 0.1.4, SkyyCollections 0.1.4, SkyyParty 0.1.2,
SkyyBank 0.1.1, SkyyIslands 0.4.3, SkyyBazaar 0.1.1, SkyyRolls 0.1.1 (Rolls stays admin-only). STILL TO DO after their running builds land:
SkyySacks (/sacks /pd /bags /craft), SkyySkills (root, top->stats, quiet), SkyyAccessories (/accessories), SkyyClasses (/class), SkyyMenu
(update MENU DATA command lines + Bank entries to the short forms).

**Built, NOT deployed (awaiting Skyy's OK, 2026-09-23):** SkyySkills 0.2 (Acrobatics: speed +1%/lvl of vanilla, jump +0.015 blocks/lvl,
fall -0.5%/lvl cap 80%, vanilla dodge detected (Dodge_Left/Right effect) -> XP + push +0.4%/lvl cap 50%; XP sprint/run/walk per block,
jumps, survived falls, 240 XP/min cap) + SkyyAccessories 0.3 (talisman speed via the shared protocol). Shared protocol v1 = tools/skyymove.py
(move:<uuid> sources with layer flat|pct; speed=(1+sum flat)(1+sum pct) clamp 0.3..5; jump in blocks via sqrt(2gh), g=32; fall-damage owner
election stat:owner:fallDamage). MoveSync.KNOWN_WRITERS lists 12 installed mods that write MovementSettings directly (RPGLeveling,
TerrariaAddons, Endgame&QoL, Hylamity, TheArmory...) - keep them OUT of SkyWynn worlds. Deploy Skills + Accessories TOGETHER (Accessories 0.2
writes speed the old way). In progress on top: SkyySkills 0.3 + SkyyAccessories 0.4 (workflow skywynn-skills03-acc04).

**SkyyMenu 0.1 (built, NOT deployed):** item Skyy_Menu (given once on first join, right-click) + /skymenu (/menu, /sbmenu), Adventurer group. One 9x6 ItemGrid page, tooltips + info lines under the grid. MAIN: Profile, Teleport, Pocket Dimension, Accessory Bag, HUD Editor, Crafting, Skills, Collections, Bazaar, Bank, Players, Party, Mods. TELEPORT: island, hub, spawn, every vanilla warp (TeleportPlugin.getWarps(); teleports directly like WarpCommand.tryGo because vanilla /warp go is Builder-only; MenuUtil.isWarpUnlocked hook for future locks). Actions run other mods' commands with CommandManager.get().handleCommand(playerRef, "cmd") (permission-checked like typing). Mod catalog + icons editable in the MENU DATA section. TODO once the perms-args builds land: switch MENU DATA command lines + Bank entries back to the short positional forms.

**SkyyClasses 0.1.1 (built, NOT deployed):** Archer (Shortbow, Crossbow, Arrow as melee too) / Warrior (Sword, Longsword, Spear) / Assassin (Daggers, Kunai) / Berserker (Axe, Battleaxe, Mace, Club) / Mage=Sorcery (Staff + Halloween_Broomstick; 0.1.1 enabled it). Shields free; 33 unassigned items (bombs, guns, wands, spellbooks, darts, claws, deployables...) deal no damage for players WITH a class (unassignedBlocked=true). Damage lock = DamageEventSystem (filter group) judging the weapon in hand at hit time, projectiles by the weapon held at launch (ShotTrack RefSystem); blocked hits lose damage + knockback; known limits: bomb knockback, deployable damage. /class page (/classes, Adventurer group since 0.1.1), first choice free, switch costs coins + cooldown; /classadmin set|reset|info|reload (subcommands, skyyclasses.admin). Bridge class:<uuid>, class:skill:<uuid>, class:fn:allowed, class:fn:get, class:list, class:weapons:<Class>.

**Command-rule builds done (NOT deployed, 2026-09-23):** SkyyHud 0.3.6, SkyyCoins 0.1.4, SkyyCollections 0.1.4, SkyyParty 0.1.2, SkyyBank 0.1.1, SkyyIslands 0.4.3, SkyyBazaar 0.1.1, SkyyRolls 0.1.1 (admin-only) - Adventurer group on player commands + short positional forms via subcommands/usage variants (old --flag forms still work). SkyyMenu 0.1.1 = MENU DATA switched to the short forms. Remaining for the rules: SkyySacks (in 0.7.0 follow-up), SkyySkills 0.3 + SkyyAccessories 0.4 (in their workflow), SkyyClasses 0.1.1 (done: /class Adventurer).

**SkyySkills 0.3 + SkyyAccessories 0.4 (built, NOT deployed, 2026-09-23):** Skills: cap 100 for all (Hypixel table to 60, +300k/level to 100; coins 100 x level), Stats page per skill (Boosts right now / Level L+1 adds, Top 10 moved inside), perks per level in xp.properties: Mining +0.05 Stamina & +0.5% double drop, Foraging +0.1 Health & +0.5% double logs, Farming +0.25 Health & +0.5% double crops, Combat (current class skill) +0.1 Health & +0.2% class-weapon damage vs monsters; class-based combat with per-class XP (Combat.<Class>), legacy Combat XP migrates to the first class; /skills stats|top|quiet positional + Adventurer. Accessories: 25 talismans in 5 rarities (2/4/6/8/10% of FLAT max Health/Stamina/Mana, speed 2..10%, regen 0.5..3% max HP per 2 s), old Talisman/Ring/Artifact = Uncommon/Rare/Epic (converted when they pass through the bag), bench accessories get rarity from tier, OMNI (Legendary, 13 top-tier bench accessories) = every bench at max tier in acc:has (one entry per bench), /accessories Adventurer. Balance note: vanilla base Stamina is 10 and Mana 0, so Endurance/Intelligence % are tiny until gear adds flat values. Deploy set together: SkyySkills 0.3 + SkyyAccessories 0.4 + SkyyClasses 0.1.1 (+ SkyyMenu 0.1.1).

**SkyySacks 0.7.0 + 0.7.1 (built, NOT deployed, 2026-09-23):** craft tabs '< Back to bags' | Crafting (Fieldcraft + every equipped bench except Alchemy/Furnace/Tannery, instant) | Alchemy | Furnace | Tannery | Collections. Furnace/Tannery = OUR OWN timed processing page (vanilla ProcessingBenchWindow needs a real placed block within 7 blocks + loaded chunk - not usable): per player per bench queue (x1/x10/All, counted removal, cap 256 units), unit time = recipe TimeSeconds x (1 - tier CraftingTimeReductionModifier; Furnace II -30%, Tannery II -40%), Furnace needs fuel (ResourceTypes Fuel, FuelQuality = burn seconds; 1 charcoal per 2 fuel like vanilla), Tannery no fuel, output slot + Collect (storage first), Cancel/Unload return items, wall-clock replay so it runs offline and across restarts, Skyy_SkyySacks/processing/<uuid>.properties atomic+fsync. Review fixes: instant-craft double-deduction fix, saves off the world thread, config miss retried after 30s, fuel/finish ordering. 0.7.1 = Adventurer group on /sacks /pd /bags /craft /recipes.

## 6. RUNNING LOG (append-only, newest last - add an entry for every build, deploy, test result or decision)

- 2026-09-22: toolchain rebuilt on Windows (javassist via jpype); HUD render blocker solved (no .ui files, no underscores in IDs); Magic Bags design locked.
- 2026-09-23 morning: Coins 0.1.3 bridge functions, Bank 0.1, Islands 0.1 spike, Rolls 0.1 spike, Collections 0.1.3 unlocks, Accessories 0.1 deployed.
- 2026-09-23 midday: 4-mod workflow -> Accessories 0.2, Skills 0.1, Bazaar 0.1, Essentials 0.1 deployed; Islands 0.2-0.4.2 (hub, protection, starter kit, tint fix); HyperEssentials disabled after a death crash.
- 2026-09-23 afternoon: HUD 0.3.3-0.3.5 (live previews, fine controls, bigger pages), Sacks 0.6.2-0.6.8 (bigger pages, craft loss = backpack section, sorting, Combat bag, merged tabs) deployed.
- 2026-09-23 evening: built without deploying (Skyy's new rule): SkyyMenu 0.1.1, SkyyClasses 0.1.1, SkyySkills 0.3, SkyyAccessories 0.4, SkyySacks 0.7.1, and the command-rule fixes (Hud 0.3.6, Coins 0.1.4, Collections 0.1.4, Party 0.1.2, Bank 0.1.1, Islands 0.4.3, Bazaar 0.1.1, Rolls 0.1.1). Accessory power plan written (SkyyAccessories-Plan.md).
- 2026-09-23 20:45: git repo initialised (branch main) with .gitignore/.gitattributes/README; engine helpers copied to tools/dev; HANDOFF restructured (sections 3 and 6). GitHub remote SkyyWynnBlock: pending - gh CLI not installed, needs Skyy to sign in to GitHub.
- 2026-09-23 20:55: pushed to the GitHub repo SkyyPlayz/SkyyWynnBlock (Skyy created it). First push was declined for exposing the private Gmail; the repo now commits as the GitHub noreply address.
- 2026-09-23 20:58: anonymous API check shows the repo is PUBLIC (created on GitHub's default). Asked Skyy to switch it to Private; further pushes held until then.
