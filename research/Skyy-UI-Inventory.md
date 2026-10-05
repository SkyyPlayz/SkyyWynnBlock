# Skyy UI Inventory (vanilla-look pass)

Research for the vanilla UI pass (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and feel vanilla",
HANDOFF section 2 rule 0). Written 2026-09-29, read-only research: nothing in any mod or tool was changed. Every fact below was read from the
live-set build scripts (`tools/deploy_set.py` SET, 22 mods) and, for the vanilla side, from the game's own `Assets.zip` (read with Python
`zipfile`, nothing extracted). Line numbers are lines of the named build script as it stands today (the pinned version in SET); they will
move as soon as a builder derives the next version, so always re-find a block by its class / method name first.

Companion file (written in parallel by another research task, only its header was read here): `research/Vanilla-UI-Research.md` = the catalogue of every vanilla
building block with inline-ready literals and a proposed kit API. This file answers the other half: what exists in the live set today and how to move it.

Paths in this file are repo-relative with forward slashes. "Old style" = the dark-blue custom panel look (`#0b1524(0.96)` root, solid-colour
buttons); "vanilla" = a page built from the game's own frame textures, styles and sounds (`Common/UI/Custom/Common.ui`, `Sounds.ui`).

## 0. Key findings (read this first)

1. **Scope confirmed.** 22 mods in SET. 20 build inline UI. **SkyyCoins has none** (chat commands `/balance /pay /coinsgive /deathpenalty`; it only
   publishes `coins:<uuid>` on the bridge for SkyyHud's Coins widget and the pages of other mods). **SkyyCooking has none** ("No pages (chat only)",
   header line 301; commands `/cooking`, `/cookadmin`); its player-facing numbers reach the Skills Stats page through the bridge hook
   `skill:stats:Cooking`, its settings through Menu's Server Setup / Settings pages. Neither needs a restyle.
2. **32 page classes + 1 HUD (10 widgets) in 20 mods.** 6 page classes are already vanilla: RankPage (Ranks), ReforgePage + IdentifyPage (Gear),
   SacksPage "Magic Bags" (Sacks 0.7.7), VBuyDlg (Vault 0.1.3), and OverallPage (Skills 0.4.6, partial). **26 page classes + the HUD are old style.**
   Vanilla state is per PAGE, not per mod: Vault's `VaultPage`, Sacks' `CraftPage` and the other two Skills pages are still old style.
3. **The vanilla look is proven on paper only.** Only Ranks (55 style values + 21 textures/sounds) and Vault's confirm window (32 + 13) prove
   their values against `Assets.zip` at build time (`VANILLA_CHECK`). No page that uses inline `Common/...png` frame textures, `FontName: "Secondary"` or
   `Sounds:` has been confirmed on Skyy's client yet (Vault header UNVERIFIED V1; Gear ships a `ui.frames` config switch as a safety valve; rounds 8 and 9
   are untested in game). **Gate the whole campaign on one in-game look at Ranks, Gear, Sacks bag page, Vault confirm window and Skills Overall.**
4. **Every old page is the same recipe**: root `Group #SkyyX { Anchor: (Width: W, Height: H); Background: #0b1524(0.96); Padding: ...; LayoutMode: Top; }`,
   a 2-3 px accent stripe in a per-mod colour, a 22-34 pt bold title, `TextButton` with `Background: #solid` colour triples (5 colour families),
   rows `#142030(0.9)`, TextField boxes `#16263a` with placeholder `#6e7da1`, layout done with empty `Label { Anchor: (Width: n) }` spacers, fonts as
   small as 8-13 pt (Hud editor 8-11, Trees nodes 10-11, Skills 10-14, Accessories 11-13) against Skyy's BIG-readable rule.
5. **The Java helper code is copy-pasted across mods** (counts in section 4): `jsonStr` x12 mods, `safe` x13, `style(bg,hov,press,fg,fs)` x6,
   `colorOf`/`textOf` status-mark helpers x8, python-side button-style builders x4 (Trees, Exploration, Menu, Auctions) plus inline copies in 8 more.
6. **SkyyMenu is a fan-out point.** Its Server Setup page (`AdminPage`, 9 views) renders the config rows of 18 mods through the kit
   (`tools/skyycfg.py`, no UI code there) and its Settings page renders the player switches of 14 mods. Restyling Menu restyles all of them at once;
   the mods themselves contain no markup for those rows. (Exceptions with their OWN admin pages: Ranks editor, Hud editor, Essentials
   `/tradeadmin config` + `/warpadmin`, Exploration `/exploreadmin`.)
7. **Fragile pages** (keep their geometry, restyle only frames / buttons / text): Hud EditorPage (1330 x 930, a 32 x 18 draggable `ItemGrid` canvas of
   576 slots with 1 px icons and hand-drawn previews behind it), Essentials TradePage (page + `TWindow` container window + read-only `ItemGrid` columns),
   Sacks SacksPage (page + empty container window so the inventory shows below), Menu MenuPage (9 x 6 `ItemGrid` launcher with tooltips), Vault (chest window +
   page), Trees node grid (12 `Button` cards with `ItemIcon` in 6 tier rows).
8. **Engine popups are already vanilla and need no restyle**: `NotificationUtil.sendNotification` (Classes, Gear), `EventTitleUtil` banners + sounds
   (Exploration). Item tooltips / qualities are asset JSON or `ItemGridSlot.setDescription` markup (Menu, Gear, Sacks, Accessories) and are outside this inventory
   except where noted.
9. **The economy trio is scheduled to merge**: Coins + Bank + Bazaar + Auctions become SkyyEconomy 0.1 (RESUME step 5, `docs/plans/SkyyEconomy-Plan.md`). Restyle their
   pages on the shared kit anyway (the merge can copy them), but keep those builds thin.
10. **Patch-based rule for the restyle versions.** 14 of the 20 mods derive by patch script (`tools/<mod>_<ver>_patch.py`, edit the patch, never the generated
    file): a restyle needs a NEW patch that `rep()`-replaces whole page blocks with asserts. Copy+edit mods (no patch): Party, Bank, Exploration, Gear, Vault, Ranks.
    Never re-run the old patches of Skills 0.4.5, Trees 0.2.3, Classes 0.1.6, Vault 0.1.2 (edited by Skyy, commit ab75b6c); their 0.4.6 / 0.2.4 / 0.1.7 / 0.1.3 are the live pins.

## 1. Summary table

Root sizes are the Anchor Width x Height of the page root. "Old" / "Vanilla" refer to the frame and buttons of that page.

| # | Mod (pin) | Script (lines) | Patch-based? | Pages (views) | State now | Root size(s) | Risk | Batch |
|---|---|---|---|---|---|---|---|---|
| 1 | SkyyAccessories 0.4.4 | SkyyAccessories/build_skyyaccessories_0.4.4.py (1781) | yes, tools/acc_0_4_4_patch.py (from 0.4.3) | 1: AccPage bag | Old | 640 x 630 | MEDIUM | B1 |
| 2 | SkyyAuctions 0.1.2 | SkyyAuctions/build_skyyauctions_0.1.2.py (4718) | yes, tools/auctions_0_1_2_patch.py (from 0.1.1) | 1: AhPage (browse, item, create, manage) | Old | 1120 x 880 | HIGH | B4 |
| 3 | SkyyBank 0.1.3 | SkyyBank/build_skyybank_0.1.3.py (1315) | no (copy+edit) | 1: BankPage | Old | 1100 x 680 | LOW | B1 |
| 4 | SkyyBazaar 0.1.2 | SkyyBazaar/build_skyybazaar_0.1.2.py (1832) | yes, tools/bazaar_0_1_2_patch.py (from 0.1.1) | 1: BzPage | Old | 1080 x 640-828 | MEDIUM | B4 |
| 5 | SkyyClasses 0.1.7 | SkyyClasses/build_skyyclasses_0.1.7.py (3836) | yes, tools/classes_0_1_7_patch.py (from EDITED 0.1.6) | 1: ClassPage | Old | 1000 x 900 | LOW | B1 |
| 6 | SkyyCoins 0.1.5 | SkyyCoins/build_skyycoins_0.1.5.py (695) | no page (no tools/coins_0_1_5_patch.py) | 0 | none | - | none | - |
| 7 | SkyyCollections 0.2.3 | SkyyCollections/build_skyycollections_0.2.3.py (3795) | yes, tools/coll_0_2_3_patch.py (from 0.2.2) | 1: CollPage (home, category, detail, recipes) | Old | 1120 x 840 | MEDIUM | B2 |
| 8 | SkyyCooking 0.1.2 | SkyyCooking/build_skyycooking_0.1.2.py (2305) | yes, tools/cooking_0_1_2_patch.py (from 0.1.1); no page | 0 | none | - | none | - |
| 9 | SkyyEssentials 0.1.5 | SkyyEssentials/build_skyyessentials_0.1.5.py (5582) | yes, tools/essentials_0_1_5_patch.py (from 0.1.4) | 3: TradePage, TCfgPage, WarpPage | Old | 1100 x 800/280; 1060 x ~750; 1120 x 880 / 1000 x 330 / 900 x 250 | HIGH | B6 |
| 10 | SkyyExploration 0.2.1 | SkyyExploration/build_skyyexploration_0.2.1.py (6664) | no (copy+edit of 0.2) | 2: ExplorePage (4 tabs), AdminPage (3 tabs) | Old | 1120 x 800; 1120 x 900 | MEDIUM | B3 |
| 11 | SkyyGear 0.1 | SkyyGear/build_skyygear_0.1.py (6784) | no (new script) | 2: ReforgePage, IdentifyPage | Vanilla (hand-reviewed, not build-proven) | 1100 x 880 x2 | LOW (migrate to kit) | B9 |
| 12 | SkyyGuilds 0.1.3 | SkyyGuilds/build_skyyguilds_0.1.3.py (3652) | yes, tools/guilds_0_1_3_patch.py (from 0.1.2) | 1: GuildPage (no guild, guild, bank log) | Old | 1120 x 660 / 900 / 900 | MEDIUM-HIGH | B2 |
| 13 | SkyyHud 0.3.10 | SkyyHud/build_skyyhud_0.3.10.py (2603) | yes, tools/hud_0_3_10_patch.py (from 0.3.9) | 3 pages (EditorPage, WidgetsPage, SettingsPage) + HUD (10 widgets) | Old | 1330 x 930; 900 x 770; 1500 x 790; HUD full screen | HIGH | B8 |
| 14 | SkyyIslands 0.5.3 | SkyyIslands/build_skyyislands_0.5.3.py (5054) | yes, tools/islands_0_5_3_patch.py (from 0.5.2) | 1: IslandMenuPage (5 tabs) | Old | 1240 x 900 | MEDIUM-HIGH | B2 |
| 15 | SkyyMenu 0.3.3 | SkyyMenu/build_skyymenu_0.3.3.py (6378) | yes, tools/menu_0_3_3_patch.py (from 0.3.2) | 3: MenuPage, SettingsPage, AdminPage (9 views) | Old | 800 x 952; 1120 x 930; 1120 x 930 | VERY HIGH | B7 |
| 16 | SkyyParty 0.1.5 | SkyyParty/build_skyyparty_0.1.5.py (1500) | no (copy+edit since 0.1.3) | 1: PartyPage | Old | 1240 x 840 | LOW-MEDIUM | B1 |
| 17 | SkyyProfiles 0.1.2 | SkyyProfiles/build_skyyprofiles_0.1.2.py (2759) | yes, tools/profiles_0_1_2_patch.py (from 0.1.1) | 1: ProfilePage (list, create) | Old | 1000 x 900 | LOW-MEDIUM | B1 |
| 18 | SkyyRanks 0.1.1 | SkyyRanks/build_skyyranks_0.1.1.py (4054) | no (copy+edit) | 1: RankPage (ranks, rank x3, players, player, confirm) | Vanilla, build-proven (55 + 21) | 1120 x 860 | LOW (migrate to kit) | B9 |
| 19 | SkyySacks 0.7.7 | SkyySacks/build_skyysacks_0.7.7.py (4619) | yes, tools/sacks_0_7_7_patch.py (from 0.7.6) | 2: SacksPage (vanilla), CraftPage (old) | Mixed | 1000 x 640; 1000 x 830 | HIGH (CraftPage) | B5 |
| 20 | SkyySkills 0.4.6 | SkyySkills/build_skyyskills_0.4.6.py (9651) | yes, tools/skills_0_4_6_patch.py (from EDITED 0.4.5) | 3: SkillsPage (+Top 10), StatsPage, OverallPage | Old x2, OverallPage partial vanilla | 640 x 690; 960 x 795 x2 | MEDIUM | B3 |
| 21 | SkyyTrees 0.2.4 | SkyyTrees/build_skyytrees_0.2.4.py (4270) | yes, tools/trees_0_2_4_patch.py (from EDITED 0.2.3) | 1: TreePage (6 trees) | Old | 1000 x 660 | MEDIUM-HIGH | B3 |
| 22 | SkyyVault 0.1.3 | SkyyVault/build_skyyvault_0.1.3.py (4155) | no (copy of EDITED 0.1.2 + edit) | 2: VaultPage (old), VBuyDlg (vanilla, build-proven 32 + 13) | Mixed | 1040 x 640; 700 x 300 | LOW | B1 |

Totals: 22 mods, 20 with UI, 32 page classes (26 old, 5 vanilla, 1 partial) + 1 HUD of 10 widgets.

## 2. What "vanilla" means here: the vocabulary a shared kit has to carry

### 2.1 Prior art already in the live set (reuse, do not redo)

| Where | What it holds | Lines | How it is proven |
|---|---|---|---|
| SkyyRanks 0.1.1 `RankUI` (+ `vlab()`, `vbtn()`, `V_SND`, `V_SND_NO`, `_check_ui()`) | The most complete kit: @DecoratedContainer frame, title label, Secondary / Small Secondary / Destructive / Primary / Tertiary (+`_Active`) text buttons with ButtonsLight / ButtonsCancel sounds, InputBox text field, WorldEventListRow rows, WorldEventSectionLabel heads, separator, status colours, confirm view. 84 named markup strings + a height/width budget assert per page. | script 614-901 (`V_SND` 635, `vlab` 641, `vbtn` 646, `UI` dict 674-772, `_check_ui` 775, `VANILLA_CHECK` 819, `VANILLA_FILES` 877, emit `RankUI` 898) | `VANILLA_CHECK`: 55 (vanilla document, text) pairs + 21 textures / sounds checked against `Assets.zip` at every build; refuses to build if a value drifts |
| SkyyVault 0.1.3 `VBuyDlg` (`DLG_*`, `BTNP`, `BTNS`) | A confirm dialog copied from `Pages/PrefabEditorExitConfirm`: frame, `#ffcc00` question (30 pt), `@DefaultLabelStyle` message, red note, centred Primary (SaveSettings sound) + Secondary (ButtonsCancel) row. | script 1952-2120 (`DLG_HOVER` 1967, `VANILLA_CHECK` 1988, files 2023, `VBuyDlg.build` 2097) | `VANILLA_CHECK`: 32 values + 13 textures / sounds |
| SkyyGear 0.1 `GearUi` (`frame`, `btn(kind 0-3)`, `lbl`, `rowStyle`, `scroll`, `vsep`, `infoColor/infoText`, `tex()`) + `GearDefs.C_*` colours | Frame with decorations, Primary / Secondary / Destructive / Disabled(`Disabled.png`) buttons, `ShrinkTextToFit` labels, ItemRepairElement row hover, vanilla scrollbar textures (`TopScrolling`), vertical separator. `ui.frames` (Server Setup, default ON) switches every texture and sound OFF for flat colours (safety valve if an inline texture path does not resolve). | script 5450-5560 (`GearUi`), 1265-1270 (`C_GRAY #878e9c`, `C_LABEL #96a9be`, `C_GOLD #E8A93B`, `C_OK`, `C_BAD`), 625 (config row), 1529 | Hand-reviewed only (no `VANILLA_CHECK`); the comment at 5450 says "FOR THE SHARED HELPER (RESUME step 5)" |
| SkyySacks 0.7.7 `SacksPage` (`V_SND`, `V_LBL`, `V_BTN`, `V_CELL`, `tabStyle`, `iconBox`) | Frame, Small Secondary buttons, Tertiary tab buttons (Tertiary_Active selected) in the bag rarity colour, item cell = BarterTradeRow card (`#252f3a`, hover gold `#c9a050`, pressed `#a08040`). | script 2222-2252 | Not build-proven |
| SkyySkills 0.4.6 `OverallPage` (`VAN_HEAD`, `VAN_PANEL`, `VAN_TITLE`, `VAN_BTN`) | The @Container variant: `ContainerHeaderNoRunes.png` (HorizontalBorder 35) + `ContainerPatch.png`, no decorations, no sounds, no `FontName`. Progress bar colours `#1a2030` / `#aa7c4a` copied from @CircularProgressBar. | script 8591-8697 (`VAN_*` 8601-8618) | Asserts the textures exist in the client folder `Client/Data/Game/Interface`; values not checked |
| SkyyAccessories 0.4.4 | Rarity text colours read at BUILD time from `Server/Item/Qualities/<Rarity>.json` `TextColor` in `Assets.zip` | script 281-290 (`RARITY_COLORS`) | Reads the game file itself |
| SkyyClasses / SkyyGear / SkyyExploration | Engine popups: `NotificationUtil.sendNotification` (Warning / Success), `EventTitleUtil.showEventTitleToPlayer` + `SoundUtil` discovery sounds | Classes 1933, 2435; Gear 2493; Exploration 3668, 4178 | Vanilla by construction |

### 2.2 The values Ranks / Vault / Gear already copied from `Common.ui` + `Sounds.ui` (the kit's core, all inline-safe)

- **Frame (@DecoratedContainer):** root `Group { Anchor: (Width: W, Height: H); }` only; title bar `Group { Anchor: (Height: 38, Top: 0); Padding: (Top: 7);
  Background: (TexturePath: "Common/ContainerHeader.png", HorizontalBorder: 50, VerticalBorder: 0); }` holding a 236 x 11 `ContainerDecorationTop.png` at Top -12 and the title
  label (`FontSize: 15, RenderBold, RenderUppercase, FontName: "Secondary", TextColor: #b4c8c9`, Padding Horizontal 19); body `Group { Anchor: (Top: 38); LayoutMode: Top;
  Padding: (Full: 17, Top: 8); Background: (TexturePath: "Common/ContainerPatch.png", Border: 23); }`; a 236 x 11 `ContainerDecorationBottom.png` at Bottom -6.
  The decorations stick out of the root by 12 px (top) and 6 px (bottom): budget for it. `@PageOverlay` (full-screen dim) and `@BackButton` are NOT copied (roots are
  Width/Height only; Esc + Close do the job).
- **Buttons** (all `TextButtonStyle(Default/Hovered/Pressed: (Background: (TexturePath: "Common/Buttons/<Kind>[_Hovered|_Pressed].png", Border: 12), LabelStyle: ...), Sounds: ...)`):
  Secondary (label 17 or Small 14, bold, uppercase, `#bdcbd3`), Primary (`VerticalBorder: 12, HorizontalBorder: 80`, label `#bfcdd5`, min width 172, the 80 px patch ends need it),
  Destructive (`#bfcdd5`, ButtonsCancel sounds), Tertiary (tabs, ON/OFF; `Tertiary_Active.png` = selected), Disabled (`Disabled.png`, Gear only).
  Sounds: `Sounds/ButtonsLightActivate.ogg` (MinPitch -0.4, MaxPitch 0.4, Volume 4) + `ButtonsLightHover.ogg` (Volume 6); cancel: `ButtonsCancelActivate.ogg` (Volume 6);
  Vault also `SaveActivate.ogg` for the main confirm button.
- **Inputs:** wrapper `Group` with `Background: (TexturePath: "Common/InputBox.png", Border: 16)`, inside `TextField { Anchor: (Full: 0); Padding: (Horizontal: 10); PlaceholderStyle: (TextColor: #6e7da1); }`.
- **Rows / lists:** `WorldEventListRow` = panel `#101925(0.55)`, 4 px status bar `#4274a5`, name `#d6e4ee` bold, caption `#7f93a6`, row actions 42 px high; section head =
  `WorldEventSectionLabel` (uppercase bold `#9aacbc`); separator `1 px #2b3542`; Gear rows use `ItemRepairElement` (`#000000(0.05/0.2/0.3/0.35)` over a row) and the vanilla scrollbar textures.
- **Text colours:** hint / label `#96a9be`, caption `#878e9c` / `#5a6a7a`, disabled `#797b7c`, gold highlight / cost `#E8A93B`, error `#ff6b6b` (PrefabSavePage), success `#39f493`
  (MemoriesCategory), warning title `#ffcc00` (PrefabEditorExitConfirm), title `#b4c8c9`.
- **Sizes:** vanilla is small (title 15, label 16, buttons 17/14, rows 14/12). Skyy's BIG-readable rule scaled row name 14 -> 18, caption 12 -> 15, section 13 -> 16 in Ranks; the kit needs ONE scale.

### 2.3 Vanilla documents in `Assets.zip` (folder `Common/UI/Custom/`, 161 `.ui` files) to mirror per page type

- `Common.ui` (960 lines, 142 definitions): colours (`@ColorDefault`, `@ColorGoldHighlight`, `@ColorGrayCaption`, `@ColorDisabled`, `@ColorPlaceholder`...), button styles (Default / Small / Big
  / Primary / Secondary / Tertiary / Cancel / Header / Close / Back), `@TextField`, `@NumberField`, `@MultilineTextField`, `@DropdownBox`, `@CheckBox`, `@Slider` / `@FloatSlider`,
  scrollbar styles (`@DefaultScrollbarStyle`, `@TranslucentScrollbarStyle`), tab styles (`@TopTabStyle`, `@TopTabsStyle`, `@HeaderTabStyle`, `@HeaderTabsStyle`), `@ContentSeparator`,
  `@PanelSeparatorFancy`, `@VerticalSeparator`, containers (`@Container`, `@DecoratedContainer`, `@SimpleContainer`, `@PageOverlay`), `@ProgressBar`, `@CircularProgressBar`,
  `@DefaultTextTooltipStyle`. `Sounds.ui`: `@ButtonsLight`, `@ButtonsCancel`, `@ButtonsMain`, `@SaveSettings`, `@Tick` / `@Untick`, `@TopBar`, `@Respawn`, ...
- `Pages/UIGallery/` (Categories: Buttons, Containers, Inputs, Navigation, Progress, Scrollbars, Selection, Sliders, Text, Tooltips): the game's own style catalogue, the first stop for every widget.
- Page-type equivalents: **BarterPage / BarterTradeRow / ShopPage / ShopElementButton** (Bazaar, Auctions, Trade), **ItemRepairPage / ItemRepairElement** (Gear, used),
  **WarpListPage / WarpEntryButton** (Warps), **PluginListPage / PluginListButton** and **CommandListPage / SubcommandCard** (Menu Mods list, Ranks lists, help),
  **InstanceListPage / Teleporter** (Islands, teleports), **RespawnPage**, **WorldEvent/*** (rows + section labels, used by Ranks), **Memories/*** (`MemoriesCategory` counter, category cards:
  Collections / Exploration cards), **Portals/*** (`Pill`, `BulletPoint`), **Fields/*** (`CheckboxRow`, `DropdownRow`, `IntRow`, `NumberRow`, `TextRow`: Server Setup rows),
  **PrefabEditorExitConfirm** (confirm dialogs, used by Vault / Ranks), **PrefabSavePage** (error label).
- HUD: only `Hud/TimeLeft.ui` (panel `Background: #000000(0.2)`, Padding Horizontal 20 / Vertical 10, 32 pt timer + a 40 px icon) and `Hud/ReturnToHubButton.ui` (Secondary button + 24 px icon)
  plus the builder tool legends (`Hud/ToolsLegends/*`). The in-game HUD proper (hotbar, bars) is client-native and has no `.ui` to copy: the HUD widgets' vanilla reference is the `#000000(0.2)`
  panel and the vanilla label colours.
- Rule reminder: values and texture PATHS may be referenced; never copy vanilla image / `.ui` files into the repo (the jar check refuses any `.ui`).

### 2.4 Not proven by any Skyy page yet (the kit has to prove or avoid)

- Inline `TexturePath: "Common/..."` frame / button / input textures on Skyy's client (used by Ranks, Gear, Sacks bag, Vault dialog, Skills Overall; none of them tested in game).
- `FontName: "Secondary"`, `Sounds:` blocks in inline styles, `ShrinkTextToFit` / `MinShrinkTextToFitFontSize` (Gear), `RenderUppercase` on long dynamic button text.
- `Common/Buttons/Disabled.png`, `Common/Scrollbar*.png`, `ContainerVerticalSeparator.png` (Gear only), `ContainerHeaderNoRunes.png` (Skills only).
- Progress bars in the vanilla style (`@ProgressBar` / `@CircularProgressBar`): every bar in the set today is two hand-sized coloured `Group`s (Party stat bars, Collections, Skills XP, Guild XP, Sacks
  bench 20 segments with `Visible:` toggles).
- Check boxes, sliders, dropdowns: none are used anywhere (ON/OFF pairs of buttons, "Less / More", "<" ">" pickers instead); vanilla `@CheckBox` / `@Slider` / `@DropdownBox` styles are unexplored inline.
- Tooltips for hover text on `Button` cards (only `ItemGridSlot.setDescription` markup is used today).

## 3. The old style: what has to be mapped to vanilla

**Button colour families** (all built as `TextButtonStyle(Default: (Background: #x, LabelStyle...), Hovered, Pressed)`; triple = default / hover / pressed background):

| Family | Triple | Where | Suggested vanilla kind (as Ranks / Vault / Gear use them) |
|---|---|---|---|
| brown | `#5a4420 / #8a6a30 / #3a2a10`, label `#ffe9c9` | Accessories, Classes, Profiles, Bazaar, Auctions `BS`, Menu `BS` + `SBS`, Settings | Secondary |
| blue | `#1d3a5f / #2f5a8f / #0f2038`, label `#e6f2ff` / `#dceeff` | Bank, Party, Guilds, Islands, Vault, Essentials, Hud pages, Sacks Craft, Auctions `BS_BLUE` | Secondary |
| green (positive) | `#1f5a34 / #2c7a48 / #133a22` (label `#e6ffe8`), `#2f6a3a / #3f8a4a / #1f4a2a` (Classes/Profiles "go"), `#2f5a34 / #3f7a46 / #1f3a22` (Bazaar buy, Auctions green) | confirm / create / deposit / accept buttons | Primary |
| green (skills family) | `#27463a / #3b6b54 / #172a22`, label `#dcffe8` | Skills, Trees `BSG`, Exploration `BSG`, Collections "Home/Refresh" | Secondary (nav) / Primary |
| red (destructive) | `#5a2424 / #7a3030 / #3a1414` (Guilds, Islands), `#6a2020 / #8f2f2f / #3a1010` (Essentials), `#6a2e2e / #8a4040 / #4a1e1e` (Bazaar sell, Auctions), `#5a2a2a / #7a3a3a` (Collections close) | leave / disband / kick / sell / cancel | Destructive |
| gold (selected / attention) | `#7a5a10 / #9a7418 / #4a3608` (Islands selected tab), `#6a4a12 / #8a641a / #3e2a08` (Vault, Essentials), `#e0b060 / #f0c878 / #b08040` label `#1a1000` (Bazaar/Auctions ON, Menu TAB_SEL), `#6b4a1c / #80592a` (Exploration BTON) | selected tab / armed action | Tertiary_Active (tabs), Primary (armed) |
| green / red ON-OFF | `#7fe07f / #a0f0a0 / #5fb05f` label `#062a06` (Hud, Menu ON_SEL), `#e07070 / #f09090 / #b05050` (Menu OFF_SEL), `#3f8a4c` / `#8a3f3f` (Islands YES/NO) | switches | Tertiary + Tertiary_Active |
| purple | `#3a2f5f / #54448a / #221a3a` label `#efe8ff` | Guilds log / limit buttons | Secondary |
| grey (disabled) | `#262f3d / #303b4c / #1a212c`, label `#7f8ea6` / `#9aa8bd`; `#262626 / #303030 / #1a1a1a` (Trees) | unavailable actions | Disabled.png |

Mapping used in Ranks / Vault / Gear: Secondary = neutral actions and navigation, Primary = the main positive action (Set rank, Buy, Reforge), Destructive = delete / remove / refuse and the Confirm of a risky question (Ranks), Tertiary = tabs and ON / OFF pairs (`Tertiary_Active` = selected), Disabled = unavailable.

**Per-mod accent stripes** (a 2-3 px `Group` under the root's top edge; vanilla has none, the frame title replaces it): Accessories `#8fd0ff`, Bank / Islands / Guilds `#ffd070`, Classes / Profiles `#d08a4a`, Party `#7fb0e0`, Collections `#b48fe0`, Bazaar / Menu / Settings / Server Setup `#e0b060`,
Skills / Stats `#9fe0a0`, Trees = the tree colour, Exploration `#e0a040`, Essentials Trade / Trade settings `#6fd3a0` and Warps `#7fb2ff`, Vault `#b48cff`, Sacks Craft `#7fb0e0`, Hud `#7fe07f`; Auctions has none.

**Data-driven colours that carry meaning** (keep as content colours, only the chrome goes vanilla): class colours (`ClassDefs.COLORS`: Archer `#8fd67a`, Warrior `#e0b060`, Mage `#7fb0e0`, ...; mirrored by
Profiles' roster), skill colours (`SkillDefs.COLORS`), tree colours (`TCOLOR`: `#8fc8ff #8fe08a #f0d060 #ffb070 #c8a0ff #e0a040`), collection accents (`ACCENT`: `#e0c060 #9fb8cc #7fcf7a #e07a6a #7fb8e0`),
bag rarity page colours (`SackDefs.RAR_PAGE`), gear rarity page colours (`GearDefs.R_PAGEHEX`), accessory quality colours (vanilla `Qualities/*.json` TextColor), Party stat bars (`#d04848 / #e0b040 / #4a8ae0` on `#3a1a1a / #3a3014 / #142440`), HUD palette (`PAL`, 14 colours).

## 4. Duplicated UI helper code -> one shared kit

### 4.1 What is copy-pasted today (live scripts only)

| Helper | Mods that carry their own copy | Note |
|---|---|---|
| `jsonStr(data, key)` (page event JSON reader) | Auctions, Bank, Bazaar, Essentials (TradePage), Exploration, Gear (`Gear.jsonStr`), Guilds, Islands, Party, Ranks, Sacks (CraftPage), Vault = **12** | byte-identical bodies (the SkyySacks 0.7.3 original) |
| `safe(String)` (replaces `: ; , { } " \`) | Accessories, Bazaar (`BzUtil.safe`), Classes, Collections (`CollUtil.safe`), Gear (`Gear.safe`), Guilds, Islands, Menu (`MenuUtil.safe` / `inl`), Profiles, Sacks, Skills, Trees, Vault = **13** | variants differ in which characters they map |
| `style(bg, hov, press, fg, fs)` -> `TextButtonStyle` | Bank, Essentials (`TradePage.style`, reused by TCfgPage + WarpPage), Guilds, Islands, Party, Vault = **6** | identical |
| Python-side button style builders | Trees `tbs`, Exploration `tbs`, Menu `_tbs` / `_tbsz`, Auctions `_bs` = **4**; inline `bs` / `BTN` strings in Accessories, Classes, Profiles, Bazaar (`BS_*`), Collections (`bs()`), Hud (x3 pages), Skills (x2 pages), Sacks Craft = **8** more | five colour families, section 3 |
| status-mark line: `colorOf` / `textOf` ("+" done, "-" refused, "=" info) | Bank, Essentials, Exploration (`ExAdminOps`), Guilds (`GuildStore`), Islands (`IslandStore`), Vault, Gear (`GearUi.infoColor/infoText`), Ranks = **8** | colours differ (`#7fe07f / #ff8080 / #8fc8ff` Bank, `#8fe39a / #ff9d6b` Vault / Essentials, vanilla `#39f493 / #ff6b6b / #E8A93B` Ranks / Gear) |
| Layout helpers `lbl / gap / sp / btn / row / cell / twoLine / dot` | Islands (`lbl` numbers ids `SkyyIsL<n>`), Auctions (`sp lab txt btn icon`), Collections (`bs btn lab sp bar icon bind`), Exploration (`gap vgap lab box btn row sep line card`), Skills (`line wrapLine gap sep`), Trees `line`, Essentials WarpPage (`btn gap lbl`), Menu AdminPage (`btn lab spc field evd bind bindEnter frame tail tabRow preview`), Ranks (`bind bindEnter rowStart texts button pre empty addRow field act tab buildTabs buildStatus buildFoot`), Gear `GearUi` | each mod re-invented them |
| TextField wrapper (`Group Background #16263a` + `TextField Anchor: (Full: 0) Padding: (Horizontal: 10)`, placeholder `#6e7da1`) | Bank, Party, Bazaar, Islands, Guilds, Essentials (Trade coins / TCfg / Warp), Sacks Craft search, Menu `AdminPage.field`, Auctions (search + price), Exploration `box`, Ranks (vanilla InputBox) | vanilla: InputBox.png, Ranks `FB0/FB1 + F0/F1` |
| Bars (two coloured `Group`s) | Party `statCol`, Collections `bar`, Skills (SkillsPage + StatsPage + OverallPage), Guilds XP bar, Sacks proc bar (20 `Visible:` segments) | vanilla `@ProgressBar` |
| Item icon box (`Group { ItemIcon { ItemId } }`) | Accessories, Classes, Profiles, Collections `icon()`, Skills, Exploration `card`, Bazaar, Auctions `icon()`, Sacks `iconBox`, Trees (Button + ItemIcon), Gear | ItemIcon is metadata-free (safe) |
| Pager (Prev / Page n of m / Next) | Menu, Vault (page numbers + Prev / Next), Guilds (members + log), Islands (trusted + bans lists), Collections, Auctions (browse + inventory picker), Essentials Warp, Sacks Craft, Ranks, Gear (flat mode) | Gear/Ranks use vanilla scrolling or a Tertiary pager |
| Confirm dialogs | Classes (inline row), Profiles (inline row), Guilds/Islands/Trees ("Sure?" / "Click again" second click), Essentials WarpPage + TCfgPage, Menu `drawConfirm`, Vault `VBuyDlg` (vanilla), Ranks `buildConfirm` (vanilla) | vanilla = PrefabEditorExitConfirm |

### 4.2 Proposed shape (for a main-session decision; nothing below was built)

- **`tools/skyyui.py`** next to `tools/skyycfg.py`: `emit(pool, PKG, ID_PREFIX, ...)` compiles ONE helper class `<PKG>.Ui` per mod (cross-mod class references are forbidden, only the
  `skyy.bridge`), plus Python constants for the style strings, a `KIT_VERSION`, and the Ranks-style build-time guards: `VANILLA_CHECK` (values and textures proven against `Assets.zip`),
  balanced-braces / no-underscore-ids / id-prefix asserts, the "inline Text only `[A-Za-z0-9 <>/-]`, everything else through `b.set`" rule (Menu and Ranks already assert it), a height budget helper
  (page must fit 1080 with the 12 + 6 px decoration overhang).
- Java surface (javassist-safe: static methods, no lambdas / generics / varargs): `frame(b, title, w, h)` (returns nothing, ids `<prefix>Root/Bar/Title/Body`), `tabs(...)`, `btn(kind, id, w, text)` with kinds
  {secondary, secondaryBig, primary, destructive, tertiary, tertiaryActive, disabled}, `field(id, w, value, placeholder)`, `row(...)` (WorldEventListRow), `section(text)`, `sep()`, `status(kind, text)`
  ("+", "-", "=" marks with the vanilla colours), `bar(id, w, h, filled)`, `icon(itemId, box, size)`, `confirm(...)`, `pager(...)`, plus the shared `jsonStr`, `safe`, `colorOf`, `textOf`.
- **One switch** like Gear's `ui.frames` (flat colours, no textures / sounds) until the texture paths are seen working on Skyy's client, then drop it.
- **Pin the kit revision** the way Menu pins `CFG_KIT` (git blob id printed in the ready line) so a mixed set of kit revisions is visible.
- Migrate Ranks / Gear / Vault dialog / Sacks bag / Skills Overall onto the kit LAST (batch B9): they work; only de-duplicate once the kit is proven.

## 5. Per-mod inventory (alphabetical)

Legend for every page block: **Opens** (command / item / link), **Shows**, **Root** (id, Anchor Width x Height), **Markup** (Java class.method, script line range), **Look today** (backgrounds, hex colours,
font sizes, buttons, textures), **Vanilla?**, **Dynamic** (rows built in loops, `b.set` text, event bindings, page state), **Risk** (restyle note). Hex lists are every colour that appears in that
page's markup lines (dynamic colour tables are named separately).

### 5.1 SkyyAccessories 0.4.4 - `SkyyAccessories/build_skyyaccessories_0.4.4.py` (1781 lines)

- **Build:** patch-based (`tools/acc_0_4_4_patch.py` derives it from 0.4.3; chain acc_0_2 .. acc_0_4_4). A restyle = a new `tools/acc_0_4_5_patch.py` reading the generated 0.4.4.
- **Menu coupling:** registers its admin rows through the kit (Server Setup -> Accessories: `slots`, `regenEverySeconds`, `bonus.<Family>`); no player switch. Menu tile "Accessory Bag" runs `/accessories`.
- **Page AccPage - "Accessory Bag"**
  - Opens: `/accessories` (aliases `/acc`, `/accbag`; `AccCmd` about 1394-1411), right-click of item `Skyy_Accessory_Bag` -> OpenCustomUI page id `SkyyAccBag` (`AccPageFactory` 1365-1370, registered 1546, item JSON 1585), Menu tile.
  - Shows: title, one hint line, a live "Bonuses" line (`AccDefs.bonusText`), one row per bag slot (up to `CAP` = 9; slots above the server's `slots` limit are hidden while empty): item icon, name in the quality colour, rarity word, Unequip button;
    then "Accessories and talismans in your inventory" (up to `INV_ROWS` = 6 rows) with Equip buttons; an info line (campfire line or the result of the last click).
  - Root: `Group #SkyyAcc { Anchor: (Width: 640, Height: 630); ... }` (line 1268; `PAGE_H` = 630, `INV_ROWS` = 6).
  - Markup: `AccPage.build` 1261-1302; helpers `safe` 1200-1203, `carried` / `takeOne` / `giveOne` 1205-1259, `giveBack` 1304-1310; `handleDataEvent` 1311-1363.
  - Look today: root `#0b1524(0.96)`, padding 16 / 10; stripe `#8fd0ff` 2 px; title `#e6f4ff` 16 bold; hint `#9fb8cc` 11; bonus `#9be89b` 11 bold; slot rows `#142030(0.9)` 34 px, inventory rows 30 px; empty slot text `#5f7a90`;
    list header `#c9dff0` 12 bold; info `#c9b89a` 12; ONE button style `bs` (brown `#5a4420 / #8a6a30 / #3a2a10`, label `#ffe9c9` 12 bold). Fonts 11, 12, 13, 16 (the smallest of the old pages). Rarity colours = vanilla quality `TextColor`s read from `Assets.zip` at build (281-290), retired `#8a97a3`, unrated `#ffffff`.
  - Vanilla?: no (colours of the item rarities are already vanilla).
  - Dynamic: loops for slots `SkyyAccSlot<i>` / `SkyyAccUn<i>` and inventory rows `SkyyAccInv<i>` / `SkyyAccEq<i>`, ids `SkyyAccBonus`, `SkyyAccInfo`; bindings `un:<i>` / `eq:<i>` (matched with `data.indexOf("un:" + i + "\"")`); state `info`, `invIds[]` (the ids drawn, so a click acts on what the player saw), `key` (profile storage key check: a profile switch since the draw refuses the click). Icons are `ItemIcon { ItemId }` only (metadata-safe).
  - Risk: MEDIUM. 15 rows in 630 px; at readable font sizes (17+) rows need about 44 px, so the root grows (about 860) or the inventory list is paged; all click logic keys on `un:<i>` / `eq:<i>` and `invIds`, keep them. The bag logic (equip / unequip, `acc:has` publishing) lives in `AccStore`, not in the markup.

### 5.2 SkyyAuctions 0.1.2 - `SkyyAuctions/build_skyyauctions_0.1.2.py` (4718 lines)

- **Build:** patch-based (`tools/auctions_0_1_2_patch.py` from 0.1.1). No config kit rows, no player switches (admin chat commands `/ahadmin list | info | remove | reload | pause | resume | regrant` only). Scheduled to merge into SkyyEconomy.
- **Page AhPage - "Auction House" (Buy It Now)**, one class, four views (`view`: browse, item, create, manage)
  - Opens: `/ah` (aliases `/auction`, `/auctionhouse`; opens Browse), `/ah manage` (opens Manage), `/ah search <words>` (opens Browse with the query), `/ah sell` and `/ah claim` (chat), right-click page id `SkyyAuctions` (`AhPageFactory`, registered 4681), Menu tile "Auction House"; all go through `AhCmds.open` (about 4195-4202, `openCustomPage` at 4200).
  - Shows: shared top (title, purse + profile name, nav Browse / Create BIN / Manage(n) / Close, orange banner for paused / no SkyyCoins / profile loading / denied / creative); **Browse** = 7 category buttons, search TextField + Search / Clear, Sort (4), Rarity filter, Refresh, column header,
    8 listing rows (icon, name, price, time left, "View"), pager; **Item** = large 1-slot `ItemGrid` (180 x 180, `InfoDisplay: None`, real restored stack built with `new ItemStack(id, qty)` - no metadata), stats, Buy / Confirm buy, Back; **Create** = 4 x 9 inventory picker (paged, 76 px `Button` cells with `ItemIcon`), selected line, price TextField + Preview,
    duration buttons (up to 8), Create BIN; **Manage** = own listings (Cancel) and claims (Claim / Claim all), paged.
  - Root: `Group #SkyyAh { Anchor: (Width: 1120, Height: 880); ... }` (line 3983).
  - Markup: consts / style fields 3395-3415 (`_bs`, `BS`, `BS_ON`, `BS_GREEN`, `BS_RED`, `BS_BLUE`); helpers `sp` 3451, `lab` / `txt` / `btn` / `icon` 3462-3495; `renderTop` 3497-3524; `results` + `renderBrowse` 3526-3625; `renderItem` 3628-3755 (ItemGrid at 3633, slot at 3660); `renderCreate` 3758-3878; `renderManage` 3881-3978; `render` / `build` 3981-3997; `evd` 3444-3449.
  - Look today: root `#0b1524(0.96)` padding 20 / 14, no stripe; title `#ffe9c9` 26; purse `#ffd766` 17 bold; banner `#ffb070` (orange); rows `#142030(0.9)`, detail panels `#10233a(0.9)`, tiles `#1d3a5f` (selected `#4f7fb0`, hover `#2f5a8f`, disabled `#1a2c3c`), search / price box `#16263a` with placeholder `#6e7da1`;
    buttons: brown `#5a4420 / #8a6a30 / #3a2a10`, ON `#e0b060 / #f0c878 / #b08040` label `#1a1000`, green `#2f5a34 / #3f7a46 / #1f3a22`, red `#6a2e2e / #8a4040 / #4a1e1e`, blue `#1d3a5f / #2f5a8f / #10243c`. Fonts 14-26. No textures.
  - Vanilla?: no. (Vanilla equivalents: `BarterPage` / `BarterTradeRow` / `ShopPage`, `@TextField`.)
  - Dynamic: 8 browse rows `SkyyAhRow<i>` / `SkyyAhRowView<i>`, 36 inventory cells `SkyyAhInv<i>` (state arrays `cellSec / cellSlot / cellSig` validate the click against the live inventory), `rowIds[8]`, `mIds[8]` / `mKinds[8]` for Manage; EVERY binding of Browse carries the search text and every binding of Create the price text (`@AhSearch` / `@AhPrice`); a two-step Confirm (`armAct / armId / armPrice / armUntil`, `AhCfg.CONFIRM_MS`) so a price change or another listing cancels the arm; status line with kinds.
  - Risk: HIGH. Money flow + four views + an `ItemGrid` (must stay `new ItemStack(id, qty)`) + two typed fields on separate views; do it together with Bazaar (same tile / tab conventions) and remember SkyyEconomy will absorb it.

### 5.3 SkyyBank 0.1.3 - `SkyyBank/build_skyybank_0.1.3.py` (1315 lines)

- **Build:** copy + edit (no patch script). No kit rows, no switches (chat `/bankconfig`). Scheduled to merge into SkyyEconomy.
- **Page BankPage - "Bank"**
  - Opens: `/bank` (no args; `BankCmd.openPage` 1123-1131), Menu tile "Bank". `/bank balance|status|deposit|withdraw` stay chat.
  - Shows: title + active profile ("Profile X (Class)"), two big number panels PURSE and BANK (40 pt, thousands separators), an interest panel (rate line, "Next interest: in N min S s (Refresh to update)", "Your next payout: +G coins"),
    Deposit all / amount box + Deposit / Withdraw / Withdraw all, captions, a result line (green / red / blue by mark), a chat hint line, Refresh + Close.
  - Root: `Group #SkyyBank { Anchor: (Width: 1100, Height: 680); ... }` (line 1013).
  - Markup: `BankPage.build` 995-1076; helpers `style` 870-875, `jsonStr` 876-897, `colorOf` 923-930, `textOf` 931-938, `subText` / `rateText` / `nextText` / `gainText` ~957-994; `typed` + `handleDataEvent` 1078-1121.
  - Look today: root `#0b1524(0.96)` padding 28 / 16; stripe `#ffd070` 3 px; title `#ffe08a` 34; sub `#cfe3ff` 17; purse box `#142236` (label `#9fb8d0` 21, number `#ffffff` 40), bank box `#2a2410` (label `#ffd070`, number `#ffe08a`), interest box `#101c2c` (`#e6f2ff` 21, gain `#7fe07f` 19); captions `#9fb8d0` / `#8fa4b8` 15;
    buttons: green `#1f5a34 / #2c7a48 / #133a22` label `#e6ffe8` 20 (Deposit), blue `#1d3a5f / #2f5a8f / #0f2038` label `#e6f2ff` 20 (Withdraw), grey `#2a3444 / #3a475c / #1a2230` 18 (Refresh / Close); amount TextField in a `#16263a` box (`FontSize: 22`, placeholder `#6e7da1`); result colours `#7fe07f / #ff8080 / #8fc8ff`. No textures.
  - Vanilla?: no.
  - Dynamic: numbers and interest lines by `b.set`; TextField `#SkyyBAmount` with `.Value` re-set from `keepAmount` and sent on every button (`@BAmount`); `info` result; the page never updates itself (Refresh only).
  - Risk: LOW. Small fixed layout; keep the amount payload and the "Enter alone never moves coins" rule.

### 5.4 SkyyBazaar 0.1.2 - `SkyyBazaar/build_skyybazaar_0.1.2.py` (1832 lines)

- **Build:** patch-based (`tools/bazaar_0_1_2_patch.py` from 0.1.1). No kit rows / switches. Scheduled to merge into SkyyEconomy.
- **Page BzPage - "Bazaar"**
  - Opens: `/bazaar` (`BazaarCmd` 1622-1640), OpenCustomUI id `SkyyBazaar` (`BzPageFactory` registered 1810, no item ships with it), Menu tile "Bazaar".
  - Shows: title + purse, up to 6 category tabs, a "Sell inventory" button (asks to confirm), sub line (or a warning when products / tabs do not fit: 6 tabs x 27 products), a grid of up to 27 product cells (9 per row, `Button` + `ItemIcon`), then a detail panel for the selected product (large icon, name, instant buy / sell quotes for 1 and 64, "You hold", demand line),
    Buy 1 / Buy 64 / Sell 1 / Sell 64 / Sell all, a custom amount row (TextField + Buy / Sell, "Enter shows the price"), limits line, result line, footnote.
  - Root: `Group #SkyyBz { Anchor: (Width: 1080, Height: 640 + (rows - 1) x 94); ... }` = 640 to 828 (line 1351; height depends on the product rows).
  - Markup: `BzUtil.safe` 405, `jsonStr` 437; style consts `BS_BROWN / BS_ON / BS_BUY / BS_SELL` 1246-1249; `buyWhy` / `sellWhy` / `limits` 1300-1331; `render` 1333-1469; `build` 1471-1475; `amountAction` 1478 on.
  - Look today: root `#0b1524(0.96)` padding 22 / 14; stripe `#e0b060`; title `#ffe9c9` 24; purse `#ffd766` (or `#e07070` when unavailable); tabs brown / ON gold `#e0b060` (label `#1a1000`); cells `#1d3a5f` (selected `#4f7fb0`, hover `#2f5a8f`, disabled `#1a2c3c`), empty `#142030(0.9)`; detail `#10233a(0.9)`; amount box `#16263a`;
    buy green `#2f5a34 / #3f7a46 / #1f3a22`, sell red `#6a2e2e / #8a4040 / #4a1e1e`; texts `#9fb8cc`, `#cfe3ff`, `#ffb070`, `#6f879c`, `#9fe8a2`. Fonts 14-24. No textures.
  - Vanilla?: no (vanilla model: `ShopPage` / `ShopElementButton`).
  - Dynamic: `cells[27]` (product ids), `tabs[]`; EVERY binding carries the amount text when a product is selected (`evd(action, amtOn)`); armed two-step trades (`confirmUntil`); price re-quoted on each rebuild; no ItemGrid (Buttons with ItemIcon).
  - Risk: MEDIUM. Fixed 9 x 3 grid math (`Padding` 99 + 9 x 93) and a height that depends on the row count; the trade rows are the money path.

### 5.5 SkyyClasses 0.1.7 - `SkyyClasses/build_skyyclasses_0.1.7.py` (3836 lines)

- **Build:** patch-based (`tools/classes_0_1_7_patch.py` from the EDITED 0.1.6; never re-run classes_0_1_6_patch.py).
- **Menu coupling:** kit rows (Server Setup -> Classes) and player switches (class reminder, kit messages). Popups by `NotificationUtil` (already vanilla).
- **Page ClassPage - "Classes"**
  - Opens: `/class` (`ClassCmd` 3637-3650), automatically at first join when SkyyProfiles is absent (`OpenTask` from 3445, gates: calm 2 polls, waits while on an island, never replaces an open page), Menu (`/class kit` text).
  - Shows: title, a sub line for the four states (no class / your class / locked to this profile / no profile yet), one card per class (Archer, Warrior, Mage, Berserker, Priest, + coming-soon Assassin, Shaman = 7): up to 4 weapon icons, name + role, combat skill + weapon text, description, action cell ("Choose" / "Switch" / "Selected" / "Locked" / "Coming soon"),
    an info line, an inline confirm row ("Switch to X for N coins?" Confirm / Cancel) and a footer (cost, cooldown, purse).
  - Root: `Group #SkyyCls { Anchor: (Width: 1000, Height: 900); ... }` (line 3321; `PAGE_W, PAGE_H` 3297; assert 3298 keeps it under 1080).
  - Markup: consts `BTN` / `BTN_GO` 3298-3308 (python strings); `ClassPage` fields / ctor 3296-3306, `safe` 3308, `build` 3312-3390, `handleDataEvent` 3391-3436.
  - Look today: root `#0b1524(0.96)` padding 16 / 14; stripe `#d08a4a`; title `#ffe9c9` 22; sub `#9fb8cc` 14; card backgrounds `#173524(0.95)` (yours), `#3a2f1a(0.95)` (pending), `#142030(0.9)` (open), `#0d1219(0.85)` (coming soon); name in the class colour (`ClassDefs.COLORS`: Archer `#8fd67a`, Warrior `#e0b060`, Mage `#7fb0e0`, ...), locked `#5f6b78`; skill line `#9fd8a2`, body `#c9d6e2` 13, footer `#8fa4b8` 13, info `#ffd27a`;
    buttons brown `#5a4420 / #8a6a30 / #3a2a10` (label `#ffe9c9` 15), green go `#2f6a3a / #3f8a4a / #1f4a2a` (label `#e9ffe9`). Fonts 13-22. No textures. Items via `ItemIcon` (48 px, up to 4 per card).
  - Vanilla?: no.
  - Dynamic: 7 cards in a loop (`SkyyClsCard<i>` ... `SkyyClsPick<i>`), `pending` (armed class) + `info` state, bindings `clspick<i>`, `clsyes`, `clsno`; profile-lock logic (`ClassStore.profileIndex`).
  - Risk: LOW. Same card shape as Profiles' Create page: restyle both with one card component.

### 5.6 SkyyCoins 0.1.5 - `SkyyCoins/build_skyycoins_0.1.5.py` (695 lines) - NO UI

- No page, no HUD widget, no `appendInline` / `CustomUIPage` / `UICommandBuilder` anywhere (grep confirmed). Commands are chat only (`/balance`, `/pay`, `/coinsgive`, `/deathpenalty`). It publishes `coins:<uuid>` and `coins:fn:get` on `skyy.bridge` for SkyyHud's Coins widget and for the pages of Bank, Bazaar, Auctions, Vault, Gear, Essentials, Classes, Collections.
- Build: no `tools/coins_0_1_5_patch.py` (only coins_0_1_4_patch.py and coins_bridge_patch.py exist). Nothing to restyle; merges into SkyyEconomy later.

### 5.7 SkyyCollections 0.2.3 - `SkyyCollections/build_skyycollections_0.2.3.py` (3795 lines)

- **Build:** patch-based (`tools/coll_0_2_3_patch.py` from 0.2.2).
- **Menu coupling:** kit rows (curves, rewards, Magic Bags, Coin unlocks, Rules, Registry) and player switches; Menu tile "Collections".
- **Page CollPage - "Collections"** (one class, `view` 0 home / 1 category / 2 collection / 3 unlocked recipes)
  - Opens: `/collections` (home), `/collections <name>` (`CollPage.openFor(pr, store, ref, coll)` 3215-3223 opens the detail), `/collections unlocks` chat; Menu tile.
  - Shows: **home** = title, summary (tiers / maxed / recipes unlocked / score), 2 x 2 category cards (Farming, Mining, Foraging, Combat: icon, "n of m found", tier bar, "Tiers a / b Maxed c", Open button), "Fishing - coming later", Unlocked recipes / Refresh / Close;
    **category** = Back + title + "Page n / m", 3 rows x 4 cards (12 per page: icon, name button, progress bar, tier + XP text, next reward; undiscovered = "???"), Prev / Next / Home / Close; **collection** = icon, name, tier line, totals, bar, tier table I..max (state chip, threshold, reward text), "From ..." line, Buy tier button (coins, `CollBypass`), Back / Home / Close;
    **recipes** = two columns of up to 20 recipe names + "and N more", Back / Close. Status line at the bottom.
  - Root: `Group #SkyyColl { Anchor: (Width: 1120, Height: 840); ... }` (line 3168).
  - Markup: helpers `bs` / `btn` / `lab` / `sp` / `bar` / `icon` / `bind` 2872-2916 (they RETURN markup strings); `catCard` 2918-2944; `buildHome` 2946-2971; `card` 2973-2999; `buildCat` 3001-3048; `buildDetail` 3050-3119; `buildRecipes` 3121-3162; `build` 3164-3181; `handleDataEvent` 3184-3213; `CollUtil.safe` 690.
  - Look today: root `#0b1524(0.96)` padding 20 / 14; stripe `#b48fe0`; titles `#f0e6ff` 28 / accent-coloured 24-30; cards `#142030(0.92)`; bars `#22324a` track with the category accent (`#e0c060 #9fb8cc #7fcf7a #e07a6a #7fb8e0`, maxed `#d9b038`); buttons `#2d3f66 / #41598c` (nav), `#27463a / #3b6b54` (Home / Refresh), `#5a2a2a / #7a3a3a` (Close), `#6a4a1a / #8a6424` (Buy tier); text `#dce8f4 #b8c8d8 #c0b3d6 #7f94a8 #8a9aaa #9fb0c0 #e6f0ff #ffe08a #c8b070`; tier-state chips `#8a3a36 #3aa655 #d98a2b ...`. Fonts 14-30. No textures. Items `ItemIcon` (`icon()` 2909).
  - Vanilla?: no. (Vanilla models: `Memories/MemoriesCategory` counter `#39f493`, category cards, `@ProgressBar`.)
  - Dynamic: `cards[12]` (collection index per drawn card, validates `ccard<n>`), `pageNo`, `coll`, `cat`, `status`; all four views share one root; bindings `ccat<n>`, `ccard<n>`, `crecipes`, `cbuy`, `cprev` / `cnext`, `chome`, `cback`, `crefresh`, `cclose`.
  - Risk: MEDIUM. Many cards (12 per page) and bars: card size and text length are tuned to fit; the tier table needs up to 9 rows (`max tier`); Buy uses the coin path (`CollBypass.click`).

### 5.8 SkyyCooking 0.1.2 - `SkyyCooking/build_skyycooking_0.1.2.py` (2305 lines) - NO UI

- No page or widget ("No pages (chat only), so no UI risk", header line 301; commands `/cooking`, `/cookadmin`). Chat text only (`.color("#ffb070")`).
- Feeds other UIs, needs no markup: kit rows -> Menu Server Setup -> Cooking (6 tabs), player switches -> Menu Settings (Cooking & Trees tab), `skill:stats:Cooking` (<= 5 text lines) -> Skills StatsPage, `cook:fn:grade` -> Menu / Hud, the Campfire cook of Sacks' `/craft` (K:camp tab).
- Build: patch-based (`tools/cooking_0_1_2_patch.py` from 0.1.1). Nothing to restyle.

### 5.9 SkyyEssentials 0.1.5 - `SkyyEssentials/build_skyyessentials_0.1.5.py` (5582 lines)

- **Build:** patch-based (`tools/essentials_0_1_5_patch.py` from 0.1.4). Has the kit rows (Parts, Teleports, Messages, Privacy, Warps, Trade tabs) and player switches; three pages of its own on top of that.
- **Page TradePage - "Trade with X"** (with `TWindow`, a `ContainerWindow` subclass = the offer window)
  - Opens: `/trade <player>` (request), the accept path, `/trade` alone reopens (`TradeCmd` 5439), and `TStore` opens it for both players when a request is accepted; mode 1 = `openCustomPageWithWindows(page, offer window)` (3749), mode 3 = plain `openCustomPage` (chest mode's control page / after the window closed; 3750). `tradeOpenMode` (page | chest) is a kit row.
  - Shows: title, status line (waiting / both ready countdown / ended), two 516 x 394 columns "Your offer" / "<name>'s offer" (READY / not ready, read-only `ItemGrid` snapshot, coin line), a coin row (TextField + Set coins, purse line, per-trade cap), Ready / Not ready, "Open as chest" (or "Edit my offer"), Cancel trade, Close, help lines;
    ended view = a small panel ("Anything still owed to you: /trade claim", Close).
  - Root: `Group #SkyyTrade { Anchor: (Width: 1100, Height: ph); ... }` with `ph` = 800 live / 280 ended (line 3067).
  - Markup: consts + `style` 2980-2985, `jsonStr` 2986-3007, `colorOf` 3008-3015, `textOf` 3016-3023, `column` 3028-3045 (the `ItemGrid` line uses `TStore.gridGeom(n)`, `AreItemsDraggable: false`), `build` 3047-3225; grid slots `TStore.gridSlots` 2789 (uses `new ItemStack(id, qty)`, the metadata rule); click handlers are compiled with the TStore bodies near the end (~4300-4850).
  - Look today: root `#0b1524(0.96)` padding 24 / 14; stripe `#6fd3a0`; title `#d8ffe8` 32; status `#cfe3ff` (`#ffd37a` countdown, `#9cff9c` you-ready, `#ff9d6b` ended); column heads `#ffffff` 23, READY `#8fe39a` / not ready `#9aa8bd`, coins `#ffd37a` 19; divider `#2a3f5a`; coin box `#16263a`;
    buttons green `#1f5a34 / #2c7a48 / #133a22`, gold `#6a4a12 / #8a641a / #3e2a08` (Set coins / Not ready), blue `#1d3a5f / #2f5a8f / #0f2038`, red `#6a2020 / #8f2f2f / #3a1010`, grey (locked) `#262f3d / #303b4c / #1a212c` label `#7f8ea6`, all 20 pt. No textures.
  - Vanilla?: no. (Vanilla model: `BarterPage` two-column trade rows.)
  - Dynamic: rebuilt only after a click or a real change (never on a timer; `lastBuilt` guards), `keepCoin` re-set into `#SkyyTrCoin.Value`, `dismissed` / `replacing` flags (a replaced page must not close the window), session `TSession` state, `TWindow` slots in the player's own container view.
  - Risk: HIGH. Page + window pair (window stays vanilla), `ItemGrid` geometry from `gridGeom`, replace-not-close rules, trade-safety timing. Restyle the frame, buttons and text only; leave the grid / window wiring alone.
- **Page TCfgPage - "Trade settings" / "Teleport and message settings"**
  - Opens: `/tradeadmin config` (`which` = 0), the Warps page footer button "Teleport and message settings" (`which` = 1; direct `openCustomPage` at 5232); needs `skyyessentials.tradeadmin` / `skyyessentials.admin` (`guard()`); the same rows are also in Menu -> Server Setup.
  - Shows: title, "SkyyEssentials 0.1.5 - every change is saved to config.properties at once", optional red "unreadable / unsaved" line, a table Setting / Now / Change / Key in the file, one row per kit row of that group (bool = ON / OFF buttons, choice = up to 2 buttons, number / text = TextField + Set), Confirm / Cancel for a pending question, Reload file, Back to warps, Close, two help lines, result line.
  - Root: `Group #SkyyTcfg { Anchor: (Width: 1060, Height: ph); ... }`, `ph` = 28 + 3 + 46 + 28 + 30 + n x 42 + 8 + 52 + 24 + 24 + 32 (+ 28 when broken) + 6 (line 3241; `n` = the group's row count).
  - Markup: `TCfgPage` ctor 3189, `build` 3226-3331 (rows loop inside `build`); handler + reload compiled near the end (~4350).
  - Look today: root `#0b1524(0.97)`; stripe `#6fd3a0`; title `#d8ffe8` 30; column heads `#8fa4b8` 15; labels `#e6f2ff` 18; values `#ffd37a` 18; key column `#7f8ea6` 13; buttons as TradePage (`TradePage.style`, 17 pt); help `#b8c8d8` 15; info via `TradePage.colorOf`. No textures.
  - Vanilla?: no. Duplicates Menu's Server Setup row types (bool / choice / number) - the reason it can be replaced by the kit's row widgets (or dropped once Server Setup is vanilla).
  - Dynamic: `keys[]` (row keys), `keep[]` drafts, `pendQ` (confirm question), bindings `b1:<r>` / `b0:<r>` / `c<k>:<r>` / `set:<r>` (+ Enter `Validating`), values from `CfgFn.cmdGet`.
  - Risk: MEDIUM. Row count varies (up to about 13); height is computed from it.
- **Page WarpPage - "Warps" (editor)**
  - Opens: `/warpadmin` (admin, `WarpAdminCmd` 5461; `openCustomPage` at 5285 / 5305); players see warps in Menu -> Teleport (Menu's own grid), not here.
  - Shows: title, count + current world + "page n of m", column heads (Warp / World / Position / Made by), rows of Go / Move here / Rename / Remove per warp (paged), Prev / Next, Warp name TextField + "Add warp here", two help lines, result line, footer (Teleport and message settings, Refresh, Close);
    confirm view ("Remove the warp X?", Confirm / Cancel); no-permission view.
  - Roots: `Group #SkyyWp` 1120 x 880 (list, line 5122), 1000 x 330 (confirm, 5100), 900 x 250 (no permission, 5090).
  - Markup: helpers `btn` / `gap` / `lbl` ~5070-5082, `question` 5082, `build` 5085-5195; go / add / move / rename handlers after it.
  - Look today: root `#0b1524(0.97)` padding 24 / 14; stripe `#7fb2ff` (confirm `#ff9d6b`); title `#dbe9ff` 30; text `#ffffff`, `#cfe3ff`, `#ffd37a`, `#9aa8bd`, heads `#8fa4b8`; name box `#16263a`; buttons via `TradePage.style` (blue / green / red / grey, 17 pt). No textures.
  - Vanilla?: no. (Vanilla model: `WarpListPage` / `WarpEntryButton`.)
  - Dynamic: `ids[per]` (warp ids per row), `pg`, `keepName` (`@WpName`), `cKind` / `cId` (pending confirm), rows built in a loop with ids `SkyyWpRow<r>`, `SkyyWpGo<r>`, `SkyyWpMv<r>`, `SkyyWpRn<r>`, `SkyyWpRm<r>`; closing before a cross-world teleport (the page is closed BEFORE the `Teleport`; the ref dies after a cross-world add).
  - Risk: MEDIUM. Depends on the vanilla `TeleportPlugin` warp calls; markup is separate from that.

### 5.10 SkyyExploration 0.2.1 - `SkyyExploration/build_skyyexploration_0.2.1.py` (6664 lines)

- **Build:** copy + edit of 0.2 (no patch script). Kit rows (Spots, Checklist, Titles, Other) + player switches. Engine banners `EventTitleUtil` + discovery sounds (already vanilla).
- **Page ExplorePage - "Exploration"** (`tab` 0-3)
  - Opens: `/explore` (`ExploreCmd` 6320; `openCustomPage` at 6289), `/title` (opens the Titles tab), `/explore quiet` (chat).
  - Shows: tab row (Overview, Zones, Titles, Checklist) + "Exploration level ..." (right, `#e0a040`), a one-line note, then per tab: **Overview** = 8 cards 258 x 150 (icon, head, value, sub: Exploration level, Zones, Loot chests, Map, Chest luck, Title, Discoveries, Island checklist); **Zones** = two columns of zone names grouped by region (found `#9adf86`, missing `#7f94a8`); **Titles** = your title + "No title" and the title list with Use buttons (level-gated); **Checklist** = world selector (< world >), per-world checklist rows with Prev / Next paging. Footer: "< Skills" (runs `/skills`), "Exploration tree" (runs `/tree exploration`), message line.
  - Root: `Group #SkyyExRoot { Anchor: (Width: 1120, Height: 800); ... }` (line 4863; budgets `EX_W/EX_H/EX_HEAD/EX_NOTE/EX_BODY = 640/EX_FOOT` at 4543+ with asserts 4560-4570).
  - Markup: consts `tbs` + `BSG / BSOFF / BTON / BTOFF` 4527-4541; `card` 4594-4605, `line` 4606-4610, `overview` 4611-4674, `zonesTab` 4676-4700, `titlesTab` 4702-4754, `checklistTab` 4756-4849, `build` 4851-4890, `handleDataEvent` 4893-4925.
  - Look today: root `#0b1524(0.96)` padding 20 / 12; NO stripe on top but a 2 px `#e0a040` rule under the note; tabs `BTON` (`#6b4a1c / #80592a / #3a2810`) / `BTOFF` (`#1d2c3c / #2c4258 / #142030`, label `#b8c8d8`), footer `BSG` green (`#27463a / #3b6b54 / #172a22`, label `#dcffe8`), 14 pt; cards `#142030(0.9)` with head `#9fb8cc` 13, value 20 in `CARD_COLOR`, sub `#c8d6e4` 13; message `#ffe08a` 15. Fonts 13-20. No textures. Icons `ItemIcon`.
  - Vanilla?: no.
  - Dynamic: `handleDataEvent` IGNORES clicks within 1 s of `build` (`lastBuild`, 4894) - keep; `ckWorld` / `ckList[]` / `ckIdx` / `ckPage`, `msg`; navigation to other pages by `CommandManager.handleCommand(playerRef, "skills")` (no close first).
  - Risk: MEDIUM. Same nav as Skills / Trees: restyle these three together.
- **Page AdminPage - "Exploration admin - <world>"** (`tab` 0-2: Spots, Checklist, Island)
  - Opens: `/exploreadmin` (`ExploreAdminCmd` 6536; `openCustomPage(new AdminPage(pr, 0))` 6555); needs `skyyexploration.admin`.
  - Shows: world-scoped editor: title + tabs, sub line (spot / checklist counts, your position, red file-state warnings), a 690 px body with the list on the left and the editor on the right (add / move / rename / remove spots with typed x y z, secrecy, XP; checklist entries; island switches), result line, footer Refresh + hint. Worlds that never pay exploration show an explanation instead.
  - Root: `Group #SkyyXaRoot { Anchor: (Width: 1120, Height: 900); ... }` (line 6117); asserts 4560-4570 (`row` widths <= 460, detail heights <= 690).
  - Markup: helpers `gap vgap lab ph box btn row sep ev3` 5762-5817, `pager` 5819, `lists` 5831, `spotsTab` 5837-5935, `checkTab` 5937-6041, `switches` 6043, `islandTab` 6053-6104, `build` 6106-6144; ops in `ExAdminOps` 4930-5760 (logic, not markup).
  - Look today: root `#0b1524(0.97)`; stripe `#e0a040` 3 px; title `#ffe08a` 24; sub `#9fb8cc` 15 (`#ff9a70` on a file warning); `XG / XOFF / XON / XRED / XBLU` buttons (16 pt: green `#27463a`, off `#1d2c3c`, on `#6b4a1c`, red `#6a2626 / #8a3434 / #401616`, blue `#1d3a5f`); TextField box `#16263a` 44 px; separators `#2c4258` (2 px); list rows `#142030`, `#24405c`; text `#e6eef6 #c8d6e4 #9adf86 #9fd0ff #d890ff #ffb070`. No textures.
  - Vanilla?: no.
  - Dynamic: typed values are bundled with every button (`ev3` / `EventData.append` up to three boxes), `lastBuild` debounce, `msg` with the `+ / - / =` marks (`ExAdminOps.colorOf` / `textOf`).
  - Risk: MEDIUM. Admin-only, fixed 460 / 690 px budgets asserted at build.

### 5.11 SkyyGear 0.1 - `SkyyGear/build_skyygear_0.1.py` (6784 lines) - ALREADY VANILLA

- **Build:** a new script (no patch script, no earlier version). Kit rows (incl. `ui.frames`, `identify.command`, costs) + player switches. The build script itself asserts there is no `new ItemGridSlot` in the source (line 6774); item icons are `ItemIcon { ItemId }` only.
- **Page ReforgePage - "Reforge"**
  - Opens: `/reforge` (`ReforgeCmd` 5814-5830; preselects the held item), Menu tile "Reforge"; back goes to `/skymenu` when Menu exists (`handleCommand`, 5790).
  - Shows: sub line, LEFT list "Your gear (n)" (470 px; rows = 44 px `Button` with a 32 px `ItemIcon`, name, "Rarity - Lv n"; `TopScrolling` with vanilla scrollbar textures, 200 rows per page; flat mode 12 per page with Prev / Next), a vertical separator, RIGHT anvil (562 px): empty view (reforge cost by rarity) or selected view (72 px icon box, rarity-coloured name + slot / gate line, "In your ... slot" line, Before / After columns 275 px each or Current modifiers, cost line `#E8A93B`, purse, big Reforge button - Primary or Disabled: "Cannot reforge" / "Not enough coins" / "Identify it first"), bottom bar (info line, Refresh, Back / Close in Destructive).
  - Root: `GearUi.frame(b, "Reforge", 1100, 880)` (5732) -> `Group #SkyyGRoot { Anchor: (Width: 1100, Height: 880); }`.
  - Markup: `GearUi` 5450-5560 (`frame` 5511, `btn` 5463, `rowStyle` / `scroll` / `vsep` 5523-5540, `infoColor` / `infoText`); `ReforgePage` fields / ctor 5563-5580, `column` 5582-5596, `anvil` 5598-5665, `list` 5667-5715, `build` 5717-5750, `forge` and `handleDataEvent` about 5752-5811.
  - Look today: frame textures `Common/ContainerHeader.png`, `ContainerPatch.png`, `ContainerDecorationTop / Bottom.png`, `Common/Buttons/Primary|Secondary|Destructive(_Hovered|_Pressed).png`, `Disabled.png`, `Common/Scrollbar.png`, `ScrollbarHandle*.png`, `ContainerVerticalSeparator.png`; sounds `ButtonsLight*` / `ButtonsCancelActivate`; colours `#ffffff`, `#96a9be` (label), `#878e9c` (caption), `#b4c8c9` (title), `#afc2c3` (section head), `#2b3542` (separator), `#393426(0.5)`, `#E8A93B` (cost), `#000000(0.05 / 0.2 / 0.25 / 0.3 / 0.35 / 0.4)` (row hovers), `#ffffff(0.6)`; flat fallback `#1b2533(0.98)`, `#0e1620(0.97)`, `#2c4a66`, `#5a2a26`, `#2b3542`, `#2a2f36`; rarity names in `GearDefs.R_PAGEHEX` (Wynn rarities, Skyy hex). Fonts 12-20 (`ShrinkTextToFit` on button labels, min 12).
  - Vanilla?: YES (hand-checked against Common.ui / Sounds.ui / ItemRepairPage, NOT build-proven; `ui.frames` OFF = flat colours).
  - Dynamic: `rows` (the player's gear as `int[]{section, slot}`), `selSec / selSlot / selId / selFp` (fingerprint re-check: "The item on the anvil moved or changed"), `epoch` (profile switch clears), `before / after` `BD` documents, `fresh`, 400 ms click guard; rebuild on every click.
  - Risk: LOW to keep; MEDIUM to migrate onto a kit (colour constants live in `GearDefs.C_*`; `ui.frames` switch and the flat variant must survive).
- **Page IdentifyPage - "Identify"**
  - Opens: `/identify` (`IdentifyCmd` 6303), Menu tile "Identify"; same back rule (the kit row `identify.command` decides whether the pages mention the command; not checked whether it also unregisters it).
  - Shows: as Reforge but the list is "Unidentified gear", the detail shows the selected item, an "Unidentified" column ("Its modifiers appear when you identify it", "Cannot be used until identified" in `C_BAD`), cost by rarity, cost / purse and an Identify button; after a click a "Revealed" list of the last reveals (`recent`).
  - Root: `GearUi.frame(b, "Identify", 1100, 880)` (6182). Markup: `ipg` fields / ctor 5975-6000, `detail` 6031-6114, `list` 6116-6163, `build` 6165-6209.
  - Look / vanilla / dynamic / risk: as ReforgePage (same helpers, `#000000(0.25)` icon box, `recent` list).

### 5.12 SkyyGuilds 0.1.3 - `SkyyGuilds/build_skyyguilds_0.1.3.py` (3652 lines)

- **Build:** patch-based (`tools/guilds_0_1_3_patch.py` from 0.1.2). Kit rows + player switches; Menu tile "Guild"; chat `/gc`.
- **Page GuildPage - "Guilds"** (three roots: no guild, guild, bank log)
  - Opens: `/guild` (root `GuildCmd` 3581-3585, `openCustomPage(new GuildPage(pr))` 3584), Menu tile; `/guild help` is chat.
  - Shows: **none view** = title, explanation, pending invite row (Accept / Decline + countdown), "Create a guild" (name TextField + button, rule line), a Commands list (`helpLines`), info line, Refresh; **guild view** = name [tag], level / season / role line, full-width guild XP bar (`#58c070` on `#22324a`, text on it), XP line, bank + online line, member table (34 + Member / Rank / Guild XP added / Taken today / Status / actions; 7 rows per page: Promote / Demote / Kick "Sure?" / Make leader "Confirm?"), Prev / Next, action row (invite TextField + Invite; amount TextField + Deposit / Withdraw), hint, limits line + (leader) limit TextField + "Set Admin limit" / "Set Member limit", a 3-line log preview + "Expand log", Refresh, Leave guild (click again), Disband guild (click again); **log view** = title, sub, limits, column heads, 15 rows per page (alternating `#142030(0.9)` / `#101a28(0.9)`), "< Newer" / "Older >", "< Back to guild", Refresh.
  - Roots: `Group #SkyyGuild { Anchor: (Width: 1120, Height: 660) }` (none, line 2954), `1120 x 900` (guild, 3029) and `1120 x 900` (log, 3217).
  - Markup: `safe` 2897, `style` 2902, `jsonStr` 2908; `infoLabel` 2944; `buildNone` 2950-3003; `buildGuild` 3005-3204; `buildLog` 3206-3287; `build` 3289-3300; `colorOf` / `textOf` in `GuildStore` 1051-1064.
  - Look today: root `#0b1524(0.96)` padding 24 / 14; stripe `#ffd070` 3 px; title `#ffe08a` 28-30 bold; sub `#cfe3ff` 17; captions `#9fb8d0` 14-15 / `#8fa4b8` 13; stats `#ffd070` 20; rows `#142030(0.9)` (you `#1c2c44(0.95)`), invite row `#1d3320(0.95)`; TextField boxes `#16263a` (placeholder `#6e7da1`); buttons blue `#1d3a5f / #2f5a8f / #0f2038`, green `#1f5a34 / #2c7a48 / #133a22`, red `#5a2424 / #7a3030 / #3a1414`, orange `#7a3a10 / #9a4c18 / #4a2208` (Make leader), purple `#3a2f5f / #54448a / #221a3a`; log text `#c8d4e0`. Fonts 13-30. No textures.
  - Vanilla?: no.
  - Dynamic: member rows `SkyyGRow<idx>` (per page 7) with per-row buttons `SkyyGPro/Dem/Kick/Lead<idx>`, `pageNo`, `keepName`, `cLeave / cDis / cKick / cLead` (armed second clicks), `expanded` log, TextFields `#SkyyGName`, `#SkyyGInvite`, `#SkyyGAmount`, `#SkyyGLimit` with `@GName` etc. payloads and Enter (`Validating`); data comes as an `Object[] s` snapshot from `GuildStore` under one lock.
  - Risk: MEDIUM-HIGH. The largest single-page mod after Menu (256-line `buildGuild`), four TextFields, money and rank actions; heights were budgeted to 867 of 872 px for the tallest leader case (comment at 3003) - a vanilla frame costs 55+ px, so the leader case needs a scrolling list (Gear's `TopScrolling`) or fewer rows.

### 5.13 SkyyHud 0.3.10 - `SkyyHud/build_skyyhud_0.3.10.py` (2603 lines)

- **Build:** patch-based (`tools/hud_0_3_10_patch.py` from 0.3.9; chain hud_0_3 .. hud_0_3_10). Kit row set (default layout, "Use my layout", editor link). No player switch.
- **HUD - `HudMain` (a `CustomUIHud`)**: 10 widgets, attach on `PlayerReadyEvent` (`AttachTask`, `HudMain.show()`), refreshed by a 1 s `TickTask` (`HudMain.tick()` -> `fill()` sends only changed texts via `update(false, b)`; a changed shape or a layout edit re-`show()`s the whole HUD).
  - Widgets (`Widgets.IDS` 307): Coords, Zone, Gclock (game clock), Rclock (real clock), Day (day counter), Session (session time), Online (players online), Coins (purse, bridge `coins:<uuid>`) - all one line, base box 180 x 26 at 100 % - plus **Party** (340 x 116: title + up to 5 member rows with status, grey when offline, optional stamina / mana) and **Guild** (260 x 94: title, level, online line, up to 2 online names) which are multi-line (`Widgets.multi`).
  - Root: `Group #SkyyHudRoot { Anchor: (Full: 0); }` (the only full-screen root in the set); each widget = `Group #SkyyW<id>` positioned by `anchorSrc` from the player's layout (anchor tl / t / tr / l / c / r / bl / b / br + dx / dy, scale 50-200 %).
  - Markup: `Widgets` 415-1110 (`def` 430, `label` 436, `textSrc` 964, `styleA` 1000, `lineSrc` 1003, `partyBody` 1033, `guildBody`, `multiWidgetSrc` 1052-1058, `widgetSrc` 1060-1066, `setText` 948, `setLines` 1056), `HudMain.fill` 1564-1603, `HudMain.build` 1605-1633.
  - Look today: optional background `#0b1524(0.72)` (5 places: 1053, 1063, 1860, 1866, 2186 = HUD + editor preview + settings preview), text `#eaf6ff` default from a 14-colour palette `PAL` (default `#eaf6ff`, white, gold `#ffaa00`, yellow `#ffff55`, green `#3fbf3f`, lime `#7cff4f`, aqua `#55ffff`, blue `#4f8cff`, purple `#b066ff`, pink `#ff77d0`, red `#ff4f4f`, orange `#ff8c1a`, gray `#a8b0b8`, black), 12 pt x scale, bold / italic switches, optional "glow" = 8 offset copies of the label at 45 % opacity in the glow colour; Party / Guild use sizes 12 / 11 / 10 x scale, grey rows `GREY`.
  - Vanilla?: no. Vanilla reference is only `Hud/TimeLeft.ui` (`#000000(0.2)` panel, padding 20 / 10, 32 pt text + icon).
  - Risk: HIGH. The layout file / export code / profile formats are shipped state (`WLayout.parse`, "unchanged: every widget"); text is player-tunable (colour, glow, scale), so only the DEFAULTS (background colour, default text colour, padding) can go vanilla; widgets must stay small (`clampToScreen`, 1920 x 1080 maths in `screenPosH`).
- **Page EditorPage - "SkyyHud Editor"** (`/skyyhud`)
  - Opens: `/skyyhud` (`HudCmd` 2465; sub-commands export / import / reset / profile / default), Menu tile "HUD Editor", Server Setup -> HUD "editor" link row; the footer "< Server Setup" (runs `/modconfig hud`) shows only for players with `skyymenu.modconfig`.
  - Shows: title + hint, a 1280 x 720 drag canvas (screen x 2/3), the selected-widget bar (arrows, Step, Size-, Size+, Hide, Settings), a Select row and a Hidden row of small buttons, an info line, footer (help text, Server Setup, Widgets / Settings).
  - Root: `Group #SkyyEditor { Anchor: (Width: 1330, Height: 930); ... }` (line 1891+). Markup: `appendPreviews` 1821-1889, `build` 1891-1981 (canvas `ItemGrid #SkyyECanvas` SlotsPerRow 32, `AreItemsDraggable: true`, `SlotSize: 40`, `SlotIconSize: 1`, 576 slots; previews at true positions drawn BEFORE the grid; handles = `ItemGridSlot` chips of `Ingredient_Crystal_White` via `chipItem` (`new ItemStack(id, 1)`); bindings `Dropped`, `SlotClicking`, `DragCancelled`).
  - Look today: root `#0b1524(0.96)` padding 20 / 10; stripe `#7fe07f` 2 px; title `#eaffea` 15; hints `#9fb8d0` 10-11 / `#6f8498`; selection outline `#ffd24a`, moved-marker `#ffd24a(0.2)` / `#7fb8ff(0.25)`; canvas border `#7fe07f` 3 px; buttons blue `#1d3a5f / #2f5a8f / #0f2038` label `#dceeff` 10, ON green `#7fe07f / #a0f0a0 / #5fb05f` label `#062a06`. Fonts 8-15.
  - Vanilla?: no. Risk: VERY HIGH (see key finding 7): only the frame, the button styles and the footer may change; keep 1280 x 720 + 40 px cells and the draw order.
- **Page WidgetsPage - "Widgets"** (900 x (150 + 62 x 10 = 770), `#SkyyWidgets`, `build` 2254-2278): one row per widget (name, ON / OFF, Settings), Back. Look: `#0b1524(0.96)`, stripe `#7fe07f`, title `#eaffea` 26, buttons 17 pt blue / green-on, name `#ffffff` 20. Ids `SkyyWRow<id>`, `SkyyWOn/Off/Cog<id>`. Risk LOW.
- **Page SettingsPage - "<Widget> settings"** (root `#SkyySet` 1500 x 790, `build` 2110-2197): rows Visible / Background (/ "Stamina and mana" or "Online names" for Party / Guild), Size (50 / 75 / 100 / 125 / 150 / 200 %), Snap to (9 anchors), Color (13 swatches), Bold, Italic, Glow, Glow color (14 swatches), Preview on dark `#141a22` and bright `#8fb3cf` backgrounds, Back / Reset style. Look: root `#0b1524(0.96)`; `onOff` helper 2100-2108 (20 pt label, ON / OFF 104 x 44); swatch buttons coloured by the palette (`swatch()`); section head `#9fe0ff` 18. Risk MEDIUM (swatches are colour data, the preview must still show the real widget markup).

### 5.14 SkyyIslands 0.5.3 - `SkyyIslands/build_skyyislands_0.5.3.py` (5054 lines)

- **Build:** patch-based (`tools/islands_0_5_3_patch.py` from 0.5.2, chain islands_0_2 .. 0_5_3; the 0.5.1 security hotfix is a hard floor). Kit rows (island defaults, co-op, visits, resets ...) + player switches; Menu tile "Island Menu" runs `/island menu`.
- **Page IslandMenuPage - "<owner>'s Island"** (`tab` 0-4)
  - Opens: `/island menu` (sub-command `IslandMenuCmd` 4402, aliases `settings`, `options`), Menu tile, `/island` itself teleports (no page).
  - Shows: title + role line (role, co-op count, visit mode), tab row (Overview, Members, Permissions, Visitors, Island), a 640 px body, result line, Refresh + Close;
    **Overview** = owner box (owner, co-op count, trusted, visit mode + limit, visitors now, PvP, world state), Go to island, pending co-op invite row (Accept / Decline + countdown), owner actions (Disband co-op, Reset island with a 3-click arm), Leave island, a Commands list, or "Create my island" when none;
    **Members** = player-name TextField + "Invite to co-op" / "Trust (build only)", co-op member rows (Promote / Demote / Kick "Sure?"), trusted list 5 rows x 2 columns (Untrust) with Prev / Next;
    **Permissions** = "Reset to defaults" + a grid of every permission flag (`IslandPerms.LABELS` + hints) x roles Visitor / Trusted / Member / Admin (YES / NO cells, click toggles with the "right side follows" rule) + Owner "always";
    **Visitors** = visit mode (3 big buttons), limit - / +, notify On / Off, visitor rows (Expel / Trust / Ban "Sure?"), banned list (Unban), Refresh list + pagers;
    **Island** = PvP on / off, mob spawning on / off, "coming in a later version" notes.
  - Root: `Group #SkyyIsRoot { Anchor: (Width: 1240, Height: 900); ... }` (line 4196).
  - Markup: class + fields 3680-3710, helpers `safe` 3711, `style` 3716, `jsonStr` 3722, `two` / `date` / `idx`, `lbl` 3766-3772, `gap` 3774, `btn` 3779, `row` 3784, `twoLine` 3789, `cell` 3799, `dot` 3806; `buildTabs` 3817-3827, `buildOverview` 3829-3909, `buildMembers` 3911-4011, `buildPerms` 4013-4050, `buildVisitors` 4052-4155, `buildIsland` 4157-4184, `build` 4186-4223, `handleDataEvent` 4225 on (per-tab payloads `tabov ... tabisl`, `pcNNv|t|m|a`, `vm<i>`, `pr<i> dm<i> kk<i>`, ...).
  - Look today: root `#0b1524(0.96)` padding 20 / 12; stripe `#ffd070` 3 px; title `#ffe08a` 26; role line in `IslandPerms.roleColor`; tabs blue `#1d3a5f / #2f5a8f / #0f2038` label `#e6f2ff` 18, selected gold `#7a5a10 / #9a7418 / #4a3608` label `#fff0c8`; panels `#132236(0.9 / 0.95)` and row shading `#142030(0.9)` / `#1c2c44(0.95)`; invite row `#1d3320(0.95)`; buttons green `#1f5a34 / #2c7a48 / #133a22`, red `#5a2424 / #7a3030 / #3a1414` (17-18 pt), grey `#2a3340 / #3a4556 / #1a2230`, YES `#2f6a3a` (hover `#3f8a4c`) / NO `#6a2f2f` (hover `#8a3f3f`) at 16; TextField box `#16263a` placeholder `#6e7da1`; status dot `#50d060` / `#55606e`; text `#e6f2ff #cfe3ff #9fb8d0 #b8c8d8 #ff9d6b #ffb070 #c8d4e0`. Fonts 13-26. No textures.
  - Vanilla?: no. (Vanilla models: `InstanceListPage`, `Teleporter`, the `Fields/CheckboxRow` for the flags.)
  - Dynamic: element ids `SkyyIsL<n>` come from a per-build counter (`nid`, reset at the top of `build`); `rowKeys`, `trustKeys`, `visUuids`, `banKeys` (what each drawn row acts on), `trustPage` / `banPage`, `keepName` (TextField value survives a rebuild), `confirm` / `confirmUntil` (armed second click: disband, reset x2, leave, kick, ban, "pdef"), `info` with marks (`IslandStore.colorOf` 639 / `textOf` 647); one tab drawn per rebuild inside `try` with a red "could not be drawn" fallback.
  - Risk: MEDIUM-HIGH. 460 lines of markup, the permission matrix (5 x N cells) and long lists tuned to 640 px of body; the vanilla frame + tab row cost about 100 px, so the body has to shrink or scroll.

### 5.15 SkyyMenu 0.3.3 - `SkyyMenu/build_skyymenu_0.3.3.py` (6378 lines)

- **Build:** patch-based (`tools/menu_0_3_3_patch.py` from 0.3.2, chain menu_0_1_2 .. menu_0_3_3). UI strings are PYTHON constants pushed into a `MenuData` class (`UI`, `UI_S`, `UI_SARR`, `UI_A`, `UI_AARR`, lines 1207-1412) with asserts on balance / ids / heights / widths; the rest is Java. It is also the FAN-OUT page for other mods (section 6).
- **Page MenuPage - "SkyyWynn Menu"** (`view`: main, tp, players, player, mods)
  - Opens: `/skymenu` (also `/menu`, `/sbmenu` when free; `MenuCmd` 6134-6160, `openCustomPage` 6156), right-click of item `Skyy_Menu` -> OpenCustomUI page `SkyyMenu` (`MenuPageFactory`, registered 6309), given at first join (`given/<uuid>.txt`), `Dismissing` binding (Esc) `mesc`.
  - Shows: title, hint, an info box (266 px: name + up to 9 lines, repeats the last clicked entry when tooltips fail), a 9 x 6 `ItemGrid` of launcher tiles (`ItemGridSlot` = `new ItemStack(icon, 1)` + `setName` + `setDescription` tooltip markup `<color is=...>`, `setActivatable`, `setSkipItemQualityBackground`, dim = `setItemIncompatible`), status line, footer (Back, Prev page, Next page, Close).
    Main tiles: Your Profile, Hover Tooltips, Teleport, Pocket Dimension, Accessory Bag, HUD Editor, Crafting, Skills, Collections, Island Menu, Bank, Vault, Bazaar, Auction House, Reforge, Identify, Players, Party, Guild, Mods, Server Setup, Settings (the tiles RUN the other mods' commands as the player: `handleCommand`, 3679 / 4074).
  - Root: `Group #SkyyMenu { Anchor: (Width: 800, Height: 952); ... }` (`PW = GW + 44` = 84 x 9 + 44, `PH = 952`; `MenuData.UI_ROOT`).
  - Markup: python `UI` dict 1207-1231 (ROOT / ACCENT / TITLE / HINT / GRIDWRAP / GRID / GRIDNOTIPS / INFOBOX / INFONAME / INFODESC / STATUS / FOOT / SPACER / BTNBACK / BTNPREV / BTNNEXT / BTNCLOSE, `INFO_LINES = 9`); Java `MenuPage` helpers 3275-3500 (`filler`, `put`, `paging`, `purseText`, `profileBody`, `fill`, `fillStatic`, `fillWarps`, `fillPlayers`, `fillPlayer`, `fillMods`, `nav`), `build` 3517-3578, `clearGrid` / `closePage` 3600-3630; `ENTRIES` 178-520 (data); `tooltip()` in `MenuData`.
  - Look today: root `#0b1524(0.96)` padding 22 / 14; stripe `#e0b060`; title `#ffe9c9` 23; hint `#9fb8cc` 14; info box `#142030(0.9)` (name `#ffe9a0` 18, text `#c9dff0` 15 / `#9fb8cc` 14); status `#ffd27f` 15; buttons brown `#5a4420 / #8a6a30 / #3a2a10` label `#ffe9c9` 17; grid `SlotSize 84`, `SlotIconSize 62`, `SlotSpacing 0`. No textures. Fonts 14-23.
  - Vanilla?: no. The grid itself is engine-drawn (slots, tooltips); only the frame / info box / footer are Skyy markup.
  - Dynamic: 54 slots rebuilt per view (`acts[54]`, `names[54]`, `bodies[54]`), `SlotClicking` (`"SlotIndex"` in the payload; binding with `false` so it never locks the interface), `RefreshTask` + `CloseTask` (a page command replaces the menu itself; `clearGrid()` empties every slot in ONE update before closing to stop a stuck tooltip), `Tips.isOff` per-player switch swaps in `GRIDNOTIPS` (`InfoDisplay: None`), `pageNo` / `pages`.
  - Risk: HIGH. Grid geometry (9 x 84 = 756 px) + tooltip behaviour + click / close ordering rules; restyle the frame, info box and footer only and keep the `ItemGrid` slots as the launcher tiles.
- **Page SettingsPage - "Settings"** (player switches)
  - Opens: `/settings` (aliases `/skysettings`; `SettingsCmd` 3999-4008, `openCustomPage` at 4008), Menu tile "Settings".
  - Shows: title, hint, two tab rows (8 tabs: Skills, Collections, Sacks & Crafting, Combat & Classes, Coins & Bank, Profiles & Islands, Cooking & Trees, General), a tab heading, 8 rows per page (name + description + ON / OFF; rows come from `settings:fn:register` of 14 mods), an "Always shown" note per tab, Prev / Next, "Reset all to defaults" (armed second click), "< SkyyWynn Menu", Close, status line.
  - Root: `Group #SkyyStg { Anchor: (Width: 1120, Height: 930); ... }` (`SPW, SPH` 1120 x 930; `MenuData.UI_SROOT`, line 3867).
  - Markup: python `_tbs`, `SBS`, `ON_SEL`, `OFF_SEL`, `TAB_SEL`, `RESET_ARM`, `UI_S`, `UI_SARR` 1237-1290 (strings validated: ids start `SkyyStg`, fixed inline text only `[A-Za-z0-9 <>/-]`, `_stall` height assert); Java `SettingsPage` ctor 3080, `build` 3846-3944, handler 3946-3996.
  - Look today: as Menu (brown buttons 18 pt); tab selected `#e0b060 / #f0c880 / #b08840` label `#2a1a00`; ON `#7fe07f / #a0f0a0 / #5fb05f` label `#062a06`, OFF `#e07070 / #f09090 / #b05050` label `#2a0606`, reset armed `#a03030 / #c04040 / #801818`; rows `#142030(0.92)` 61 px (name `#ffffff` 21, description `#b8c8d8` 16); note `#8fa0b0` 15; status `#ffd27f` 17. Fonts 15-28.
  - Vanilla?: no. Vanilla models: `Fields/CheckboxRow`, `@CheckBox`, `@TopTabsStyle`.
  - Dynamic: rows filled from the registry (`SetReg`), 8 fixed row groups `SkyyStgRow<r>`, `SkyyStgOn/Off<r>`, tab ids `SkyyStgTab<i>`; paging when a tab has more than 8.
  - Risk: HIGH (shared by 14 mods' switches, exact width asserts `14 + 774 + 120 + 10 + 120 <= 1080`).
- **Page AdminPage - "Server Setup"** (`/modconfig`; 9 views)
  - Opens: `/modconfig [mod]` and `/serversetup` (`AdminCmd` 6113-6130, `AdminModCmd` 6101), Menu tile "Server Setup" (and, for admins, a Server Setup entry per mod in the Menu Mods view), links from other pages (Ranks / Hud `< Server Setup`), needs `skyymenu.modconfig` (view) + the mod's `.admin` node to change; opened at 3760 / 6090.
  - Views (`view`): `list` (one row per registered mod: name, version, summary / red state, "Open"; search field), `mod` (tab row of the mod's categories, 7 rows per page of the kit rows: bool ON / OFF, number / text = TextField + Set (+ Less / More), choice = up to 4 buttons or "<" value ">", action, link "Open", table / items "Open - n entries" + a Default button per row; help line under each row; footer Prev / Next, Changes, History, Export / Import, Back, Close), `table` (key-family tables: find box, column heads, 7 entry rows, add row), `confirm` (question box, up to 16 lines, Confirm / Cancel), `log` ("Changes": config-changes.log lines with Undo, 10 per page, mod filter), `hist` ("History": saved file versions, preview panel 282 px, Restore), `io` (Export / Import codes: export box, scope button, import box), `locked` (no permission), `fileonly` (installed mod without kit rows: file names only).
  - Root: `Group #SkyyAdm { Anchor: (Width: 1120, Height: 930); ... }` (`APW, APH`; `MenuData.UI_AROOT`, line 4466); body height `A_BODY` = 733.
  - Markup: python `_tbsz`, `ADM_STYLE` (BS / BS16 / SEL / SEL16 / ONSEL / OFFSEL / RED), `UI_A`, `UI_AARR`, samples + asserts 1300-1412 (row counts `ADM_ROWS 7, ADM_LROWS 8, ADM_GROWS 10, ADM_HROWS 8, ADM_INFOLINES 24, ADM_MSGLINES 16, ADM_PLINES 12, ADM_FROWS 4`); Java `AdminPage` helpers `lab` 4425, `field` 4431, `evReset / evField / evd / bind / bindEnter` 4438-4463, `frame` 4465-4473, `foot` / `tail` 4487-4504, `tabRow` 4506, `preview` 4513, `drawLocked` 4527, `summary` ~4540, `drawList` 4642-4710, `drawRow` 4766-4877 (the one renderer of every kit row type), `drawFileOnly` 4879-4934, `drawMod` 4936-5003, `drawTable` 5020-5173, `drawConfirm` 5176-5200, `drawLog` 5228-5306, `drawHist` 5318-5381, `drawIo` 5384-5435, `build` 5439-5451 on.
  - Look today: same palette as Settings; rows `#142030(0.92)` 70 px (name `#ffffff` 20 bold, help `#b8c8d8` 15, read-only value `#ffe9a0` 19); TextField box `#16263a`; preview / info panels `#101c2c`, `#142030(0.92)`; status kinds `#ffd27f / #7fe07f / #ffb347 / #ff7a7a`; tabs 126 x 48 at 16 pt with label clipped to 14 characters. Fonts 15-28. No textures.
  - Vanilla?: no. Vanilla models: `Fields/*Row`, `@TopTabsStyle`, `PluginListPage`.
  - Dynamic: EVERY button carries EVERY TextField of the view (`evd()`; drafts survive any click), fixed row groups per view (ids `SkyyAdmRow<r>`, `SkyyAdmVal<r>`, `SkyyAdmSet<r>` ...), `rowKeys[]`, `drafts`, `pending*` confirm state, search hits jump; kit ops through the `config:fn:<Mod>` bridge function.
  - Risk: VERY HIGH. About 100 constants + 5 helper families whose sizes are tied together by asserts (`ADM_INNER`, footer width, 7 x 76 rows); it is the single place where all 18 mods' settings look change. Build it last among the big ones (B7) and re-run the full cross-check afterwards.

### 5.16 SkyyParty 0.1.5 - `SkyyParty/build_skyyparty_0.1.5.py` (1500 lines)

- **Build:** copy + edit since 0.1.3 (no patch script). Kit rows + player switches (party invites). Menu tile "Party"; chat `/pc`.
- **Page PartyPage - "Party"**
  - Opens: `/party` with no args (`PartyCmd` 1313, `openCustomPage` 1331), Menu tile; the sub-commands are chat.
  - Shows: title ("Party  n / max players"), info line, pending invite row (Accept / Decline + seconds), the member table (Member / Health / Stamina / Mana / Where; per member a name + role, three stat columns with a two-part bar each, Online / Offline + place ("Hub", "Your island", "<name>'s island", "(with you)"), leader-only Promote / Kick per other member; more than 5 members switches to a compact row height), or the "Play together - start a party" help box, an invite row (name TextField + Invite), Leave party, Disband party (leader), Refresh, Close, two footer lines.
  - Root: `Group #SkyyParty { Anchor: (Width: 1240, Height: 840); ... }` (line 1030).
  - Markup: `PartyPage` ctor 893-899, `jsonStr` 900, `style` 936, `stats` 962-965, `where` 967-992, `statCol` 994-1009 (the bar), `closePage` 1011-1016, `build` 1018-1176, `handleDataEvent` 1180-1211.
  - Look today: root `#0b1524(0.96)` padding 16 / 12; stripe `#7fb0e0` 2 px; title `#e6f2ff` 28; info `#f0d890` 18; member rows `#13243a` (you `#1b3354`), invite row `#1f3a24`; names `#ffffff` 22 (leader `#f0c850`), roles `#9fb8d0` / `#f0c850`, online `#8fe08f` / offline `#e08f8f`; bars 170 x 14 px (fill `#d04848 / #e0b040 / #4a8ae0`, rest `#3a1a1a / #3a3014 / #142440`); heads `#8fa4b8` 15; TextField box `#16263a`; buttons blue `#1d3a5f / #2f5a8f / #0f2038`, red `#6a2020 / #8f3030 / #401010`, green `#1f5a2a / #2f8040 / #10381a` (18 / 15 pt). Fonts 14-28. No textures.
  - Vanilla?: no.
  - Dynamic: rows in a loop `SkyyPRow<i>` (`SkyyPHp/St/Mp<i>` bars, `SkyyPPro<i>` / `SkyyPKick<i>` carry the member UUID in the payload `promote:<uuid>`), stats from the bridge `party:stats:<uuid>` (updated on Refresh only; the page never updates itself), invite TextField `@InviteName` (Enter `Validating` or the button), `info`.
  - Risk: LOW-MEDIUM. One page; the stat bar width (170 px) and 5 / compact row logic are the only geometry.

### 5.17 SkyyProfiles 0.1.2 - `SkyyProfiles/build_skyyprofiles_0.1.2.py` (2759 lines)

- **Build:** patch-based (`tools/profiles_0_1_2_patch.py` from 0.1.1). Kit rows + player switches.
- **Page ProfilePage - "Profiles" / "Create your first profile"** (`view` 0 list, 1 create; `first`)
  - Opens: `/profiles` (`ProfilesCmd` 2520; `openCustomPage` at 2222 (`ProfilePage(pr, v, first)`)), `/profiles create`, automatically at first join with no profile (`OpenTask`, `new ProfilePage(pr, 1, true)` at 2295; same calm / island-wait / never-replace guards as Classes), Menu (Your Profile tile only shows text).
  - Shows: **list** = title + sub line, one card per profile (class item icon, name + "ACTIVE", class + combat skill, created / last played, Switch or "Active"), an empty-slot card with "Create new" while `n < maxProfiles`, info line, an inline confirm row ("Switch to X? Your inventory is saved ...", Confirm / Cancel) or a footer; **create** = "Profile N will be called <name>" + "Other name", sub text (kit / locked-forever wording), up to 8 class cards (3 item icons, name, skill + weapons line, role line, description, Select / Selected / "Coming later"; a `tight` variant for 8 cards), a "Create X as a Y? The class can never be changed." row with Create profile + Later / Back, info line.
  - Root: `Group #SkyyPf { Anchor: (Width: 1000, Height: 900); ... }` for both views (lines 1943 and 2015) (`PAGE_W, PAGE_H` line 229; `MAX_CARDS = 8` line 231).
  - Markup: consts `BTN` / `BTN_GO` 1880-1885 and `ui()` 1886 (python `__X__` placeholder substitution for ~60 sizes), `safe` 1906, `prepareCreate` 1911-1935, `buildList` 1937-2008, `buildCreate` 2010-2091, `build` 2093-2099, `closeSelf` 2101, `handleDataEvent` about 2115-2222.
  - Look today: identical to Classes: root `#0b1524(0.96)`, stripe `#d08a4a`, title `#ffe9c9` 20, sub `#9fb8cc`, cards `#173524(0.95)` / `#3a2f1a(0.95)` / `#142030(0.9)` / `#0d1219(0.85)`, class colour names, `#5f6b78` locked, brown / green-go buttons 14 pt. Fonts 11-20 (card lines 11-13). No textures. Icons `ItemIcon`.
  - Vanilla?: no.
  - Dynamic: list rows per profile id (`SkyyPfCard<id>`, `SkyyPfSw<id>`), create cards per roster index (`SkyyPfCls<i>`, `SkyyPfPick<i>`), `pending` (armed switch), `pickName` / `pickClass`, `first`, `info`; a "Later" on the first-profile page reminds in chat (`remindFirst`).
  - Risk: LOW-MEDIUM (tight variant for 8 cards; auto-open flow must stay unchanged). Restyle together with ClassPage.

### 5.18 SkyyRanks 0.1.1 - `SkyyRanks/build_skyyranks_0.1.1.py` (4054 lines) - ALREADY VANILLA (build-proven)

- **Build:** copy + edit (no patch script). Kit rows (KEEP 10, chat prefix, priority, default rank ...) + the editor below. Menu Server Setup -> Ranks has a link row "Ranks editor".
- **Page RankPage - "Ranks" (the ranks editor)**
  - Opens: `/rankadmin` (page; `/rankadmin player <player>`, `sync`, `reload` are chat), the Server Setup link row (Menu runs `/rankadmin`), the footer "< Server Setup" runs `/modconfig ranks` (3864); the many `/rank ...` commands are chat. `skyyranks.admin` only (ops and the Owner rank); everybody else sees a locked view (`guard()`).
  - Shows: vanilla frame, hint, tab row (Ranks, Players, Settings, Grants, Members), status line, footer; views: ranks list (7 rows per page: Up / Down / Edit / Delete + a create row: id + name + "Create rank"), rank -> Settings (display name, chat prefix + colour, staff on / off, default, ...), Grants (search, grant / remove rows), Members (add by name, online list, remove), players (search, list, Open), player (set rank with `<` `>` picker + "Set rank", denies, groups readout), confirm (warning `#ffcc00` + message + Confirm / Cancel).
  - Root: `RankUI.ROOT` = `Group #SkyyRk { Anchor: (Width: 1120, Height: 860); }` (`PW, PH, NROWS = 1120, 860, 7`; line 3631 `appendInline((String) null, RankUI.ROOT)`).
  - Markup: python kit 614-901 (section 2.1); Java `RankPage` 3056-3664: `init` / ctors 3062-3100, `guard`, `redraw`, `jsonStr`, `evd` / `bind` / `bindEnter` 3150-3160, `rowStart` 3171, `texts` 3178, `rowEnd` 3185, `sp` 3187, `button` 3189, `pre` 3195, `empty` 3202, `addRow` 3207, `field` 3214, `act` 3224, `tab` 3231, `buildTabs` 3236, `buildStatus` 3253, `buildFoot` 3261, `buildRanks` 3279-3320, `setRow` 3323, `buildSettings` 3334-3380, `buildGrants` 3383-3437, `buildMembers` 3440-3487, `buildPlayers` 3490-3527, `buildPlayer` 3530-3594, `buildConfirm` 3596-3614, `build` 3625-3664.
  - Look today: textures `Common/ContainerHeader.png`, `ContainerDecorationTop/Bottom.png`, `ContainerPatch.png`, `InputBox.png`, `Buttons/{Primary,Secondary,Destructive,Tertiary}(_Hovered|_Pressed).png`, `Tertiary_Active.png`; sounds ButtonsLight / ButtonsCancel; colours `#101925(0.55)` row, `#4274a5` bar, `#d6e4ee` name, `#7f93a6` caption, `#9aacbc` section, `#2b3542` separator, `#96a9be` hint, `#797b7c` dim, `#5a6a7a`, `#bdcbd3` / `#bfcdd5` button text, `#b4c8c9` title, `#6e7da1` placeholder, `#39f493` ok, `#ff6b6b` error, `#E8A93B` info, `#ffcc00` confirm; rank prefix colours are DATA (`#ff5555`, `#55ffff`, `#ffaa00` seeds). Fonts 12-32 (vanilla sizes scaled up).
  - Vanilla?: YES, proven at build (55 style values + 21 textures / sounds, `_check_ui` also asserts ids `SkyyRk*`, no underscores, a height and width budget).
  - Dynamic: rows via `rowStart` / `texts` / `button` with `%R` placeholders, `rowKeys`, `pending` confirm array, TextFields `F0` / `F1` with `@F0` / `@F1` payloads and Enter bindings, 7 rows per page, `pageNo` / `pages`, `testMode` (a harness constructor without PlayerRef).
  - Risk: LOW to keep; it is the template for the kit (section 4.2).

### 5.19 SkyySacks 0.7.7 - `SkyySacks/build_skyysacks_0.7.7.py` (4619 lines) - MIXED (bag page vanilla, /craft old)

- **Build:** patch-based (`tools/sacks_0_7_7_patch.py` from 0.7.6, chain sacks_0_2 .. 0_7_7). Kit rows (five bag caps, free recipes, craft search ...) + player switches. Items open pages by right-click (`SacksPageFactory` / `CraftPageFactory`, registered 4439-4448: ids `SkyySacks`, `SkyySacksMining|Foraging|Farming|Combat|Smithing`, `SkyySacksCraft`, `SkyySacksAlchemy`, `SkyySacksFurnace`, `SkyySacksTannery`).
- **Page SacksPage - "Magic Bags" (the pocket dimension)** - VANILLA (0.7.7)
  - Opens: `/sacks` (aliases `/pd`, `/bags`; `SacksCmd` 2531-2548: `openCustomPageWithWindows(page, an empty container window)` so the inventory shows under the page), right-click of a bag item (page id per bag type), the CraftPage "< Back to bags" button, Menu tile "Pocket Dimension".
  - Shows: vanilla frame "Magic Bags", 5 bag tabs (Mining, Foraging, Farming, Combat, Smithing) in the best carried bag's rarity colour (grey = not carried) + a Craft tab, a grey-tab note; **carried view** = cap line (bag rarity, "up to N of each item - M stored"), "Next: <bag> - <unlock text>" line, a 4 x 9 grid of 74 px item cards (`Button` with `ItemIcon`, count label; left click takes a stack, right click takes one), info line, Pick up all / Deposit all;
    **not-carried view** (`buildNoBag`) = how to get the Normal bag (recipe icons, your counts), unlock status (free / unlocked / collection tier with progress), the whole rarity ladder with caps and unlocks, what already waits in it, hint.
  - Root: `Group #SkyySacks { Anchor: (Width: 1000, Height: 640); }` (line 2368; body 577 px).
  - Markup: `safe` 2171; vanilla consts `V_SND / V_LBL / V_BTN / V_CELL` 2222-2237, `iconBox` 2241, `tabStyle` 2246-2252, `unlockText` ~2275, `nextLine` ~2290; `buildNoBag` 2298-2358; `render` 2362-2441 (frame 2368-2373, tabs 2376-2390, cells 2410-2426, actions 2436-2441); `build` 2446-2456; `handleDataEvent` 2462-2515; `profileNotice` 2520-2527; `SacksCmd` 2531; `SacksPageFactory` 2550.
  - Look today: textures `Common/ContainerHeader.png`, `ContainerDecorationTop/Bottom.png`, `ContainerPatch.png`, `Common/Buttons/Secondary(_Hovered|_Pressed).png`, `Tertiary(_Hovered|_Active|_Pressed).png`; sounds `ButtonsLightActivate/Hover`; `FontName: "Secondary"` title `#b4c8c9` 15; label `#96a9be`, caption `#878e9c`, info `#7caacc`, ok `#3d913f`, error `#cc4444`, gold `#E8A93B`, disabled `#797b7c`, separator `#2b3542`; item cards `#252f3a` (hover `#c9a050`, pressed `#a08040`, disabled `#1a1e24`) over `#1c2835` (empty `#1c2835(0.55)`); bag rarity colours `SackDefs.RAR_PAGE` = `#ffffff #ffff55 #ff55ff #55ffff #aa00aa` (Normal / Unique / Rare / Legendary / Mythic). Fonts 13-28.
  - Vanilla?: YES (copied from Common.ui / Sounds.ui / `BarterTradeRow`; not build-proven; not yet seen on the client).
  - Dynamic: `cat`, `carried`, `cells[36]` (item id per drawn cell), 5 tab ids `SkyySTab<Cat>`, bindings `tab:<Cat>`, `cell:<idx>:stack|one` (`Activating` + `RightClicking`), `pickall`, `depall`, `craft`; `profileNotice(k)` sends ONE `sendUpdate` (text "Your profile changed - click a tab to refresh") when the profile key changes (not periodic).
  - Risk: LOW to keep (only migrate); the page + empty window pairing is the delicate part.
- **Page CraftPage - "Crafting" (`/craft`)** - OLD
  - Opens: `/craft` (aliases `/recipes`; `/craft <words>` opens it searching; `CraftCmd` 4209-4232), right-click ids `SkyySacksCraft|Alchemy|Furnace|Tannery`, the SacksPage "Craft" tab, Menu tile "Crafting".
  - Shows: title, a tab row (multi-row: "< Back to bags", Crafting, Smithing, [Farming], [Campfire], [Furnace], [Tannery ...], [Collections]; tabs appear with the accessory tiers you own), a search TextField + Search / Clear (Crafting / Smithing / Farming tabs), a materials note, recipe rows (9 per page: item icon, name, "need" line in green / red with your counts, Craft / x10 / All n), Prev / Page n / Next, "Craftable only: ON / OFF";
    **Processing benches** (Furnace, Tannery) = status line, progress line, a 20-segment bar (each segment a `Group` with `Visible: true|false`), queue line, output row (Collect, Cancel queue, Unload fuel), fuel buttons (up to 4), recipe rows (7 per page: Queue / x10 / All), pager.
  - Root: `Group #SkyyCraft { Anchor: (Width: 1000, Height: 830); ... }` (line 3894).
  - Markup: `buildProc` 3728-3856, `handleProc` 3858-3886, `build` 3888-4018, `handleDataEvent` 4022 on; `CraftPageFactory` ~4237; `profileNotice` 4198.
  - Look today: root `#0b1524(0.96)` padding 16 / 10; stripe `#7fb0e0` 2 px; title `#e6f2ff` 19; buttons blue `#1d3a5f / #2f5a8f / #0f2038` label `#dceeff` 13 (ON `#7fb0e0 / #a0c8f0 / #5f90c0` label `#06192a`); rows `#10233a(0.9)` (unavailable `#0e1826(0.6)`); need line `#9fd8a2` / `#c07070` 12; progress track `#1a2838`, fill `#e0a040`; status `#ffd9a0` 14, info `#c9b89a`; search box `#16263a`. Fonts 12-19. No textures.
  - Vanilla?: no (the SacksPage in the same script is; reuse its `V_*` strings).
  - Dynamic: `tabs` (from `buildTabs` 3330), `tab`, `pageNo`, `query`, `rows` (recipes drawn; the click indexes them), `key` (profile key), `fuelIds[4]`, per-row ids `SkyyCRow<i>`, `SkyyCCraft/Ten/All<i>`, `SkyyPQ/PTen/PAll<i>`, 20 bar segments `SkyyPSeg<i>`; `@SearchQuery` payload on Search + Enter; the page is never refreshed by a timer (0.7.3 removed `live()`).
  - Risk: HIGH. Recipe / craft logic and the search path are intertwined with the markup in one 300-line method; 9 rows + 2 tab rows + search must fit under a frame; keep the two-step "craft counts from live materials" logic untouched.

### 5.20 SkyySkills 0.4.6 - `SkyySkills/build_skyyskills_0.4.6.py` (9651 lines)

- **Build:** patch-based (`tools/skills_0_4_6_patch.py` from the EDITED 0.4.5; never re-run skills_0_4_5_patch.py). Kit rows + player switches. The Stats page also renders text lines contributed by other mods (`skill:stats:<Skill>`, e.g. Cooking) and the Trees bridge opens tree pages.
- **Page SkillsPage - "Skills" / "Top 10 - <skill>"** (`view` -1 = overview, >= 0 = leaderboard of that skill)
  - Opens: `/skills` (aliases `/skill`; `SkillsCmd` 9523-9545), Menu tile "Skills", back buttons of StatsPage / OverallPage / TreePage / ExplorePage; the leaderboard view opens from StatsPage's "Top 10" (`/skills top <skill>` prints to chat).
  - Shows: overview = title, "Overall Level n - average x of k skills" + Overall button, 9 skill rows (`ROW_SLOTS` 0,1,2,10,11,12,4,13,3 = Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration, and your class combat skill): item icon, title "<skill> <level>" in the skill colour, XP bar (`BARW` 400 or 330 with the Tree button), "n / m XP to level L", Acrobatics bonus line, Tree (when the tree exists) and Stats buttons; footer line; leaderboard = top 10 rows + your rank + Back.
  - Root: `Group #SkyySkills { Anchor: (Width: 640, Height: 690); ... }` (line 8203).
  - Markup: `BARW` 8186, `SkillsPage` ctor 8189, `safe` 8194, `build` 8199-8290 (`bs` inline style at 8201), `handleDataEvent` 8709-8733; `SkillTop` 8133-8185 (leaderboard data).
  - Look today: root `#0b1524(0.96)` padding 16 / 10; stripe `#9fe0a0` 2 px; title `#e6fff0` 16; overall line `#E8A93B` 14; rows `#142030(0.9)` 58 px (Acrobatics 72); skill name in `SkillDefs.COLORS`; bar `#22324a` track; progress text `#b8c8d8` 11; Acrobatics bonus `#d8c0ff` 10; footer `#7f94a8` 10; buttons green `#27463a / #3b6b54 / #172a22` label `#dcffe8` 12. Fonts 10-16 (the smallest text in the set outside Hud). No textures. Icons `ItemIcon` 44 px.
  - Vanilla?: no.
  - Dynamic: rows built in a loop over `ROW_SLOTS` (ids `SkySkRow<i>`, `SkySkStat<i>`, `SkySkTree<i>`, `SkySkBar<i>`), class row swaps to the chosen class skill, bindings `skstat<slot>`, `sktree<slot>`, `skstatov`, `skback`.
  - Risk: MEDIUM. 640 px wide with Tree + Stats buttons and 10 pt lines; readable sizes need a wider root (960 like StatsPage).
- **Page StatsPage - "<Skill> - level n of 100"** (`slot`)
  - Opens: SkillsPage "Stats" buttons, `/skills stats <skill>` (`StatsCmd` 9455).
  - Shows: title, "n / m XP to level L (x to go)", XP bar (600 x 18), an optional orange "You are not a <class> right now" note, "Boosts right now (level n)" up to 7 lines, "Level n+1 adds" up to 7 lines, a how-to line (wraps to 2), buttons `< Back`, `Top 10`, `Skill tree` (when a tree exists).
  - Root: `Group #SkySkStats { Anchor: (Width: 960, Height: 795); ... }` (line 8524; scaled 1.5x in 0.4.2).
  - Markup: `STBARW` 8294, `StatsPage` ctor 8299; `num` 8306, `pc` / `stat`, `lines` 8401, `how` 8478 (text builders; also `PerkCfg`, other mods' `skill:stats:*` hooks); `line` 8494, `wrapLine` 8500; `build` 8505-8573; `handleDataEvent` 8575-8597.
  - Look today: as SkillsPage but scaled: root `#0b1524(0.96)` padding 24 / 15, stripe `#9fe0a0` 3 px, title 24 in the skill colour, sub `#9fb8cc` 17, heads `#e6fff0` 20, lines `#dfe8f0` 18 (next `#bfe8c8`), note `#ffb080` 17, how `#8fa6ba` 15, bar `#22324a`, buttons `#27463a / #3b6b54 / #172a22` 18. No textures. Fonts 15-24.
  - Vanilla?: no. Risk: LOW-MEDIUM (text-heavy; height budget 752 px asserted in the comment at 8226).
- **Page OverallPage - "Overall Level"** - PARTIALLY VANILLA (0.4.6)
  - Opens: SkillsPage "Overall" button, `/skills stats overall` (9465). Shows: level "n of 100", average sentence, XP-style bar (600 x 18), "Skills that count (n)" list, "Boosts right now" (up to 3), "Overall Level n+1 adds" (up to 2), how-to text, Back.
  - Root: `Group #SkyyOvPage { Anchor: (Width: 960, Height: 795); LayoutMode: Top; }` (line 8659) = header (44) + body (751).
  - Markup: `VAN_HEAD / VAN_PANEL / VAN_TITLE / VAN_BTN` 8601-8609, the client texture assertion `_VAN_TEX` 8611-8619, `OVBARW` 8620, `line` 8631, `wrapLine` 8636, `gap` 8641, `sep` 8645, `build` 8649-8695, `handleDataEvent` 8699-8706.
  - Look today: textures `Common/ContainerHeaderNoRunes.png` (HorizontalBorder 35), `Common/ContainerPatch.png` (Border 23), `Common/Buttons/Secondary(_Hovered|_Pressed).png`; colours `#b4c8c9` title (20), `#96a9be`, `#ffffff`, `#878e9c`, `#2b3542`, bar `#1a2030` / `#aa7c4a`, `#bfcdd5`, `#E8A93B`, button `#bdcbd3` 17. NO decorations, NO sounds, NO `FontName`.
  - Vanilla?: partly (a different container variant than Ranks / Vault / Gear / Sacks; values not build-checked). Risk: LOW (migrate to the kit's frame for consistency).

### 5.21 SkyyTrees 0.2.4 - `SkyyTrees/build_skyytrees_0.2.4.py` (4270 lines)

- **Build:** patch-based (`tools/trees_0_2_4_patch.py` from the EDITED 0.2.3; never re-run trees_0_2_3_patch.py). Kit rows (general, abilities, nodes tables) + player switch ("Tree bonus" line).
- **Page TreePage - "<Tree> skill tree"** (`tree` 0-5: Mining, Foraging, Farming, Cooking, Acrobatics, Exploration)
  - Opens: `/tree` (`TreeCmd` 4194; `/tree <name>` `TreeSkillCmd` 4152 opens that tree; `/tree quiet` chat), Skills / Stats "Tree" buttons (`SkillBonus.openTree` -> `handleCommand("tree <name>")`), Exploration footer "Exploration tree"; `openCustomPage` at 4144 (`TreePage.LASTTREE` remembers the last tree per player).
  - Shows: header row (6 tree tabs 88 x 32, level `<tree> n`, "Tokens a of b", "Dust d"), one-line note, a 2 px rule in the tree colour, the grid: 6 tier rows (I-VI, gated by skill level) x up to 4 node cards (`Button` 158 x 76 with a 44 px `ItemIcon`, name + a state line "Locked / Unlock / Level n"), and the detail panel (330 x 498: icon, name (S<n>), state, now / next effect, cost, needs, how text, Buy button "Unlock - n tokens" / "Level up - d Dust" / "Need ..." + Turn on / off), footer (`< Skills`, "Respec <tree>" -> "Click again to respec" armed 10 s, message line).
  - Root: `Group #SkyyTrRoot { Anchor: (Width: 1000, Height: 660); ... }` (line 3771).
  - Markup: python `tbs` + `T["BSG" ...]` 3588-3604 and node colour arrays `BG / HV / FG / SOON_*` 3606-3617; `TreePage` ctor 3619, `safe` 3628, state helpers 3640-3752 (`stateLine`, `nowLine`, `needLine`, `buyText`, `note` ...), `line` 3753-3756, `build` 3758-3841, `handleDataEvent` 3843-3880.
  - Look today: root `#0b1524(0.96)` padding 14 / 10; no top stripe (a 2 px rule in the tree colour under the note); tabs `BTON` `#3b6b54 / #4a8068 / #172a22` (selected, white) / `BTOFF` `#1d2c3c / #2c4258 / #142030` label `#b8c8d8` 12; node states `BG #1c1414 (locked) / #16301f (can unlock) / #10243d (unlocked) / #3a3010 (maxed)`, hover `#2c2020 / #22462e / #1a3a5e / #54461a`, text `#b07a68 / #9adf86 / #9cd8ff / #ffc300`, coming later `#1a1a24 / #262634 / #8890a0`, disabled `#141414`; detail panel `#101d30`; Buy `BSG` green / `BSX` grey `#262626`, respec red `#5a1e1e / #7a2a2a / #3a1414`; tokens `#ffe08a`, dust `#c8a0ff`; tree colours `#8fc8ff #8fe08a #f0d060 #ffb070 #c8a0ff #e0a040`. Fonts 10-16 (node card text 10-11). No textures.
  - Vanilla?: no.
  - Dynamic: 12 nodes per tree looped by tier (`SkyyTrN<s>`, `SkyyTrRow<k>`), `sel` node, `armT / armAt` (respec double click, 10 s), `msg`, bindings `trtab<i>`, `trnode<s>`, `trbuy`, `trtoggle`, `trrespec`, `trback` (runs `/skills`), all text through `b.set`.
  - Risk: MEDIUM-HIGH. The node card is a `Button` with two labels and an icon inside a 158 x 76 cell; readable font sizes (16+) do not fit 76 px cards, so either the detail panel shrinks or nodes move to icon tiles + tooltips. Restyle with Skills + Exploration (same nav).

### 5.22 SkyyVault 0.1.3 - `SkyyVault/build_skyyvault_0.1.3.py` (4155 lines) - MIXED

- **Build:** copy + edit of the EDITED 0.1.2 (no patch script; the next version copies 0.1.3). Kit rows (pages, prices, `buyConfirmCoins`, open mode). Menu tile "Vault".
- **Page VaultPage - "Vault"** - OLD
  - Opens: `/vault pages` (`VaultPagesCmd` -> `VStore.openNav` 2603-2620; `VStore.open2` 2539 does the page / window / session plumbing), the page-mode default (`openMode` page: `openCustomPageWithWindows(page, vault window)` at 2574 shows the vault slots under the page), Menu tile "Vault"; in chest mode `/vault` opens the chest window only (no page). `/vault buy|next|prev|info|<page>` are chest / chat.
  - Shows: title, sub line ("One chest shared by ALL your profiles ..."), Prev / "Page n of m" / Next, page number buttons (up to 10, current green, locked grey), "Page n - x of y slots used", Open page / Open as chest, Buy page N - price (gold; asks through VBuyDlg above the threshold), Close, 3 help lines, result line.
  - Root: `Group #SkyyVault { Anchor: (Width: 1040, Height: 640); ... }` (line 1849).
  - Markup: `style` 1783, `safe` 1788, `jsonStr` 1794, `colorOf` 1816, `textOf` 1824, `refreshWith` / `refresh` 1830-1840, `build` 1841-1948 (error view 1855-1866); `handleDataEvent` after; page + window plumbing in `VStore` / `VSessions` (logic, not markup).
  - Look today: root `#0b1524(0.96)` padding 26 / 16; stripe `#b48cff` 3 px; title `#dccaff` 34; sub `#cfe3ff` 18; page label `#ffffff` 26; used line `#e6f2ff` 20; help `#b8c8d8` 17; result `#8fe39a` / `#ff9d6b` / `#cfe3ff` 19; buttons blue `#1d3a5f / #2f5a8f / #0f2038`, green `#1f5a34 / #2c7a48 / #133a22` (current page), gold `#6a4a12 / #8a641a / #3e2a08` (Buy), grey `#262f3d / #303b4c / #1a212c` label `#7f8ea6` (disabled), all 19 pt. Fonts 17-34. No textures.
  - Vanilla?: no. Risk: LOW (a small nav page; the vault chest window itself is the engine's).
- **Page VBuyDlg - "Buy page X for Y coins?"** - VANILLA, build-proven (32 values + 13 textures / sounds)
  - Opens: the gold arrow in the vault window, the page's Buy button and `/vault buy` when the price is at or above `buyConfirmCoins` (default 50,000); `askBuy` retires the vault view first, then opens this window and replaces it on Buy / Cancel (`dlgBack`); one-shot (double click, Buy then Cancel act once).
  - Shows: title "Vault", `#ffcc00` question (30), message (`#96a9be`, wraps), a purse note (red `#cc4444` when short), centred Buy (Primary, SaveSettings sound) + Cancel (Secondary, ButtonsCancel sound) buttons.
  - Root: `Group #SkyyVDlg { Anchor: (Width: 700, Height: 300); }` (line 2102); markup `VBuyDlg.build` 2097-2116, helpers `question` 2081 / `note` 2086, consts `DLG_*` 1967-2056; `askBuy` 2667; `VBuyDlg` part 2 (Buy / Cancel / Esc) 3471-3530.
  - Look today: `ContainerHeader.png`, `ContainerDecorationTop/Bottom.png`, `ContainerPatch.png` (padding 20), `Primary*.png` (VerticalBorder 12, HorizontalBorder 80), `Secondary*.png`; label 17 `#bfcdd5` / `#bdcbd3`, title `#b4c8c9` 15 with `FontName: "Secondary"`. Fonts 14-32.
  - Vanilla?: YES (from `Pages/PrefabEditorExitConfirm`). Risk: LOW (template for every confirm dialog). UNVERIFIED on the client (header item V1).

## 6. Pages that share pages or feed each other (why some mods must move together)

| Cluster | Mods | How they are coupled | Consequence for the restyle |
|---|---|---|---|
| **Server Setup fan-out** | Menu (AdminPage) <- 18 kit mods: Accessories, Classes, Collections, Cooking, Essentials, Exploration, Gear, Guilds, Hud, Islands, Menu, Party, Profiles, Ranks, Sacks, Skills, Trees, Vault (all `CFG.emit(...)`; `tools/skyycfg.py` has no UI code) | Every mod publishes `config:def:<Mod>` rows; Menu's `AdminPage.drawRow` / `drawTable` / `drawMod` draw ALL of them (bool, int / text, choice, action, link, table, items) | Restyling `AdminPage` restyles every mod's settings at once; no per-mod change is needed. Coins, Bank, Bazaar, Auctions have no kit rows (they get theirs as SkyyEconomy). |
| **Player switches** | Menu (SettingsPage) <- 14 mods: Classes, Collections, Cooking, Essentials, Exploration, Gear, Guilds, Islands, Menu, Party, Profiles, Sacks, Skills, Trees (`settings:fn:register`) | Same idea: 8 tabs x 8 rows of ON / OFF | Same: one page, 14 mods |
| **Launcher** | Menu MenuPage runs the commands of Sacks (`/sacks`, `/craft`), Accessories, Hud, Skills, Collections, Islands (`/island menu`), Bank, Vault, Bazaar, Auctions, Gear (`/reforge`, `/identify`), Party, Guilds, plus its own Settings / Server Setup; Gear's Back runs `/skymenu` | `CommandManager.handleCommand(playerRef, ...)` as the player: no compile dependency, the target page replaces the menu | A new look on either side never breaks the link; only command names / permissions matter |
| **Own admin pages beside Server Setup** | Ranks (editor), Hud (editor), Essentials (`/tradeadmin config`, `/warpadmin`), Exploration (`/exploreadmin`) | Ranks and Hud add a `< Server Setup` footer that runs `/modconfig <mod>`; Essentials' TCfgPage draws kit rows itself (duplicates `drawRow` for 3 types) | Restyle these with the same kit as Menu so an admin moving Server Setup -> editor -> back sees one style |
| **Skills family** | Skills (SkillsPage / StatsPage / OverallPage) <-> Trees (TreePage, `< Skills`) <-> Exploration (ExplorePage footer `< Skills`, `Exploration tree`) | Buttons run `/skills`, `/tree <name>`, `/tree exploration` (and `SkillBonus.openTree`); the three share the green nav style `#27463a / #3b6b54 / #172a22` and the same header / tab conventions; Skills' Stats text lines come from other mods' bridge hooks | Same kit revision, same in-game pass (Skills -> Tree -> back, Explore footer) |
| **Class cards** | Classes (ClassPage) and Profiles (ProfilePage "create") | Same card layout, same class colours / icons; both auto-open at first join (`OpenTask`, same calm / island-wait / never-replace guards) | One card component; keep the auto-open flow untouched |
| **Economy** | Bank, Bazaar, Auctions (+ Coins data); Vault / Gear / Essentials / Classes / Collections read coins | Same button conventions (brown / green / red), same purse header; SkyyEconomy 0.1 will merge Coins + Bank + Bazaar + Auctions | Build the three on one kit revision; the merged mod can copy them |
| **Crafting** | Sacks (CraftPage) <- Collections (recipe unlocks: Collections tab), Accessories (bench tiers: Farming / Furnace / Tannery / Campfire tabs), Cooking (Campfire note, grade) | Data only (bridge), no markup shared | Order-independent, but test the tab set after restyling |
| **Party / Guild** | Party (PartyPage), Guilds (GuildPage), Hud (Party + Guild widgets) | The HUD widgets read `party:*` / `guild:*` bridge keys; no markup shared | Independent |

## 7. Suggested batch order (small / low-risk first, then big; parallel where the mods do not touch each other)

Size proxy = `appendInline` call sites in the UI code (Islands builds through `lbl` / `btn` helpers, so its count understates a 460-line page): Menu 224, Essentials 146, Guilds 139, Sacks 120, Gear 119,
Collections 101, Hud 100, Exploration 87, Ranks 70, Skills 65, Profiles 59, Party 58, Bazaar 52, Auctions 49, Bank 47, Vault 45, Trees 31, Classes 29, Accessories 19, Islands 19 (+ helper calls).
Budget note (HANDOFF / memory): about 4-6 builders at once, sonnet reviews. Every build: plain `python`, must end `assembled ...jar`, then `python tools/ci/lint.py` (0 fails); after each batch the whole-set cross-check (one JVM, `-Xverify:all`, Adventurer permission audit) and a `HANDOFF` log line by the main session.

| Batch | What | Mods (next version) | Builders | Why here | Depends on |
|---|---|---|---|---|---|
| **B0** | Gate + kit | (a) Skyy looks at the six existing vanilla pages in game (Ranks editor, `/reforge`, `/identify`, `/sacks`, the Vault confirm window with a low `buyConfirmCoins`, `/skills stats overall`) and says whether frame textures, `FontName Secondary` and sounds render; (b) `tools/skyyui.py` + a harness test, extracted from Ranks `RankUI` + Gear `GearUi` + Vault `DLG_*` (section 4.2), flat-colour fallback switch | 1-2 (kit only, no mod) | Every later batch is guesswork without it; the check decides whether the textured look is the default or the fallback | nothing |
| **B1** | Small single pages (fixed layouts, no window / grid, at most 6 markup areas) | Accessories 0.4.5 (patch), Bank 0.1.4 (copy), Vault 0.1.4 (VaultPage only; copy of 0.1.3), Party 0.1.6 (copy), Classes 0.1.8 + Profiles 0.1.3 (ONE builder: shared card, first-join flow) | 5 | They exercise frame, 4 button kinds, TextField (Bank, Party), list rows (Accessories), bars (Party), item icons, inline confirm rows (Classes / Profiles) on pages with little logic in the markup | B0 |
| **K1** | Kit widening | tabs, section heads, progress bar, pager, scrolling list, `card` (from what B1 needed) | 1 | B2-B5 need tabs / bars / lists | B1 |
| **B2** | Mid, one mod each, independent | Collections 0.2.4 (patch, 4 views, 12-card grid, bars), Guilds 0.1.4 (patch, 3 views, 4 TextFields, leader-case height 867 of 872), Islands 0.5.4 (patch, 5 tabs, permission matrix, long lists) | 3 | Largest pages that need no window, no item grid, no cross-mod nav | K1 |
| **B3** | Skills family | Skills 0.4.7 (patch; SkillsPage + StatsPage, OverallPage onto the kit frame), Trees 0.2.5 (patch; node cards), Exploration 0.2.2 (copy; ExplorePage + AdminPage) | 3 (same kit revision, same in-game pass) | Shared nav + green button family; deploy and test together | K1 (can run beside B2) |
| **B4** | Economy | Bazaar 0.1.3 (patch), Auctions 0.1.3 (patch; ItemGrid detail + inventory picker + money confirm) | 2 | Same conventions as Bank; SkyyEconomy will absorb them, so keep the builds thin and leave money paths alone | K1 |
| **B5** | Sacks | Sacks 0.7.8 (patch): CraftPage to the kit (+ SacksPage onto the same kit calls) | 1 | One large logic-heavy method (search, benches, segment bar); Sacks bag page already vanilla | K1; test with Collections + Accessories tabs |
| **B6** | Essentials | Essentials 0.1.6 (patch): WarpPage + TCfgPage first, TradePage last | 1 | Trade = page + `TWindow` + `ItemGrid` columns + replace-not-close rules; the two admin pages are safe warm-ups (TCfgPage can reuse the kit's row renderer) | K1 |
| **B7** | Menu | Menu 0.3.4: MenuPage + SettingsPage; Menu 0.3.5: AdminPage (9 views, ~100 constants tied by asserts) | 1 per version (one script: do not run two builders on it) | The fan-out page (18 mods' rows, 14 mods' switches); do it after the kit has every row widget and after B1-B6 so nothing is left to rework; re-check every mod's Server Setup page afterwards | B1-B6 |
| **B8** | Hud | Hud 0.3.11 (patch): WidgetsPage, SettingsPage, EditorPage frame + buttons (canvas geometry frozen), HUD default background / colours | 1 | Most fragile page (576-slot drag canvas), player-tunable text, saved layout formats; needs an in-game drag test | B0 answers Q1 below |
| **B9** | Migration + cleanup (optional) | Ranks 0.1.2, Gear 0.2, Vault dialog, Sacks bag page, Skills Overall move from their own copies onto `tools/skyyui.py`; delete the duplicated `jsonStr` / `safe` / `style` / `colorOf` / `textOf` copies (section 4.1) | 2 | Working vanilla pages: touch them only when the kit is proven | B0-B8 |

Deploy together (same round): {Classes, Profiles}, {Skills, Trees, Exploration}, {Bazaar, Auctions}; Menu only after or with the mods whose link rows / commands it names (no compile dependency, but the look should match). Never deploy a batch before its in-game pass (Skyy's standing auto-deploy rule applies per finished round).

Per-batch acceptance list (for the builders' "in-game test steps"): every state of every view (empty / error / locked / no permission / profile loading), every button still bound (id and payload unchanged), root anchor Width / Height only, no underscore ids, inline text only `[A-Za-z0-9 <>/-]`, no page update from a Mouse handler, no periodic updates, page height <= 1080 including the 12 + 6 px decoration overhang, `ItemGridSlot` only with `new ItemStack(id, qty)`, no `.ui` files in the jar.

## 8. UNVERIFIED and open questions

**UNVERIFIED (needs Skyy in game or a further read):**
1. Whether inline `Common/...png` frame / button / input textures, `FontName: "Secondary"`, and `Sounds:` resolve on Skyy's client (none of the six vanilla pages was seen yet; Vault header V1; Gear's `ui.frames` valve exists for this). Also whether the 236 x 11 decorations sticking out 12 px above / 6 px below the root are clipped.
2. Which container variant is "right": `ContainerHeader.png` + decorations (Ranks, Vault, Gear, Sacks) or `ContainerHeaderNoRunes.png` (Skills Overall, the vanilla `@Container`). The prior art uses the decorated one four times; Overall is the odd one out.
3. That the values Gear and Sacks copied (no `VANILLA_CHECK`) still match `Assets.zip` (Ranks and Vault prove theirs at every build).
4. Every line number here is from static reading of the pinned scripts; nothing was built or run in this task. Click handlers (`handleDataEvent`) were read in full only for Accessories, Bank, Classes, Collections, Exploration (ExplorePage), Gear (ReforgePage), Hud (WidgetsPage), Skills and Trees; only the start of Party, Profiles, Islands and Sacks; not at all for Auctions, Bazaar, Essentials, Guilds, Menu, Ranks, Vault and the Hud editor / settings pages - the logic notes in the risk lines come from the markup and the comments, not from a full read of every handler.
5. Counts of mods feeding Server Setup (18) and Settings (14) come from `CFG.emit` / `settings:fn:register` in the build scripts; the runtime registry can differ (a disabled mod publishes nothing).
6. The HUD widgets' "vanilla" target: the only vanilla HUD documents are `Hud/TimeLeft.ui` and `Hud/ReturnToHubButton.ui`; the real in-game HUD is client-native.

**Questions for Skyy (design decisions the builders must not guess):**
- Q1: HUD widgets: default background `#000000(0.2)` (vanilla TimeLeft) instead of `#0b1524(0.72)`, and default text colour vanilla white / `#96a9be`? The player-tunable palette / glow stay either way.
- Q2: Font scale: Ranks used vanilla x 1.3 (14 -> 18, 12 -> 15, 13 -> 16). One scale for the kit, or per page kind?
- Q3: Keep any per-mod accent colour (stripe, title colour) as identity, or none (the vanilla frame replaces it)? Rarity / class / skill / tree colours are content and are assumed to stay.
- Q4: Economy trio: restyle Bazaar / Auctions now (B4) or wait and build SkyyEconomy 0.1 pages directly on the kit?
- Q5: Menu launcher: keep the 9 x 6 `ItemGrid` of item icons with tooltips (vanilla has no such launcher; the game's cosmetic tiles are the nearest), or move to vanilla list rows (Common.ui `PluginListPage` style)?
- Q6: Are the `+ / - / =` result colours to become the vanilla trio `#39f493` / `#ff6b6b` / `#E8A93B` everywhere (Ranks and Gear already do)?

## 9. How this inventory was made

Read-only pass over the 22 build scripts named by `tools/deploy_set.py` SET plus the patch script headers; per mod: `makeClass` / page class discovery, `appendInline` clustering (line ranges per method), every `openCustomPage` / `registerSimple` / command that opens a page, the style constants and helper methods, hex colours / font sizes / texture paths per page range (regex extraction), and the vanilla side from `Assets.zip` (`Common/UI/Custom/`: Common.ui, Sounds.ui, Hud/*, Pages/* listed by name; `TimeLeft.ui` and `ReturnToHubButton.ui` read; nothing extracted to disk). The scratch folder `tools/dev/scratch/ui-research-inventory/` held the helper scripts and drafts; it was deleted at the end. No mod, tool, design doc or handoff file was edited.
