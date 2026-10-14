# Admin page plan (SkyyMenu) - build brief, 2026-10-14

One in-game "Admin" page in the SkyWynn Menu with buttons for the admin commands we already have, grouped by job. Sources: grep of the pinned build scripts of the SET
(`/<x>admin <sub>` usage strings, `requirePermission("skyy*.admin")`), `HANDOFF.md` section 3 (command rules), `SkyyMenu/build_skyymenu_0.3.21.py` (Server Setup entry gated by
`skyymenu.modconfig`, the Mods list `modsHelp`, tile rules). Subcommand lists come from usage text and comments, so the build round must confirm each against the real command
classes (UNVERIFIED, section 6). Nothing is built.

## 0. Short version

1. **~28 admin commands in 22 mods**, each its own `/xadmin` with its own permission node (`skyy<mod>.admin`). Admins today must remember all of them. The Mods page lists them as
   text; Server Setup holds the NUMBERS, not the ACTIONS (give item, move merchant, pause AH, reload, list, reset).
2. **The page is a launcher plus a few safe live views, not a new settings system.** Numbers stay in Server Setup (CONFIG-CONTRACT). Each button either runs a command with no
   argument (reload, list, status, info, pause / resume) or opens a small argument form (player + amount, item id).
3. **Gate on the real node of each target command**, never on `skyymenu.modconfig` alone: a button shows only if the viewer has the node of the command it runs (Skyy 2026-09-25
   LOCKED: hidden rows, no greyed-out entries). The page itself needs `skyymenu.modconfig` (as Server Setup does).
4. **Danger buttons confirm** (reset, remove, repay, sweep, undo) with the existing 2-step confirm pattern; show one result line, never close the page (HANDOFF section 2: never
   close a page right before opening another).

## 1. What exists - by group

Node column = permission of the parent command (`requirePermission`). "Needs arg" = the command takes arguments, so the button opens a form or prefills a console-style command.

### Server

| Command | Mod | Subcommands found | Button (no arg) | Needs arg |
|---|---|---|---|---|
| `/modconfig` | Menu / Hud / Skills ... | `menu`, per-mod page | **Open Server Setup** | - |
| `/zone` | WorldGen / Menu | `list`, `info`, `reload`, `setlanding`, `leave` | Zone list, Reload zones | setlanding (here) |
| `/sethub` | Islands / WorldGen | - | **Set hub here** (confirm) | - |
| `/warpadmin` | Essentials | `spawn`, `off`, `page`, `nodes` | Warp page | spawn / off |
| `/tradeadmin` | Essentials | `config`, `log`, `reload` | Trade log, Reload | - |
| `/rankadmin` | Ranks | `player`, `reload`, `sync`, `editor` | Reload ranks, Sync | player + rank |
| `/profileadmin` | Profiles | `info`, `archive`, `reload`, `config`, `setclass`, `bonus`, `name`, `set` | Reload, Config | info / archive / setclass need a player |
| `/deathpenalty`, `/bankconfig` | Coins, Bank | spec / percent minutes | show current | set values |
| `/island ... reload`, `reset` | Islands | `reload`, `reset` | Reload islands | reset needs a player |

### Economy

| Command | Mod | Subcommands | Button | Needs arg |
|---|---|---|---|---|
| `/bazaaradmin` | Bazaar | `info`, `reload`, `price`, `reset` | Info, Reload | price (item + value), reset (confirm) |
| `/ahadmin` | Auctions | `status`, `info`, `list`, `pause`, `resume`, `remove`, `regrant`, `reload` | **Pause / Resume AH** (toggle by status), List, Reload | remove, regrant (listing id) |
| `/vaultadmin` | Vault | `info`, `open`, `setpages`, `config`, `reload` | Info, Reload | open / setpages (player) |
| `/merchantadmin` | Merchants | `list`, `move`, `spawn` | **List merchants**, Move all | spawn (zone) |
| `/tradeadmin` | Essentials | see Server | Trade log | - |

### Players and progress

| Command | Mod | Subcommands | Button | Needs arg |
|---|---|---|---|---|
| `/classadmin` | Classes | `info`, `kit`, `reload`, `reset`, `set`, `abil`, `shape` | Info, Reload | kit / reset / set (player + class) |
| `/questadmin` | Quests | `check`, `npc`, `place`, `reload`, `repay`, `set` | Check, Reload, **Set hub spots** (the 4 `place set hub.*` Skyy still needs to run) | place / repay / set |
| `/exploreadmin` | Exploration | `stats`, `luggage`, `check`, `get`, `set`, `resetme`, `reload`, `help` | **Stats**, Reload | get / set / resetme |
| `/petadmin` | Pets | `list`, `kinds`, `give`, `restore`, `sweep`, `unlock`, `help` | Kinds, Sweep (confirm) | give / restore / unlock (player + kind) |
| `/requipadmin`, `/wardrobeadmin` | Wardrobe | `info`, `slots`, `give`, `repair`, `reload` | Info, Reload | give / repair |
| `/cookadmin` | Cooking | `reload`, `give`, `campfire`, `node` | Reload | give |
| `/fishadmin` | Fishing | `status`, `give`, `kit`, `pond`, `bite`, `treasure` | **Status** | give / kit |
| `/pdadmin` | Sacks | `rarity`, `omni`, `legacybags`, `resume`, `world` | Resume, Legacy bags check | rarity / omni (player + rarity) |
| `/partyadmin`, `/guildadmin`, `limadmin` | Party, Guilds | `reload`, `set`, `config`, `delete`, `info`, `season` | Reload | delete / set |
| `/rebirthadmin` (R3, not built) | Rebirth | dry-run, crashtest (spec) | Rebirth status, Dry-run | player |
| `/gear admin` rows, `/settings` | Gear, Menu | (Gear admin is Server Setup + give commands) | - | - |

### Diagnostics (new, small, read-only)

| Button | Runs | Notes |
|---|---|---|
| Server stats | engine `/server stats`, `/world tps` (names UNVERIFIED, see `research/Load-Test-Plan.md`) | shows 3 lines, no tick polling |
| Mod versions | reads the bridge / Mods list | which SET versions are loaded |
| Recent warnings | last 20 `[Skyy*] WARN` lines from the world log | read-only text |
| Sound test | `/soundtest <id>` (proposed in `research/Sound-Pass-Plan.md`) | form with an id box |
| Economy snapshot | `coins:fn:*`, bank totals, Bazaar counters | numbers for `research/Economy-Audit-1014.md` measure list |

## 2. Page layout (Sky Window kit, vanilla look)

| Area | Content |
|---|---|
| Frame | `tools/skyyui.py` (SUI) page, 1080-high fit, left tab list of groups, right panel of buttons (kit `tab` style probe `/skyprobe kit` first - same dependency as RESUME item 4) |
| Tabs | Server, Economy, Players, Diagnostics (+ "Mods" link to the existing Mods list) |
| Button row | label, one-line help (the command it runs), state text (status line from a bridge call when one exists: AH "paused / running", merchants "N out") |
| Result line | one line under the tabs: "Done: Auction House paused", "Needs: player name" - same line for errors |
| Forms | one shared "argument" panel (player dropdown from online players + text box + Run); each button defines its fields, e.g. `give`: player, kind, amount |
| Confirm | red button text "Confirm: <action>" for 5 s, then back (existing buy-confirm pattern) |
| Search | one text box that filters buttons by name (30+ buttons) |

## 3. How a button runs a command (decision needed in the build round)

| Option | How | Pros | Cons |
|---|---|---|---|
| A. Dispatch the command string as the player | engine command manager `handleCommand(sender, "ahadmin pause")` | zero changes in the other 22 mods; permission check is the real one | exact engine call UNVERIFIED (look in `tools/dev/reflect.py` for `CommandManager`); output goes to chat, not the page |
| B. Bridge functions per mod | each mod publishes `admin:fn:<mod>:<action>` | page can show results | touches 22 mods, bigger round |
| C. Mix | A for everything now; B only for the 5 status lines (AH, merchants, exploration stats, Bazaar info, fishing status) | cheap start, good feedback | two paths |

Recommended: **A**, then **C** for status lines. Cross-mod calls still only through `skyy.bridge` with java.lang types (AGENT-BRIEF).

## 4. Permissions and safety

| Rule | Detail |
|---|---|
| Page node | `skyymenu.modconfig` (as Server Setup); a hub tile "Admin" drawn only for it (TILE_RULES perm entry) |
| Buttons | each carries the node of its target; hidden without it |
| Command rules | no new player command; `/admin` opener (if any) uses `requirePermission` + `setPermissionGroups(new String[0])` (lint rule `perm_group_leaks`) |
| Audit | every button press writes one line to the existing Server Setup change log style: who, command, result |
| No deletes without confirm | reset, remove, repay, sweep, delete, archive, undo |
| Never in the page | passwords, tokens, anything under AppData |

## 5. Build brief for the SkyyMenu round

| Item | Detail |
|---|---|
| Version | SkyyMenu 0.3.22 or 0.4 (from the current generated script via a patch script, `tools/menu_0_3_22_patch.py`) |
| New | `AdminPage` class (kit page), tab list, `AdminAction` table (id, group, label, help, command, node, needs-form fields, confirm flag, status bridge key), `/modconfig admin` opens it (no new top-level command) |
| Data | the table is a Java static list generated from a Python list in the patch, so adding a button = one line |
| Tests | harness: every row's node exists in the live nodes, every command string starts with a registered command, page builds with 0 / 1 / 20 rows visible, a non-admin sees nothing, confirm flow, result line |
| Not in this round | writing new commands in other mods (only reuse), merging with Server Setup |
| Round size | lean round (one mod, no saved data) unless option B is chosen |

## 6. UNVERIFIED

| # | Item |
|---|---|
| 1 | The exact subcommand lists above are from usage strings and comments, not the command classes; the build harness must read the real registrations. |
| 2 | That the engine allows dispatching a command string as a player from a page click (option A). |
| 3 | Command outputs go to chat; the page cannot capture them without option B. |
| 4 | `/wardrobeadmin` vs `/requipadmin`: both strings appear; one may be the old name. |
| 5 | `/rankadmin` appears in Menu and Ranks scripts (Ranks owns it). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One Admin page in the SkyWynn Menu (right bar, admin only), tabs Server / Economy / Players / Diagnostics? | [yes] |
| 2 | Buttons run the existing commands as you (chat shows the output), with a one-line result on the page for the 5 status buttons? | [yes, option C] |
| 3 | Which buttons first: pause AH, list merchants, reload mod, set hub spots, exploration stats, server stats? | [all six first, rest after] |
| 4 | Dangerous buttons (reset, remove, repay) confirm for 5 s before they run? | [yes] |
| 5 | Build it after the Sky Window kit probe (`/skyprobe kit`) so it uses the final tab look? | [yes] |
