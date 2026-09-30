# Vanilla UI style guide - the contract for every Skyy page builder

Skyy, 2026-09-28: *"the new goal for any and all UI added in the game is for them to look and feel vanilla. i want them as close to
the original game look and feel as possible."* (HANDOFF section 2 rule 0). This file says HOW: every page is built from
**`tools/skyyui.py`** (the one shared kit, 1.4). It holds the game's own style values, textures and sounds and proves them against
Assets.zip at every build. Background and every value's source: `research/Vanilla-UI-Research.md`. What exists today:
`research/Skyy-UI-Inventory.md`. Test the kit: `python tools/skyyui_test.py`.

The HANDOFF section 2 rules still apply and the kit enforces the markup ones: inline pages only (`appendInline`), no underscores in
element ids (also in Java selectors), no duplicate element ids on a page, page root Anchor Width / Height only, TextButton + EventData
for clicks, never periodic page updates, never close a page right before opening another, BIG readable pages that fit 1080 px, no UI
on the vanilla inventory screen, and ItemGridSlot content only as `new ItemStack(id, qty)` (section 8b).

## 0. The in-game gate (read first)

Several properties the kit relies on have never been used inline by a Skyy page (FlexWeight, LayoutMode Full / Right,
LetterSpacing, WrapMaxLines, texture button backgrounds, inline button Sounds, the Disabled look, ShrinkTextToFit, the ornaments
hanging outside the root). One bad property fails the whole inline document ("Failed to parse or resolve document" = a
disconnect), so **the first restyle ships only after Skyy has opened the base probe pages**.

- `SUI.probe_pages()` returns the probe pages. The BASE pages (key `"base"`) come first: `base1` = page 1 (frame, buttons, tabs,
  text), `base2` = page 2 (lists, well, rows, fields, panels), `base3` = page 18 (the kit 1.3 builders: pager, item grid, icon
  cells, confirm views, punctuated text, the display number). Then ONE page per UNVERIFIED feature (3-17), so a page that fails
  names its culprit.
- Every probe page has a **stable name** (`.name`: `base1`, `checkbox`, `number-field`, ..., `base3`; numbers may grow, names do
  not) and **shows its own numbered "what to see" list** (a "PROBE <name> - WHAT TO SEE" head plus one line per check; the same
  lines are in `.look`). `SUI.probe_page("checkbox")` (or a number) returns one page; `.java("b")` = the statements for a
  CustomUIPage build, `.key` = the UNVERIFIED key it proves.
- One mod gets a small admin probe command (for example `/skyyprobe <name>`) that opens a page by name. Open `base1`, `base2`,
  `base3`, then the rest in number order.
- When a page works, add its key to `skyyui.PROBED` (`"base"` once all three base pages work). The UNVERIFIED builders then need
  no `trial=True`, and `verify()` stops printing the "base look not yet seen" note.
- Kit 1.4 APPENDS pages 19-22 (pages 1-18 keep their numbers, names and content - the deployed SkyyUiProbe 0.1 opens them by
  number / name): **19 `base4`** (every kit 1.4 builder, key `"base4"`), **20 `button-text`** (b.set on a TextButton's Text),
  **21 `flex-rows`** (FlexWeight on its own), **22 `layout-right`** (LayoutMode Right on its own). The base pages open first in
  the order `SUI.PROBE_OPEN_FIRST` (base1, base2, base3, base4). Every page has `.summary` (one line, <= 95 characters, for a probe
  mod's index: `SUI.PROBE_SUMMARY`), and `probe.with_footer(footer, foot_h)` places a probe mod's own Back / Close footer with
  the height proofs (the SkyyUiProbe 0.1 rules; it reproduces that mod's views 1-18 exactly). SkyyUiProbe 0.1 itself shows 18
  rows: rebuilt on kit 1.4 its index budget stops the build (22 rows), so pages 19-22 need a SkyyUiProbe 0.2 (a two-column or
  scrolling index built on `.summary` + `with_footer`).

## 1. Setup in a build script

```python
import skyyui as SUI                 # tools/ is on sys.path already (the skyybuild import line)
SUI.verify()                         # prints "vanilla look checked: N style values, M textures / sounds"; fails loudly
KIT_ID = SUI.kit_id()                # "skyyui 1.4 <blob12>": put it in the ready log line, like SkyyMenu shows CFG_KIT
```

- Import it as `SUI`, not `UI`: SkyyRanks 0.1.1 and SkyyMenu 0.3.3 already have a module-level `UI = {...}` table.
- `verify()` raises a `SystemExit` if Assets.zip is missing or any copied value changed after a game update. Never catch it. The fix
  is always in `tools/skyyui.py`, never in the mod.
- The Java emitters (`java_append`, `java_set`, `java_expr`, `java_field`, `java_grid_fill`, `sh.java(...)`) raise
  `NotVerifiedError` until `verify()` has passed in this process, so "every value is proven at every build" cannot be skipped.

## 2. Which kit function for which element

| Element | Kit call | Vanilla source |
|---|---|---|
| Window (title bar, runes, gold ornaments, body) | `page_shell(prefix, w, h, title, body_id=...)` then `.java("b")` / `.appends` | `@DecoratedContainer` (dialogs, forms) |
| Plain window (no runes, no ornaments) | `page_shell(..., kind="plain")` | `@Container` (the list pages: ShopPage, WarpListPage, InstanceListPage) |
| Way out | Esc + a footer Close: `button(id, "Close", "secondary", sound="cancel")`. The X (`page_shell(..., close=True)` / `close_button(id)`) is optional | WorldEventPanelPage footer; containers ship the X hidden |
| Confirm / question window | `confirm_dialog(prefix, title=..., yes_text=, yes_kind="primary"/"destructive")` (title required) | `Pages/PrefabEditorExitConfirm` |
| Confirm INSIDE the page (question + Confirm / Cancel, nothing closes) | `confirm_view(parent, prefix, w, question=, message=, yes_kind=)`; one row: `compact=True` | SkyyRanks buildConfirm in the PrefabEditorExitConfirm look |
| Section head in a list | `section(id, text)` | `WorldEventSectionLabel` |
| Subtitle / panel title with line | `subtitle(id)` / `panel_title(id)` | `@Subtitle` / `@PanelTitle` |
| Any text | `label(id, text, kind, font=, spacing=)`. Kinds: `default bold strong message caption captionLight note muted gold error formError success warning info disabled have outOfStock stock quantity rowName rowSub rowBadge heading propKey propValue summary fieldLabel display tileName section subtitle panelTitle formCaption optionName optionDetail cardCaption tipName tipId tipDesc tipStat setting settingHead` | `SUI.LABELS` names each source |
| Text with commas, dots, "?", "%" or a runtime value | `ap.text(parent, id or None, text, kind, ...)` / `sh.text(...)` (Appends.text: an empty label + a b.set line, automatically) | - |
| Key / value info row (Stats, Bank, Guild, Profile) | `property_row(id, key_id, value_id, key_text)` inside `panel(id, "well")` | `WorldEventPropertyRow` |
| Result line (+ / - / =) | `status_line(id, "colorOf(this.info)")` + `java_status_methods()`; long results: `wrap=True, h=44`; margins: `anchor=` | success `#39f493` / error `#ff6b6b` / "=" info `#7caacc` (`SUI.STATUS`) |
| Button | `button(id, text, kind, size, w)`: kinds `primary secondary tertiary destructive`, sizes `normal small big` | `@TextButton` family |
| Tab row | `tab_row(parent, row_id, tab_ids, names, selected)`: flex Secondary tabs, the active one Primary, 5 px apart (`mode="tertiary"` = the old Skyy look) | `Pages/EntitySpawnPage` |
| Pager (Prev / page / Next) | `pager(parent, prefix, w, text=, prev_on=, next_on=)` - only where `scroll_list` cannot be used (section 3) | small Secondary buttons + a caption (vanilla has no pager) |
| Switch (setting ON / OFF) | `checkbox_row(id, label_id, box_id, checked, text)` once probed; until then `setting_row(...)` + `on_off(...)` | PrefabSavePage @InputLabel + `@CheckBox` |
| Button row (dialog / footer) | `button_row(id, align="center"/"left"/"right")` | confirm page row |
| Plain row / column (no look: holds kit elements) | `group(id or None, "Left"/"Top", w=, h=, anchor=, flex=, pad=)` | PrefabSavePage `Group { LayoutMode: Left; }` around #SelectedPackBox + Browse |
| Text input | `text_field(box_id, field_id, w or flex=1, placeholder=, look=)` | `@TextField` (InputBox.png) |
| Search box | `search_field(box_id, field_id, w, placeholder=)` | `@DefaultDropdownBoxStyle` SearchInputStyle + PluginListPage decoration |
| Read-only value box | `value_box(box_id, text_id, w or flex=1)` | PrefabSavePage `#SelectedPackBox` |
| Dropdown | `dropdown(id, w, search=)` (entries from Java) | `@DropdownBox` |
| List row (panel, status bar, actions) | `panel_row(id, "normal"/"selected"/"static")` + `row_text` + `row_badge` + `row_action` | `WorldEventListRow` |
| Plain hover row (icon + name) | `hover_row(id, "normal"/"selected")` | `ItemRepairElement` / `ShopElementButton` |
| Option card | `option_row(id, selected)` (silent, has Disabled) | `OverrideRespawnPointButton` |
| Nav / category menu | `list_button(id, text, "normal"/"selected")` | `WorldEventNavButton` |
| Settings row (fallback) | `setting_row(id, label_id)` + `on_off(...)` | client `LabeledCheckBoxSetting` |
| Scrolling list | `scroll_list(id, h= or flex=, well=True)` - lists sit on the well | `LayoutMode: TopScrolling` + `@DefaultScrollbarStyle` on `#000000(0.15)` |
| Separators | `separator("content"/"fancy"/"vertical"/"header"/"footer"/"panel"/"form", anchor=)` | `@ContentSeparator` ... form = `#5e512c` divider |
| Inner panel | `panel(id, "well"/"simple"/"full"/"secondary"/"tooltip"/"dark"/"row"/"hud")` | well = WorldEventPanelPage `#Summary` |
| Item icon / slot frame | `item_icon(id, item_id, size)` (a runtime id: `SUI.J("expr", "Weapon_Sword_Iron")`) / `item_frame(id, icon_id=)` / `quality_frame(id, quality, icon_id=)` | ItemIcon / BarterTradeRow border / item quality frames |
| Item grid (inventory-like slots) | `item_grid(id, cols, rows, tooltips=, well=)` + `java_grid_methods()` / `java_grid_fill()` to fill it (section 8b) | client inventory grid 74 / 64 / 2 on the list well |
| Compact clickable item cell (Bazaar products, AH picker, Accessories rows, Trees nodes, Menu launcher) | `icon_cell(id, item, size, state, look=, qty=)`: states `normal selected disabled empty`, looks `row` / `plain` | WorldEventListRow palette / ItemRepairElement palette |
| Trade / product card | `card(id, sold_out=)` (5 px margin box around the button) | `BarterTradeRow` |
| Picker tile (classes, islands) | `tile(id, text, "default"/"selected"/"complete"/"empty")` | Memories tiles |
| Progress bar | `progress(id, kind="memories")` once probed; `bar(id, w, h, fill_px)` is the flat fallback | MemoriesCategoryPanel bar / `@CircularProgressBar` colours |
| Loading | `spinner(id)` | `@DefaultSpinner` |
| Tooltip / tooltip-like panel | `tooltip(text)` as `extra=` / `tooltip_panel(id, quality=)` + `tip*` labels | `@DefaultTextTooltipStyle` / item tooltip frames |
| A look picked at runtime (selected cell, disabled Prev) | `choose(SUI.J("i == sel"), markup_a, markup_b)` in an Appends / `java_append` | - |
| Style fragments for your own elements | `button_style() text_style() row_style() option_style() list_button_style() checkbox_style() dropdown_style() tooltip_style() title_style() scrollbar_style() clear_button_style() search_icon() sounds() patch()` | - |
| **Kit 1.4 blocks** (section 12; proven properties only - probe page 19 `base4`) | | |
| Fixed-width list row (icon + name / sub + right tag + action, no FlexWeight) | `static_row(id, w, icon=, name=, sub=, tag=, action=, bar=)` -> a Markup (`.h` = its outer height, `.sets`, `.ids`) | WorldEventListRow look; SkyyAccessories 0.4.5 rows |
| The 4 px status bar alone (also at runtime) | `status_bar(id, on=True / False / SUI.J("sel"))` (= `row_bar`) | WorldEventListRow #StatusBar |
| Fixed (non-scrolling) list on the well | `list_well(id, w, h=)` or `list_well(id, w, rows=, row_h=)`; `list_well_h(rows, row_h)` | WorldEventPanelPage #ListContainer |
| Result line whose texts carry no + / - / = mark | `result_line(id, colour=SUI.J("infoColor(this.info)", "#39f493"))` + `java_color_by_text("infoColor", rules)` | the status line look |
| Stat / progress bar that drops its fill at 0 | `stat_bar(id, w, h, fill=SUI.J("fillPx(cur, max)", "80"), col=)` -> `bar.choose()` / `bar.pick()` | SkyyParty 0.1.6 bars, progress track |
| Column heads + table rows from ONE list | `column_spec([(text, w), ...], avail, pad_left)` -> `spec.heads(id)` / `spec.row(id, texts)`; `column_heads(id, cols, pad_left)`, `column_row(id, cols, texts)` | WorldEventSectionLabel heads |
| Right-aligned / centred footer WITHOUT LayoutMode Right / Center | `button_row(id, align="right", used=, avail=)` or `left_margin=SUI.J("gapR", "344")`; `right_margin(avail, used)`, `centre_margin(avail, used)` | WorldEventPanelPage #Footer |
| Big number box (PURSE / BANK) | `stat_well(id, heading, number=SUI.J("coinText(purse)", "12345"), caption=)` | SkyyBank 0.1.4 wells |
| Class / profile card | `list_card(parent, id, w, lines, look=, icons=, icon_item=, on=, action=)` -> emit with `card.java("b")`; `list_card_h(rows)`, `list_card_button(...)` | the SKYY CARD of SkyyClasses 0.1.8 / SkyyProfiles 0.1.3 |
| A word where a button would be (Selected / Active / Locked / Coming soon) | `state_word(id or None, text, kind)` | the card_state label |
| Background picked at runtime, from colour NAMES | `group(..., bg=)` / `panel(..., bg=)` with `color_by([(cond, name), ...], default_name)` | - |
| Item in the slot border, optional sold-out cover | `item_frame(id, item=SUI.J("ids[i]", "Weapon_Sword_Iron"), cover=True)` | BarterTradeRow |
| Display-only item cell (no click) | `icon_cell(id, item, size, "static", qty=)` | the static row colour |
| One-row question: wraps / greyed Confirm / a grey hint | `confirm_view(..., compact=True, wrap=True, yes_on=False or SUI.J("picked"), q_col="text")` | SkyyProfiles 0.1.3 pf_row |
| Height budget read from the markup | `ap.add(parent, markup)` (returns its outer height) / `used_height(ap, container)` / `used_width(ap, row)` / `outer_size(markup)` | - |
| Will the text fit? | `text_width(text, size, bold)`, `text_lines(text, width, size)`, `line_height(size)`; `button()` / `label()` warn by themselves (`fit_warnings()`) | the client's NunitoSans / Lexend tables |
| Only proven properties on the page | `assert_proven(sh.appends)` (one table minus `PROBED`; replaces the per-patch forbidden loops) | the deployed pages |
| Button label with punctuation or a runtime value | `ap.button(parent, id, text, kind, trial=True)` (UNVERIFIED `button-text`, probe page 20) | - |

Every builder takes `anchor=` (margins), and the layout builders also take `flex=`, `padding=` / `pad=` and `extra=`. For example
`text_field(..., flex=1, anchor={"left": 0})` (InstanceListPage search) or `separator("content", anchor={"top": 8, "bottom": 8})`
(WorldEventPanelPage). The block builders `pager` and `confirm_view` return a **Part**: an Appends (the `(parent, markup)` list plus
its `.sets` b.set lines) with its ids and `.h`, the height it takes (margins included) for `sh.fit([...])`. Add it to the page
with `sh.appends.extend(part)` (or `+=`): the `.sets` come along and `sh.java("b")` emits them after the appends.

UNVERIFIED (they need `trial=True` and their probe page first): `checkbox` / `checkbox_row`, `text_field(number=True)`, `tooltip`,
`progress` (and `kind="memories"`), `quality_frame` / `tooltip_panel(quality=)`, `item_slot`, `dropdown`, `search_field`, `spinner`,
`tile`, `gradient_label` / `list_button(mask=True)`, `item_grid(slot_bg=True)` / `item_grid_style(slot_bg=True)`,
`button(disable_element=True)`, `java_ref_style` (Value.ref). The kit 1.3 builders (`pager`, `item_grid`, `icon_cell`,
`confirm_view`, `Appends.text`, `choose`) use only base properties and the patterns the deployed pages already use (LayoutMode
Left / Top, Anchor margins, the Button + ItemIcon cell of SkyyBazaar / SkyyAuctions / SkyyTrees, the ItemGrid of SkyyAuctions /
SkyyEssentials / SkyyMenu); they are on base page 18.

## 3. Page layout recipe

```
page root  Group #<Frame> { Anchor: (Width: W, Height: H); }      <- W x H only; H <= 980 (+12 px top / +6 px bottom ornaments)
 title bar 38 px ContainerHeader, gold ornament on top, title 15 px Secondary uppercase #b4c8c9   (never scale it)
 body      ContainerPatch, LayoutMode Top, Padding 17             <- inner width W - 34, inner height H - 38 - 34
   hint      label(kind "default"), or a tab_row (margins 10)
   content   scroll_list(well=True) of rows / a panel("well") of property rows / cards (sh.fit([...]) proves the heights)
   status    status_line(...)
   separator separator("content", anchor={"top": 8, "bottom": 8})
   footer    button_row(align "left" or "right"): Secondary buttons (flex=1 like WorldEventPanelPage), Close = Secondary + cancel
```

- Padding 17 is the container default (the player pages ItemRepairPage, WarpListPage, ShopPage). Editor-style pages may pass
  `pad=SUI.PAGE_PAD` (16); dialogs use 20 (`confirm_dialog`), forms may use 24 (`FORM_PAD`).
- Budget heights: `sh.fit([hint_h, tabs_h, list_h, status_h, footer_h])` raises when the parts do not fit (a Part adds its `.h`).
- Spacing: section head top 10 / bottom 4, subtitle bottom 10, list rows `ROW_GAP` 3, property rows 2, option rows 4, check rows 12,
  settings rows 8, buttons in a row 6 apart (`anchor={"right": 6}`), button row top 8, tabs 5 apart.
- **Paging.** Vanilla never paginates: every vanilla list is `TopScrolling`. **Use `scroll_list` when the page allows it, `pager`
  otherwise** - where the data really is paged (a fixed page size the Java counts on, money lists whose rows must not move under
  the cursor, the "click acts on what the player saw" arrays). `pager` = two small Secondary buttons around a centred caption,
  Prev / Next in the vanilla Disabled look at the ends (`prev_on=SUI.J("pageNo > 0")`); the disabled look is not un-clickable, so
  keep ignoring Prev on page 1 in `handleDataEvent`.
- Confirmations: a separate window only when the page has nothing else to show (`confirm_dialog`); otherwise the in-page
  `confirm_view` (SkyyRanks) or its one-row `compact=True` form (Classes / Profiles inline rows), which also keeps the HANDOFF
  rule "never close a page right before opening another". Guilds / Islands / Trees "click again" arms become a `confirm_view`.
- A settings / form page: `checkbox_row`s (once probed), `text_field`s with a `label` above, `separator("form")` between groups.
- Rows and columns of kit elements go in `group(...)` (no hand-written `Group { LayoutMode: ... }`). Until the base probe pages have
  been seen, prefer what Skyy pages already proved: `LayoutMode: Left / Top`, fixed widths and Anchor margins, and a height budget
  that sums exactly to `sh.inner_h` (`sh.fit(...) == 0`) instead of a FlexWeight filler - SkyyBank 0.1.4 is built that way, and
  `pager` / `confirm_view` centre themselves with a computed left margin for the same reason.

## 4. Buttons and sounds

| Action | Kind | Sound |
|---|---|---|
| The main positive action (Buy, Set rank, Reforge, Create) | `primary` (172 px default, never < 120; a small Primary defaults to 150) | light, or `sound="save"` on a confirm |
| Neutral actions, navigation, Refresh, Prev / Next | `secondary` (row actions and pagers: `size="small"`, 92 / 150 px) | light |
| Cancel / Close / Back | `secondary` | `sound="cancel"` |
| Delete / Remove / Kick / Disband / Reset All, the Confirm of a risky question | `destructive` | cancel (default) |
| The active tab | `primary` inside `tab_row` (the others `secondary`) | light |
| Quiet toggles (no vanilla precedent) | `tertiary` (`selected=True` = Tertiary_Active) | light |
| Unavailable | same kind with `disabled=True` (Disabled.png, grey label, no sound). Do not bind it | none |

- Sound sets: light (every button), cancel, save, main (main menu only), lock / unlock (they keep the light hover, like the vanilla
  merge). Vanilla list rows, nav buttons and option cards are silent; `sound="light"` adds the click where a page wants it.
  `icon_cell` clicks with the light sound by default (the list-row style it copies has it); `sound=None` makes it silent.
- Old colour families map to kinds: brown / blue -> secondary, green -> primary, red -> destructive, gold "selected" -> the active tab
  (primary) or tertiary selected, grey -> disabled (`research/Skyy-UI-Inventory.md` section 3).

## 5. Colours

- Chrome and text: only `SUI.COLOR` names (`label(..., col="gold")`, `color("rowSub")`). Main text `#96a9be`, titles `#b4c8c9`, row
  names `#d6e4ee`, property keys `#7a8a9a` / values `#b7cedd`, summaries `#8fa6ba`, captions `#878e9c`, error `#ff6b6b`, success
  `#39f493`, warning `#ffcc00`, info `#7caacc`, rows `#101925(0.55)`, the well `#000000(0.15)`, the form divider `#5e512c`.
- Result marks (`SUI.STATUS`, read by `java_status_methods`): "+" success `#39f493`, "-" error `#ff6b6b`, "=" **info `#7caacc`**
  (BarterPage `#RefreshTimer`, the info colour a real page shows; kit 1.3). The older gold "=" of SkyyRanks 0.1.1 / SkyyGear 0.1
  stays available by name: `SUI.STATUS_INFO` = `{"info": "#7caacc", "gold": "#E8A93B"}`, `java_status_methods(info="gold")`.
- `gold` (`#E8A93B`) is only a UI Gallery sample in vanilla. It stays for costs and as that named alternative.
- Content colours stay: `SUI.RARITY` (Skyy's lock: Normal `#FFFFFF`, Unique `#FFFF55`, Rare `#FF55FF`, Legendary `#55FFFF`, Fabled
  `#FF5555`, Mythic `#CC66CC` on pages (`RARITY_WYNN` keeps Wynn's `#AA00AA`), Set `#55FF55`), `SUI.QUALITY` (the game's item
  qualities), and data colours such as class, skill and tree colours. List those in a module constant `UI_DATA_COLORS` (a list /
  tuple / dict of literals or of earlier module constants, `list(CLASS.values())`, `A + B`) or mark the line `ui-data`. Otherwise the
  lint rule warns about any other literal colour in a script that imports skyyui.
- A runtime colour goes through `J()`: `label(id, "", "rowName", col=SUI.J("ClassDefs.COLORS[i]", "#8fd67a"))`.

## 5b. Text rules (kit 1.3)

- **Static inline text** is `[A-Za-z0-9 <>/-]` only. For anything else use `ap.text(parent, id, text, kind, ...)` /
  `sh.text(...)`: proven text goes inline, other text (and a `J()` runtime text) becomes an empty label plus a b.set line in
  `.sets` - the SkyyBank `#SkyyBCapMid` pattern, without splitting by hand. With `id=None` it names the label `<parent>Tx<n>`.
  TextButton text cannot be b.set (no Skyy page has done it): keep button labels proven text. Kit 1.4 `ap.button(parent, id, text,
  kind, trial=True)` does the b.set for a punctuated / runtime label, UNVERIFIED (`button-text`) until probe page 20 works.
- **Titles** have no LetterSpacing: vanilla `@TitleStyle`'s `LetterSpacing: 0` is the engine default, and the deployed SkyyRanks /
  SkyyVault titles leave it out. `spacing=0` is never written; `spacing=0.5` / `1.8` are (MemoriesCategory / RespawnPage).
- **WrapMaxLines** only together with `Wrap: true` (vanilla always pairs them): `label(..., wrap=True, max_lines=2)`.
  `max_lines=False` (or `0`) removes a kind's own line limit (heading, propKey, propValue, summary keep Wrap), `wrap=False` drops
  it too, and a `max_lines` without wrap raises. `WrapMaxLines: 0` is never written.
- **Big numbers** (`display`) are 32 px in the Default font: the one big number a real page shows is the Hud/TimeLeft timer. Big
  text in the Secondary font on real pages is a title (RespawnPage 38 px, PortalDeviceSummon 24 px); PortalDeviceSummon's 32 px
  Secondary `@TimeLimitStyle` is defined but never used.
- **Does it fit?** (kit 1.4) `button()` and `label()` measure every static one-line text with the client's own glyph tables
  (`Client/Data/Shared/UI/Fonts`: NunitoSans Medium / ExtraBold for the Default font, Lexend Bold for Secondary - read-only; a
  per-character-class fallback when the client is not installed) and print `skyyui WARNING: ...` when it is wider than its box
  (a button: its width minus 2 x the padding - the vanilla label then shrinks, down to 12 px). A warning, never an error, and never
  a markup change; `fit=False` silences one call, `SUI.fit_warnings("collect" / "off")` all of them. `Appends.text` /
  `ap.button` measure their b.set texts too. For your own checks: `text_width(text, size, bold, font, upper)`,
  `text_lines(text, width, size)` (greedy wrap), `line_height(size)` (1.364 em for Nunito: two 16 px lines = 43.7 px).

## 6. Do / don't

Do:
- Build every window with `page_shell` / `confirm_dialog`, every button with `button` / `button_style`.
- Put lists on the well (`scroll_list(..., well=True)`) and info boxes in `panel(id, "well")`.
- Keep static inline text to `[A-Za-z0-9 <>/-]`; let `Appends.text` / `Shell.text` b.set the rest (the kit raises otherwise).
- Keep text readable. The kit's `text_scale()` is "readable": vanilla 11 / 12 / 13 / 14 px lines become 14 / 15 / 16 / 18 (the
  SkyyRanks scale). Titles, 16 px labels and button labels stay vanilla. Use `panel_row` height 56 for two-line rows.
- Run `SUI.check_page(sh.appends, prefix)` / `SUI.check_markup(s, prefix)` on your own static markup at build time (`java_append`
  runs `check_markup` on everything it emits anyway; `check_page` also proves every b.set target was appended).
- Kit 1.4: run `SUI.assert_proven(ap)` on every page state instead of a hand-written forbidden-property loop (one table: what the
  deployed pages use, minus what `PROBED` has not proven yet), and budget heights with `ap.add(parent, markup)` /
  `SUI.used_height(ap, container)` instead of typing "+ 12" next to an anchor.

Don't:
- No dark-blue custom panels (`#0b1524(0.96)` roots, `#142030` rows, `#16263a` input boxes) and no accent stripes. The vanilla frame
  replaces them.
- No custom button colour triples. No fonts other than `Default` (body, numbers) and `Secondary` (titles, tile names). No custom or
  missing sounds. Lint warns about non-kit texture / sound paths and fonts.
- No `@Variables` / `$C` imports in inline markup (they only work in `.ui` documents; the kit spells every value out).
- No client-only textures (`Pages/Inventory/Slot.png`, the client's own tooltip frame, the settings CheckBox toggle). The item
  QUALITY frames are in Assets.zip (`Common/UI/ItemQualities`, outside the custom root): only their inline path
  `"../ItemQualities/..."` is unverified - use `quality_frame` / `tooltip_panel(quality=)` with `trial=True` until probe page 8
  works. No `@SmallDefaultTextButtonStyle` (its ButtonSmall textures are missing) or `@ButtonDestructiveSounds` (undefined).
- No full-screen dim / BackButton (page roots are Width / Height only; Esc + the footer Close do it).
- Never `new ItemGridSlot(stack)` with a stack you hold (section 8b); lint warns about it in every newest build script.

## 7. Restyling an existing page, step by step

1. Derive the next version the normal way (tools/AGENT-BRIEF.md): a patch script for patch-based mods (a replace of each whole page
   block, with asserts), a copy for copy+edit mods. Never re-run the old patches of Skills 0.4.5, Trees 0.2.3, Classes 0.1.6 or
   Vault 0.1.2.
2. Add `import skyyui as SUI` and one `SUI.verify()` near the top of the generated build script (section 8c).
3. Frame: replace the old root append with `sh = SUI.page_shell("<Prefix>F", W, H, title, body_id="<the OLD root id>")` and paste
   `sh.java("b")` where the old root append was. The old root id is now the body, so every existing
   `appendInline("#<OldRoot>", ...)` keeps working. Delete the old root's Background / Padding / LayoutMode and the accent stripe. A
   page whose size is computed at runtime passes `w=SUI.J("w", "900")`.
4. Styles, element by element, **keeping every id, Text and binding**: swap each old `Style: TextButtonStyle(...)` for
   `SUI.button_style(kind, size)`, each label style for a `label` kind / `text_style`, rows for `panel_row` / `hover_row`, the input
   box Group for `text_field(old_box_id, old_field_id, ...)`, lists into `scroll_list(..., well=True)`, item cells into
   `icon_cell(old_cell_id, ...)`, pagers into `pager(..., ids={"prev": old, "page": old, "next": old})`, confirm rows into
   `confirm_view(..., ids={...})`. Kit 1.4: fixed-width rows into `static_row(old_row_id, w, ..., ids={...})`, class / profile
   cards into `list_card(...)`, number boxes into `stat_well(...)`, heads + table rows into one `column_spec(...)` (recipes in
   sections 13 and 14).
5. Keep the Java working: never rename an element id that is bound (`addEventBinding(..., "#Id", ...)`), set (`b.set("#Id...")`) or
   read (`"#Field.Value"` in EventData). Never change an EventData key or payload (`"a"`, `"tab3"`, `"cell:4:one"`). Keep the state
   arrays (`rowIds`, `cells`, `invIds`) and the "click acts on what the player saw" checks.
6. Re-budget the height: the frame takes 38 px of title bar plus 2 x 17 px of padding. If rows no longer fit, shrink the row count or
   move the list into `scroll_list`. The page must stay <= 980 px high (`assert_page_size`). Kit 1.4: `fit([SUI.used_height(ap,
   sh.body)], sh.inner_h)` reads the heights back out of the markup (`== 0` for a body filled exactly), `SUI.used_width` a row.
7. Run `SUI.assert_proven(ap)` on every page state (kit 1.4), build (must end `assembled ...jar`; read any `skyyui WARNING`
   text-fit line), run `python tools/ci/lint.py` (0 fails; read the colour / path / font / grid-slot warnings), and list in-game
   test steps covering every view and state: empty, error, locked, no permission, profile loading (`spinner` once probed).

## 8. Java embedding

- Static markup: a Java constant `SUI.java_field("ROW", markup)` (or `SUI.emit_fields(cls, {...}, CtField)`), or inline
  `SUI.java_lit(markup)`.
- Runtime parts: wrap them in `SUI.J("expr", sample)` and emit `SUI.java_expr(markup)`. For example, `"Group #SkyyXRow" + (i) + " {..."`.
  Ids take a digit sample, colours a `#rrggbb` sample, sizes a number sample, item ids an item id sample. Never put `J()` inside Text
  (use `Appends.text` or `java_set`).
- Whole statements: `sh.java("b", sets=[(id, "Text", SUI.J("expr"))])`, `SUI.java_append(parent, markup)` (a HUD root such as
  `Anchor: (Full: 0)` needs `page_root=False`), `SUI.java_set(id, "Text", value)`.
- A look picked at runtime: `SUI.java_append(parent, SUI.choose(SUI.J("i == sel"), selected_markup, normal_markup))` emits
  `b.appendInline(p, (i == sel) ? (...) : (...));` - both markups are checked and must create the same element ids.
- Typed values: `SUI.java_set(id, "Value", 0.5)` / `True` / `3` emit a float / boolean / int literal, and
  `SUI.java_set_raw(id, "Value", "pct")` emits `(pct)` so Java picks the `set(String, float / int / boolean)` overload (ProgressBar
  Value, CheckBox Value, Visible, an ItemGrid's Slots list). A `J()` inside a str value is always a String concatenation (safe for Text).

## 8b. ItemGrid slots (the metadata rule)

An ItemStack that may carry metadata (rolled stats, gear records, names) inside an `ItemGridSlot` disconnects the client. So:

- Build the grid with `item_grid(id, cols, rows)`: the markup the deployed pages use (SkyyAuctions item view, SkyyEssentials trade
  columns, SkyyMenu launcher), the client inventory's slot 74 / icon 64 / spacing 2, width `cols x slot + (cols - 1) x spacing`, on the
  list well (no textures: the client's slot frame is client-only, `slot_bg=True` is UNVERIFIED). `tooltips=False` writes
  `InfoDisplay: None` (SkyyAuctions: no hover tooltip left behind after Esc); `drag=True` only for a drag canvas (SkyyHud editor).
- Fill it ONLY with the kit's Java: `SUI.java_grid_methods()` = four static methods (add them with `CtNewMethod.make`, in order):
  `gridSlot(id, qty)`, `gridSlotOf(stack)` (copies the item id and quantity, never the stack), `gridSlots(ids, qtys, n)`,
  `gridSlotsOf(stacks, n)`; then `SUI.java_set_raw("SkyyXGrid", "Slots", "slots")`. Fixed items (a showcase, base page 18):
  `SUI.java_grid_fill(id, [("Food_Bread", 12), None, ...], var="slots")`.
- `SUI.item_grid_java_is_safe(java)` is the same rule as a check; the kit test runs it on every probe page and the grid Java, and
  `tools/ci/lint.py` warns when any newest build script builds `new ItemGridSlot(x)` from anything but a `new ItemStack(...)`.
- Icons outside a grid need no stack at all: `item_icon` / `icon_cell` take the item id (metadata-free).

## 8c. Patch scripts: how kit output gets into a generated build script (worked example)

Patch-based mods (tools/AGENT-BRIEF.md) never edit the generated script; a patch reads the previous generated script, replaces
whole blocks and writes the next one. There are two ways to bring kit output in:

**A. Preferred: the generated script calls the kit at build time** (SkyyBank 0.1.4, `tools/bank_0_1_4_patch.py`). The patch
inserts Python code, so `SUI.verify()` runs at every build and a kit fix reaches the mod on its next build. Cut the old block out
with a token, then replace the token with the new code:

```python
# tools/skyyx_0_2_patch.py  (s = the previous GENERATED script; rep() asserts each anchor occurs exactly once)
rep("import skyybuild as B\n", "import skyybuild as B\nimport skyyui as SUI\nSUI.verify()\n")
cut('PM(r"""\npublic void rows(', "# ---- after the rows", "@@ROWS@@")      # the old markup block becomes a token
NEW = '''ROW = SUI.panel_row("SkyyXRow" + SUI.J("i", "0"))                 # kit calls run when the BUILD runs
PM(r"""
public void rows(@UCB@ b, int n) {
  for (int i = 0; i < n; i++) b.appendInline("#SkyyXList", """ + SUI.java_expr(ROW) + r""");
}""")
'''
rep("@@ROWS@@", NEW)
```

- `@@NAME@@` tokens are safe: kit output never contains `@` (inline markup has no document variables), and the build scripts' own
  `@PKG@` / `@UCB@` tokens are single-`@`.
- The patch's own template is plain Python text: if it uses `%` formatting (`NEW = '''...''' % {...}` like the bank patch), double
  every literal `%` in it; the kit calls inside are evaluated later, at build time, and need nothing.
- Java source goes into the build script's raw strings (`PM(r"""...""")`) and the kit's Java is concatenated in
  (`""" + SUI.java_expr(ROW) + r"""`), so no escaping is involved.
- In a build script whose Java lives in an f-string template (SkyyBazaar `f"""...{PKG}..."""`), give the kit output a name
  before the template and interpolate it: `BZ_CELL = SUI.java_expr(...)` then `{BZ_CELL}` inside the f-string. Interpolated
  text is never re-parsed, so it needs no escaping either.

**B. Pasting already-rendered kit output INTO a template's source text** (only when the generated script cannot call the kit):
the text must survive the template's parsing. `SUI.for_pysource(text)` for a non-raw `f"""` template (braces and backslashes
doubled); `SUI.for_pysource(text, raw=True)` for `rf"""`; `SUI.for_pysource(text, raw=True, fstring=False)` for `r"""` (it only
refuses text that would end the quotes); `SUI.for_fstring(text)` for a `.format` template string; `SUI.for_percent(text)` for a
`%` template. All five round trips, `@@TOKEN@@` replacement and build-time interpolation are run through real Python templates
and then compiled with javassist by `tools/skyyui_test.py`. Pasted output is frozen at patch time: prefer A.

## 9. Maintaining the kit

- Every value the kit emits has a needle `(document, exact text)` registered with `_need(...)`. `verify()` checks each needle, every
  texture (`<path>` or its `@2x`, `../` resolved against the custom root), every sound and the item quality colours / slot frames /
  tooltip frames. Client-only reference values (tooltip / settings / inventory grid) are checked when the client folder exists.
- The test also parses the kit's style values and compares them key by key with the vanilla definitions expanded from Common.ui /
  Sounds.ui / the vanilla pages (spreads, references, constructors): buttons in every kind / size / sound, scrollbar, tooltip, checkbox,
  dropdown, title, list rows, nav buttons, option cards.
- Adding a value means adding its constant, its needle and a builder test in `tools/skyyui_test.py`; a new UNVERIFIED feature also
  needs its probe page in `probe_pages()` with a stable name and a short look list (the test checks every key has one and that
  every page shows its list). The test must print `N ok, 0 fail`.
- Bump `KIT_VERSION` when a builder's output changes. Builds print `kit_id()`, so a mixed set of kit revisions is visible.
- **Additive kits (1.4 on): the old output is frozen.** `tools/skyyui_test.py` holds `SNAP13`: (item count, hash) per group of the
  kit 1.3 builders over ~1760 call shapes, the tables, the vanilla needles and probe pages 1-18, recorded from the 1.3 file before
  any 1.4 change. A later additive kit may only add functions, parameters whose defaults keep the old output, table entries at the
  END of a table, needles registered after the old ones and probe pages after the last one. A group that changes fails the test;
  `python tools/skyyui_test.py --snapshot-dump <tools/dev/scratch/...json>` writes every item's text to diff against a dump made
  from the older kit file. A deliberate output change is a new kit version: record its own snapshot the same way
  (`--print-snapshot`) and say so in section 11.

## 10. Decisions taken from the reviews (2026-09-29)

- Q1 font scale: keep "readable" (vanilla tops out at 14 px in lists; 18 px row names are a deliberate departure).
- Q2 dialog buttons: Cancel / Close = Secondary + cancel sound; Destructive for Delete / Remove / Reset All and the confirm of a
  destructive question.
- Q3 status colours: vanilla green / red; "=" = info blue `#7caacc` since kit 1.3 (SkyyBank pilot review); gold stays available as
  `java_status_methods(info="gold")`.
- Q4 tabs: Primary / Secondary (EntitySpawnPage) is the default, tertiary stays an option.
- Q5 window: decorated for dialogs and forms, plain for list pages - both are vanilla.
- Q6 Mythic: `#CC66CC` stays (Skyy's lock).
- Q7 HUD: `panel(id, "hud")` = `#000000(0.2)`, padding 20 / 10 (Hud/TimeLeft).
- Q8 in-game test page: yes - `probe_pages()`, section 0.
- Q9 paging: `scroll_list` when the page allows, `pager` otherwise (kit 1.3).

## 11. Kit changes and restyles

- 1.2 (2026-09-29, the SkyyBank 0.1.4 pilot restyle): `group()` for plain rows / columns (no look) and `status_line(wrap=,
  max_lines=, anchor=)`. No existing builder's output changed.
- 1.3 (2026-09-29, the SkyyBank pilot review). Output changes (the only ones): titles without `LetterSpacing: 0` (page_shell,
  confirm_dialog, title_label); `display` = 32 px Default font (no `FontName: "Secondary"`); `java_status_methods` "=" =
  `#7caacc`; `WrapMaxLines` never without Wrap / never 0 (no existing builder emitted either); the probe pages (stable names,
  their own look lists, base page 18, pages 1 / 2 wider for the list). New: `pager`, `item_grid`, `java_grid_methods`,
  `java_grid_fill`, `item_grid_java_is_safe`, `icon_cell`, `confirm_view` (+ `compact=True`), `Appends.text` / `Shell.text` /
  `Shell.all_sets`, `Appends.sets`, `choose` / `Choice`, `Part`, `probe_page`, `STATUS_INFO`, `item_icon` with a `J()` id; lint
  WARN rule for grid slots built from a held stack.
- 1.4 (2026-09-29, the stage-1b restyle reviews) - **additive only**: every kit 1.3 builder output is byte-identical (`SNAP13`,
  section 9; the five held restyles below rebuild to the same page Java - SkyyBank's page id stays a838d325f680). New (section 12):
  `Markup`, `static_row`, `status_bar` / `row_bar`, `list_well` / `list_well_h`, `result_line`, `java_color_by_text`, `stat_bar` /
  `BarPair`, `column_spec` / `Columns` / `column_heads` / `column_row`, `right_margin` / `centre_margin`, `button_row(used=,
  avail=, left_margin=)`, `stat_well`, `list_card` / `Card` / `list_card_h` / `list_card_text_w` / `list_card_button` /
  `LIST_CARD_*`, `state_word`, `color_by`, `group(bg=)` / `panel(bg=)`, `item_frame(item=, cover=, icon_anchor=, cover_id=)`,
  `icon_cell(state="static")`, `confirm_view(wrap=, yes_on=, q_col=)`, `Appends.add` / `Appends.used` / `Appends.button`,
  `java_add`, `outer_size` / `used_height` / `used_width` / `is_flex`, `text_width` / `text_lines` / `line_height` /
  `font_table` / `fit_warnings` (+ `fit=` on `button` / `label`), `assert_proven` / `proven_tokens` / `PROVEN_*` /
  `UnprovenError`, `Probe.summary` / `Probe.with_footer`, `PROBE_SUMMARY`, `PROBE_OPEN_FIRST`, probe pages 19-22 and their
  UNVERIFIED keys `base4`, `button-text`, `flex-rows`, `layout-right` (appended to `UNVERIFIED`; `ICON_CELL_STATES` gains
  `"static"` at its end).
- Restyled on the kit, built + reviewed + cross-checked but **HELD** (their SET pins are not bumped) until Skyy has opened the base
  probe pages: SkyyBank 0.1.4 (`tools/bank_0_1_4_patch.py`, regenerated on kit 1.3; page id a838d325f680), SkyyParty 0.1.6
  (`SkyyParty/build_skyyparty_0.1.6.py`), SkyyAccessories 0.4.5 (`tools/acc_0_4_5_patch.py`), SkyyClasses 0.1.8
  (`tools/classes_0_1_8_patch.py`) and SkyyProfiles 0.1.3 (`tools/profiles_0_1_3_patch.py`; the SKYY CARD block they share is
  `list_card` in kit 1.4). Each has a committed harness (`test_*.py` next to its build script). Their generated scripts call the
  kit at build time, so a rebuild on kit 1.4 gives the same pages (checked when 1.4 was made); later restyles (Vault,
  Collections, Guilds, Islands, Skills, Trees, Exploration - research/Skyy-UI-Inventory.md section 7) start from sections 13 / 14.

## 12. Kit 1.4 blocks (the stage-1b restyle reviews)

Every block below is what one of the five held restyles composed by hand, now in the kit - made ONLY from properties the deployed
pages already use (LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour backgrounds, ItemIcon with an
inline ItemId, Wrap): no FlexWeight, no LayoutMode Center / Right / Full, no WrapMaxLines, no LetterSpacing, nothing UNVERIFIED
(`assert_proven` passes on each; probe page 19 `base4` shows all of them - a restyle on them waits for that page like the others
wait for base1-3). Texts follow the `Appends.text` rule everywhere: proven static text inline, punctuated / `J()` text as b.set
lines in the block's `.sets`, `""` = empty (b.set it yourself). Every block takes `ids={...}` or an id argument so a restyle keeps
its page's OLD element ids.

**12.1 Markup and height accounting.** Single-markup blocks return a `SUI.Markup`: a plain markup str (every kit function,
`java_append`, `choose` and `check_markup` take it) that also carries `.h` / `.w` (its OUTER size: Anchor Height + Top + Bottom
(+ 2 x Vertical / Full), Width + Left + Right ...), `.sets` (its b.set lines) and `.ids`. Add it with `ap.add(parent, markup)`: it
appends, carries the `.sets` along and RETURNS the outer height (None when it sets no Height). In a Java loop use
`SUI.java_add(parent, markup)` (the append + its b.set lines). `SUI.used_height(ap, container)` sums the outer heights of a Top
column's direct children (a FlexWeight child counts 0; a child with neither raises), `SUI.used_width(ap, row)` a Left row's widths,
`SUI.outer_size(markup)` / `SUI.is_flex(markup)` one element. Budget: `SUI.fit([SUI.used_height(ap, sh.body)], sh.inner_h)`.

**12.2 Rows and lists.**
- `static_row(id, w, h=56, icon=, name=, sub=, tag=, action=, bar=True, state="static")` - the WorldEventListRow look at a FIXED
  width, as ONE markup: the row #id (56 + 3) = the row panel #idP (w minus the action; `state` "static" = the #101925(0.55) Group,
  "normal" / "selected" = a clickable Button with the vanilla row style - bind #idP), the status bar #idBar, the icon box #idIb +
  ItemIcon #idIc (40 px), the text column #idT (name #idNm 18 px bold + sub #idSb 15 px, centred), the right tag #idTg (150 wide,
  right-aligned) and the small action button #idAct (92 wide, `action_kind` / `action_w` / `action_on=False` = the Disabled look).
  `bar`: True = blue, None = no colour but its 12 px kept (rows line up), False = none, `SUI.J("sel")` = at runtime, a colour name.
  `.text_w` = the text column width (use it for the column heads). A runtime action state: `choose(SUI.J("c"), row_a, row_b)`.
- `status_bar(id, on=True / False / SUI.J("cond"), col="selected")` (= `row_bar`): the 4 px bar + its 8 px gap; `on=J(...)` makes
  its Background a runtime property (`(cond) ? "Background: #4274a5; " : ""`), so the bar keeps its space either way.
- `list_well(id, w, h=)` / `list_well(id, w, rows=, row_h=56, gap=3)`: the vanilla list well, NOT scrolling (= `panel(id, "well",
  pad=4)`); `.inner_w` / `.inner_h`; `list_well_h(rows, row_h, gap)`. Scrolling lists stay `scroll_list(..., well=True)`.
- `column_spec([(text, w), ...], avail=, pad_left=, gap=)` -> a `Columns`: ONE list for the heads, the rows and the widths
  (`.total`, `.slack`, `.width(i or name)`, `.x(i or name)`). `spec.heads(id, outside=4)` = `column_heads(id, spec, pad_left)` - the
  SkyyParty 0.1.6 heads: section-style labels as wide as their columns, Padding Left = the first column's offset (outside = the
  list well's padding when the heads sit above the well). `spec.row(id, texts, kinds=)` = `column_row(...)`: a fixed-width table
  row (row panel or `panel_kind=None`) with one cell #id C<i> per column.

**12.3 Numbers, bars and result lines.**
- `stat_well(id, heading, number=SUI.J("coinText(purse)", "12345"), caption=, w=)` - SkyyBank 0.1.4's PURSE / BANK box as one
  markup: the well (padding 8) with the centred @Subtitle head, the 32 px display number #idN and a grey caption; 118 px + margins.
- `stat_bar(id, w, h, fill, col=, track="progressTrack")` -> a `BarPair` (full, empty): the track #id (LayoutMode Left, the vanilla
  progress track) with its fill Group ONLY in the full variant (SkyyParty's bars: never a 0 px Group). `SUI.java_append(p,
  bar.choose())` appends the right one at runtime (fill > 0); `bar.pick()` for a static fill.
- `result_line(id, colour, h=44)` - the status line look (16 px bold, centred, two lines) for pages whose result texts carry NO
  + / - / = mark (SkyyAccessories 0.4.5, SkyyParty 0.1.6): colour = a COLOR name or `SUI.J("infoColor(this.info)", "#39f493")`.
  `java_color_by_text("infoColor", [("startsWith", "equipped ", "+"), ("contains", " could not", "-")], empty="=",
  default="-")` writes that Java helper (first match wins; colours are the marks or COLOR names; javassist-safe).

**12.4 Cards and state words.**
- `list_card(parent, id, w, lines, look=, icons=, icon_item=, icon_max=1, on=None, ids=, action=)` - the SKYY CARD of SkyyClasses
  0.1.8 / SkyyProfiles 0.1.3 (research/Skyy-UI-Inventory.md section 6), byte for byte (the kit test runs both): the 4 px bar, the
  card body in the look's colour, the item cells (the slot border with an ItemIcon; `icons` = a Java String[] expression for a
  runtime count, looped in the Java), up to three text lines (a line may carry a right-aligned `tag`), the 200 px action column
  #act (a `list_card_button(...)` or a `state_word(...)` goes in: `action=` appends one). `look` = selected / pending / normal /
  off / empty (`LIST_CARD_LOOKS`) or `[(look, java boolean), ..., last]`; `on` = false -> grey text and the sold-out cover over
  the icons. The card's runtime look and icon loop are Java statements, so ALWAYS emit it with `card.java("b")`. Sizes:
  `LIST_CARD_H` 84 + `LIST_CARD_GAP` 4, `list_card_h(rows)` for its list well, `list_card_text_w(w, icon_max)`.
- `state_word(id or None, text, kind="success")` - the bold centred 172 x 44 word where a button would be: Selected / Active
  (success), Locked / Coming soon / Coming later (disabled); kinds `STATE_WORD_KINDS`.

**12.5 Smaller additions (defaults keep the kit 1.3 output).**
- `group(..., bg=)` / `panel(..., bg=)` (colour panels only): a background colour - a COLOR name, a rarity / quality literal or a
  runtime `J()`; `color_by([(java condition, colour name), ...], default_name)` builds that `J()` from validated colour NAMES.
- `item_frame(id, item=, icon_anchor=, cover=True, cover_id=)`: the slot border with an inline-ItemId icon and the vanilla sold-out
  cover; `icon_cell(id, item, size, "static")`: a display-only cell (a Group, no style, no sound).
- `confirm_view(..., compact=True, wrap=True, yes_on=False or SUI.J("picked"), q_col="text")`: the SkyyProfiles 0.1.3 pf_row
  options (a wrapped question, a greyed silent Confirm, a plain grey hint instead of the yellow question).
- `button_row(id, align="right" / "center", used=, avail=)` or `left_margin=SUI.J("gapR", "344")`: a right-aligned or centred
  footer WITHOUT LayoutMode Right / Center - a Left row whose Padding Left is `right_margin(avail, used)` / `centre_margin(...)`;
  `used` = the buttons' outer widths (`used_width`).
- `ap.button(parent, id, text, kind, trial=True)`: a button label with punctuation or a runtime value through b.set (UNVERIFIED
  `button-text`: probe page 20).

**12.6 Text fit and the proven-property table.** `text_width` / `text_lines` / `line_height` / `font_table` measure with the
client's own glyph tables (section 5b); `button()` / `label()` / `ap.text` warn by themselves (`fit=False`, `fit_warnings(mode)`).
`assert_proven(markups, allow=())` raises `UnprovenError` for every element, property key, LayoutMode or special path (the
`Disabled: true` property, `../ItemQualities`, the Memories textures) that no deployed Skyy page uses and no `PROBED` key has
proven, and for anything the table (`PROVEN_ELEMENTS`, `PROVEN_LAYOUTS`, `PROVEN_KEYS`, `PROVEN_SPECIAL`) does not know. The
"base" gate holds exactly what the five restyles kept out by hand: FlexWeight (also proven by `flex-rows`), WrapMaxLines,
LetterSpacing, LayoutMode Center / Right (also `layout-right`) / Full and the other LayoutModes. The kit test checks that every
PROVEN entry really appears in a live build script of the `tools/deploy_set.py` SET. `proven_tokens(markups)` lists what a page
uses.

**12.7 Probe support.** `probe.summary` (one line per page, `PROBE_SUMMARY`), `probe.with_footer(footer, foot_h, foot_w=,
slack=4)` (a probe mod's footer placed with the height proofs; returns the page + footer appends, its Java and where it went) and
`PROBE_OPEN_FIRST` - section 0.

## 13. Recipe: restyle a LIST page (Vault, Collections, Guilds, Islands, Exploration lists)

1. Frame: `page_shell(..., kind="plain", body_id=<old root>)` - vanilla list pages use the plain window.
2. Rows: one `static_row` per entry, built ONCE with `J()` ids / values and appended in the page's Java loop with
   `SUI.java_add(list_id, ROW)`. Keep the old ids through `ids={...}` (row, name, action ...). An icon cell grid (Bazaar-like)
   stays `icon_cell`; a stats table uses `column_row`.
3. List: `scroll_list(id, h=, well=True)` when the page may scroll, `list_well(id, w, rows=)` when the Java counts on a fixed page
   size (then `pager(...)` under it).
4. Heads: a `column_spec` whose first column is the row's text column (`ROW.text_w`), `pad_left` = the row padding + bar + icon box
   (8 + 12 + 52), `spec.heads(id, outside=SUI.WELL_LIST_PAD)` above the well.
5. Result line: `status_line` when the texts carry + / - / =, else `result_line` + `java_color_by_text`. Footer:
   `button_row(align="right", used=, avail=)` (no LayoutMode Right).
6. Budget with `ap.add` / `used_height`, then `SUI.assert_proven(ap)` on every page state.

```python
sh = SUI.page_shell("SkyyXF", 1100, 900, "Vault", kind="plain", body_id="SkyyX")     # the plain list window, old root = body
ap, W = sh.appends, sh.inner_w
ROW_W = W - 2 * SUI.WELL_LIST_PAD
ROW = SUI.static_row("SkyyXRow" + SUI.J("i", "0"), ROW_W, icon=SUI.J("ids[i]", "Weapon_Sword_Iron"),
                     name=SUI.J("names[i]", "Iron sword"), sub=SUI.J("subs[i]", "Rare"), tag=SUI.J("worth[i]", "120 coins"),
                     action="Take", ids={"action": "SkyyXTake" + SUI.J("i", "0")})
spec = SUI.column_spec([("Item", ROW.text_w), ("Worth", 150 + 8)], avail=ROW_W, pad_left=8 + 12 + 52)
ap.add(sh.body, spec.heads("SkyyXHead", outside=SUI.WELL_LIST_PAD))
ap.add(sh.body, SUI.list_well("SkyyXList", rows=10))                          # or SUI.scroll_list("SkyyXList", h=..., well=True)
ap.add(sh.body, SUI.result_line("SkyyXInfo", SUI.J("infoColor(this.info)", "#39f493"), anchor={"top": 8}))
ap.add(sh.body, SUI.button_row("SkyyXFoot", align="right", used=2 * SUI.BTN_MIN_W + 6, avail=W))
ap.add("SkyyXFoot", SUI.button("SkyyXRefresh", "Refresh"))
ap.add("SkyyXFoot", SUI.button("SkyyXClose", "Close", sound="cancel", anchor={"left": 6}))
SUI.fit([SUI.used_height(ap, sh.body)], sh.inner_h)                           # heights read back out of the markup
SUI.assert_proven(ap)                                                         # proven properties only (minus PROBED)
ROW_JAVA = SUI.java_add("SkyyXList", ROW)                                     # goes inside the Java for loop over the entries
```

## 14. Recipe: restyle a CARD page (Classes, Profiles, Skills trees, Islands pickers)

1. Frame: `page_shell(..., body_id=<old root>)` (decorated for a picker / dialog-like page).
2. List: `list_well(id, h=SUI.list_card_h(n))` (or a `scroll_list(..., well=True)` when n can grow).
3. Card: ONE `list_card(...)` with `J()` ids and texts, emitted inside the Java loop with `card.java("b")`; the look chain
   (`look=[("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"]`) and the icon loop (`icons="ic"`) are part of it.
4. Action column: per Java branch append `list_card_button(...)` (Choose / Switch; Primary while pending) or `state_word(...)`
   (Selected / Locked / Coming soon) into `card.act`.
5. A pending choice: `confirm_view(..., compact=True, ids={...})` (with `wrap=True` for a long question, `yes_on=False` while
   nothing is picked, `q_col="text"` for a hint). Heights: `used_height`; then `assert_proven`.

```python
W = sh.inner_w - 2 * SUI.WELL_LIST_PAD
sh.appends.add(sh.body, SUI.list_well("SkyyXList", h=SUI.list_card_h(7)))
i = SUI.J("i")
CARD = SUI.list_card("SkyyXList", "SkyyXCard" + i, W, [
    {"id": "Nm", "text": SUI.J("titleOf(i)"), "kind": "rowName", "h": 24, "col": SUI.J("colorOf(i)", "#8fd67a")},
    {"id": "Sk", "text": SUI.J("skillLine(i)"), "kind": "fieldLabel", "h": 20, "col": "value"},
    {"id": "Ds", "text": SUI.J("descOf(i)"), "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}],
    look=[("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"], icons="ic",
    icon_item=SUI.J("ic[k]", "Weapon_Sword_Iron"), icon_max=4, on="on",
    ids={"icons": "SkyyXIco" + i, "text": "SkyyXTxt" + i, "act": "SkyyXAct" + i})
CARD_JAVA = CARD.java("b")                                                    # inside the loop, before the branches below
PICK_JAVA = SUI.java_append(CARD.act, SUI.list_card_button("SkyyXPick" + i, "Choose"))
DONE_JAVA = SUI.java_append(CARD.act, SUI.state_word(None, "Selected", "success"))
```
