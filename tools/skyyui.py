"""skyyui - the ONE shared vanilla-look UI kit for every Skyy build script (Skyy 2026-09-28: "the new goal for any and all UI added
in the game is for them to look and feel vanilla"; HANDOFF section 2 rule 0).

Contract for builders: research/Vanilla-UI-Style-Guide.md. Vanilla catalogue it is built from: research/Vanilla-UI-Research.md.
Test: python tools/skyyui_test.py (verify() against Assets.zip, every builder, a structural diff of the kit styles against the
expanded Common.ui / Sounds.ui definitions, a javassist compile of the Java output).

What it is: a BUILD-TIME Python module. Every mod has its own classloader and there is no javac, so the kit cannot be a shared jar;
it returns INLINE-READY markup text (appendInline) that a build script drops into its own page code, as a Python string and as a
Java string literal / concatenation for the javassist source. Every style value, texture path and sound path it emits is copied from
the game's own custom-UI documents in Assets.zip (Common/UI/Custom/Common.ui, Sounds.ui and vanilla pages) and verify() proves each
one is still there, verbatim, at every build (a game update that changes one fails the build instead of drifting). The Java emitters
(java_append / java_set / java_expr / java_field, Shell.java) refuse to run before verify() has passed in this process.

    import skyyui as SUI                    # tools/ is already on sys.path (the skyybuild import line). Not "as UI": SkyyRanks and
                                            # SkyyMenu already have a module-level UI = {...}
    SUI.verify()                            # prints "vanilla look checked: N style values, M textures / sounds"; fails loudly
    sh = SUI.page_shell("SkyyBankF", 1100, 860, body_id="SkyyBank", title="Bank")   # old root id becomes the body: old appends work
    SRC = sh.java("b")                      # Java statements: the root, title bar, body, decorations (+ b.set of the title)
    OK  = SUI.button("SkyyBDeposit", "Deposit", kind="primary", w=200)             # one TextButton, all states + vanilla sounds
    ROW = SUI.panel_row("SkyyBRow" + SUI.J("i"), state="normal")                   # J(expr) = a runtime Java value
    java = SUI.java_expr(ROW)               # "Group #SkyyBRow" + (i) + " { ... }"   (SUI.java_lit for static text)

Rules the kit enforces (HANDOFF section 2): element ids letters + digits only (an underscore raises, also in Java selectors),
no duplicate static ids on a page, inline Text only [A-Za-z0-9 <>/-] (anything else goes through b.set: Appends.text / Shell.text
do that split for you), page roots Anchor Width / Height only, pages fit a 1080 px screen, no document variables (@X / $C) inline,
every texture / sound path is one the kit verifies, WrapMaxLines only together with Wrap: true.
Elements nobody has seen work inline yet need trial=True (UNVERIFIED below); probe_pages() builds one in-game test page per
UNVERIFIED feature (plus three "base" pages for the core look: 1, 2 and 18) - add a feature to PROBED once Skyy has seen its page
work in game. Each probe page has a stable name (probe_page("checkbox")) and shows its own numbered "what to see" list.
ItemGrid slots: the kit builds the grid (item_grid) and the only Java that fills it (java_grid_methods / java_grid_fill: every slot
is new ItemGridSlot(new ItemStack(id, qty)) - never a stack you hold, whose metadata disconnects the client). Kept out on purpose:
the full-screen @PageOverlay dim and the bottom-left BackButton (Skyy page roots are Width / Height only; Esc + a footer Close do it), the
client-only textures (Pages/Inventory/Slot.png, the client's own tooltip frame, the settings CheckBox toggle), the broken vanilla
styles (@SmallDefaultTextButtonStyle -> Common/ButtonSmall*.png is missing, @ButtonDestructiveSounds -> an undefined sound set).
The item QUALITY frames (Common/UI/ItemQualities/Slots|Tooltips/*.png) ARE in Assets.zip, outside the custom root: only their
inline path "../ItemQualities/..." is unverified (quality_frame / tooltip_panel(quality=), trial=True).
Kit 1.4 is ADDITIVE: every kit 1.3 builder output is frozen (the test's SNAP13 snapshot); the new blocks (static_row, list_well,
result_line, stat_bar, column_spec, stat_well, list_card, state_word, ...: the "kit 1.4 blocks" section) are made from proven
properties only, assert_proven() checks a page against ONE table of proven properties minus PROBED, text_width() measures with the
client's own font tables (button() / label() warn when a static text does not fit), and probe pages 19-22 come after page 18.
"""
import os, re, json, zipfile, hashlib, posixpath

KIT_VERSION = "1.4"   # 1.2 (2026-09-29, SkyyBank 0.1.4 pilot): + group(), status_line(wrap=, max_lines=, anchor=)
# 1.3 (2026-09-29, the SkyyBank pilot review): titles without LetterSpacing 0 (= the deployed SkyyRanks / SkyyVault titles),
#     WrapMaxLines only with Wrap: true (max_lines=False / 0 = none), display = 32 px Default font (Hud/TimeLeft), STATUS "=" =
#     info blue #7caacc (gold: java_status_methods(info="gold")); + pager, item_grid + java_grid_methods / java_grid_fill,
#     icon_cell, Appends.text / Shell.text (punctuated text -> b.set), confirm_view, choose (a markup picked at runtime),
#     probe pages with stable names + their own "what to see" list (+ base page 18 for the 1.3 builders)
# 1.4 (2026-09-29, the stage-1b restyle reviews) - ADDITIVE ONLY: every kit 1.3 builder output is byte-identical (the test's
#     SNAP13 snapshot), only new functions / parameters (defaults keep the old output) / table entries at the end / probe pages
#     after 18. New: Markup (a markup str carrying .h / .w / .sets / .ids), static_row, status_bar / row_bar, list_well,
#     result_line + java_color_by_text, stat_bar (a choose()-ready full / empty pair), column_spec / Columns / column_heads /
#     column_row, right_margin / centre_margin + button_row(used=, avail=, left_margin=), stat_well, list_card (+ LIST_CARD_*
#     = the Classes / Profiles SKYY CARD, byte for byte), state_word, color_by, group(bg=) / panel(bg=), item_frame(item=,
#     cover=), icon_cell(state="static"), confirm_view(wrap=, yes_on=, q_col=), Appends.add / Appends.button / java_add,
#     outer_size / used_height / used_width, text_width / text_lines / line_height (the client's font tables) + fit warnings in
#     button() / label() / Appends.text, assert_proven (one table of proven properties minus PROBED), Probe.summary +
#     Probe.with_footer, probe pages 19-22 (base4, button-text, flex-rows, layout-right)

# ================================================================= where the game files are (READ-ONLY; never written)
_HYTALE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
GAME_DIR = os.path.join(_HYTALE, "install", "release", "package", "game", "latest")
ASSETS_ZIP = os.path.join(GAME_DIR, "Assets.zip")
CLIENT_UI_DIR = os.path.join(GAME_DIR, "Client", "Data", "Game", "Interface")   # optional reference checks (client-only look)
CUSTOM = "Common/" + "UI/Custom/"          # the custom-UI root inside Assets.zip; inline paths are relative to it

# vanilla documents the kit copies from (key -> path under CUSTOM, without the extension)
DOCS = {
    "C": "Common", "S": "Sounds",
    "W": "Pages/WorldEvent/WorldEventListRow", "L": "Pages/WorldEvent/WorldEventSectionLabel",
    "W2": "Pages/WorldEvent/WorldEventPanelPage", "PR": "Pages/WorldEvent/WorldEventPropertyRow",
    "SR": "Pages/WorldEvent/WorldEventSummaryRow", "WN": "Pages/WorldEvent/WorldEventNavButton",
    "E": "Pages/PrefabSavePage", "M": "Pages/Memories/MemoriesCategory", "P": "Pages/PrefabEditorExitConfirm",
    "MM": "Pages/Memories/Memory", "MC": "Pages/Memories/MemoriesCategoryPanel",
    "R": "Pages/ItemRepairElement", "I": "Pages/ItemRepairPage", "B": "Pages/BarterTradeRow", "BP": "Pages/BarterPage",
    "O": "Pages/OverrideRespawnPointButton", "A": "Pages/BasicTextButton", "N": "Pages/NameRespawnPointPage",
    "G": "Pages/UIGallery/Categories/ProgressContent", "T": "Pages/UIGallery/Categories/TooltipsContent",
    "CB": "Pages/UIGallery/CategoryButton", "RS": "Pages/RespawnPage", "ES": "Pages/EntitySpawnPage",
    "PD": "Pages/PortalDeviceActive", "PS": "Pages/PortalDeviceSummon", "PI": "Pages/Point/PointInspectorPage",
    "LP": "Pages/LaunchPadSettingsPage", "CL": "Pages/CommandListPage", "TV": "Pages/TriggerVolume/TriggerVolumeInspectorPage",
    "BS": "Pages/BlockSpawner/BlockSpawnerSpawnerEntryRow", "IL": "Pages/InstanceListPage", "PL": "Pages/PluginListPage",
    "HT": "Hud/TimeLeft",
}
# client in-game UI documents (NOT in Assets.zip; Client/Data/Game/Interface). Checked only when that folder exists.
CLIENT_DOCS = {"CT": "InGame/Tooltips/ItemTooltip", "CS": "Common/Settings/LabeledCheckBoxSetting",
               "CH": "Common/Settings/SectionHeader", "CG": "InGame/Common", "CC": "InGame/Pages/Inventory/BasicCraftingPanel"}

_CHECKS = []        # (document key, exact text that must be in it, what it proves)
_STATE = {"verified": False}


def _need(doc, needle, what=""):
    assert doc in DOCS or doc in CLIENT_DOCS, doc
    if (doc, needle) not in [(d, n) for d, n, _w in _CHECKS]:
        _CHECKS.append((doc, needle, what))


class VanillaCheckError(SystemExit):
    """verify() failed: Assets.zip missing, or a vanilla value the kit copies changed (the build must stop)."""


class UnverifiedError(ValueError):
    """An element nobody has seen work in an inline page yet was used without trial=True."""


class NotVerifiedError(RuntimeError):
    """Java was emitted before verify() passed in this process (the kit promises every value is proven at every build)."""


def require_verified():
    if not _STATE["verified"]:
        raise NotVerifiedError("skyyui: call SUI.verify() once near the top of the build script before emitting any Java "
                               "(java_append / java_set / java_expr / java_field / Shell.java): the kit only emits values proven "
                               "against Assets.zip in this build")


# ================================================================= colours by meaning (vanilla values, each proven by a needle)
COLOR = {}
_COLOR_SRC = {}


def _col(name, value, doc, needle, *more):
    """A kit colour: its value, the needle that proves it on a vanilla page, and optional extra (doc, needle) proofs."""
    COLOR[name] = value
    _COLOR_SRC[name] = (doc, needle)
    _need(doc, needle, "colour " + name)
    for d, n in more:
        _need(d, n, "colour " + name)


# text
_col("text", "#96a9be", "C", "@DefaultLabelStyle = (FontSize: 16, TextColor: #96a9be);")    # default label / hint / body text
_col("white", "#ffffff", "C", "@ColorDefault = #ffffff;")                                   # highlight, input text, values
_col("title", "#b4c8c9", "C", '  TextColor: #b4c8c9,\n  FontName: "Secondary",')            # window title (@TitleStyle)
_col("panelTitle", "#afc2c3", "C", "FontSize: 15, TextColor: #afc2c3")                     # @PanelTitle label
_col("panelLine", "#393426(0.5)", "C", "Background: #393426(0.5);")                         # @PanelTitle underline
_col("section", "#9aacbc", "L", "RenderBold: true, TextColor: #9aacbc")                    # WorldEventSectionLabel
_col("formCaption", "#94a7bb", "N", "Style: (RenderBold: true, RenderUppercase: true, TextColor: #94a7bb);")
# caption / captionLight: the Common.ui variables are UI-Gallery samples, the literal values sit on real pages (CommandListPage
# alias captions, TriggerVolumeInspectorPage empty-state lines)
_col("caption", "#878e9c", "CL", "TextColor: #878e9c,", ("C", "@ColorGrayCaption = #878e9c;"))
_col("captionLight", "#5a6a7a", "TV", "HorizontalAlignment: Center, TextColor: #5a6a7a);", ("C", "@ColorCaptionLight = #5a6a7a;"))
_col("rowName", "#d6e4ee", "W", "Style: (FontSize: 14, RenderBold: true, TextColor: #d6e4ee")
_col("rowSub", "#7f93a6", "W", "Style: (FontSize: 12, TextColor: #7f93a6")
_col("rowBadge", "#9aacbc", "W", "Style: (FontSize: 12, TextColor: #9aacbc, HorizontalAlignment: End")
_col("muted", "#ffffff(0.6)", "R", "Style: (TextColor: #ffffff(0.6));")                     # ItemRepairElement durability
_col("disabled", "#797b7c", "C", "@ColorDisabled = #797b7c;")                               # the disabled button label (real)
# gold: @ColorGoldHighlight is only a UI Gallery sample (TextContent.ui), no real page shows it. Kept for costs and as the named
# alternative "=" colour (STATUS_INFO["gold"], the SkyyRanks 0.1.1 / SkyyGear 0.1 look); the kit's "=" is info #7caacc (kit 1.3).
_col("gold", "#E8A93B", "C", "@ColorGoldHighlight = #E8A93B;")
_col("buttonText", "#bfcdd5", "C", "@ColorButtonText = #bfcdd5;")                           # primary / destructive label
_col("button2Text", "#bdcbd3", "C", "...@DefaultButtonLabelStyle,\n  TextColor: #bdcbd3")    # secondary / tertiary label
_col("placeholder", "#6e7da1", "C", "@DefaultInputFieldPlaceholderStyle = InputFieldStyle(TextColor: #6e7da1);")
_col("searchPlaceholder", "#3d5a85", "C", "@ColorPlaceholder = #3d5a85;")
_col("value", "#b7cedd", "PR", "Style: (FontSize: 13, TextColor: #b7cedd, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);",
     ("W2", "Style: (...$C.@DefaultInputFieldStyle, FontSize: 13, TextColor: #b7cedd);"))   # property values, filter inputs
_col("propKey", "#7a8a9a", "PR", "RenderBold: true, TextColor: #7a8a9a, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);")
_col("summary", "#8fa6ba", "SR", "Style: (FontSize: 13, TextColor: #8fa6ba, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);")
# results / states
_col("error", "#ff6b6b", "E", "Style: (...$C.@DefaultLabelStyle, TextColor: #ff6b6b);")
_col("formError", "#bb3333", "N", "Style: (RenderBold: true, TextColor: #bb3333);")
_col("success", "#39f493", "M", "TextColor: #39f493);")
_col("warning", "#ffcc00", "P", "HorizontalAlignment: Center, FontSize: 32, TextColor: #ffcc00);")
_col("info", "#7caacc", "BP", "TextColor: #7caacc,")
_col("have", "#3d913f", "B", "TextColor: #3d913f,")
_col("outOfStock", "#cc4444", "B", "TextColor: #cc4444,")
_col("stock", "#7a8a9a", "B", "FontSize: 12,\n            TextColor: #7a8a9a,")
# accents / selection (the @ColorBlueAccent* variables are UI Gallery samples; "active" / "activeHover" are BasicTextButton's)
_col("accent", "#7a9cc6", "C", "@ColorBlueAccent = #7a9cc6;")
_col("accentHover", "#96b8e0", "C", "@ColorBlueAccentHovered = #96b8e0;")
_col("accentPressed", "#5a7a9c", "C", "@ColorBlueAccentPressed = #5a7a9c;")
_col("selected", "#4274a5", "W", "Default: (Background: (Color: #4274a5)),")
_col("active", "#7a9cc6(0.25)", "A", "Background: #7a9cc6(0.25)")
_col("activeHover", "#7a9cc6(0.35)", "A", "Background: #7a9cc6(0.35)")
# panels / rows / lines
_col("row", "#101925(0.55)", "W", "Default: (Background: (Color: #101925(0.55))),")
_col("rowHover", "#132033(0.8)", "W", "Hovered: (Background: (Color: #132033(0.8))),")
_col("rowPressed", "#182a40(0.9)", "W", "Pressed: (Background: (Color: #182a40(0.9))),")
_col("hover", "#000000(0.2)", "C", "@ColorSimpleButtonBackground = #000000(0.2);")
_col("well", "#000000(0.15)", "W2", "Background: (Color: #000000(0.15));\n            Padding: (Full: 8);")   # lists / summaries
_col("hud", "#000000(0.2)", "HT", "Background: #000000(0.2);\n    Anchor: (Left: 20);\n    Padding: (Horizontal: 20, Vertical: 10);")
_col("darkBlock", "#000000(0.3)", "RS", "Background: (Color: #000000(0.3));")              # RespawnPage full-screen block only
_col("overlay", "#000000(0.45)", "C", "@PageOverlay = Group {\n  Background: #000000(0.45);")
_col("separator", "#2b3542", "C", "Background: (Color: #2b3542);")
_col("formLine", "#5e512c", "LP", "Anchor: (Vertical: 16, Height: 1);\n        Background: #5e512c;")
_col("footerLine", "#19252F", "BP", "Background: #19252F;")
_col("card", "#252f3a", "B", "Background: #252f3a,")
_col("cardHover", "#c9a050", "B", "Background: #c9a050,")
_col("cardPressed", "#a08040", "B", "Background: #a08040,")
_col("cardDisabled", "#1a1e24", "B", "Background: #1a1e24,")
_col("cardInner", "#1c2835", "B", "Background: #1c2835;")
_col("cardDivider", "#252F3A", "B", "Background: #252F3A;")
_col("cardCaption", "#8a9aaa", "B", "TextColor: #8a9aaa,")
_col("cardOverlay", "#0a0e12(0.75)", "B", "Background: #0a0e12(0.75);")
_col("slotBorder", "#1a2530", "B", "Background: #1a2530;")
_col("slotBorderHave", "#2a5a3a", "B", "Background: #2a5a3a;")
_col("optionName", "#90a2b7", "O", "TextColor: #90a2b7);")
_col("optionDetail", "#8698ad", "O", "TextColor: #8698ad, FontSize: 14);")
_col("optionHover", "#ffffff(0.7)", "O", "Color: #ffffff(0.7)")
_col("optionPressed", "#ffffff(0.85)", "O", "Color: #ffffff(0.85)")
_col("progressTrack", "#1a2030", "C", "Background: #1a2030;")
_col("progressFill", "#aa7c4a", "C", "Color: #aa7c4a;")
_col("progressBlue", "#4a7caa", "G", "Color: #4a7caa;")
_col("progressGreen", "#7caa4a", "G", "Color: #7caa4a;")
_col("checkDisabled", "#424242", "C", "DisabledBackground: (Color: #424242),")
_col("transparent", "#00000000", "C", "DefaultBackground: (Color: #00000000),")
# dropdown / search field internals (@DefaultDropdownBoxStyle, @ClearButtonStyle)
_col("dropHover", "#0a0f17", "C", "HoveredEntryBackground: (Color: #0a0f17),")
_col("dropPressed", "#0f1621", "C", "PressedEntryBackground: (Color: #0f1621),")
_col("dropNoItems", "#b7cedd(0.5)", "C", "NoItemsLabelStyle: (...@DefaultDropdownBoxEntryLabelStyle, TextColor: #b7cedd(0.5)),")
_col("focusLine", "#ffffff(0.4)", "C", "FocusOutlineColor: #ffffff(0.4)")
_col("iconTint", "#ffffff(0.25)", "C", 'Icon: (Texture: (TexturePath: "Common/SearchIcon.png", Color: #ffffff(0.25)), Width: 16, Height: 16, '
     'Offset: 7),')
_col("clearTint", "#ffffff(0.3)", "C", 'Texture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.3)),')
_col("clearHover", "#ffffff(0.5)", "C", 'HoveredTexture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.5)),')
_col("clearPressed", "#ffffff(0.4)", "C", 'PressedTexture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.4)),')
# client-only reference values (item tooltip text, settings rows); proven only when the client folder exists
_col("tipStat", "#bca57a", "CT", "@PrimaryTextColor = #bca57a;")
_col("tipId", "#838383", "CT", "Style: (TextColor: #838383, FontSize: 14, RenderItalics: true);")
_col("tipDesc", "#696969", "CT", "Style: (TextColor: #696969, FontSize: 14, Wrap: true);")
_col("tipLine", "#25262c", "CT", "Background: (Color: #25262c);")
_col("settingOff", "#495972", "CS", "TextColor: #495972, RenderUppercase: true, FontSize: 18, RenderBold: false")

# the three result marks every Skyy status line uses ("+" done, "-" refused, "=" info). "+" / "-" are the vanilla success / error
# (MemoriesCategory #39f493, PrefabSavePage #ff6b6b). "=" is the vanilla info blue #7caacc (BarterPage #RefreshTimer: the info
# colour a real page shows; kit 1.3, SkyyBank pilot review) - the gallery-only gold of SkyyRanks 0.1.1 / SkyyGear 0.1 stays
# available by name: java_status_methods(info="gold"). Change the default HERE only; java_status_methods reads these tables.
STATUS_INFO = {"info": COLOR["info"], "gold": COLOR["gold"]}
STATUS = {"+": COLOR["success"], "-": COLOR["error"], "=": STATUS_INFO["info"]}

# ================================================================= rarity palettes (content colours, kept as they are)
# LOCKED by Skyy 2026-09-25 (research/SkyyGear-Stage1-Spec.md 2.1, SkyyGear 0.1 RARITIES, SkyySacks 0.7.7 BAG_RARITY):
# the Wynn ladder in Wynncraft's Minecraft chat colours. Mythic: Wynn #AA00AA reads ~2.8:1 on the dark panels, so pages use the
# readable #CC66CC (still purple; SkyySacks' choice, adopted by SkyyGear design review 4); RARITY_WYNN keeps the original hexes.
RARITY = {"Normal": "#FFFFFF", "Unique": "#FFFF55", "Rare": "#FF55FF", "Legendary": "#55FFFF", "Fabled": "#FF5555",
          "Mythic": "#CC66CC", "Set": "#55FF55"}
RARITY_WYNN = dict(RARITY, Mythic="#AA00AA")
RARITY_ORDER = ["Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic", "Set"]
# the game's own item qualities (Server/Item/Qualities/<Q>.json; verify() reads each file): text colour, slot frame, tooltip frame
QUALITY = {"Junk": "#c9d2dd", "Common": "#c9d2dd", "Uncommon": "#3e9049", "Rare": "#2770b7", "Epic": "#8b339e",
           "Legendary": "#bb8a2c", "Technical": "#3b7a8f", "Tool": "#269edc", "Developer": "#bb2f2c", "Debug": "#ce1624",
           "Template": "#ce1624"}
QUALITY_SLOT = {"Junk": "Junk", "Common": "Common", "Uncommon": "Uncommon", "Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary",
                "Technical": "Tool", "Tool": "Tool", "Developer": "Developer", "Debug": "Developer", "Template": "Developer"}
QUALITY_TIP = {"Junk": "Junk", "Common": "Common", "Uncommon": "Uncommon", "Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary",
               "Technical": "Technical", "Tool": "Default", "Developer": "Common", "Debug": "Common", "Template": "Technical"}

# ================================================================= fonts, sizes, spacing
FONT_DEFAULT = "Default"          # body text, buttons, inputs (the engine default; never needs to be written)
FONT_SECONDARY = "Secondary"      # window titles (@TitleStyle), big titles (RespawnPage 38 px, PortalDeviceSummon #Title0 24 px),
                                  # tile names (Memories). Big NUMBERS are Default (Hud/TimeLeft timer 32 px: the "display" kind)
FONTS = (FONT_DEFAULT, FONT_SECONDARY)

TITLE_H = 38                      # @TitleHeight (fixed by the ContainerHeader texture: never scale it)
TITLE_PAD_TOP = 7                 # #Title Padding Top
TITLE_LABEL_PAD = 19              # @Title Padding Horizontal
TITLE_SIZE = 15                   # @TitleStyle FontSize
DECO_W, DECO_H, DECO_TOP, DECO_BOTTOM = 236, 11, -12, -6     # ContainerDecorationTop / Bottom (stick out 12 px above, 6 below)
CONTENT_PAD = 17                  # @DecoratedContainer / @Container default content padding (9 + 8): the page_shell default, as on
                                  # the player pages ItemRepairPage, WarpListPage, ShopPage
PAGE_PAD = 16                     # what the (mostly editor) vanilla pages set on #Content (28 pages)
DIALOG_PAD = 20                   # confirm dialogs (PrefabEditorExitConfirm)
FORM_PAD = 24                     # form pages
BTN_H, BTN_SMALL_H, BTN_BIG_H = 44, 32, 48                   # @PrimaryButtonHeight, @SmallButtonHeight, @BigButtonHeight
BTN_PAD, BTN_SMALL_PAD = 24, 16   # @ButtonPadding, the small buttons' Padding Horizontal
BTN_MIN_W = 172                   # @DefaultButtonMinWidth (the default width of a normal / big button)
PRIMARY_MIN_W = 120               # the narrowest Primary a vanilla page uses (PointInspectorPage #SaveNameButton); below 160 the
                                  # texture's two 80 px patch ends overlap, vanilla accepts that
PRIMARY_SMALL_W = 150             # the default width of a small Primary (PrefabEditorExitConfirm Save and exit)
BTN_BORDER = 12                   # @ButtonBorder
FIELD_H, FIELD_PAD, INPUT_BORDER = 38, 10, 16                # @TextField
FILTER_H, FILTER_PAD = 28, 6      # the compact filter field (WorldEventPanelPage #FilterField)
SEARCH_H, SEARCH_PAD_LEFT = 30, 28                           # @DefaultDropdownBoxStyle SearchInputStyle
ROW_H, ROW_GAP, ROW_ACTION_W = 42, 3, 92                     # WorldEventListRow (vanilla sizes)
ROW_H_READABLE = 56               # a panel row that holds the readable 18 + 15 px text lines
OPTION_ROW_H, OPTION_ROW_GAP = 50, 4                         # OverrideRespawnPointButton
SETTING_ROW_H, SETTING_ROW_GAP = 44, 8                       # client settings rows (LabeledCheckBoxSetting)
PROP_ROW_H, PROP_ROW_GAP, PROP_KEY_W = 20, 2, 150            # WorldEventPropertyRow
CHECK_SIZE, CHECK_LABEL_W, CHECK_ROW_GAP = 22, 220, 12       # @CheckBox, PrefabSavePage @InputLabel + its check rows
TAB_GAP, TAB_MARGIN = 5, 10       # EntitySpawnPage tab row: 5 px spacers, Top / Bottom 10
WELL_PAD, WELL_LIST_PAD = 8, 4    # the #000000(0.15) well: summary box padding 8, list container padding 4 (WorldEventPanelPage)
SEP_MARGIN, FORM_LINE_MARGIN = 8, 16                         # ContentSeparator Top / Bottom 8 (WorldEventPanelPage), form line 16
SCROLL_SIZE, SCROLL_SPACING = 6, 6                           # @DefaultScrollbarStyle
CONFIRM_W = 620                   # PrefabEditorExitConfirm
PROGRESS_W, PROGRESS_H = 284, 6   # @ProgressBar
MEMBAR_H, MEMBAR_PAD, MEMBAR_W = 22, 6, 600                  # MemoriesCategoryPanel bar (vanilla width 1018)
DROPDOWN_W, DROPDOWN_H = 330, 32  # @DropdownBox
SPINNER = 32                      # @DefaultSpinner
TILE_W, TILE_H, TILE_GAP, TILE_BORDER = 144, 176, 16, 8      # Memories tiles
TOOLTIP_MAX_W, TOOLTIP_PAD, TOOLTIP_BORDER = 400, 24, 24     # @DefaultTextTooltipStyle
CLOSE_SIZE = 32                   # the container close X
SLOT_FRAME, SLOT_ICON = 68, 64    # BarterTradeRow output slot border group / icon
CARD_W, CARD_H, CARD_MARGIN = 230, 185, 5                    # BarterTradeRow
ICON = 32                         # ItemRepairElement icon
MAX_PAGE_H = 980                  # page root height ceiling: + 18 px of decorations it still fits 1080 with the client's margins
MAX_PAGE_W = 1600
MIN_PAGE_W = 300                  # the 236 px decorations + the header's 50 px patch ends

for _n, _t in (("TITLE_H", "@TitleHeight = 38;"), ("TITLE_PAD_TOP", "Padding: (Top: 7);"),
               ("TITLE_LABEL_PAD", "Padding: (Horizontal: 19);"), ("DECO_TOP", "Anchor: (Width: 236, Height: 11, Top: -12);"),
               ("DECO_BOTTOM", "Anchor: (Width: 236, Height: 11, Bottom: -6);"),
               ("CONTENT_PAD", "@ContentPadding = Padding(Full: 9 + 8);"), ("BTN_BORDER", "@ButtonBorder = 12;"),
               ("CONTENT_PAD plain", "@FullPaddingValue = @InnerPaddingValue + 9;"),
               ("BTN_H", "@PrimaryButtonHeight = 44;"), ("BTN_SMALL_H", "@SmallButtonHeight = 32;"),
               ("BTN_BIG_H", "@BigButtonHeight = 48;"), ("BTN_PAD", "@ButtonPadding = 24;"),
               ("BTN_SMALL_PAD", "Padding: (Horizontal: 16);"), ("BTN_MIN_W", "@DefaultButtonMinWidth = 172;"),
               ("FIELD_H", "  Anchor: (...@Anchor, Height: 38);\n  Padding: (Horizontal: 10);"),
               ("CLOSE_SIZE", "Anchor: (Width: 32, Height: 32, Top: -8, Right: -8);"),
               ("PROGRESS", "Anchor: (...@Anchor, Width: 284, Height: 6);"),
               ("DROPDOWN", "Anchor: (...@Anchor, Width: 330, Height: @DropdownBoxHeight);"),
               ("DROPDOWN_H", "@DropdownBoxHeight = 32;"),
               ("SEARCH", "    Anchor: (Height: 30),\n    Padding: (Left: 28),")):
    _need("C", _t, "size " + _n)
_need("C", "@TitleStyle = LabelStyle(\n  FontSize: 15,", "size TITLE_SIZE")
_need("P", "Anchor: (Width: 620);", "size CONFIRM_W")
_need("P", "Padding: (Full: 20);", "size DIALOG_PAD")
_need("P", "@Anchor = (Width: 150, Right: 6);", "size PRIMARY_SMALL_W")
_need("PI", "@Anchor = (Width: 120);", "size PRIMARY_MIN_W (#SaveNameButton, a $C.@TextButton)")
_need("W", "Anchor: (Height: 42, Bottom: 3);", "size ROW_H")
_need("W", "$C.@SmallSecondaryTextButton #ActionA {\n    Anchor: (Width: 92, Height: 42, Left: 4);", "size ROW_ACTION_W")
_need("O", "Anchor: (Height: 50, Bottom: 4);", "size OPTION_ROW_H")
_need("B", "Anchor: (Width: 68, Height: 68);", "size SLOT_FRAME")
_need("R", "Anchor: (Width: 32, Height: 32);", "size ICON")
_need("CS", "Anchor: (Height: 44, Bottom: 8);", "size SETTING_ROW_H")
_need("PR", "LayoutMode: Left;\n  Anchor: (Height: 20, Bottom: 2);", "size PROP_ROW_H")
_need("PR", "Anchor: (Width: 150, Right: 8);", "size PROP_KEY_W")
_need("E", "@InputLabel = Label {\n  Anchor: (Left: 6, Right: 16, Width: 220);\n  Style: (...$C.@DefaultLabelStyle, VerticalAlignment: Center);",
      "size CHECK_LABEL_W")
_need("E", "Group #Entities {\n        LayoutMode: Left;\n        Anchor: (Bottom: 12);", "size CHECK_ROW_GAP")
_need("ES", "Anchor: (Top: 10, Bottom: 10);\n\n      $C.@SecondaryTextButton #TabNPC {\n        Text: %server.customUI.entitySpawnPage.tab.npc;\n"
      "        FlexWeight: 1;", "tab row: margins 10, flex-width Secondary tabs")
_need("ES", "Group {\n        Anchor: (Width: 5);\n      }", "size TAB_GAP")
_need("W2", "Background: (Color: #000000(0.15));\n              Padding: (Full: 4);", "size WELL_LIST_PAD")
_need("W2", "$C.@ContentSeparator {\n        @Anchor = (Top: 8, Bottom: 8);", "size SEP_MARGIN")
_need("MC", 'Background: "MemoriesProgress/MemoriesBarBg.png";\n          Anchor: (Height: 22, Width: @progressBarWidth, Bottom: 30);\n'
      "          Padding: (Full: 6);", "size MEMBAR")
_need("MM", "Anchor: (Width: 144, Height: 176, Right: 16, Bottom: 16);", "size TILE")
_need("B", "Anchor: (Width: 230, Height: 185);\n  Padding: (Horizontal: 5, Vertical: 5);", "size CARD + CARD_MARGIN")

# ---- text sizes: vanilla is small (12 / 13 / 14 px lines); Skyy's rule is BIG readable pages. "readable" (default) scales ONLY the
# small line sizes the way SkyyRanks 0.1.1 did (row name 14 -> 18, caption 12 -> 15, section 13 -> 16); titles (15), labels (16)
# and button labels (17 / 14) always stay vanilla. text_scale("vanilla") switches every kit label back to the exact vanilla size.
READABLE = {11: 14, 12: 15, 13: 16, 14: 18}
_SCALE = ["readable"]


def text_scale(mode=None):
    """Get (no argument) or set ("readable" | "vanilla") the kit's small-text scale; returns the current mode."""
    if mode is not None:
        if mode not in ("readable", "vanilla"):
            raise ValueError("text_scale is 'readable' or 'vanilla', not %r" % (mode,))
        _SCALE[0] = mode
    return _SCALE[0]


def fs(vanilla_size):
    """The kit font size for a vanilla label size (see text_scale)."""
    return READABLE.get(vanilla_size, vanilla_size) if _SCALE[0] == "readable" else vanilla_size


# ================================================================= texture and sound paths (inline form: relative to CUSTOM, no @2x)
TEX = {
    "header": "Common/ContainerHeader.png", "headerPlain": "Common/ContainerHeaderNoRunes.png",
    "decoTop": "Common/ContainerDecorationTop.png", "decoBottom": "Common/ContainerDecorationBottom.png",
    "patch": "Common/ContainerPatch.png", "fullPatch": "Common/ContainerFullPatch.png",
    "panelPatch": "Common/ContainerPanelPatch.png", "secondaryPanel": "Common/ContainerBackgroundSecondary.png",
    "close": "Common/ContainerCloseButton.png", "closeHovered": "Common/ContainerCloseButtonHovered.png",
    "closePressed": "Common/ContainerCloseButtonPressed.png",
    "vsep": "Common/ContainerVerticalSeparator.png", "fancyLine": "Common/ContainerPanelSeparatorFancyLine.png",
    "fancyDeco": "Common/ContainerPanelSeparatorFancyDecoration.png", "headerSep": "Common/HeaderTabSeparator.png",
    "input": "Common/InputBox.png", "inputSelected": "Common/InputBoxSelected.png", "option": "Common/OptionBackgroundPatch.png",
    "scroll": "Common/Scrollbar.png", "scrollHandle": "Common/ScrollbarHandle.png",
    "scrollHandleHovered": "Common/ScrollbarHandleHovered.png", "scrollHandleDragged": "Common/ScrollbarHandleDragged.png",
    "tooltip": "Common/TooltipDefaultBackground.png",
    "progress": "Common/ProgressBar.png", "progressFill": "Common/ProgressBarFill.png", "progressEffect": "Common/ProgressBarEffect.png",
    "checkFrame": "Common/CheckBoxFrame.png", "checkmark": "Common/Checkmark.png",
    "slot": "Common/BlockSelectorSlotBackground.png", "textGradient": "Common/TextGradient.png",
    "dropdown": "Common/Dropdown.png", "dropdownHovered": "Common/DropdownHovered.png", "dropdownPressed": "Common/DropdownPressed.png",
    "dropdownCaret": "Common/DropdownCaret.png", "dropdownPressedCaret": "Common/DropdownPressedCaret.png",
    "dropdownPanel": "Common/DropdownBox.png", "searchIcon": "Common/SearchIcon.png", "clearIcon": "Common/ClearInputIcon.png",
    "spinner": "Common/Spinner.png",
    "tileDefault": "Pages/Memories/Tiles/TileDefault.png", "tileHovered": "Pages/Memories/Tiles/TileHovered.png",
    "tileSelected": "Pages/Memories/Tiles/TileSelected.png", "tileComplete": "Pages/Memories/Tiles/TileComplete.png",
    "tileEmpty": "Pages/Memories/Tiles/TileEmpty.png",
    "memBarBg": "Pages/Memories/MemoriesProgress/MemoriesBarBg.png", "memBarFill": "Pages/Memories/MemoriesProgress/MemoriesBarFill.png",
    "memBarTip": "Pages/Memories/MemoriesProgress/MemoriesBarTipOfTheBar.png",
    "memBarTexture": "Pages/Memories/MemoriesProgress/MemoriesBarTexture.png",
}
for _fam in ("Primary", "Secondary", "Tertiary", "Destructive"):
    for _st in ("", "_Hovered", "_Pressed"):
        TEX["btn" + _fam + _st.replace("_", "")] = "Common/Buttons/%s%s.png" % (_fam, _st)
TEX["btnTertiaryActive"] = "Common/Buttons/Tertiary_Active.png"
TEX["btnDisabled"] = "Common/Buttons/Disabled.png"
# the item quality frames: Common/UI/ItemQualities, OUTSIDE the custom root (the quality JSONs name them as SlotTexture /
# ItemTooltipTexture). In Assets.zip for sure; the "../" inline path is UNVERIFIED (quality-frame).
for _q in sorted(set(QUALITY_SLOT.values()) | {"Default"}):
    TEX["qSlot" + _q] = "../ItemQualities/Slots/Slot%s.png" % _q
for _q in sorted(set(QUALITY_TIP.values())):
    TEX["qTip" + _q] = "../ItemQualities/Tooltips/ItemTooltip%s.png" % _q
    TEX["qTipArrow" + _q] = "../ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _q

SND = {"lightActivate": "Sounds/ButtonsLightActivate.ogg", "lightHover": "Sounds/ButtonsLightHover.ogg",
       "cancelActivate": "Sounds/ButtonsCancelActivate.ogg", "save": "Sounds/SaveActivate.ogg",
       "mainActivate": "Sounds/ButtonsMainActivate.ogg", "mainHover": "Sounds/ButtonsMainHover.ogg",
       "tick": "Sounds/TickActivate.ogg", "untick": "Sounds/UntickActivate.ogg",
       "lock": "Sounds/LockActivate.ogg", "unlock": "Sounds/UnlockActivate.ogg"}
for _k, _needle in (("lightActivate", '@ButtonsLightActivate = "Sounds/ButtonsLightActivate.ogg";'),
                    ("lightHover", '@ButtonsLightHover = "Sounds/ButtonsLightHover.ogg";'),
                    ("cancelActivate", '@ButtonsCancelActivate = "Sounds/ButtonsCancelActivate.ogg";'),
                    ("save", '@SaveActivate = "Sounds/SaveActivate.ogg";'),
                    ("mainActivate", '@ButtonsMainActivate = "Sounds/ButtonsMainActivate.ogg";'),
                    ("mainHover", '@ButtonsMainHover = "Sounds/ButtonsMainHover.ogg";'),
                    ("tick", '@Tick = "Sounds/TickActivate.ogg";'), ("untick", '@Untick = "Sounds/UntickActivate.ogg";'),
                    ("lock", 'SoundPath: "Sounds/LockActivate.ogg",'), ("unlock", 'SoundPath: "Sounds/UnlockActivate.ogg",')):
    _need("S", _needle, "sound path " + _k)

# the vanilla sound SETS (Sounds.ui), spelled out for inline use. Vanilla merges every button's own set OVER @ButtonsLight (Common.ui
# @TextButton: Sounds: (...$Sounds.@ButtonsLight, ...@Sounds)), so a set that defines only Activate (lock / unlock) keeps the light
# hover: the kit spells out that merged result. "main" is the main-menu set (no server page uses it); lock / unlock neither.
_HOVER = '(SoundPath: "%s", Volume: 6)' % SND["lightHover"]
SOUNDS = {
    "light": '(Activate: (SoundPath: "%s", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), MouseHover: %s)' % (SND["lightActivate"], _HOVER),
    "cancel": '(Activate: (SoundPath: "%s", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6), MouseHover: %s)' % (SND["cancelActivate"], _HOVER),
    "save": '(Activate: (SoundPath: "%s", Volume: 6), MouseHover: %s)' % (SND["save"], _HOVER),
    "main": ('(Activate: (SoundPath: "%s", Volume: 6), MouseHover: (SoundPath: "%s", MinPitch: -0.1, MaxPitch: 0.1, Volume: 2))'
             % (SND["mainActivate"], SND["mainHover"])),
    "lock": '(Activate: (SoundPath: "%s", Volume: 6), MouseHover: %s)' % (SND["lock"], _HOVER),
    "unlock": '(Activate: (SoundPath: "%s", Volume: 6), MouseHover: %s)' % (SND["unlock"], _HOVER),
}
# the DropdownBoxSounds set (@DropdownBox in Sounds.ui): open = Tick, hover = light hover, close = cancel
DROPDOWN_SOUNDS = ('(Activate: (SoundPath: "%s", Volume: 6), MouseHover: %s, Close: (SoundPath: "%s", Volume: 6))'
                   % (SND["tick"], _HOVER, SND["cancelActivate"]))
_need("S", "@ButtonsLight = (\n  Activate: (\n    SoundPath: @ButtonsLightActivate,\n    MinPitch: -0.4,\n    MaxPitch: 0.4,\n"
      "    Volume: 4\n  ),\n  MouseHover: (\n    SoundPath: @ButtonsLightHover,\n    Volume: 6\n  )\n);", "sound set light")
_need("S", "@ButtonsCancel = (\n  Activate: (\n    SoundPath: @ButtonsCancelActivate,\n    MinPitch: -0.4,\n    MaxPitch: 0.4,\n"
      "    Volume: 6\n  ),\n  MouseHover: (\n    SoundPath: @ButtonsLightHover,\n    Volume: 6\n  )\n);", "sound set cancel")
_need("S", "@SaveSettings = (\n  Activate: (\n    SoundPath: @SaveActivate,\n    Volume: 6\n  ),\n  MouseHover: (\n"
      "    SoundPath: @ButtonsLightHover,\n    Volume: 6\n  )\n);", "sound set save")
_need("S", "@ButtonsMain = (\n  Activate: (\n    SoundPath: @ButtonsMainActivate,\n    Volume: 6\n  ),\n  MouseHover: (\n"
      "    SoundPath: @ButtonsMainHover,\n    MinPitch: -0.1,\n    MaxPitch: 0.1,\n    Volume: 2\n  )\n);", "sound set main")
_need("S", '@Lock = (\n  Activate: (\n    SoundPath: "Sounds/LockActivate.ogg",\n    Volume: 6\n  )\n);', "sound set lock")
_need("S", '@Unlock = (\n  Activate: (\n    SoundPath: "Sounds/UnlockActivate.ogg",\n    Volume: 6\n  )\n);', "sound set unlock")
_need("S", "@DropdownBox = DropdownBoxSounds(\n  Activate: (\n    SoundPath: @Tick,\n    Volume: 6\n  ),\n  MouseHover: (\n"
      "    SoundPath: @ButtonsLightHover,\n    Volume: 6\n  ),\n  Close: (\n    SoundPath: @ButtonsCancelActivate,\n    Volume: 6\n  )",
      "sound set dropdown")
_need("C", "@ButtonSounds = $Sounds.@ButtonsLight;", "buttons use @ButtonsLight")
_need("C", "  Style: (\n    ...@DefaultTextButtonStyle,\n    Sounds: (\n      ...$Sounds.@ButtonsLight,\n      ...@Sounds\n    )\n  );",
      "a button's own sounds merge over @ButtonsLight")
_need("C", "  Sounds: @ButtonsCancel,\n);", "the cancel / destructive style uses @ButtonsCancel")
_need("P", "@Sounds = $Sounds.@SaveSettings;", "confirm main button = SaveSettings")
_need("P", "@Sounds = $Sounds.@ButtonsCancel;", "confirm cancel button = ButtonsCancel")
_need("W2", "$C.@SecondaryTextButton #CloseButton {\n          @Sounds = $Sounds.@ButtonsCancel;", "footer Close = Secondary + ButtonsCancel")

# ================================================================= features not yet seen working inline (trial=True to use them)
UNVERIFIED = {
    "base": "the kit's core look inline: frame + ornaments + close X, button textures / states / inline Sounds / Disabled look, "
            "FlexWeight, LayoutMode Full / Right, LetterSpacing, WrapMaxLines, ShrinkTextToFit, the well, and the kit 1.3 "
            "builders made from them (pager, item_grid, icon_cell, confirm_view) (probe pages 1, 2 and 18; no trial gate - the "
            "first restyle waits for these pages)",
    "itemslot": "the ItemSlot element with ShowQualityBackground + #Id.ItemId (vanilla BarterTradeRow) inline",
    "disabled-prop": "Disabled: true on an inline TextButton (the style's Disabled state + clicks stop)",
    "tooltip": "TooltipText + TextTooltipStyle on an inline element (also test Esc with a tooltip open)",
    "progress-element": "the vanilla ProgressBar element inline (b.set #Id.Value as a float)",
    "memories-bar": "the textured Memories progress bar (Pages/Memories/MemoriesProgress/*.png) inline",
    "checkbox": "the CheckBox element inline (its change is a ValueChanged binding, not Activating)",
    "slot-background": "SlotBackground (BlockSelectorSlotBackground) in an inline ItemGrid style",
    "text-mask": "MaskTexturePath / LabelMaskTexturePath (TextGradient) on an inline Label / TextButton",
    "number-field": "the NumberField element inline",
    "value-ref": 'b.set("#Id.Style", Value.ref("Common.ui", "<StyleName>")) on an element built by appendInline',
    "dropdown": "the DropdownBox element + an inline DropdownBoxStyle (entries set from Java; ValueChanged binding)",
    "search-field": "a TextField with the vanilla search Decoration (SearchIcon + ClearButtonStyle) inline",
    "spinner": "the Sprite element (Common/Spinner.png, 72 frames at 30 fps) inline",
    "tile": "the Memories tile textures (Pages/Memories/Tiles/*.png) on an inline TextButton",
    "quality-frame": 'the item quality frames outside the custom root ("../ItemQualities/Slots|Tooltips/...png") from inline markup',
    # kit 1.4 (appended; the 1.3 keys above are unchanged)
    "base4": "the kit 1.4 builders, made from proven properties only (static_row, status_bar, list_well, result_line, stat_bar, "
             "column_heads / column_row, button_row(used=), stat_well, list_card, state_word, item_frame(item=, cover=), "
             "icon_cell static, confirm_view compact wrap / yes_on) (probe page 19; no trial gate - a restyle on them waits for it)",
    "button-text": 'b.set("#Id.Text", ...) on a TextButton: a button label with punctuation or a runtime value (Appends.button)',
    "flex-rows": "FlexWeight on its own: equal flex buttons, a flex label next to a fixed button, a flex spacer, a flex filler in a "
                 "column, the panel_row select button (probe page 21; FlexWeight is also on base1 / base2)",
    "layout-right": "LayoutMode Right on its own: a right-aligned footer, a row of cells and labels (probe page 22; also on base1)",
}
PROBED = set()      # add a key here once Skyy has seen its probe page work in game; it then needs no trial=True


def _gate(feature, trial):
    if feature in PROBED or trial:
        return
    raise UnverifiedError("%s is UNVERIFIED in game (%s). Pass trial=True to use it on a page that is tested in game first "
                          "(SUI.probe_pages()), then add %r to skyyui.PROBED." % (feature, UNVERIFIED[feature], feature))


# ================================================================= runtime values inside markup: J(expr) -> Java concatenation
_JS, _JM, _JE = "\x01", "\x03", "\x02"
_J_RE = re.compile("\x01([^\x01\x02\x03]+)\x03([^\x01\x02\x03]*)\x02")
_DYN = "Qjq"        # stands in front of a J() sample when ids are collected (an id holding it is runtime: never a duplicate)


def J(expr, sample="0"):
    """A runtime Java value inside markup (an id suffix, a width, a colour...). `sample` stands in for it in checks and previews:
    digits for ids and numbers, a #rrggbb for colours. java_expr() turns it into `" + (expr) + "`. Never use it inside Text."""
    expr, sample = str(expr).strip(), str(sample)
    if not expr or any(c in expr + sample for c in _JS + _JM + _JE) or '"' in sample:
        raise ValueError("J(): bad expression / sample %r / %r" % (expr, sample))
    return _JS + expr + _JM + sample + _JE


def has_j(s):
    return isinstance(s, str) and _JS in s


def render(s, mark=False):
    """The markup with every J() replaced by its sample (a preview / what the checks read); mark=True prefixes each sample with
    the runtime marker (for telling runtime ids from static ones)."""
    out = _J_RE.sub(lambda m: (_DYN if mark else "") + m.group(2), s)
    if any(c in out for c in _JS + _JM + _JE):
        raise ValueError("broken J() marker in markup")
    return out


def _sample_num(v):
    """The number an int / float / J() value stands for in checks (J: its sample), or None when it is not a number."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    if has_j(v):
        try:
            return float(render(v))
        except ValueError:
            return None
    return None


# ================================================================= Java emission (javassist source)
def java_escape(s):
    """The inside of a Java string literal (no quotes): \\ " and newlines escaped. Refuses J() markers (use java_expr)."""
    if any(c in s for c in _JS + _JM + _JE):
        raise ValueError("java_lit / java_escape got a J() runtime value - use java_expr()")
    for c in s:
        if ord(c) < 32 and c not in "\n\r\t":
            raise ValueError("control character %r in a Java literal" % c)
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def java_lit(s):
    """A Java string literal for static text: "..." (javassist reads the characters as they are; only \\ " \\n \\r \\t escaped)."""
    return '"' + java_escape(s) + '"'


def java_unlit(lit):
    """The Python text of a Java string literal made by java_lit (for tests)."""
    if len(lit) < 2 or lit[0] != '"' or lit[-1] != '"':
        raise ValueError("not a Java string literal: %r" % lit[:40])
    out, i, body = [], 0, lit[1:-1]
    esc = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t", "'": "'"}
    while i < len(body):
        c = body[i]
        if c == "\\":
            i += 1
            if i >= len(body) or body[i] not in esc:
                raise ValueError("bad escape in %r" % lit[:60])
            out.append(esc[body[i]])
        elif c == '"':
            raise ValueError("unescaped quote in %r" % lit[:60])
        else:
            out.append(c)
        i += 1
    return "".join(out)


def _java_expr(s):
    parts, pos = [], 0
    for m in _J_RE.finditer(s):
        if m.start() > pos:
            parts.append(java_lit(s[pos:m.start()]))
        parts.append("(" + m.group(1) + ")")
        pos = m.end()
    if pos < len(s):
        parts.append(java_lit(s[pos:]))
    if not parts:
        return '""'
    if not parts[0].startswith('"'):
        parts.insert(0, '""')
    return " + ".join(parts)


def java_expr(s):
    """A Java String expression for markup that may hold J() values: "static" + (expr) + "static" (starts with "" when the first
    part is a value, so two numbers are never added)."""
    require_verified()
    return _java_expr(s)


def java_value(v):
    """java_expr for a str (J() allowed), or the literal of a plain str."""
    return _java_expr(v) if has_j(v) else java_lit(v)


def java_field(name, s):
    """`public static final String NAME = "...";` for a static markup constant (CtField.make(text, cls))."""
    require_verified()
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name):
        raise ValueError("not a Java field name: %r" % (name,))
    return "public static final String %s = %s;" % (name, java_lit(s))


def emit_fields(cls, consts, CtField):
    """Add every {NAME: markup} as a public static final String field to a javassist CtClass."""
    for k in consts:
        cls.addField(CtField.make(java_field(k, consts[k]), cls))
    return len(consts)


def for_fstring(s):
    """Double the braces so a markup / Java text survives being put inside a Python f-string or str.format template."""
    return s.replace("{", "{{").replace("}", "}}")


def for_pysource(s, raw=False, fstring=True, quote='"""'):
    """Kit output made safe to paste INTO Python source text (a patch script writing a build script): braces doubled for an
    f-string / .format template (fstring=True), backslashes doubled unless the template is a raw string (raw=True: rf\"\"\"...),
    and it refuses text that would end the template's quotes (quote). Interpolating {SUI.java_lit(x)} at run time needs none of this."""
    out = for_fstring(s) if fstring else s
    if not raw:
        out = out.replace("\\", "\\\\")
    elif out.endswith("\\"):
        raise ValueError("for_pysource: a raw string cannot end with a backslash")
    if quote and (quote in out or out.endswith(quote[0])):
        raise ValueError("for_pysource: the text holds / ends with the template quote %r" % quote)
    return out


def for_percent(s):
    """Double the percent signs so a text survives Python % formatting."""
    return s.replace("%", "%%")


def _sel(ident):
    """'#Id' for a selector id (a leading # optional); the id is checked (letters + digits, J() suffixes allowed)."""
    if not isinstance(ident, str):
        raise ValueError("selector id must be a str: %r" % (ident,))
    bare = ident[1:] if ident.startswith("#") else ident
    check_id(bare)
    return "#" + bare


class Choice(object):
    """A markup picked at runtime (SUI.choose): the Java appends (cond) ? a : b. Both markups are checked and must create the same
    static element ids (later appends and b.set lines target them either way)."""

    def __init__(self, cond, a, b):
        self.cond, self.a, self.b = cond, a, b

    def variants(self):
        return (self.a, self.b)

    def __repr__(self):
        return "Choice(%r, ...)" % self.cond


def choose(cond, a, b):
    """A markup chosen in the Java at runtime: cond = J("expr") or a plain Java boolean expression str ("pageNo > 0"), a = the
    markup when it is true, b = when false (J() values allowed in both). Use it where a page picks a look by its state (a pager's
    disabled Prev, a selected icon cell); Appends / java_append emit b.appendInline(p, (cond) ? (a) : (b))."""
    if isinstance(cond, str) and has_j(cond):
        m = _J_RE.fullmatch(cond)
        if not m:
            raise ValueError("choose(): cond is one J(expr), not text around it")
        cond = m.group(1)
    if not isinstance(cond, str) or not cond.strip() or ";" in cond or any(ord(c) < 32 for c in cond):
        raise ValueError("choose(): cond must be a Java boolean expression (no ';', one line): %r" % (cond,))
    for mk in (a, b):
        if not isinstance(mk, str):
            raise ValueError("choose(): both variants are markup strings")
    return Choice(cond.strip(), a, b)


def _variants(mk):
    return mk.variants() if isinstance(mk, Choice) else (mk,)


def java_append(parent, markup, b="b", page_root=True):
    """One Java statement: b.appendInline(<parent or (String) null>, <markup>); the markup is check_markup-ed first (a root append
    is checked as a page root: Anchor Width / Height only; page_root=False for a HUD root such as Anchor Full 0). markup may be a
    choose(...) Choice: b.appendInline(p, (cond) ? (a) : (b))."""
    require_verified()
    check_markup(markup, root=(parent is None and page_root))
    p = "(String) null" if parent is None else java_value(_sel(parent))
    if isinstance(markup, Choice):
        return "%s.appendInline(%s, (%s) ? (%s) : (%s));" % (b, p, markup.cond, java_value(markup.a), java_value(markup.b))
    return "%s.appendInline(%s, %s);" % (b, p, java_value(markup))


_PROP_OK = re.compile(r"[A-Za-z][A-Za-z0-9]*")


def _typed(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v) + "f"
    return None


def java_set(ident, prop, value, b="b", raw=False):
    """One Java statement: b.set("#Id.Prop", value). value = a str (J() allowed: a String concatenation, e.g. a Text), a Python
    bool / int / float (a typed Java literal: set(String, boolean / int / float)), or with raw=True exactly one J(expr) emitted as a
    typed Java expression (expr): a ProgressBar Value float, a CheckBox Value boolean, a Visible flag (see java_set_raw)."""
    require_verified()
    if not isinstance(prop, str) or not _PROP_OK.fullmatch(prop):
        raise ValueError("b.set property %r: letters and digits only (Text, Value, Visible, ItemId...)" % (prop,))
    t = _typed(value)
    if t is not None:
        val = t
    elif not isinstance(value, str):
        raise ValueError("java_set value must be a str, bool, int, float or J(): %r" % (value,))
    elif raw:
        m = _J_RE.fullmatch(value)
        if not m:
            raise ValueError("java_set(raw=True) takes exactly one J(expr) as the value")
        val = "(" + m.group(1) + ")"
    else:
        val = java_value(value)
    return "%s.set(%s, %s);" % (b, java_value(_sel(ident) + "." + prop), val)


def java_set_raw(ident, prop, expr, b="b"):
    """b.set("#Id.Prop", (expr)) with a typed Java expression (float / int / boolean / String): java_set(..., raw=True)."""
    return java_set(ident, prop, expr if has_j(expr) else J(expr), b, raw=True)


def java_status_methods(name_color="colorOf", name_text="textOf", info=None):
    """Java source of two static methods (CtNewMethod.make each): the vanilla colour of a result line by its first character
    ("+" success #39f493, "-" error #ff6b6b, "=" STATUS["="] = info #7caacc, else the label colour) and the text without that
    mark. info = the "=" colour by name instead: "gold" (STATUS_INFO: the SkyyRanks 0.1.1 / SkyyGear 0.1 gold) or a COLOR name."""
    eq = STATUS["="] if info is None else (STATUS_INFO[info] if info in STATUS_INFO else color(info))
    if has_j(eq):
        raise ValueError("java_status_methods(info=...) takes a colour name or literal, not a J() runtime value")
    c = ('public static String %s(String res) {\n  if (res == null || res.length() == 0) return "%s";\n  char c = res.charAt(0);\n'
         '  if (c == \'+\') return "%s";\n  if (c == \'-\') return "%s";\n  if (c == \'=\') return "%s";\n  return "%s";\n}'
         % (name_color, COLOR["text"], STATUS["+"], STATUS["-"], eq, COLOR["text"]))
    t = ('public static String %s(String res) {\n  if (res == null) return "";\n'
         '  if (res.length() > 0 && (res.charAt(0) == \'+\' || res.charAt(0) == \'-\' || res.charAt(0) == \'=\')) return res.substring(1);\n'
         '  return res;\n}' % name_text)
    return [c, t]


def java_ref_style(ident, style_name, doc="Common.ui", b="b", trial=False):
    """UNVERIFIED: apply a vanilla style by reference (what vanilla server pages do): b.set("#Id.Style", Value.ref(doc, name))."""
    _gate("value-ref", trial)
    sel = _sel(ident)
    if not isinstance(style_name, str) or not re.fullmatch(r"[A-Za-z]+", style_name):
        raise ValueError("style name: letters only")
    return '%s.set(%s, com.hypixel.hytale.server.core.ui.Value.ref(%s, %s));' % (
        b, java_lit(sel + ".Style"), java_lit(doc), java_lit(style_name))


# ================================================================= validation (the HANDOFF section 2 rules + SkyyRanks' _check_ui)
TEXT_OK = re.compile(r"\A[A-Za-z0-9 <>/-]*\Z")     # the inline Text characters proven on Skyy's client (Menu / Ranks assert it)
_ID_OK = re.compile(r"\A[A-Za-z][A-Za-z0-9]*\Z")
_COLOR_OK = re.compile(r"\A#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*(?:0|1|0?\.\d+|1\.0+)\s*\))?\Z")
# \A ... \Z (never ^ ... $: "$" also accepts a trailing newline) and the kit calls them with fullmatch


def check_id(ident, prefix=None):
    """An element id: letters + digits, starts with a letter, no underscore (HANDOFF section 2 rule 1). J() suffixes allowed."""
    if not isinstance(ident, str) or not ident:
        raise ValueError("element id must be a non-empty str: %r" % (ident,))
    plain = render(ident)
    if "_" in plain:
        raise ValueError("underscore in UI element id #%s - the client cannot resolve ids with underscores (HANDOFF section 2 "
                         "rule 1): use CamelCase like #SkyyBankRow0" % plain)
    if not _ID_OK.fullmatch(plain):
        raise ValueError("element id #%r: letters and digits only, starting with a letter" % plain)
    if prefix and not plain.startswith(prefix):
        raise ValueError("element id #%s must start with the page prefix %s" % (plain, prefix))
    return ident


def check_text(text, what="Text"):
    """Static inline text: only [A-Za-z0-9 <>/-] (proven); anything else must be set with b.set("#Id.Text", ...)."""
    if not isinstance(text, str):
        raise ValueError("%s must be a str" % what)
    if has_j(text):
        raise ValueError("runtime text inside the markup (%s) - leave it empty and b.set(\"#Id.Text\", value) after the append" % what)
    if not TEXT_OK.fullmatch(text):
        raise ValueError("inline %s %r has characters not proven on the client - leave it empty and b.set(\"#Id.Text\", ...)"
                         % (what, text))
    return text


def color(c):
    """A kit colour: a COLOR name ("gold"), a literal #rrggbb[aa][(alpha)] or a J() runtime colour."""
    if isinstance(c, str) and c in COLOR:
        return COLOR[c]
    if isinstance(c, str) and has_j(c):
        return c
    if not isinstance(c, str) or not _COLOR_OK.fullmatch(c):
        raise ValueError("not a colour: %r (use a skyyui.COLOR name, a RARITY value or #rrggbb)" % (c,))
    return c


def _num(v, what="number"):
    if isinstance(v, bool):
        raise ValueError(what + " must be a number")
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return ("%.4f" % v).rstrip("0").rstrip(".") if v != int(v) else "%.1f" % v
    if isinstance(v, str) and has_j(v):
        return v
    raise ValueError("%s must be an int or J(): %r" % (what, v))


def _size(v, what="size"):
    """_num for a Width / Height: a static value must be > 0, a J() sample a number >= 0 (a runtime width may be 0)."""
    s = _num(v, what)
    n = _sample_num(v)
    if n is None:
        raise ValueError("%s: the J() sample of %r must be a number" % (what, render(v)))
    if n < 0 or (n == 0 and not has_j(v)):
        raise ValueError("%s must be > 0, got %s" % (what, render(s) if has_j(s) else s))
    return s


def _strip_quoted(s):
    """s with every "..." body blanked (so text never counts as syntax); raises on an unterminated quote."""
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            if j >= n:
                raise ValueError("unterminated quote in markup: %s" % s[i:i + 60])
            out.append('""')
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


_ELEM_OPEN = re.compile(r"(?:^|(?<=[;{}]))\s*([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9_]+))?\s*\{")
_PATH_RE = re.compile(r'"((?:\.\./)*(?:Common|Sounds|Pages|Hud|ItemQualities)/[^"]*)"')
_TEXT_PROP_RE = re.compile(r'(?:\bText|PlaceholderText|TooltipText): "((?:[^"\\]|\\.)*)"')


def _static_ids(s):
    """The element ids of one markup that hold no J() value (runtime ids are never counted as duplicates); a Choice: its first
    variant (check_markup proves both create the same ids)."""
    s = _variants(s)[0]
    return [m.group(2) for m in _ELEM_OPEN.finditer(_strip_quoted(render(s, mark=True))) if m.group(2) and _DYN not in m.group(2)]


def check_markup(s, prefix=None, root=False, kit_paths=True):
    """Syntax / rule check of one inline markup string (raises ValueError). Mirrors SkyyRanks 0.1.1 _check_ui: balanced { } ( ),
    no underscore ids, ids start with the page prefix, no Anchow typo, no ';;', inline Text only [A-Za-z0-9 <>/-], no unfilled
    placeholder - plus: every { opens an element (Type or Type #Id), no duplicate static id, no @variables / $imports inline, every
    texture / sound path is one the kit verifies (kit_paths), and root=True: the page root's Anchor has Width and Height only.
    A choose(...) Choice: both variants, which must create the same element ids (static and runtime)."""
    if isinstance(s, Choice):
        for v in s.variants():
            check_markup(v, prefix, root, kit_paths)
        ids = [sorted(m.group(2) for m in _ELEM_OPEN.finditer(_strip_quoted(render(v, mark=True))) if m.group(2))
               for v in s.variants()]
        if ids[0] != ids[1]:
            raise ValueError("choose(): both markups must create the same element ids, got %s / %s" % (ids[0], ids[1]))
        return s
    if not isinstance(s, str) or not s.strip():
        raise ValueError("empty markup")
    for m in _TEXT_PROP_RE.finditer(s):
        if has_j(m.group(1)):
            raise ValueError("runtime text inside Text: \"...\" - use b.set(\"#Id.Text\", ...)")
    t = render(s)
    bare = _strip_quoted(t)
    if bare.count("{") != bare.count("}") or bare.count("(") != bare.count(")"):
        raise ValueError("unbalanced inline UI markup: %s" % t[:160])
    stack = []
    for ch in bare:
        if ch in "{(":
            stack.append(ch)
        elif ch in "})":
            if not stack or stack.pop() != ("{" if ch == "}" else "("):
                raise ValueError("a bracket closes before it opens / brackets cross: %s" % t[:160])
    opens = bare.count("{")
    found = list(_ELEM_OPEN.finditer(bare))
    if len(found) != opens:
        raise ValueError("every { must open an element ('Group #Id {' / 'Label {'): %s" % t[:160])
    for m in found:
        eid = m.group(2)
        if eid is not None:
            if "_" in eid:
                raise ValueError("underscore in element id #" + eid)
            if not _ID_OK.fullmatch(eid):
                raise ValueError("bad element id #" + eid)
            if prefix and not eid.startswith(prefix):
                raise ValueError("element id #%s does not start with the page prefix %s" % (eid, prefix))
    ids = _static_ids(s)
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate element id(s) in one markup: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
    if "Anchow" in t or ";;" in bare:
        raise ValueError("Anchow typo or ';;' in markup: %s" % t[:160])
    if "@" in bare or "$" in bare:
        raise ValueError("document variables (@X, $C) do not work inline - spell the value out: %s" % t[:160])
    if "%" in bare:
        raise ValueError("unfilled % placeholder in markup: %s" % t[:160])
    for m in _TEXT_PROP_RE.finditer(t):
        if not TEXT_OK.fullmatch(m.group(1)):
            raise ValueError("inline text with unproven characters (use b.set): %r" % m.group(1))
    if kit_paths:
        known = set(TEX.values()) | set(SND.values())
        for m in _PATH_RE.finditer(t):
            if m.group(1) not in known:
                raise ValueError("texture / sound path %s is not one the kit verifies (add it to skyyui.TEX / SND)" % m.group(1))
    if root:
        m = re.match(r"\s*Group\s+#[A-Za-z0-9]+\s*\{\s*Anchor:\s*\(([^)]*)\)\s*;", bare)
        if not m:
            raise ValueError("a page root is 'Group #Id { Anchor: (Width: w, Height: h); ... }': %s" % t[:120])
        keys = sorted(k.split(":")[0].strip() for k in m.group(1).split(","))
        if keys != ["Height", "Width"]:
            raise ValueError("page root Anchor must be Width / Height only (HANDOFF section 2), got %s" % keys)
    return s


def check_page(appends, prefix=None, known_parents=()):
    """check_markup on every (parent, markup) of an Appends list: the first one is the root, every parent exists before use, and
    no static element id is created twice (a duplicate id makes the client bind / set the wrong element)."""
    seen = set(p.lstrip("#") for p in known_parents)
    static = set(seen)
    for i, (parent, mk) in enumerate(appends):
        check_markup(mk, prefix=prefix, root=(parent is None))
        if parent is not None and render(parent).lstrip("#") not in seen:
            raise ValueError("append %d goes into #%s, which no earlier append created" % (i, render(parent)))
        for eid in _static_ids(mk):
            if eid in static:
                raise ValueError("append %d creates #%s a second time (duplicate element id)" % (i, eid))
            static.add(eid)
        for m in _ELEM_OPEN.finditer(_strip_quoted(render(_variants(mk)[0]))):
            if m.group(2):
                seen.add(m.group(2))
    for ident, _prop, _v in getattr(appends, "sets", ()):
        if render(ident).lstrip("#") not in seen:
            raise ValueError("a b.set line targets #%s, which no append created" % render(ident))
    return appends


def fit(parts, avail, what="page"):
    """Assert the heights (or widths) in `parts` fit `avail` px; returns the px left over."""
    tot = sum(parts)
    if tot > avail:
        raise ValueError("%s parts are %d px, only %d px available" % (what, tot, avail))
    return avail - tot


def _sample_int(v, what):
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    if has_j(v) and render(v).isdigit():
        return int(render(v))
    raise ValueError("%s must be an int or J(expr, sample) with a digit sample: %r" % (what, v))


def assert_page_size(w, h):
    """Page root size rules: ints (or J() with an int sample), h <= 980 (fits 1080 with the ornaments), 300 <= w <= 1600."""
    w, h = _sample_int(w, "page width"), _sample_int(h, "page height")
    if h > MAX_PAGE_H:
        raise ValueError("page is %d px high; the most is %d (it must fit a 1080 px screen with its 12 + 6 px decorations)"
                         % (h, MAX_PAGE_H))
    if w > MAX_PAGE_W or w < MIN_PAGE_W:
        raise ValueError("page width %d is outside %d-%d" % (w, MIN_PAGE_W, MAX_PAGE_W))
    if h < TITLE_H + 60:
        raise ValueError("page height %d is too small for the title bar and a body" % h)
    return w, h


# ================================================================= small property builders
_ANCHOR_KEYS = {"left": "Left", "right": "Right", "top": "Top", "bottom": "Bottom", "horizontal": "Horizontal",
                "vertical": "Vertical", "full": "Full"}


def _merge(defaults, anchor):
    """Anchor margins: the builder's vanilla defaults, overridden by the caller's anchor dict (keys case-insensitive)."""
    out = dict((k.lower(), v) for k, v in (defaults or {}).items())
    for k, v in (anchor or {}).items():
        if not isinstance(k, str):
            raise ValueError("anchor key %r" % (k,))
        out[k.lower()] = v
    return out or None


def _anchor(w=None, h=None, extra=None):
    parts = []
    if w is not None:
        parts.append("Width: " + _size(w, "width"))
    if h is not None:
        parts.append("Height: " + _size(h, "height"))
    for k, v in (extra or {}).items():
        if not isinstance(k, str) or k.lower() not in _ANCHOR_KEYS:
            raise ValueError("anchor key %r (use left / right / top / bottom / horizontal / vertical / full)" % (k,))
        parts.append("%s: %s" % (_ANCHOR_KEYS[k.lower()], _num(v, "anchor " + k)))
    return ("Anchor: (%s); " % ", ".join(parts)) if parts else ""


def _padding(p):
    if p is None:
        return ""
    if isinstance(p, dict):
        parts = []
        for k, v in p.items():
            if not isinstance(k, str) or k.lower() not in _ANCHOR_KEYS:
                raise ValueError("padding key %r" % (k,))
            parts.append("%s: %s" % (_ANCHOR_KEYS[k.lower()], _num(v, "padding")))
        return "Padding: (%s); " % ", ".join(parts)
    if isinstance(p, int) and p < 0:
        raise ValueError("padding must be >= 0")
    return "Padding: (Full: %s); " % _num(p, "padding")


def _flex(f):
    return ("FlexWeight: %s; " % _num(f, "flex")) if f is not None else ""


def _layout(mode):
    if mode is None:
        return ""
    if mode not in ("Top", "Left", "Right", "Center", "Middle", "Full", "TopScrolling", "CenterMiddle", "MiddleCenter",
                    "LeftCenterWrap"):
        raise ValueError("LayoutMode %r" % mode)
    return "LayoutMode: %s; " % mode


def _extra(extra):
    if not extra:
        return ""
    e = extra.strip()
    if not e.endswith(";"):
        e += ";"
    return e + " "


def patch(tex, border=None, h_border=None, v_border=None, tint=None):
    """(TexturePath: "Common/...", Border: n) - tex = a TEX name or path; border / h+v borders; tint = a Color over it."""
    path = TEX.get(tex, tex)
    if path not in TEX.values():
        raise ValueError("texture %r is not a kit texture" % tex)
    parts = ['TexturePath: "%s"' % path]
    if v_border is not None or h_border is not None:
        parts.append("HorizontalBorder: %d, VerticalBorder: %d" % (h_border or 0, v_border or 0))     # the ContainerHeader order
    elif border is not None:
        parts.append("Border: %d" % border)
    if tint is not None:
        parts.append("Color: " + color(tint))
    return "(" + ", ".join(parts) + ")"


def sounds(kind="light"):
    """The inline value of a vanilla button sound set: light (every button), cancel (cancel / close / destructive), save (the main
    confirm), main (big main-menu buttons; no server page uses it), lock / unlock (toggles; each keeps the light hover)."""
    if kind not in SOUNDS:
        raise ValueError("sound set %r (one of %s)" % (kind, ", ".join(sorted(SOUNDS))))
    return SOUNDS[kind]


def _is_zero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == 0


def _max_lines(v):
    """The WrapMaxLines to write: None / False / 0 = none (never "WrapMaxLines: 0"), else an int >= 1."""
    if v is None or v is False:
        return None
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise ValueError("max_lines is an int >= 1 (0 / False / None = no WrapMaxLines), got %r" % (v,))
    return v or None


def text_style(size, col, bold=False, upper=False, italic=False, halign=None, valign="Center", wrap=False, max_lines=None,
               font=None, shrink=None, spacing=None):
    """A LabelStyle value (FontSize, TextColor, ...) in vanilla key order. spacing = LetterSpacing (float allowed: 0.5, 1.8; 0 = the
    engine default, not written - the deployed SkyyRanks / SkyyVault titles have none). max_lines = WrapMaxLines, only together
    with wrap=True (vanilla always pairs them; it raises otherwise); None / False / 0 = no line limit."""
    ml = _max_lines(max_lines)
    if ml is not None and not wrap:
        raise ValueError("WrapMaxLines without Wrap: true - pass wrap=True with max_lines=%d (or max_lines=False for none)" % ml)
    parts = ["FontSize: " + _num(size, "font size"), "TextColor: " + color(col)]
    if bold:
        parts.append("RenderBold: true")
    if upper:
        parts.append("RenderUppercase: true")
    if italic:
        parts.append("RenderItalics: true")
    if font is not None:
        if font not in FONTS:
            raise ValueError("font %r: vanilla fonts are Default and Secondary" % font)
        parts.append('FontName: "%s"' % font)
    if spacing is not None and not _is_zero(spacing):
        parts.append("LetterSpacing: " + _num(spacing, "letter spacing"))
    if halign is not None:
        if halign not in ("Start", "Center", "End"):
            raise ValueError("HorizontalAlignment %r" % halign)
        parts.append("HorizontalAlignment: " + halign)
    if valign is not None:
        if valign not in ("Start", "Center", "End"):
            raise ValueError("VerticalAlignment %r" % valign)
        parts.append("VerticalAlignment: " + valign)
    if wrap:
        parts.append("Wrap: true")
    if ml is not None:
        parts.append("WrapMaxLines: %d" % ml)
    if shrink is not None:
        parts.append("ShrinkTextToFit: true, MinShrinkTextToFitFontSize: %d" % shrink)
    return "(" + ", ".join(parts) + ")"


# ================================================================= labels
# kind: (vanilla size, colour, bold, uppercase, horizontal alignment, wrap, italic, where vanilla uses it)
LABELS = {
    "default": (16, "text", False, False, None, False, False, "@DefaultLabelStyle: hints, body text"),
    "bold": (16, "text", True, False, None, False, False, "@DefaultLabelStyle + RenderBold (Teleporter field labels)"),
    "strong": (16, "white", True, False, None, False, False, "white bold values / names (@ColorDefault)"),
    "message": (16, "text", False, False, "Center", True, False, "wrapped centred message (PrefabEditorExitConfirm)"),
    "caption": (12, "caption", False, False, None, False, False, "gray caption / description (#878e9c, CommandListPage)"),
    "captionLight": (11, "captionLight", False, False, None, False, False, "footnote / empty state (#5a6a7a)"),
    "note": (12, "text", False, False, None, False, False, "small note under a heading (PrefabEditorExitConfirm)"),
    "muted": (16, "muted", False, False, None, False, False, "muted value (ItemRepairElement durability)"),
    "gold": (16, "gold", True, False, None, False, False, "cost / highlight (@ColorGoldHighlight; gallery-only colour)"),
    "error": (16, "error", False, False, None, False, False, "error line (PrefabSavePage)"),
    "formError": (16, "formError", True, False, None, False, False, "form error (NameRespawnPointPage)"),
    "success": (16, "success", True, False, None, False, False, "done / complete (MemoriesCategory counter)"),
    "warning": (32, "warning", False, False, "Center", False, False, "confirm question (PrefabEditorExitConfirm #WarningTitle)"),
    "info": (14, "info", False, False, None, False, False, "info / timer line (BarterPage #RefreshTimer)"),
    "disabled": (16, "disabled", False, False, None, False, False, "unavailable (@ColorDisabled)"),
    "have": (13, "have", False, False, None, False, False, "you have enough (BarterTradeRow)"),
    "outOfStock": (14, "outOfStock", True, False, None, False, False, "out of stock / missing (BarterTradeRow)"),
    "stock": (12, "stock", False, False, "End", False, False, "stock line (BarterTradeRow #Stock)"),
    "quantity": (15, "white", True, False, "End", False, False, "item quantity overlay (BarterTradeRow #OutputQuantity)"),
    "rowName": (14, "rowName", True, False, None, False, False, "list row name (WorldEventListRow #Label)"),
    "rowSub": (12, "rowSub", False, False, None, False, False, "list row sub line (WorldEventListRow #Sub)"),
    "rowBadge": (12, "rowBadge", False, False, "End", False, False, "list row badge (WorldEventListRow #Badge)"),
    "heading": (18, "rowName", True, False, None, True, False, "content heading (WorldEventPanelPage #PageTitle, one line)"),
    "propKey": (13, "propKey", True, False, None, True, False, "property key (WorldEventPropertyRow #Key, one line)"),
    "propValue": (13, "value", False, False, None, True, False, "property value (WorldEventPropertyRow #Value, one line)"),
    "summary": (13, "summary", False, False, None, True, False, "summary line (WorldEventSummaryRow, one line)"),
    "fieldLabel": (13, "text", True, False, None, False, False, "form field label (BlockSpawnerSpawnerEntryRow @FieldLabelStyle)"),
    "display": (32, "white", False, False, None, False, False, "big number (Hud/TimeLeft timer: 32 px, the Default font - big "
                "Secondary text on real pages is a title: RespawnPage 38, PortalDeviceSummon 24)"),
    "tileName": (15, "title", True, True, "Center", True, False, "tile name (MemoriesCategory, font Secondary, bottom-aligned)"),
    "section": (13, "section", True, True, "Start", False, False, "list section head (WorldEventSectionLabel)"),
    "subtitle": (15, "text", True, True, None, False, False, "section subtitle (@SubtitleStyle)"),
    "panelTitle": (15, "panelTitle", True, False, None, False, False, "sub-panel title (@PanelTitle)"),
    "formCaption": (16, "formCaption", True, True, None, False, False, "form field caption (NameRespawnPointPage)"),
    "optionName": (16, "optionName", True, False, None, False, False, "option row name (OverrideRespawnPointButton)"),
    "optionDetail": (14, "optionDetail", False, False, "End", False, False, "option row detail (OverrideRespawnPointButton)"),
    "cardCaption": (14, "cardCaption", False, False, None, False, False, "card caption (BarterTradeRow Cost)"),
    "tipName": (18, "white", True, False, None, True, False, "item-tooltip-like name (client ItemTooltip; colour by rarity)"),
    "tipId": (14, "tipId", False, False, None, False, True, "item-tooltip-like id / type line (client ItemTooltip)"),
    "tipDesc": (14, "tipDesc", False, False, None, True, False, "item-tooltip-like description (client ItemTooltip)"),
    "tipStat": (14, "tipStat", False, False, None, False, False, "item-tooltip-like stat line (client ItemTooltip)"),
    "setting": (18, "text", False, False, None, False, False, "settings row label (client LabeledCheckBoxSetting)"),
    "settingHead": (18, "text", True, True, None, False, False, "settings section header (client SectionHeader)"),
}
# kind: (font, WrapMaxLines, VerticalAlignment) where it is not the default (None, None, Center)
LABEL_MORE = {"tileName": (FONT_SECONDARY, None, "End"),
              "heading": (None, 1, "Center"), "propKey": (None, 1, "Center"), "propValue": (None, 1, "Center"),
              "summary": (None, 1, "Center")}
_need("C", "@SubtitleStyle = LabelStyle(FontSize: 15, RenderUppercase: true, TextColor: #96a9be, RenderBold: true);", "label subtitle")
_need("C", "  Style: @SubtitleStyle;\n  Text: @Text;\n  Anchor: (Bottom: 10);", "subtitle bottom 10")
_need("C", "Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3, HorizontalAlignment: @Alignment);\n"
      "    Anchor: (Height: 35, Horizontal: 8);", "label panelTitle")
_need("L", "Anchor: (Top: 10, Bottom: 4, Left: 2);\n  Style: (FontSize: 13, RenderUppercase: true, RenderBold: true, TextColor: #9aacbc, "
      "HorizontalAlignment: Start);", "label section")
_need("W", "Style: (FontSize: 14, RenderBold: true, TextColor: #d6e4ee, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);",
      "label rowName")
_need("W", "Style: (FontSize: 12, TextColor: #7f93a6, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);", "label rowSub")
_need("W2", "Style: (FontSize: 18, RenderBold: true, TextColor: #d6e4ee, VerticalAlignment: Center, Wrap: true, WrapMaxLines: 1);",
      "label heading")
_need("BS", "@FieldLabelStyle = (...$C.@DefaultLabelStyle, FontSize: 13, RenderBold: true);", "label fieldLabel")
# display: the one big NUMBER a real custom page shows is the Hud/TimeLeft timer (32 px, no FontName = Default). PortalDeviceSummon's
# @TimeLimitStyle (32 px Secondary) is defined but never used on that page; big Secondary text on real pages is a title.
_need("HT", "TimerLabel #TimeLabel {\n      Style: (FontSize: 32, Alignment: Center);", "label display (Hud/TimeLeft timer, Default font)")
_need("PS", 'Style: (FontSize: 24, TextColor: #dee2ef, FontName: "Secondary", RenderUppercase: true, HorizontalAlignment: Center, '
      'ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 18);', "big Secondary text is a title (PortalDeviceSummon #Title0, 24 px)")
_need("MC", 'Style: (...@TitleStyle, FontName: "Default", RenderBold: true, TextColor: #b4c8c9, LetterSpacing: 0.5);',
      "LetterSpacing takes a float (0.5)")
_need("RS", "FontSize: 38,\n            LetterSpacing: 1.8,\n            FontName: \"Secondary\",", "LetterSpacing 1.8 on a Secondary title")
_need("M", "@CategoryButtonLabelStyle = LabelStyle(\n  Wrap: true,\n  HorizontalAlignment: Center,\n  VerticalAlignment: End,\n"
      "  TextColor: #b4c8c9,\n  FontName: \"Secondary\",\n  RenderBold: true,\n  RenderUppercase: true,\n  FontSize: 15,", "label tileName")
_need("B", "FontSize: 15,\n              TextColor: #ffffff,", "label quantity")
_need("P", "Style: (...$C.@DefaultLabelStyle, HorizontalAlignment: Center, Wrap: true, FontSize: 16);", "label message")
_need("P", "Label {\n        Anchor: (Bottom: 8, Horizontal: 4);\n        Style: (...$C.@DefaultLabelStyle, FontSize: 12, TextColor: #96a9be);",
      "label note + the confirm note anchor")
_need("P", "Anchor: (Bottom: 12, Horizontal: 8);", "confirm question anchor")
_need("P", "Anchor: (Bottom: 16, Horizontal: 8);", "confirm message anchor")
_need("T", "Style: (FontSize: 12, TextColor: $C.@ColorGrayCaption, Wrap: true);", "label caption (12)")
_need("G", "Style: (FontSize: 11, TextColor: $C.@ColorCaptionLight);", "label captionLight (11)")
_need("BP", "FontSize: 14,\n            TextColor: #7caacc,", "label info (14)")
_need("B", "FontSize: 14,\n            TextColor: #8a9aaa,", "label cardCaption (14)")
_need("O", "Style: (RenderBold: true, VerticalAlignment: Center, TextColor: #90a2b7);", "label optionName")
_need("O", "Style: (VerticalAlignment: Center, HorizontalAlignment: End, TextColor: #8698ad, FontSize: 14);", "label optionDetail")
_need("CT", "Style: (RenderBold: true, FontSize: 18, Wrap: true);", "label tipName")
_need("CS", "Style: (VerticalAlignment: Center, TextColor: #96a9be, RenderUppercase: false, FontSize: 18);", "label setting")
_need("CH", "Style: (FontSize: 18, TextColor: #96a9be, RenderUppercase: true, RenderBold: true);", "label settingHead")


def label(ident=None, text="", kind="default", h=None, w=None, size=None, col=None, bold=None, upper=None, align=None,
          valign=None, wrap=None, max_lines=None, italic=None, anchor=None, padding=None, flex=None, font=None, spacing=None,
          extra="", fit=True):
    """A Label in one of the vanilla LABELS kinds. Text is empty by default (b.set it); static text must be [A-Za-z0-9 <>/-]
    (Appends.text / Shell.text split other text into an empty label + a b.set line for you).
    size defaults to fs(the vanilla size); h defaults to size + 10 (h=False: no Height, the label fills its parent / row);
    col / bold / font (Default / Secondary) / spacing (LetterSpacing, float; 0 = none) / valign (False = none) / ... override the
    kind. max_lines = WrapMaxLines (needs wrap; max_lines=False / 0 removes the kind's own line limit, and wrap=False drops it too).
    fit (kit 1.4): a static one-line text wider than w (minus the padding) prints a build WARNING (text_width, the client's own
    font tables; never an error); fit=False for a text that is meant to be clipped. It never changes the markup."""
    if kind not in LABELS:
        raise ValueError("label kind %r (one of %s)" % (kind, ", ".join(sorted(LABELS))))
    vs, kc, kb, ku, ka, kw, ki, _where = LABELS[kind]
    kf, kml, kva = LABEL_MORE.get(kind, (None, None, "Center"))
    sz = size if size is not None else fs(vs)
    if h is None and isinstance(sz, int):
        h = sz + 10
    elif h is False:
        h = None                       # no Height: the label fills its parent (a row badge, a property value)
    wr = kw if wrap is None else bool(wrap)
    ml = (kml if wr else None) if max_lines is None else max_lines    # the kind's line limit goes with its wrap
    eb, eu, ef = kb if bold is None else bold, ku if upper is None else upper, font if font is not None else kf
    st = text_style(sz, col if col is not None else kc, bold=eb, upper=eu,
                    italic=ki if italic is None else italic, halign=align if align is not None else ka,
                    valign=kva if valign is None else (None if valign is False else valign), wrap=wr,
                    max_lines=ml, font=ef, spacing=spacing)
    head = "Label #%s { " % check_id(ident) if ident else "Label { "
    mk = (head + _anchor(w, h, anchor) + _padding(padding) + _flex(flex) + 'Text: "%s"; ' % check_text(text)
          + "Style: %s; " % st + _extra(extra) + "}")
    if fit and text and not wr:
        _fit_label(ident, text, sz, eb, eu, ef, w, padding)     # kit 1.4: a WARNING only, after the markup passed its checks
    return mk


def status_line(ident, color_expr="colorOf(this.info)", h=30, size=16, wrap=False, max_lines=None, anchor=None):
    """The page's result line (SkyyRanks look: 16 px bold, centred) whose colour is picked at runtime by the mark of the result
    ("+" success, "-" error, "=" STATUS["="] = info blue: java_status_methods()). color_expr is the Java expression that gives the
    colour: the default assumes your page class keeps the result in a field named `info`. b.set its Text with textOf(...).
    wrap=True (with a taller h, e.g. 44 for two lines) for pages whose results can be longer than one line; max_lines =
    WrapMaxLines (a "base" probe property; only with wrap=True - it raises otherwise); anchor = its margins (e.g. {"top": 12})."""
    return label(ident, "", "default", h=h, size=size, bold=True, align="Center", col=J(color_expr, COLOR["success"]),
                 wrap=True if wrap else None, max_lines=max_lines, anchor=anchor)


def title_style():
    """The window title LabelStyle (@Title: ...@TitleStyle + HorizontalAlignment Center). @TitleStyle's LetterSpacing: 0 is the
    engine default and is not written (kit 1.3), so the title matches the deployed SkyyRanks 0.1.1 / SkyyVault 0.1.3 titles."""
    return text_style(TITLE_SIZE, "title", bold=True, upper=True, font=FONT_SECONDARY, spacing=0, halign="Center", valign="Center")


def title_label(ident, text=""):
    """The window title label (@Title + @TitleStyle: 15 px, bold, uppercase, font Secondary, #b4c8c9, centred)."""
    return 'Label #%s { Padding: (Horizontal: %d); Text: "%s"; Style: %s; }' % (check_id(ident), TITLE_LABEL_PAD, check_text(text),
                                                                               title_style())


def section(ident=None, text="", h=None, w=None):
    """A list section head (WorldEventSectionLabel: uppercase bold #9aacbc, margins top 10 / bottom 4 / left 2)."""
    return label(ident, text, "section", h=h, w=w, anchor={"top": 10, "bottom": 4, "left": 2})


def subtitle(ident=None, text="", h=None):
    """A section subtitle (@Subtitle: 15 px bold uppercase #96a9be, bottom 10)."""
    return label(ident, text, "subtitle", h=h, anchor={"bottom": 10})


def panel_title(ident, text="", w=None):
    """@PanelTitle: a 35 px bold #afc2c3 title with its 1 px #393426(0.5) line, as one Group (ident + 'Box')."""
    check_id(ident)
    lab = label(ident, text, "panelTitle", h=35, anchor={"horizontal": 8})
    return "Group #%sBox { %sLayoutMode: Top; %s Group { Anchor: (Height: 1); Background: %s; } }" % (
        ident, _anchor(w, 36), lab, COLOR["panelLine"])


def property_row(ident, key_id, value_id, key_text="", key_w=PROP_KEY_W, h=None, gap=PROP_ROW_GAP, w=None, anchor=None):
    """A key / value info row (Pages/WorldEvent/WorldEventPropertyRow): LayoutMode Left, height 20 (readable 26) + bottom 2; the
    key 150 wide + right 8 (13 px bold #7a8a9a, one line), the value FlexWeight 1 (13 px #b7cedd, one line). b.set the value Text
    (and the key Text when it is not static). For Stats / Bank / Guild / Profile info boxes; put the rows in a panel("well")."""
    check_id(ident)
    h = h if h is not None else (PROP_ROW_H if _SCALE[0] == "vanilla" else fs(13) + 10)
    key = label(key_id, key_text, "propKey", w=key_w, h=False, anchor={"right": 8})
    val = label(value_id, "", "propValue", h=False, flex=1)
    return "Group #%s { %sLayoutMode: Left; %s %s }" % (ident, _anchor(w, h, _merge({"bottom": gap} if gap else None, anchor)), key, val)


# ================================================================= buttons
# kind: (texture family, patch borders, label colour, default sound set)
BUTTONS = {
    "primary": ("Primary", "VerticalBorder: 12, HorizontalBorder: 80", "buttonText", "light"),
    "secondary": ("Secondary", "Border: 12", "button2Text", "light"),
    "tertiary": ("Tertiary", "Border: 12", "button2Text", "light"),
    "destructive": ("Destructive", "Border: 12", "buttonText", "cancel"),
}
BUTTON_SIZES = {"normal": (17, BTN_H, BTN_PAD), "small": (14, BTN_SMALL_H, BTN_SMALL_PAD), "big": (17, BTN_BIG_H, BTN_PAD)}
_need("C", "@DefaultButtonLabelStyle = LabelStyle(\n  FontSize: 17,\n  TextColor: @ColorButtonText,\n  RenderBold: true,\n"
      "  RenderUppercase: true,\n  HorizontalAlignment: Center,\n  ShrinkTextToFit: true,\n  MinShrinkTextToFitFontSize: 12,\n"
      "  VerticalAlignment: Center\n);", "button label style")
_need("C", "@DefaultButtonDisabledLabelStyle = LabelStyle(\n  ...@DefaultButtonLabelStyle,\n  TextColor: @ColorDisabled\n);",
      "disabled button label")
_need("C", "@SmallButtonLabelStyle = LabelStyle(\n  ...@DefaultButtonLabelStyle,\n  FontSize: 14\n);", "small button label")
_need("C", "@SmallSecondaryButtonLabelStyle = LabelStyle(\n  ...@SecondaryButtonLabelStyle,\n  FontSize: 14\n);",
      "small secondary label")
for _st in ("", "_Hovered", "_Pressed"):
    _need("C", 'PatchStyle(TexturePath: "Common/Buttons/Primary%s.png", VerticalBorder: @ButtonBorder, HorizontalBorder: 80);' % _st,
          "primary texture")
    _need("C", 'PatchStyle(TexturePath: "Common/Buttons/Secondary%s.png", Border: @ButtonBorder), LabelStyle: @SecondaryButtonLabelStyle'
          % _st, "secondary texture + label")
    _need("C", 'PatchStyle(TexturePath: "Common/Buttons/Tertiary%s.png", Border: @ButtonBorder), LabelStyle: @SecondaryButtonLabelStyle'
          % _st, "tertiary texture + label")
    _need("C", 'PatchStyle(TexturePath: "Common/Buttons/Destructive%s.png", Border: @ButtonBorder), LabelStyle: @DefaultButtonLabelStyle'
          % _st, "destructive texture + label")
_need("C", '@DefaultButtonDisabledBackground = PatchStyle(TexturePath: "Common/Buttons/Disabled.png", VerticalBorder: @ButtonBorder, '
      'HorizontalBorder: 80);', "primary disabled texture")
_need("C", 'Disabled: (Background: PatchStyle(TexturePath: "Common/Buttons/Disabled.png", Border: @ButtonBorder), LabelStyle: '
      '@DefaultButtonDisabledLabelStyle)', "disabled texture + label")
_need("C", 'Disabled: (Background: PatchStyle(TexturePath: "Common/Buttons/Disabled.png", Border: @ButtonBorder), LabelStyle: '
      '@SmallButtonDisabledLabelStyle)', "small disabled label")
_need("C", '@TertiaryActiveButtonBackground = PatchStyle(TexturePath: "Common/Buttons/Tertiary_Active.png", Border: @ButtonBorder);',
      "selected tertiary texture")
_need("C", "  Anchor: (...@Anchor, Height: @DefaultButtonHeight);\n  Padding: (Horizontal: @DefaultButtonPadding);", "button padding 24")


def _btn_label(size, col):
    return "(FontSize: %d, TextColor: %s, RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, ShrinkTextToFit: true, " \
           "MinShrinkTextToFitFontSize: 12, VerticalAlignment: Center)" % (size, color(col))


def button_style(kind="secondary", size="normal", selected=False, disabled=False, sound=None):
    """The `Style: TextButtonStyle(...);` of a vanilla text button: Default / Hovered / Pressed / Disabled states with the kind's
    textures and label, plus its sound set. selected (tertiary only) = Tertiary_Active (a quiet toggle; no vanilla page uses it).
    disabled = the Disabled look in every state and no sounds (do not bind it). sound = a SOUNDS name to override (save on a main
    confirm, cancel on Cancel / Close / Back)."""
    if kind not in BUTTONS:
        raise ValueError("button kind %r (primary / secondary / tertiary / destructive)" % kind)
    if size not in BUTTON_SIZES:
        raise ValueError("button size %r (normal / small / big)" % size)
    fam, pb, lc, snd = BUTTONS[kind]
    if selected and kind != "tertiary":
        raise ValueError("selected= is the tertiary toggle look (Tertiary_Active); a selected tab is a Primary button (tab_row)")
    lsz = BUTTON_SIZES[size][0]
    lab, dlab = _btn_label(lsz, lc), _btn_label(lsz, "disabled")
    dis = '(Background: (TexturePath: "%s", %s), LabelStyle: %s)' % (TEX["btnDisabled"], pb, dlab)
    if disabled:
        return "Style: TextButtonStyle(Default: %s, Hovered: %s, Pressed: %s, Disabled: %s);" % (dis, dis, dis, dis)
    d = TEX["btn" + fam] if not selected else TEX["btnTertiaryActive"]
    hv = TEX["btn" + fam + "Hovered"] if not selected else TEX["btnTertiaryActive"]
    pr = TEX["btn" + fam + "Pressed"]
    st = lambda tex: '(Background: (TexturePath: "%s", %s), LabelStyle: %s)' % (tex, pb, lab)
    return "Style: TextButtonStyle(Default: %s, Hovered: %s, Pressed: %s, Disabled: %s, Sounds: %s);" % (
        st(d), st(hv), st(pr), dis, sounds(sound or snd))


def button(ident, text="", kind="secondary", size="normal", w=None, h=None, selected=False, disabled=False, sound=None,
           anchor=None, flex=None, disable_element=False, trial=False, extra="", fit=True):
    """One vanilla TextButton (bind it with Activating on #ident). w defaults to 172 (normal / big), 92 (small) or 150 (a small
    Primary); a Primary is never narrower than 120 (PointInspectorPage; a J() width is checked by its sample, a flex width is not
    checked). disable_element=True also writes `Disabled: true;` (UNVERIFIED, trial=True). fit (kit 1.4): a static label wider than
    w - 2 x the padding prints a build WARNING (the vanilla label then shrinks to fit, down to 12 px - ShrinkTextToFit); fit=False
    for a label that is meant to shrink. It never changes the markup."""
    check_id(ident)
    if size not in BUTTON_SIZES:
        raise ValueError("button size %r (normal / small / big)" % size)
    if kind not in BUTTONS:
        raise ValueError("button kind %r (primary / secondary / tertiary / destructive)" % kind)
    lsz, bh, bp = BUTTON_SIZES[size]
    if w is None and flex is None:
        if size == "small":
            w = PRIMARY_SMALL_W if kind == "primary" else ROW_ACTION_W
        else:
            w = BTN_MIN_W                  # a flex button takes its width from the row
    if kind == "primary" and w is not None:
        n = _sample_num(w)
        if n is not None and n < PRIMARY_MIN_W:
            raise ValueError("a Primary button is at least %d px wide (PointInspectorPage; %d recommended, @DefaultButtonMinWidth); "
                             "use secondary for %s px" % (PRIMARY_MIN_W, BTN_MIN_W, n))
    dp = ""
    if disable_element:
        _gate("disabled-prop", trial)
        dp = "Disabled: true; "
    mk = ("TextButton #%s { " % ident + _anchor(w, h if h is not None else bh, anchor) + "Padding: (Horizontal: %d); " % bp
          + _flex(flex) + dp + 'Text: "%s"; ' % check_text(text)
          + button_style(kind, size, selected, disabled, sound) + " " + _extra(extra) + "}")
    if fit and text and flex is None:
        _fit_button(ident, text, lsz, w, bp)                    # kit 1.4: a WARNING only, after the markup passed its checks
    return mk


def on_off(prefix, on, w=120, h=None, texts=("ON", "OFF")):
    """An ON / OFF pair of small tertiary buttons (ids prefix+'On' / prefix+'Off'); the current one is selected (Tertiary_Active).
    No vanilla precedent: the FALLBACK switch until the vanilla CheckBox is probed (then use checkbox_row)."""
    check_id(prefix)
    return [button(prefix + "On", texts[0], "tertiary", "small", w=w, h=h, selected=bool(on)),
            button(prefix + "Off", texts[1], "tertiary", "small", w=w, h=h, selected=not on, anchor={"left": 6})]


def close_button(ident):
    """The container close X (top-right, 32 x 32 at -8 / -8; ButtonsCancel sounds). OPTIONAL: vanilla containers ship it hidden
    (Visible: @CloseButton, default false) and no server page turns it on; the vanilla way out is Esc + a footer Close button
    (Secondary + sound="cancel", WorldEventPanelPage). Append it LAST into the page root."""
    check_id(ident)
    return ('Button #%s { Anchor: (Width: %d, Height: %d, Top: -8, Right: -8); Style: ButtonStyle(Default: (Background: "%s"), '
            'Hovered: (Background: "%s"), Pressed: (Background: "%s"), Sounds: %s); }'
            % (ident, CLOSE_SIZE, CLOSE_SIZE, TEX["close"], TEX["closeHovered"], TEX["closePressed"], sounds("cancel")))


_need("C", 'Default: (Background: "Common/ContainerCloseButton.png"),\n      Hovered: (Background: "Common/ContainerCloseButtonHovered.png"),\n'
      '      Pressed: (Background: "Common/ContainerCloseButtonPressed.png"),\n      Sounds: @ButtonsCancel', "close X")


def button_row(ident, h=BTN_H, align="center", top=8, w=None, anchor=None, used=None, avail=None, left_margin=None):
    """A row for buttons (vanilla dialogs: LayoutMode Center, Top 8; give the buttons anchor right / left 6).
    Kit 1.4, WITHOUT LayoutMode Center / Right (base probe properties): used = the outer width of the buttons in the row (their
    Width + Anchor margins: SUI.used_width, or add them up), avail = the row's inner width (default w) -> a LayoutMode Left row
    whose Padding Left right-aligns (align "right": right_margin(avail, used)) or centres (align "center": centre_margin) them;
    left_margin = that padding as an int or a J("expr", "344") runtime value (a footer whose buttons come and go - SkyyParty's
    gapR). Returns a Markup (.left = the padding) on that path; without used / left_margin the kit 1.3 row (a plain str)."""
    lm = {"center": "Center", "left": "Left", "right": "Right"}.get(align)
    if lm is None:
        raise ValueError("align center / left / right")
    if used is None and left_margin is None:
        return "Group #%s { %s%s}" % (check_id(ident), _anchor(w, h, _merge({"top": top} if top else None, anchor)), _layout(lm))
    if left_margin is None:
        room = avail if avail is not None else w
        if not isinstance(room, int) or isinstance(room, bool) or not isinstance(used, int) or isinstance(used, bool):
            raise ValueError("button_row(used=) needs int used and an int avail= (or w=): the row's inner width")
        left = {"right": right_margin(room, used), "center": centre_margin(room, used), "left": 0}[align]
    else:
        if _sample_num(left_margin) is None or _sample_num(left_margin) < 0:
            raise ValueError("button_row left_margin: an int >= 0 or a J(expr, sample) with a number sample: %r" % (left_margin,))
        left = left_margin
    mk = "Group #%s { %s%s%s}" % (check_id(ident), _anchor(w, h, _merge({"top": top} if top else None, anchor)), _layout("Left"),
                                  _padding({"left": left}) if not _is_zero(left) else "")
    return Markup(mk, left=left)


_need("P", "LayoutMode: Center;\n        Anchor: (Top: 8);", "button row")


def spacer(w=None, h=None):
    """An empty Group of the given size (vanilla @ActionButtonSeparator / @VerticalActionButtonSeparator, EntitySpawnPage tab gap)."""
    if w is None and h is None:
        raise ValueError("spacer needs w or h")
    return "Group { %s}" % _anchor(w, h)


def group(ident=None, layout="Left", w=None, h=None, anchor=None, flex=None, pad=None, extra="", bg=None):
    """A plain layout container with NO look of its own (no background, no border): a row (layout "Left") or column ("Top") that
    holds kit elements, the way vanilla pages nest plain Groups (PrefabSavePage `Group { LayoutMode: Left; ... #SelectedPackBox
    ... #BrowsePackButton }`, WorldEventPanelPage #Body / #Panes / #Footer). layout = a LayoutMode (Left, Top, Right, Center,
    Middle, Full, TopScrolling, ... - Right / Center / Full are "base" probe properties; Left / Top are proven on Skyy pages);
    w / h / anchor (margins) / flex / pad (int or dict) / extra as the other builders. ident may be None (an anonymous row). Never a
    page root (page_shell builds that). bg (kit 1.4) = a background colour: a COLOR name, a RARITY / QUALITY literal or a J()
    runtime colour (build one from colour NAMES with color_by(...)); written where extra="Background: ..." went, so the output is
    the same as that hand-written form."""
    head = ("Group #%s { " % check_id(ident)) if ident else "Group { "
    return (head + _anchor(w, h, anchor) + _flex(flex) + _layout(layout) + _padding(pad)
            + (("Background: %s; " % color(bg)) if bg is not None else "") + _extra(extra) + "}")


_need("E", "        Group {\n          LayoutMode: Left;\n\n          Group #SelectedPackBox {", "plain layout row (group)")


# ================================================================= inputs
_need("C", '@InputBoxBackground = PatchStyle(TexturePath: "Common/InputBox.png", Border: 16);', "input box")
_need("C", '@InputBoxSelectedBackground = PatchStyle(TexturePath: "Common/InputBoxSelected.png", Border: 16);', "input selected")
_need("C", "@DefaultInputFieldStyle = InputFieldStyle();", "the vanilla text field style is the engine default")
_need("E", "Background: $C.@InputBoxBackground;\n            Padding: (Horizontal: 10);", "value box")
_need("E", "Anchor: (Right: 8, Height: 38);\n            Background: $C.@InputBoxBackground;\n            Padding: (Horizontal: 10);\n"
      "            FlexWeight: 1;", "value box flex")
_need("IL", "$C.@TextField #SearchInput {\n        @Anchor = (Left: 0);\n        FlexWeight: 1;", "text field flex")
_need("W2", "TextField #FilterField {\n              Anchor: (Width: 260, Height: 28);", "filter field height 28")
_need("W2", "Style: (...$C.@DefaultInputFieldStyle, FontSize: 13, TextColor: #b7cedd);\n              Padding: (Horizontal: 6);",
      "filter field look")

FIELD_LOOKS = ("kit", "vanilla", "filter")


def text_field(box_id, field_id, w=None, h=None, placeholder="", max_length=None, size=16, number=False, trial=False,
               look="kit", anchor=None, flex=None, padding=None, extra="", field_extra=""):
    """A vanilla @TextField: the InputBox.png patch (Border 16) on a wrapper Group #box_id (the Skyy-proven pattern) holding the
    field #field_id (Anchor Full 0, Padding Horizontal 10, placeholder #6e7da1). Its value comes back with
    EventData.append(key, "#field.Value"). w=None + flex=None = the full parent width; flex=1 in a LayoutMode Left row
    (InstanceListPage search). look: "kit" (text white at `size`, SkyyRanks 0.1.1), "vanilla" (exactly @TextField: the engine's
    default text style, placeholder colour only), "filter" (WorldEventPanelPage filter: 13 px #b7cedd, 28 high, padding 6) -
    which one matches the game best is decided on probe page 2. number=True makes it a NumberField (UNVERIFIED, trial=True).
    extra goes on the box Group, field_extra on the field."""
    check_id(box_id)
    check_id(field_id)
    if number:
        _gate("number-field", trial)
    if look not in FIELD_LOOKS:
        raise ValueError("text field look %r (one of %s)" % (look, ", ".join(FIELD_LOOKS)))
    if look == "filter":
        h = h if h is not None else FILTER_H
        pad = padding if padding is not None else {"horizontal": FILTER_PAD}
        st = "Style: (FontSize: %s, TextColor: %s); " % (_num(fs(13)), COLOR["value"])
        pst = "PlaceholderStyle: (TextColor: %s); " % COLOR["placeholder"]
    elif look == "vanilla":
        h = h if h is not None else FIELD_H
        pad = padding if padding is not None else {"horizontal": FIELD_PAD}
        st = ""
        pst = "PlaceholderStyle: (TextColor: %s); " % COLOR["placeholder"]
    else:
        h = h if h is not None else FIELD_H
        pad = padding if padding is not None else {"horizontal": FIELD_PAD}
        st = "Style: (TextColor: %s, FontSize: %s); " % (COLOR["white"], _num(size, "font size"))
        pst = "PlaceholderStyle: (TextColor: %s, FontSize: %s); " % (COLOR["placeholder"], _num(size, "font size"))
    ml = ("MaxLength: %d; " % max_length) if max_length else ""
    ph = ('PlaceholderText: "%s"; ' % check_text(placeholder, "PlaceholderText")) if placeholder else ""
    return ("Group #%s { %s%sBackground: %s; %s%s #%s { Anchor: (Full: 0); %s%s%s%s%s%s} }"
            % (box_id, _anchor(w, h, anchor), _flex(flex), patch("input", INPUT_BORDER), _extra(extra),
               "NumberField" if number else "TextField", field_id, _padding(pad), ml, ph, pst, st, _extra(field_extra)))


_need("C", '@ClearButtonStyle = (\n  Texture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.3)),\n'
      '  HoveredTexture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.5)),\n'
      '  PressedTexture: (TexturePath: "Common/ClearInputIcon.png", Color: #ffffff(0.4)),\n  Width: 16,\n  Height: 16,\n'
      '  Side: Right,\n  Offset: 10\n);', "clear button")
_need("PL", "Decoration: (\n              Default: (\n                Icon: (Texture: \"../Common/SearchIcon.png\", Width: 16, Height: 16, "
      "Offset: -25),\n                ClearButtonStyle: (...$C.@ClearButtonStyle, Offset: 10)", "search decoration on a TextField")


def clear_button_style():
    """The @ClearButtonStyle value (the x that empties a search field)."""
    ct = lambda c: '(TexturePath: "%s", Color: %s)' % (TEX["clearIcon"], COLOR[c])
    return "(Texture: %s, HoveredTexture: %s, PressedTexture: %s, Width: 16, Height: 16, Side: Right, Offset: 10)" % (
        ct("clearTint"), ct("clearHover"), ct("clearPressed"))


def search_icon():
    """The search magnifier icon value (@DefaultDropdownBoxStyle SearchInputStyle Icon: tinted #ffffff(0.25), 16 x 16, offset 7)."""
    return '(Texture: (TexturePath: "%s", Color: %s), Width: 16, Height: 16, Offset: 7)' % (TEX["searchIcon"], COLOR["iconTint"])


def search_field(box_id, field_id, w=None, h=SEARCH_H, placeholder="", max_length=None, look="kit", trial=False, anchor=None,
                 flex=None, extra=""):
    """UNVERIFIED (trial=True): a vanilla search box = the @DefaultDropdownBoxStyle SearchInputStyle look (InputBox, 30 high,
    padding left 28, the tinted SearchIcon + the ClearButtonStyle x) on a TextField, with PluginListPage's Decoration(Default: ...)
    structure. Read it like a text_field ("#field.Value"). Vanilla filters lists as you type; a Skyy page filters on Enter / a
    button (no periodic updates)."""
    _gate("search-field", trial)
    deco = "Decoration: (Default: (Icon: %s, ClearButtonStyle: %s));" % (search_icon(), clear_button_style())
    return text_field(box_id, field_id, w, h, placeholder, max_length, look=look, anchor=anchor, flex=flex,
                      padding={"left": SEARCH_PAD_LEFT}, extra=extra, field_extra=deco)


def value_box(box_id, text_id, w=None, h=FIELD_H, kind="default", anchor=None, flex=None, padding=None, extra=""):
    """A read-only value in the input box look (PrefabSavePage #SelectedPackBox: InputBox patch, padding horizontal 10, often
    FlexWeight 1 with anchor right 8 next to a Browse button) + a label (b.set its Text)."""
    check_id(box_id)
    pad = padding if padding is not None else {"horizontal": FIELD_PAD}
    return "Group #%s { %s%sBackground: %s; %s%s%s }" % (
        box_id, _anchor(w, h, anchor), _flex(flex), patch("input", INPUT_BORDER), _padding(pad), _extra(extra), label(text_id, "", kind, h=h))


def checkbox_style():
    """The @DefaultCheckBoxStyle value (transparent / Checkmark states, Tick / Untick sounds)."""
    un = "(Color: %s)" % COLOR["transparent"]
    ck = '(TexturePath: "%s")' % TEX["checkmark"]
    return ('(Unchecked: (DefaultBackground: %s, HoveredBackground: %s, PressedBackground: %s, DisabledBackground: (Color: %s), '
            'ChangedSound: (SoundPath: "%s", Volume: 6)), Checked: (DefaultBackground: %s, HoveredBackground: %s, PressedBackground: '
            '%s, ChangedSound: (SoundPath: "%s", Volume: 6)))' % (un, un, un, COLOR["checkDisabled"], SND["untick"], ck, ck, ck,
                                                                SND["tick"]))


def checkbox(ident, checked=False, trial=False, anchor=None, extra=""):
    """UNVERIFIED (trial=True): the vanilla @CheckBox (22 x 22 CheckBoxFrame + Checkmark, Tick / Untick). Its change is a
    ValueChanged binding; read "#Id.Value" (a boolean) in the EventData. Set it with java_set(id, "Value", True / False)."""
    _gate("checkbox", trial)
    check_id(ident)
    return "CheckBox #%s { %sBackground: %s; Padding: (Full: 4); Value: %s; Style: %s; %s}" % (
        ident, _anchor(CHECK_SIZE, CHECK_SIZE, anchor), patch("checkFrame", 7), "true" if checked else "false", checkbox_style(),
        _extra(extra))


_need("C", '@CheckBox = CheckBox {\n  Anchor: (Width: 22, Height: 22);\n  Background: (TexturePath: "Common/CheckBoxFrame.png", Border: 7);\n'
      '  Padding: (Full: 4);', "checkbox")
_need("C", 'DefaultBackground: (TexturePath: "Common/Checkmark.png"),', "checkmark")
_need("C", "ChangedSound: (SoundPath: $Sounds.@Untick, Volume: 6)", "checkbox untick")
_need("C", "ChangedSound: (SoundPath: $Sounds.@Tick, Volume: 6)", "checkbox tick")


def checkbox_row(ident, label_id, box_id, checked=False, text="", label_w=CHECK_LABEL_W, h=CHECK_SIZE, gap=CHECK_ROW_GAP,
                 trial=False, anchor=None):
    """UNVERIFIED (trial=True, the checkbox key): the vanilla settings switch row (PrefabSavePage: a LayoutMode Left row, bottom 12,
    the @InputLabel 220 wide at left 6 / right 16, then the @CheckBox). THE default Skyy switch once the CheckBox is probed (until
    then: setting_row + on_off)."""
    _gate("checkbox", trial)
    check_id(ident)
    lab = label(label_id, text, "default", w=label_w, h=h, anchor={"left": 6, "right": 16})
    return "Group #%s { %sLayoutMode: Left; %s %s }" % (ident, _anchor(None, h, _merge({"bottom": gap} if gap else None, anchor)), lab,
                                                         checkbox(box_id, checked, trial=True))


_need("C", "@DefaultDropdownBoxLabelStyle = LabelStyle(TextColor: #96a9be, RenderUppercase: true, VerticalAlignment: Center, FontSize: 13);",
      "dropdown label")
_need("C", "@DefaultDropdownBoxEntryLabelStyle = LabelStyle(...@DefaultDropdownBoxLabelStyle, TextColor: #b7cedd);", "dropdown entry")
_need("C", '  DefaultBackground: (TexturePath: "Common/Dropdown.png", Border: 16),\n  HoveredBackground: (TexturePath: '
      '"Common/DropdownHovered.png", Border: 16),\n  PressedBackground: (TexturePath: "Common/DropdownPressed.png", Border: 16),\n'
      '  DefaultArrowTexturePath: "Common/DropdownCaret.png",\n  HoveredArrowTexturePath: "Common/DropdownCaret.png",\n'
      '  PressedArrowTexturePath: "Common/DropdownPressedCaret.png",\n  ArrowWidth: 13,\n  ArrowHeight: 18,', "dropdown box")
_need("C", "  HorizontalPadding: 8,\n  PanelScrollbarStyle: @DefaultScrollbarStyle,\n  PanelBackground: (TexturePath: "
      "\"Common/DropdownBox.png\", Border: 16),\n  PanelPadding: 6,\n  PanelAlign: Right,\n  PanelOffset: 7,\n  EntryHeight: 31,\n"
      "  EntriesInViewport: 10,\n  HorizontalEntryPadding: 7,", "dropdown panel")
_need("C", "  Sounds: $Sounds.@DropdownBox,\n  EntrySounds: $Sounds.@ButtonsLight,\n  FocusOutlineSize: 1,", "dropdown sounds")


def dropdown_style(search=False):
    """The @DefaultDropdownBoxStyle value spelled out (labels 13 px, readable-scaled); search=True adds its SearchInputStyle."""
    lab = "(TextColor: %s, RenderUppercase: true, VerticalAlignment: Center, FontSize: %d)" % (COLOR["text"], fs(13))
    ent = "(TextColor: %s, RenderUppercase: true, VerticalAlignment: Center, FontSize: %d)" % (COLOR["value"], fs(13))
    noi = "(TextColor: %s, RenderUppercase: true, VerticalAlignment: Center, FontSize: %d)" % (COLOR["dropNoItems"], fs(13))
    sel = "(TextColor: %s, RenderUppercase: true, VerticalAlignment: Center, FontSize: %d, RenderBold: true)" % (COLOR["value"], fs(13))
    srch = ""
    if search:
        srch = ("SearchInputStyle: (Background: %s, Icon: %s, ClearButtonStyle: %s, Anchor: (Height: %d), Padding: (Left: %d), "
                "PlaceholderStyle: (TextColor: %s)), " % (patch("input", INPUT_BORDER), search_icon(), clear_button_style(), SEARCH_H,
                                                          SEARCH_PAD_LEFT, COLOR["placeholder"]))
    return ("DropdownBoxStyle(DefaultBackground: %s, HoveredBackground: %s, PressedBackground: %s, DefaultArrowTexturePath: \"%s\", "
            "HoveredArrowTexturePath: \"%s\", PressedArrowTexturePath: \"%s\", ArrowWidth: 13, ArrowHeight: 18, LabelStyle: %s, "
            "EntryLabelStyle: %s, NoItemsLabelStyle: %s, SelectedEntryLabelStyle: %s, %sHorizontalPadding: 8, PanelScrollbarStyle: %s, "
            "PanelBackground: %s, PanelPadding: 6, PanelAlign: Right, PanelOffset: 7, EntryHeight: 31, EntriesInViewport: 10, "
            "HorizontalEntryPadding: 7, HoveredEntryBackground: (Color: %s), PressedEntryBackground: (Color: %s), Sounds: %s, "
            "EntrySounds: %s, FocusOutlineSize: 1, FocusOutlineColor: %s)"
            % (patch("dropdown", 16), patch("dropdownHovered", 16), patch("dropdownPressed", 16), TEX["dropdownCaret"],
               TEX["dropdownCaret"], TEX["dropdownPressedCaret"], lab, ent, noi, sel, srch, scrollbar_style(),
               patch("dropdownPanel", 16), COLOR["dropHover"], COLOR["dropPressed"], DROPDOWN_SOUNDS, sounds("light"),
               COLOR["focusLine"]))


def dropdown(ident, w=DROPDOWN_W, h=DROPDOWN_H, search=False, trial=False, anchor=None, flex=None, extra=""):
    """UNVERIFIED (trial=True): the vanilla @DropdownBox (330 x 32, @DefaultDropdownBoxStyle). Entries come from Java:
    b.set("#Id.Entries", <java.util.List of com.hypixel.hytale.server.core.ui.DropdownEntryInfo(LocalizableString label, String
    value)>), the choice with java_set(id, "Value", "value"); its change is a ValueChanged binding ("#Id.Value" in the EventData).
    search=True adds the vanilla search input (ShowSearchInput)."""
    _gate("dropdown", trial)
    check_id(ident)
    return "DropdownBox #%s { %s%sStyle: %s; %s%s}" % (ident, _anchor(w if flex is None else None, h, anchor), _flex(flex),
                                                     dropdown_style(search), "ShowSearchInput: true; " if search else "", _extra(extra))


# ================================================================= tabs
def tab_row(parent, row_id, tab_ids, names, selected, w=None, h=None, gap=TAB_GAP, mode="primary", row_h=None, top=TAB_MARGIN,
            bottom=TAB_MARGIN):
    """A row of text tabs: Appends [(parent, row), (row, tab0), (row, spacer), (row, tab1), ...]. mode "primary" (default) = the
    vanilla server tab row (EntitySpawnPage: Secondary buttons, FlexWeight 1, 5 px spacers, margins 10; the server sets the active
    tab to the Primary DefaultTextButtonStyle). mode "tertiary" = small tertiary buttons with the active one on Tertiary_Active
    (SkyyRanks / SkyySacks; no vanilla page). w=None = equal flex widths, or a fixed width per tab. names[i] = static text or ""
    (b.set it). Bind each tab id with Activating."""
    if len(tab_ids) != len(names) or not tab_ids:
        raise ValueError("tab ids and names differ in length / are empty")
    if mode not in ("tertiary", "primary"):
        raise ValueError("tab mode primary / tertiary")
    size = "small" if mode == "tertiary" else "normal"
    th = h if h is not None else BUTTON_SIZES[size][1]
    margins = {}
    if top:
        margins["top"] = top
    if bottom:
        margins["bottom"] = bottom
    out = Appends([(parent, "Group #%s { %sLayoutMode: Left; }" % (check_id(row_id), _anchor(None, row_h or th, margins or None)))])
    for i, (tid, nm) in enumerate(zip(tab_ids, names)):
        if i and gap:
            out.append((row_id, spacer(gap)))
        fl = 1 if w is None else None
        if mode == "tertiary":
            mk = button(tid, nm, "tertiary", "small", w=w, h=th, flex=fl, selected=(i == selected))
        else:
            mk = button(tid, nm, "primary" if i == selected else "secondary", "normal", w=w, h=th, flex=fl)
        out.append((row_id, mk))
    return out


# ================================================================= lists and rows
_need("W", "@NormalRowStyle = (\n  Default: (Background: (Color: #101925(0.55))),\n  Hovered: (Background: (Color: #132033(0.8))),\n"
      "  Pressed: (Background: (Color: #182a40(0.9))),\n  Sounds: $Sounds.@ButtonsLight\n);", "panel row normal")
_need("W", "@SelectedRowStyle = (\n  Default: (Background: (Color: #4274a5)),\n  Hovered: (Background: (Color: #4274a5)),\n"
      "  Pressed: (Background: (Color: #4274a5)),\n  Sounds: $Sounds.@ButtonsLight\n);", "panel row selected")
_need("W", "@StaticRowStyle = (\n  Default: (Background: (Color: #101925(0.55))),\n  Hovered: (Background: (Color: #101925(0.55))),\n"
      "  Pressed: (Background: (Color: #101925(0.55)))\n);", "panel row static")
_need("W", "FlexWeight: 1;\n    LayoutMode: Left;\n    Style: @NormalRowStyle;\n    Padding: (Left: 8, Right: 8);", "panel row button")
_need("W", "Anchor: (Width: 4, Right: 8);\n      Background: (Color: #4274a5);", "panel row status bar")
_need("W", "Anchor: (Width: 150, Left: 8);", "panel row badge width")


def row_style(state="normal"):
    """The `Style: ButtonStyle(...);` of a WorldEventListRow select button: normal (panel, hover, pressed + ButtonsLight),
    selected (#4274a5) or static (reads as a panel, no sounds)."""
    if state == "normal":
        return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s), Sounds: %s);" % (
            COLOR["row"], COLOR["rowHover"], COLOR["rowPressed"], sounds("light"))
    if state == "selected":
        c = COLOR["selected"]
        return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s), Sounds: %s);" % (
            c, c, c, sounds("light"))
    if state == "static":
        c = COLOR["row"]
        return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s));" % (c, c, c)
    raise ValueError("row state normal / selected / static")


def panel_row(ident, state="normal", h=None, gap=ROW_GAP, bar=True, w=None):
    """A vanilla list row (Pages/WorldEvent/WorldEventListRow): Group #ident (LayoutMode Left, h + gap) holding Button #identSel
    (FlexWeight 1, the row_style, padding 8) with the 4 px #4274a5 status bar #identBar. Put row_text / row_badge into #identSel,
    row actions (row_action) into #ident after it. Bind the row click on #identSel. h defaults to ROW_H_READABLE (56; the vanilla
    42 fits only the vanilla 14 / 12 px text). state static = a Group panel (no click). Rows go into a scroll_list(well=True)."""
    check_id(ident)
    h = h if h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H)
    barm = ("Group #%sBar { Anchor: (Width: 4, Right: 8); Background: %s; } " % (ident, COLOR["selected"])) if bar else ""
    if state == "static":
        inner = "Group #%sSel { FlexWeight: 1; LayoutMode: Left; Padding: (Left: 8, Right: 8); Background: %s; %s}" % (
            ident, COLOR["row"], barm)
    else:
        inner = "Button #%sSel { FlexWeight: 1; LayoutMode: Left; Padding: (Left: 8, Right: 8); %s %s}" % (
            ident, row_style(state), barm)
    return "Group #%s { %sLayoutMode: Left; %s }" % (ident, _anchor(w, h, {"bottom": gap} if gap else None), inner)


def row_text(ident, name_id, sub_id=None, row_h=None, name_kind="rowName", sub_kind="rowSub"):
    """The text column of a panel row: Group #ident (FlexWeight 1, LayoutMode Top) with the name and sub labels, centred in row_h."""
    check_id(ident)
    nh, sh = fs(LABELS[name_kind][0]) + 6, fs(LABELS[sub_kind][0]) + 5
    row_h = row_h if row_h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H)
    tot = nh + (sh if sub_id else 0)
    fit([tot], row_h, "row text")
    top = (row_h - tot) // 2
    kids = label(name_id, "", name_kind, h=nh) + (" " + label(sub_id, "", sub_kind, h=sh) if sub_id else "")
    return "Group #%s { FlexWeight: 1; LayoutMode: Top; %s%s }" % (ident, ("Padding: (Top: %d); " % top) if top else "", kids)


def row_badge(ident, w=150):
    """The right-hand badge of a panel row (WorldEventListRow #Badge: 150 wide, right-aligned #9aacbc)."""
    return label(ident, "", "rowBadge", w=w, h=False, anchor={"left": 8}, wrap=True, max_lines=2)


def row_action(ident, text="", kind="secondary", w=None, h=None, disabled=False, sound=None):
    """A row action button (WorldEventListRow #ActionA: small secondary 92 wide, left 4; a small Primary defaults to 150) - append
    it into the row Group."""
    return button(ident, text, kind, "small", w=w, h=h if h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H),
                  disabled=disabled, sound=sound, anchor={"left": 4})


def hover_row(ident, state="normal", h=None, pad=6, w=None, sound=None):
    """A plain list row (ItemRepairElement / ShopElementButton / WarpEntryButton): Button, LayoutMode Left, Padding 6, hover
    #000000(0.2); state selected = the vanilla active list item (#7a9cc6(0.25), hover (0.35); BasicTextButton @ActiveLabelStyle).
    Vanilla list rows are silent; sound="light" adds the button click."""
    check_id(ident)
    snd = (", Sounds: %s" % sounds(sound)) if sound else ""
    if state == "normal":
        st = "Style: ButtonStyle(Hovered: (Background: %s)%s);" % (COLOR["hover"], snd)
    elif state == "selected":
        st = "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s)%s);" % (
            COLOR["active"], COLOR["activeHover"], COLOR["activeHover"], snd)
    else:
        raise ValueError("hover_row state normal / selected")
    return "Button #%s { %sLayoutMode: Left; %s%s }" % (ident, _anchor(w, h), _padding(pad), st)


_need("R", "Button #Button {\n  LayoutMode: Left;\n  Padding: (Full: 6);\n  Style: (\n    Hovered: (\n      Background: #000000(0.2),",
      "hover row")
_need("R", "Label #Name {\n    Padding: (Horizontal: 10, Vertical: 5);\n    Style: (RenderBold: true);\n    FlexWeight: 1;", "hover row name")


def option_style(selected=False, sound=None):
    """The `Style: ButtonStyle(...);` of an option card (OverrideRespawnPointButton @DefaultRespawnButtonStyle: OptionBackgroundPatch
    Border 16, hover tint 0.7, pressed 0.85, Disabled plain; selected = InputBoxSelected, which vanilla gives only as Default - the
    kit repeats it on hover / press). Silent like vanilla (the row declares @Sounds but never applies it); sound= adds a set."""
    snd = (", Sounds: %s" % sounds(sound)) if sound else ""
    if selected:
        s = patch("inputSelected", 16)
        return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s)%s);" % (s, s, s, snd)
    return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s), Disabled: (Background: %s)%s);" % (
        patch("option", 16), patch("option", 16, tint="optionHover"), patch("option", 16, tint="optionPressed"), patch("option", 16), snd)


def option_row(ident, selected=False, h=OPTION_ROW_H, gap=OPTION_ROW_GAP, w=None, sound=None, anchor=None):
    """A selectable option card (OverrideRespawnPointButton, 50 high + 4): option_style. Put an optionName (FlexWeight 2, padding
    left 14) / optionDetail label inside."""
    check_id(ident)
    return "Button #%s { %sLayoutMode: Left; %s }" % (ident, _anchor(w, h, _merge({"bottom": gap} if gap else None, anchor)),
                                                      option_style(selected, sound))


_need("O", 'Default: (Background: (TexturePath: "../Common/OptionBackgroundPatch.png", Border: 16)),', "option row")
_need("O", '@SelectedRespawnButtonStyle = ButtonStyle(\n  Default: (Background: (TexturePath: "../Common/InputBoxSelected.png", Border: 16))',
      "option row selected")
_need("O", '  Pressed: (Background: (TexturePath: "../Common/OptionBackgroundPatch.png", Border: 16, Color: #ffffff(0.85))),\n'
      '  Disabled: (Background: (TexturePath: "../Common/OptionBackgroundPatch.png", Border: 16))\n);', "option row disabled, no Sounds")


def list_button_style(state="normal", mask=False, trial=False):
    """The `Style: TextButtonStyle(...);` of a nav / category list button (WorldEventNavButton - the nav pane vanilla shows):
    14 px uppercase #96a9be (shrinks to 11), hover #bfcdd5 on #000000(0.2); selected = white bold on #000000(0.2), with the
    TextGradient label mask when mask=True (UNVERIFIED text-mask, trial=True)."""
    sz = fs(14)
    if state == "normal":
        d = text_style(sz, "text", upper=True, shrink=11)
        hv = text_style(sz, "buttonText", upper=True, shrink=11)
        return "Style: TextButtonStyle(Default: (LabelStyle: %s), Hovered: (LabelStyle: %s, Background: %s));" % (d, hv, COLOR["hover"])
    if state == "selected":
        mk = ""
        if mask:
            _gate("text-mask", trial)
            mk = ', LabelMaskTexturePath: "%s"' % TEX["textGradient"]
        s = text_style(sz, "white", bold=True, upper=True)
        return "Style: TextButtonStyle(Default: (LabelStyle: %s%s, Background: %s), Hovered: (LabelStyle: %s%s, Background: %s));" % (
            s, mk, COLOR["hover"], s, mk, COLOR["hover"])
    raise ValueError("list_button state normal / selected")


def list_button(ident, text="", state="normal", h=32, w=None, gap=4, sound=None, mask=False, trial=False):
    """A text nav / category button (WorldEventNavButton / UIGallery CategoryButton): height 32 + gap 4, padding horizontal 10,
    list_button_style. Silent like vanilla; sound="light" adds the button click."""
    check_id(ident)
    st = list_button_style(state, mask, trial)
    if sound:
        st = st[:-2] + ", Sounds: %s);" % sounds(sound)
    return 'TextButton #%s { %sPadding: (Horizontal: 10); Text: "%s"; %s }' % (
        ident, _anchor(w, h, {"bottom": gap} if gap else None), check_text(text), st)


_need("WN", "@LabelStyle = (\n  Default: (\n    LabelStyle: (FontSize: 14, TextColor: $C.@ColorDefaultLabel, RenderUppercase: true, "
      "VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11)\n  ),\n  Hovered: (\n    LabelStyle: (FontSize: 14, "
      "TextColor: $C.@ColorButtonText, RenderUppercase: true, VerticalAlignment: Center, ShrinkTextToFit: true, "
      "MinShrinkTextToFitFontSize: 11),\n    Background: $C.@ColorSimpleButtonBackground\n  )\n);", "list button")
_need("WN", "@SelectedLabelStyle = (\n  Default: (\n    LabelStyle: (FontSize: 14, TextColor: $C.@ColorDefault, RenderBold: true, "
      "RenderUppercase: true, VerticalAlignment: Center),\n    LabelMaskTexturePath: $C.@TextHighlightGradientMask,\n"
      "    Background: $C.@ColorSimpleButtonBackground\n  ),", "list button selected")
_need("WN", "TextButton #NavButton {\n  Anchor: (Height: 32, Bottom: 4);\n  Padding: (Horizontal: 10);", "list button size")
_need("C", "@ColorDefaultLabel = #96a9be;", "list button text colour")


def setting_row(ident, label_id, label_w=600, h=SETTING_ROW_H, gap=SETTING_ROW_GAP, anchor=None, extra=""):
    """A settings row (client LabeledCheckBoxSetting look, OptionBackgroundPatch Border 16, 44 + 8, label 18 #96a9be at left 16).
    Add on_off(...) buttons after the label - the fallback until checkbox_row is probed."""
    check_id(ident)
    lab = label(label_id, "", "setting", w=label_w, h=h, anchor={"left": 16})
    return "Group #%s { %sBackground: %s; LayoutMode: Left; %s%s }" % (
        ident, _anchor(None, h, _merge({"bottom": gap} if gap else None, anchor)), patch("option", 16), _extra(extra), lab)


def scroll_list(ident, h=None, flex=None, w=None, extra_spacing=False, well=False, pad=None, anchor=None, extra=""):
    """A scrolling list (every vanilla list page; vanilla never paginates): LayoutMode TopScrolling with the vanilla scrollbar.
    well=True = the vanilla list well (WorldEventPanelPage #ListContainer: #000000(0.15), padding 4) - lists sit on it, not flat
    on the frame. Give h or flex (default flex 1)."""
    check_id(ident)
    if h is None and flex is None:
        flex = 1
    p = pad if pad is not None else (WELL_LIST_PAD if well else None)
    return "Group #%s { %s%sLayoutMode: TopScrolling; ScrollbarStyle: %s; %s%s%s}" % (
        ident, _anchor(w, h, anchor), _flex(flex), scrollbar_style(12 if extra_spacing else SCROLL_SPACING),
        ("Background: %s; " % COLOR["well"]) if well else "", _padding(p), _extra(extra))


def scrollbar_style(spacing=SCROLL_SPACING):
    """The @DefaultScrollbarStyle value (spacing 12 = @DefaultExtraSpacingScrollbarStyle)."""
    return ("(Spacing: %d, Size: %d, Background: %s, Handle: %s, HoveredHandle: %s, DraggedHandle: %s)"
            % (spacing, SCROLL_SIZE, patch("scroll", 3), patch("scrollHandle", 3), patch("scrollHandleHovered", 3),
               patch("scrollHandleDragged", 3)))


_need("C", '@DefaultScrollbarStyle = ScrollbarStyle(\n  Spacing: 6,\n  Size: 6,\n  Background: (TexturePath: "Common/Scrollbar.png", '
      'Border: 3),\n  Handle: (TexturePath: "Common/ScrollbarHandle.png", Border: 3),\n  HoveredHandle: (TexturePath: '
      '"Common/ScrollbarHandleHovered.png", Border: 3),\n  DraggedHandle: (TexturePath: "Common/ScrollbarHandleDragged.png", Border: 3)\n);',
      "scrollbar")
_need("C", "@DefaultExtraSpacingScrollbarStyle = ScrollbarStyle(\n  ...@DefaultScrollbarStyle,\n  Spacing: 12\n);", "scrollbar extra")
_need("I", "LayoutMode: TopScrolling;\n      ScrollbarStyle: $C.@DefaultScrollbarStyle;", "scroll list")


# ================================================================= separators, panels
SEPARATORS = ("content", "fancy", "vertical", "header", "footer", "panel", "form")


def separator(kind="content", ident=None, w=None, h=None, anchor=None, flex=None, extra=""):
    """content (1 px #2b3542, @ContentSeparator; WorldEventPanelPage puts it at top / bottom 8: anchor=), fancy
    (@PanelSeparatorFancy), vertical (@VerticalSeparator: 6 wide, Top -2), header (@HeaderSeparator 5 x 34), footer (2 px #19252F,
    BarterPage), panel (the 1 px @PanelTitle line), form (the 1 px #5e512c form divider, vertical margins 16: BiomeEditorPage,
    ConfigureInstanceBlockPage, LaunchPadSettingsPage)."""
    head = ("Group #%s { " % check_id(ident)) if ident else "Group { "

    def mk(anc, body):
        return head + anc + _flex(flex) + body + _extra(extra) + "}"
    if kind == "content":
        return mk(_anchor(w, h or 1, _merge(None, anchor)), "Background: %s; " % COLOR["separator"])
    if kind == "footer":
        return mk(_anchor(w, h or 2, _merge(None, anchor)), "Background: %s; " % COLOR["footerLine"])
    if kind == "panel":
        return mk(_anchor(w, h or 1, _merge(None, anchor)), "Background: %s; " % COLOR["panelLine"])
    if kind == "form":
        return mk(_anchor(w, h or 1, _merge({"vertical": FORM_LINE_MARGIN}, anchor)), "Background: %s; " % COLOR["formLine"])
    if kind == "vertical":
        return mk(_anchor(w or 6, h, _merge({"top": -2}, anchor)), "Background: %s; " % patch("vsep"))
    if kind == "header":
        return mk(_anchor(5, 34, _merge(None, anchor)), 'Background: "%s"; ' % TEX["headerSep"])
    if kind == "fancy":
        ln = 'Group { FlexWeight: 1; Background: "%s"; }' % TEX["fancyLine"]
        return mk(_anchor(w, 8, _merge(None, anchor)), 'LayoutMode: Left; %s Group { Anchor: (Width: 11); Background: "%s"; } %s ' % (
            ln, TEX["fancyDeco"], ln))
    raise ValueError("separator kind %s" % " / ".join(SEPARATORS))


_need("C", "@ContentSeparator = Group {\n  @Anchor = Anchor();\n\n  Anchor: (...@Anchor, Height: 1);\n  Background: (Color: #2b3542);",
      "content separator")
_need("C", '@VerticalSeparator = Group {\n  Background: (TexturePath: "Common/ContainerVerticalSeparator.png");\n  Anchor: (Width: 6, Top: -2);',
      "vertical separator")
_need("C", '@HeaderSeparator = Group {\n  Anchor: (Width: 5, Height: 34);\n  Background: "Common/HeaderTabSeparator.png";', "header separator")
_need("C", '  LayoutMode: Left;\n  Anchor: (...@Anchor, Height: 8);\n\n  Group {\n    FlexWeight: 1;\n'
      '    Background: "Common/ContainerPanelSeparatorFancyLine.png";\n  }\n\n  Group {\n    Anchor: (Width: 11);\n'
      '    Background: "Common/ContainerPanelSeparatorFancyDecoration.png";', "fancy separator")
_need("BP", "Group #FooterDivider {\n        Anchor: (Height: 2);\n        Background: #19252F;", "footer separator")

PANELS = {"simple": ("panelPatch", 4, 12), "full": ("fullPatch", 20, None), "secondary": ("secondaryPanel", 5, None),
          "tooltip": ("tooltip", 24, 24)}
PANEL_KINDS = ("simple", "full", "secondary", "tooltip", "well", "dark", "row", "hud")


def panel(ident, kind="simple", w=None, h=None, pad=None, layout="Top", flex=None, anchor=None, extra="", bg=None):
    """An inner panel: simple (@SimpleContainer ContainerPanelPatch Border 4, padding 12), full (@Panel ContainerFullPatch 20),
    secondary (ContainerBackgroundSecondary 5, PortalDevice info box), tooltip (the text tooltip frame, padding 24), well (THE vanilla
    inset for summaries / info boxes / form cards: #000000(0.15), padding 8 - WorldEventPanelPage #Summary, BlockSpawner entry
    rows), dark (#000000(0.3): the RespawnPage full-screen block only), row (the #101925(0.55) row panel), hud (a HUD widget:
    #000000(0.2), padding 20 / 10 - Hud/TimeLeft). pad = an int or a {left / right / top / bottom / horizontal / vertical / full} dict.
    bg (kit 1.4, colour kinds well / dark / row / hud only) = the background at runtime: a COLOR name or a J() colour (color_by
    builds one from colour NAMES), in place of the kind's colour; the kind still gives the default padding."""
    check_id(ident)
    user_bg = bg
    if kind in PANELS:
        tex, border, dpad = PANELS[kind]
        bg = patch(tex, border)
    elif kind == "well":
        bg, dpad = COLOR["well"], WELL_PAD
    elif kind == "dark":
        bg, dpad = COLOR["darkBlock"], None
    elif kind == "row":
        bg, dpad = COLOR["row"], None
    elif kind == "hud":
        bg, dpad = COLOR["hud"], {"horizontal": 20, "vertical": 10}
    else:
        raise ValueError("panel kind %s" % " / ".join(PANEL_KINDS))
    if user_bg is not None:
        if kind in PANELS:
            raise ValueError("panel(bg=) replaces the colour of a colour panel (well / dark / row / hud), not the %s texture" % kind)
        bg = color(user_bg)
    p = pad if pad is not None else dpad
    return "Group #%s { %s%s%sBackground: %s; %s%s}" % (ident, _anchor(w, h, anchor), _flex(flex), _layout(layout), bg, _padding(p),
                                                      _extra(extra))


_need("C", '@SimpleContainer = Group {\n  Background: (TexturePath: "Common/ContainerPanelPatch.png", Border: 4);\n  Padding: 12;',
      "simple panel")
_need("C", '@Panel = Group {\n  Background: (TexturePath: "Common/ContainerFullPatch.png", Border: 20);', "full panel")
_need("PD", 'Background: (TexturePath: "../Common/ContainerBackgroundSecondary.png", Border: 5);', "secondary panel")
_need("BS", "LayoutMode: Top;\n  Anchor: (Bottom: 8);\n  Background: (Color: #000000(0.15));\n  Padding: (Full: 8);", "well form card")


# ================================================================= items
_ITEM_ID_OK = re.compile(r"\A[A-Za-z0-9_*]+\Z")


def _item_id(item_id):
    """A static item id ([A-Za-z0-9_*]) or a J(expr, sample) runtime one (written inline like the deployed pages do:
    ItemId: "" + (expr) + ""; the expression must give a plain item id - wrap untrusted text in the mod's safe())."""
    if not isinstance(item_id, str) or not _ITEM_ID_OK.fullmatch(render(item_id)):
        raise ValueError("item id %r: letters, digits, _ (a runtime id: J(expr, \"Weapon_Sword_Iron\"))" % (item_id,))
    if has_j(item_id) and not _J_RE.fullmatch(item_id):
        raise ValueError("a runtime item id is one J(expr), not text around it")
    return item_id


def item_icon(ident=None, item_id=None, size=ICON, anchor=None):
    """ItemIcon (metadata-free, proven on Skyy pages). item_id static or a J(expr, sample) written inline the way the deployed pages
    write it (SkyyBazaar / SkyySacks / SkyyAuctions cells: ItemId: "" + id + ""); no Skyy page has b.set an ItemId yet."""
    head = ("ItemIcon #%s { " % check_id(ident)) if ident else "ItemIcon { "
    iid = ""
    if item_id is not None:
        iid = 'ItemId: "%s"; ' % _item_id(item_id)
    return head + _anchor(size, size, anchor) + iid + "}"


def item_frame(ident, size=SLOT_FRAME, border="slotBorder", icon_id=None, icon_size=None, anchor=None, extra="", item=None,
               cover=False, icon_anchor=None, cover_id=None):
    """The vanilla slot border (BarterTradeRow: a 68 x 68 #1a2530 group, padding 2) - with an ItemIcon inside when icon_id is given
    (icon = size - 4). border = "slotBorderHave" (green: you have it) or any kit colour.
    Kit 1.4: item = the icon's item id written INLINE (static or J(expr, "Weapon_Sword_Iron"), as item_icon; the ItemIcon is
    anonymous unless icon_id is given), icon_anchor = the icon's margins, cover=True = the vanilla sold-out cover over it
    (BarterTradeRow #OutOfStockOverlay colour #0a0e12(0.75), Anchor Full 0; cover_id names it) - a picked-at-runtime cover:
    choose(J("on"), item_frame(...), item_frame(..., cover=True))."""
    check_id(ident)
    kids = []
    if icon_id or item is not None:
        kids.append(item_icon(icon_id, item, icon_size or size - 4, anchor=icon_anchor))
    if cover:
        kids.append(group(cover_id, None, anchor={"full": 0}, bg="cardOverlay"))
    return "Group #%s { %sBackground: %s; Padding: (Full: 2); %s%s}" % (ident, _anchor(size, size, anchor), color(border), _extra(extra),
                                                                     (" ".join(kids) + " ") if kids else "")


def item_slot(ident, slot_id, size=SLOT_FRAME, quality=True, quantity=False, trial=False):
    """UNVERIFIED (trial=True): the vanilla item with its QUALITY slot frame and no ItemStack (BarterTradeRow #OutputSlot):
    a 68 x 68 border group + ItemSlot (ShowQualityBackground); set the item with b.set("#slot_id.ItemId", id)."""
    _gate("itemslot", trial)
    check_id(ident)
    check_id(slot_id)
    return "Group #%s { %sBackground: %s; Padding: (Full: 2); ItemSlot #%s { Anchor: (Full: 0); ShowQualityBackground: %s; %s} }" % (
        ident, _anchor(size, size), COLOR["slotBorder"], slot_id, "true" if quality else "false",
        "" if quantity else "ShowQuantity: false; ")


_need("B", "ItemSlot #OutputSlot {\n              Anchor: (Full: 0);\n              ShowQualityBackground: true;", "item slot")


def quality_frame(ident, quality="Default", size=SLOT_FRAME, icon_id=None, icon_size=None, trial=False, anchor=None):
    """UNVERIFIED (trial=True, quality-frame): an item icon on the game's own quality slot frame (the SlotTexture of
    Server/Item/Qualities/<quality>.json: "../ItemQualities/Slots/Slot<frame>.png", outside the custom root). quality = a QUALITY
    name or "Default" (no quality). Runtime quality: build one frame per quality or b.set the Background (UNVERIFIED)."""
    _gate("quality-frame", trial)
    check_id(ident)
    frame = "Default" if quality == "Default" else QUALITY_SLOT.get(quality)
    if frame is None:
        raise ValueError("quality %r (one of Default, %s)" % (quality, ", ".join(sorted(QUALITY_SLOT))))
    inner = (" " + item_icon(icon_id, None, icon_size or size - 4)) if icon_id else ""
    return 'Group #%s { %sBackground: "%s"; Padding: (Full: 2);%s }' % (ident, _anchor(size, size, anchor), TEX["qSlot" + frame], inner)


def item_grid_style(slot=74, icon=64, spacing=2, slot_bg=False, trial=False):
    """The Style value of an ItemGrid (SlotSize / SlotIconSize / SlotSpacing; client inventory 74 / 64 / 2). slot_bg = the
    custom-kit slot background (EntitySpawnPage; UNVERIFIED inline, trial=True). Keep the ItemGridSlot rule: new ItemStack(id, qty)."""
    bg = ""
    if slot_bg:
        _gate("slot-background", trial)
        bg = ', SlotBackground: "%s"' % TEX["slot"]
    return "(SlotSize: %s, SlotIconSize: %s, SlotSpacing: %s%s)" % (_num(slot), _num(icon), _num(spacing), bg)


_need("ES", 'SlotBackground: "../Common/BlockSelectorSlotBackground.png"', "grid slot background")

GRID_SLOT, GRID_ICON, GRID_SPACING = 74, 64, 2       # the client inventory grid (@DefaultItemSlotSize / SlotIconSize / Spacing)
GRID_WELL_PAD = WELL_LIST_PAD                        # the grid sits 4 px inside the well (Anchor Left / Top, no Padding)
_need("CG", "@DefaultItemSlotSpacing = 2;\n@DefaultItemSlotSize = 74;", "grid slot 74 / spacing 2 (client inventory)")
_need("CG", "@DefaultItemGridStyle = ItemGridStyle(\n  SlotSpacing: @DefaultItemSlotSpacing,\n  SlotSize: @DefaultItemSlotSize,\n"
      "  SlotIconSize: 64,", "grid icon 64 (client inventory)")
_need("CC", "Anchor: (Width: $InGame.@DefaultItemSlotSize * 3 + $InGame.@DefaultItemSlotSpacing * 2 + $InGame.@PanelPadding,",
      "grid width = cols x slot + (cols - 1) x spacing (client BasicCraftingPanel)")


def item_grid(ident, cols, rows, slot=GRID_SLOT, icon=GRID_ICON, spacing=GRID_SPACING, drag=False, tooltips=True, well=True,
              box_id=None, w=None, h=None, anchor=None, slot_bg=False, trial=False):
    """An ItemGrid written the way the deployed pages write it (SkyyAuctions item view, SkyyEssentials trade columns, SkyyMenu
    launcher, SkyyHud editor): Anchor Width / Height, SlotsPerRow, AreItemsDraggable (drag=True only for a drag canvas like the
    HUD editor), InfoDisplay: None when tooltips=False (no hover tooltip that could stay up after Esc - SkyyAuctions), and the Style
    SlotSize / SlotIconSize / SlotSpacing, by default the client inventory's 74 / 64 / 2. Size = cols x slot + (cols - 1) x spacing
    (the client's own grid anchors, BasicCraftingPanel); give w / h when cols / rows / slot are J() runtime values.
    well=True (default) = the vanilla list well behind it: Group #<box_id or ident+'Box'> (#000000(0.15)) with the grid at Left /
    Top 4 - no textures, since the client's slot frame (Pages/Inventory/Slot.png) is client-only and SlotBackground
    (BlockSelectorSlotBackground) is UNVERIFIED inline (slot_bg=True needs trial=True). well=False = the bare grid (anchor= then
    goes on the grid). FILL IT ONLY through java_grid_methods() / java_grid_fill(): every slot is new ItemGridSlot(new
    ItemStack(id, qty)) (an ItemStack that may carry metadata in an ItemGridSlot disconnects the client). Bind SlotClicking on
    #ident for clicks (SkyyMenu launcher); set the slots with java_set_raw(ident, "Slots", "slotsList")."""
    check_id(ident)
    for v, what in ((cols, "cols"), (rows, "rows")):
        n = _sample_num(v)
        if n is None or n < 1 or int(n) != n:
            raise ValueError("item_grid %s must be an int >= 1 or a J() with a digit sample: %r" % (what, v))
    for v, what in ((slot, "slot size"), (icon, "icon size")):
        _size(v, what)
    _num(spacing, "slot spacing")
    if _sample_num(spacing) is None or _sample_num(spacing) < 0:
        raise ValueError("slot spacing must be >= 0")
    static = all(isinstance(v, int) and not isinstance(v, bool) for v in (cols, rows, slot, spacing))
    if w is None or h is None:
        if not static:
            raise ValueError("item_grid with J() cols / rows / slot / spacing needs w= and h= (the grid's pixel size)")
        w = w if w is not None else cols * slot + (cols - 1) * spacing
        h = h if h is not None else rows * slot + (rows - 1) * spacing
    if static and isinstance(icon, int) and icon > slot:
        raise ValueError("item_grid icon %d is larger than its slot %d" % (icon, slot))
    grid_anchor = {"left": GRID_WELL_PAD, "top": GRID_WELL_PAD} if well else anchor
    mk = ("ItemGrid #%s { %sSlotsPerRow: %s; AreItemsDraggable: %s; %sStyle: %s; }"
          % (ident, _anchor(w, h, grid_anchor), _num(cols, "cols"), "true" if drag else "false",
             "" if tooltips else "InfoDisplay: None; ",
             item_grid_style(slot, icon, spacing, slot_bg=slot_bg, trial=trial)))
    if not well:
        return mk
    box = check_id(box_id or ident + "Box")
    return "Group #%s { %sBackground: %s; %s }" % (box, _anchor(_plus(w, 2 * GRID_WELL_PAD), _plus(h, 2 * GRID_WELL_PAD), anchor),
                                                   COLOR["well"], mk)


def _plus(v, n):
    """v + n for a size that is an int or ONE J(expr, sample) (then a J of (expr) + n with the sample moved too)."""
    if isinstance(v, int) and not isinstance(v, bool):
        return v + n
    m = _J_RE.fullmatch(v) if isinstance(v, str) else None
    if not m or _sample_num(v) is None:
        raise ValueError("a size here is an int or one J(expr, sample) with a number sample: %r" % (v,))
    return J("(%s) + %d" % (m.group(1), n), str(int(_sample_num(v)) + n))


GRID_SLOT_CLASS = "com.hypixel.hytale.server.core.ui.ItemGridSlot"
ITEM_STACK_CLASS = "com.hypixel.hytale.server.core.inventory.ItemStack"
_JAVA_CLASS_OK = re.compile(r"\A[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*\Z")


def _java_class(name, what):
    if not isinstance(name, str) or not _JAVA_CLASS_OK.fullmatch(name):
        raise ValueError("%s must be a Java class name: %r" % (what, name))
    return name


def java_grid_methods(prefix="grid", igs=GRID_SLOT_CLASS, stack=ITEM_STACK_CLASS):
    """Java source of the four static methods (CtNewMethod.make each, IN THIS ORDER: a method comes before its callers) that are
    the only way a Skyy page should fill an ItemGrid - every slot is new ItemGridSlot(new ItemStack(id, qty)), never a stack the
    player holds (its metadata in an ItemGridSlot disconnects the client; HANDOFF section 2):
      <prefix>Slot(String itemId, int qty)            one slot; a null / blank id or qty < 1 = an empty slot
      <prefix>SlotOf(ItemStack s)                     a slot from s's item id + quantity ONLY (null / empty stack = empty slot)
      <prefix>Slots(String[] ids, int[] qtys, int n)  n slots (missing ids = empty; qtys null or short = 1 each)
      <prefix>SlotsOf(ItemStack[] a, int n)           n slots from a snapshot, id + quantity only
    A stack's display name / description is gone in the copy: set it on the slot yourself (ItemGridSlot.setName /
    setDescription, SkyyEssentials 0.1.5 gridSlot) if the page needs it. Then b.set the list: java_set_raw(id, "Slots", "list").
    igs / stack = the two class names (the defaults are the engine's)."""
    if not isinstance(prefix, str) or not re.fullmatch(r"[a-z][A-Za-z0-9]*", prefix):
        raise ValueError("java_grid_methods prefix: a lower-case Java name like grid")
    G, S = _java_class(igs, "igs"), _java_class(stack, "stack")
    p = prefix
    return [
        ("public static %(G)s %(p)sSlot(String itemId, int qty) {\n"
         "  if (itemId == null || itemId.trim().length() == 0 || qty < 1) return new %(G)s();\n"
         "  return new %(G)s(new %(S)s(itemId, qty));\n}") % {"G": G, "S": S, "p": p},
        ("public static %(G)s %(p)sSlotOf(%(S)s s) {\n"
         "  if (s == null || s.isEmpty()) return new %(G)s();\n"
         "  return %(p)sSlot(s.getItemId(), s.getQuantity());\n}") % {"G": G, "S": S, "p": p},
        ("public static java.util.ArrayList %(p)sSlots(String[] ids, int[] qtys, int n) {\n"
         "  java.util.ArrayList l = new java.util.ArrayList();\n"
         "  for (int i = 0; i < n; i++) {\n"
         "    String id = (ids != null && i < ids.length) ? ids[i] : null;\n"
         "    int q = (qtys != null && i < qtys.length) ? qtys[i] : 1;\n"
         "    l.add(%(p)sSlot(id, q));\n  }\n  return l;\n}") % {"p": p},
        ("public static java.util.ArrayList %(p)sSlotsOf(%(S)s[] a, int n) {\n"
         "  java.util.ArrayList l = new java.util.ArrayList();\n"
         "  for (int i = 0; i < n; i++) l.add(%(p)sSlotOf((a != null && i < a.length) ? a[i] : null));\n"
         "  return l;\n}") % {"S": S, "p": p},
    ]


def java_grid_fill(ident, items, var="gridSlots", b="b", igs=GRID_SLOT_CLASS, stack=ITEM_STACK_CLASS):
    """Java statements that fill ItemGrid #ident with FIXED items (a showcase, a recipe, a probe page): a local java.util.ArrayList
    `var` (unique per method) of new ItemGridSlot(new ItemStack(id, qty)) - items = [(item_id, qty) or None for an empty slot];
    item_id static or J(expr) (a Java String), qty an int >= 1 or J(expr) (a Java int) - then b.set("#ident.Slots", var)."""
    check_id(ident)
    if not isinstance(var, str) or not re.fullmatch(r"[a-z][A-Za-z0-9]*", var):
        raise ValueError("java_grid_fill var: a lower-case Java local name")
    G, S = _java_class(igs, "igs"), _java_class(stack, "stack")
    out = ["java.util.ArrayList %s = new java.util.ArrayList();" % var]
    for it in items:
        if it is None:
            out.append("%s.add(new %s());" % (var, G))
            continue
        iid, qty = it
        _item_id(iid)
        if has_j(qty):
            q = "(" + _J_RE.fullmatch(qty).group(1) + ")" if _J_RE.fullmatch(qty) else None
            if q is None:
                raise ValueError("a runtime quantity is one J(expr)")
        elif isinstance(qty, int) and not isinstance(qty, bool) and qty >= 1:
            q = str(qty)
        else:
            raise ValueError("quantity must be an int >= 1 or J(expr): %r" % (qty,))
        out.append("%s.add(new %s(new %s(%s, %s)));" % (var, G, S, java_value(iid), q))
    out.append(java_set_raw(ident, "Slots", var, b))
    return "\n".join(out)


def item_grid_java_is_safe(java_src, igs=GRID_SLOT_CLASS, stack=ITEM_STACK_CLASS):
    """True when every `new <ItemGridSlot>(...)` in a Java text is empty or takes a `new <ItemStack>(...)` built right there (the
    metadata rule, as the kit's own grid Java does it); the test and tools/ci/lint.py (WARN) apply the same rule to build scripts."""
    G, S = re.escape(igs), re.escape(stack)
    bad = re.compile(r"new\s+%s\s*\((?!\s*\)|\s*new\s+%s\s*\()" % (G, S))
    return bad.search(java_src) is None


ICON_CELL_STATES = ("normal", "selected", "disabled", "empty", "static")       # "static" = kit 1.4 (a non-clickable Group)
ICON_CELL_LOOKS = ("row", "plain")


def _cell_style(look, state, sound):
    snd = (", Sounds: %s" % sounds(sound)) if sound and state in ("normal", "selected") else ""
    if look == "row":                    # WorldEventListRow @NormalRowStyle / @SelectedRowStyle / @StaticRowStyle
        d, hv, pr = {"normal": ("row", "rowHover", "rowPressed"), "selected": ("selected", "selected", "selected")}.get(
            state, ("row", "row", "row"))
    else:                                # ItemRepairElement / BasicTextButton: no back, hover #000000(0.2), active #7a9cc6(0.25)
        d, hv, pr = {"normal": ("transparent", "hover", "hover"), "selected": ("active", "activeHover", "activeHover")}.get(
            state, ("transparent", "transparent", "transparent"))
    return "Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), Pressed: (Background: %s)%s);" % (
        COLOR[d], COLOR[hv], COLOR[pr], snd)


def icon_cell(ident, item=None, size=74, state="normal", icon=None, qty=False, look="row", w=None, h=None, sound="light",
              icon_left=None, anchor=None, extra=""):
    """A compact clickable item cell (Bazaar product cells, Auctions picker cells, Accessories rows, Trees nodes, Menu launcher) in
    the cell pattern the deployed pages already use (SkyyBazaar / SkyyAuctions / SkyyTrees / SkyySacks: a Button with a ButtonStyle
    holding an ItemIcon and a quantity Label, children placed by Anchor) with vanilla state looks from kit colours:
      look "row" (default) = the WorldEventListRow palette: normal #101925(0.55), hover #132033(0.8), pressed #182a40(0.9) + the
        light click; selected = #4274a5 (@SelectedRowStyle); disabled / empty = the static row colour, silent;
      look "plain" = the ItemRepairElement / BasicTextButton palette: no back, hover #000000(0.2); selected #7a9cc6(0.25/0.35).
    disabled also lays the vanilla sold-out cover (#0a0e12(0.75), BarterTradeRow) over the icon; empty = no icon. Neither is
    un-clickable (the Disabled: true property is UNVERIFIED): leave them unbound or refuse the click. item = a static item id or
    J(expr, sample) written inline (as the deployed cells do); None = an ItemIcon without an id. ItemIcon #<ident>Ic is icon px
    (default size - 10), centred (icon_left = its left margin for a wide cell with text next to it; append your labels into
    #ident with Anchor Left / Top). qty: False, True (an empty 15 px bold white label #<ident>Qty at the bottom right - b.set it)
    or static digits ("64"). w / h override size for a wide cell. sound=None = silent. A runtime state: choose(J("i == sel"),
    icon_cell(..., state="selected"), icon_cell(...)).
    state "static" (kit 1.4) = a NON-clickable cell: a Group (not a Button, no style, no sound) in the static row colour (look
    "row") or with no back (look "plain"), with the icon and the quantity - a display cell (a reward, an ingredient)."""
    check_id(ident)
    if state not in ICON_CELL_STATES:
        raise ValueError("icon_cell state %s" % " / ".join(ICON_CELL_STATES))
    if look not in ICON_CELL_LOOKS:
        raise ValueError("icon_cell look %s" % " / ".join(ICON_CELL_LOOKS))
    cw = w if w is not None else size
    ch = h if h is not None else size
    for v, what in ((cw, "cell width"), (ch, "cell height")):
        if not isinstance(v, int) or isinstance(v, bool) or v < 24:
            raise ValueError("icon_cell %s must be an int >= 24: %r" % (what, v))
    ic = icon if icon is not None else min(cw, ch) - 10
    if not isinstance(ic, int) or isinstance(ic, bool) or ic < 8 or ic > min(cw, ch):
        raise ValueError("icon_cell icon size %r must fit the cell" % (ic,))
    top = (ch - ic) // 2
    left = icon_left if icon_left is not None else ((cw - ic) // 2 if cw == ch else top)
    kids = []
    if state != "empty":
        kids.append(item_icon(ident + "Ic", item, ic, anchor={"left": left, "top": top}))
    if state == "disabled":
        kids.append("Group #%sOut { Anchor: (Full: 0); Background: %s; }" % (ident, COLOR["cardOverlay"]))
    if qty is not False and state != "empty":
        if qty is True:
            qtext = ""
        elif isinstance(qty, str) and re.fullmatch(r"[0-9]{1,6}", qty):
            qtext = qty
        else:
            raise ValueError("icon_cell qty: False, True (b.set #<id>Qty.Text) or static digits like \"64\"; got %r" % (qty,))
        kids.append(label(ident + "Qty", qtext, "quantity", w=cw - 8, h=20, anchor={"right": 4, "bottom": 3}))
    if state == "static":
        return "Group #%s { %s%s%s%s}" % (ident, _anchor(cw, ch, anchor), ("Background: %s; " % COLOR["row"]) if look == "row" else "",
                                          _extra(extra), (" ".join(kids) + " ") if kids else "")
    return "Button #%s { %s%s %s%s}" % (ident, _anchor(cw, ch, anchor), _cell_style(look, state, sound), _extra(extra),
                                        (" ".join(kids) + " ") if kids else "")


def card(ident, w=CARD_W, h=CARD_H, inner_id=None, margin=CARD_MARGIN, sold_out=False, out_id=None, anchor=None, flex=None, extra=""):
    """A trade / product card (BarterTradeRow): a w x h Group #identBox with padding `margin` (5: the vanilla 10 px card gap) holding
    Button #ident (Anchor Full 0: bind it; #252f3a, hover gold #c9a050, pressed #a08040, disabled #1a1e24, padding 2, ButtonsLight)
    with the inner Group #<inner_id or ident+'In'> #1c2835 (LayoutMode Top) for the icon and texts (label kinds cardCaption, have,
    stock, quantity). sold_out=True adds the vanilla out-of-stock cover #identOut (#0a0e12(0.75)) with its label #identOutL (b.set the
    Text). margin=0 = the button itself is w x h (the kit 1.0 card). flex= = a flex width instead of w."""
    check_id(ident)
    inner = check_id(inner_id or ident + "In")
    if flex is not None:
        w = None
    anc = _anchor(w, h, anchor) + _flex(flex)
    over = ""
    if sold_out:
        oid = check_id(out_id or ident + "Out")
        over = " Group #%s { Anchor: (Full: 0); Background: %s; LayoutMode: CenterMiddle; %s }" % (
            oid, COLOR["cardOverlay"], label(oid + "L", "", "outOfStock", align="Center"))
    btn = ("Button #%s { %sLayoutMode: Full; Padding: (Full: 2); Style: ButtonStyle(Default: (Background: %s), Hovered: (Background: %s), "
           "Pressed: (Background: %s), Disabled: (Background: %s), Sounds: %s); Group #%s { Anchor: (Full: 0); LayoutMode: Top; "
           "Background: %s; }%s }" % (ident, "Anchor: (Full: 0); " if margin else anc, COLOR["card"], COLOR["cardHover"],
                                      COLOR["cardPressed"], COLOR["cardDisabled"], sounds("light"), inner, COLOR["cardInner"], over))
    if not margin:
        return btn[:-1] + _extra(extra) + "}"
    return "Group #%sBox { %sPadding: (Horizontal: %s, Vertical: %s); %s%s }" % (ident, anc, _num(margin), _num(margin), _extra(extra), btn)


_need("B", "Sounds: $C.@ButtonSounds,", "card sounds")
_need("B", "ItemSlotButton #TradeButton {\n    Anchor: (Full: 0);\n    LayoutMode: Full;\n    Padding: 2;", "card button fills the box")
_need("B", "Group #OutOfStockOverlay {\n      Anchor: (Full: 0);\n      Background: #0a0e12(0.75);\n      LayoutMode: CenterMiddle;",
      "card sold-out cover")


# ================================================================= feedback: bars, progress, tooltips, spinner, tiles
def bar(ident, w, h, fill, col="progressFill", track="progressTrack", anchor=None, flex=None, extra=""):
    """FALLBACK stat / progress bar from two flat Groups (the proven Skyy way): track #1a2030 + fill #aa7c4a - the vanilla
    @CircularProgressBar palette laid flat, not a vanilla horizontal bar (progressBlue #4a7caa / progressGreen #7caa4a are the
    gallery's other two). Prefer progress(kind="memories") once probed. fill = the filled width in px (int >= 0 or J());
    flex= (w=None) = a flex-width track (then compute fill from the width you gave the row)."""
    check_id(ident)
    if isinstance(fill, (int, float)) and not isinstance(fill, bool) and fill < 0:
        raise ValueError("bar fill must be >= 0")
    return "Group #%s { %s%sBackground: %s; %sGroup #%sFill { Anchor: (Left: 0, Width: %s, Height: %s); Background: %s; } }" % (
        ident, _anchor(w if flex is None else None, h, anchor), _flex(flex), color(track), _extra(extra), ident, _num(fill, "fill"),
        _num(h), color(col))


def progress(ident, w=None, h=None, value=0.0, kind="default", trial=False, anchor=None, flex=None, extra=""):
    """UNVERIFIED (trial=True): a vanilla ProgressBar element; set it with java_set(id, "Value", 0.5) / java_set_raw(id, "Value",
    "f"). kind "default" = @ProgressBar (284 x 6, ProgressBar / Fill / Effect textures; only the UI Gallery shows it). kind
    "memories" = the one textured bar a real page shows (MemoriesCategoryPanel: Group #identBox MemoriesBarBg 22 high, padding 6,
    holding ProgressBar #ident (fill + tip effect 114 x 32 at 104) and the texture overlay ProgressBar #identTex - set BOTH Values;
    also gated by memories-bar)."""
    _gate("progress-element", trial)
    check_id(ident)
    v = _num(float(value))
    if kind == "default":
        anc = _anchor(None if flex is not None else (w or PROGRESS_W), h or PROGRESS_H, anchor) + _flex(flex)
        return ('ProgressBar #%s { %sBackground: "%s"; BarTexturePath: "%s"; EffectTexturePath: "%s"; EffectWidth: 102; EffectHeight: 58; '
                'EffectOffset: 74; Value: %s; %s}' % (ident, anc, TEX["progress"], TEX["progressFill"], TEX["progressEffect"], v,
                                                      _extra(extra)))
    if kind == "memories":
        _gate("memories-bar", trial)
        anc = _anchor(None if flex is not None else (w or MEMBAR_W), h or MEMBAR_H, anchor) + _flex(flex)
        return ('Group #%sBox { %sBackground: "%s"; Padding: (Full: %d); %sProgressBar #%s { BarTexturePath: "%s"; EffectTexturePath: "%s"; '
                'EffectWidth: 114; EffectHeight: 32; EffectOffset: 104; Value: %s; } ProgressBar #%sTex { BarTexturePath: "%s"; Value: %s; } }'
                % (ident, anc, TEX["memBarBg"], MEMBAR_PAD, _extra(extra), ident, TEX["memBarFill"], TEX["memBarTip"], v, ident,
                   TEX["memBarTexture"], v))
    raise ValueError("progress kind default / memories")


_need("C", '  Background: "Common/ProgressBar.png";\n  BarTexturePath: "Common/ProgressBarFill.png";\n'
      '  EffectTexturePath: "Common/ProgressBarEffect.png";\n  EffectWidth: 102;\n  EffectHeight: 58;\n  EffectOffset: 74;', "progress bar")
_need("MC", 'ProgressBar #MemoriesProgressBar {\n            BarTexturePath: "MemoriesProgress/MemoriesBarFill.png";\n'
      '            EffectTexturePath: "MemoriesProgress/MemoriesBarTipOfTheBar.png";\n            EffectWidth: 114;\n'
      '            EffectHeight: 32;\n            EffectOffset: 104;', "memories bar")
_need("MC", 'ProgressBar #MemoriesProgressBarTexture {\n            BarTexturePath: "MemoriesProgress/MemoriesBarTexture.png";',
      "memories bar texture")


def tooltip_style():
    """The @DefaultTextTooltipStyle value."""
    return "(Background: %s, MaxWidth: %d, LabelStyle: (Wrap: true, FontSize: 16), Padding: %d)" % (
        patch("tooltip", TOOLTIP_BORDER), TOOLTIP_MAX_W, TOOLTIP_PAD)


def tooltip(text, trial=False):
    """UNVERIFIED (trial=True): the properties that give any element the vanilla text tooltip (@DefaultTextTooltipStyle):
    pass the result as extra= to a builder. Static text only ([A-Za-z0-9 <>/-])."""
    _gate("tooltip", trial)
    return 'TooltipText: "%s"; TextTooltipStyle: %s;' % (check_text(text, "TooltipText"), tooltip_style())


_need("C", '@DefaultTextTooltipStyle = TextTooltipStyle(\n  Background: (TexturePath: "Common/TooltipDefaultBackground.png", Border: 24),\n'
      '  MaxWidth: 400,\n  LabelStyle: (Wrap: true, FontSize: 16),\n  Padding: 24\n);', "text tooltip")
_need("T", "TextTooltipStyle: $C.@DefaultTextTooltipStyle;", "tooltip usage")
_need("CT", "@TextureBorder = 24;", "item tooltip frame border")
_need("CT", "Padding: (Full: 24, Top: 21);", "item tooltip padding")


def tooltip_panel(ident, w=360, h=None, quality=None, trial=False, anchor=None):
    """A tooltip-like info panel for tipName / tipId / tipDesc / tipStat labels: the text tooltip frame (padding 24), or with
    quality= the game's own item tooltip frame of that quality (UNVERIFIED quality-frame, trial=True: "../ItemQualities/Tooltips/
    ItemTooltip<frame>.png" Border 24, the client ItemTooltip padding 24 / top 21)."""
    if quality is None:
        return panel(ident, "tooltip", w=w, h=h, pad=TOOLTIP_PAD, anchor=anchor)
    _gate("quality-frame", trial)
    check_id(ident)
    frame = QUALITY_TIP.get(quality) if quality != "Default" else "Default"
    if frame is None:
        raise ValueError("quality %r (one of Default, %s)" % (quality, ", ".join(sorted(QUALITY_TIP))))
    return "Group #%s { %sLayoutMode: Top; Background: %s; Padding: (Full: %d, Top: 21); }" % (
        ident, _anchor(w, h, anchor), patch("qTip" + frame, TOOLTIP_BORDER), TOOLTIP_PAD)


def spinner(ident=None, size=SPINNER, trial=False, anchor=None):
    """UNVERIFIED (trial=True): the vanilla loading spinner (@DefaultSpinner: Sprite Common/Spinner.png, 32 x 32 frames, 8 per row,
    72 frames at 30 fps) - for "profile loading" states."""
    _gate("spinner", trial)
    head = ("Sprite #%s { " % check_id(ident)) if ident else "Sprite { "
    return head + _anchor(size, size, anchor) + 'TexturePath: "%s"; Frame: (Width: 32, Height: 32, PerRow: 8, Count: 72); ' \
                                                'FramesPerSecond: 30; }' % TEX["spinner"]


_need("C", '@DefaultSpinner = Sprite {\n  @Anchor = ();\n  Anchor: (...@Anchor, Width: 32, Height: 32);\n  TexturePath: "Common/Spinner.png";\n'
      '  Frame: (Width: 32, Height: 32, PerRow: 8, Count: 72);\n  FramesPerSecond: 30;', "spinner")

TILE_STATES = ("default", "selected", "complete", "empty")


def tile(ident, text="", state="default", w=TILE_W, h=TILE_H, gap=TILE_GAP, sound="light", trial=False, anchor=None, extra=""):
    """UNVERIFIED (trial=True): a selectable picture tile (Memories: Pages/Memories/Tiles/Tile*.png Border 8, 144 x 176, margins
    right / bottom 16, ButtonsLight) - for pickers (classes, islands, cosmetics). state default (hover = TileHovered), selected
    (TileSelected), complete (TileComplete), empty (a TileEmpty Group, no click). The name is a tileName label (Secondary 15 bold
    uppercase #b4c8c9, bottom, padding bottom 10); put an item_icon / picture group in it. Lay tiles out in LayoutMode
    LeftCenterWrap."""
    _gate("tile", trial)
    check_id(ident)
    if state not in TILE_STATES:
        raise ValueError("tile state %s" % " / ".join(TILE_STATES))
    an = _merge({"right": gap, "bottom": gap} if gap else None, anchor)
    tx = lambda k: patch(k, TILE_BORDER)
    if state == "empty":
        return "Group #%s { %sBackground: %s; %s}" % (ident, _anchor(w, h, an), tx("tileEmpty"), _extra(extra))
    lab = text_style(fs(15), "title", bold=True, upper=True, halign="Center", valign="End", wrap=True, font=FONT_SECONDARY)
    d = {"default": "tileDefault", "selected": "tileSelected", "complete": "tileComplete"}[state]
    hv = "tileSelected" if state == "selected" else "tileHovered"
    snd = (", Sounds: %s" % sounds(sound)) if sound else ""
    return ('TextButton #%s { %sPadding: (Bottom: 10); Text: "%s"; Style: TextButtonStyle(Default: (LabelStyle: %s, Background: %s), '
            'Hovered: (LabelStyle: %s, Background: %s)%s); %s}' % (ident, _anchor(w, h, an), check_text(text), lab, tx(d), lab, tx(hv), snd,
                                                                _extra(extra)))


_need("MM", 'Background: (TexturePath: "Tiles/TileDefault.png", Border: 8),', "tile default")
_need("MM", 'Background: (TexturePath: "Tiles/TileHovered.png", Border: 8),', "tile hovered")
_need("MM", 'Background: (TexturePath: "Tiles/TileSelected.png", Border: 8),', "tile selected")
_need("MM", 'Background: (TexturePath: "Tiles/TileEmpty.png", Border: 8);', "tile empty")
_need("M", 'Background: (TexturePath: "Tiles/TileComplete.png", Border: 8);', "tile complete")
_need("M", "TextButton #Button {\n    Padding: (Bottom: 10);\n    Style: (\n      Sounds: $Sounds.@ButtonsLight,", "tile button")


def gradient_label(ident, text="", size=20, trial=False):
    """UNVERIFIED (trial=True): a big highlighted heading (UI Gallery category title: TextGradient mask, bold uppercase white)."""
    _gate("text-mask", trial)
    return label(ident, text, "strong", size=size, upper=True, extra='MaskTexturePath: "%s"' % TEX["textGradient"])


_need("C", '@TextHighlightGradientMask = "Common/TextGradient.png";', "text gradient")


# ================================================================= Appends, page shell, confirm dialog
class Appends(list):
    """A list of (parent id or None for the page root, markup) plus .sets, the b.set lines [(id, prop, value)] that go with them
    (Appends.text, pager, confirm_view fill it). .java(b) = the appendInline statements, then the b.set lines; .check(prefix) =
    check_page (also: every b.set target exists). extend / += carry the other list's .sets along."""

    def __init__(self, items=()):
        list.__init__(self, items)
        self.sets = list(getattr(items, "sets", ()))

    def extend(self, items):
        list.extend(self, items)
        self.sets.extend(getattr(items, "sets", ()))

    def __iadd__(self, items):
        self.extend(items)
        return self

    def java(self, b="b", page_root=True, sets=None):
        lines = [java_append(p, mk, b, page_root) for p, mk in self]
        lines += [java_set(i, pr, v, b) for i, pr, v in list(self.sets) + list(sets or [])]
        return "\n".join(lines)

    def check(self, prefix=None, known_parents=()):
        return check_page(self, prefix, known_parents)

    def markups(self):
        return [mk for _p, mk in self]

    def text(self, parent, ident=None, text="", kind="default", **kw):
        """Append a label (a label() kind + its options) WITH its text, whatever the text holds: proven static text
        ([A-Za-z0-9 <>/-]) goes inline; static text with other characters (commas, dots, "?", "%", ...) or a J() runtime text goes
        in as an empty label + a b.set line in .sets - the SkyyBank #SkyyBCapMid pattern, so a builder never splits it by hand.
        ident=None and a b.set text = an id made from the parent: <parent>Tx<n> (the first n free in this list). Returns the
        label id (None for an anonymous inline label)."""
        if parent is None:
            raise ValueError("Appends.text needs a parent element (not the page root)")
        if not isinstance(text, str):
            raise ValueError("Appends.text: text must be a str or J(): %r" % (text,))
        inline = not has_j(text) and TEXT_OK.fullmatch(text) is not None
        if not inline and not ident:
            base = parent[1:] if parent.startswith("#") else parent
            taken = set(render(i) for _p, mk in self for v in _variants(mk)
                        for i in (m.group(2) for m in _ELEM_OPEN.finditer(_strip_quoted(render(v)))) if i)
            n = 0
            while render(base + "Tx%d" % n) in taken:
                n += 1
            ident = base + "Tx%d" % n
        self.append((parent, label(ident, text if inline else "", kind, **kw)))
        if not inline:
            self.sets.append((ident, "Text", text))
            _fit_label_kw(ident, text, kind, kw)        # kit 1.4: a b.set static text is measured too (the label saw "")
        return ident

    def add(self, parent, markup):
        """Kit 1.4: append (parent, markup) and bring a Markup's .sets (the b.set lines of its texts; a Choice: both looks' must
        be the same) along. Returns the markup's OUTER height (Anchor Height + Top + Bottom (+ 2 x Vertical / Full); None when
        it sets no Height; a Choice: both looks must agree) - the height accounting of a LayoutMode Top column: add up what
        add() returns, or ask used_height(ap, container)."""
        self.append((parent, markup))
        self.sets.extend(_markup_sets(markup))
        return outer_size(markup)[1]

    def used(self, container, axis="h"):
        """used_height(self, container) (axis "h", a LayoutMode Top column) or used_width (axis "w", a LayoutMode Left row)."""
        return used_height(self, container) if axis == "h" else used_width(self, container)

    def button(self, parent, ident, text="", kind="secondary", size="normal", trial=False, **kw):
        """Kit 1.4: append a button() WITH its label, whatever the text holds: proven static text goes inline; other text
        (commas, "?", brackets, a J() runtime value) goes in as an empty label + a b.set("#id.Text") line - UNVERIFIED
        (button-text: no Skyy page has b.set a TextButton's Text yet; trial=True until probe page 20 works). Returns ident."""
        if parent is None:
            raise ValueError("Appends.button needs a parent element (not the page root)")
        if not isinstance(text, str):
            raise ValueError("Appends.button: text must be a str or J(): %r" % (text,))
        inline = not has_j(text) and TEXT_OK.fullmatch(text) is not None
        if not inline:
            _gate("button-text", trial)
        self.append((parent, button(ident, text if inline else "", kind, size, **kw)))
        if not inline:
            self.sets.append((ident, "Text", text))
            if kw.get("fit", True) and kw.get("flex") is None and not has_j(text):
                lsz, _bh, bp = BUTTON_SIZES[size]
                w = kw.get("w")
                if w is None:
                    w = (PRIMARY_SMALL_W if kind == "primary" else ROW_ACTION_W) if size == "small" else BTN_MIN_W
                _fit_button(ident, text, lsz, w, bp)
        return ident


class Part(Appends):
    """What pager / confirm_view return: the Appends (+ .sets) of one block plus its ids and .h (the height it takes in a
    LayoutMode Top parent, its margins included - add it to sh.fit([...]))."""

    def __init__(self, items=(), **kw):
        Appends.__init__(self, items)
        self.__dict__.update(kw)


class Shell(object):
    """What page_shell / confirm_dialog return: ids (root, bar, title, body, close), sizes (w, h, pad, inner_w, body_h, inner_h;
    from the J() samples when the size is a runtime value), the appends that build the frame, and the b.set lines it needs."""

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.sets = []

    def sel(self, which="body"):
        return "#" + getattr(self, which)

    def fit(self, parts, what="page body"):
        return fit(parts, self.inner_h, what)

    def java(self, b="b", sets=None):
        lines = [self.appends.java(b)]
        for ident, prop, val in self.sets + list(sets or []):
            lines.append(java_set(ident, prop, val, b))
        return "\n".join(lines)

    def text(self, parent, ident=None, text="", kind="default", **kw):
        """Appends.text on this page's appends: a label with any text (punctuated / J() text -> an empty label + a b.set line)."""
        return self.appends.text(parent, ident, text, kind, **kw)

    def all_sets(self):
        """Every b.set line this shell emits, in order: the appends' (Appends.text, blocks) then the shell's own (the title)."""
        return list(self.appends.sets) + list(self.sets)


def page_shell(prefix, w, h, title="", kind="decorated", pad=CONTENT_PAD, root_id=None, bar_id=None, title_id=None, body_id=None,
               close=False, close_id=None, layout="Top"):
    """The vanilla window: kind decorated = @DecoratedContainer (ContainerHeader title bar with runes + the two gold ornaments;
    dialogs and forms), plain = @Container (ContainerHeaderNoRunes, no ornaments; the vanilla list pages ShopPage / WarpListPage).
    The page root (prefix, Anchor Width / Height only; w / h may be J(expr, "900") for a runtime size) holds the 38 px title bar with
    the @Title label, the ContainerPatch body (Top 38, LayoutMode Top, padding 17 = the container default), the bottom ornament and
    (close=True, optional - no vanilla server page shows it) the close X. Pass the OLD page root id as body_id and every old
    appendInline into it keeps working. title: static proven text goes inline, anything else (or J()) is b.set by shell.java()."""
    check_id(prefix)
    ws, hs = assert_page_size(w, h)
    if kind not in ("decorated", "plain"):
        raise ValueError("page kind decorated / plain")
    if not isinstance(pad, int) or isinstance(pad, bool) or pad < 0 or ws - 2 * pad < 60 or hs - TITLE_H - 2 * pad < 20:
        raise ValueError("page padding %r leaves no body (0 <= pad, inner width >= 60, inner height >= 20)" % (pad,))
    root = check_id(root_id or prefix)
    barid = check_id(bar_id or prefix + "Bar")
    tid = check_id(title_id or prefix + "Title")
    body = check_id(body_id or prefix + "Body")
    cid = check_id(close_id or prefix + "Close") if close else None
    ids = [root, barid, tid, body] + ([cid] if cid else [])
    if len(set(render(i) for i in ids)) != len(ids):
        raise ValueError("page shell ids must differ: %s" % ids)
    static = isinstance(title, str) and not has_j(title) and TEXT_OK.fullmatch(title) is not None
    head = patch("header", h_border=50, v_border=0) if kind == "decorated" else patch("headerPlain", h_border=35, v_border=0)
    deco_top = ' Group { Anchor: (Width: %d, Height: %d, Top: %d); Background: "%s"; }' % (DECO_W, DECO_H, DECO_TOP, TEX["decoTop"])
    ap = Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %s, Height: %s); }" % (root, _num(w, "page width"), _num(h, "page height"))))
    ap.append((root, "Group #%s { Anchor: (Height: %d, Top: 0); Padding: (Top: %d); Background: %s;%s %s }" % (
        barid, TITLE_H, TITLE_PAD_TOP, head, deco_top if kind == "decorated" else "", title_label(tid, title if static else ""))))
    ap.append((root, "Group #%s { Anchor: (Top: %d); %s%sBackground: %s; }" % (
        body, TITLE_H, _layout(layout), _padding(pad), patch("patch", 23))))
    if kind == "decorated":
        ap.append((root, 'Group { Anchor: (Width: %d, Height: %d, Bottom: %d); Background: "%s"; }' % (
            DECO_W, DECO_H, DECO_BOTTOM, TEX["decoBottom"])))
    if cid:
        ap.append((root, close_button(cid)))
    sh = Shell(prefix=prefix, w=ws, h=hs, pad=pad, kind=kind, root=root, bar=barid, title=tid, body=body, close=cid, appends=ap,
               inner_w=ws - 2 * pad, body_h=hs - TITLE_H, inner_h=hs - TITLE_H - 2 * pad)
    if title and not static:
        sh.sets.append((tid, "Text", title))
    return sh


_need("C", '  Group #Title {\n    Anchor: (Height: @TitleHeight, Top: 0);\n    Background: (TexturePath: "Common/ContainerHeader.png", '
      'HorizontalBorder: 50, VerticalBorder: 0);\n    Padding: (Top: 7);', "decorated title bar")
_need("C", '    Group #ContainerDecorationTop {\n      Anchor: (Width: 236, Height: 11, Top: -12);\n      Background: "Common/ContainerDecorationTop.png";',
      "top ornament")
_need("C", '  Group #ContainerDecorationBottom {\n    Anchor: (Width: 236, Height: 11, Bottom: -6);\n    Background: "Common/ContainerDecorationBottom.png";',
      "bottom ornament")
_need("C", '  Group #Content {\n    LayoutMode: Top;\n    Anchor: (Top: @TitleHeight);\n    Padding: @ContentPadding;\n'
      '    Background: (TexturePath: "Common/ContainerPatch.png", Border: 23);', "decorated body")
_need("C", 'Background: (TexturePath: "Common/ContainerHeaderNoRunes.png", HorizontalBorder: 35, VerticalBorder: 0);', "plain title bar")
_need("C", '@TitleStyle = LabelStyle(\n  FontSize: 15,\n  VerticalAlignment: Center,\n  RenderUppercase: true,\n  TextColor: #b4c8c9,\n'
      '  FontName: "Secondary",\n  RenderBold: true,\n  LetterSpacing: 0\n);', "title style")
_need("C", "  Style: (\n    ...@TitleStyle,\n    HorizontalAlignment: @Alignment\n  );\n  Padding: (Horizontal: 19);", "title label")
_need("C", "    Visible: @CloseButton;\n  }\n};\n\n@PageOverlay", "the container close X ships hidden")


def confirm_dialog(prefix, w=CONFIRM_W, msg_h=48, note=True, yes_text="Confirm", no_text="Cancel", yes_kind="primary",
                   yes_sound=None, yes_w=180, no_w=180, title="", ids=None):
    """The vanilla confirm window (Pages/PrefabEditorExitConfirm): 620 wide, padding 20, a title (REQUIRED, like vanilla: static
    proven text or J() / b.set), the #ffcc00 32 px question (bottom 12), the wrapped #96a9be message (bottom 16), an optional 12 px
    left-aligned note (bottom 8, horizontal 4), a centred button row (top 8): yes (Primary with the SaveSettings sound; destructive =
    Destructive + ButtonsCancel, WorldEventPanelPage ConfirmPage) right 6, no (Secondary + ButtonsCancel) left 6. Height computed.
    Texts: b.set the question / message / note ids. ids = {"question": .., "message": .., "note": .., "row": .., "yes": .., "no": ..}."""
    if not title:
        raise ValueError("confirm_dialog needs a title= (vanilla PrefabEditorExitConfirm has one; a blank title bar reads broken)")
    ids = dict(ids or {})
    q = check_id(ids.get("question", prefix + "Q"))
    m = check_id(ids.get("message", prefix + "Msg"))
    n = check_id(ids.get("note", prefix + "Note")) if note else None
    r = check_id(ids.get("row", prefix + "Btns"))
    y = check_id(ids.get("yes", prefix + "Yes"))
    no = check_id(ids.get("no", prefix + "No"))
    qh, nh = 46, fs(12) + 10
    parts = [qh + 12, msg_h + 16] + ([nh + 8] if note else []) + [BTN_H + 8]
    h = TITLE_H + 2 * DIALOG_PAD + sum(parts)
    sh = page_shell(prefix, w, h, title=title, pad=DIALOG_PAD, body_id=ids.get("body"), root_id=ids.get("root"))
    ap = sh.appends
    ap.append((sh.body, label(q, "", "warning", h=qh, anchor={"bottom": 12, "horizontal": 8})))
    ap.append((sh.body, label(m, "", "message", h=msg_h, anchor={"bottom": 16, "horizontal": 8})))
    if note:
        ap.append((sh.body, label(n, "", "note", h=nh, anchor={"bottom": 8, "horizontal": 4})))
    ap.append((sh.body, button_row(r, BTN_H, "center", 8)))
    ysnd = yes_sound or ("save" if yes_kind == "primary" else None)
    ap.append((r, button(y, yes_text, yes_kind, "normal", w=yes_w, sound=ysnd, anchor={"right": 6})))
    ap.append((r, button(no, no_text, "secondary", "normal", w=no_w, sound="cancel", anchor={"left": 6})))
    sh.question, sh.message, sh.note, sh.row, sh.yes, sh.no = q, m, n, r, y, no
    fit(parts, sh.inner_h, "confirm dialog")
    return sh


def _text_into(part, parent, ident, text, kind, **kw):
    """A label whose text is static-inline, b.set (punctuated / J()) or left empty (None / "": the builder b.sets it)."""
    if text is None or text == "":
        part.append((parent, label(ident, "", kind, **kw)))
    else:
        part.text(parent, ident, text, kind, **kw)


def _left_margin(avail, used, align, what):
    left = fit([used], avail, what)
    return {"center": left // 2, "left": 0, "right": left}[align]


def _state_button(ident, text, on, w, anchor, size="small", kind="secondary"):
    """A button that is live (True), shows the vanilla Disabled look (False) or picks one at runtime (J(cond): choose)."""
    live = button(ident, text, kind, size, w=w, anchor=anchor)
    if on is True:
        return live
    dead = button(ident, text, kind, size, w=w, anchor=anchor, disabled=True)
    if on is False:
        return dead
    if isinstance(on, str) and has_j(on):
        return choose(on, live, dead)
    raise ValueError("a pager button state is True, False or J(\"condition\"): %r" % (on,))


def pager(parent, prefix, w, text=None, prev_on=True, next_on=True, btn_w=150, caption_w=260, gap=12, prev_text="< Prev",
          next_text="Next >", align="center", top=8, kind="default", ids=None):
    """Prev / page / Next for the pages that keep a pager. Vanilla never paginates (every vanilla list is a TopScrolling
    scroll_list): use scroll_list when the page allows, this pager otherwise (fixed page sizes, money lists that must not
    scroll). Two small Secondary buttons #<prefix>Prev / #<prefix>Next (btn_w 150, 32 high, the light click) around the caption
    label #<prefix>Page (caption_w, a `kind` label, centred) in a LayoutMode Left row #<prefix> (32 high, top margin 8): the first
    button's left margin centres the group in w (the parent's inner width, e.g. sh.inner_w; align "left" / "right") - only
    properties the deployed pages already use (no LayoutMode Center, no FlexWeight).
    prev_on / next_on: True, False (the vanilla Disabled look: Disabled.png, grey label, silent - still clickable, so keep ignoring
    Prev on page 1 in handleDataEvent) or J("pageNo > 0") (both looks, picked in the Java: choose). text: the caption - static
    proven text ("Page 2 / 5") inline, punctuated / J() text as a b.set line in .sets, None = b.set #<prefix>Page yourself.
    ids = {"row": .., "prev": .., "page": .., "next": ..} keeps a restyled page's old ids. Returns a Part: .h (32 + top), .row,
    .prev, .page, .next."""
    ids = dict(ids or {})
    row = check_id(ids.get("row", prefix))
    pv, pg, nx = (check_id(ids.get(k, prefix + d)) for k, d in (("prev", "Prev"), ("page", "Page"), ("next", "Next")))
    if align not in ("center", "left", "right"):
        raise ValueError("pager align center / left / right")
    used = 2 * btn_w + 2 * gap + caption_w
    left = _left_margin(w, used, align, "pager")
    h = BTN_SMALL_H
    part = Part(h=h + (top or 0), row=row, prev=pv, page=pg, next=nx)
    part.append((parent, group(row, "Left", h=h, anchor={"top": top} if top else None)))
    part.append((row, _state_button(pv, prev_text, prev_on, btn_w, _merge({"left": left} if left else None, {"right": gap}))))
    _text_into(part, row, pg, text, kind, w=caption_w, h=h, align="Center")
    part.append((row, _state_button(nx, next_text, next_on, btn_w, {"left": gap})))
    return part


CONFIRM_PANELS = ("well", "row", None)


def _yes_button(ident, text, kind, w, sound, anchor, on):
    """confirm_view's yes button: live (True), the silent vanilla Disabled look (False) or both picked at runtime (J(cond))."""
    live = button(ident, text, kind, w=w, sound=sound, anchor=anchor)
    if on is True:
        return live
    dead = button(ident, text, kind, w=w, disabled=True, anchor=anchor)
    if on is False:
        return dead
    if isinstance(on, str) and has_j(on):
        return choose(on, live, dead)
    raise ValueError("confirm_view yes_on is True, False or J(\"condition\"): %r" % (on,))


def confirm_view(parent, prefix, w, question="", message="", note=None, msg_h=48, yes_text="Confirm", no_text="Cancel",
                 yes_kind="primary", yes_sound=None, yes_w=180, no_w=180, panel="well", pad=DIALOG_PAD, compact=False, top=8,
                 ids=None, wrap=False, yes_on=True, q_col="warning"):
    """The in-page confirm (SkyyRanks 0.1.1 buildConfirm: a question + Confirm / Cancel INSIDE the same page - nothing closes or
    opens, so the HANDOFF rule "never close a page right before opening another" holds) in the vanilla confirm look
    (Pages/PrefabEditorExitConfirm): a panel #<prefix> w wide (panel "well" = #000000(0.15), "row" = #101925(0.55) like SkyyRanks,
    None = no back; padding pad = 20) holding the #ffcc00 32 px question #<prefix>Q (bottom 12), the wrapped #96a9be message
    #<prefix>Msg (msg_h high, bottom 16), with note= a 12 px note #<prefix>Note (bottom 8), and the button row #<prefix>Btns (top 8):
    yes #<prefix>Yes (Primary + the SaveSettings sound; yes_kind="destructive" = Destructive + ButtonsCancel for a risky question:
    Delete / Disband / Kick / Reset) and no #<prefix>No (Secondary + ButtonsCancel), centred by a computed left margin (LayoutMode
    Left + Anchor margins only). compact=True = ONE row instead (Classes / Profiles inline confirm rows): the question in 16 px bold
    #ffcc00 filling what is left + yes + no. Texts: static proven text inline, anything else ("?", ",", J()) through b.set lines
    in .sets; "" / None = b.set it yourself. Returns a Part: .h (height incl. its top margin), .box, .question, .message, .note,
    .row, .yes, .no. Bind yes / no with Activating; the page's own state (pending action) decides what Confirm does.
    Kit 1.4 (the SkyyProfiles 0.1.3 pf_row options, now in the kit; the defaults keep the 1.3 output): wrap=True = the compact
    question wraps to two 16 px lines in its 44 px row (a long question); yes_on = True, False (yes in the vanilla Disabled look,
    silent - leave it unbound: nothing is picked yet) or J("cond") (both looks, picked in the Java: choose); q_col = the compact
    question colour (default "warning" = the vanilla confirm yellow; "text" = a plain hint line, not a question; a COLOR name or
    J()). Not compact: yes_on works the same, wrap / q_col are the compact row's options only."""
    ids = dict(ids or {})
    box = check_id(ids.get("box", prefix))
    q = check_id(ids.get("question", prefix + "Q"))
    yes = check_id(ids.get("yes", prefix + "Yes"))
    no = check_id(ids.get("no", prefix + "No"))
    if panel not in CONFIRM_PANELS:
        raise ValueError("confirm_view panel well / row / None")
    if yes_kind not in ("primary", "destructive"):
        raise ValueError("confirm_view yes_kind primary / destructive")
    if not isinstance(w, int) or isinstance(w, bool):
        raise ValueError("confirm_view needs the int width w (the parent's inner width, e.g. sh.inner_w)")
    bg = ("Background: %s; " % COLOR[panel]) if panel else ""
    ysnd = yes_sound or ("save" if yes_kind == "primary" else None)
    tm = {"top": top} if top else None
    if compact:
        cpad = 8
        inner = w - 2 * 12
        qw = inner - yes_w - no_w - 2 * 6
        if qw < 160:
            raise ValueError("confirm_view compact: %d px left for the question (w too small / buttons too wide)" % qw)
        h = BTN_H + 2 * cpad
        part = Part(h=h + (top or 0), box=box, question=q, message=None, note=None, row=box, yes=yes, no=no)
        part.append((parent, "Group #%s { %sLayoutMode: Left; %sPadding: (Horizontal: 12, Vertical: %d); }"
                     % (box, _anchor(w, h, tm), bg, cpad)))
        qkw = {"w": qw, "h": BTN_H, "col": q_col}
        if wrap:
            qkw["wrap"] = True
        _text_into(part, box, q, question, "bold", **qkw)
        part.append((box, _yes_button(yes, yes_text, yes_kind, yes_w, ysnd, {"left": 6}, yes_on)))
        part.append((box, button(no, no_text, "secondary", w=no_w, sound="cancel", anchor={"left": 6})))
        return part
    m = check_id(ids.get("message", prefix + "Msg"))
    n = check_id(ids.get("note", prefix + "Note")) if note is not None else None
    r = check_id(ids.get("row", prefix + "Btns"))
    if not isinstance(pad, int) or isinstance(pad, bool) or pad < 0:
        raise ValueError("confirm_view pad must be an int >= 0")
    qh, nh = 46, fs(12) + 10
    parts = [qh + 12, msg_h + 16] + ([nh + 8] if n else []) + [BTN_H + 8]
    h = 2 * pad + sum(parts)
    inner = w - 2 * pad
    left = _left_margin(inner, yes_w + no_w + 2 * 6, "center", "confirm_view buttons")
    part = Part(h=h + (top or 0), box=box, question=q, message=m, note=n, row=r, yes=yes, no=no)
    part.append((parent, "Group #%s { %sLayoutMode: Top; %s%s}" % (box, _anchor(w, h, tm), bg, _padding(pad) if pad else "")))
    _text_into(part, box, q, question, "warning", h=qh, anchor={"bottom": 12, "horizontal": 8})
    _text_into(part, box, m, message, "message", h=msg_h, anchor={"bottom": 16, "horizontal": 8})
    if n:
        _text_into(part, box, n, note, "note", h=nh, anchor={"bottom": 8, "horizontal": 4})
    part.append((box, group(r, "Left", h=BTN_H, anchor={"top": 8})))
    part.append((r, _yes_button(yes, yes_text, yes_kind, yes_w, ysnd, _merge({"left": left} if left else None, {"right": 6}), yes_on)))
    part.append((r, button(no, no_text, "secondary", w=no_w, sound="cancel", anchor={"left": 6})))
    return part


# ================================================================= kit 1.4 blocks (the stage-1b restyle reviews; ADDITIVE ONLY)
# Everything below is new in kit 1.4 and made from the kit 1.3 builders + proven properties only (LayoutMode Left / Top, fixed
# widths / heights, Anchor margins, Padding, colour backgrounds, ItemIcon with an inline ItemId, Wrap): no FlexWeight, no LayoutMode
# Center / Right / Full, no WrapMaxLines, no LetterSpacing, nothing UNVERIFIED (assert_proven checks it; probe page 19 "base4"
# shows every block in game). The compositions are the ones the five held restyles made by hand (SkyyBank 0.1.4 wells, SkyyParty
# 0.1.6 heads / bars / footer, SkyyAccessories 0.4.5 fixed rows / result line, SkyyClasses 0.1.8 + SkyyProfiles 0.1.3 cards).
class Markup(str):
    """A markup str that also carries what its builder knows (kit 1.4): .h / .w = its OUTER height / width (Anchor Height + Top +
    Bottom (+ 2 x Vertical / Full), Width + Left + Right (+ 2 x Horizontal / Full); None when the markup sets none), .sets = the
    b.set lines its texts need [(id, "Text", value)], .ids = {role: element id}, plus builder-specific attributes. It IS the markup:
    every kit function, java_append, choose and check_markup take it as a str. Add it with ap.add(parent, markup) (carries .sets)
    or java_add(parent, markup) (the append + its b.set lines) - a plain ap.append((parent, markup)) drops the .sets."""

    def __new__(cls, text, **attrs):
        o = str.__new__(cls, text)
        o.sets = list(attrs.pop("sets", ()))
        o.ids = dict(attrs.pop("ids", None) or {})
        if "h" not in attrs or "w" not in attrs:
            ow, oh = outer_size(str(text))
            attrs.setdefault("w", ow)
            attrs.setdefault("h", oh)
        o.__dict__.update(attrs)
        return o


def _markup_sets(mk):
    """The b.set lines a Markup (or a Choice of two Markups: both must carry the same) brings along."""
    if isinstance(mk, Choice):
        a, b = list(getattr(mk.a, "sets", ())), list(getattr(mk.b, "sets", ()))
        if a != b:
            raise ValueError("choose(): the two looks carry different b.set lines (%s / %s) - set the texts once, after the append"
                             % (a, b))
        return a
    return list(getattr(mk, "sets", ()))


def java_add(parent, markup, b="b", page_root=True):
    """Kit 1.4: java_append(parent, markup) followed by the java_set lines of a Markup's .sets (its texts), as one text."""
    return "\n".join([java_append(parent, markup, b, page_root)] + [java_set(i, pr, v, b) for i, pr, v in _markup_sets(markup)])


_OUTER_KEYS = ("Width", "Height", "Left", "Right", "Top", "Bottom", "Horizontal", "Vertical", "Full")


def _own_props(mk):
    """The OUTER element's own property text of one markup (brace depth 1, quoted text blanked, J() values as their samples)."""
    s = _strip_quoted(render(mk))
    out, depth = [], 0
    for ch in s:
        if ch == "{":
            depth += 1
            if depth == 1:
                continue
        elif ch == "}":
            depth -= 1
        if depth == 1:
            out.append(ch)
    return "".join(out)


def _top_prop(own, key):
    """The value text of property `key` written at paren depth 0 of an element's own properties (None when absent)."""
    depth, i, n = 0, 0, len(own)
    pat = re.compile(r"(?<![A-Za-z0-9])%s\s*:\s*" % key)
    while i < n:
        ch = own[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            m = pat.match(own, i)
            if m:
                j, d = m.end(), 0
                k = j
                while k < n and not (d == 0 and own[k] == ";"):
                    d += 1 if own[k] == "(" else (-1 if own[k] == ")" else 0)
                    k += 1
                return own[j:k].strip()
        i += 1
    return None


def _number(v, what):
    try:
        f = float(v)
    except ValueError:
        raise ValueError("%s: %r is not a number (a J() size needs a number sample)" % (what, v))
    return int(f) if f == int(f) else f


def _anchor_vals(mk):
    """{Width / Height / Left / ...: number} of a markup's OUTER element's own Anchor (J() values as their samples)."""
    anc = _top_prop(_own_props(_variants(mk)[0]), "Anchor")
    vals = {}
    if anc is not None:
        body = anc.strip()
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1]
        for part in body.split(","):
            k, _s, v = part.partition(":")
            k = k.strip()
            if k in _OUTER_KEYS and v.strip():
                vals[k] = _number(v.strip(), "Anchor " + k)
    return vals


def outer_size(mk):
    """(outer width, outer height) of a markup's OUTER element (kit 1.4), read from its own Anchor: Width + Left + Right
    (+ 2 x Horizontal / Full) and Height + Top + Bottom (+ 2 x Vertical / Full); None where it sets no Width / Height. J() values
    count as their samples. A Choice: both looks must have the same outer size."""
    if isinstance(mk, Choice):
        a, b = outer_size(mk.a), outer_size(mk.b)
        if a != b:
            raise ValueError("choose(): the two looks have different outer sizes %s / %s" % (a, b))
        return a
    vals = _anchor_vals(mk)
    g = vals.get
    hm = g("Left", 0) + g("Right", 0) + 2 * (g("Horizontal", 0) + g("Full", 0))
    vm = g("Top", 0) + g("Bottom", 0) + 2 * (g("Vertical", 0) + g("Full", 0))
    return (g("Width") + hm if "Width" in vals else None), (g("Height") + vm if "Height" in vals else None)


def is_flex(mk):
    """True when a markup's outer element has a FlexWeight (it takes the free space of its row / column)."""
    mk = _variants(mk)[0]
    return _top_prop(_own_props(mk), "FlexWeight") is not None


def _used(appends, container, axis, what):
    cid = render(container).lstrip("#")
    total = 0
    kids = [mk for p, mk in appends if p is not None and render(p).lstrip("#") == cid]
    for mk in kids:
        size = outer_size(mk)[axis]
        if size is None:
            if is_flex(mk):
                continue
            raise ValueError("%s of #%s: a child without a fixed %s or a FlexWeight - its size cannot be proven: %s"
                             % (what, cid, "Height" if axis else "Width", render(_variants(mk)[0])[:120]))
        total += size
    return total


def used_height(appends, container):
    """Kit 1.4: the height the DIRECT children of `container` take in a LayoutMode Top column - the sum of their outer heights
    (Anchor Height + Top + Bottom ...; a FlexWeight child counts 0: it takes what is left). Raises when a child has neither a
    Height nor a FlexWeight. Budget: fit([used_height(ap, "SkyyXBody")], sh.inner_h) (or == 0 for a body filled exactly)."""
    return _used(appends, container, 1, "used_height")


def used_width(appends, row):
    """Kit 1.4: the width the DIRECT children of `row` take in a LayoutMode Left row (outer widths; FlexWeight children count 0)."""
    return _used(appends, row, 0, "used_width")


def right_margin(avail, used):
    """Kit 1.4: the left margin (Padding Left / Anchor Left) that right-aligns content `used` px wide in `avail` px, without
    LayoutMode Right (a base probe property): avail - used (raises when it does not fit)."""
    return fit([used], avail, "right-aligned content")


def centre_margin(avail, used):
    """Kit 1.4: the left margin that centres content `used` px wide in `avail` px, without LayoutMode Center: (avail - used) // 2."""
    return fit([used], avail, "centred content") // 2


def _inside(outer, kids):
    """Kit markup `outer` (ending with its closing brace) with the markups `kids` placed inside it."""
    kids = [k for k in kids if k]
    if not outer.endswith("}"):
        raise ValueError("not a kit element markup: %r" % outer[:60])
    return (outer[:-1] + " ".join(kids) + " }") if kids else outer


def _text_bits(ident, text, what):
    """(inline text, [b.set line]) of a builder's text: proven static text inline; punctuated static text or J() = empty + a b.set
    line (then the element needs an id); None / "" = empty, no line (the caller b.sets it)."""
    if text is None or text == "":
        return "", []
    if not isinstance(text, str):
        raise ValueError("%s text must be a str or J(): %r" % (what, text))
    if not has_j(text) and TEXT_OK.fullmatch(text):
        return text, []
    if not ident:
        raise ValueError("%s: text %r goes in with b.set, so the label needs an id" % (what, render(text)))
    return "", [(ident, "Text", text)]


def color_by(pairs, default):
    """Kit 1.4: a runtime colour from colour NAMES (each one validated): [(java condition, colour), ...] + the default colour ->
    J('(c1) ? "#..." : ((c2) ? "#..." : ("#..."))', sample = the first colour) - the first true condition wins (the SKYY CARD
    look chain). A condition is a Java boolean expression str or one J(expr). Use it as group(bg=) / panel(bg=) / label(col=)."""
    d = color(default)
    if has_j(d):
        raise ValueError("color_by: the default is a colour name or literal, not a J() value")
    e = java_lit(d)
    first = d
    for cond, col in reversed(list(pairs)):
        c = color(col)
        if has_j(c):
            raise ValueError("color_by: colours are names or literals (validated), not J() values: %r" % (col,))
        e = "(%s) ? %s : (%s)" % (choose(cond, "x", "x").cond, java_lit(c), e)
        first = c
    return J(e, first)


STATE_WORD_KINDS = ("success", "disabled", "error", "info", "gold", "muted", "strong", "default")


def state_word(ident=None, text="", kind="success", w=BTN_MIN_W, h=BTN_H, anchor=None):
    """Kit 1.4: the bold centred word that stands where a button would (w x h = a normal button, 172 x 44): Selected / Active
    (success green), Locked / Coming soon / Coming later (disabled grey), ... (the SKYY CARD card_state: label(None, text, kind,
    w=172, h=44, align="Center", bold=True) - the same markup). Punctuated / J() text needs an ident (b.set, in .sets)."""
    if kind not in STATE_WORD_KINDS:
        raise ValueError("state_word kind %r (one of %s)" % (kind, ", ".join(STATE_WORD_KINDS)))
    inline, sets = _text_bits(ident, text, "state_word")
    return Markup(label(ident, inline, kind, w=w, h=h, align="Center", bold=True, anchor=anchor), sets=sets,
                  ids={"word": ident} if ident else {})


def status_bar(ident=None, on=True, col="selected", w=4, gap=8):
    """Kit 1.4: the 4 px status bar at a list row's left edge (WorldEventListRow #StatusBar: Width 4, Right 8, #4274a5): on=True =
    the bar (col = any kit colour), False = no colour but its 4 + 8 px kept (rows with and without a bar line up), J("cond") = the
    bar only when cond is true at runtime (its Background is a runtime property: `(cond) ? "Background: ...; " : ""`)."""
    head = ("Group #%s { " % check_id(ident)) if ident else "Group { "
    anc = _anchor(w, None, {"right": gap} if gap else None)
    c = color(col)
    if on is True:
        return head + anc + "Background: %s; }" % c
    if on is False:
        return head + anc + "}"
    if isinstance(on, str) and has_j(on):
        if has_j(c):
            raise ValueError("status_bar(on=J(...)) takes a colour name or literal, not a J() colour")
        prop = "Background: %s; " % c
        return head + anc + J('(%s) ? %s : ""' % (choose(on, "x", "x").cond, java_lit(prop)), prop) + "}"
    raise ValueError("status_bar on is True, False or J(\"condition\"): %r" % (on,))


row_bar = status_bar


def static_row(ident, w, h=None, icon=None, name="", sub=None, tag=None, action=None, bar=True, state="static", gap=ROW_GAP,
               icon_size=40, tag_w=150, tag_kind="rowBadge", action_kind="secondary", action_w=None, action_on=True,
               action_sound=None, name_kind="rowName", sub_kind="rowSub", name_col=None, sub_col=None, tag_col=None, pad=8,
               anchor=None, ids=None):
    """Kit 1.4: a FIXED-WIDTH list row (the WorldEventListRow look without FlexWeight - SkyyAccessories 0.4.5's rows) as ONE markup:
    Group #ident (LayoutMode Left, h + gap bottom) holding the row panel #<ident>P (w minus the action, padding left / right 8;
    state "static" = the #101925(0.55) panel Group, "normal" / "selected" = a clickable Button with row_style: bind #<ident>P)
    with the status bar #<ident>Bar (bar: True = blue, None = no colour but its 12 px kept, False = none, J("cond") = runtime,
    or a colour name), the icon box #<ident>Ib + ItemIcon #<ident>Ic (icon = an item id or J(); None = no icon), the text column
    #<ident>T (name #<ident>Nm 18 px bold + sub #<ident>Sb 15 px, vertically centred) and the right tag #<ident>Tg (tag_w wide,
    right-aligned, tag=None = none), then the small action button #<ident>Act (action = its proven label; None = none;
    action_on=False = the vanilla Disabled look - a runtime state: choose(J("c"), static_row(...), static_row(..., action_on=False))).
    Texts (name / sub / tag): proven text inline, punctuated / J() text as b.set lines in .sets, "" = empty (b.set it yourself).
    ids = {"panel", "bar", "icon_box", "icon", "text", "name", "sub", "tag", "action"} keeps a restyled page's old ids.
    Returns a Markup: .h = its outer height (h + gap), .w, .sets, .ids, .text_w (the text column width)."""
    check_id(ident)
    ids = dict(ids or {})
    idd = lambda k, d: check_id(ids.get(k, ident + d))
    h = h if h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H)
    for v, what in ((w, "width"), (h, "height"), (icon_size, "icon size"), (tag_w, "tag width"), (pad, "padding")):
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise ValueError("static_row %s must be an int: %r" % (what, v))
    if state not in ("static", "normal", "selected"):
        raise ValueError("static_row state static / normal / selected")
    aw = action_w if action_w is not None else (PRIMARY_SMALL_W if action_kind == "primary" else ROW_ACTION_W)
    panel_w = w - ((4 + aw) if action is not None else 0)
    bar_w = 0 if bar is False else 4 + 8
    box_w = (icon_size + 12) if icon is not None else 0
    tag_room = (tag_w + 8) if tag is not None else 0
    text_w = panel_w - 2 * pad - bar_w - box_w - tag_room
    if text_w < 40:
        raise ValueError("static_row %s: %d px left for the text column (w %d is too small for its parts)" % (ident, text_w, w))
    sets, kids = [], []
    pid = idd("panel", "P")
    got = {"row": ident, "panel": pid}
    if bar is not False:
        got["bar"] = idd("bar", "Bar")
        if bar is True or bar is None:
            kids.append(status_bar(got["bar"], bar is True))
        elif isinstance(bar, str) and has_j(bar):
            kids.append(status_bar(got["bar"], bar))
        else:
            kids.append(status_bar(got["bar"], True, col=bar))
    if icon is not None:
        got["icon_box"], got["icon"] = idd("icon_box", "Ib"), idd("icon", "Ic")
        kids.append(_inside(group(got["icon_box"], None, w=box_w, h=h),
                            [item_icon(got["icon"], icon, icon_size, anchor={"left": 0, "top": (h - icon_size) // 2})]))
    nh, shh = fs(LABELS[name_kind][0]) + 6, fs(LABELS[sub_kind][0]) + 5
    tot = nh + (shh if sub is not None else 0)
    fit([tot], h, "static_row text")
    top = (h - tot) // 2
    nid = got["name"] = idd("name", "Nm")
    got["text"] = idd("text", "T")
    t_in, t_sets = _text_bits(nid, name, "static_row name")
    sets += t_sets
    tkids = [label(nid, t_in, name_kind, h=nh, col=name_col, fit=False)]
    if sub is not None:
        sid = got["sub"] = idd("sub", "Sb")
        s_in, s_sets = _text_bits(sid, sub, "static_row sub")
        sets += s_sets
        tkids.append(label(sid, s_in, sub_kind, h=shh, col=sub_col, fit=False))
    kids.append(_inside(group(got["text"], "Top", w=text_w, h=h, pad={"top": top} if top else None), tkids))
    if tag is not None:
        gid = got["tag"] = idd("tag", "Tg")
        g_in, g_sets = _text_bits(gid, tag, "static_row tag")
        sets += g_sets
        kids.append(label(gid, g_in, tag_kind, w=tag_w, h=h, col=tag_col, anchor={"left": 8}, fit=False))
    pad_d = {"left": pad, "right": pad} if pad else None
    if state == "static":
        pnl = panel(pid, "row", w=panel_w, h=h, layout="Left", pad=pad_d)
    else:
        pnl = "Button #%s { %sLayoutMode: Left; %s%s }" % (pid, _anchor(panel_w, h), _padding(pad_d), row_style(state))
    row_kids = [_inside(pnl, kids)]
    if action is not None:
        got["action"] = idd("action", "Act")
        if action_on not in (True, False):
            raise ValueError("static_row action_on is True or False (a runtime state: choose() two rows)")
        row_kids.append(button(got["action"], action, action_kind, "small", w=aw, h=h, disabled=not action_on, sound=action_sound,
                               anchor={"left": 4}))
    mk = _inside(group(ident, "Left", h=h, anchor=_merge({"bottom": gap} if gap else None, anchor)), row_kids)
    return Markup(mk, sets=sets, ids=got, w=w, text_w=text_w)


def list_well(ident, w=None, h=None, rows=None, row_h=None, gap=ROW_GAP, anchor=None):
    """Kit 1.4: a FIXED (non-scrolling) list on the vanilla list well (WorldEventPanelPage #ListContainer: #000000(0.15),
    padding 4; LayoutMode Top) - = panel(ident, "well", w, h, pad=4). rows + row_h (default the readable 56) + gap (3) give the
    height: list_well_h(rows, row_h, gap). Returns a Markup (.h, .inner_w, .inner_h: the room for the rows)."""
    if h is None:
        if rows is None:
            raise ValueError("list_well needs h= or rows=")
        h = list_well_h(rows, row_h, gap)
    mk = panel(ident, "well", w=w, h=h, pad=WELL_LIST_PAD, anchor=anchor)
    iw = (w - 2 * WELL_LIST_PAD) if isinstance(w, int) and not isinstance(w, bool) else None
    ih = (h - 2 * WELL_LIST_PAD) if isinstance(h, int) and not isinstance(h, bool) else None
    return Markup(mk, inner_w=iw, inner_h=ih)


def list_well_h(rows, row_h=None, gap=ROW_GAP):
    """The height of a list_well holding `rows` rows of row_h (+ gap under each) - its padding 4 included."""
    rh = row_h if row_h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H)
    return 2 * WELL_LIST_PAD + rows * (rh + gap)


def result_line(ident, colour=None, h=44, wrap=True, size=16, anchor=None):
    """Kit 1.4: the result line for pages whose result texts carry NO +/-/= marks (SkyyAccessories 0.4.5, SkyyParty 0.1.6):
    status_line's look (16 px bold, centred, two lines in 44 px) with the colour given as a COLOR name or a J() runtime colour -
    J("infoColor(this.info)", "#39f493") with a Java helper from java_color_by_text(), or color_by([...]). b.set its Text."""
    if colour is None:
        raise ValueError("result_line needs colour= (a COLOR name or J(\"javaColourExpr(...)\", \"#39f493\"))")
    return label(ident, "", "default", h=h, size=size, bold=True, align="Center", col=colour, wrap=True if wrap else None, anchor=anchor)


_JAVA_NAME_OK = re.compile(r"\A[a-z][A-Za-z0-9]*\Z")


def java_color_by_text(name, rules, empty="=", default="-"):
    """Kit 1.4: Java source of `public static String <name>(String t)` (CtNewMethod.make) - the colour of a result text WITHOUT a
    mark, by its words: rules = [(test, text, colour), ...] in order, the first match wins; test = "startsWith" / "endsWith" /
    "contains" / "equals"; colour = "+" / "-" / "=" (SUI.STATUS: success / error / info) or a COLOR name. empty = the colour of
    a null / empty text, default = when no rule matches. javassist-safe (if chains; no String switch)."""
    if not isinstance(name, str) or not _JAVA_NAME_OK.fullmatch(name):
        raise ValueError("java_color_by_text name: a lower-case Java method name like infoColor")

    def col(c):
        v = STATUS[c] if c in STATUS else color(c)
        if has_j(v):
            raise ValueError("java_color_by_text colours are marks or colour names, not J() values")
        return v
    lines = ["public static String %s(String t) {" % name, '  if (t == null || t.length() == 0) return "%s";' % col(empty)]
    for test, text, c in rules:
        if not isinstance(text, str) or not text:
            raise ValueError("java_color_by_text: rule text must be a non-empty str")
        cond = {"startsWith": "t.startsWith(%s)", "endsWith": "t.endsWith(%s)", "contains": "t.indexOf(%s) >= 0",
                "equals": "t.equals(%s)"}.get(test)
        if cond is None:
            raise ValueError("java_color_by_text test %r (startsWith / endsWith / contains / equals)" % (test,))
        lines.append('  if (%s) return "%s";' % (cond % java_lit(text), col(c)))
    lines += ['  return "%s";' % col(default), "}"]
    return "\n".join(lines)


class BarPair(tuple):
    """stat_bar's result: (full, empty) - choose()-ready (both create the same id; the empty one has no fill child). .full /
    .empty, .h (outer height), .fill (the fill width), .choose(cond=None) = choose(J(cond or "fill > 0"), full, empty), .pick() =
    the right one for a static fill."""

    def __new__(cls, full, empty, **attrs):
        o = tuple.__new__(cls, (full, empty))
        o.__dict__.update(attrs)
        return o

    @property
    def full(self):
        return self[0]

    @property
    def empty(self):
        return self[1]

    def choose(self, cond=None):
        if cond is None:
            m = _J_RE.fullmatch(self.fill) if isinstance(self.fill, str) else None
            if m is None:
                raise ValueError("stat_bar.choose(): a static fill needs no choice - use .pick()")
            cond = "(%s) > 0" % m.group(1)
        return choose(cond, self[0], self[1])

    def pick(self):
        if not isinstance(self.fill, int) or isinstance(self.fill, bool):
            raise ValueError("stat_bar.pick() is for a static int fill; a J() fill: .choose()")
        return self[0] if self.fill > 0 else self[1]


def stat_bar(ident, w, h, fill, col="progressFill", track="progressTrack", anchor=None):
    """Kit 1.4: a flat stat / progress bar that can drop its fill (SkyyParty 0.1.6's health / stamina / mana bars; the kit 1.3
    bar() always writes the fill child): the track Group #ident (w x h, LayoutMode Left, the vanilla progress track #1a2030) and
    - in the FULL variant only - an anonymous fill Group (fill px wide: an int or J("fillPx(cur, max)", "80"); col = a kit /
    data colour or J()). Returns a BarPair (full, empty): SUI.java_append(p, bar.choose()) appends the fill only when fill > 0
    (never a 0 px Group); .pick() for a static fill."""
    check_id(ident)
    n = _sample_num(fill)
    if n is None or n < 0:
        raise ValueError("stat_bar fill: an int >= 0 or J(expr, sample) with a number sample: %r" % (fill,))
    empty = group(ident, "Left", w=w, h=h, anchor=anchor, bg=track)
    full = _inside(empty, [group(None, None, w=fill if has_j(fill) else max(int(fill), 1), h=h, bg=col)])
    return BarPair(full, empty, h=outer_size(empty)[1], fill=fill)


class Columns(object):
    """Kit 1.4 column spec (column_spec): ONE list [(head text, width), ...] gives the heads, the rows and the inner widths.
    .names, .widths, .gap, .pad_left (the first column's offset inside a ROW: row padding + status bar ...), .total (widths + gaps),
    .avail and .slack (avail - pad_left - total; raises when it does not fit), .width(i or name), .x(i or name) (offset from the
    row's left edge), .heads(ident, outside=4) (column_heads over a list well: outside = the well's padding) and .row(ident, ...)."""

    def __init__(self, cols, avail=None, pad_left=0, gap=0):
        cols = list(cols)
        if not cols:
            raise ValueError("column_spec needs at least one (text, width) column")
        self.names, self.widths = [], []
        for c in cols:
            if not (isinstance(c, (tuple, list)) and len(c) == 2 and isinstance(c[0], str) and isinstance(c[1], int)
                    and not isinstance(c[1], bool) and c[1] > 0):
                raise ValueError("a column is (head text, int width > 0): %r" % (c,))
            self.names.append(c[0])
            self.widths.append(c[1])
        for v, what in ((pad_left, "pad_left"), (gap, "gap")):
            if not isinstance(v, int) or isinstance(v, bool) or v < 0:
                raise ValueError("column_spec %s must be an int >= 0" % what)
        self.gap, self.pad_left, self.avail = gap, pad_left, avail
        self.total = sum(self.widths) + gap * (len(self.widths) - 1)
        self.slack = fit([pad_left, self.total], avail, "columns") if avail is not None else None

    def _i(self, key):
        return key if isinstance(key, int) else self.names.index(key)

    def width(self, key):
        return self.widths[self._i(key)]

    def x(self, key):
        i = self._i(key)
        return self.pad_left + sum(self.widths[:i]) + self.gap * i

    def heads(self, ident, h=30, kind="section", outside=0, anchor=None):
        return column_heads(ident, self, pad_left=self.pad_left + outside, h=h, kind=kind, anchor=anchor)

    def row(self, ident, texts=None, h=None, kinds="default", **kw):
        return column_row(ident, self, texts, h=h, kinds=kinds, **kw)


def column_spec(cols, avail=None, pad_left=0, gap=0):
    """Kit 1.4: a Columns spec from [(head text, width), ...] (see Columns)."""
    return Columns(cols, avail, pad_left, gap)


def column_heads(ident, cols, pad_left=0, h=30, kind="section", gap=None, anchor=None):
    """Kit 1.4: the column heads over a list (SkyyParty 0.1.6 #SkyyPHead): ONE markup, a LayoutMode Left Group #ident (h high,
    Padding Left = pad_left - the offset of the first column: list well padding + row padding + status bar) holding one label per
    column in the vanilla section head style (13 -> 16 px bold uppercase #9aacbc), each as wide as its column (gap between).
    cols = [(text, width), ...] or a Columns. A punctuated head is b.set (#<ident>H<i>, in .sets). Returns a Markup."""
    spec = cols if isinstance(cols, Columns) else Columns(cols, pad_left=pad_left, gap=gap or 0)
    g = spec.gap if gap is None else gap
    kids, sets = [], []
    for i, (text, w) in enumerate(zip(spec.names, spec.widths)):
        hid = ident + "H" + str(i)
        inline, s = _text_bits(hid, text, "column head")
        sets += s
        kids.append(label(hid if s else None, inline, kind, w=w, h=h, anchor={"right": g} if g and i < len(spec.widths) - 1 else None))
    mk = _inside(group(check_id(ident), "Left", h=h, anchor=anchor, pad={"left": pad_left} if pad_left else None), kids)
    return Markup(mk, sets=sets, ids={"heads": ident})


def column_row(ident, cols, texts=None, h=None, kinds="default", panel_kind="row", gap=ROW_GAP, pad_left=None, cols_col=None,
               anchor=None):
    """Kit 1.4: one fixed-width table row whose cells line up under column_heads: a LayoutMode Left row #ident (panel_kind "row"
    = the #101925(0.55) row panel, None = no back; h high + gap under it; Padding Left = the spec's pad_left) with one label per
    column #<ident>C<i> as wide as its column. texts[i]: proven text inline, punctuated / J() text as b.set lines (.sets), "" /
    None = empty (b.set it). kinds = one label kind or a list; cols_col = a list of colours (or None each). Returns a Markup."""
    spec = cols if isinstance(cols, Columns) else Columns(cols)
    n = len(spec.widths)
    h = h if h is not None else (ROW_H_READABLE if _SCALE[0] == "readable" else ROW_H)
    texts = list(texts) if texts is not None else [""] * n
    kinds = [kinds] * n if isinstance(kinds, str) else list(kinds)
    colours = list(cols_col) if cols_col is not None else [None] * n
    if not (len(texts) == len(kinds) == len(colours) == n):
        raise ValueError("column_row: texts / kinds / colours must have one entry per column (%d)" % n)
    pl = spec.pad_left if pad_left is None else pad_left
    kids, sets = [], []
    for i in range(n):
        cid = check_id(ident + "C" + str(i))
        inline, s = _text_bits(cid, texts[i], "column_row cell")
        sets += s
        kids.append(label(cid, inline, kinds[i], w=spec.widths[i], h=h, col=colours[i],
                          anchor={"right": spec.gap} if spec.gap and i < n - 1 else None, fit=False))
    anc = _merge({"bottom": gap} if gap else None, anchor)
    padd = {"left": pl} if pl else None
    if panel_kind == "row":
        outer = panel(ident, "row", h=h, pad=padd, layout="Left", anchor=anc)
    elif panel_kind is None:
        outer = group(ident, "Left", h=h, pad=padd, anchor=anc)
    else:
        raise ValueError("column_row panel_kind row / None")
    return Markup(_inside(outer, kids), sets=sets, ids=dict([("row", ident)] + [("c%d" % i, ident + "C" + str(i)) for i in range(n)]))


def stat_well(ident, heading="", number=None, caption="", w=None, anchor=None, ids=None, head_h=25, num_h=42, cap_h=25):
    """Kit 1.4: SkyyBank 0.1.4's PURSE / BANK box as ONE markup - a vanilla well (#000000(0.15), padding 8, LayoutMode Top)
    holding the centred subtitle `heading` (the vanilla @Subtitle 15 px bold uppercase, bottom 10), the big number #<ident>N (the
    display style: 32 px, Default font, the Hud/TimeLeft timer; number = J("fmt(purse)", "12,345") -> a b.set line, None = b.set it
    yourself, a proven static text = inline) and a centred grey caption. Punctuated heading / caption texts are b.set too
    (#<ident>H / #<ident>C). ids = {"number", "heading", "caption"}. Returns a Markup (.h = the outer height: 118 + margins)."""
    check_id(ident)
    ids = dict(ids or {})
    nid = check_id(ids.get("number", ident + "N"))
    if number is not None and not (isinstance(number, str) and (has_j(number) or TEXT_OK.fullmatch(number))):
        raise ValueError("stat_well number: J(\"javaExpr\", \"12345\"), a proven static text or None: %r" % (number,))
    sets = []
    h_in, hs = _text_bits(ids.get("heading", ident + "H"), heading, "stat_well heading")
    n_in, ns = _text_bits(nid, number, "stat_well number")
    c_in, cs = _text_bits(ids.get("caption", ident + "C"), caption, "stat_well caption")
    sets = hs + ns + cs
    hid = ids.get("heading") or (ident + "H" if hs else None)
    cid = ids.get("caption") or (ident + "C" if cs else None)
    h = head_h + 10 + num_h + cap_h + 2 * WELL_PAD
    kids = [label(hid, h_in, "subtitle", h=head_h, align="Center", anchor={"bottom": 10}),
            label(nid, n_in, "display", h=num_h, align="Center"),
            label(cid, c_in, "caption", h=cap_h, align="Center")]
    got = {"well": ident, "number": nid}
    if hid:
        got["heading"] = hid
    if cid:
        got["caption"] = cid
    return Markup(_inside(panel(ident, "well", w=w, h=h, anchor=anchor), kids), sets=sets, ids=got)


# ---- list_card: the SKYY CARD of SkyyClasses 0.1.8 / SkyyProfiles 0.1.3 (their shared block, CARD_SHA 85a04785...), in the kit.
# list_card(...).java(b) is byte-identical to that block's card_java(...) for the same inputs (the kit test runs both), so the next
# Classes / Profiles version can switch to the kit without a visual change.
LIST_CARD_H = 84                 # name 24 + line two 20 + line three 40 (two wrapped 15 px lines)
LIST_CARD_GAP = 4                # under each card (the OverrideRespawnPointButton option rows: 50 + 4)
LIST_CARD_BAR = 4                # the status bar (WorldEventListRow #StatusBar)
LIST_CARD_FRAME = 64             # the item cell border (BarterTradeRow slot border #1a2530, padding 2) around a 60 px ItemIcon
LIST_CARD_CELL = LIST_CARD_FRAME + 8
LIST_CARD_ACT_W = 200            # the action column: a normal button (172) centred in it
LIST_CARD_BTN_W = BTN_MIN_W
LIST_CARD_PAD_R = 12
LIST_CARD_LOOKS = {"selected": ("rowPressed", "selected"),     # yours / picked: the WorldEventListRow pressed step + the blue bar
                   "pending": ("rowHover", "warning"),         # waiting for Confirm: the hovered row + the confirm-yellow bar
                   "normal": ("row", "row"),                   # the list row panel (bar in the card colour = no bar)
                   "off": ("cardDisabled", "cardDisabled"),    # coming later: BarterTradeRow's disabled card (+ grey text, covers)
                   "empty": ("well", "well")}                  # an empty slot: one more step of the well tone


def list_card_h(rows):
    """The height of a list_well holding `rows` list cards (padding 4 + rows x (84 + 4))."""
    return 2 * WELL_LIST_PAD + rows * (LIST_CARD_H + LIST_CARD_GAP)


def list_card_text_w(w, icon_max=1):
    """The text column width of a w px list card with icon_max item cells (>= 240 px, asserted)."""
    tw = w - LIST_CARD_BAR - icon_max * LIST_CARD_CELL - LIST_CARD_ACT_W - LIST_CARD_PAD_R
    fit([LIST_CARD_BAR, icon_max * LIST_CARD_CELL, tw, LIST_CARD_ACT_W, LIST_CARD_PAD_R], w, "card width")
    if tw < 240:
        raise ValueError("list card text column too narrow: %d px" % tw)
    return tw


def _card_col(col, on):
    c = color(col)
    if on is None:
        return c
    sample = render(c) if has_j(c) else c
    return J("(%s) ? (%s) : %s" % (on, java_value(c), java_lit(COLOR["disabled"])), sample)


def _card_look(look, var):
    if isinstance(look, str):
        if look not in LIST_CARD_LOOKS:
            raise ValueError("list card look %r (one of %s)" % (look, ", ".join(sorted(LIST_CARD_LOOKS))))
        bg, bar = LIST_CARD_LOOKS[look]
        return [], color(bg), color(bar)
    conds, last = list(look[:-1]), look[-1]
    if not conds or not isinstance(last, str) or last not in LIST_CARD_LOOKS or any(nm not in LIST_CARD_LOOKS for nm, _c in conds):
        raise ValueError("list card look: a LIST_CARD_LOOKS name or [(look, java condition), ..., last look name]: %r" % (look,))
    if not isinstance(var, str) or not _JAVA_NAME_OK.fullmatch(var):
        raise ValueError("list card var: a lower-case Java local name")
    e_bg, e_bar = java_lit(color(LIST_CARD_LOOKS[last][0])), java_lit(color(LIST_CARD_LOOKS[last][1]))
    for name, cond in reversed(conds):
        e_bg = "(%s) ? %s : (%s)" % (cond, java_lit(color(LIST_CARD_LOOKS[name][0])), e_bg)
        e_bar = "(%s) ? %s : (%s)" % (cond, java_lit(color(LIST_CARD_LOOKS[name][1])), e_bar)
    first = LIST_CARD_LOOKS[conds[0][0]]
    decl = ["String %sBg = %s;" % (var, e_bg), "String %sBar = %s;" % (var, e_bar)]
    return decl, J(var + "Bg", color(first[0])), J(var + "Bar", color(first[1]))


def _card_cell(fid, item, on):
    cell = group(None, None, w=LIST_CARD_CELL, h=LIST_CARD_H)
    anc = {"left": LIST_CARD_CELL - LIST_CARD_FRAME, "top": (LIST_CARD_H - LIST_CARD_FRAME) // 2}
    live = _inside(cell, [item_frame(fid, LIST_CARD_FRAME, anchor=anc, item=item, icon_anchor={"left": 0, "top": 0})])
    if on is None:
        return live
    return choose(J(on), live, _inside(cell, [item_frame(fid, LIST_CARD_FRAME, anchor=anc, item=item, icon_anchor={"left": 0, "top": 0},
                                                         cover=True)]))


class Card(Part):
    """list_card's result: a Part (.h = 84 + 4, .card, .body, .icons, .text, .act, .text_w, and .sets = the line texts) whose
    .java(b) emits the SKYY CARD statements in their order: the runtime look's two String locals, the appends (the icon cells
    in a Java for loop when icons is a Java array expression), the text b.set lines, then the action column. ALWAYS emit a card
    with card.java(b) (a runtime look / an icon loop are not appends: extending it into a bigger Appends would drop them)."""

    def java(self, b="b", page_root=True, sets=None):
        out = list(self.decl)
        for i, (p, mk) in enumerate(self):
            if i == self.act_index:
                out += [java_set(ident, pr, v, b) for ident, pr, v in list(self.sets) + list(sets or [])]
            line = java_append(p, mk, b, page_root)
            if i == self.loop_index:
                out += ["for (int %s = 0; %s < %s.length && %s < %d; %s++) {" % (self.k, self.k, self.icons_expr, self.k, self.icon_max,
                                                                                self.k), "  " + line, "}"]
            else:
                out.append(line)
        return "\n".join(out)


def list_card(parent, ident, w, lines, look="normal", icons=None, icon_item=None, icon_max=1, on=None, ids=None, var="card",
              k="k", action=None):
    """Kit 1.4: ONE list card (the SKYY CARD of SkyyClasses 0.1.8 / SkyyProfiles 0.1.3; research/Skyy-UI-Inventory.md section 6):
    a row of a list_well (Group #ident, LayoutMode Left, 84 high + 4) = the 4 px status bar #<ident>Bar + the card body #<ident>In
    (the look's background) holding the item cells #<icons> (the vanilla slot border with an ItemIcon, 72 px each), the text column
    #<text> (up to three label lines, their Text b.set) and the action column #<act> (200 wide: a normal button or a state_word
    goes in, centred; action= appends one for you).
      parent  the list well; w = the card width (the well's inner width)
      lines   [{"id": suffix, "text": J("javaExpr") / proven text / "" , "kind": label kind, "h": px, "col": COLOR name or J(),
              "wrap": bool, "tag": {"id", "text", "col", "w", "kind"}}] - the label is <ident><suffix>; a tag = a second,
              right-aligned label on the same row (<ident><tag id>, the row <ident><suffix>Row). The heights sum to <= 84.
      look    a LIST_CARD_LOOKS name (selected / pending / normal / off / empty) or [(look, java boolean), ..., last look]: the
              first true condition wins (two String locals <var>Bg / <var>Bar, declared by .java())
      icons   a Java String[] expression (one cell per entry, at most icon_max; icon_item = J(item id of entry k)), or None and
              icon_item = one item id (static or J()): one cell
      on      a Java boolean: false = the coming-later look (grey text, the sold-out cover over the icons); None = always on
      ids     {"icons", "text", "act"} (defaults <ident>Ics / <ident>Txt / <ident>Act) - a restyled page's old ids
    Returns a Card; emit it with card.java(b)."""
    ids = dict(ids or {})
    card = check_id(ident)
    text = check_id(ids.get("text", ident + "Txt"))
    act = check_id(ids.get("act", ident + "Act"))
    icons_id = check_id(ids.get("icons") or ident + "Ics")
    tw = list_card_text_w(w, icon_max)
    decl, bg, bar = _card_look(look, var)
    body = card + "In"
    part = Card(h=LIST_CARD_H + LIST_CARD_GAP, card=card, body=body, icons=icons_id, text=text, act=act, text_w=tw, decl=decl,
                loop_index=None, act_index=None, icons_expr=icons, icon_max=icon_max, k=k)
    part.append((parent, group(card, "Left", h=LIST_CARD_H, anchor={"bottom": LIST_CARD_GAP})))
    part.append((card, group(card + "Bar", None, w=LIST_CARD_BAR, h=LIST_CARD_H, bg=bar)))
    part.append((card, group(body, "Left", w=w - LIST_CARD_BAR, h=LIST_CARD_H, bg=bg)))
    part.append((body, group(icons_id, "Left", w=icon_max * LIST_CARD_CELL, h=LIST_CARD_H)))
    if icons is None:
        part.append((icons_id, _card_cell(card + "F0", icon_item, on)))
    else:
        if not isinstance(icons, str) or not icons.strip() or ";" in icons or has_j(icons):
            raise ValueError("list_card icons: a Java String[] expression (no ';'), or None + one icon_item")
        if not isinstance(k, str) or not _JAVA_NAME_OK.fullmatch(k):
            raise ValueError("list_card k: a lower-case Java loop variable")
        part.loop_index = len(part)
        part.append((icons_id, _card_cell(card + "F" + J(k), icon_item, on)))
    top = fit([ln["h"] for ln in lines], LIST_CARD_H, "card text lines") // 2
    part.append((body, group(text, "Top", w=tw, h=LIST_CARD_H, pad={"top": top} if top else None)))
    for ln in lines:
        lid, col = card + ln["id"], _card_col(ln["col"], on)
        tag = ln.get("tag")
        inline, s = _text_bits(lid, ln.get("text"), "list_card line")
        if tag is None:
            part.append((text, label(lid, inline, ln["kind"], h=ln["h"], col=col, wrap=ln.get("wrap", False), fit=False)))
        else:
            row, tid = card + ln["id"] + "Row", card + tag["id"]
            part.append((text, group(row, "Left", h=ln["h"])))
            part.append((row, label(lid, inline, ln["kind"], w=tw - tag["w"], h=ln["h"], col=col, wrap=False, fit=False)))
            t_in, ts = _text_bits(tid, tag.get("text"), "list_card tag")
            part.append((row, label(tid, t_in, tag.get("kind", "default"), w=tag["w"], h=ln["h"], col=_card_col(tag["col"], on),
                                    align="End", wrap=False, fit=False)))
            s = s + ts
        part.sets.extend(s)
    part.act_index = len(part)
    part.append((body, group(act, "Top", w=LIST_CARD_ACT_W, h=LIST_CARD_H, pad={"top": (LIST_CARD_H - BTN_H) // 2,
                                                                              "left": (LIST_CARD_ACT_W - LIST_CARD_BTN_W) // 2})))
    if action is not None:
        part.append((act, action))
        part.sets.extend(_markup_sets(action))
    return part


def list_card_button(ident, text, kind="secondary", sound=None):
    """The list card's action button: a vanilla normal text button 172 x 44 (append it into the card's action column)."""
    return button(ident, text, kind, w=LIST_CARD_BTN_W, sound=sound)


# ---- text measuring: the client's own font tables (Client/Data/Shared/UI/Fonts/*.json, READ-ONLY; optional)
FONT_DIR = os.path.join(GAME_DIR, "Client", "Data", "Shared", "UI", "Fonts")
# The custom-UI FontName -> the client's font atlas. Inferred, not proven in a document (research/Vanilla-UI-Research.md 3.4): the
# client ships NunitoSans Medium / ExtraBold (+ Regular / SemiBold ttf only) and Lexend-Bold; Default = Nunito Sans (bold =
# ExtraBold), Secondary = Lexend Bold.
FONT_FILES = {("Default", False): "NunitoSans-Medium.json", ("Default", True): "NunitoSans-ExtraBold.json",
              ("Secondary", False): "Lexend-Bold.json", ("Secondary", True): "Lexend-Bold.json"}
# fallback when the client folder is missing: the per-character-class average advances (em) measured from those tables on
# 2026-09-29 (lower-case, upper-case, digit, space, punctuation) + the line height. A flat 0.43 em rule of thumb (the SkyyUiProbe
# harness note) UNDER-estimates running Nunito text (0.49 em Medium / 0.51 em ExtraBold per character) - so the classes are used.
FONT_FALLBACK = {("Default", False): (0.512, 0.665, 0.600, 0.260, 0.428, 1.364),
                 ("Default", True): (0.538, 0.689, 0.600, 0.278, 0.454, 1.364),
                 ("Secondary", False): (0.582, 0.722, 0.594, 0.320, 0.487, 1.25),
                 ("Secondary", True): (0.582, 0.722, 0.594, 0.320, 0.487, 1.25)}
_FONT_CACHE = {}


def font_table(font="Default", bold=False, font_dir=None):
    """({codepoint: advance in em}, line height in em) of the client's font atlas for FontName `font` (bold for Default = the
    ExtraBold table), read-only and cached; None when the client folder / file is missing (text_width then uses FONT_FALLBACK)."""
    if font not in FONTS:
        raise ValueError("font %r: vanilla fonts are Default and Secondary" % (font,))
    name = FONT_FILES[(font, bool(bold))]
    path = os.path.join(font_dir or FONT_DIR, name)
    if path not in _FONT_CACHE:
        tab = None
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            tab = (dict((int(g["unicode"]), float(g["advance"])) for g in d.get("glyphs", ()) if "unicode" in g),
                   float(d["metrics"]["lineHeight"]))
        _FONT_CACHE[path] = tab
    return _FONT_CACHE[path]


def _em(ch, font, bold, tab):
    if tab is not None:
        adv = tab[0]
        v = adv.get(ord(ch))
        return v if v is not None else adv.get(ord("M"), 0.9)       # an unknown glyph counts as wide as M (conservative)
    lo, up, dg, sp, pu, _lh = FONT_FALLBACK[(font, bool(bold))]
    return lo if ch.islower() else up if ch.isupper() else dg if ch.isdigit() else sp if ch == " " else pu


def text_width(text, size, bold=False, font="Default", upper=False, font_dir=None):
    """Kit 1.4: the px width of ONE line of `text` at `size` px (RenderBold, FontName, RenderUppercase as the label renders it),
    from the client's own glyph advances (font_table; the per-class FONT_FALLBACK when the client is not installed). No kerning
    (the atlases carry none). A J() runtime text cannot be measured (ValueError)."""
    if not isinstance(text, str) or has_j(text):
        raise ValueError("text_width measures a static str, not %r" % (text,))
    t = text.upper() if upper else text
    tab = font_table(font or "Default", bold, font_dir)
    return sum(_em(c, font or "Default", bold, tab) for c in t) * size


def line_height(size, font="Default", bold=False):
    """The px height of one text line (the font's line height x size: 1.364 em for Nunito Sans, 1.25 em for Lexend)."""
    tab = font_table(font or "Default", bold)
    return (tab[1] if tab is not None else FONT_FALLBACK[(font or "Default", bool(bold))][5]) * size


def text_lines(text, width, size, bold=False, font="Default", upper=False):
    """Greedy word wrap at spaces: how many lines `text` takes in `width` px (a word wider than the line counts as one line)."""
    lines, cur = 1, ""
    for word in text.split(" "):
        cand = (cur + " " + word) if cur else word
        if not cur or text_width(cand, size, bold, font, upper) <= width:
            cur = cand
        else:
            lines += 1
            cur = word
    return lines


_FIT = {"mode": "print", "seen": set(), "log": []}


def fit_warnings(mode=None, clear=False):
    """Kit 1.4 text-fit WARNINGS (button() / label() / Appends.text / Appends.button, never an error): mode "print" (default:
    'skyyui WARNING: ...' once per message), "collect" (only kept) or "off"; clear=True empties the list. Returns the messages
    so far (a copy)."""
    if mode is not None:
        if mode not in ("print", "collect", "off"):
            raise ValueError("fit_warnings mode print / collect / off")
        _FIT["mode"] = mode
    if clear:
        _FIT["seen"].clear()
        del _FIT["log"][:]
    return list(_FIT["log"])


def _warn_fit(msg):
    if _FIT["mode"] == "off" or msg in _FIT["seen"]:
        return
    _FIT["seen"].add(msg)
    _FIT["log"].append(msg)
    if _FIT["mode"] == "print":
        print("skyyui WARNING: " + msg)


def _pad_h(padding):
    if padding is None:
        return 0
    if isinstance(padding, dict):
        d = dict((str(k).lower(), v) for k, v in padding.items())
        tot = 0
        for k, mult in (("left", 1), ("right", 1), ("horizontal", 2), ("full", 2)):
            n = _sample_num(d.get(k, 0))
            tot += (n or 0) * mult
        return tot
    n = _sample_num(padding)
    return 2 * (n or 0)


def _fit_label(ident, text, size, bold, upper, font, w, padding):
    if not isinstance(text, str) or has_j(text) or not isinstance(w, int) or isinstance(w, bool) or not isinstance(size, int):
        return
    room = w - _pad_h(padding)
    need = text_width(text, size, bool(bold), font or "Default", bool(upper))
    if need > room + 0.5:
        _warn_fit("label %s %r: %.0f px of %d px %stext in a %d px box - the client clips it (widen the box, wrap it or shorten "
                  "the text)" % ("#" + render(ident) if ident else "(anonymous)", text, need, size, "bold " if bold else "", room))


def _fit_label_kw(ident, text, kind, kw):
    """_fit_label for Appends.text (the label kind's own size / bold / upper / font / wrap, the call's overrides on top)."""
    if not kw.get("fit", True) or kind not in LABELS:
        return
    vs, _kc, kb, ku, _ka, kwr, _ki, _where = LABELS[kind]
    kf = LABEL_MORE.get(kind, (None, None, "Center"))[0]
    wrap = kw.get("wrap")
    if (kwr if wrap is None else bool(wrap)):
        return
    size = kw.get("size") if kw.get("size") is not None else fs(vs)
    bold = kw.get("bold") if kw.get("bold") is not None else kb
    upper = kw.get("upper") if kw.get("upper") is not None else ku
    font = kw.get("font") if kw.get("font") is not None else kf
    _fit_label(ident, text, size, bold, upper, font, kw.get("w"), kw.get("padding"))


def _fit_button(ident, text, size, w, pad):
    if not isinstance(text, str) or has_j(text) or not isinstance(w, int) or isinstance(w, bool):
        return
    room = w - 2 * pad
    need = text_width(text, size, True, "Default", True)
    if need > room + 0.5:
        at12 = need * 12.0 / size
        _warn_fit("button #%s %r: %.0f px of %d px label in %d px (w %d - 2 x %d padding) - the vanilla label shrinks to fit "
                  "(ShrinkTextToFit, down to 12 px: %s); widen the button or shorten the label"
                  % (render(ident), text, need, size, room, w, pad,
                     "it fits at about %d px" % int(size * room / need) if at12 <= room else "still %.0f px at 12 px - it clips" % at12))


# ---- assert_proven: ONE table of the properties a page may use, minus what Skyy has not seen yet (PROBED)
# gate None = PROVEN: used inline by a deployed Skyy page (the kit test checks each one appears in a live build script of the
# tools/deploy_set.py SET - SkyyRanks 0.1.1, SkyyVault 0.1.3, SkyyGear 0.1, SkyyBazaar, SkyySacks, SkyyMenu, ...; the probe mod
# itself not counted); a tuple = the UNVERIFIED / probe keys that prove it (any one of them in PROBED is enough). The base keys are
# what the five held restyles kept out by hand (FlexWeight, WrapMaxLines, LetterSpacing, LayoutMode Center / Right / Full): LayoutMode
# Center is in the SkyyVault 0.1.3 buy dialog, but it stays behind "base" as those reviews decided.
PROVEN_ELEMENTS = {"Group": None, "Label": None, "TextButton": None, "Button": None, "ItemIcon": None, "ItemGrid": None,
                   "TextField": None, "NumberField": ("number-field",), "CheckBox": ("checkbox",), "DropdownBox": ("dropdown",),
                   "ProgressBar": ("progress-element", "memories-bar"), "Sprite": ("spinner",), "ItemSlot": ("itemslot",)}
PROVEN_LAYOUTS = {"Top": None, "Left": None, "TopScrolling": None, "Center": ("base",), "Right": ("base", "layout-right"),
                  "Full": ("base",), "Middle": ("base",), "CenterMiddle": ("base",), "MiddleCenter": ("base",),
                  "LeftCenterWrap": ("base",)}
_P_CHECK, _P_DROP, _P_SEARCH, _P_TIP, _P_PROG = ("checkbox",), ("dropdown",), ("search-field", "dropdown"), ("tooltip",), \
    ("progress-element", "memories-bar")
PROVEN_KEYS = dict([(k, None) for k in (
    "Activate", "Anchor", "AreItemsDraggable", "Background", "Border", "Bottom", "Color", "Default", "Disabled", "DraggedHandle",
    "FontName", "FontSize", "Full", "Handle", "Height", "Horizontal", "HorizontalAlignment", "HorizontalBorder", "Hovered",
    "HoveredHandle", "InfoDisplay", "ItemId", "LabelStyle", "LayoutMode", "Left", "MaxLength", "MaxPitch", "MinPitch",
    "MinShrinkTextToFitFontSize", "MouseHover", "Padding", "PlaceholderStyle", "PlaceholderText", "Pressed", "RenderBold",
    "RenderItalics", "RenderUppercase", "Right", "ScrollbarStyle", "ShrinkTextToFit", "Size", "SlotIconSize", "SlotSize",
    "SlotSpacing", "SlotsPerRow", "SoundPath", "Sounds", "Spacing", "Style", "Text", "TextColor", "TexturePath", "Top", "Vertical",
    "VerticalAlignment", "VerticalBorder", "Visible", "Volume", "Width", "Wrap")]
    + [("FlexWeight", ("base", "flex-rows")), ("LetterSpacing", ("base",)), ("WrapMaxLines", ("base",)),
       ("Value", _P_CHECK + _P_PROG), ("Unchecked", _P_CHECK), ("Checked", _P_CHECK), ("DefaultBackground", _P_CHECK + _P_DROP),
       ("HoveredBackground", _P_CHECK + _P_DROP), ("PressedBackground", _P_CHECK + _P_DROP), ("DisabledBackground", _P_CHECK),
       ("ChangedSound", _P_CHECK), ("ShowSearchInput", _P_DROP), ("SearchInputStyle", _P_DROP), ("ArrowWidth", _P_DROP),
       ("ArrowHeight", _P_DROP), ("DefaultArrowTexturePath", _P_DROP), ("HoveredArrowTexturePath", _P_DROP),
       ("PressedArrowTexturePath", _P_DROP), ("EntriesInViewport", _P_DROP), ("EntryHeight", _P_DROP), ("EntryLabelStyle", _P_DROP),
       ("EntrySounds", _P_DROP), ("FocusOutlineColor", _P_DROP), ("FocusOutlineSize", _P_DROP), ("HorizontalEntryPadding", _P_DROP),
       ("HorizontalPadding", _P_DROP), ("HoveredEntryBackground", _P_DROP), ("PressedEntryBackground", _P_DROP),
       ("NoItemsLabelStyle", _P_DROP), ("PanelAlign", _P_DROP), ("PanelBackground", _P_DROP), ("PanelOffset", _P_DROP),
       ("PanelPadding", _P_DROP), ("PanelScrollbarStyle", _P_DROP), ("SelectedEntryLabelStyle", _P_DROP), ("Close", _P_DROP),
       ("Decoration", ("search-field",)), ("Icon", _P_SEARCH), ("ClearButtonStyle", _P_SEARCH), ("Texture", _P_SEARCH),
       ("HoveredTexture", _P_SEARCH), ("PressedTexture", _P_SEARCH), ("Side", _P_SEARCH), ("Offset", _P_SEARCH),
       ("TooltipText", _P_TIP), ("TextTooltipStyle", _P_TIP), ("MaxWidth", _P_TIP), ("BarTexturePath", _P_PROG),
       ("EffectTexturePath", _P_PROG), ("EffectWidth", _P_PROG), ("EffectHeight", _P_PROG), ("EffectOffset", _P_PROG),
       ("Frame", ("spinner",)), ("PerRow", ("spinner",)), ("Count", ("spinner",)), ("FramesPerSecond", ("spinner",)),
       ("ShowQualityBackground", ("itemslot",)), ("ShowQuantity", ("itemslot",)), ("MaskTexturePath", ("text-mask",)),
       ("LabelMaskTexturePath", ("text-mask",)), ("SlotBackground", ("slot-background",))])
PROVEN_SPECIAL = ((re.compile(r"(?<![A-Za-z])Disabled:\s*true\b"), "Disabled: true", ("disabled-prop",)),
                  (re.compile(r'"(?:\.\./)+ItemQualities/'), "a ../ItemQualities path", ("quality-frame",)),
                  (re.compile(r'"Pages/Memories/Tiles/'), "a Memories tile texture", ("tile",)),
                  (re.compile(r'"Pages/Memories/MemoriesProgress/'), "a Memories bar texture", ("memories-bar",)))
_PROP_KEY_RE = re.compile(r"(?<![A-Za-z0-9_#.$@])([A-Za-z][A-Za-z0-9]*)\s*:")
_LAYOUT_RE = re.compile(r"LayoutMode:\s*([A-Za-z]+)")


class UnprovenError(ValueError):
    """assert_proven found a property / element no deployed Skyy page uses and no PROBED key has proven yet (or an unknown one)."""


def _flat_markups(x):
    if isinstance(x, Choice):
        return list(x.variants())
    if isinstance(x, Shell):
        return _flat_markups(x.appends)
    if isinstance(x, Appends):
        return [v for _p, mk in x for v in _variants(mk)]
    if isinstance(x, str):
        return [x]
    if isinstance(x, (list, tuple)):
        return [v for it in x if it is not None for v in _flat_markups(it)]
    raise ValueError("assert_proven takes markups, Choices, Appends / Parts, Shells or lists of them, not %r" % (x,))


def proven_tokens(markups):
    """{token: gates} of every element, property key, LayoutMode and special path in the markups (gates None = proven)."""
    found = {}
    for mk in _flat_markups(markups):
        full = render(mk)
        bare = _strip_quoted(full)
        for m in _ELEM_OPEN.finditer(bare):
            e = m.group(1)
            found["element " + e] = PROVEN_ELEMENTS.get(e, "unknown")
        for v in _LAYOUT_RE.findall(bare):
            found["LayoutMode: " + v] = PROVEN_LAYOUTS.get(v, "unknown")
        for k in _PROP_KEY_RE.findall(bare):
            found[k] = PROVEN_KEYS.get(k, "unknown")
        for rx, token, gates in PROVEN_SPECIAL:
            if rx.search(full):
                found[token] = gates
    return found


def assert_proven(markups, allow=(), what="page"):
    """Kit 1.4: raise UnprovenError unless every element, property key, LayoutMode and special path in the markups is PROVEN (used
    inline by a deployed Skyy page) or proven by a key in skyyui.PROBED (or in allow=, e.g. allow=("base",) on a page meant to test
    it). One table (PROVEN_ELEMENTS / PROVEN_LAYOUTS / PROVEN_KEYS / PROVEN_SPECIAL) for every restyle, instead of each patch's own
    forbidden-property loop; an element / key the table does not know raises too (classify it first). markups = markup strs,
    Choices, Appends / Parts / Cards, a Shell or lists of them. Returns {token: gates} of everything found."""
    found = proven_tokens(markups)
    ok = set(PROBED) | set(allow or ())
    bad = []
    for tok in sorted(found):
        gates = found[tok]
        if gates == "unknown":
            bad.append("%s (not in the kit's property table - classify it in skyyui.PROVEN_*)" % tok)
        elif gates is not None and not any(g in ok for g in gates):
            bad.append("%s (needs %s in skyyui.PROBED: probe page %s)" % (tok, " or ".join(gates),
                                                                           " / ".join(_probe_of(g) for g in gates)))
    if bad:
        raise UnprovenError("assert_proven(%s): %d unproven: %s" % (what, len(bad), "; ".join(bad)))
    return found


def _probe_of(key):
    return {"base": "base1 / base2 / base3", "base4": "base4 (19)", "button-text": "20", "flex-rows": "21",
            "layout-right": "22"}.get(key, key)


# ================================================================= probe pages: the in-game gate for everything UNVERIFIED
class Probe(object):
    """One in-game probe page: n (its number), name (a STABLE key for a probe command: "base1", "checkbox", ... - numbers may
    grow, names do not; probe_page(name)), key (the UNVERIFIED key it proves: add it to PROBED once the page works; "base" for the
    base pages 1, 2 and 18), shell (appends + b.set lines), look (the short numbered "what to see" list - the page shows it too),
    java_extra (extra Java statements with %B% for the builder variable, or callables f(b) -> statements).
    Kit 1.4: summary (one line, <= 95 characters: what the page proves - for a probe mod's index / list; PROBE_SUMMARY) and
    with_footer(footer, foot_h) (the probe mod's Back / Close footer placed by the kit, with the height proofs)."""

    def __init__(self, n, key, shell, look, java_extra=(), name=None, summary=None):
        self.n, self.key, self.shell, self.look, self.java_extra = n, key, shell, list(look), list(java_extra)
        self.name = name or key
        s = summary or PROBE_SUMMARY.get(self.name) or UNVERIFIED.get(self.key, self.name)
        self.summary = s if len(s) <= 95 else s[:92] + "..."

    def java(self, b="b", extra=True):
        more = [x(b) if callable(x) else x.replace("%B%", b) for x in self.java_extra] if extra else []
        return "\n".join([self.shell.java(b)] + more)

    def check(self):
        return self.shell.appends.check(self.shell.prefix)

    def with_footer(self, footer, foot_h, foot_w=0, slack=4, prefix=None):
        """Kit 1.4 (the public footer hook): this page with a probe mod's own footer (SkyyUiProbe's Back / Close row) placed by the
        kit. footer(container_id) -> the footer's appends [(parent, markup), ...] (an Appends keeps its .sets), foot_h = its
        outer height. Placement (the SkyyUiProbe 0.1 rules, proven with used_height): at the END of the page body, the page
        root taller by foot_h (+ up to `slack` px when the body had less free), when the page stays <= 980 px; otherwise at the
        bottom of a LayoutMode Top column with a fixed Height, no Padding, >= foot_w wide and >= foot_h + slack px free (not the
        look list). The page's own markup is not changed (a copy). Returns a Part: .appends (the page + footer, check_page-ed
        with every b.set target), .sets (+ the shell's own), .container, .how, .h (the page height), .java(b) (the page's Java with
        the root height line + the footer lines; java_extra after them); raises when there is no room."""
        sh = self.shell
        ap = Appends(sh.appends)
        root_par, root_mk = ap[0]
        m = re.fullmatch(r"Group #(%s) \{ Anchor: \(Width: (\d+), Height: (\d+)\); \}" % re.escape(render(sh.root)), render(root_mk))
        if root_par is not None or not m or int(m.group(3)) != sh.h:
            raise ValueError("probe %d: the page root is not the kit's Width / Height root" % self.n)
        used = used_height(ap, sh.body)
        grow = foot_h + max(0, slack - (sh.inner_h - used))
        page_h, container, how = sh.h, None, None
        if sh.h + grow <= MAX_PAGE_H:
            page_h = sh.h + grow
            assert_page_size(sh.w, page_h)
            ap[0] = (None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (m.group(1), sh.w, page_h))
            left = fit([used, foot_h], sh.inner_h + grow, "probe %d body + footer" % self.n)
            container, how = sh.body, "body end, page %d -> %d px high, %d px slack" % (sh.h, page_h, left)
        else:
            for par, mk in ap:
                if par is None or isinstance(mk, Choice):
                    continue
                em = _ELEM_OPEN.match(_strip_quoted(render(mk)))
                cid = em.group(2) if em else None
                own = _own_props(mk)
                av = _anchor_vals(mk)
                if (not cid or cid.endswith("Look") or _top_prop(own, "LayoutMode") != "Top" or "Height" not in av
                        or _top_prop(own, "Padding") is not None or av.get("Width", foot_w) < foot_w):
                    continue
                free = av["Height"] - used_height(ap, cid)
                if free >= foot_h + slack:
                    container, how = cid, "bottom of #%s (%d px free, %d px slack), page stays %d px high" % (cid, free, free - foot_h,
                                                                                                          sh.h)
                    break
            if container is None:
                raise ValueError("probe %d (%s): no place for a %d px footer (page %d px high, no column with %d px free)"
                                 % (self.n, self.name, foot_h, sh.h, foot_h + slack))
        ap.extend(footer(container))
        chk = Appends(ap)
        chk.sets.extend(sh.sets)
        check_page(chk, prefix)
        more = [x("b") if callable(x) else x.replace("%B%", "b") for x in self.java_extra]
        view = Part(ap, container=container, how=how, h=page_h, shell_sets=list(sh.sets), extra=more)

        def java(b="b", page_root=True, sets=None):
            lines = [ap.java(b, page_root, list(sh.sets) + list(sets or []))]
            lines += [x(b) if callable(x) else x.replace("%B%", b) for x in self.java_extra]
            return "\n".join(lines)
        view.java = java
        view.sets = list(ap.sets) + list(sh.sets)
        view.appends = ap
        return view


PROBE_BASE = ("base1", "base2", "base3")     # the base pages (key "base", numbers 1, 2 and 18): open these first
PROBE_OPEN_FIRST = PROBE_BASE + ("base4",)   # kit 1.4: the order to open the base pages in (base4 = page 19, the 1.4 builders)
# kit 1.4: one line per probe page - what it proves (the SkyyUiProbe 0.1 index texts for 1-18); Probe.summary
PROBE_SUMMARY = {
    "base1": "Window frame, gold ornaments, close X, all button kinds + sounds, tabs, big text, separators",
    "base2": "Plain window, list well + scrollbar, list rows, property box, cards, 3 text field looks, option / nav rows",
    "base3": "Kit 1.3 builders: pager, item grid, icon cells, confirm views, punctuated text, big number",
    "checkbox": "CheckBox element inline (tick / untick sound)",
    "number-field": "NumberField element inline (digits only)",
    "tooltip": "Hover tooltips on a button and a label; Esc with a tooltip open",
    "progress-element": "Vanilla ProgressBar element (its Value set from the server)",
    "memories-bar": "Textured Memories progress bar",
    "quality-frame": "Item quality slot frames + a quality tooltip frame (../ItemQualities paths)",
    "itemslot": "ItemSlot element with its quality background",
    "dropdown": "DropdownBox, plain and with a search box",
    "search-field": "Search box with the magnifier and the clear x",
    "spinner": "Loading spinner (animated sprite)",
    "tile": "Memories tile textures in their 4 states",
    "text-mask": "Gradient text mask on a label and on a nav button",
    "slot-background": "Slot backgrounds in an item grid",
    "disabled-prop": "Disabled: true on a button (grey look, no click)",
    "value-ref": "A button style set by reference to the vanilla style",
    "base4": "Kit 1.4 builders: fixed rows, list wells, stat wells + bars, columns, cards, state words",
    "button-text": "Button labels set from the server (b.set on a TextButton Text)",
    "flex-rows": "FlexWeight on its own: flex buttons, a flex label, a flex spacer, a flex filler",
    "layout-right": "LayoutMode Right on its own: a right-aligned footer and rows",
}


def _look_lines(name, look, w, size=16):
    """(head, numbered lines, line heights, total height) of a probe page's own "what to see" list in w px (wrapped default
    labels: about 0.55 em per character, 21 px per line)."""
    head = "Probe " + name + " - what to see"
    lines = ["%d. %s" % (i + 1, t[:1].upper() + t[1:]) for i, t in enumerate(look)]
    per = max(10, int((w - 4) / (size * 0.55)))
    hs = [max(1, -(-len(t) // per)) * 21 + 4 for t in lines]
    return head, lines, hs, (fs(13) + 10) + 10 + 4 + sum(hs)


def _look_list(ap, parent, P, name, look, w):
    """Append the probe page's numbered "what to see" list (Group #<P>Look: a section head + one wrapped label per line; the lines
    hold punctuation, so they are b.set lines - Appends.text). Returns its height."""
    head, lines, hs, total = _look_lines(name, look, w)
    ap.append((parent, group(P + "Look", "Top", w=w, h=total)))
    ap.append((P + "Look", section(P + "LookH", head)))
    for i, (t, h) in enumerate(zip(lines, hs)):
        ap.text(P + "Look", P + "Look" + str(i + 1), t, "default", h=h, wrap=True)
    return total


def _probe_shell(prefix, n, title, h, w=900, kind="plain"):
    return page_shell(prefix + str(n), w, h, title, kind=kind)


def probe_pages(prefix="SkyyPb"):
    """The in-game probe pages (engine review 7 / open question 8). The BASE pages (key "base": base1 = page 1, base2 = page 2,
    base3 = page 18) show the kit's core look - every property the restyles rely on that no Skyy page has used inline yet, and
    the kit 1.3 builders made from them; then ONE page per UNVERIFIED feature (3-17), so a page that fails to parse ("Failed to
    parse or resolve document" = a disconnect) names its culprit. Every page shows its own numbered "what to see" list (Probe.look)
    and has a stable name (Probe.name; probe_page(name)). A mod-side probe command opens a page with probe.java("b") inside a
    CustomUIPage build (no bindings needed). Order: base1, base2, base3, then 3-17; after a page works in game, add its key to
    PROBED (and tell the next builders). Returns [Probe, ...] in number order.
    Kit 1.4 appends pages 19-22 (1-18 keep their numbers, names and content): 19 base4 (the kit 1.4 builders, key "base4"),
    20 button-text (b.set on a TextButton Text), 21 flex-rows (FlexWeight on its own), 22 layout-right (LayoutMode Right on its
    own). Open order: PROBE_OPEN_FIRST (base1, base2, base3, base4), then the rest by number. Every page body's children have a
    fixed Height (or a FlexWeight), so used_height / Probe.with_footer can prove where a probe mod's footer goes."""
    check_id(prefix)
    pages = []
    t = True

    # ---- page 1 (base1): frame, ornaments, close X, buttons, tabs, text
    look1 = ["the page opens (no disconnect): every base property parses inline",
             "title bar: runes, KIT PROBE 1 in the Secondary font; the gold ornaments show above and below, not clipped",
             "the close X hangs off the top-right corner; its click is the cancel sound",
             "tabs: three equal tabs 5 px apart, the first gold (Primary); below them two tertiary tabs, the first outlined gold",
             "every button changes on hover / press and clicks; BACK and DELETE use the cancel sound",
             "LOCKED is grey and silent",
             "REFORGE EVERYTHING NOW shrinks to fit its 150 px; the small SAVE (Primary) is 150 wide",
             "12345 is big (32 px, the default font); Letter spacing is spaced out",
             "separators: a thin line, the fancy line with its centre ornament, the gold-brown form line",
             "the long caption stays on one line",
             "CLOSE sits at the bottom right"]
    sh = page_shell(prefix + "1", 1500, 860, "Kit probe 1", close=True)
    P = prefix + "1"
    ap = sh.appends
    main_w = 1066
    ap.append((sh.body, group(P + "Cols", "Left", h=sh.inner_h)))
    ap.append((P + "Cols", group(P + "Main", "Top", w=main_w, h=sh.inner_h)))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    body = P + "Main"
    ap.extend(tab_row(body, P + "Tabs", [P + "TabA", P + "TabB", P + "TabC"], ["Primary tab", "Second", "Third"], 0))
    ap.extend(tab_row(body, P + "Tabt", [P + "TabD", P + "TabE"], ["Quiet on", "Quiet off"], 0, w=190, mode="tertiary"))
    ap.append((body, label(P + "Head", "Buttons", "heading")))
    ap.append((body, button_row(P + "Row1", align="left", top=0)))
    for i, (k, tx, extra) in enumerate((("primary", "Buy", {}), ("secondary", "Back", {"sound": "cancel"}),
                                        ("destructive", "Delete", {}), ("tertiary", "Tertiary", {}),
                                        ("secondary", "Locked", {"disabled": True}))):
        ap.append((P + "Row1", button(P + "B" + str(i), tx, k, anchor={"right": 6}, **extra)))
    ap.append((body, button_row(P + "Row2", h=BTN_BIG_H, align="left")))
    ap.append((P + "Row2", button(P + "S0", "Save", "primary", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S1", "Edit", "secondary", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S2", "Remove", "destructive", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S3", "Reforge everything now", "primary", w=150, anchor={"right": 6}, fit=False)))
    ap.append((P + "Row2", button(P + "S4", "Big", "primary", "big")))
    ap.append((body, "Group #%sTxt { Anchor: (Height: 52, Top: 12); LayoutMode: Left; }" % P))
    ap.append((P + "Txt", label(P + "Num", "12345", "display", w=220)))
    ap.append((P + "Txt", label(P + "Spc", "Letter spacing", "strong", w=300, font=FONT_SECONDARY, spacing=0.5)))
    ap.append((P + "Txt", label(P + "Gold", "Gold info", "gold", w=200)))
    ap.append((P + "Txt", label(P + "Ok", "Success", "success", w=200)))
    ap.append((body, separator("content", anchor={"top": SEP_MARGIN, "bottom": SEP_MARGIN})))
    ap.append((body, separator("fancy")))
    ap.append((body, separator("form")))
    ap.append((body, label(P + "Wrap", "One line only - this caption is long enough to wrap but WrapMaxLines keeps one line", "caption",
                           wrap=True, max_lines=1, w=500)))
    ap.append((body, spacer(h=40)))
    ap.append((body, button_row(P + "Foot", align="right")))
    ap.append((P + "Foot", button(P + "Close2", "Close", "secondary", sound="cancel")))
    fit([_look_list(ap, P + "Cols", P, "base1", look1, sh.inner_w - main_w - 22)], sh.inner_h, "probe 1 look list")
    pages.append(Probe(1, "base", sh, look1, name="base1"))

    # ---- page 2 (base2): lists, well, rows, fields, panels (plain window)
    look2 = ["the page opens; the title bar has NO runes and NO ornaments (plain window)",
             "the list sits on a darker well with a slim scrollbar",
             "rows: normal lights up on hover and clicks, selected is blue, static never changes",
             "the first row shows its badge and a small EDIT button",
             "property box: grey bold keys, light blue values, one line each",
             "two trade cards 10 px apart, gold on hover; the second is covered dark (sold out)",
             "three text fields (kit, vanilla, filter look): tell the builder which typed text matches the game",
             "the value box stretches next to BROWSE",
             "option rows: the first tints on hover and is silent, the second has the selected frame",
             "hover rows and nav buttons light up silently; the selected nav item is white and bold on the dark back",
             "the setting row shows ON (gold outline) and OFF; the flat bar is two thirds full",
             "the vertical separators start 2 px above the columns (Top -2)"]
    sh = page_shell(prefix + "2", 1600, 900, "Kit probe 2", kind="plain")
    P = prefix + "2"
    ap = sh.appends
    ap.append((sh.body, "Group #%sCols { FlexWeight: 1; LayoutMode: Left; }" % P))
    ap.append((P + "Cols", "Group #%sL { FlexWeight: 1; LayoutMode: Top; }" % P))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    ap.append((P + "Cols", "Group #%sR { FlexWeight: 1; LayoutMode: Top; }" % P))
    ap.append((P + "L", section(P + "Sec", "Section head")))
    ap.append((P + "L", scroll_list(P + "List", h=260, well=True)))
    for i, st in enumerate(("normal", "selected", "static")):
        rid = P + "Row" + str(i)
        ap.append((P + "List", panel_row(rid, st)))
        ap.append((rid + "Sel", row_text(rid + "T", rid + "N", rid + "D")))
        if i == 0:
            ap.append((rid + "Sel", row_badge(rid + "Bd")))
            ap.append((rid, row_action(rid + "A", "Edit")))
    ap.append((P + "L", panel(P + "Well", "well", h=4 * (fs(13) + 12) + 2 * WELL_PAD, anchor={"top": 8})))
    for i in range(3):
        ap.append((P + "Well", property_row(P + "Pr" + str(i), P + "Pk" + str(i), P + "Pv" + str(i), "Key " + str(i))))
    ap.append((P + "Well", label(P + "Sum", "Summary line", "summary")))
    ap.append((P + "L", "Group #%sCards { Anchor: (Height: %d, Top: 8); LayoutMode: Left; }" % (P, CARD_H)))
    ap.append((P + "Cards", card(P + "Card")))
    ap.append((P + "Cards", card(P + "Soldout", sold_out=True)))
    ap.append((P + "Cards", item_frame(P + "Fr", icon_id=P + "FrI", anchor={"left": 8})))
    ap.append((P + "R", label(P + "Fk", "Text field - kit look", "default")))
    ap.append((P + "R", text_field(P + "Fkb", P + "Fkf", placeholder="type here")))
    ap.append((P + "R", label(P + "Fv", "Text field - vanilla look", "default", anchor={"top": 6})))
    ap.append((P + "R", text_field(P + "Fvb", P + "Fvf", placeholder="type here", look="vanilla")))
    ap.append((P + "R", label(P + "Ff", "Text field - filter look", "default", anchor={"top": 6})))
    ap.append((P + "R", text_field(P + "Ffb", P + "Fff", placeholder="filter", look="filter")))
    ap.append((P + "R", "Group #%sVb { Anchor: (Height: %d, Top: 8); LayoutMode: Left; }" % (P, FIELD_H)))
    ap.append((P + "Vb", value_box(P + "Vbx", P + "Vbl", flex=1, anchor={"right": 8})))
    ap.append((P + "Vb", button(P + "Vbb", "Browse", w=150)))
    ap.append((P + "R", option_row(P + "Op0", anchor={"top": 8})))
    ap.append((P + "Op0", label(P + "Op0N", "Option", "optionName", h=False, flex=2, padding={"left": 14})))
    ap.append((P + "Op0", label(P + "Op0D", "12 m", "optionDetail", h=False, flex=1)))
    ap.append((P + "R", option_row(P + "Op1", True)))
    ap.append((P + "R", hover_row(P + "Hr0", h=44)))
    ap.append((P + "Hr0", item_icon(None, "Weapon_Sword_Iron")))
    ap.append((P + "Hr0", label(P + "Hr0N", "Hover row", "bold", h=False, flex=1, padding={"horizontal": 10})))
    ap.append((P + "R", hover_row(P + "Hr1", "selected", h=44)))
    ap.append((P + "R", list_button(P + "Lb0", "Nav item")))
    ap.append((P + "R", list_button(P + "Lb1", "Nav selected", "selected")))
    ap.append((P + "R", setting_row(P + "Set", P + "SetL", label_w=300)))
    for mk in on_off(P + "Set", True):
        ap.append((P + "Set", mk))
    ap.append((P + "R", bar(P + "Stat", 300, 12, 180, anchor={"top": 8})))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    fit([_look_list(ap, P + "Cols", P, "base2", look2, 400)], sh.inner_h, "probe 2 look list")
    sh.sets.append((P + "SetL", "Text", "Setting row"))
    pages.append(Probe(2, "base", sh, look2, name="base2"))

    # ---- one page per UNVERIFIED feature (the page grows by its "what to see" list)
    def small(n, key, title, h, build, look, extra=(), w=900):
        lh = _look_lines(key, look, w - 2 * CONTENT_PAD)[3]
        s = _probe_shell(prefix, n, title, h + lh, w)
        build(s, prefix + str(n))
        _look_list(s.appends, s.body, prefix + str(n), key, look, s.inner_w)
        pages.append(Probe(n, key, s, look, extra, name=key))

    def b_checkbox(s, p):
        s.appends.append((s.body, checkbox(p + "C0", True, trial=t)))
        s.appends.append((s.body, checkbox(p + "C1", False, trial=t, anchor={"top": 8})))
        s.appends.append((s.body, checkbox_row(p + "Row", p + "RowL", p + "RowC", True, "Include entities", trial=t, anchor={"top": 12})))

    small(3, "checkbox", "Probe checkbox", 300, b_checkbox, [
        "the page opens", "two check boxes (checked, empty) in the vanilla frame; a click toggles with the tick / untick sound",
        "the row: Include entities (a 220 px label), then its box"])

    def b_number(s, p):
        s.appends.append((s.body, text_field(p + "Nb", p + "N", 200, number=True, trial=t)))

    small(4, "number-field", "Probe number field", 240, b_number, [
        "the page opens", "a number box in the input frame: letters are refused, digits work"])

    def b_tooltip(s, p):
        s.appends.append((s.body, button(p + "Tip", "Hover me", extra=tooltip("Sells for 20 coins", trial=t))))
        s.appends.append((s.body, label(p + "Tl", "Hover this label", "default", anchor={"top": 12}, extra=tooltip("A label tooltip", trial=t))))

    small(5, "tooltip", "Probe tooltip", 260, b_tooltip, [
        "the page opens", "hovering the button or the label shows the vanilla tooltip frame with its text",
        "Esc with a tooltip open closes the page cleanly (no stuck tooltip)"])

    def b_progress(s, p):
        s.appends.append((s.body, progress(p + "Pr", value=0.6, trial=t)))
        s.sets.append((p + "Pr", "Value", 0.75))

    small(6, "progress-element", "Probe progress", 220, b_progress, [
        "the page opens", "a thin vanilla bar three quarters full (the b.set Value 0.75 wins over the inline 0.6)"])

    def b_membar(s, p):
        s.appends.append((s.body, progress(p + "Mb", value=0.4, kind="memories", trial=t)))
        s.sets.append((p + "Mb", "Value", 0.5))
        s.sets.append((p + "MbTex", "Value", 0.5))

    small(7, "memories-bar", "Probe memories bar", 220, b_membar, [
        "the page opens", "the Memories bar: a framed track, half full, a glowing tip at the fill end"])

    def b_quality(s, p):
        s.appends.append((s.body, "Group #%sQs { Anchor: (Height: %d); LayoutMode: Left; }" % (p, SLOT_FRAME)))
        for i, q in enumerate(("Common", "Uncommon", "Rare", "Epic", "Legendary")):
            s.appends.append((p + "Qs", quality_frame(p + "Q" + str(i), q, icon_id=p + "Q" + str(i) + "I", trial=t, anchor={"right": 8})))
            s.sets.append((p + "Q" + str(i) + "I", "ItemId", "Weapon_Sword_Iron"))
        s.appends.append((s.body, tooltip_panel(p + "Tp", w=360, h=120, quality="Rare", trial=t, anchor={"top": 12})))
        s.appends.append((p + "Tp", label(p + "TpN", "Rare sword", "tipName", col=QUALITY["Rare"])))

    small(8, "quality-frame", "Probe quality frames", 340, b_quality, [
        "the page opens (the ../ItemQualities paths resolve)",
        "five swords on the Common, Uncommon, Rare, Epic and Legendary slot frames",
        "a Rare item tooltip frame with the name"])

    def b_itemslot(s, p):
        s.appends.append((s.body, item_slot(p + "Sb", p + "Sl", trial=t)))
        s.sets.append((p + "Sl", "ItemId", "Weapon_Sword_Iron"))

    small(9, "itemslot", "Probe item slot", 240, b_itemslot, [
        "the page opens", "the iron sword on its quality background in the 68 px border (no ItemStack sent)"])

    def b_dropdown(s, p):
        s.appends.append((s.body, dropdown(p + "Dd", trial=t)))
        s.appends.append((s.body, dropdown(p + "Ds", search=True, trial=t, anchor={"top": 12})))

    small(10, "dropdown", "Probe dropdown", 260, b_dropdown, [
        "the page opens", "two dropdowns with the caret; a click opens the panel (no entries: a dim line) with the tick sound",
        "the second one has a search box"])

    def b_search(s, p):
        s.appends.append((s.body, search_field(p + "Sb", p + "Sf", 400, placeholder="search", trial=t)))

    small(11, "search-field", "Probe search field", 220, b_search, [
        "the page opens", "an input box with the magnifier on the left; typing shows the clear x, a click on it empties the box"])

    def b_spinner(s, p):
        s.appends.append((s.body, spinner(p + "Sp", trial=t)))

    small(12, "spinner", "Probe spinner", 200, b_spinner, ["the page opens", "the loading spinner turns smoothly"])

    def b_tile(s, p):
        s.appends.append((s.body, "Group #%sTiles { Anchor: (Height: %d); LayoutMode: Left; }" % (p, TILE_H + TILE_GAP)))
        for i, st in enumerate(TILE_STATES):
            s.appends.append((p + "Tiles", tile(p + "T" + str(i), st.upper()[:8], st, trial=t)))

    small(13, "tile", "Probe tiles", 320, b_tile, [
        "the page opens", "four Memories tiles: default (lights on hover, clicks), selected, complete, empty (dim, no click)"], w=900)

    def b_mask(s, p):
        s.appends.append((s.body, gradient_label(p + "G", "Gradient heading", trial=t)))
        s.appends.append((s.body, list_button(p + "Lb", "Nav selected", "selected", mask=True, trial=t)))

    small(14, "text-mask", "Probe text mask", 220, b_mask, [
        "the page opens", "the heading and the selected nav text fade with the vanilla gradient"])

    def b_slotbg(s, p):
        s.appends.append((s.body, item_grid(p + "Grid", 4, 1, well=False, slot_bg=True, trial=t)))

    small(15, "slot-background", "Probe slot background", 240, b_slotbg, [
        "the page opens", "the empty 4-slot grid shows the block selector slot backgrounds"])

    def b_disabled(s, p):
        s.appends.append((s.body, button(p + "D", "Disabled", disable_element=True, trial=t)))

    small(16, "disabled-prop", "Probe disabled", 200, b_disabled, [
        "the page opens", "the button shows the grey Disabled look by itself and does not click"])

    def b_ref(s, p):
        s.appends.append((s.body, button(p + "R", "By reference", fit=False)))

    small(17, "value-ref", "Probe style reference", 200, b_ref, [
        "the page opens", "the button turns into the gold Primary (Value.ref of Common.ui DefaultTextButtonStyle)"],
        extra=[java_ref_style(prefix + "17R", "DefaultTextButtonStyle", b="%B%", trial=t)])

    # ---- page 18 (base3): the kit 1.3 builders (pager, item grid, icon cells, confirm views, punctuated text, display)
    look18 = ["the page opens (every piece uses base properties only)",
              "pager: < PREV greyed out and silent, the caption Page 2 / 5 in the middle, NEXT > normal with the click",
              "item grid: 5 x 2 slots on a dark well - a sword, 64 iron bars, a pickaxe, 12 bread; hover shows the item tooltip",
              "icon cells: normal (lighter on hover, click), selected (blue), disabled (dark cover, silent), empty; then the "
              "plain pair (no back, hover dark, selected light blue)",
              "the first cell shows 64 at its bottom right",
              "confirm view: yellow question, grey message, CONFIRM (gold, save sound) and CANCEL (cancel sound) centred",
              "the one-row confirm: the question on the left, SWITCH (red) and CANCEL on the right",
              "the line Costs 1,250 coins (50% off) shows its comma, brackets and percent sign",
              "12345 big in the default font"]
    sh = page_shell(prefix + "18", 1400, 960, "Kit probe 18")
    P = prefix + "18"
    ap = sh.appends
    main_w = 900
    ap.append((sh.body, group(P + "Cols", "Left", h=sh.inner_h)))
    ap.append((P + "Cols", group(P + "Main", "Top", w=main_w, h=sh.inner_h)))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    body = P + "Main"
    used = []
    ap.append((body, label(P + "H1", "Pager", "heading")))
    used.append(fs(18) + 10)
    pg = pager(body, P + "Pg", main_w, text="Page 2 / 5", prev_on=False)
    ap.extend(pg)
    used.append(pg.h)
    ap.append((body, label(P + "H2", "Item grid", "heading", anchor={"top": 12})))
    used.append(fs(18) + 10 + 12)
    ap.append((body, item_grid(P + "Grid", 5, 2)))
    used.append(2 * GRID_SLOT + GRID_SPACING + 2 * GRID_WELL_PAD)
    ap.append((body, label(P + "H3", "Icon cells", "heading", anchor={"top": 12})))
    used.append(fs(18) + 10 + 12)
    ap.append((body, group(P + "Cells", "Left", h=74)))
    used.append(74)
    for i, (st, it, q, lk) in enumerate((("normal", "Ingredient_Bar_Iron", "64", "row"), ("selected", "Weapon_Sword_Iron", False, "row"),
                                         ("disabled", "Food_Bread", False, "row"), ("empty", None, False, "row"),
                                         ("normal", "Plant_Fruit_Apple", False, "plain"), ("selected", "Tool_Pickaxe_Iron", False, "plain"))):
        ap.append((P + "Cells", icon_cell(P + "C" + str(i), it, 74, st, qty=q, look=lk, anchor={"right": 8 if i != 3 else 24})))
    ap.append((body, label(P + "H4", "Confirm view", "heading", anchor={"top": 12})))
    used.append(fs(18) + 10 + 12)
    cv = confirm_view(body, P + "Cf", main_w, question="Sell 64 iron bars?", message="You get 1,250 coins. This cannot be undone.")
    ap.extend(cv)
    used.append(cv.h)
    cc = confirm_view(body, P + "Cc", main_w, question="Switch to Mage for 500 coins?", yes_text="Switch", yes_kind="destructive",
                      compact=True)
    ap.extend(cc)
    used.append(cc.h)
    sh.text(body, None, "Costs 1,250 coins (50% off) - shown exactly as written.", "default", h=26, anchor={"top": 12})
    used.append(26 + 12)
    ap.append((body, label(P + "Num", "12345", "display", h=44)))
    used.append(44)
    fit(used, sh.inner_h, "probe 18 body")
    fit([_look_list(ap, P + "Cols", P, "base3", look18, sh.inner_w - main_w - 22)], sh.inner_h, "probe 18 look list")
    fill = [("Weapon_Sword_Iron", 1), ("Ingredient_Bar_Iron", 64), ("Tool_Pickaxe_Iron", 1), ("Food_Bread", 12)] + [None] * 6
    pages.append(Probe(18, "base", sh, look18, name="base3",
                       java_extra=[lambda b, _p=P, _f=fill: java_grid_fill(_p + "Grid", _f, var="pbGridSlots", b=b)]))

    # ---- kit 1.4: page 19 (base4) - every kit 1.4 builder, from proven properties only (two columns + the look list)
    look19 = ["the page opens: every block is made of properties the deployed pages already use",
              "fixed rows: a blue bar, the sword, name + sub, the 12 m tag, EQUIP; the second row has a greyed EQUIP",
              "column heads MEMBER, LEVEL, WHERE sit exactly over Steve, 12 and Hub",
              "two wells: PURSE and BANK heads, big numbers, grey captions",
              "a green bar two thirds full, then an empty track; the result line under them is green",
              "cards: Warrior on the dark blue step with a blue bar and SELECTED; the second a dark grey card, grey text, LOCKED",
              "a sword in a frame, the same sword under the dark sold-out cover, then two plain cells",
              "the one-row question is grey, CREATE is greyed out and silent, CANCEL is normal",
              "REFRESH and CLOSE sit at the right edge of the right column"]
    P = prefix + "19"
    col_w, look_w = 560, 1600 - 2 * CONTENT_PAD - 2 * 560 - 2 * 22
    left, right = Appends(), Appends()
    L, R = P + "L", P + "R"
    lw = list_well(P + "Lw", w=col_w, rows=2)
    left.add(L, label(P + "H1", "Fixed rows in a list well", "heading", wrap=False))
    left.add(L, lw)
    left.add(P + "Lw", static_row(P + "Ra", lw.inner_w, icon="Weapon_Sword_Iron", name="Iron sword", sub="Rare - equipped", tag="12 m",
                                  action="Equip"))
    left.add(P + "Lw", static_row(P + "Rb", lw.inner_w, name="Empty slot", sub="Craft one at a Workbench", bar=None, action="Equip",
                                  action_on=False))
    spec = column_spec([("Member", 200), ("Level", 100), ("Where", 200)], avail=col_w, pad_left=8)
    left.add(L, label(P + "H2", "Column heads", "heading", wrap=False, anchor={"top": 12}))
    left.add(L, spec.heads(P + "Hd"))
    left.add(L, spec.row(P + "Cr", ["Steve", "12", "Hub"], kinds=["rowName", "default", "rowSub"]))
    left.add(L, label(P + "H3", "Stat wells and bars", "heading", wrap=False, anchor={"top": 12}))
    left.add(L, group(P + "Sw", "Left", h=118))
    left.add(P + "Sw", stat_well(P + "Sa", "Purse", "12345", "coins you carry", w=270))
    left.add(P + "Sw", stat_well(P + "Sb", "Bank", "987", "safe when you die", w=270, anchor={"left": 12}))
    left.add(L, group(P + "Bars", "Top", h=66, anchor={"top": 12}))
    left.add(P + "Bars", label(P + "Bl", "Health 18 / 20", "propValue", h=26, wrap=False))
    left.add(P + "Bars", stat_bar(P + "Bf", 300, 12, 200, col="progressGreen", anchor={"top": 8}).pick())
    left.add(P + "Bars", stat_bar(P + "Be", 300, 12, 0, anchor={"top": 8}).pick())
    left.add(L, result_line(P + "Res", "success", h=44, anchor={"top": 12}))
    left.sets.append((P + "Res", "Text", "Equipped the iron sword - 2 slots left."))
    right.add(R, label(P + "H4", "List cards", "heading", wrap=False))
    cw = list_well(P + "Cw", w=col_w, h=list_card_h(2))
    right.add(R, cw)
    right.extend(list_card(P + "Cw", P + "Ca", cw.inner_w, [
        {"id": "Nm", "text": "Warrior - your class", "kind": "rowName", "h": 24, "col": "rowName"},
        {"id": "Sk", "text": "Combat skill Swords", "kind": "fieldLabel", "h": 20, "col": "value"},
        {"id": "Ds", "text": "Strong in close combat. Wears heavy armour and swings big swords.", "kind": "rowSub", "h": 40, "col": "rowSub",
         "wrap": True}], look="selected", icon_item="Weapon_Sword_Iron", action=state_word(None, "Selected", "success")))
    right.extend(list_card(P + "Cw", P + "Cb", cw.inner_w, [
        {"id": "Nm", "text": "Miner", "kind": "rowName", "h": 24, "col": "disabled",
         "tag": {"id": "Tg", "text": "Coming later", "col": "disabled", "w": 120}},
        {"id": "Sk", "text": "Combat skill Picks", "kind": "fieldLabel", "h": 20, "col": "disabled"}],
        look="off", icon_item="Tool_Pickaxe_Iron", action=state_word(None, "Locked", "disabled")))
    right.add(R, label(P + "H5", "Item frames and static cells", "heading", wrap=False, anchor={"top": 12}))
    right.add(R, group(P + "If", "Left", h=74))
    right.add(P + "If", item_frame(P + "Fa", item="Weapon_Sword_Iron", anchor={"top": 3}))
    right.add(P + "If", item_frame(P + "Fb", item="Weapon_Sword_Iron", cover=True, anchor={"top": 3, "left": 8}))
    right.add(P + "If", icon_cell(P + "Sc", "Food_Bread", 74, "static", qty="12", anchor={"left": 16}))
    right.add(P + "If", icon_cell(P + "Sd", "Ingredient_Bar_Iron", 74, "static", look="plain", qty="64", anchor={"left": 8}))
    right.add(R, label(P + "H6", "One-row question and a right footer", "heading", wrap=False, anchor={"top": 12}))
    cq = confirm_view(R, P + "Cq", col_w, question="Pick a class first - then create the profile", yes_text="Create", yes_w=160,
                      no_w=160, compact=True, top=0, wrap=True, yes_on=False, q_col="text")
    right.extend(cq)
    right.add(R, button_row(P + "Ft", align="right", top=12, used=2 * BTN_MIN_W + 6, avail=col_w))
    right.add(P + "Ft", button(P + "Rf", "Refresh"))
    right.add(P + "Ft", button(P + "Cl", "Close", sound="cancel", anchor={"left": 6}))
    content_h = max(used_height(left, L), used_height(right, R), _look_lines("base4", look19, look_w)[3])
    sh = page_shell(P, 1600, TITLE_H + 2 * CONTENT_PAD + content_h, "Kit probe 19")
    ap = sh.appends
    ap.append((sh.body, group(P + "Cols", "Left", h=sh.inner_h)))
    ap.append((P + "Cols", group(L, "Top", w=col_w, h=sh.inner_h)))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    ap.append((P + "Cols", group(R, "Top", w=col_w, h=sh.inner_h)))
    ap.append((P + "Cols", separator("vertical", anchor={"left": 8, "right": 8})))
    ap.extend(left)
    ap.extend(right)
    fit([used_height(ap, L)], sh.inner_h, "probe 19 left column")
    fit([used_height(ap, R)], sh.inner_h, "probe 19 right column")
    fit([_look_list(ap, P + "Cols", P, "base4", look19, look_w)], sh.inner_h, "probe 19 look list")
    pages.append(Probe(19, "base4", sh, look19, name="base4"))

    # ---- kit 1.4: page 20 - b.set on a TextButton Text
    def b_btext(s, p):
        a = s.appends
        a.add(s.body, label(p + "Hd", "Button labels set by the server", "heading", wrap=False))
        a.add(s.body, button_row(p + "Row", align="left"))
        a.button(p + "Row", p + "B1", "Buy 1,250 coins?", "primary", w=300, trial=t, anchor={"right": 6})
        a.add(p + "Row", button(p + "B2", "Sell", w=220))
        a.sets.append((p + "B2", "Text", "Sell (64)"))
        a.add(s.body, label(p + "Cp", "Both labels are set by the server after the page is built", "caption", anchor={"top": 8}))
        fit([used_height(a, s.body)], s.inner_h - _look_lines("button-text", look20, s.inner_w)[3], "probe 20 body")

    look20 = ["the page opens", "the first button reads BUY 1,250 COINS? - the comma and the ? came from the server",
              "the second button reads SELL (64), not SELL: the server text replaced the inline one",
              "both buttons still light up on hover and click"]
    small(20, "button-text", "Probe button text", 240, b_btext, look20)

    # ---- kit 1.4: page 21 - FlexWeight on its own
    def b_flex(s, p):
        a = s.appends
        a.add(s.body, group(p + "F1", "Left", h=BTN_H))
        for i, tx in enumerate(("One", "Two", "Three")):
            if i:
                a.add(p + "F1", spacer(TAB_GAP))
            a.add(p + "F1", button(p + "E" + str(i), tx, flex=1))
        a.add(s.body, group(p + "F2", "Left", h=BTN_H, anchor={"top": 12}))
        a.add(p + "F2", label(p + "Fl", "This label takes the free width", "bold", h=False, flex=1))
        a.add(p + "F2", button(p + "Fb", "Browse"))
        a.add(s.body, list_well(p + "Fw", rows=1, anchor={"top": 12}))
        a.add(p + "Fw", panel_row(p + "Fr", "normal"))
        a.add(p + "FrSel", row_text(p + "FrT", p + "FrN", p + "FrD"))
        a.add(p + "FrSel", label(p + "FrB", "", "rowBadge", w=150, h=False, anchor={"left": 8}))    # no WrapMaxLines: FlexWeight only
        a.add(p + "Fr", row_action(p + "FrA", "Edit"))
        a.sets.extend([(p + "FrN", "Text", "Flex row"), (p + "FrD", "Text", "the select button and the text take the width"),
                       (p + "FrB", "Text", "badge")])
        a.add(s.body, group(p + "F4", "Left", h=BTN_H, anchor={"top": 12}))
        a.add(p + "F4", button(p + "Rf", "Refresh"))
        a.add(p + "F4", group(None, None, flex=1))
        a.add(p + "F4", button(p + "Cl", "Close", sound="cancel"))
        a.add(s.body, group(p + "F5", "Top", h=150, anchor={"top": 12}))
        a.add(p + "F5", label(p + "Top", "Top of the column", "default"))
        a.add(p + "F5", group(None, None, flex=1))
        a.add(p + "F5", label(p + "Bot", "Bottom of the column", "default"))
        fit([used_height(a, s.body)], s.inner_h - _look_lines("flex-rows", look21, s.inner_w)[3], "probe 21 body")

    look21 = ["the page opens", "ONE, TWO, THREE are three equal buttons 5 px apart across the page",
              "the bold label fills the row and BROWSE sits at its right end",
              "the list row stretches: name and sub on the left, the badge and EDIT at the right",
              "REFRESH on the left, CLOSE pushed to the right edge by the empty flex group",
              "Top of the column at the top, Bottom of the column at the bottom of its 150 px column"]
    small(21, "flex-rows", "Probe flex rows", 560, b_flex, look21, w=1200)

    # ---- kit 1.4: page 22 - LayoutMode Right on its own
    def b_right(s, p):
        a = s.appends
        a.add(s.body, button_row(p + "Ft", align="right", top=0))
        a.add(p + "Ft", button(p + "Rf", "Refresh", anchor={"right": 6}))
        a.add(p + "Ft", button(p + "Cl", "Close", sound="cancel"))
        a.add(s.body, group(p + "Cells", "Right", h=74, anchor={"top": 12}))
        for i, (it, q) in enumerate((("Weapon_Sword_Iron", False), ("Food_Bread", "12"), ("Ingredient_Bar_Iron", "64"))):
            a.add(p + "Cells", icon_cell(p + "C" + str(i), it, 74, "static", qty=q, anchor={"left": 8}))
        a.add(s.body, group(p + "Lb", "Right", h=30, anchor={"top": 12}))
        a.add(p + "Lb", label(None, "First", "bold", w=120, h=30))
        a.add(p + "Lb", label(None, "Second", "bold", w=120, h=30))
        fit([used_height(a, s.body)], s.inner_h - _look_lines("layout-right", look22, s.inner_w)[3], "probe 22 body")

    look22 = ["the page opens", "REFRESH then CLOSE hug the right edge (tell the builder if CLOSE comes first)",
              "the three item cells sit at the right edge, the sword first", "FIRST and SECOND sit at the right edge"]
    small(22, "layout-right", "Probe layout right", 300, b_right, look22, w=1000)
    pages.sort(key=lambda pg: pg.n)
    for pg in pages:
        pg.check()
    return pages


def probe_page(which, prefix="SkyyPb"):
    """One probe page by its stable name ("base1", "checkbox", "base3", ...) or its number."""
    for pg in probe_pages(prefix):
        if pg.name == which or pg.n == which:
            return pg
    raise KeyError("no probe page %r (names: %s)" % (which, ", ".join(p.name for p in probe_pages(prefix))))


# ================================================================= verify() - the build-time vanilla check
def _zip_path(path):
    """The Assets.zip entry of an inline path (relative to the custom root; "../" climbs out of it)."""
    return posixpath.normpath(CUSTOM + path)


def _az_texture(names, path):
    base = _zip_path(path)
    return base in names or (base[:-4] + "@2x.png") in names


def texture_files():
    return sorted(set(TEX.values()))


def sound_files():
    return sorted(set(SND.values()))


def verify(assets_zip=None, client_dir=None, quiet=False):
    """Open Assets.zip READ-ONLY and prove every vanilla value, texture and sound the kit emits is still there verbatim (and the
    item quality text colours / slot frames / tooltip frames in Server/Item/Qualities). Client-only reference values are checked too
    when the client folder exists (skipped otherwise). Raises VanillaCheckError (a SystemExit: the build stops) on a missing
    Assets.zip or any drift. Returns {"values": n, "files": m, "client": k or 0, "client_dir": bool}; prints the 'vanilla look
    checked' line unless quiet. Only a passing verify() unlocks the Java emitters."""
    _STATE["verified"] = False
    path = assets_zip or ASSETS_ZIP
    if not os.path.isfile(path):
        raise VanillaCheckError("skyyui.verify: Assets.zip not found at %s - the vanilla look cannot be checked, so the build stops "
                                "(install / update the game, or pass the path: skyyui.verify(r'...\\Assets.zip'))" % path)
    bad, values, files = [], 0, 0
    with zipfile.ZipFile(path, "r") as z:
        names = set(z.namelist())
        cache = {}
        for doc, needle, what in _CHECKS:
            if doc in CLIENT_DOCS:
                continue
            f = CUSTOM + DOCS[doc] + ".ui"
            if f not in names:
                bad.append("%s is missing (needed for %s)" % (f, what))
                continue
            if f not in cache:
                cache[f] = z.read(f).decode("utf-8", "replace").replace("\r\n", "\n")
            if needle not in cache[f]:
                bad.append("%s no longer contains %r (%s)" % (f, needle, what))
            else:
                values += 1
        for q, want in sorted(QUALITY.items()):
            f = "Server/Item/Qualities/%s.json" % q
            try:
                d = json.loads(z.read(f).decode("utf-8", "replace"))
            except KeyError:
                bad.append("%s is missing (quality colour %s)" % (f, q))
                continue
            ok = True
            if str(d.get("TextColor", "")).lower() != want.lower():
                bad.append("%s TextColor is %s, the kit has %s" % (f, d.get("TextColor"), want))
                ok = False
            for key, frame in (("SlotTexture", "UI/ItemQualities/Slots/Slot%s.png" % QUALITY_SLOT[q]),
                               ("ItemTooltipTexture", "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % QUALITY_TIP[q])):
                if d.get(key) != frame:
                    bad.append("%s %s is %s, the kit has %s" % (f, key, d.get(key), frame))
                    ok = False
            values += 1 if ok else 0
        for t in texture_files():
            if _az_texture(names, t):
                files += 1
            else:
                bad.append("texture %s (as %s or its @2x) is not in Assets.zip" % (t, _zip_path(t)))
        for s in sound_files():
            if _zip_path(s) in names:
                files += 1
            else:
                bad.append("sound %s is not in Assets.zip" % _zip_path(s))
    cdir = client_dir or CLIENT_UI_DIR
    client, have_client = 0, os.path.isdir(cdir)
    if have_client:
        ccache = {}
        for doc, needle, what in _CHECKS:
            if doc not in CLIENT_DOCS:
                continue
            f = os.path.join(cdir, *(CLIENT_DOCS[doc] + ".ui").split("/"))
            if f not in ccache:
                ccache[f] = open(f, encoding="utf-8", errors="replace").read().replace("\r\n", "\n") if os.path.isfile(f) else None
            if ccache[f] is None:
                bad.append("client document %s is missing (%s)" % (f, what))
            elif needle not in ccache[f]:
                bad.append("client document %s no longer contains %r (%s)" % (f, needle, what))
            else:
                client += 1
    if bad:
        raise VanillaCheckError("vanilla look check failed (%d) - a game update changed a value the skyyui kit copies; re-copy it in "
                                "tools/skyyui.py (research/Vanilla-UI-Style-Guide.md):\n  - %s" % (len(bad), "\n  - ".join(bad)))
    _STATE["verified"] = True
    if not quiet:
        if have_client:
            extra = "+ %d client reference values" % client
        else:
            extra = "client folder not found: %d client reference values skipped" % sum(1 for d, _n, _w in _CHECKS if d in CLIENT_DOCS)
        print("vanilla look checked: %d style values, %d textures / sounds (Assets.zip; %s; %s)" % (values, files, extra, kit_id()))
        if "base" not in PROBED:
            print("  note: the kit's base look is not yet seen in game - open the base probe pages (probe_page(\"base1\"), \"base2\", "
                  "\"base3\" = pages 1, 2, 18) before shipping a restyle")
    return {"values": values, "files": files, "client": client, "client_dir": have_client}


# ================================================================= misc: kit revision, colour lists for lint
def kit_blob():
    """git blob id of this file (= git rev-parse HEAD:tools/skyyui.py when committed), like SkyyMenu pins the config kit."""
    d = open(os.path.abspath(__file__), "rb").read()
    return hashlib.sha1(("blob %d" % len(d)).encode("ascii") + b"\x00" + d).hexdigest()


def kit_id():
    return "skyyui %s %s" % (KIT_VERSION, kit_blob()[:12])


_NORM_RE = re.compile(r"#([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)(?:\(\s*(\d+(?:\.\d+)?|\.\d+)\s*\))?")


def norm_color(c):
    """#RRGGBB(0.50) -> #rrggbb(0.5) (for comparisons); anything that is not a well-formed colour comes back lower-cased."""
    s = c.strip()
    m = _NORM_RE.fullmatch(s)
    if not m:
        return s.lower()
    try:
        a = format(float(m.group(2)), "g") if m.group(2) else None
    except ValueError:
        return s.lower()
    return "#" + m.group(1).lower() + (("(%s)" % a) if a is not None else "")


def allowed_colors():
    """Every colour literal a restyled page may carry: the kit colours, RARITY, RARITY_WYNN and QUALITY (normalised)."""
    out = set()
    for d in (COLOR, RARITY, RARITY_WYNN, QUALITY):
        for v in d.values():
            out.add(norm_color(v))
    return out


def checks():
    """(document key, needle, what) of every vanilla check (read-only copy)."""
    return list(_CHECKS)
