# SkyWynn UI kit - "SKY WINDOW" (Isles of the Void) - draft v1

**Status: DRAFT v1 for Skyy's review. Not wired in, not committed.** All pixels are original. No vanilla file was copied, traced
or recoloured. Vanilla textures were only read for their sizes and 9-slice borders.

## Why this exists
- Skyy (2026-10-10), on the SKY WINDOW tooltips (`art/tooltip-sky/`): "beautiful! can we design it all with the new theme". So every
  menu and hub page now uses the same theme.
- For the page frame Skyy picked "Each hub its own mood". Every hub uses the same frame, but its corner windows show a different sky:

  | Hub | Mood |
  |---|---|
  | Character | sunrise |
  | Storage | night vault (stars) |
  | Market | golden noon |
  | Smithing | ember forge |
  | World | clear sky |
  | Social | sunset |

  Every other page uses a neutral clear-sky frame.
- The element names, sizes and borders follow `research/Hubs-Spec.md` section 7.3.

## Tools
- **Generator:** `python tools/art/make_ui_kit_sky.py`.
  - Pure Python with no Pillow. It uses every CPU core and takes about 20 s.
  - It is deterministic: two runs give the same bytes.
  - It imports the approved tooltip painters from `tools/art/make_tooltip_sky.py` (gold bevel, sky scenes, isle and waterfall,
    sparkles). That keeps the pages and the tooltips one family.
- **Validator:** `python tools/art/validate_ui_kit_sky.py`. It prints one line per check and ends with ALL OK. It checks:
  - spec names, sizes and borders;
  - that the stretch strips are uniform;
  - that the text areas are opaque;
  - contrast, recomputed from the pixels;
  - hard alpha on the 64 px icons;
  - manifest sha256 values;
  - determinism;
  - that no path collides with Assets.zip.
- **`sheet.png`** (2100 px wide) contains:
  1. **Mock 1:** the Storage hub at UI scale 1 (1080p).
     - The page is 1100 x 860 UI and uses `Frame_Storage`.
     - The hub bar shows Storage selected, Market hovered and Smithing pressed.
     - The Tertiary sub-tabs are Pocket / Requip / Vault (Active) / Bank.
     - It also shows a search box, a panel of 8 rows (normal, hovered, selected) with a scrollbar, a details panel with an inset and
       the empty slot, every button kind in some state, a checkbox, a focused input and a footer.
  2. **Mock 2:** the six hub tiles (CardFrame tiles with the hub icons) on the neutral frame.
  3. The page frame in all 7 moods.
  4. The hub icons at 64 px on dark and light, plus the 128 px @2x file.
  5. Every element twice: once raw, with the 9-slice cuts dashed, and once stretched at 1x.
  6. Every button family and state at game size: 172x44, 150x32 and 172x48.
  7. The contrast table.
- The sheet uses a stand-in 5x7 font. The game font is narrower.

## Files
Every file is in `Common/UI/Custom/SkyyKit/`.
- Markup path: `"SkyyKit/<Element>.png"`, written without `@2x`; the client loads the @2x file itself.
- The jar ships the PNG at that same path.
- Border values are in UI units (1 UI = 2 px of the @2x file).

| Element (states) | @2x px | Border (UI) | What it is / replaces in `tools/skyyui.py` |
|---|---|---|---|
| `Frame` | 160x160 | 32 | Page body, neutral clear sky. Has 4 corner windows (sun, clouds, birds) and star points. Its centre is 98 % opaque. Replaces `ContainerPatch.png` (Border 23). |
| `Frame_<Hub>` (Character, Storage, Market, Smithing, World, Social) | 160x160 | 32 | Same frame. Only the windows change: two sky windows on top and two floating isles with waterfalls on the bottom, in the hub's mood. |
| `Header` | 600x76 | H 60, V 0 | Title bar, always 38 UI high. Each cap has a small sky gem, a gold wing and a stud. The centre is uniform. Replaces `ContainerHeader.png` (H 50, V 0). |
| `HeaderOrnament` | 472x44 | none (236x22 UI) | Crest over the title bar: a sky window, swept gold wings and a star point. Use it like vanilla's decoration (Width 236, Height 22, Top -12). Drop `ContainerDecorationBottom`. |
| `CardFrame` | 160x160 | 32 | Lighter frame with smaller windows. For hub tiles, Smithing set cards and Profiles cards. |
| `Tab`, `_Hovered`, `_Pressed`, `_Selected` | 240x88 | H 20, V 12 | Hub-bar tabs, 44 UI high. Selected has a gold rim, a soft sky glow and a glowing gold underline. |
| `Primary`, `_Hovered`, `_Pressed`, `_Disabled` | 440x88 | H 24, V 12 | Gold main action. The face is deep amber so the kit label `#bfcdd5` stays readable. |
| `Secondary`, `_Hovered`, `_Pressed`, `_Disabled` | 440x88 | 12 | Blue-slate. Use it for most buttons. |
| `Tertiary`, `_Hovered`, `_Pressed`, `_Active` | 256x64 | 12 | Quiet buttons, 32 UI high: sub-tabs, ON/OFF, pagers. Active has a gold rim and a sky tint. |
| `Danger`, `_Hovered`, `_Pressed` | 440x88 | 12 | Crimson with gold sparkles. Use `Primary_Disabled` / `Secondary_Disabled` for a disabled danger button. |
| `Close`, `_Hovered` | 64x64 | none (32 UI) | Gold-ringed round X. |
| `Panel` | 64x64 | 12 | Section panel or inner well: a thin gold line, star sparkles in the corners and a dark interior. Replaces `ContainerPanelPatch` / `ContainerFullPatch`. |
| `PanelInset` | 48x48 | 8 | Recessed sub-box inside a panel, with a dim gold hairline. Replaces the `#000000(0.15)` well. |
| `Row`, `_Hovered`, `_Selected` | 64x48 | 8 | List rows. Selected has a gold left bar and a faint sky tint. Replaces the colour rows (`#101925(0.55)` etc.). |
| `InputBox`, `_Hovered`, `_Selected` | 96x64 | 16 | Recessed field with a bronze rim. Selected (focus) has a gold rim and a sky inner line. Replaces `InputBox*.png`; the border is the same 16. |
| `CheckBox` / `CheckMark` | 44x44 / 32x32 | 7 / none | Check box frame (22 UI) and a gold tick with a sparkle (16 UI). |
| `ScrollTrack`; `ScrollHandle`, `_Hovered`, `_Dragged` | 12x24 | 3 | 6 UI wide bar. The track is a dark groove with a gold thread; the handle is a gold dome, and Dragged adds a sky core. |
| `Separator` | 64x4 | H 8, V 0 | 2 UI gold line that tapers at the ends. |
| `SlotEmpty` | 148x148 | none (74 UI) | Empty item well, in the tooltip-sky `Slot_<R>` family, with a neutral sky. |
| `HubIcon_<Hub>@2x` + `HubIcon_<Hub>` | 128 / 64 | none | Round sky-window badges in the hub's mood, each with a symbol (see the list below). The @2x file is a 64 UI texture. The 64 px file is item-icon size with hard alpha, in the `art/menu-icons` style. |

The hub icon symbols are:
- Character: a blocky player bust with a gold gem.
- Storage: a chest with gold bands and a lock.
- Market: a coin stack and a big coin with an emerald.
- Smithing: an anvil, a gold hammer and sparks.
- World: the floating isle with its waterfall.
- Social: two busts.

`manifest.json` has, for each element:
- the file and markup path;
- its UI size and Border;
- which axis is strip-uniform;
- its `skyyui_use`, saying what it replaces;
- its bytes and sha256.

It also has `hub_frames` / `hub_moods`, the hub icons and the full contrast table.

## How `tools/skyyui.py` should use them (Hubs-Spec 7.2; nothing was edited)
- Add one `THEME["sky"]` table, keyed by element: `(path "SkyyKit/<Element>.png", border)`. Copy the borders straight from
  `manifest.json`.
- `page_shell(..., hub=None)`:
  - the title bar uses `Header` (HorizontalBorder 60, VerticalBorder 0);
  - the body uses `Frame`, or `Frame_<Hub>` on that hub's pages (Border 32);
  - the decoration is `HeaderOrnament`, a 236x22 Group at Top -12;
  - the content padding is **24**, so the corner windows never sit under text. Footer buttons should stay about 20 UI in from
    the sides; mock 1 shows this.
- `button_style(kind)`. All states use the same borders.

  | `kind` | Textures | Borders |
  |---|---|---|
  | primary | `Primary*` | HorizontalBorder 24, VerticalBorder 12 (vanilla used 80; ours works down to about 48 UI wide) |
  | secondary | `Secondary*` | Border 12 |
  | tertiary | `Tertiary*`; `selected=True` uses `Tertiary_Active` | Border 12 |
  | destructive | `Danger*`; disabled uses `Secondary_Disabled` | Border 12 |

- `tab_row` / `hub_bar_markup`: Default `Tab`, Hovered `Tab_Hovered`, Pressed `Tab_Pressed`, active tab `Tab_Selected` (HorizontalBorder 20,
  VerticalBorder 12).
- `row_style` / `hover_row`:
  - use `Row` / `Row_Hovered` for Default / Hovered / Pressed;
  - use `Row_Selected` for the selected row;
  - drop the 4 px `#4274a5` status bar, because the selected row now has its own gold bar.
- `panel(kind simple / full)` uses `Panel` (Border 12, padding 12). `panel(kind well)` uses `PanelInset` (Border 8).
- `text_field` / `search_field` / `value_box` use `InputBox` (Border 16), `InputBox_Hovered` and `InputBox_Selected`.
- `checkbox_style` uses `CheckBox` (Border 7) and `CheckMark`.
- A new `scrollbar_style()`:
  `ScrollbarStyle(Spacing: 6, Size: 6, Background: (TexturePath: "SkyyKit/ScrollTrack.png", Border: 3), Handle: ..ScrollHandle..,
  HoveredHandle: ..ScrollHandle_Hovered.., DraggedHandle: ..ScrollHandle_Dragged..)`.
- `separator(...)`: a Group `Height: 2` with `Background: (TexturePath: "SkyyKit/Separator.png", HorizontalBorder: 8, VerticalBorder: 0)`.
- `close_button`: `Close` / `Close_Hovered` (32x32 UI).
- Text colours, fonts and sounds stay vanilla. Every kit text colour was checked against these textures.

## Readability / contrast
Contrast is the lowest WCAG ratio over the rows where text sits, recomputed by the validator. Every listed colour reaches **4.5:1 or
more**.

- **Frame and CardFrame centre `#0d1527`:**
  - kit text 7.6, white 18.2, title 10.4, row name 14.0, caption 5.5;
  - gold 8.8, error 6.6, success 12.6, info 7.4;
  - Legendary 14.9, Mythic 5.5, Fabled 5.8, Rare 6.9.
  - Report only: captionLight `#5a6a7a` 3.3, a footnote colour that vanilla also keeps faint.
- **Header:** title 6.6.
- **Panel:** text 7.9, propKey 5.4, caption 5.8.
- **PanelInset:** caption 6.0.
- **Rows:**

  | Row | rowName | rowSub `#7f93a6` |
  |---|---|---|
  | `Row` | 13.4 | 5.5 |
  | `Row_Hovered` | 11.4 | 4.65 |
  | `Row_Selected` | 11.0 | 4.51 |

  `Row_Selected` is the tightest pair in the kit.
- **InputBox:** white 19.7, placeholder `#6e7da1` 4.8.
- **Tabs:** 6.2 to 9.0.
- **Buttons:** Primary 5.3, Hovered 4.58, Pressed 6.5; Secondary 5.7 / 4.6 / 7.0; Tertiary 7.2 to 9.6; Danger 5.8 / 5.1 / 7.2.
- **Disabled label `#797b7c`:** about 2.9, which is the intended greyed-out look (report only).
- The frame centre is 98 % opaque, as in the spec. Over a bright sky that shifts it by at most about 5 levels, which keeps every ratio
  above.

## Open points / unsure (default in brackets)
1. **File name for the hub frames.** The coordinator's note said `PageFrame_<Hub>@2x.png`. Hubs-Spec 7.3 names the family
   `Frame` / `Frame_<Mood>`, and the same note asked to match the 7.3 names. [The files are `Frame_<Hub>`, keyed by hub, plus the
   neutral `Frame`. Renaming is one line (`elements()`) plus the validator's SPEC.]
2. **Texture root.** The files are under `Common/UI/Custom/SkyyKit/` with markup path `SkyyKit/...`, per Hubs-Spec 7.1. If probe K1(a)
   proves that `../SkyyKit/` works, they can move to `Common/UI/SkyyKit/`. [Keep Custom/.]
3. **The corner windows are small at UI scale 1.** The page window glass is 21 UI across; at 1080p the scenes read as coloured
   glints with a hint of sun, moon or isle. They read well at UI scale 2. Border 32 cannot take a bigger window without the star
   point leaving the corner patch. [Keep. Use Border 40 with 200 px textures if Skyy wants bigger windows.]
4. **Primary is a deep amber face with a bright gold rim, not a bright gold face.** The kit's light button label (`#bfcdd5`) needs a
   dark face to reach 4.5:1 (Hovered is 4.58). A brighter gold face would need a dark label colour in the kit. [Keep the dark face.]
5. **Danger has no disabled state** in the 7.3 list. [Use `Secondary_Disabled`.]
6. **The neutral Frame and Frame_World look alike.** Neutral has sky in all four windows (sun, clouds, birds). World has two floating
   isles with waterfalls in the bottom windows. [Keep. A second clear-sky variant could be added if Skyy wants World to stand out more.]
7. **The Sunrise (Character) and Sunset (Social) moods share the low-sun scene.** They differ in palette: sunrise is a pale peach sky
   with a blue top, sunset is violet into coral and also has a pink cloud by the isle. [Keep. Ask Skyy if they read too alike.]
8. **The Header has no sky windows**, only small sky gems. The frame's top windows sit just below it. [Keep. Hubs-Spec says the header
   centre is uniform.]
9. **Not tested in game.** These are unverified:
   - Tab HorizontalBorder 20 at about 110 UI wide;
   - the 98 % frame alpha;
   - scrollbar textures inside an inline `ScrollbarStyle`;
   - `SlotEmpty` as an ItemGrid slot background (probe K1(c)).

   [A probe page with every element before the restyle round.]
10. **Hub icon use.** The @2x 128 px file is meant as a 64 UI UI-texture. The 64 px file is for an ItemGrid item icon, and for that
    it would need an item asset (`Skyy_Hub_Icon_<Hub>`) and the path `Common/Icons/ItemsGenerated/`. [Ship the @2x file in the kit.
    The menu round copies the 64 px file as item icons if the hub tiles stay ItemGrid slots.]
