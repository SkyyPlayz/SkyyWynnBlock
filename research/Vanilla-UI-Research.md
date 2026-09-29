# Vanilla Hytale UI - research catalogue for Skyy inline pages

Written 2026-09-29 for the vanilla UI pass (HANDOFF section 2 rule 0, tools/AGENT-BRIEF.md "UI LOOK", RESUME step 5).
Skyy's goal (2026-09-28): every UI we add should look and feel as close to the original game as possible.
This file lists every vanilla UI building block with its exact vanilla definition and the **inline-ready literal** a server-built
page (`appendInline`) should contain. It ends with a comparison to the existing VANILLA_CHECK lists and a proposed shared kit API.

Everything here was READ from the game files (nothing copied into the repo, no image files copied). Style VALUES and texture
PATHS are referenced as the project rules allow.

---

## 0. Key findings (read this first)

1. **There are two sets of vanilla UI documents, and only one of them is ours to use.**
   - `Assets.zip` -> `Common/UI/Custom/` = the **server custom-UI kit** (161 `.ui` files: `Common.ui`, `Sounds.ui`, 2 in `Common/`,
     29 HUD, 128 pages). This is the kit vanilla server pages use (Barter shop, Item repair, Warps, Respawn, Memories, the UI Gallery...),
     and its textures/sounds are the ones delivered to every client with the server assets.
   - The **client's own in-game UI** (inventory, chest, crafting benches, furnace, tooltips, pause menu, settings, HUD, map, creative
     library) is NOT in Assets.zip. It lives in the client install: `...\game\latest\Client\Data\Game\Interface\` (195 `.ui` files,
     plus 41 editor files). Read-only reference only: most of its textures (slot frames, item tooltip frames, notification patches,
     checkbox toggles) are NOT in Assets.zip, so an inline page cannot count on them (see 2.3).
   - Good news: the custom-UI `Common.ui` is an almost 1:1 copy of the client's `Common.ui` + `Common/Container.ui` (same frame, same
     button textures, same label styles, same colours). Mirroring `Common/UI/Custom/Common.ui` IS the vanilla in-game look.
     The small differences are listed in 1.3.
2. **Vanilla server code applies vanilla styles by reference**: `Value.ref("Common.ui", "DefaultTextButtonStyle")` set on
   `#TabNPC.Style` (EntitySpawnPage), `Value.ref("Common.ui", "DefaultTextTooltipStyle")` (AssetPackSaveBrowser),
   `Value.ref("Pages/BasicTextButton.ui", "SelectedLabelStyle")`, `Value.ref("Common/TextButton.ui", "LabelStyle")`. API:
   `com.hypixel.hytale.server.core.ui.Value.ref(String documentPath, String valueName)` + `UICommandBuilder.set(String, Value)`.
   The third-party HyUI 0.9.8 library in Skyy's pack also calls `Value.ref` with `"Common.ui"` (scrollbar / text-field styles). This could give our inline
   elements the EXACT vanilla style (all states + sounds) without copying literals - **UNVERIFIED for elements created by
   appendInline** (vanilla only does it on elements from its own `.ui` pages). Needs one in-game probe before the kit relies on it.
3. **Two vanilla styles in the custom kit are broken - do not copy them**: `@SmallDefaultTextButtonStyle` uses
   `Common/ButtonSmall.png` / `ButtonSmallHovered.png` / `ButtonSmallPressed.png`, which are not in Assets.zip; and
   `@ButtonDestructiveSounds = $Sounds.@ButtonsDestructive;` points at a sound set that the custom `Sounds.ui` never defines (only the
   client `Sounds.ui` has it). `@TitledDropdownBoxStyle` is commented out by the devs for missing textures.
4. **The custom kit's button click sound is louder / more varied than the client's**: custom `@ButtonsLight` Activate is
   `MinPitch -0.4, MaxPitch 0.4, Volume 4`; the client's own is `-0.2 / 0.2 / 2`. Custom pages use the custom value, so our pages
   should too (SkyyRanks / SkyyGear / SkyyVault already do).
5. Vanilla window content padding is usually `Padding: (Full: 16)` (19 pages), sometimes 20 or 24; the `@DecoratedContainer` default
   is `Full: 17`. SkyyRanks uses `(Full: 17, Top: 8)` - harmless, but not what vanilla pages do.
6. `ItemSlot` + `ShowQualityBackground: true` + `set("#X.ItemId", id)` is the vanilla way to show an item WITH its rarity slot frame
   (BarterTradeRow, DroppedItemSlot) and takes only an item id - no ItemStack, so no metadata disconnect risk. No Skyy page uses it yet.
7. SkyyVault 0.1.3's main page is still the old dark-blue custom style (`#0b1524(0.96)` root, custom green / yellow buttons); only
   its buy-confirm dialog is vanilla.
8. Texture paths in custom UI are written without `@2x` (`"Common/ContainerHeader.png"`); Assets.zip only holds the `@2x` file and the
   client picks it. Logical size = half the `@2x` pixel size (ContainerHeader@2x 1428 x 76 -> 38 px high title bar).

---

## 1. Inventory of the vanilla UI files

### 1.1 Assets.zip (READ-ONLY, `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Assets.zip`)

| Group | Count | Notes |
|---|---|---|
| `Common/UI/Custom/Common.ui` | 1 | the custom-UI style sheet (colours, frames, buttons, inputs, tabs, scrollbars, tooltips) |
| `Common/UI/Custom/Sounds.ui` | 1 | UI sound sets |
| `Common/UI/Custom/Common/*.ui` | 2 | `TextButton.ui` (list label styles), `ActionButton.ui` (key-binding hint) |
| `Common/UI/Custom/Hud/**.ui` | 29 | builder tool legends (`ToolsLegends/*`), `TimeLeft.ui`, `ReturnToHubButton.ui` |
| `Common/UI/Custom/Pages/**.ui` | 128 | vanilla server pages (see list below) |
| `Common/UI/Custom/Common/*.png` | 99 | frame / input / dropdown / scrollbar / tab / icon textures (mostly `@2x`) |
| `Common/UI/Custom/Common/Buttons/*.png` | 17 | Primary, Primary_Square, Secondary, Tertiary (+Active), Destructive, Disabled (each Default/Hovered/Pressed) |
| `Common/UI/Custom/Pages/**.png` | 80 | Memories tiles / category icons, Portals, Respawn page art |
| `Common/UI/Custom/Hud/ToolsLegends/*.png` | 2 | `LegendContainerPanelPatch`, `HintContainerPanelPatch` |
| `Common/UI/Custom/Sounds/*.ogg` | 20 | every sound the custom `Sounds.ui` names |
| `Common/UI/ItemQualities/Slots/*.png` | 9 | rarity slot frames (Default, Junk, Common, Uncommon, Rare, Epic, Legendary, Tool, Developer) |
| `Common/UI/ItemQualities/Tooltips/*.png` | 16 | rarity tooltip frames + arrows |
| `Server/Item/Qualities/*.json` | 11 | rarity -> tooltip texture, slot texture, TextColor |

Vanilla server pages by kind (all under `Common/UI/Custom/Pages/`):
- **shop / barter**: `BarterPage.ui`, `BarterTradeRow.ui`, `BarterGridSpacer.ui`, `ShopPage.ui`, `ShopElementButton.ui`
- **lists**: `WarpListPage.ui` + `WarpEntryButton.ui`, `ItemRepairPage.ui` + `ItemRepairElement.ui`, `CommandListPage.ui`,
  `PluginListPage.ui` + `PluginListButton.ui`, `PrefabListPage.ui`, `InstanceListPage.ui`, `WorldEvent/*` (list rows, section labels),
  `TriggerVolume/*` (inspector rows, tabs, chips)
- **dialogs / confirm**: `PrefabEditorExitConfirm.ui`, `NameRespawnPointPage.ui`, `SelectOverrideRespawnPointPage.ui`,
  `OverrideNearbyRespawnPointPage.ui`, `PrefabSavePage.ui`, `PortalDeviceError.ui`
- **forms / settings**: `Teleporter.ui`, `LaunchPadSettingsPage.ui`, `PrefabEditorSettings.ui`, `Fields/*Row.ui` (checkbox, dropdown,
  int, number, text, vec3 rows)
- **special**: `RespawnPage.ui` (death screen), `Memories/*` (collection tiles), `Portals/*`, `UIGallery/*` (the devs' own
  component gallery - the best single reference for "how to use each block")

### 1.2 Client install (READ-ONLY reference, `...\game\latest\Client\Data\`)

| Group | Count | What |
|---|---|---|
| `Game/Interface/Common.ui`, `Sounds.ui`, `Common/Container.ui` | 3 | the client's style sheets (the originals of the custom kit) |
| `Game/Interface/InGame/Pages/Inventory/*.ui` | 28 (+36 builder tools, +2 memories) | inventory, chest (`ContainerPanel`), storage, crafting (`BasicCraftingPanel`, `DiagramCraftingPanel`, `StructuralCraftingPanel`), furnace (`ProcessingPanel`, `ProcessingBar`), bench info, item info, character panel, quantity popup, recipe catalogue, creative item library |
| `Game/Interface/InGame/Tooltips/*.ui` | 2 | `ItemTooltip.ui`, `CreativeModeTooltip.ui` |
| `Game/Interface/InGame/Overlays/*.ui` | 3 | pause menu (`MenuOverlay`), quit confirm (`ConfirmQuitOverlay`), online play |
| `Game/Interface/InGame/Hud/**.ui` | 43 | hotbar, chat, notifications, event titles, health / stamina / mana bars, objectives, kill feed, boss bar |
| `Game/Interface/InGame/Pages/*.ui` | 7 | map (`MapPage`, markers), tools settings, entity spawn |
| `Game/Interface/Common/Settings/*.ui` | 18 | settings menu rows (checkbox, slider, dropdown, key binding, section header, warning banner) |
| `Shared/UI/Fonts/` | 12 ttf | Nunito Sans (Regular / Medium / SemiBold / ExtraBold), Lexend Bold, Noto Mono, Noto Sans (+CJK) |
| `Shared/UI/Sounds/*.ogg` | 41 | client UI sounds (InventoryOpen/Close, MapOpen/Close, DefaultTabActivate, AutoSort ... - most NOT in Assets.zip) |

### 1.3 Custom kit vs client originals - the differences that matter

| Value | `Common/UI/Custom/*.ui` (use this) | client `Game/Interface/*.ui` |
|---|---|---|
| `@ButtonsLight` Activate | `MinPitch: -0.4, MaxPitch: 0.4, Volume: 4` | `MinPitch: -0.2, MaxPitch: 0.2, Volume: 2` |
| DropdownBox Close sound | `@ButtonsCancelActivate` | `@Untick` |
| dropdown caret | `Common/DropdownCaret.png`, `Common/DropdownPressedCaret.png` | `Common/DefaultDropdownCaret.png`, `Common/PressedDropdownCaret.png` (not in Assets.zip) |
| text tooltip frame | `Common/TooltipDefaultBackground.png` Border 24 | `InGame/Tooltips/ItemTooltipDefault.png` Border 24 |
| `@PanelTitle` label | 15 bold, `#afc2c3`, default font, line `#393426(0.5)` | 15 bold UPPERCASE, font Secondary, `#cfd6e0`, ShrinkTextToFit, line `#1b2533` |
| `@SubtitleStyle` | 15 uppercase **bold** `#96a9be` | 15 uppercase `#96a9be` (not bold) |
| `@TitleStyle` | no shrink | adds `ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11` |
| Primary button name | `@TextButton` / `@DefaultTextButtonStyle` | `@PrimaryTextButton` / `@PrimaryTextButtonStyle` |
| Destructive button name | `@CancelTextButton` / `@CancelTextButtonStyle` (sounds `@ButtonsCancel`) | `@DestructiveTextButton` (sounds `@ButtonsDestructive` = same ogg) |
| small tertiary | `@SmallTertiaryTextButton` exists | not in client |
| page dim | `@PageOverlay` `#000000(0.45)` | `@Overlay` `#000000(0.82)`; inventory `#000000(0.55)` + `SceneBlur`; pause menu `#0e1219(0.90)` + `SceneBlur` |
| top tab selected | `Anchor: (...@TopTabAnchor, Bottom: 4)` | `Bottom: 0`, + `TabSounds: $Sounds.@DefaultTabNavigation` |

---

## 2. What works in an INLINE page

### 2.1 How the existing vanilla-look pages do it

SkyyRanks 0.1.1 (`SkyyRanks\build_skyyranks_0.1.1.py` lines 612-896), SkyyVault 0.1.3 (`SkyyVault\build_skyyvault_0.1.3.py` lines
1952-2044, confirm dialog only), SkyyGear 0.1 (`SkyyGear\build_skyygear_0.1.py` lines 504-563 and 5450-5536, class `GearUi`) and
SkyySacks 0.7.7 all build every element with `appendInline` and **copy the literal values** into the markup. Document variables
(`@DefaultLabelStyle`, `$C.@TextButton`, `$Sounds.@ButtonsLight`) are never used inline: an inline fragment has no `$C = "Common.ui";`
import and no `@` definitions, so every value must be spelled out. The builds then prove each copied value against Assets.zip at
build time (VANILLA_CHECK: `(document key, exact text that must be in it)` + a list of texture / sound files that must exist).

### 2.2 Paths from inline markup

| Kind | Inline form | Status |
|---|---|---|
| custom-kit texture | `"Common/ContainerHeader.png"`, `"Common/Buttons/Secondary.png"` (relative to `Common/UI/Custom/`, no `@2x`) | used by the SkyyRanks / SkyyGear / SkyySacks jars installed in `UserData\Mods`; also by HyUI 0.9.8, EndgameAndQoL 5.4.1, Clay Factoria (runtime inline markup / style objects). No in-game confirmation is recorded in HANDOFF / TEST-CHECKLIST - treat as very likely |
| custom-kit sound | `"Sounds/ButtonsLightActivate.ogg"` (relative to `Common/UI/Custom/`) | same as above |
| custom page art | `"Pages/Memories/Tiles/TileDefault.png"`, `"Hud/ToolsLegends/LegendContainerPanelPatch.png"` | same root, UNVERIFIED individually |
| rarity frames | `Common/UI/ItemQualities/...` is OUTSIDE the custom root: `"../ItemQualities/Slots/SlotRare.png"`? | UNVERIFIED - prefer `ItemSlot` + `ShowQualityBackground: true` (the engine picks the frame) |
| client-only texture | `"Pages/Inventory/Slot.png"`, `"InGame/Tooltips/ItemTooltipDefault.png"` | UNVERIFIED and contradictory: the custom `Common.ui` comments out `@TitledDropdownBoxStyle` because its textures are "missing" (they exist only client-side), but the vanilla `Hud/ReturnToHubButton.ui` points at `"../InGame/Pages/MapIcons/ReturnToCrossroads.png"`, which exists only client-side. Do not use until probed |
| vanilla style by reference | `b.set("#SkyyXBtn.Style", Value.ref("Common.ui", "SecondaryTextButtonStyle"))` | vanilla server pages do this; UNVERIFIED on inline-built elements |

Lint note: `tools/ci/lint.py` fails a line that has a quoted `...ui"` string AND `files[` / `extra_files` / `Common/UI` on the same
line. Keep `Value.ref("Common.ui", ...)` lines free of the text `Common/UI` (SkyyGear already splits `"Common/" + "UI/Custom/"`).

### 2.3 What an inline page cannot reproduce

- Client-only textures (slot frames `Pages/Inventory/Slot.png`, item tooltip frame, `CheckBox.png` ON/OFF toggle, notification patch,
  chat patches, menu label gradients, map art) - see 2.2.
- Client-only sounds not in `Common/UI/Custom/Sounds/`: `InventoryOpen.ogg`, `InventoryClose.ogg`, `MapOpen.ogg`,
  `DefaultTabActivate.ogg` (tab click), `AutoSort.ogg`, `SearchFieldExpand/Collapse.ogg`, `HoverMagic.ogg` (filter tabs).
- Full-screen dim / blur behind the window (`@PageOverlay`, `SceneBlur {}`): Skyy page roots are Width/Height only (HANDOFF rule).
  A separate root-level sibling `Group { Background: #000000(0.45); }` appended BEFORE the page root might work - UNVERIFIED.
- Localized `%server.customUI...` text keys: inline pages set plain text with `b.set("#Id.Text", ...)`.

---

## 3. Building blocks

Notation: **V** = vanilla definition (verbatim, with path); **Where** = where vanilla uses it; **Inline** = literal for a server-built
inline page. `Common.ui` without a folder = `Common/UI/Custom/Common.ui` in Assets.zip. Ids in the inline forms (`#SkyyX...`) are
examples - every page uses its own prefix, no underscores.

### 3.1 Page frame

#### 3.1.1 `@DecoratedContainer` - the standard vanilla window (title bar with runes + gold ornaments)

V (`Common.ui` lines 840-877):
```
@DecoratedContainer = Group {
  @ContentPadding = Padding(Full: 9 + 8);
  @CloseButton = false;

  Group #Title {
    Anchor: (Height: @TitleHeight, Top: 0);
    Background: (TexturePath: "Common/ContainerHeader.png", HorizontalBorder: 50, VerticalBorder: 0);
    Padding: (Top: 7);

    Group #ContainerDecorationTop {
      Anchor: (Width: 236, Height: 11, Top: -12);
      Background: "Common/ContainerDecorationTop.png";
    }
  }

  Group #Content {
    LayoutMode: Top;
    Anchor: (Top: @TitleHeight);
    Padding: @ContentPadding;
    Background: (TexturePath: "Common/ContainerPatch.png", Border: 23);
  }

  Group #ContainerDecorationBottom {
    Anchor: (Width: 236, Height: 11, Bottom: -6);
    Background: "Common/ContainerDecorationBottom.png";
  }

  Button #CloseButton { ... Visible: @CloseButton; }
};
```
plus `@TitleHeight = 38;` `@TitleOffset = 4;` (lines 662-663). The title text is placed inside `#Title` by each page with `$C.@Title`.
Where: 30 vanilla server pages (Barter, Item repair, confirm dialogs, Teleporter, Memories, UI Gallery, WorldEvent panel); client
bench / item / character info panels and the quit confirm (`Common/Container.ui` has the identical block).
Texture sizes: ContainerHeader 714 x 38 logical, ContainerPatch 66 x 66 (Border 23), decorations 236 x 11.

Inline (root + 3 children; the page root keeps Width/Height only):
```
Group #SkyyXRoot { Anchor: (Width: 900, Height: 640); }
Group #SkyyXTitle { Anchor: (Height: 38, Top: 0); Padding: (Top: 7); Background: (TexturePath: "Common/ContainerHeader.png", HorizontalBorder: 50, VerticalBorder: 0); Group { Anchor: (Width: 236, Height: 11, Top: -12); Background: "Common/ContainerDecorationTop.png"; } Label #SkyyXTitleTxt { Padding: (Horizontal: 19); Text: ""; Style: (FontSize: 15, VerticalAlignment: Center, HorizontalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: "Secondary", RenderBold: true, LetterSpacing: 0); } }
Group #SkyyXBody { Anchor: (Top: 38); LayoutMode: Top; Padding: (Full: 16); Background: (TexturePath: "Common/ContainerPatch.png", Border: 23); }
Group { Anchor: (Width: 236, Height: 11, Bottom: -6); Background: "Common/ContainerDecorationBottom.png"; }
```
(`#SkyyXTitle`, `#SkyyXBody` and the bottom decoration are appended into `#SkyyXRoot`. Body padding: vanilla default 17; vanilla pages
mostly override to 16, dialogs 20, forms 24 / `(Vertical: 32, Horizontal: 45)`.)

#### 3.1.2 `@Container` - plain window (title bar without runes, no ornaments)

V (`Common.ui` lines 811-838):
```
  Group #Title {
    Anchor: (Height: @TitleHeight, Top: 0);
    Padding: (Top: 7);
    Background: (TexturePath: "Common/ContainerHeaderNoRunes.png", HorizontalBorder: 35, VerticalBorder: 0);
  }

  Group #Content {
    LayoutMode: Top;
    Padding: @ContentPadding;
    Anchor: (Top: @TitleHeight);
    Background: (TexturePath: "Common/ContainerPatch.png", Border: 23);
  }
```
Where: Shop, Warps, Command list, side tool panels; client chest (`ContainerPanel.ui`, content padding 15), inventory storage,
crafting bench, furnace. Inline: as 3.1.1 with `"Common/ContainerHeaderNoRunes.png", HorizontalBorder: 35` and no decoration groups.

#### 3.1.3 Close button (top-right X)

V (`Common.ui` 867-876, inside `@DecoratedContainer`):
```
  Button #CloseButton {
    Anchor: (Width: 32, Height: 32, Top: -8, Right: -8);
    Style: (
      Default: (Background: "Common/ContainerCloseButton.png"),
      Hovered: (Background: "Common/ContainerCloseButtonHovered.png"),
      Pressed: (Background: "Common/ContainerCloseButtonPressed.png"),
      Sounds: @ButtonsCancel
    );
    Visible: @CloseButton;
  }
```
Where: hidden by default (`@CloseButton = false`); vanilla pages close with the bottom-left BackButton or Esc.
Inline (append into the root, bind Activating -> close):
```
Button #SkyyXClose { Anchor: (Width: 32, Height: 32, Top: -8, Right: -8); Style: ButtonStyle(Default: (Background: "Common/ContainerCloseButton.png"), Hovered: (Background: "Common/ContainerCloseButtonHovered.png"), Pressed: (Background: "Common/ContainerCloseButtonPressed.png"), Sounds: (Activate: (SoundPath: "Sounds/ButtonsCancelActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))); }
```

#### 3.1.4 BackButton, overlay, other panels

| Block | V (verbatim) | Where | Inline |
|---|---|---|---|
| `@BackButton` | `Group { LayoutMode: Left; Anchor: (Left: 50, Bottom: 50, Width: 110, Height: 27); BackButton {} }` (`Common.ui` 917-922) | bottom-left of every full-screen vanilla page | needs a full-screen parent - Skyy pages use a footer Close button + Esc instead (built-in `BackButton {}` element inside the root: UNVERIFIED) |
| `@PageOverlay` | `Group { Background: #000000(0.45); }` (879-881) | behind every custom page | see 2.3 |
| `@Panel` | `Group { Background: (TexturePath: "Common/ContainerFullPatch.png", Border: 20); }` (23-25) | UI Gallery panel demo | `Background: (TexturePath: "Common/ContainerFullPatch.png", Border: 20);` |
| `@SimpleContainer` (inner sub-panel) | `Group { Background: (TexturePath: "Common/ContainerPanelPatch.png", Border: 4); Padding: 12; }` (942-945) | gallery; client crafting recipe panel, furnace fuel / input / output boxes, character stats, bench tier box | `Group #SkyyXBox { Background: (TexturePath: "Common/ContainerPanelPatch.png", Border: 4); Padding: (Full: 12); LayoutMode: Top; }` |
| secondary panel | `Background: (TexturePath: "../Common/ContainerBackgroundSecondary.png", Border: 5);` (`Pages/PortalDeviceActive.ui`) | portal device info box | `Background: (TexturePath: "Common/ContainerBackgroundSecondary.png", Border: 5);` |
| dark info block | `Background: (Color: #000000(0.3));` + `Padding: (Vertical: 35)` (`Pages/RespawnPage.ui`) | death screen item-loss box | `Background: #000000(0.3);` |
| static row panel | `Default: (Background: (Color: #101925(0.55)))` (`Pages/WorldEvent/WorldEventListRow.ui`) | list rows, message boxes | `Background: #101925(0.55);` |

### 3.2 Titles and headings

| Block | V (verbatim, path) | Where | Inline |
|---|---|---|---|
| window title `@TitleStyle` + `@Title` | `@TitleStyle = LabelStyle(FontSize: 15, VerticalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: "Secondary", RenderBold: true, LetterSpacing: 0);` and `@Title = Label { ... Padding: (Horizontal: 19); ... };` (`Common.ui` 640-660, reformatted onto one line) | every window title bar | `Label #SkyyXTitleTxt { Padding: (Horizontal: 19); Text: ""; Style: (FontSize: 15, VerticalAlignment: Center, HorizontalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: "Secondary", RenderBold: true, LetterSpacing: 0); }` |
| section subtitle `@SubtitleStyle` | `@SubtitleStyle = LabelStyle(FontSize: 15, RenderUppercase: true, TextColor: #96a9be, RenderBold: true);` + `Anchor: (Bottom: 10)` (632-638) | UI Gallery section heads | `Label #SkyyXSub { Anchor: (Height: 24, Bottom: 10); Text: ""; Style: (FontSize: 15, RenderUppercase: true, TextColor: #96a9be, RenderBold: true, VerticalAlignment: Center); }` |
| list section label | `Style: (FontSize: 13, RenderUppercase: true, RenderBold: true, TextColor: #9aacbc, HorizontalAlignment: Start);` `Anchor: (Top: 10, Bottom: 4, Left: 2);` (`Pages/WorldEvent/WorldEventSectionLabel.ui`) | WorldEvent / TriggerVolume lists | `Label #SkyyXSec { Anchor: (Height: 20, Top: 10, Bottom: 4, Left: 2); Text: ""; Style: (FontSize: 13, RenderUppercase: true, RenderBold: true, TextColor: #9aacbc, HorizontalAlignment: Start, VerticalAlignment: Center); }` |
| panel title + line `@PanelTitle` | `Label #PanelTitle { Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3, HorizontalAlignment: @Alignment); Anchor: (Height: 35, Horizontal: 8); ... }` then `Group { Background: #393426(0.5); Anchor: (Height: 1); }` (763-779) | sub-panel headers (gallery; client furnace / crafting boxes use the client variant) | `Label #SkyyXPt { Anchor: (Height: 35, Horizontal: 8); Text: ""; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }` + `Group { Anchor: (Height: 1); Background: #393426(0.5); }` |
| client panel title (in-game look) | `Style: (RenderBold: true, RenderUppercase: true, VerticalAlignment: Center, FontSize: 15, TextColor: #cfd6e0, FontName: "Secondary", ...)`, line `Background: #1b2533;` (client `Common/Container.ui` 238-265) | chest / furnace / crafting sub-panels | same shape with `TextColor: #cfd6e0, RenderUppercase: true, FontName: "Secondary"`, line `#1b2533` |
| settings section header | `Style: (FontSize: 18, TextColor: #96a9be, RenderUppercase: true, RenderBold: true);` `Anchor: (Bottom: 16)` (client `Common/Settings/SectionHeader.ui`) | settings menu | `Label { Anchor: (Height: 26, Bottom: 16); Text: ""; Style: (FontSize: 18, TextColor: #96a9be, RenderUppercase: true, RenderBold: true, VerticalAlignment: Center); }` |
| gallery category title (highlight) | `Style: (RenderUppercase: true, RenderBold: true, FontSize: 20, TextColor: $C.@ColorDefault); MaskTexturePath: $C.@TextHighlightGradientMask;` (`Pages/UIGallery/UIGalleryPage.ui`), mask = `"Common/TextGradient.png"` | big highlighted headings, settings title (40 px) | `Label #SkyyXBig { Text: ""; MaskTexturePath: "Common/TextGradient.png"; Style: (RenderUppercase: true, RenderBold: true, FontSize: 20, TextColor: #ffffff); }` (inline MaskTexturePath UNVERIFIED) |
| popup title | `@PopupTitleStyle = LabelStyle(FontSize: 38, LetterSpacing: 2, RenderUppercase: true, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center);` (595-602) | large modal titles | copy literally |
| `@TitleLabel` | `Label { Style: (FontSize: 40, Alignment: Center); }` (27-29) | legacy | - |

### 3.3 Text styles

| Meaning | V (verbatim, path) | Inline `Style: (...)` |
|---|---|---|
| default body label | `@DefaultLabelStyle = (FontSize: 16, TextColor: #96a9be);` (`Common.ui` 31) | `(FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center)` |
| wrapped message | `Style: (...$C.@DefaultLabelStyle, HorizontalAlignment: Center, Wrap: true, FontSize: 16);` (`Pages/PrefabEditorExitConfirm.ui`) | `(FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, Wrap: true)` |
| bold field label | `Style: (...$C.@DefaultLabelStyle, RenderBold: true);` (`Pages/Teleporter.ui`) | `(FontSize: 16, TextColor: #96a9be, RenderBold: true)` |
| form caption (uppercase) | `Style: (RenderBold: true, RenderUppercase: true, TextColor: #94a7bb);` (`Pages/NameRespawnPointPage.ui`) | `(RenderBold: true, RenderUppercase: true, TextColor: #94a7bb)` |
| gray caption / description | `@ColorGrayCaption = #878e9c;` used `Style: (FontSize: 12, TextColor: $C.@ColorGrayCaption, ...)` / 13 (`Pages/UIGallery/*`) | `(FontSize: 13, TextColor: #878e9c)` |
| light caption / footnote | `@ColorCaptionLight = #5a6a7a;` used at `FontSize: 11` (`UIGallery/Categories/TextContent.ui`) | `(FontSize: 11, TextColor: #5a6a7a)` |
| small note under a heading | `Style: (...$C.@DefaultLabelStyle, FontSize: 12, TextColor: #96a9be);` (`PrefabEditorExitConfirm.ui`) | `(FontSize: 12, TextColor: #96a9be)` |
| row name | `Style: (FontSize: 14, RenderBold: true, TextColor: #d6e4ee, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);` (`WorldEventListRow.ui`) | same |
| row sub-line | `Style: (FontSize: 12, TextColor: #7f93a6, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);` | same |
| row badge (right) | `Style: (FontSize: 12, TextColor: #9aacbc, HorizontalAlignment: End, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 2);` | same |
| muted value | `Style: (TextColor: #ffffff(0.6));` (`ItemRepairElement.ui` durability) | `(TextColor: #ffffff(0.6))` |
| very muted italic | `Style: (TextColor: #ffffff(0.2), RenderItalics: true);` (`WarpEntryButton.ui`) | same |
| disabled | `@ColorDisabled = #797b7c;` (`Common.ui` 13) | `(TextColor: #797b7c)` |
| gold highlight / cost | `@ColorGoldHighlight = #E8A93B;` (9) | `(TextColor: #E8A93B, RenderBold: true)` |
| warning / confirm question | `Style: (...$C.@DefaultLabelStyle, HorizontalAlignment: Center, FontSize: 32, TextColor: #ffcc00);` (`PrefabEditorExitConfirm.ui` #WarningTitle) | `(FontSize: 32, TextColor: #ffcc00, HorizontalAlignment: Center)` |
| error | `Style: (...$C.@DefaultLabelStyle, TextColor: #ff6b6b);` (`PrefabSavePage.ui`; also AssetPackSaveBrowser, PrefabEditorSettings); form error `Style: (RenderBold: true, TextColor: #bb3333);` (`NameRespawnPointPage.ui`) | `(FontSize: 16, TextColor: #ff6b6b)` |
| success / complete | `Style: (...@MemoryCounterStyle, TextColor: #39f493);` (`Pages/Memories/MemoriesCategory.ui`) | `(TextColor: #39f493, RenderBold: true)` |
| have enough (shop) | `TextColor: #3d913f` FontSize 13 (`BarterTradeRow.ui` #HaveNeedLabel) | same |
| out of stock | `Style: (FontSize: 14, TextColor: #cc4444, ..., RenderBold: true)` (`BarterTradeRow.ui`) | same |
| info / timer | `Style: (FontSize: 14, TextColor: #7caacc, ...)` (`BarterPage.ui` #RefreshTimer) | same |
| stat name / value (client) | `Style: (TextColor: #878e9c, FontSize: 11, RenderBold: false)` / `Style: (TextColor:  #b4c8c9, FontSize: 14, RenderBold: true)` (client `CharacterPanel.ui`) | same |
| client ingredient missing / met | `@InvalidColor = #D13B3B;` `@ValidColor = #48d185;` (client `BasicCraftingIngredient.ui`) | reference only (SkyyGear uses the custom-kit red / green) |

Engine defaults: a `Label` with no `TextColor` renders in the engine default (ItemRepair / Shop / Warp rows rely on it, bold names
are white-ish) - exact default not in any document (UNVERIFIED; always set a colour inline).

### 3.4 Fonts

| FontName | Used for | Evidence |
|---|---|---|
| `"Default"` (or omitted) | all body text, buttons, inputs | 12 explicit uses; `@HeaderTextButtonLabelStyle` switches back to it (`FontName: "Default"`) |
| `"Secondary"` | window titles (`@TitleStyle`), memory tiles, key-binding hints, pause-menu buttons (25), event titles (26), respawn title (38), settings title (40), stat numbers | 46 uses |

Shipped font files (client `Shared/UI/Fonts/`): NunitoSans Regular / Medium / SemiBold / ExtraBold, Lexend-Bold, NotoMono-Regular,
NotoSans-Bold + CJK. Mapping inferred (not proven in a document): Default = Nunito Sans (bold = ExtraBold), Secondary = Lexend Bold.
Font sizes in vanilla game docs (count): 12 (83), 13 (104), 14 (118), 15 (66), 16 (42), 18 (50); titles 15; headings 20-40.
Other label keys used: `RenderBold`, `RenderUppercase`, `RenderItalics`, `LetterSpacing` (0-2), `OutlineColor`, `Wrap`,
`WrapMaxLines`, `ShrinkTextToFit` + `MinShrinkTextToFitFontSize`, `HorizontalAlignment` / `VerticalAlignment` (Start / Center / End),
`Alignment: Center`, `MaskTexturePath` / `LabelMaskTexturePath` (gradient text).

### 3.5 Buttons

Shared values (`Common.ui` 38-43): `@ButtonBorder = 12;` `@PrimaryButtonHeight = 44;` `@SmallButtonHeight = 32;`
`@BigButtonHeight = 48;` `@ButtonPadding = 24;` `@DefaultButtonMinWidth = 172;`. Button textures are 220 x 44 logical
(`Buttons/*@2x.png` 440 x 88); Primary uses `HorizontalBorder: 80`, so a Primary button narrower than ~160 px squashes its ends -
keep it >= 172.

Label styles (`Common.ui` 65-113):
```
@DefaultButtonLabelStyle = LabelStyle(
  FontSize: 17,
  TextColor: @ColorButtonText,
  RenderBold: true,
  RenderUppercase: true,
  HorizontalAlignment: Center,
  ShrinkTextToFit: true,
  MinShrinkTextToFitFontSize: 12,
  VerticalAlignment: Center
);
```
`@ColorButtonText = #bfcdd5;` Secondary / Tertiary label = the same with `TextColor: #bdcbd3`; Small = `FontSize: 14`;
Disabled = `TextColor: @ColorDisabled` (#797b7c).

| Kind | Vanilla style (Common.ui) | Textures (Default / Hovered / Pressed / Disabled) | Patch | Label | Height / padding | Sounds | Vanilla use |
|---|---|---|---|---|---|---|---|
| Primary | `@TextButton` / `@DefaultTextButtonStyle` (123-129) | `Common/Buttons/Primary.png`, `Primary_Hovered`, `Primary_Pressed`, `Disabled` | `VerticalBorder: 12, HorizontalBorder: 80` | 17 `#bfcdd5` | 44, Horizontal 24 | `@ButtonsLight` (confirm pages override with `@SaveSettings`) | main action: Save, Confirm, Craft, Respawn, Spawn |
| Secondary | `@SecondaryTextButton` (163-168, 288-301) | `Buttons/Secondary*.png`, `Disabled.png` | `Border: 12` | 17 `#bdcbd3` | 44, 24 | `@ButtonsLight`; Cancel buttons use `@ButtonsCancel` | Cancel, Browse, Clear, Reset |
| Small secondary | `@SmallSecondaryTextButton` (178-183, 257-271) | Secondary* | `Border: 12` | 14 `#bdcbd3` | 32, Horizontal 16 | `@ButtonsLight` | list row actions (WorldEvent 92 x 42), Craft x10 / Craft all |
| Tertiary | `@TertiaryTextButton` (185-190, 317-330) | `Buttons/Tertiary*.png`; selected = `Tertiary_Active.png` (`@TertiaryActiveButtonBackground`, 63) | `Border: 12` | 17 `#bdcbd3` | 44, 24 | `@ButtonsLight` | quiet actions, toggles, "Show code" |
| Small tertiary | `@SmallTertiaryTextButton` (192-197, 273-286) | Tertiary* | `Border: 12` | 14 `#bdcbd3` | 32, 16 | `@ButtonsLight` | gallery "Show code"; Skyy tabs / ON-OFF |
| Destructive | `@CancelTextButton` / `@CancelTextButtonStyle` (139-145, 228-241) | `Buttons/Destructive*.png`, `Disabled.png` | `Border: 12` | 17 `#bfcdd5` (Primary label) | 44, 24 | `@ButtonsCancel` | Delete, Quit to desktop (client `ConfirmQuitOverlay`) |
| Square / icon | `@Button` (`@DefaultButtonStyle`, 115-121, 214-226), `@SecondaryButton`, `@TertiaryButton`, `@CancelButton` | `Buttons/Primary_Square*.png` (Border 12) / Secondary / Tertiary / Destructive | `Border: 12` | icon child 32 x 32 | 44 x 44 | `@ButtonsLight` | icon buttons (gallery), quantity popup confirm / cancel (31 high) |
| Small (broken) | `@SmallDefaultTextButtonStyle` (131-137) | `Common/ButtonSmall*.png` - **missing in Assets.zip** | - | - | - | - | do not use |
| Header text button | `@HeaderTextButtonStyle` (745-756) | none (text only) | - | `...@TitleStyle, TextColor: #d3d6db, FontName: "Default", RenderBold: true, LetterSpacing: 1`; hover `#eaebee`, pressed `#b6bbc2` | Padding `(Right: 22, Left: 15, Bottom: 1)` | client adds Tick | text buttons in a title bar |
| Plain list button | `Pages/BasicTextButton.ui` | Hovered `Background: #000000(0.2)`; Selected `LabelStyle: (RenderBold: true)`; Active `Background: #7a9cc6(0.25)` / hover `#7a9cc6(0.35)` | - | default | Padding `(Full: 6)` | none | file / plugin / command lists |
| Pause-menu button (client) | `@ButtonStyle` in `InGame/Overlays/MenuOverlay.ui` | label mask gradients (client-only) | - | 25 bold uppercase Secondary `#ffffff`, pressed `#bbb9b9` | 45 | `@ButtonsLight` | reference only |

Inline form (one button; swap the texture family / label colour / size per kind):
```
TextButton #SkyyXOk { Anchor: (Width: 220, Height: 44); Padding: (Horizontal: 24); Text: "Confirm"; Style: TextButtonStyle(Default: (Background: (TexturePath: "Common/Buttons/Primary.png", VerticalBorder: 12, HorizontalBorder: 80), LabelStyle: (FontSize: 17, TextColor: #bfcdd5, RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12)), Hovered: (Background: (TexturePath: "Common/Buttons/Primary_Hovered.png", VerticalBorder: 12, HorizontalBorder: 80), LabelStyle: (...same...)), Pressed: (Background: (TexturePath: "Common/Buttons/Primary_Pressed.png", VerticalBorder: 12, HorizontalBorder: 80), LabelStyle: (...same...)), Disabled: (Background: (TexturePath: "Common/Buttons/Disabled.png", VerticalBorder: 12, HorizontalBorder: 80), LabelStyle: (...same..., TextColor: #797b7c)), Sounds: (Activate: (SoundPath: "Sounds/ButtonsLightActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))); }
```
(`(...same...)` = repeat the full LabelStyle - inline has no spread operator.) Secondary / Tertiary / Destructive: `Border: 12`
instead of the Vertical/Horizontal pair, label `#bdcbd3` (Destructive keeps `#bfcdd5`), Destructive sounds =
`Activate: (SoundPath: "Sounds/ButtonsCancelActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6)`.
Disable a button the vanilla way: `Disabled: true;` in the markup or `b.set("#SkyyXOk.Disabled", true)` (vanilla gallery and client
`BenchInfoPanel.ui` `#TierUpgradeButtonMax { ... Disabled: true; }`; inline UNVERIFIED) - the style's Disabled state then shows and
clicks stop.
Selected tab / toggle look (Skyy practice, vanilla texture): Default and Hovered = `Common/Buttons/Tertiary_Active.png`.

Button spacing in vanilla dialogs: buttons centred in `LayoutMode: Center` rows with `Anchor: (Right: 6)` / `(Left: 6)` (confirm
page), `(Right: 4)` / `(Left: 4)` with `FlexWeight: 1` (name / save dialogs), vertical gap 10-20 (quit confirm); action rows
`@ActionButtonSeparator` = 35 wide, `@VerticalActionButtonSeparator` = 20 high.

### 3.6 Text inputs

V (`Common.ui` 452-489):
```
@InputBoxBackground = PatchStyle(TexturePath: "Common/InputBox.png", Border: 16);
@InputBoxHoveredBackground = PatchStyle(TexturePath: "Common/InputBoxHovered.png", Border: 16);
@InputBoxPressedBackground = PatchStyle(TexturePath: "Common/InputBoxPressed.png", Border: 16);
@InputBoxSelectedBackground = PatchStyle(TexturePath: "Common/InputBoxSelected.png", Border: 16);

@DefaultInputFieldStyle = InputFieldStyle();
@DefaultInputFieldPlaceholderStyle = InputFieldStyle(TextColor: #6e7da1);

@TextField = TextField {
  @Anchor = ();

  Style: @DefaultInputFieldStyle;
  PlaceholderStyle: @DefaultInputFieldPlaceholderStyle;
  Background: @InputBoxBackground;
  Anchor: (...@Anchor, Height: 38);
  Padding: (Horizontal: 10);
};
```
`@NumberField` = same with `NumberField`; `@MultilineTextField` = same with `Padding: (Full: 10);` and `ScrollbarStyle`.
Where: every form (Teleporter number fields 60 wide with `Format: (MaxDecimalPlaces: 2, Step: 0.5)`, respawn name 44 high,
prefab save). Read-only "value box" = a Group with `Background: $C.@InputBoxBackground; Padding: (Horizontal: 10);` height 38
(`PrefabSavePage.ui` #SelectedPackBox).
Inline (Skyy-proven wrapper pattern - the background on a Group, the field fills it):
```
Group #SkyyXBox0 { Anchor: (Width: 300, Height: 38); Background: (TexturePath: "Common/InputBox.png", Border: 16); TextField #SkyyXIn0 { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 40; PlaceholderText: "Search"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); } }
```
Search box (`@HeaderSearch`, 723-743): `CompactTextField` 30 high, `CollapsedWidth: 34; ExpandedWidth: 200;`,
`PlaceholderStyle: (TextColor: #3d5a85, RenderUppercase: true, FontSize: 14);`, `Padding: (Horizontal: 12, Left: 34);`,
icon `"Common/SearchIcon.png"` 16 x 16 offset 9, clear icon `"Common/ClearInputIcon.png"` `Color: #ffffff(0.3)` (hover 0.5, pressed 0.4).
Client quantity popup number field: `Style: (RenderBold: true, TextColor: #95a9bd, FontSize: 14); PlaceholderStyle: (RenderBold: true, TextColor: #526579, FontSize: 14);`.

### 3.7 Checkbox, toggle rows, slider, dropdown, colour picker

- **CheckBox** (`Common.ui` 407-428):
  ```
  @CheckBox = CheckBox {
    Anchor: (Width: 22, Height: 22);
    Background: (TexturePath: "Common/CheckBoxFrame.png", Border: 7);
    Padding: (Full: 4);
    Style: @DefaultCheckBoxStyle;
  };
  ```
  `@DefaultCheckBoxStyle`: Unchecked backgrounds `(Color: #00000000)` (disabled `#424242`), `ChangedSound: (SoundPath: $Sounds.@Untick, Volume: 6)`;
  Checked backgrounds `(TexturePath: "Common/Checkmark.png")`, `ChangedSound: (SoundPath: $Sounds.@Tick, Volume: 6)`.
  `@CheckBoxWithLabel` = LayoutMode Left, checkbox + label `Anchor: (Right: 30, Left: 11)` in `@DefaultLabelStyle`.
  Where: prefab save options, Teleporter "relative". Inline (UNVERIFIED element; Skyy pages use ON / OFF Tertiary buttons today):
  `CheckBox #SkyyXChk { Anchor: (Width: 22, Height: 22); Background: (TexturePath: "Common/CheckBoxFrame.png", Border: 7); Padding: (Full: 4); Value: true; Style: (Unchecked: (DefaultBackground: (Color: #00000000), HoveredBackground: (Color: #00000000), PressedBackground: (Color: #00000000), DisabledBackground: (Color: #424242), ChangedSound: (SoundPath: "Sounds/UntickActivate.ogg", Volume: 6)), Checked: (DefaultBackground: (TexturePath: "Common/Checkmark.png"), HoveredBackground: (TexturePath: "Common/Checkmark.png"), PressedBackground: (TexturePath: "Common/Checkmark.png"), ChangedSound: (SoundPath: "Sounds/TickActivate.ogg", Volume: 6))); }`
  A value change needs a `ValueChanged` event binding (not Activating) - check the binding type before use.
- **Settings toggle row** (client `Common/Settings/LabeledCheckBoxSetting.ui`): row `Anchor: (Height: 44, Bottom: 8); Background: (TexturePath: "../OptionBackgroundPatch.png", Border: 16);`
  label `Anchor: (Left: 16)`, `Style: (VerticalAlignment: Center, TextColor: #96a9be, RenderUppercase: false, FontSize: 18)`; the ON / OFF
  control is 330 wide, ON label `#96a9be` bold 18 uppercase, OFF label `#495972` not bold, sounds Tick / Untick. Its `CheckBox.png`
  textures are client-only; `OptionBackgroundPatch` IS in Assets.zip, so the row itself is reproducible:
  `Group #SkyyXOpt0 { Anchor: (Height: 44, Bottom: 8); Background: (TexturePath: "Common/OptionBackgroundPatch.png", Border: 16); LayoutMode: Left; Label { Anchor: (Left: 16, Width: 420); Text: ""; Style: (VerticalAlignment: Center, TextColor: #96a9be, FontSize: 18); } }`
  with two Small Tertiary ON / OFF buttons (selected = Tertiary_Active, labels as above) at the right end.
- **Slider** (`Common.ui` 883-915): `Background: (TexturePath: "Common/SliderBackground.png", Border: 2), Handle: "Common/SliderHandle.png", HandleWidth: 16, HandleHeight: 16, Sounds: (MouseHover: (SoundPath: $Sounds.@ButtonsLightHover, Volume: 6))`,
  `@DefaultSliderAnchor = (Height: 5);`. `SliderNumberField` pairs it with a number field (settings rows 270 wide). Client adds
  `Activate: $Sounds.@SliderRelease` (UntickActivate.ogg vol 9).
- **DropdownBox** (`Common.ui` 491-540): 330 x 32; backgrounds `Common/Dropdown.png` / `DropdownHovered.png` / `DropdownPressed.png` Border 16;
  arrows `Common/DropdownCaret.png` / `DropdownPressedCaret.png` 13 x 18; label `LabelStyle(TextColor: #96a9be, RenderUppercase: true, VerticalAlignment: Center, FontSize: 13)`,
  entries `#b7cedd`, empty `#b7cedd(0.5)`, selected entry bold; panel `Common/DropdownBox.png` Border 16, padding 6, `EntryHeight: 31`,
  `EntriesInViewport: 10`, hovered entry `(Color: #0a0f17)`, pressed `(Color: #0f1621)`, `FocusOutlineColor: #ffffff(0.4)`; sounds
  `@DropdownBox` (Tick / hover / ButtonsCancelActivate close), entries `@ButtonsLight`. Settings variant: label 16 bold, HorizontalPadding 12.
  Entries: `DropdownEntry { Value: "..."; Text: "..."; }` children or `UICommandBuilder.set(... List<DropdownEntryInfo>)`.
- **Colour picker**: `ColorPickerDropdownBox` 32 x 32 with `@DefaultColorPickerDropdownBoxStyle` (`Common.ui` 347-369) - not needed by Skyy pages.

### 3.8 Tabs

| Kind | V | Where | Inline |
|---|---|---|---|
| Tertiary button tabs (Skyy practice) | `@SmallTertiaryTextButtonStyle` + `@TertiaryActiveButtonBackground` | vanilla uses Tertiary for quiet buttons; EntitySpawnPage switches its tab `TextButton`s between `Value.ref("Common.ui", "DefaultTextButtonStyle")` (active) and `SecondaryTextButtonStyle` (inactive) | vanilla-exact alternative: active tab = Primary style, inactive = Secondary style (what EntitySpawnPage does) |
| icon top tabs `@TopTabsStyle` | `TabStyleState(Background: "Common/Tab.png", Overlay: "Common/TabOverlay.png", IconAnchor: (Width: 44, Height: 44), Anchor: (Width: 82, Height: 62, Right: 5, Bottom: -14))`; hovered Bottom -5, pressed -8, selected Bottom 4 + `"Common/TabSelectedOverlay.png"` (`Common.ui` 668-689) | crafting bench categories, gallery | `TabNavigation` element inline (UNVERIFIED); needs `TabButton { Icon: "..."; Id: "..."; }` children |
| header icon tabs `@HeaderTabsStyle` | `Anchor: (Width: 37, Height: 30, Left: 4), IconAnchor: (Width: 22, Height: 22), IconOpacity: 0.4` (hover 0.6, pressed 0.8, selected 1 + `"Common/HeaderTabSelectedBackground.png"` Border 7 + mask `"Common/SelectedIconGradient.png"`) (691-711) | list / grid switch in a title bar, inventory filters | same (UNVERIFIED) |
| client text top tabs | `LabelStyle: (FontSize: 19)`, selected `(FontSize: 19, TextColor: #f0de7bff, RenderBold: true)`, `Background: (TexturePath: "Tab.png", Border: 3)`, Padding `(Left: 20, Right: 20, Top: 14)` (client `Common/Container.ui` 55-97) | client text tabs | gold selected-tab colour `#f0de7b` is reusable |
| settings navigation (client) | `LabelStyle(TextColor: #4d5865, FontSize: 21, ..., RenderUppercase: true, RenderBold: true)`; hover `#7b8998`, pressed `#a5b4c4`, selected `#ffffff` + TextGradient mask; 2 px lines `#a9bed8(0.15)` above / below a 44 px bar (client `Common/Settings/Settings.ui`) | settings menu top bar | text-only TextButtons with these label colours |
| gallery category list | `LabelStyle: (FontSize: 14, TextColor: $C.@ColorDefaultLabel, RenderUppercase: true, ...)`, hover label `@ColorButtonText` + `Background: $C.@ColorSimpleButtonBackground` (#000000(0.2)); selected white bold + TextGradient; 32 high, bottom 4, padding horizontal 10 (`UIGallery/CategoryButton.ui`) | left-side category menus | `TextButton #SkyyXCat0 { Anchor: (Height: 32, Bottom: 4); Padding: (Horizontal: 10); Text: ""; Style: TextButtonStyle(Default: (LabelStyle: (FontSize: 14, TextColor: #96a9be, RenderUppercase: true, VerticalAlignment: Center)), Hovered: (LabelStyle: (FontSize: 14, TextColor: #bfcdd5, RenderUppercase: true, VerticalAlignment: Center), Background: #000000(0.2))); }` |

Tab sounds: custom kit has no tab sound set; client uses `DefaultTabActivate.ogg` (not in Assets.zip) -> use `@ButtonsLight`.

### 3.9 Lists and rows

| Row | V (verbatim, path) | Size | Where | Inline |
|---|---|---|---|---|
| panel row (normal / selected / static) | `@NormalRowStyle = (Default: (Background: (Color: #101925(0.55))), Hovered: (Background: (Color: #132033(0.8))), Pressed: (Background: (Color: #182a40(0.9))), Sounds: $Sounds.@ButtonsLight);` `@SelectedRowStyle` all `#4274a5`; `@StaticRowStyle` all `#101925(0.55)`; status bar `Anchor: (Width: 4, Right: 8); Background: (Color: #4274a5);` (`Pages/WorldEvent/WorldEventListRow.ui`) | 42 high + 3 gap, padding L/R 8, actions 92 x 42 | world event list | `Button #SkyyXRow0 { Anchor: (Height: 42, Bottom: 3); LayoutMode: Left; Padding: (Left: 8, Right: 8); Style: ButtonStyle(Default: (Background: #101925(0.55)), Hovered: (Background: #132033(0.8)), Pressed: (Background: #182a40(0.9)), Sounds: (...ButtonsLight...)); Group { Anchor: (Width: 4, Right: 8); Background: #4274a5; } }` |
| hover-only list row | `Button #Button { LayoutMode: Left; Padding: (Full: 6); Style: (Hovered: (Background: #000000(0.2),)); ItemIcon #Icon { Anchor: (Width: 32, Height: 32); } ...` 2 px underline `#ffffff(0.6)` (`Pages/ItemRepairElement.ui`); same pattern in `ShopElementButton.ui` (64 x 64 icon), `WarpEntryButton.ui` | icon 32 / 64, padding 6 | repair, shop, warp lists | `Button #SkyyXRow0 { LayoutMode: Left; Padding: (Full: 6); Style: ButtonStyle(Hovered: (Background: #000000(0.2))); ItemIcon #SkyyXRowIco0 { Anchor: (Width: 32, Height: 32); ItemId: "..."; } Label #SkyyXRowName0 { Padding: (Horizontal: 10, Vertical: 5); FlexWeight: 1; Text: ""; Style: (RenderBold: true); } }` |
| option row (selectable card) | `@DefaultRespawnButtonStyle = ButtonStyle(Default: (Background: (TexturePath: "../Common/OptionBackgroundPatch.png", Border: 16)), Hovered: (... Color: #ffffff(0.7))), Pressed: (... Color: #ffffff(0.85))), ...)`; `@SelectedRespawnButtonStyle = ButtonStyle(Default: (Background: (TexturePath: "../Common/InputBoxSelected.png", Border: 16)));` name `(RenderBold: true, VerticalAlignment: Center, TextColor: #90a2b7)` padding left 14, detail `(... TextColor: #8698ad, FontSize: 14)` (`Pages/OverrideRespawnPointButton.ui`) | 50 high + 4 gap | respawn point picker | `Button #SkyyXOpt0 { Anchor: (Height: 50, Bottom: 4); LayoutMode: Left; Style: ButtonStyle(Default: (Background: (TexturePath: "Common/OptionBackgroundPatch.png", Border: 16)), Hovered: (Background: (TexturePath: "Common/OptionBackgroundPatch.png", Border: 16, Color: #ffffff(0.7))), Pressed: (Background: (TexturePath: "Common/OptionBackgroundPatch.png", Border: 16, Color: #ffffff(0.85))), Sounds: (...ButtonsLight...)); }`; selected: `Default: (Background: (TexturePath: "Common/InputBoxSelected.png", Border: 16))` |
| label list button | `TextButton #Button { Padding: (Full: 6); Style: @LabelStyle; }` hover `#000000(0.2)`, selected bold, active `#7a9cc6(0.25)` (`Pages/BasicTextButton.ui`, `Common/TextButton.ui`) | padding 6 | file / command / plugin lists | see 3.5 "Plain list button" |
| trade card | card 230 x 185, button bg `#252f3a`, hover `#c9a050`, pressed `#a08040`, disabled `#1a1e24`, inner `#1c2835`, slot border `#1a2530` (output) / `#2a5a3a` (have), divider 140 x 1 `#252F3A`, grid `LayoutMode: LeftCenterWrap` (`Pages/BarterTradeRow.ui`, `BarterPage.ui`) | 230 x 185 | NPC barter shop | the vanilla shop look for AH / Bazaar cards |
| settings row | 44 high + 8 gap, `OptionBackgroundPatch` Border 16, label 18 `#96a9be` (client settings) | 44 | settings menu | see 3.7 |

Scrolling list container (every vanilla list page): `Group #ElementList { FlexWeight: 1; LayoutMode: TopScrolling; ScrollbarStyle: $C.@DefaultScrollbarStyle; }`.
Column header above a list: `Label { FlexWeight: 1; Text: ...; Style: (RenderBold: true); }` in a `LayoutMode: Left` group with
`Padding: (Right: 15, Bottom: 5)` (`ItemRepairPage.ui`).

### 3.10 Scrollbars

V (`Common.ui` 381-405):
```
@DefaultScrollbarStyle = ScrollbarStyle(
  Spacing: 6,
  Size: 6,
  Background: (TexturePath: "Common/Scrollbar.png", Border: 3),
  Handle: (TexturePath: "Common/ScrollbarHandle.png", Border: 3),
  HoveredHandle: (TexturePath: "Common/ScrollbarHandleHovered.png", Border: 3),
  DraggedHandle: (TexturePath: "Common/ScrollbarHandleDragged.png", Border: 3)
);
```
`@DefaultExtraSpacingScrollbarStyle` = Spacing 12; `@TranslucentScrollbarStyle` = Spacing 6, Size 6, `OnlyVisibleWhenHovered: true`,
handle only; `@DefaultPlaceholderScrollbarStyle` = Spacing 12, Size 10 (no textures).
Inline (SkyyGear `GearUi.scroll()` uses exactly this): `LayoutMode: TopScrolling; ScrollbarStyle: (Spacing: 6, Size: 6, Background: (TexturePath: "Common/Scrollbar.png", Border: 3), Handle: (TexturePath: "Common/ScrollbarHandle.png", Border: 3), HoveredHandle: (TexturePath: "Common/ScrollbarHandleHovered.png", Border: 3), DraggedHandle: (TexturePath: "Common/ScrollbarHandleDragged.png", Border: 3));`

### 3.11 Separators and dividers

| Kind | V (verbatim, path) | Inline |
|---|---|---|
| content separator | `@ContentSeparator = Group { ... Anchor: (...@Anchor, Height: 1); Background: (Color: #2b3542); };` (`Common.ui` 604-609) | `Group { Anchor: (Height: 1); Background: #2b3542; }` |
| fancy separator | `@PanelSeparatorFancy`: Left layout, height 8: `"Common/ContainerPanelSeparatorFancyLine.png"` (FlexWeight 1) + `"Common/ContainerPanelSeparatorFancyDecoration.png"` (11 wide) + line (786-806) | `Group { Anchor: (Height: 8); LayoutMode: Left; Group { FlexWeight: 1; Background: "Common/ContainerPanelSeparatorFancyLine.png"; } Group { Anchor: (Width: 11); Background: "Common/ContainerPanelSeparatorFancyDecoration.png"; } Group { FlexWeight: 1; Background: "Common/ContainerPanelSeparatorFancyLine.png"; } }` |
| vertical separator | `@VerticalSeparator = Group { Background: (TexturePath: "Common/ContainerVerticalSeparator.png"); Anchor: (Width: 6, Top: -2); };` (781-784) | `Group { Anchor: (Width: 6); Background: (TexturePath: "Common/ContainerVerticalSeparator.png"); }` |
| title-bar separator | `@HeaderSeparator = Group { Anchor: (Width: 5, Height: 34); Background: "Common/HeaderTabSeparator.png"; };` (758-761) | same |
| footer divider | `Group #FooterDivider { Anchor: (Height: 2); Background: #19252F; }` (`BarterPage.ui`) | same |
| panel title line | `#393426(0.5)` 1 px (custom) / `#1b2533` (client) | see 3.2 |
| list divider | `Anchor: (Height: 2, Vertical: 6); Background: #292b2a;` (`SelectOverrideRespawnPointPage.ui`); `Anchor: (Vertical: 16, Height: 1); Background: #5e512c;` (`Teleporter.ui`) | same |
| tooltip separator (client) | `Anchor: (Top: 0, Height: 1); Background: (Color: #25262c);` (`InGame/Tooltips/ItemTooltip.ui`) | same |
| HUD legend separator | `Anchor: (Height: 2, Vertical: 10); Background: #ffffff(0.15);` (`Hud/ToolsLegends/ToolsLegendsCommon.ui`) | same |
| stats separator (client) | `Anchor: (Height: 2); Background: #c1c9d3(0.07);` (`CharacterPanel.ui`) | same |

### 3.12 Item slots, grids and rarity frames

- **Client inventory grid** (client `InGame/Common.ui`): `@DefaultItemSlotsPerRow = 9; @DefaultItemSlotSpacing = 2; @DefaultItemSlotSize = 74; @DefaultItemGridPadding = 2;`
  `@DefaultItemGridStyle = ItemGridStyle(SlotSpacing: ..., SlotSize: ..., SlotIconSize: 64, SlotBackground: "Pages/Inventory/Slot.png", ..., DurabilityBarAnchor: (Bottom: 10, Left: 13, Width: 48, Height: 2), DurabilityBarColorStart: #a63232, DurabilityBarColorEnd: #63b649, ..., ItemStackHoveredSound: (SoundPath: $Sounds.@ButtonsLightHover, Volume: 6));`
  crafting list 72 / spacing 4 (activate sound ButtonsLightActivate vol 4 pitch +-0.2); bench 64 / 4; furnace fuel 64 / 0 icon 58.
  `Slot.png` is client-only (UNVERIFIED inline).
- **Custom-kit slot background**: `SlotBackground: "../Common/BlockSelectorSlotBackground.png"` (`Pages/EntitySpawnPage.ui`; 46 x 46
  logical). Inline ItemGrid style: `Style: (SlotSize: 74, SlotIconSize: 64, SlotSpacing: 2, SlotBackground: "Common/BlockSelectorSlotBackground.png");`
  (inline SlotBackground UNVERIFIED; Skyy grids set none today). Keep the ItemGridSlot rule: only `new ItemStack(id, qty)`.
- **Item with rarity frame** (vanilla, no ItemStack):
  ```
  ItemSlot #OutputSlot {
    Anchor: (Full: 0);
    ShowQualityBackground: true;
  }
  ```
  inside a 68 x 68 border group `Background: #1a2530; Padding: 2;` (`Pages/BarterTradeRow.ui`; `DroppedItemSlot.ui` adds
  `ShowQuantity: false;` and a quantity label `FontSize: 16, TextColor: #e2d8d8, ... RenderBold: true`). Server sets
  `#OutputSlot.ItemId` (BarterPage bytecode). Inline: `Group #SkyyXSlotB0 { Anchor: (Width: 68, Height: 68); Background: #1a2530; Padding: (Full: 2); ItemSlot #SkyyXSlot0 { Anchor: (Full: 0); ShowQualityBackground: true; ShowQuantity: false; } }`
  then `b.set("#SkyyXSlot0.ItemId", "Weapon_Sword_Iron")` (inline UNVERIFIED; recommended probe).
- **Plain icon**: `ItemIcon #Icon { Anchor: (Width: 32, Height: 32); }` + `#Icon.ItemId` (ItemRepairElement; Skyy pages already use
  `ItemIcon { ItemId: "..."; }` inline - proven).
- **Rarity data** (`Server/Item/Qualities/*.json`): slot frame `UI/ItemQualities/Slots/Slot<Q>.png`, tooltip frame
  `UI/ItemQualities/Tooltips/ItemTooltip<Q>.png` + `...Arrow.png`, TextColor: Junk `#c9d2dd` (label hidden), Common `#c9d2dd`,
  Uncommon `#3e9049`, Rare `#2770b7`, Epic `#8b339e`, Legendary `#bb8a2c`, Technical `#3b7a8f`, Tool `#269edc`, Developer `#bb2f2c`,
  Debug / Template `#ce1624`.

### 3.13 Tooltips

- **Text tooltip (custom kit)** - V (`Common.ui` 924-929):
  ```
  @DefaultTextTooltipStyle = TextTooltipStyle(
    Background: (TexturePath: "Common/TooltipDefaultBackground.png", Border: 24),
    MaxWidth: 400,
    LabelStyle: (Wrap: true, FontSize: 16),
    Padding: 24
  );
  ```
  Use on any element: `TooltipText: "..."; TextTooltipStyle: $C.@DefaultTextTooltipStyle;` (`UIGallery/Categories/TooltipsContent.ui`).
  Inline: `TooltipText: "Sells for 20 coins"; TextTooltipStyle: (Background: (TexturePath: "Common/TooltipDefaultBackground.png", Border: 24), MaxWidth: 400, LabelStyle: (Wrap: true, FontSize: 16), Padding: 24);`
  (no Skyy page uses tooltips yet; the HANDOFF beta note "menu tooltip stuck after Esc" means: test Esc with a tooltip open).
  Client variants: `MaxWidth: 300, LabelStyle: (FontSize: 14, Wrap: true)` (crafting ingredient), `Alignment: TopLeft` (info buttons).
- **Item tooltip (client, reference for "tooltip-like" panels)** - `InGame/Tooltips/ItemTooltip.ui`: `@MinWidth = 320; @MaxWidth = 480; @TextureBorder = 24;`
  frame = quality tooltip texture Border 24, arrow 33 x 24 at Bottom -8, padding `(Full: 24, Top: 21)`, name `(RenderBold: true, FontSize: 18, Wrap: true)`
  (coloured by rarity), quality label `(HorizontalAlignment: End, FontSize: 14)`, id `(TextColor: #838383, FontSize: 14, RenderItalics: true)`,
  type `#838383` 14, description `(TextColor: #696969, FontSize: 14, Wrap: true)`, separator `#25262c`, stats `@PrimaryTextColor = #bca57a;`
  14 with 24 x 24 icons, durability `#bca57a` right-aligned, cursed `#a020f0`. The real hover tooltip is drawn by the client for
  ItemGrid / ItemSlot / ItemIcon items (it reads the item's rarity) - an inline page should rely on that, not rebuild it.
  Inline "tooltip-like" info panel: `Group #SkyyXTip { Anchor: (Width: 360); Background: (TexturePath: "Common/TooltipDefaultBackground.png", Border: 24); Padding: (Full: 24, Top: 21); LayoutMode: Top; }`.

### 3.14 Progress bars, spinner, timers

- `@ProgressBar` (`Common.ui` 949-959): `Anchor: (...@Anchor, Width: 284, Height: 6); Background: "Common/ProgressBar.png"; BarTexturePath: "Common/ProgressBarFill.png"; EffectTexturePath: "Common/ProgressBarEffect.png"; EffectWidth: 102; EffectHeight: 58; EffectOffset: 74;`
  Inline: `ProgressBar #SkyyXBar { Anchor: (Width: 284, Height: 6); Background: "Common/ProgressBar.png"; BarTexturePath: "Common/ProgressBarFill.png"; EffectTexturePath: "Common/ProgressBarEffect.png"; EffectWidth: 102; EffectHeight: 58; EffectOffset: 74; Value: 0.5; }`
  then `b.set("#SkyyXBar.Value", 0.75f)`. Caption under it `(FontSize: 11, TextColor: #5a6a7a)`. Client bench upgrade bar = 10 high,
  effect 53 x 30 offset 38; crafting bar 4 high.
- `@CircularProgressBar` (931-940): 48 x 48, `Background: #1a2030; Color: #aa7c4a; MaskTexturePath: "Common/CircularProgressBarMask.png";` (gallery colours `#4a7caa`, `#7caa4a`).
- `@DefaultSpinner` (611-617): `Sprite` 32 x 32 `TexturePath: "Common/Spinner.png"; Frame: (Width: 32, Height: 32, PerRow: 8, Count: 72); FramesPerSecond: 30;`.
- Client furnace bar (`ProcessingBar.ui`, client-only textures), HUD timer `TimerLabel` `Style: (FontSize: 32, Alignment: Center)` on `#000000(0.2)` (`Hud/TimeLeft.ui`).

### 3.15 Icons available in Assets.zip (custom root, inline path `"Common/<name>.png"`)

`SearchIcon`, `ClearInputIcon`, `Checkmark` (19 x 19), `IconCheckGreen` (48 px, non-2x), `IconCrossRed` (40 px, non-2x),
`RecipesIcon` (34 x 34), `UnknownItemIcon` (64), `WIPIcon`, `ContainerTitleArrow` (6 x 10, the arrow between title and category
in the client crafting header), `InputBinding` (key-cap patch, Border 6), `InputIconMouseLeftClick` / `MiddleClick` / `RightClick`,
`SmallInputIconMouse*`, `InputIconKeyUp/Down/Left/Right_White`, `BackButton` / `Hovered` / `Pressed`, `Spinner`, `IconMaskSettings`,
`BlockSelectorSlotDropIcon`, `ColorPicker*`. Custom page art: `Pages/Memories/Checkmark`, `Pages/Portals/IconBullet`, `Pages/RespawnPointArrow`.
Hover-dim convention for icon buttons: `Hovered: (Background: (TexturePath: "...", Color: #ffffff(0.8)))`, `Pressed: (... Color: #ffffff(0.6))`
(client crafting / bug report buttons); icon opacity 0.65 -> 1 on hover (`TriggerVolumeInspectorPage.ui`).
Key hint chip (HUD legends): `Background: (TexturePath: "Common/InputBinding.png", Border: 6)` + label `(RenderBold: true, RenderUppercase: true, FontName: "Secondary", FontSize: 14, TextColor: #ffffff(0.8), OutlineColor: #000000(0))`.

### 3.16 Spacing conventions and window sizes

| Value | Vanilla | Source |
|---|---|---|
| title bar | 38 high, label padding horizontal 19, bar padding top 7 | `@TitleHeight`, `@Title` |
| content padding | default 17 (`9 + 8`); pages mostly 16, dialogs 20, forms 24 | `@DecoratedContainer`, page overrides |
| inner padding | 8 (`@InnerPaddingValue`), full 17 (`@FullPaddingValue`) | `Common.ui` 808-809 |
| client panels | center 715, side 410, vertical spacing 8, horizontal 38, panel padding 14, panel title 24 | client `InGame/Common.ui` |
| button heights | 44 / 32 / 48; padding 24 / 16; min width 172 | `Common.ui` 38-43 |
| text field height | 38 (dialog name fields 44) | `@TextField`, NameRespawnPointPage |
| dropdown | 330 x 32 | `@DropdownBox` |
| list rows | 42 + 3 (panel rows), 50 + 4 (option rows), 44 + 8 (settings rows), padding 6 (hover rows) | 3.9 |
| section spacing | subtitle bottom 10; section label top 10 / bottom 4; gallery element row bottom 12, section group bottom 20-25 | gallery, WorldEvent |
| confirm dialog | 620 wide, padding 20, question 32 px bottom 12, message bottom 16, buttons 150-220 wide in a centred row | `PrefabEditorExitConfirm.ui` |
| small dialogs | 420 / 500 / 532 wide (height from content) | PrefabSave / NameRespawnPoint / Teleporter |
| list pages | 600 x 700 (Shop, Warps, Prefab list), 600 x 400 (Item repair), 740 x 480 (Barter) | page roots |
| big pages | 1000-1100 x 700-720 (Command list, Plugin list, UI Gallery), 1070 x 825 (Memories), 1200 x 660 (WorldEvent), 1240 x 768 (TriggerVolume inspector) | page roots |
| client inventory | 1611 wide total (715 + 2 x 410 + 2 x 38) | client `InGame/Common.ui` |

Fit rule: the biggest vanilla page is 825 high, so HANDOFF's "BIG readable, fits 1080" matches vanilla's own ceiling; SkyyRanks
(1120 x 860) and SkyyVault (1040 x 640) are within range. SkyyRanks scales vanilla font sizes up by 3-4 px for readability - keep
that as the one documented deviation, and never scale the 38 px title bar (fixed by its texture).

### 3.17 Colour constants (all docs), grouped by meaning

Named (custom `Common.ui` 4-19): `@ColorDefault = #ffffff;` `@ColorDefaultLabel = #96a9be;` `@ColorBlueAccent = #7a9cc6;`
`@ColorBlueAccentHovered = #96b8e0;` `@ColorBlueAccentPressed = #5a7a9c;` `@ColorGoldHighlight = #E8A93B;` `@ColorGrayCaption = #878e9c;`
`@ColorCaptionLight = #5a6a7a;` `@ColorButtonText = #bfcdd5;` `@ColorDisabled = #797b7c;` `@ColorPlaceholder = #3d5a85;`
`@ColorCodeText = #c9d1d9;` `@ColorBackgroundCode = #0d1117;` `@ColorSimpleButtonBackground = #000000(0.2);`

| Meaning | Colours (where) |
|---|---|
| main text | `#96a9be` default label (most used colour in the client: 52 uses), `#ffffff` highlights, `#d6e4ee` row names, `#b7cedd` dropdown entries / queue size, `#dee2ef` portal text |
| titles | `#b4c8c9` window titles / memory tiles / stat values, `#afc2c3` panel title (custom), `#cfd6e0` panel title (client), `#ccd3dd` bench tier, `#9aacbc` section labels, `#94a7bb` form captions, `#c5cdd9` event subtitle |
| buttons | `#bfcdd5` primary / destructive label, `#bdcbd3` secondary / tertiary label, `#d3d6db` header text button (hover `#eaebee`, pressed `#b6bbc2`), `#7c8b99` nav button (hover `#bbcedf`) |
| captions / muted | `#878e9c` gray caption, `#7f93a6` row sub, `#5a6a7a` light caption, `#7a8a9a` / `#8a9aaa` barter captions, `#90a2b7` / `#8698ad` option rows, `#ffffff(0.6)` durability, `#ffffff(0.2)` warp world, `#838383` / `#696969` tooltip id / description, `#9097a5` popup title |
| gold / highlight | `#E8A93B` gold highlight, `#f0de7b` selected tab / active search, `#ccb588` popup menu title, `#bca57a` tooltip stats, `#ca9f37` objective gold, `#c9a050` barter card hover (pressed `#a08040`), `#ffcc00` warning title |
| blue accent / selection | `#7a9cc6` accent (hover `#96b8e0`, pressed `#5a7a9c`), `#4274a5` selected row / status bar, `#7a9cc6(0.25)` active list item, `#7caacc` barter timer, `#4a7caa` progress |
| success | `#39f493` complete counter, `#48d185` ingredient met (client), `#3d913f` barter have, `#70c970` notification success, `#61df72`, `#63b649` durability full |
| error / danger | `#ff6b6b` error label, `#bb3333` form error, `#cc4444` out of stock, `#d13b3b` ingredient missing (client), `#e04242` clear-inventory warning, `#c2354c` settings warning (banner bg `#c2354c(0.15)`), `#eb3e3e` notification danger, `#d96a6a`, `#a63232` durability empty, `#4a1f1f` / `#5c2828` / `#3a1818` destructive icon button bg |
| warning | `#ffcc00` confirm question, `#e66431` notification warning |
| disabled / placeholder | `#797b7c` disabled, `#424242` disabled checkbox, `#6e7da1` input placeholder, `#3d5a85` search placeholder, `#495972` OFF label, `#526579` number placeholder |
| panel / row backgrounds | `#101925(0.55)` row, `#132033(0.8)` row hover, `#182a40(0.9)` row pressed, `#1c2835` / `#252f3a` card, `#1a2535` tooltip-demo group, `#1a2030` circular bar, `#0a0f17` / `#0f1621` dropdown entry hover / pressed, `#000000(0.2)` simple hover, `#000000(0.3)` info block, `#0d1117` code |
| overlays | `#000000(0.45)` custom page dim, `#000000(0.55)` inventory dim, `#000000(0.82)` client overlay, `#0e1219(0.90)` pause / quit, `#0e1219(0.95)` settings, `#0a0e12(0.75)` out-of-stock cover |
| lines | `#2b3542` content separator, `#19252f` barter footer, `#393426(0.5)` / `#1b2533` panel title lines, `#25262c` tooltip, `#a9bed8(0.15)` settings bars, `#a9bed8(0.25)` menu divider, `#292b2a`, `#5e512c`, `#ffffff(0.15)`, `#c1c9d3(0.07)` |
| rarity | see 3.12 |

Full per-file tallies were produced during research (151 distinct colours in the custom docs; 188 in the client in-game docs, editor / main menu / dev / builder tools excluded).

### 3.18 UI sounds (`Common/UI/Custom/Sounds.ui`; files in `Common/UI/Custom/Sounds/`, all 20 present)

| Sound set id | Activate | MouseHover | Vanilla use |
|---|---|---|---|
| `@ButtonsLight` | `ButtonsLightActivate.ogg` MinPitch -0.4 MaxPitch 0.4 Volume 4 | `ButtonsLightHover.ogg` Volume 6 | default for every button, row, dropdown entry, popup item |
| `@ButtonsCancel` | `ButtonsCancelActivate.ogg` -0.4 / 0.4 Volume 6 | ButtonsLightHover 6 | Cancel buttons, close X, destructive buttons |
| `@SaveSettings` | `SaveActivate.ogg` Volume 6 | ButtonsLightHover 6 | Save / Confirm / Save and exit |
| `@ButtonsMain` | `ButtonsMainActivate.ogg` Volume 6 | `ButtonsMainHover.ogg` -0.1 / 0.1 Volume 2 | main-menu big buttons |
| `@TopBar` | `TopBarActivate.ogg` Volume 6 | ButtonsMainHover Volume 2 | top navigation bar |
| `@DropdownBox` | `@Tick` (`TickActivate.ogg`) 6 | ButtonsLightHover 6 | dropdown open; Close = `ButtonsCancelActivate.ogg` 6 |
| `@Tick` / `@Untick` | `TickActivate.ogg` / `UntickActivate.ogg` (Volume 6 in the checkbox style) | - | checkbox on / off |
| `@Lock` / `@Unlock` | `LockActivate.ogg` / `UnlockActivate.ogg` Volume 6 | - | toggle buttons (client "hide unknown recipes") |
| `@Shuffle` | `ShuffleActivate.ogg` -0.4 / 0.4 Volume 1 | - | put-all / shuffle |
| `@EnterWorld`, `@ServerList` | `EnterWorldActivate.ogg` 6 | ButtonsLightHover 6 | world / server tiles |
| `@CosmeticsTiles` | `CosmeticsTilesActivate.ogg` -0.4 / 0.4 6 | ButtonsLightHover 6 | cosmetic tiles |
| `@ButtonMemoryRestore` | `MemoryRestoreButtonSting_Stereo.ogg` 4 | ButtonsMainHover -0.1 / 0.1 2 | memories restore |
| `@RespawnActivate` | `Respawn_Stereo.ogg` Volume -6 | - | death screen respawn |
| `@HButtonHover`, `@MemoriesButton`, `@MemoriesSting` | single files | - | misc |

Inline forms (Skyy-proven for the first two):
- light: `Sounds: (Activate: (SoundPath: "Sounds/ButtonsLightActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))`
- cancel: `Sounds: (Activate: (SoundPath: "Sounds/ButtonsCancelActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))`
- save: `Sounds: (Activate: (SoundPath: "Sounds/SaveActivate.ogg", Volume: 6), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))`
- small icon button (client `@ButtonsSmall`, files in Assets.zip): `Sounds: (Activate: (SoundPath: "Sounds/TickActivate.ogg", Volume: 6), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))`
- lock / unlock: `Sounds: (Activate: (SoundPath: "Sounds/LockActivate.ogg", Volume: 6))` / `UnlockActivate.ogg`

Page open / close: vanilla custom pages play no open sound (only the client inventory plays `InventoryOpen.ogg` -3 / `InventoryClose.ogg` +2,
client-only files). Server sound events exist for bench / chest pages (`Server/Audio/SoundEvents/SFX/UI/Interactions/Benches/SFX_Workbench_Open.json`,
`..._Close`, `Chests/SFX_Chest_Wooden_Open/Close`) - optional, played from Java, not markup.

### 3.19 HUD pieces reachable from the server

- Legend / info panel (`Hud/ToolsLegends/ToolsLegendsCommon.ui`): `Background: (TexturePath: "LegendContainerPanelPatch.png", Border: 4);` `Padding: (Full: 14);`
  300 wide at `Left: 20, Top: 110`; title `(Alignment: Center, FontSize: 16, RenderBold: true, RenderUppercase: true)`; row label
  `(FontSize: 14, TextColor: #96a9be, Wrap: true)`; section header `(FontSize: 15, TextColor: #ffffff(0.95))`; key chip see 3.15.
  Inline: `Background: (TexturePath: "Hud/ToolsLegends/LegendContainerPanelPatch.png", Border: 4);` (UNVERIFIED path).
- Timer chip (`Hud/TimeLeft.ui`): `Background: #000000(0.2); Padding: (Horizontal: 20, Vertical: 10);` label 32.
- Client HUD values for reference (not reproducible textures): notifications 48 high, message 15 bold / secondary 12, colours default
  `#a7afa7`, success `#70c970`, warning `#e66431`, danger `#eb3e3e`; event title primary 26 Secondary bold white with TextGradient,
  subtitle 12 uppercase bold `#c5cdd9` / `#b7cedd`; objective text 15 bold letter-spacing 1, gold `#ca9f37`, gray `#b7b8b9`; chat text
  `#f7f7f7` 15.

---

## 4. Coverage of the existing VANILLA_CHECK lists

| Project file | Checks | Covers |
|---|---|---|
| `SkyyRanks\build_skyyranks_0.1.1.py` | 55 values (Common 39, Sounds 6, WorldEventListRow 5, PrefabEditorExitConfirm 2, WorldEventSectionLabel 1, PrefabSavePage 1, MemoriesCategory 1) + 21 files | DecoratedContainer frame (header, decorations, patch, 38 px, content padding, title style + padding 19), default label, disabled, caption light, gold, button border / min width / text colours / label style, Primary / Secondary / Destructive / Tertiary (+Active) textures, ButtonsCancel on the cancel style, InputBox + placeholder + field padding, content separator, light / cancel sounds, WorldEvent row colours / name / sub / 92 x 42 action, section label, error red, success green, warning yellow, cancel sounds on confirm |
| `SkyyVault\build_skyyvault_0.1.3.py` (buy dialog only) | 32 values (Common 21, confirm page 8, Sounds 3) + 13 files | frame, title style, default label, 44 px buttons + padding 24, Primary / Secondary textures and labels, Save / Cancel / hover sounds, confirm page width 620 / padding 20 / #ffcc00 32 / wrapped message / centred button row / sound choices |
| `SkyyGear\build_skyygear_0.1.py` (`GearUi`, ReforgePage, IdentifyPage) | 6 named colours + 20 Common.ui needles + 3 Sounds needles + ItemRepairPage / ItemRepairElement checks + 2 colour docs + 19 textures + 3 sounds; quality JSON field set vs vanilla | frame (body padding 17), title, Primary / Secondary / Destructive / Disabled textures + labels with ShrinkTextToFit, scrollbar, vertical separator, row hover `#000000(0.2)` + muted `#ffffff(0.6)`, panel title colours, gray caption, gold, disabled, error / success, 2 cancel / light sounds, 7 rarity quality assets |

Missing from all three (candidates for the shared kit):
1. Disabled states: Ranks / Vault styles have no `Disabled:` entry; SkyyGear fakes disabled with a separate style. Add `Disabled.png` +
   `#797b7c` label to every TextButtonStyle and use `Disabled: true`.
2. Sounds: `@SaveSettings` only in Vault; `@Tick` / `@Untick` (checkbox, small icon buttons), `@Lock` / `@Unlock`, `@ButtonsMain`,
   dropdown sounds - none.
3. Controls never used inline yet: CheckBox (CheckBoxFrame + Checkmark), Slider, DropdownBox, CompactTextField search
   (`@HeaderSearch`), NumberField, MultilineTextField, TabNavigation (top / header tabs), ProgressBar, CircularProgressBar, Spinner.
4. Tooltips: `TooltipText` + `TextTooltipStyle` (TooltipDefaultBackground) - unused.
5. Item display: `ItemSlot` + `ShowQualityBackground` + `.ItemId`; ItemGrid `SlotBackground` (BlockSelectorSlotBackground); rarity
   slot / tooltip textures inline.
6. Containers: `@Container` (ContainerHeaderNoRunes, HorizontalBorder 35), `@SimpleContainer` (ContainerPanelPatch Border 4, padding 12),
   `@Panel` (ContainerFullPatch Border 20), ContainerBackgroundSecondary, the close X button, `@PanelSeparatorFancy`, `@HeaderSeparator`.
7. Rows: OptionBackgroundPatch option rows (+ InputBoxSelected selected), BasicTextButton list styles (active `#7a9cc6(0.25)`),
   settings rows, barter trade cards, gallery category buttons.
8. Text: `@SubtitleStyle`, `@PopupTitleStyle`, TextGradient mask headings, form caption `#94a7bb`, blue accents, gray caption usage
   sizes (12-13), client stat block (11 / 14).
9. HUD: legend panel patch + key chip.
10. The `Value.ref` route (none).
Discrepancies found: SkyyRanks body `Padding: (Full: 17, Top: 8)` vs vanilla pages' `(Full: 16)` / container default 17;
SkyyRanks button labels omit `ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12` (SkyyGear has them); SkyyRanks "Cancel" uses
Secondary + ButtonsCancel (correct, as PrefabEditorExitConfirm) - keep. SkyyVault's main page and every older Skyy page (dark
`#0b1524`, custom coloured buttons) still need the pass.

---

## 5. Recommended kit API (shared Python helper for server-built inline pages)

Constraints: mods are standalone (no cross-mod runtime dependency), Java runs through javassist (no varargs / lambdas / generics).
So the kit is a **build-time Python module** (proposed `tools/skyyui.py`) that returns literal markup strings and emits per-mod Java
helper methods (like SkyyGear's `GearUi`) into each mod's own class, plus one shared VANILLA_CHECK built from the same source table.

1. **Source table** - one dict `VANILLA = {name: (doc_key, exact_text_in_doc, inline_literal)}` covering every block in section 3;
   `vanilla_check(assets_zip)` verifies every `exact_text_in_doc` + every referenced texture (`@2x`) / sound file, prints
   `vanilla look checked: N values, M files`, fails the build on drift (replaces the three copies in Ranks / Vault / Gear).
2. **Constants**: `COLOR` (section 3.17 names: label, title, button, button2, gold, gray, caption, disabled, error, success, warning,
   row, rowHover, rowPressed, selected, separator, placeholder, rarity map), `SIZE` (title 38, pad 16/17, btn 44/32/48, pad 24/16,
   min 172, field 38, dropdown 330x32, row 42/50/44), `FONT` ("Secondary"), `SOUND` (light, cancel, save, main, tick, untick, lock,
   unlock, shuffle - inline `Sounds: (...)` strings).
3. **Frame**: `frame(prefix, w, h, decorated=True, close=False)` -> list of `(parent, markup)` appends + body id; `container()` (no
   runes); `panel(id, kind="simple"|"full"|"secondary")`; `close_button(id)`; `assert_root(w, h)` (<= 1080 - margin).
4. **Text**: `label(id, kind, h, align, wrap)` with kinds `default, bold, caption, caption_light, note, row_name, row_sub, row_badge,
   section, subtitle, panel_title, form_caption, gold, error, success, warning, disabled, muted, stat_name, stat_value, big_highlight`;
   `title_label(id)`.
5. **Buttons**: `button(id, text, kind="primary"|"secondary"|"tertiary"|"destructive", size="normal"|"small"|"big", w, selected=False,
   disabled=False, sound=None)` - always all four states + ShrinkTextToFit; `icon_button(id, icon, kind)` (square 44); `list_button(id,
   state="normal"|"selected"|"active")`; `header_text_button(id)`.
6. **Inputs**: `text_field(id, w, placeholder, maxlen, h=38)` (wrapper-group pattern), `number_field(...)`, `search_field(id)`,
   `value_box(id, w)` (read-only InputBox group).
7. **Controls**: `checkbox(id, checked)`, `toggle_row(id, label, on)` (OptionBackgroundPatch row + ON / OFF small tertiary pair),
   `slider(id, min, max, value, w)`, `dropdown(id, w, entries)` - flag the UNVERIFIED ones until probed.
8. **Tabs**: `tab_row(prefix, names, selected, mode="tertiary"|"primary_secondary")`.
9. **Lists**: `scroll_list(id, h)` (TopScrolling + scrollbar), `panel_row(id, state)` (WorldEventListRow), `hover_row(id)`
   (ItemRepairElement), `option_row(id, selected)`, `section_label(id)`, `column_header(...)`, `trade_card(prefix)`.
10. **Separators**: `separator("content"|"fancy"|"vertical"|"header"|"footer")`.
11. **Items**: `item_icon(id, size, item_id)`, `item_slot(id, size, quality=True)` (ItemSlot + `.ItemId` set), `item_grid_style(size,
    icon, spacing, slot_bg=True)`; keep the ItemGridSlot metadata assert.
12. **Feedback**: `tooltip(text)` -> `TooltipText + TextTooltipStyle` string, `info_panel(id, w)` (tooltip-frame panel),
    `progress_bar(id, w, h)`, `spinner(id)`, `status_line(id, kind)`.
13. **Dialogs**: `confirm_dialog(prefix, title, question, message, yes_text, yes_kind="primary", yes_sound="save", no_text="Cancel")`
    (PrefabEditorExitConfirm layout, 620 wide, padding 20).
14. **HUD**: `hud_panel(id, w)` (LegendContainerPanelPatch Border 4, padding 14), `key_chip(id, text)`.
15. **Optional reference mode**: `ref_style_java(selector, doc, name)` -> `b.set("#Id.Style", Value.ref("Common.ui", "SecondaryTextButtonStyle"));`
    behind a per-mod switch until the probe passes.
16. **Safety**: `check_markup(s, prefix)` (balanced braces / parens, no underscore ids, id prefix, no `Anchow`, only proven text
    characters, root anchor W/H only), and SkyyGear's `ui.frames` idea as a global "flat colours" fallback flag.

## 6. UNVERIFIED items - one probe page would settle them

1. `Value.ref("Common.ui", ...)` applied to elements created by `appendInline`.
2. Client-only texture paths from inline (`Pages/Inventory/Slot.png`, `InGame/Tooltips/ItemTooltipDefault.png`) and the
   `../ItemQualities/...` / `Hud/ToolsLegends/...` relative paths.
3. `ItemSlot` with `ShowQualityBackground: true` + `set("#Id.ItemId", ...)` inline.
4. `Disabled: true` / `set("#Id.Disabled", true)` on inline TextButtons.
5. `TooltipText` + `TextTooltipStyle` inline (and Esc with a tooltip open).
6. `MaskTexturePath: "Common/TextGradient.png"` on an inline Label.
7. CheckBox / Slider / DropdownBox / TabNavigation / ProgressBar / CompactTextField elements inline, and their event binding types.
8. A root-level dim sibling (`#000000(0.45)`) / `SceneBlur {}` appended before a Width/Height page root.
9. The exact default Label text colour, and the Default / Secondary font-file mapping.
10. That the `Common/...` textures of the deployed SkyyRanks 0.1.1 / SkyyGear 0.1 / SkyySacks 0.7.7 pages really show (no in-game
    confirmation is recorded yet).
