# SkyWynn hub contract (kit skyyui 1.5, 2026-10-15)

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
