# SkyWynn hub contract (kit skyyui 1.5, 2026-10-15; + kit 1.6 and kit 1.7 - THE PAGE SHELL - at the end)

Skyy (2026-10-10, `docs/answered/ui.md`) picked all the hubs and the Sky Window look: "I like 2 the best", then "beautiful! can we
design it all with the new theme". So the SkyWynn Menu becomes a few **hubs** with **tabs**. Each mod adds its own tab through the
bridge, so nothing is rewritten centrally, and a mod that is not loaded simply has no tab.

- Spec: `research/Hubs-Spec.md` sections 1.2 (the tabs), 2 (how a hub works) and 7 (the Sky Window look).
- Implementation: the kit 1.5 section at the end of `tools/skyyui.py`.
- Proof: `python tools/test_skyyui_hubs.py` (see "Tests" at the end).
- Engine facts (H0 probes, 2026-10-15):
  - kit textures work under `Common/UI/Custom/SkyyKit/`;
  - a path outside `Common/UI/Custom` **disconnects the client**;
  - when two jars ship one path, the later-loaded jar wins;
  - a tab in jar A opening jar B's page through a bridge Function works with no flicker, and so does the command fallback.

## 1. The registry (on `skyy.bridge`; java.lang / java.util types only)

| Key | Value | Who |
|---|---|---|
| `hub:tab:<hub>:<tab>` | `Object[]{ String mod, String label, Integer order, String command, Function open, Function visible }` | the mod that owns the page; put in start/setup, removed in `shutdown()` |
| `hub:def:<hub>` | `Object[]{ String title, String command, String iconItemId }` | SkyyMenu |
| `hub:last:<uuid>` | `java.util.Map<String hub, String tab>`, memory only | SkyyMenu creates it. Every `HubBar.build` writes into it when it exists |

**Names.**
- `<hub>` is one of `character storage market smithing world social settings` (`skyyui.HUBS`).
- `<tab>` is 1-16 lowercase letters or digits, starting with a letter. It can never be `back` or `close`.
- Labels keep only `[A-Za-z0-9 <>/-]` and at most 24 characters.

**The Functions.**
- `open.apply(UUID)` opens the page and returns `Boolean.TRUE`. It runs on the player's world thread.
- `visible.apply(UUID)` must return `Boolean.TRUE` for the tab to show. `null` means always visible. Anything else, or an exception,
  hides the tab.
- Either Function may be `null`.

**When `open` fails.** If `open` is missing, throws, or does not return TRUE, the bar runs `command` as the player, so permission
checks apply as if the player had typed it.

**Tab orders.** The orders in `skyyui.HUB_TABS` (= spec 1.2) are the contract. A new tab picks an order number between two of them.

## 2. How a mod adds its tab (H3 rounds: about 6 lines per mod)

> **Core mode (SkyyCore 1.0, 2026-10-15): read `tools/CORE-CONTRACT.md` section 2 step 3 instead of steps 1, 3 and 7 below.** A mod
> built with `B.link_core` installs NO HubBar of its own: it calls the shared `com.skyy.core.ui.HubBar` (`put(...)` the same,
> `removeAll("<Mod>")` with its mod name, `SUI.java_hub_build(sh, "<tab>", cls=SUI.CORE_HUB_BAR)`) and ships NO kit art (SkyyCore
> ships the 59 files once). Steps 2, 4, 5 and 6 are unchanged. Old-way builds keep following this section as written.

1. **Install the class.** `SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod)` adds class `HubBar` to the mod's own
   package, and you `writeFile` it with your other classes. Every jar gets its own copy, because cross-jar classes are not allowed.
2. **Register.** In start/setup, call
   `HubBar.put("<hub>", "<tab>", "<Mod>", "<Label>", <order>, "<command>", new <Mod>HubOpen(), <visible or null>)`. `<Mod>HubOpen` is
   a small class that implements `java.util.function.Function` and opens the page for the UUID.
3. **Remove on shutdown.** In `shutdown()`, call `HubBar.removeAll()`. It removes only keys that still hold this jar's own array.
4. **The page markup.** There are two ways:
   - Use `sh = SUI.hub_shell(prefix, w, h, "<hub>")`: the theme frame, the hub title, `< Menu`, the close X and the tab strip.
   - Keep your own shell and add `SUI.hub_bar_markup(body, prefix)` as the body's FIRST child, `SUI.hub_menu_button(prefix)` into
     your title bar, and `SUI.hub_close(prefix)` last into the root.

   Either way, drop the page's own in-body title row and check the new size with
   `SUI.assert_hub_page(w, h, hub="<hub>", pad=<your padding>)`. The bar costs +52 px, minus the 38 px title row it replaces.
5. **build().** Right after the shell, add the line from `SUI.java_hub_build(sh, "<tab>", cls="@PKG@.HubBar")`. It reads the
   registry, keeps the visible tabs, sorts them by order, draws them, and binds `a = "hub:<tab>"`, `"hub:back"` and `"hub:close"`.
6. **handleDataEvent().** Do this FIRST:
   `String r = HubBar.handle(this.playerRef, data, "<hub>", "<tab>"); if ("close".equals(r)) { close(); return; } if (r != null) return;`
   - It returns `null` when the click was not a hub click.
   - `< Menu` runs `/skymenu`. Without SkyyMenu it answers `"close"`.
   - The page's own tab answers `"self"`.
   - Any other tab opens through `open`, or else through `command`.
   - To switch in place to a tab of the same page (like Reforge -> Upgrade), check `a` before calling `handle`.
7. **Ship the kit art.** Build the jar with `extra_files=dict(files, **SUI.kit_texture_files())`. That is all 59 Sky Window files,
   byte-identical in every jar.
   - The kit pins their sha256; `sky_verify()` stops the build if a byte differs.
   - `SUI.check_jar_kit(jar)` checks a built jar.
   - Never write a texture path outside `Common/UI/Custom`. `SUI.check_sky_paths(markups)` refuses one.

## 3. Sizes and looks

- **The bar.**
  - Tabs are 44 high, with 8 px under them (`HUB_BAR_H` 52) and 5 px between them.
  - Tab width = `(w - 5 x (n - 1)) / n`.
  - The minimum is 110 with the sky Tab art (`HUB_THEME = "sky"`) and 160 with vanilla.
  - If more tabs are registered than fit, the bar shows the first ones that fit and always keeps the active tab.
- **Character (8 tabs)** needs a 915 px strip. That means:
  - a 960 page with the vanilla padding 17, which is today's Skills page;
  - or 963 or more with the sky padding 24.

  The hub page target is 1200 x 900 (spec 2.5). The kit asserts this (`assert_hub_fits`).
- **Themes.** `THEME["vanilla" | "sky"]` maps each role (frame, header, ornament, panel, inset, row*, separator, input*, scroll*, slot,
  close*, tab*, the button families) to its Background value.
  - The theme helpers are `theme_bg`, `theme_button_style`, `theme_tab_style`, `theme_scrollbar_style`, `theme_row_style` and
    `theme_separator`.
  - With "vanilla", the helpers return exactly the kit 1.4 output.
  - `KIT_THEME` stays `"vanilla"`, so the old builders are unchanged. Hub pages use `"sky"`, and H9 moves each page over in its
    mod's round.
  - Text colours, fonts and sounds stay vanilla.

## 4. Not proven in game yet (the H2 in-game test)

- The `< Menu` button sits INSIDE the 38 px title bar (Anchor Left 10, Top -3, 110 x 30). No probe has drawn a button in a title bar
  yet.
- The sky title bar (`Header`) with the `HeaderOrnament` crest has only been drawn as boxes inside a page (art1), not as a page
  shell.
- The 16 px tab label with ShrinkTextToFit on the sky Tab. Probe art2 used a 16 px label without the shrink.

## Tests

`python tools/test_skyyui_hubs.py`:
- checks the art (pins, manifest, a changed byte fails);
- builds a self-test Character page and checks it: markup rules, proven properties only, every texture under `Common/UI/Custom`,
  and 8 tabs of 110 or more at 1080p;
- compiles `HubBar` with javassist against the cached HytaleServer.jar and runs it with `-Xverify:all`. It checks that `build()`
  into a real UICommandBuilder gives the same bytes as `hub_bar_preview()`, and it also covers the bindings, `hub:last`,
  `handle` / `open` (the bridge Function, the command fallback, hidden / missing), the overflow rule and `removeAll`.

`python tools/skyyui_test.py` still proves that the kit 1.4 output is byte-identical.

## Kit 1.6 (2026-10-15, research/Unified-Menu-Plan.md U1) - additive

Skyy (2026-10-15, `docs/answered/ui.md` UNIFIED MENU LAYOUT): "combined D and A ... with the bub row up top", tabs "Icon first, themed
later". Kit 1.6 adds ROW 1 (the hubs) on every hub page, an optional icon behind each tab's word and a default tab per hub.

- **Nothing changes for a kit 1.5 builder.** `KIT_VERSION` stays `"1.5"` (41 builders assert it); `KIT_HUB_VERSION = "1.6"` names the new
  level. With the default arguments every 1.5 function returns byte-identical output (the self-test compares against the committed kit).
  A mod that stays on 1.5 keeps "< Menu", which runs `/skymenu` - since SkyyMenu 0.3.29 that opens **Home**.
- **Opting in (each hub mod's next round, U2):**
  1. `SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True)` - the same class plus the kit 1.6 members.
  2. `sh = SUI.hub_shell(prefix, w, h, "<hub>", row=True)` - the 38 px title bar holds `#<prefix>HubRow` instead of "< Menu", the title
     and the crest. **Same page size**: `assert_hub_page` as before. `sh.row_w` = `w - 50`; `sh.parts` = row + close (no `HubMenu`).
  3. `SUI.java_hub_build(sh, "<tab>", cls="@PKG@.HubBar")` now emits `HubBar.build2(b, ev, prefix, hub, tab, tabs_w, uuid, parts, row_w)`:
     row 1, the X binding and the tab strip.
  4. In `handleDataEvent` call `HubBar.route(...)` where you called `handle(...)` (same answers, plus row 1). Row clicks send
     `a = "hub:h:<id>"`: `"home"` runs `/skymenu` (answer `"back"`; SkyyMenu's own pages open Home in place), the page's own hub answers
     `"self"`, another hub opens its tab (`goHub`: the default tab, else the last tab, else the first visible one; a hub with no tab runs
     its `hub:def` command).
- **Row 1** = Home + every hub with a `hub:def` (order `SUI.HUB_ROW_IDS`), icon (the def's item id) + label, the active one Primary, the
  others Tertiary; 30 px buttons, 4 px apart, from 10 px in to 40 px before the right edge (the X keeps its corner). Buttons narrower than
  88 px drop the icon; every title fits at the 10 px shrink floor (`assert_hub_row_fits`). Without any `hub:def` (no SkyyMenu) the row
  shows the page's hub title.
- **Registry additions** (java.lang types only):

| Key | Value | Who |
|---|---|---|
| `hub:def:<hub>` | `Object[]{ title, command, iconItemId, String defaultTab or null }` (4th element new; 1.5 readers use 0-2) | SkyyMenu (`HubBar.def4`) |
| `hub:def:home` | `Object[]{ "Home", "skymenu", "Skyy_Menu", null }` | SkyyMenu |
| `hub:tab:<hub>:<tab>` | the 1.5 entry, optionally + element 6 = `"<hub>_<tab>"` (the tab icon) | the owning mod (`HubBar.putIcon`) |
| `home:alert:<mod>` | `java.util.function.Function`: `apply(UUID)` -> `null` or up to 3 lines `"text\|target"` (target `<hub>:<tab>`, `<hub>` or `edit`), called on the world thread while Home draws | any mod (U3); SkyyMenu publishes `home:alert:SkyyMenu` |

  Default tabs: Character -> `skills` (Skyy: "id do skills as the default one for this").
  A hub's default tab beats its remembered last tab (`HubBar.pickTab`): the Character hub always opens on Skills; a hub without a
  default tab reopens its last tab (`hub:last`).
- **Tab icons (the hook only - no art yet):** a tab put with `HubBar.putIcon(..., "<hub>_<tab>")` draws `SkyyHubTabs/<hub>_<tab>.png`
  (36 x 36, centred, behind the word; the active tab `..._on.png`, brighter) inside a `Button` with the tab art and a label on top. Ship
  the art at `Common/UI/Custom/SkyyHubTabs/<hub>_<tab>@2x.png` (+ `_on`) in the SAME round that names it (`SUI.hub_tab_icon_paths`); a tab
  without an icon is the 1.5 TextButton, byte for byte. `check_sky_paths(..., tab_icons=True)` accepts the hook path; never a path outside
  `Common/UI/Custom`. Themed tabs (Skyy: "or the tab is stylized to whatever it is") come later, hub by hub.
- **Python twins:** `hub_row_preview` (= `buildRow`), `hub_bar_preview2` (= `build2`'s strip). `python tools/test_skyyui_hubs.py` phase 4
  compiles the row class (sky + vanilla) and compares both byte for byte, plus `def4` / `defTab` / `putIcon` / `pickTab` / `goHub` / `route`.
- **Not proven in game yet:** an `ItemIcon` inside a row `Button` in the title bar; a `Button` holding a background Group + a Label as a tab
  (the icon hook); the 30 px Tertiary / Primary art at 88-150 px wide.

## Kit 1.7 (2026-10-16, research/Menu-Pattern.md) - THE PAGE SHELL: every hub page is `hub_page()`

Skyy (2026-10-16, `docs/answered/ui.md`): "lets try to reduce and compress the menus together to reduce clutter. then make sure its
consistent across the board, then follow the pattern when making new or adding to existing menus." + "keep this top bar at this size
consistent at the top across every menu." + "I never want to have to use a back button. The menus at the top should always be there for
easy navigation." Popups: every hub page Home's size (1600 x 980); row 2 big like Teleport (56 px).

- **Additive.** `KIT_VERSION` stays `"1.5"`, `KIT_HUB_VERSION` stays `"1.6"` (pinned SET scripts assert them); `KIT_PAGE_VERSION = "1.7"`.
  Nothing changes for a page that does not call `hub_page`; `install_hub_bar(..., page=False)` is byte-identical to before.
- **The page (1600 x 980, sky theme, padding 24 -> 1552 inside), top to bottom:** title bar 38 (crest + hub title + X) | row 1 =
  Home + 7 hubs at Home's exact size (48 + 8; `BIG_ROW_*`) | row 2 = the hub's tabs at Teleport's size (56 + 8; `HUB_BIG_TAB_*`, the
  48 px tab art behind the word, labels 20 px shrinking to 14, tabs >= 150 wide; not on Home) | optional ONE sub-tab row (32 + 8;
  `SUB_TAB_*`, 150 px small buttons, the active one Primary) | the content (what is left) | optional footer (10 + 48: info line left,
  buttons right, the Primary right-most). Rows 1 + 2 never shrink - the content does. Content heights: no sub / no footer 774, footer
  716, sub + footer 676 (`sh.content_h`); Home (no row 2): 838.
- **No back buttons (rule 8).** A sub view is a sub-tab or an in-page selection; rows 1 + 2 always lead away. Never draw "< Menu",
  "< Back", "Go Back", "< <page>" - `hub_menu_button` / `HUB_MENU_TEXT` are DEPRECATED (kit 1.5 pages not yet swept only).
- **Lists (rule 7 + 3.3):** `SUI.scroll_list(id, h=..., well=True)`, never `pager()` (exception: a grid of real slots - Vault pages, the
  Menu's shortcut grids; mark the line `# menu-pattern-ok`). Few rows grow: `hs = SUI.grow_row_sizes(list_h, row_h)` (3 heights, up to
  2x, a big tier never more than half the list) and in Java `int k = HubBar.growSize(n, list_h, HS, gap)` (Python twin `grow_pick`).
  Empty list: `SUI.empty_state(id)`; locked content greyed with how to unlock it: `SUI.locked_line(id)`. Detail panel `SUI.DETAIL_W` (456).
- **Footer pieces:** `SUI.foot_info(id, w)` (the info / status line), `SUI.foot_button(id, text, w, kind, sound)` (48 high), `FOOT_GAP` 10.

### How to move a page (sweep rounds S1-S4: the recipe)

1. HubBar: `SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)` (page implies big + sub; keep
   `sub=True` users as they are).
2. Shell: `sh = SUI.hub_page("<Prefix>", "<hub>", sub=<has sub-tabs>, footer=<has buttons>, body_id="<Prefix>B",
   content_id="<the OLD body / root id>", content_w=<old inner width if the content is not widened>, content_layout="Top" | "Left")`.
   Passing the old body id as `content_id` keeps every old `appendInline("#<old body>", ...)` working. Delete the page's own title row,
   "< Menu", back button, tab strip, inner tab rows and pagers.
3. Height: the old body must fit `sh.content_h` (see the numbers above) - shrink rows / turn pages into one `scroll_list`, never shrink
   rows 1 / 2. Width: 1552 (or `content_w`, centred).
4. build(): `sh.java("b")`, then `SUI.java_hub_page(sh, "<tab>", cls="@PKG@.HubBar")` (a merged page: `tab_expr=
   '@PKG@.HubBar.selOf("<hub>", "<tab>")'`) = `HubBar.page17(b, ev, prefix, hub, tab, 1552, uuid, parts)` (row 1, row 2, the X).
   Sub-tabs: `HubBar.subTab(b, ev, "<Prefix>", i, label, selected, "<action>" | null, 150)` into `#<Prefix>Sub`; footer pieces into
   `#<Prefix>Foot`; content into `sh.content`.
5. handleDataEvent: unchanged - `HubBar.route(...)` first (row 1 sends `hub:h:<id>`, row 2 `hub:<tab>`, the X `hub:close`).
6. Build-time check: `pv = SUI.hub_page_preview(sh, tabs=[(id, label) ...], my_tab="<tab>")` + the page's content markup, then
   `SUI.check_page(pv, prefix)`, `SUI.assert_proven(pv)`, `SUI.check_sky_paths(pv, tab_icons=True)`, `SUI.assert_menu_page(pv, sh)`
   (1600 x 980, row 1 + row 2, at most one sub row, no back / < Menu text inline or in b.set, no pager unless `pager_ok=True`, content
   fits). The harness: build the real page and run `assert_menu_page` on its commands (SkyyMenu/test_skyymenu_0.3.35.py `built()`).
7. Lint: `python tools/ci/lint.py` rule `menu_pattern` (WARN now; `MENU_PATTERN_FAIL = True` after S4 makes it FAIL) - a moved mod
   shows no `old-shell` / `menu-button` / `back-text` line any more.

- **Row 2's art:** a tab draws its `putIcon` icon, else the contract art SkyyMenu ships when its stem is in the bridge key `hub:art`
  (`String[]` of `"<hub>_<tab>"`, put by SkyyMenu 0.3.35+; `HubBar.hasArt`). Without SkyyMenu: words only.
- **Retired contract tabs:** `SUI.HUB_RETIRED` (`settings:layout` - Home's Edit shortcuts button replaces it); `SUI.hub_page_tabs(hub)`
  = what row 2 shows with every mod loaded.
- **Python twins / proofs:** `hub_big_row_preview` (= `bigRowFill`), `hub_big_tabs_preview` (= `bigTabsFill`), `sub_tabs_preview` (=
  `subTab`), `grow_pick` (= `growSize`). `python tools/test_skyyui_hubs.py` phase 5: every hub x sub / footer, the refusals of
  `assert_menu_page`, the BYTE COMPARE of rows 1 + 2 against SkyyMenu 0.3.34's own Home / Teleport row code, and (JVM) `page17` /
  `subTab` / `growSize` / `hasArt` executed against the previews.
- **SkyyCore's shared HubBar** (`hub_bar_java_core`) is still kit 1.5: SkyyCore 1.0.1 needs `row / sub / big / page` there, with the
  owner swaps for the new `mine()` users (`def4`, `putIcon`, `putSub`) - until then a SkyyCore-linked page uses its own jar's HubBar.
- **Not proven in game yet:** the 1600 x 980 hub pages other than Home; row 2 on pages other than Teleport (same markup); the sub-tab row
  (small Primary / Secondary at 150 x 32); a sky footer under a scroll list.
