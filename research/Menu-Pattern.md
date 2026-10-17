# Menu Pattern - fewer menus, one look, one set of rules

*Spec 2026-10-16 (paper only, nothing built). Owner: Skyy (they/them). Where this goes: research/ (INDEX.md "research"). Answers go to
`docs/answered/ui.md`; the pattern rules (section 3) become the standing rule for every new or changed menu (PROJECT-RULES 4).*

Skyy 2026-10-16 (docs/answered/ui.md, FEWER MENUS, ONE PATTERN): "lets try to reduce and compress the menus together to reduce clutter. then
make sure its consistent across the board, then follow the pattern when making new or adding to existing menus." Same day: the top hub
row on EVERY page at exactly the Home page's size ("keep this top bar at this size consistent at the top across every menu"); replace
commands, never add extra; no duplicates; sort by tier everywhere; scroll lists instead of pages; Accessory Bag -> Void Charms (menu
only, /charm /charms /ch); Pets get Pets / Eggs / Hatchery tabs; the Smithing pages join the Crafting hub row.

Read with: `research/Unified-Menu-Plan.md` (Home + two rows), `research/Hubs-Spec.md` (hub contract), `research/Vanilla-UI-Style-Guide.md`,
`HANDOFF.md` section 2, `tools/skyyui.py` (HUB_TABS, HUB_MERGED, hub_shell, kit 1.6 row), `tools/HUBS-CONTRACT.md`.

Sources for the inventory: the SET build scripts (`tools/deploy_set.py`, 2026-10-16: Menu 0.3.33, Skills 0.4.45, Trees 0.3.19, Classes 0.1.33,
Collections 0.2.22, Sacks 0.8.13, Bank 0.1.15, Vault 0.1.8, Bazaar 0.1.17, Auctions 0.1.9, Gear 0.3.14 ...), grepped for page classes,
hub_shell / page_shell, sizes, tab rows, pagers and commands. Sizes are the page root (w x h). "~" = read from constants, not run.

---

## 1. INVENTORY (every page / window / tab today)

**Bars legend:** **BIG** = Home's big row 1 (48 px buttons, 32 px icons, 18 px labels; only SkyyMenu Home + Teleport have it).
**ROW** = kit 1.6 small row 1 in the title bar (30 px buttons, 22 px icons, 14 px labels) + 44 px tab strip. **MENU** = kit 1.5:
"< Menu" + hub title + 44 px tab strip (no row 1). **NONE** = a plain window, no hub bars at all.
**Flags:** D = duplicate of another page, P = PREV / NEXT paging, T = old inner tab row, S = size differs from its hub mates,
O = old dark-blue style (#0b1524 / #142030, not vanilla).

### 1.1 Hub pages

| Hub > tab (row 2) | Mod (SET) | Commands | Size | Bars | Inner rows (sub-tabs) | List | Flags / notes |
|---|---|---|---|---|---|---|---|
| **Home** | Menu 0.3.33 | /skymenu (/menu), menu item, double-tap crouch | 1600 x 926 | BIG | - | 5 x 5 shortcut grid | THE reference size |
| World > Teleport | Menu | (World hub = this page) /travel | 1300 x 962 | BIG + big row 2 (56 px) | - | 5 x 5 grid | S (1300 wide, not 1600) |
| World > Island | Islands 0.5.17 | /island menu (/is), /island, /hub, /lobby | 1254 x 980 | MENU | Overview / Members / Permissions / Visitors / Island | P (members, visitors) | T, P, S |
| World > Explore | Exploration 0.2.12 | /explore (/exploration, /discoveries), /title(s) | ~1134 x ~970 | MENU | 4 fixed tabs (172 px) | P ("< Island / Island >", "page x of y") | T, P, S |
| World > Quests | Quests 0.3.4 | /quests (/quest), /quests track / hide / show / claim / skip | 1000 x 660 "Quests" log | NONE (contract tab, not put) | "< Line / Line >" switcher | P (10 rows, page x of 3) | not in the hub, P, crowded (Skyy 10-16: "quests menu is crowded and confusing.") - section 2b |
| Character > Skills (+ Your Stats) | Skills 0.4.45 + Menu Stats | /skills (/skill), /stats (/profilestats) | 974 x 980; Your Stats 1114 x 974 | MENU (Skills) / ROW (Your Stats) | [YOUR STATS] [SKILLS]; Your Stats adds Main / Combat / Gathering / Skills / Profile | scroll (skills) | merged 10-16 (pinned); two bar styles inside ONE tab; 3 tab levels on Your Stats; Your Stats "Skills" + "Profile" tabs = D |
| Character > Skills: skill Stats / Overall / Top 10 | Skills | /skills top, /skills stats | 974 x 914 / 974 x 755 | MENU | own "< Back" | - | S (heights jump) |
| Character > Trees (+ Class) | Trees 0.3.19 + Classes 0.1.33 | /tree (/trees), /class (/classes) | 1454 x 980; class tree 1600 x 980; class list 1114 x 980 | MENU | TWO tree-tab rows (Mining..Smithing / Acrobatics, Exploration, Fishing) + class tab | - | merged 10-16 (pinned); T (2 rows), S (3 widths in one tab) |
| Character > Pets | Pets 0.4.0 | /pets (/pet) | 974 x 946; Hatch page 760 x 640 | MENU; Hatch NONE | Pet slot / Summon slot / Fuse / Rebirth | P (pet grid) | P, S; petmenu (Pets 0.4.1, RUNNING) adds Pets / Eggs / Hatchery |
| Character > Accessories | Accessories 0.5.20 | /accessories (/acc, /accbag) | ~1100 x ~900 "Accessory Bag" | NONE (stand-in tab from Menu) | Bag / Craft | P (9 rows a page, two pagers) | no hub bars, T, P; accraft 0.5.21 adds Benches / Combat / Gathering; AP1 renames it **Void Charms** (/charm /charms /ch) |
| Character > Collections (+ Recipes) | Collections 0.2.22 | /collections (/coll), /recipes | 1264 x 892 | MENU | category grid -> collection page | P (grid, recipe list) + scroll (recipes) | merged 10-16 (pinned); P, S |
| Character > Profiles | Profiles 0.1.15 | /profiles (/profile, /profile new) | 1114 x 980 | MENU | list / Create Profile view | scroll | ok |
| Storage > Pocket (the Void) | Sacks 0.8.13 | /sacks (/pd, /bags, /pocket) | 1300 x 690 "SkyyVoid" | NONE (stand-in tab) | 6 bag categories | - | no hub bars, S (opens over the vanilla inventory) |
| Storage > Requip | Wardrobe 0.2.4 | /requip (/rq, /wardrobe, /wd, /loadout(s)) | 1320 x 900 "Requip" | NONE (stand-in tab) | Armor / Weapons / Items / Inventory | scroll | no hub bars, S |
| Storage > Vault (+ Bank) | Vault 0.1.8 + Bank 0.1.15 | /vault, /bank | 1054 x ~960 | MENU | vault page numbers | P (vault pages = real slot pages) | merged 10-16 (pinned); /bank still opens the old Bank page 1225 x 667 = D |
| Market > Market (Bazaar + AH) | Bazaar 0.1.17 + Auctions 0.1.9 | /bazaar (/bz), /ah (/auction, /auctionhouse), /ah sell / manage / claim | Bazaar ~1094 x ~970; AH 1128 x 976 | MENU | [BAZAAR] [AUCTION HOUSE] switch + 6 bag tabs (Bazaar) / Browse, Manage (AH) | P (Bazaar 3 grid rows, AH lists) | merged 10-16 (pinned); P, S (two widths in one tab) |
| Market > Merchants | Merchants 0.1.5 | /merchants (/rumours, /rumors) | 1214 x ~782 rumours | MENU | - | scroll | S |
| Crafting > Crafting | Sacks 0.8.13 | /craft (/recipes in help text), /crafting (hub) | 1200 x 960 | ROW (small - Skyy: "a little small") | category tabs + Craftable only | P (9 rows, Page 1/4) | P; sacks0814 (RUNNING) = bigger rows + scroll |
| Crafting > Smithing / Anvil / Tools / Upgrade / Identify | Gear 0.3.14 | /smithing (/smith), /reforge, /upgrade, /identify, /multitool, /pickaxe ... /can (tool fetch) | 1100 x 880 | NONE | SMITHING / ANVIL / IDENTIFY / TOOLS / UPGRADE (own row) | P (piece pages, upgrade rows "6 a page") | T = D of the Crafting hub row (Skyy 10-16); smithhub (Gear 0.3.15, RUNNING) adds the hub bars |
| Social > Players | Menu | (Social hub) /social | 804 x 980 | ROW | player -> player view | grid | S (804 wide) |
| Social > Party | Party 0.1.9 | /party (/p), /pc | 1414 x ~866 | MENU | - | scroll | S |
| Social > Guild | Guilds 0.1.10 | /guild, /gc | 1414 x ~980 | MENU | views (members, log, bank ...) | P (members, log) | P, S |
| Settings > Settings | Menu | /settings (/skysettings) | 1128 x 980 | ROW | 9 category tabs (Skills ... Messages) + search | P (8 rows a tab page) | T, P |
| Settings > HUD | Hud 0.3.29 | /skyyhud (/shud) | 1128 x ~400 launcher | MENU | - | - | a launcher with 2 buttons; the Home HUD shortcut already skips it (Skyy 10-16) = D |
| Settings > Edit shortcuts | Menu | (opens Home in edit mode) | - | - | - | - | D of Home's own Edit shortcuts button |
| Settings > Mods | Menu | (admin / modsHelp) | 804 x 980 | ROW | - | P | S |
| Settings > Server Setup | Menu | /modconfig (/serversetup) | 1128 x 980 | ROW | per-mod categories | P (7 rows) | O (#142030 rows), P |

### 1.2 Windows outside the hubs (opened by a block, NPC, item, or an admin command)

| Window | Mod | Reached by | Size | Inner rows | Flags / notes |
|---|---|---|---|---|---|
| HUD editor / widget settings / widgets list | Hud | Settings > HUD, /skyyhud | full screen / ~1320 x 924 / ~1100 x 404 | 4 config cats | the editor is full screen (stays) |
| Pocket craft window | Sacks | inventory crafting | small | - | stays (vanilla inventory side) |
| Fishing Bench | Fishing 0.1.8 | the bench block, /fishing | 1000 x 760 | Parts / Rig / Fillet and Sell | ok as a window |
| Traveling Merchant shop | Merchants | the NPC | 900 x 720 | Weapons / Mounts / Pet eggs | ok as a window |
| Shard menu / Totem bench / Totem / Exit | Shards 0.4.1 | shard blocks, /totem | 1100 x 860 / 640-660 wide | Collect / Upgrades / Islands / Totems; Craft / Tier up / Bench | ok as windows |
| Quest board / NPC dialog / Welcome | Quests | board block, NPC, first join | ~1000 / 900 x 430 / 760 x 420 | - | ok as windows |
| Rebirth (Nexus of the Void) | Rebirth 0.3.4 | /rebirth | 1120 x 952 | tree view / node view | no hub bars; a player menu that lives nowhere in the hubs |
| Trade + trade settings | Essentials 0.1.11 | /trade request | 516-col window | - | O |
| Warp list | Essentials | /warp page | 900 x 250 / 1000 x 330 / 1120 x 880 | - | O, D of World > Teleport (warps fill its grid) |
| Ranks | Ranks 0.1.1 | admin command | 1120 x 860 | Ranks / Players / Settings / Grants / Members (190 x 40 tabs) | admin; P; S |
| Admin page (ops) | Menu | admin | 1160 x 960 | Server / Economy / Players / Diagnostics | admin; S |
| Explore admin | Exploration | /exploreadmin | decorated window | - | admin |

**Chat-only (no page, fine):** Coins (/balance /bal /coins /purse, /pay), Cooking (/cooking, /campfire - numbers show on the Skills
stats page), WorldGen (/zone), Essentials (/tpa ..., /msg /w /tell /r, /fly), Mobs, Armory, Islands (/island alone teleports).

### 1.3 What is wrong today (the clutter list)

1. **Four header styles:** BIG (Home, Teleport), ROW (Menu pages, Crafting), MENU "< Menu" (17 pages in 15 mods), NONE (Void, Requip,
   Accessory Bag, Smithing, Rebirth, Hatch). Skyy saw it: "crafting has all of the tabs across the verry top. but nont of the others seem to."
2. **The top row has two sizes** (BIG 48 px on Home, ROW 30 px elsewhere). Skyy: keep Home's size everywhere.
3. **13 page widths** (804, 974, 1054, 1094, 1114, 1128, 1200, 1254, 1264, 1300, 1414, 1454, 1600) and heights 755 - 980: the bar jumps
   on every tab click, even inside one tab (Skills 974 vs Your Stats 1114; Trees 1454 / 1600 / 1114; Bazaar vs AH).
4. **Old inner tab rows** that duplicate or deepen the hub rows: Smithing's own row, Trees' two tree rows, Your Stats' 5 tabs (3 levels
   deep), Islands' 5 tabs, Explore's 4, Settings' 9 categories, Accessory Bag Bag / Craft.
5. **PREV / NEXT paging on 13 pages** (Crafting, Collections, Bazaar, AH, Islands, Explore, Guild, Pets, Accessories, Settings, Server
   Setup, Mods, Smithing) where Skyy wants scroll lists.
6. **Duplicates:** Your Stats > Skills tab (= the Skills list), Your Stats > Profile tab (= Profiles + Home's You panel), /bank page (=
   the Vault's coin panel), Settings > Edit shortcuts (= Home's button), Settings > HUD launcher (= the HUD editor), Essentials warp list
   (= World > Teleport), the Hatch window (= Pets > Hatchery after petmenu), help text "/craft (or /recipes)" while /recipes belongs
   to Collections.
7. **Button sizes:** row buttons 30 / 48, tabs 44 / 56, sub-tabs 32 (Skills) / 36 (Market switch) / 40 (Ranks) / 44 (Islands, Explore).

---

## 2. MERGE / CUT proposals (ranked by clutter saved)

"Replace, don't add": each line says which commands go. **The 10-16 merges already built** (Stats+Skills, Class+Trees, Bank+Vault,
Bazaar+AH, Recipes+Collections, Crafting hub, Void Charms, pet tabs) are not repeated here.

| # | Proposal | Replaces | Commands | Saved | Mark |
|---|---|---|---|---|---|
| M1 | **Every page gets the same header** (BIG row 1 + row 2) - the sweep. All "< Menu" buttons, the small ROW, and the NONE pages (Void, Requip, Void Charms, Smithing, Rebirth) go | 4 header styles -> 1 | none | biggest: every page | [recommended] |
| M2 | **One page size for every hub page: 1600 x 980** (Home's width, so row 1 is pixel-identical) | 13 widths | none | the bar never jumps | [recommended] (Q1) |
| M3 | **Crafting hub = 4 tabs:** Crafting / Smithing / Anvil (sub-tabs Reforge, Identify) / Tools (sub-tabs Your tools, Upgrade). Gear's own SMITHING / ANVIL / IDENTIFY / TOOLS / UPGRADE row goes | 6 tabs + Gear's inner row | /reforge, /identify, /upgrade open their sub-tab (Q3); no new words | 2 tabs + 1 row | [recommended] (Q6) |
| M4 | **Your Stats = one scroll list** with section heads (Main, Combat, Gathering) instead of 5 inner tabs; its Skills and Profile tabs are cut (duplicates) | 5 tabs, 3 tab levels | none | 1 row + 2 duplicates | [recommended] (Q4) |
| M5 | **All PREV / NEXT pagers -> scroll lists** (13 pages). Exception: Vault pages (each page = real storage slots) | 13 pagers | none | 13 pagers | [recommended] |
| M6 | **Trees: ONE sub-tab row** (Class first, then the 9 skill trees, sorted as the Skills list) instead of two rows | 2 rows | none | 1 row | [recommended] |
| M7 | **Settings hub: cut Edit shortcuts** (Home has the button); **HUD tab = the widget list page** with an "Open HUD editor" button (no launcher page) | 2 pages | none (/skyyhud still opens the editor) | 2 pages | [recommended] (Q5) |
| M8 | **Settings page: one scroll list** with category section heads + the search box it already has, instead of 9 category tabs + 8-row pages. Server Setup: kit rows (vanilla look) + scroll instead of 7-row pages | 9 tabs + 2 pagers + old style | none | 1 row + 2 pagers | [recommended] |
| M9 | **Bank page goes**: /bank opens Storage > Vault (the coins panel is on top) | 1 page | /bank = alias of /vault's tab (Q3) | 1 duplicate | [recommended] |
| M10 | **Warp list page goes** (players): warps are on World > Teleport; /warp <name> stays a chat command; admin warp setup stays in Server Setup | 1 page (old style) | the page form of /warp | 1 duplicate | [recommended] |
| M11 | **Islands: 5 inner tabs -> 3 sub-tabs** Overview / Members (roles + permissions on one list) / Visitors; the "Island" tab (pick / switch island) moves into Overview | 2 tabs + 2 pagers | none | 2 tabs | [optional] |
| M12 | **Explore: 4 inner tabs -> sub-tab row** + scroll (no "< Island / Island >" pager) | 1 old row + 2 pagers | none | 2 pagers | [recommended] |
| M13 | **Quests log becomes World > Quests**, redesigned (section 2b; the 1000 x 660 plain window goes) | 1 window + 2 pagers | /quests opens the tab; no new words | 1 window | [recommended] |
| M14 | **Rebirth joins Character > Profiles as a sub-tab** (rebirth is per profile): Profiles / Rebirth | 1 hub-less window | /rebirth opens that sub-tab | 1 window | [optional] |
| M15 | **Merchants rumours -> a 3rd button of the Market switch** [BAZAAR] [AUCTION HOUSE] [MERCHANTS]; the Market hub then has ONE tab, so row 2 shows those three as its tabs (no switch row) | 1 tab + 1 switch row | /merchants opens that tab | 1 row | [optional] |
| M16 | **Admin pages under Settings > Server Setup** as sub-tabs: Setup / Ranks / Admin (ops) / Mods (Mods tab leaves row 2) | 3 windows + 1 tab | admin commands unchanged | 3 windows | [optional] |
| M17 | **No footer Close buttons**: Close = the X + Esc on every page (Home's Close button goes) | ~15 buttons | none | 1 button a page | [optional] |

After M1-M13 the hubs read: **Character** Skills / Trees / Pets / Void Charms / Collections / Profiles - **Storage** Void / Requip /
Vault - **Market** Market / Merchants (or M15) - **Crafting** Crafting / Smithing / Anvil / Tools - **World** Teleport / Island /
Explore / Quests - **Social** Players / Party / Guild - **Settings** Settings / HUD / Mods / Server Setup. No tab row ever deeper than
one sub-tab row.

---

## 2b. The Quests page (SkyyQuests) - a calmer layout

Skyy 2026-10-16 (screenshot: the QUESTS window - "< LINE  Getting Started  LINE >", "11 / 23 done - every task counts the moment you do
it, in any order - Skip any task you like", 10 rows mixing green "Done: ..." rows with long reward strings ("done +25 coins +2 Oak
Sapling +25 coins +3 Cop..."), grey "coming soon" rows, "< PREV page 1 of 3 NEXT >", footer TRACK / CLAIM REWARDS / HIDE TUTORIAL /
CLOSE, no hub bars): "quests menu is crowded and confusing."

**Today (Quests 0.3.4, QLogPage):** a plain 1000 x 660 window, one line at a time behind "< Line / Line >", 10 rows a page with
PREV / NEXT, every row = name + a long progress / reward string, done and "coming soon" rows mixed in with open ones, a footer of four
buttons for the whole page (Track, Claim rewards, Hide tutorial, Close).

**After (World > Quests, the pattern page 1600 x 980):**

```
[row 1: Home Character Storage Market Crafting WORLD Social Settings]                                                  (X)
[row 2: Teleport | Island | Explore | QUESTS]
[sub-tabs: Open | Done]                                                                       [search tasks.......]
+-- QUEST LINES (left, 456) -----+-- TASKS of the picked line (middle, scroll) ------------+-- TASK (right, 456) ------+
| > Getting Started   11 / 23 ## | T1 Chop 10 logs           4 / 10  [=====-----]          | T1 Chop 10 logs           |
|   (tracked on HUD)             | T1 Mine 5 Copper Ore      0 / 5   [----------]          | Where: Zone 1 forest      |
|   Farming Basics     2 / 12 #  | T2 Craft a Copper Pickaxe          Ready to claim (gold)| Progress 4 / 10           |
|   Zone 1 Area        0 / 8     | ...                                                     | Reward: 25 coins, 2 Oak   |
|                                | + 11 done (folded - Done sub-tab shows them)            |   Sapling                 |
|                                |                                                         | [Skip]        [Claim]     |
+--------------------------------+---------------------------------------------------------+---------------------------+
| info line: "Every task counts the moment you do it, in any order."            [Track this line]  [Claim all (3)]      |
```

1. **Where it lives:** World > Quests (the HUB_TABS contract row world / quests / 40, owner SkyyQuests, command /quests). Rows 1 + 2 on
   top; the plain window goes. The Quest board, NPC dialog and Welcome windows stay windows (section 3.6).
2. **Quest lines as a list, not "< Line / Line >":** left column = every line you have (tutorial, area lines, job lines), each with
   "11 / 23" and a thin progress bar; the tracked one shows "(tracked on HUD)". Click a line to show its tasks. Lines with nothing left
   to do sink to the bottom. Sorted: tracked first, then by tier / zone, then name.
3. **Open tasks first, done folded:** sub-tab **Open** (default) lists only open and ready-to-claim tasks; one folded row at the end
   says "+ 11 done". Sub-tab **Done** lists the finished ones (green, no buttons). Skipped tasks sit at the end of Open, greyed, with
   Unskip in their detail.
4. **One clean line per task:** tier tag + task name left, "4 / 10" + a progress bar right. No reward text in the row; the reward
   shows once, in plain words, in the detail panel ("25 coins, 2 Oak Sapling"). A task whose reward is waiting shows "Ready to claim" in
   gold instead of the bar.
5. **No "coming soon" rows:** tasks or lines that are not built / not unlocked are not listed. A locked line shows ONE greyed row in the
   line list with how to unlock it ("Unlocks at Overall Level 5") - the pattern's locked rule (3.4).
6. **Scroll, not pages:** the task list is a scroll list (ROW_H_READABLE 56 rows, ~11 visible), no PREV / NEXT.
7. **Claim:** each ready task has **Claim** (Primary) in its detail panel, and the footer has **Claim all (n)** (Primary, shown only
   while n > 0). Both use the existing verified claim ledger unchanged; /quests claim = Claim all.
8. **Track:** "Track this line" moves into the footer as a toggle for the PICKED line ("Tracked on HUD" when it is the tracked one) -
   one button instead of a page-wide Track. /quests track keeps working.
9. **Hide tutorial goes from this page:** the HUD Quest Tracker is shown / hidden in Settings > HUD (where every widget is switched),
   and a finished or unwanted tutorial line is simply untracked (Track this line off). /quests hide / show keep working (same command,
   replace not add).
10. **Close button goes** (the X + Esc), the footer keeps only the info line + Track + Claim all.
11. **Skip** moves from every row into the task's detail panel (Skip / Unskip) - the rows stay clean.

Build: one lean-to-full round **q04** (SkyyQuests 0.4.0 from the SET pin 0.3.4) in sweep group S3, after kit 1.7. No saved-data change
(lines, ledger, skip list, tracked line stay as they are); the quest:fn:hud widget contract is unchanged. Test: open /quests, pick a line,
finish a task, claim it, claim all, skip / unskip, track another line (HUD widget follows), Done sub-tab, a locked line row.

---

## 3. THE PATTERN (every hub page follows this; builders check it, the kit asserts it)

### 3.1 The layout stack (top to bottom, inside one 1600 x 980 page)

| # | Part | Size (px) | Kit piece (kit 1.7, section 4) | Check |
|---|---|---|---|---|
| 0 | Title bar: the sky crest, the page title (= the hub title, e.g. "Character"), the X | 38 high (TITLE_H, never scaled), X 32 at Right -8 | `hub_page()` | assert |
| 1 | **Row 1 = Home + 7 hubs**, Home's size: buttons 48 high, 6 apart, padding 10 / 6, 32 px item icon + 6 gap, label 18 bold (shrinks to 12), 8 below; button width = (1552 - 7 x 6) / 8 = **188**; active hub = selected style | 48 + 8 | `HUB_BIG_ROW_*` (moved from SkyyMenu BR_*) | assert: same constants, byte-compare with Home |
| 2 | **Row 2 = this hub's tabs**, Teleport's size: 56 high, 6 apart, the 48 px tab icon behind the word, label 20 bold (shrinks to 14), min width 150, 8 below; equal widths across 1552 | 56 + 8 | `HUB_BIG_TAB_*` (moved from BT_*) | assert_hub_fits (n x 150 + gaps <= 1552) |
| 3 | Sub-tab row (optional, one only): Secondary small buttons, the active one Primary, 32 high (BTN_SMALL_H), min 150 (PRIMARY_SMALL_W), 5 apart (TAB_GAP), left aligned, 8 below. Right side may hold a search box (SEARCH_H 30) or the purse line | 32 + 8 | `sub_tabs()` | assert: at most 1 sub row, no tab_row() on hub pages |
| 4 | Content | what is left: **894 - 64 - 72 - (40) - (58) = 660 - 758 high**, 1552 wide | `hub_page().body_h` | assert_menu_page |
| 5 | Footer (optional): info / hint line left (16 px, 2 lines max), buttons right, primary right-most, 48 high (BTN_BIG_H), 10 above | 48 + 10 | `footer()` | assert height |

Page = 38 title + 2 x 24 sky padding (THEME_PAD["sky"]) + rows. Width 1600 = MAX_PAGE_W, height 980 = MAX_PAGE_H (1080p with the
client margins). **Pages never shrink row 1 or row 2; the content shrinks.** Every hub page, every sub-page (a skill's stats, a
collection, a piece page) shows rows 1 + 2 with its tab selected; sub-pages add a "< Back" as the first sub-tab-row button.

### 3.2 Look (vanilla, from the kit only)

- **Fonts:** Default (Nunito Sans) for everything; Secondary only for the title-bar title (TITLE_SIZE 15) and tile names. Text sizes:
  the kit's "readable" scale (rows 18 / 15, captions 15, sections 16). Never type a font size by hand outside the kit kinds (LABELS).
- **Colours:** kit COLOR names only (vanilla values proven against Assets.zip): text #96a9be, rowName #d6e4ee, caption #878e9c,
  gold #E8A93B (costs), success #39f493, error #ff6b6b, disabled #797b7c, selected bar #4274a5, wells #000000(0.15). Item names in
  RARITY / QUALITY colours. Never a hex in a build script (lint kit_color_warnings).
- **Frames:** the sky theme (HUB_THEME = "sky": `theme_*` helpers, Sky Window textures under Common/UI/Custom/SkyyKit). No #0b1524 /
  #142030 panels (old style).

### 3.3 Lists

- **Scroll, not pages:** `scroll_list()` inside a `list_well()`; no `pager()` and no "< Prev / Next >" on hub pages (exception: Vault
  storage pages). A list longer than **200 rows** shows the first 200 + a "Show more" row at its end (UNVERIFIED limit: probe the
  client's speed with 200 / 500 rows once in SkyyUiProbe before the sweep).
- **Row heights:** text rows ROW_H_READABLE 56 (name 18 + sub line 15); item rows `list_card` 84 (icon 60 in a 64 frame); item grids
  `item_grid` 74 px slots; gaps ROW_GAP 3 / LIST_CARD_GAP 4. About 6 - 12 rows visible, filling the content height (Skyy 10-16
  crafting: "scale up ... reduce the items show on page to 6 and allow scroll").
- **Sort by tier, then name** everywhere (shops, crafting, recipes, collections, bags): `tools/tier_tags.py`; farming lists group each
  crop as crop, Enchanted crop, seeds, Eternal seeds; untiered first. Every tiered row shows its tier tag first ("T3 Iron - ...").
- **Search:** one search box (SEARCH_H 30) at the right of the sub-tab row when a list has more than ~30 rows.

### 3.4 Detail panel, buttons, states

- **List + detail:** list on the left, detail panel on the right, **456 px wide** (Home's side panels), a `panel("well")`: 64 px item
  icon + name (tipName 18, rarity colour, tier tag first), property rows, then the action buttons at the panel's foot.
- **Buttons:** one **Primary** per view = the main action (Buy, Craft, Upgrade, Hatch); everything else Secondary. Normal 44 high (172
  min wide), big 48 in the footer, small 32 in sub-tab rows and list rows (ROW_ACTION_W 92). Labels say the action and its cost ("Craft
  x10 - 450 coins"). Sounds from the kit (SOUNDS).
- **Dangerous actions** (delete, respec, sell all, fuse): click once -> the label turns into "Click again to ..." for 5 s (the Trees respec
  pattern), or `confirm_view()` for big ones. Never a page-opening confirm from a hover.
- **Empty state:** a centred `captionLight` line inside the well: what is missing + how to get it ("No pets yet - hatch an egg in the
  Hatchery").
- **Locked:** a tab whose mod is not loaded is hidden; content locked by progress shows greyed (disabled colour) with how to unlock it
  ("Unlocks at Farming Collection III"), never hidden.
- **Info line:** status / result text in the footer's left (status_line), never a chat line for something the page can show.

### 3.5 Commands

- Every hub tab has ONE command (its row in `SUI.HUB_TABS`) + the hub commands (/character /storage /market /crafting /travel /social
  /settings). A merged or renamed page **replaces** commands, never adds: new words in, old words out (Void Charms: /charm /charms /ch
  replace /accessories /acc /accbag). Whether old words of merged pages stay as aliases of the host: Q3.
- No two mods register the same word (lint already; /recipes = Collections only - fix the Menu help text "/craft (or /recipes)").
- Every player command / variant has `setPermissionGroups(hytale:Adventurer)` (HANDOFF section 3; lint perm_group_leaks).

### 3.6 Windows (block / NPC / item / admin pages, section 1.2)

Not hub pages: no rows 1 + 2. They use `page_shell(kind="decorated")` in the sky theme, the same list (3.3), detail and button (3.4)
rules, a title naming the block or NPC, one optional tab row (32 px sub-tab style), and fit 1600 x 980. Admin pages follow the same.

### 3.7 What can be checked automatically

| Check | Where | What it catches |
|---|---|---|
| `SUI.assert_menu_page(w, h, parts)` (new) | every hub page builder | size != 1600 x 980, content taller than the room, more than one sub row |
| `tools/test_skyyui_hubs.py` byte compare | kit | row 1 / row 2 markup = Home's, for every hub |
| `tools/ci/lint.py` new rule `menu_pattern` | all SET scripts | "< Menu" / HUB_MENU_TEXT used, `hub_shell(` without the 1.7 big rows, `pager(` or "< Prev" on a hub page, `tab_row(` on a hub page, page_shell for a page that has a HUB_TABS row |
| existing lint | all | kit_color_warnings / kit_style_warnings (hand-written colours, styles), grid_slot_warnings, perm_group_leaks |
| `tools/ci/crosscheck.py` | the set | two mods with the same command word; a HUB_TABS tab nobody puts |
| tier-sort self-test (each list builder) | per mod | a list built without `tier_tags` order |

---

## 4. SWEEP plan

**K - kit 1.7 first (alone, with SkyyMenu).** After smithhub (Gear 0.3.15 + Menu 0.3.34) lands, because it adds the first top-row kit
helper. `tools/skyyui.py` 1.7 (additive; KIT_HUB_VERSION "1.7"): `hub_page(prefix, hub, tab, sub=None, footer=False)` = title bar +
BIG row 1 + big row 2 + optional sub-tab row + body + footer at 1600 x 980; constants `HUB_BIG_ROW_*` / `HUB_BIG_TAB_*` (= SkyyMenu's
BR_* / BT_*), `SUB_TAB_*`, `FOOT_*`, `DETAIL_W = 456`; the HubBar Java draws the big rows (both copies: HUB_BAR_JAVA in each jar and
SkyyCore's com.skyy.core.ui.HubBar -> SkyyCore 1.0.1); `assert_menu_page`; `tools/test_skyyui_hubs.py` byte compare; lint rule
`menu_pattern` (warn first, fail after the sweep); guide section in `research/Vanilla-UI-Style-Guide.md`. SkyyMenu 0.3.35 moves Home /
Teleport onto the kit helper (byte-identical rows; Teleport becomes 1600 wide) and does M7, M8, M10-help-text, M16 if picked.
Full round (kit + several mods). One builder (Opus) + critics.

**Then the sweep, 2 groups at a time (usage pacing), no two groups touch the same mod:**

| Group | Mods (each its own patch file) | Also does | Waits for |
|---|---|---|---|
| S1 Character | Skills, Trees + Classes, Pets, Collections, Profiles | M4 (Your Stats list - Menu half rides K or S4), M6, M14 (Rebirth sub-tab: + SkyyRebirth) | petmenu (Pets 0.4.1) |
| S2 Storage + Market | Sacks (Void + Crafting page), Wardrobe, Vault + Bank, Bazaar + Auctions, Merchants | M5 for those, M9, M15 if picked | sacks0814 (Sacks 0.8.14) |
| S3 Crafting + World + Social | Gear, Islands, Exploration, Quests (q04 = section 2b), Party, Guilds | M3, M11, M12, M13 | smithhub (Gear 0.3.15) |
| S4 Settings + Void Charms + windows | Hud, Accessories (Void Charms page), Ranks, Essentials, Fishing, Shards, Rebirth (if M14 not picked) | M7 (Hud half), windows pattern 3.6 | AP1 (Accessories 0.5.22) |

Order: K -> (S1 + S2 in parallel) -> (S3 + S4 in parallel) -> lint `menu_pattern` switched to FAIL. Each group = a full round
(skywynn-round; several mods, commands), cross-check `--baseline`, smoke test, deploy together per group. A page not yet swept keeps
working (kit 1.6 pages still show their old header), so groups can deploy one at a time. Trees + Classes, Vault + Bank, Bazaar +
Auctions always build in the same group (shared merged tabs).

---

## 5. Questions for Skyy (default in [brackets])

1. **One page size:** every hub page 1600 x 980 (Home's width), so the top row is exactly Home's and never moves? Home grows from 926
   to 980 high. [Yes, 1600 x 980 for all]
2. **Row 2 (the hub's tabs) size:** big like the Teleport page (56 px, icon behind the word) on every page, or the smaller 44 px tabs
   most pages have now? [Big, like Teleport]
3. **Old commands of merged pages** (/bank, /ah, /stats, /class, /recipes, /reforge, /identify, /upgrade): keep them as the same command
   opening the merged page (nothing new added), or remove them? [Keep them, opening the merged page]
4. **Your Stats:** one scroll list with section heads (Main, Combat, Gathering), dropping its own Skills and Profile tabs (duplicates)?
   [Yes]
5. **Settings hub:** drop the Edit shortcuts tab (Home has the button) and make the HUD tab the widget list with an "Open HUD editor"
   button? [Yes]
6. **Crafting hub tabs:** Crafting / Smithing / Anvil (Reforge + Identify inside) / Tools (Upgrade inside), instead of 6 tabs? [Yes, 4 tabs]

Optional cuts (M11, M14, M15, M16, M17) ride their group with the default "no" unless Skyy says yes.
Quests page (2b): no open choice - claim keeps both (per task + Claim all); defaults as written unless Skyy says otherwise.

## Skyy's answers (2026-10-16, word for word in docs/answered/ui.md)

1. All hub pages Home size (1600 x 980): YES. 2. Row 2 big like Teleport (56 px): YES. 3. Old commands: keep the ones that still describe what
they open, drop the rest (HANDOFF section 3 rule 3). 4. Your Stats = one scroll list with headings: YES. 5. Settings drops Edit Shortcuts, HUD tab =
widget list + Open HUD editor: YES. 6. Crafting hub = Crafting / Smithing / Anvil (Reforge + Identify inside) / Upgrade (tools page; Skyy: "tools can be
rolled into upgrade"): YES. Optional cuts M11 / M14-M17: off. Build per section 4 (sweep plan).
7. Short lists fill the space (Skyy: "i dont mind scrolling, but if there are only a few items try to scale them to all fit."): a scroll list
   with few entries uses bigger rows (up to ~2x) to fill its area; it scrolls only when entries no longer fit at normal row size.
8. No back buttons, top rows always (Skyy: "I never want to have to use a back button. The menus at the top should always be there for easy
   navigation."): EVERY page and window - hubs, the Void, Requip, Rebirth, the hatch reels, detail / sub pages (a set page, one collection, a
   skill's stats) - shows row 1 (hubs) + row 2 (that hub's tabs). No BACK, '< MENU' or close-to-return buttons: a sub view is a sub-tab or an
   in-page selection that the top rows can always leave. The sweep audits every page id against this (a lint check: no element labelled Back /
   < Menu on a hub page).
9. Requirements = a colour list (Skyy 2026-10-17: "do a color coded list (level 10 (IN RED) :6 my lvl  Copper 25 (in green) (use this pattern
   everywhere"): one requirement per line - 'Farming Lv 10 : 6' red when not met, 'Copper Ingot 25' green when met ('(need N)' may follow a red
   item); no explanation sentences. Every upgrade / tier-up / craft cost / egg / Void upgrade / collection / rebirth requirement uses it.
   Kit helper wanted: SUI.req_list(rows) (name, need, have, met) so every page draws it the same.
