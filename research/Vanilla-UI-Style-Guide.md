# Vanilla UI style guide - the contract for every Skyy page builder

Skyy, 2026-09-28: *"the new goal for any and all UI added in the game is for them to look and feel vanilla. i want them as close to
the original game look and feel as possible."* (HANDOFF section 2 rule 0). This file says HOW: every page is built from
**`tools/skyyui.py`** (the one shared kit, 1.2). It holds the game's own style values, textures and sounds and proves them against
Assets.zip at every build. Background and every value's source: `research/Vanilla-UI-Research.md`. What exists today:
`research/Skyy-UI-Inventory.md`. Test the kit: `python tools/skyyui_test.py`.

The HANDOFF section 2 rules still apply and the kit enforces the markup ones: inline pages only (`appendInline`), no underscores in
element ids (also in Java selectors), no duplicate element ids on a page, page root Anchor Width / Height only, TextButton + EventData
for clicks, never periodic page updates, never close a page right before opening another, BIG readable pages that fit 1080 px, no UI
on the vanilla inventory screen, and ItemGridSlot content only as `new ItemStack(id, qty)`.

## 0. The in-game gate (read first)

Several properties the kit relies on have never been used inline by a Skyy page (FlexWeight, LayoutMode Full / Right,
LetterSpacing, WrapMaxLines, texture button backgrounds, inline button Sounds, the Disabled state, ShrinkTextToFit, the ornaments
hanging outside the root). One bad property fails the whole inline document ("Failed to parse or resolve document" = a
disconnect), so **the first restyle ships only after Skyy has opened probe pages 1 and 2**.

- `SUI.probe_pages()` returns the probe pages: 1-2 = the kit's base look, then ONE page per UNVERIFIED feature (so a page that fails
  names its culprit). Each has `.java("b")` (the statements for a CustomUIPage build), `.look` (numbered: what Skyy should see and
  hear) and `.key`.
- One mod gets a small admin probe command (for example `/skyyprobe <n>`) that opens page n. Open 1, 2, then the rest in order.
- When a page works, add its key to `skyyui.PROBED` (`"base"` for pages 1-2). The UNVERIFIED builders then need no `trial=True`,
  and `verify()` stops printing the "base look not yet seen" note.

## 1. Setup in a build script

```python
import skyyui as SUI                 # tools/ is on sys.path already (the skyybuild import line)
SUI.verify()                         # prints "vanilla look checked: N style values, M textures / sounds"; fails loudly
KIT_ID = SUI.kit_id()                # "skyyui 1.2 <blob12>": put it in the ready log line, like SkyyMenu shows CFG_KIT
```

- Import it as `SUI`, not `UI`: SkyyRanks 0.1.1 and SkyyMenu 0.3.3 already have a module-level `UI = {...}` table.
- `verify()` raises a `SystemExit` if Assets.zip is missing or any copied value changed after a game update. Never catch it. The fix
  is always in `tools/skyyui.py`, never in the mod.
- The Java emitters (`java_append`, `java_set`, `java_expr`, `java_field`, `sh.java(...)`) raise `NotVerifiedError` until
  `verify()` has passed in this process, so "every value is proven at every build" cannot be skipped by accident.

## 2. Which kit function for which element

| Element | Kit call | Vanilla source |
|---|---|---|
| Window (title bar, runes, gold ornaments, body) | `page_shell(prefix, w, h, title, body_id=...)` then `.java("b")` / `.appends` | `@DecoratedContainer` (dialogs, forms) |
| Plain window (no runes, no ornaments) | `page_shell(..., kind="plain")` | `@Container` (the list pages: ShopPage, WarpListPage, InstanceListPage) |
| Way out | Esc + a footer Close: `button(id, "Close", "secondary", sound="cancel")`. The X (`page_shell(..., close=True)` / `close_button(id)`) is optional | WorldEventPanelPage footer; containers ship the X hidden |
| Confirm / question window | `confirm_dialog(prefix, title=..., yes_text=, yes_kind="primary"/"destructive")` (title required) | `Pages/PrefabEditorExitConfirm` |
| Section head in a list | `section(id, text)` | `WorldEventSectionLabel` |
| Subtitle / panel title with line | `subtitle(id)` / `panel_title(id)` | `@Subtitle` / `@PanelTitle` |
| Any text | `label(id, text, kind, font=, spacing=)`. Kinds: `default bold strong message caption captionLight note muted gold error formError success warning info disabled have outOfStock stock quantity rowName rowSub rowBadge heading propKey propValue summary fieldLabel display tileName section subtitle panelTitle formCaption optionName optionDetail cardCaption tipName tipId tipDesc tipStat setting settingHead` | `SUI.LABELS` names each source |
| Key / value info row (Stats, Bank, Guild, Profile) | `property_row(id, key_id, value_id, key_text)` inside `panel(id, "well")` | `WorldEventPropertyRow` |
| Result line (+ / - / =) | `status_line(id, "colorOf(this.info)")` + `java_status_methods()`; long results: `wrap=True, h=44`; margins: `anchor=` | success `#39f493` / error `#ff6b6b` / "=" `SUI.STATUS` |
| Button | `button(id, text, kind, size, w)`: kinds `primary secondary tertiary destructive`, sizes `normal small big` | `@TextButton` family |
| Tab row | `tab_row(parent, row_id, tab_ids, names, selected)`: flex Secondary tabs, the active one Primary, 5 px apart (`mode="tertiary"` = the old Skyy look) | `Pages/EntitySpawnPage` |
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
| Item icon / slot frame | `item_icon(id, item_id, size)` / `item_frame(id, icon_id=)` / `quality_frame(id, quality, icon_id=)` | ItemIcon / BarterTradeRow border / item quality frames |
| Trade / product card | `card(id, sold_out=)` (5 px margin box around the button) | `BarterTradeRow` |
| Picker tile (classes, islands) | `tile(id, text, "default"/"selected"/"complete"/"empty")` | Memories tiles |
| Progress bar | `progress(id, kind="memories")` once probed; `bar(id, w, h, fill_px)` is the flat fallback | MemoriesCategoryPanel bar / `@CircularProgressBar` colours |
| Loading | `spinner(id)` | `@DefaultSpinner` |
| Tooltip / tooltip-like panel | `tooltip(text)` as `extra=` / `tooltip_panel(id, quality=)` + `tip*` labels | `@DefaultTextTooltipStyle` / item tooltip frames |
| Style fragments for your own elements | `button_style() text_style() row_style() option_style() list_button_style() checkbox_style() dropdown_style() tooltip_style() title_style() scrollbar_style() clear_button_style() search_icon() sounds() patch()` | - |

Every builder takes `anchor=` (margins), and the layout builders also take `flex=`, `padding=` / `pad=` and `extra=`. For example
`text_field(..., flex=1, anchor={"left": 0})` (InstanceListPage search) or `separator("content", anchor={"top": 8, "bottom": 8})`
(WorldEventPanelPage).

UNVERIFIED (they need `trial=True` and their probe page first): `checkbox` / `checkbox_row`, `text_field(number=True)`, `tooltip`,
`progress` (and `kind="memories"`), `quality_frame` / `tooltip_panel(quality=)`, `item_slot`, `dropdown`, `search_field`, `spinner`,
`tile`, `gradient_label` / `list_button(mask=True)`, `item_grid_style(slot_bg=True)`, `button(disable_element=True)`,
`java_ref_style` (Value.ref).

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
- Budget heights: `sh.fit([hint_h, tabs_h, list_h, status_h, footer_h])` raises when the parts do not fit.
- Spacing: section head top 10 / bottom 4, subtitle bottom 10, list rows `ROW_GAP` 3, property rows 2, option rows 4, check rows 12,
  settings rows 8, buttons in a row 6 apart (`anchor={"right": 6}`), button row top 8, tabs 5 apart.
- Vanilla never paginates: every vanilla list is `TopScrolling`. Use `scroll_list` wherever the page allows; keep a pager only where
  the data really is paged (and then build it from Secondary buttons).
- A settings / form page: `checkbox_row`s (once probed), `text_field`s with a `label` above, `separator("form")` between groups.
- Rows and columns of kit elements go in `group(...)` (no hand-written `Group { LayoutMode: ... }`). Until the base probe pages have
  been seen, prefer what Skyy pages already proved: `LayoutMode: Left / Top`, fixed widths and Anchor margins, and a height budget
  that sums exactly to `sh.inner_h` (`sh.fit(...) == 0`) instead of a FlexWeight filler - SkyyBank 0.1.4 is built that way.

## 4. Buttons and sounds

| Action | Kind | Sound |
|---|---|---|
| The main positive action (Buy, Set rank, Reforge, Create) | `primary` (172 px default, never < 120; a small Primary defaults to 150) | light, or `sound="save"` on a confirm |
| Neutral actions, navigation, Refresh | `secondary` (row actions: `size="small"`, 92 px) | light |
| Cancel / Close / Back | `secondary` | `sound="cancel"` |
| Delete / Remove / Kick / Disband / Reset All, the Confirm of a risky question | `destructive` | cancel (default) |
| The active tab | `primary` inside `tab_row` (the others `secondary`) | light |
| Quiet toggles (no vanilla precedent) | `tertiary` (`selected=True` = Tertiary_Active) | light |
| Unavailable | same kind with `disabled=True` (Disabled.png, grey label, no sound). Do not bind it | none |

- Sound sets: light (every button), cancel, save, main (main menu only), lock / unlock (they keep the light hover, like the vanilla
  merge). Vanilla list rows, nav buttons and option cards are silent; `sound="light"` adds the click where a page wants it.
- Old colour families map to kinds: brown / blue -> secondary, green -> primary, red -> destructive, gold "selected" -> the active tab
  (primary) or tertiary selected, grey -> disabled (`research/Skyy-UI-Inventory.md` section 3).

## 5. Colours

- Chrome and text: only `SUI.COLOR` names (`label(..., col="gold")`, `color("rowSub")`). Main text `#96a9be`, titles `#b4c8c9`, row
  names `#d6e4ee`, property keys `#7a8a9a` / values `#b7cedd`, summaries `#8fa6ba`, captions `#878e9c`, error `#ff6b6b`, success
  `#39f493`, warning `#ffcc00`, info `#7caacc`, rows `#101925(0.55)`, the well `#000000(0.15)`, the form divider `#5e512c`.
- `gold` (`#E8A93B`) is only a UI Gallery sample in vanilla. It stays for costs and the "=" info mark that SkyyRanks / SkyyGear use;
  whether "=" stays gold or becomes info `#7caacc` (the colour with real-page support) is Skyy's call - change `SUI.STATUS` only.
- Content colours stay: `SUI.RARITY` (Skyy's lock: Normal `#FFFFFF`, Unique `#FFFF55`, Rare `#FF55FF`, Legendary `#55FFFF`, Fabled
  `#FF5555`, Mythic `#CC66CC` on pages (`RARITY_WYNN` keeps Wynn's `#AA00AA`), Set `#55FF55`), `SUI.QUALITY` (the game's item
  qualities), and data colours such as class, skill and tree colours. List those in a module constant `UI_DATA_COLORS` (a list /
  tuple / dict of literals or of earlier module constants, `list(CLASS.values())`, `A + B`) or mark the line `ui-data`. Otherwise the
  lint rule warns about any other literal colour in a script that imports skyyui.
- A runtime colour goes through `J()`: `label(id, "", "rowName", col=SUI.J("ClassDefs.COLORS[i]", "#8fd67a"))`.

## 6. Do / don't

Do:
- Build every window with `page_shell` / `confirm_dialog`, every button with `button` / `button_style`.
- Put lists on the well (`scroll_list(..., well=True)`) and info boxes in `panel(id, "well")`.
- Keep static inline text to `[A-Za-z0-9 <>/-]`. Set everything else with `b.set("#Id.Text", ...)` (the kit raises otherwise).
- Keep text readable. The kit's `text_scale()` is "readable": vanilla 11 / 12 / 13 / 14 px lines become 14 / 15 / 16 / 18 (the
  SkyyRanks scale). Titles, 16 px labels and button labels stay vanilla. Use `panel_row` height 56 for two-line rows.
- Run `SUI.check_page(sh.appends, prefix)` / `SUI.check_markup(s, prefix)` on your own static markup at build time (`java_append`
  runs `check_markup` on everything it emits anyway).

Don't:
- No dark-blue custom panels (`#0b1524(0.96)` roots, `#142030` rows, `#16263a` input boxes) and no accent stripes. The vanilla frame
  replaces them.
- No custom button colour triples. No fonts other than `Default` (body) and `Secondary` (titles, display numbers, tile names). No
  custom or missing sounds. Lint warns about non-kit texture / sound paths and fonts.
- No `@Variables` / `$C` imports in inline markup (they only work in `.ui` documents; the kit spells every value out).
- No client-only textures (`Pages/Inventory/Slot.png`, the client's own tooltip frame, the settings CheckBox toggle). The item
  QUALITY frames are in Assets.zip (`Common/UI/ItemQualities`, outside the custom root): only their inline path
  `"../ItemQualities/..."` is unverified - use `quality_frame` / `tooltip_panel(quality=)` with `trial=True` until probe page 8
  works. No `@SmallDefaultTextButtonStyle` (its ButtonSmall textures are missing) or `@ButtonDestructiveSounds` (undefined).
- No full-screen dim / BackButton (page roots are Width / Height only; Esc + the footer Close do it).

## 7. Restyling an existing page, step by step

1. Derive the next version the normal way (tools/AGENT-BRIEF.md): a patch script for patch-based mods (a replace of each whole page
   block, with asserts), a copy for copy+edit mods. Never re-run the old patches of Skills 0.4.5, Trees 0.2.3, Classes 0.1.6 or
   Vault 0.1.2.
2. Add `import skyyui as SUI` and one `SUI.verify()` near the top.
3. Frame: replace the old root append with `sh = SUI.page_shell("<Prefix>F", W, H, title, body_id="<the OLD root id>")` and paste
   `sh.java("b")` where the old root append was. The old root id is now the body, so every existing
   `appendInline("#<OldRoot>", ...)` keeps working. Delete the old root's Background / Padding / LayoutMode and the accent stripe. A
   page whose size is computed at runtime passes `w=SUI.J("w", "900")`.
4. Styles, element by element, **keeping every id, Text and binding**: swap each old `Style: TextButtonStyle(...)` for
   `SUI.button_style(kind, size)`, each label style for a `label` kind / `text_style`, rows for `panel_row` / `hover_row`, the input
   box Group for `text_field(old_box_id, old_field_id, ...)`, lists into `scroll_list(..., well=True)`.
5. Keep the Java working: never rename an element id that is bound (`addEventBinding(..., "#Id", ...)`), set (`b.set("#Id...")`) or
   read (`"#Field.Value"` in EventData). Never change an EventData key or payload (`"a"`, `"tab3"`, `"cell:4:one"`). Keep the state
   arrays (`rowIds`, `cells`, `invIds`) and the "click acts on what the player saw" checks.
6. Re-budget the height: the frame takes 38 px of title bar plus 2 x 17 px of padding. If rows no longer fit, shrink the row count or
   move the list into `scroll_list`. The page must stay <= 980 px high (`assert_page_size`).
7. Build (must end `assembled ...jar`), run `python tools/ci/lint.py` (0 fails; read the colour / path / font warnings), and list
   in-game test steps covering every view and state: empty, error, locked, no permission, profile loading (`spinner` once probed).

## 8. Java embedding

- Static markup: a Java constant `SUI.java_field("ROW", markup)` (or `SUI.emit_fields(cls, {...}, CtField)`), or inline
  `SUI.java_lit(markup)`.
- Runtime parts: wrap them in `SUI.J("expr", sample)` and emit `SUI.java_expr(markup)`. For example, `"Group #SkyyXRow" + (i) + " {..."`.
  Ids take a digit sample, colours a `#rrggbb` sample, sizes a number sample. Never put `J()` inside Text.
- Whole statements: `sh.java("b", sets=[(id, "Text", SUI.J("expr"))])`, `SUI.java_append(parent, markup)` (a HUD root such as
  `Anchor: (Full: 0)` needs `page_root=False`), `SUI.java_set(id, "Text", value)`.
- Typed values: `SUI.java_set(id, "Value", 0.5)` / `True` / `3` emit a float / boolean / int literal, and
  `SUI.java_set_raw(id, "Value", "pct")` emits `(pct)` so Java picks the `set(String, float / int / boolean)` overload (ProgressBar
  Value, CheckBox Value, Visible). A `J()` inside a str value is always a String concatenation (safe for Text).
- Kit output never contains `@`, so `@PKG@`-style token replacement is safe. Inside a Python f-string / `.format` template, wrap it in
  `SUI.for_fstring(...)`. Inside a `%` template, wrap it in `SUI.for_percent(...)`. A patch script that pastes kit output INTO the
  source of a generated build script (a non-raw `f"""` template, as in SkyyAccessories, SkyyBazaar, SkyyHud, SkyySacks, SkyySkills)
  uses `SUI.for_pysource(text)` (braces and backslashes doubled; `raw=True` for an `rf"""` template). Interpolating
  `{SUI.java_lit(x)}` at run time needs none of this.

## 9. Maintaining the kit

- Every value the kit emits has a needle `(document, exact text)` registered with `_need(...)`. `verify()` checks each needle, every
  texture (`<path>` or its `@2x`, `../` resolved against the custom root), every sound and the item quality colours / slot frames /
  tooltip frames. Client-only reference values (tooltip / settings) are checked when the client folder exists.
- The test also parses the kit's style values and compares them key by key with the vanilla definitions expanded from Common.ui /
  Sounds.ui / the vanilla pages (spreads, references, constructors): buttons in every kind / size / sound, scrollbar, tooltip, checkbox,
  dropdown, title, list rows, nav buttons, option cards.
- Adding a value means adding its constant, its needle and a builder test in `tools/skyyui_test.py`; a new UNVERIFIED feature also
  needs its probe page in `probe_pages()` (the test checks every key has one). The test must print `N ok, 0 fail`.
- Bump `KIT_VERSION` when a builder's output changes. Builds print `kit_id()`, so a mixed set of kit revisions is visible.

## 10. Decisions taken from the reviews (2026-09-29)

- Q1 font scale: keep "readable" (vanilla tops out at 14 px in lists; 18 px row names are a deliberate departure).
- Q2 dialog buttons: Cancel / Close = Secondary + cancel sound; Destructive for Delete / Remove / Reset All and the confirm of a
  destructive question.
- Q3 status colours: vanilla green / red; "=" stays gold until Skyy picks (see section 5).
- Q4 tabs: Primary / Secondary (EntitySpawnPage) is the default, tertiary stays an option.
- Q5 window: decorated for dialogs and forms, plain for list pages - both are vanilla.
- Q6 Mythic: `#CC66CC` stays (Skyy's lock).
- Q7 HUD: `panel(id, "hud")` = `#000000(0.2)`, padding 20 / 10 (Hud/TimeLeft).
- Q8 in-game test page: yes - `probe_pages()`, section 0.

## 11. Kit changes and restyles

- 1.2 (2026-09-29, the SkyyBank 0.1.4 pilot restyle): `group()` for plain rows / columns (no look) and `status_line(wrap=,
  max_lines=, anchor=)`. No existing builder's output changed.
- Restyled on the kit (built, not yet seen in game): SkyyBank 0.1.4 (`tools/bank_0_1_4_patch.py`, BankPage; kit 1.2).
