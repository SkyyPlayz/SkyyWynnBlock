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
no duplicate static ids on a page, inline Text only [A-Za-z0-9 <>/-] (anything else goes through b.set), page roots Anchor Width /
Height only, pages fit a 1080 px screen, no document variables (@X / $C) inline, every texture / sound path is one the kit verifies.
Elements nobody has seen work inline yet need trial=True (UNVERIFIED below); probe_pages() builds one in-game test page per
UNVERIFIED feature (plus two "base" pages for the core look) - add a feature to PROBED once Skyy has seen its page work in game.
Kept out on purpose: ItemGridSlot content (the metadata rule stays with the page: only new ItemStack(id, qty)), the full-screen
@PageOverlay dim and the bottom-left BackButton (Skyy page roots are Width / Height only; Esc + a footer Close button do it), the
client-only textures (Pages/Inventory/Slot.png, the client's own tooltip frame, the settings CheckBox toggle), the broken vanilla
styles (@SmallDefaultTextButtonStyle -> Common/ButtonSmall*.png is missing, @ButtonDestructiveSounds -> an undefined sound set).
The item QUALITY frames (Common/UI/ItemQualities/Slots|Tooltips/*.png) ARE in Assets.zip, outside the custom root: only their
inline path "../ItemQualities/..." is unverified (quality_frame / tooltip_panel(quality=), trial=True).
"""
import os, re, json, zipfile, hashlib, posixpath

KIT_VERSION = "1.2"   # 1.2 (2026-09-29, SkyyBank 0.1.4 pilot): + group(), status_line(wrap=, max_lines=, anchor=)

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
               "CH": "Common/Settings/SectionHeader"}

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
# gold: @ColorGoldHighlight is only a UI Gallery sample (TextContent.ui), no real page shows it. Kept for the "=" info mark that
# SkyyRanks / SkyyGear already use; whether "=" stays gold or becomes info #7caacc (BarterPage timer) is Skyy's call (STATUS).
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
# (MemoriesCategory #39f493, PrefabSavePage #ff6b6b). "=" is gold like SkyyRanks 0.1.1 / SkyyGear 0.1 - OPEN for Skyy: keep gold
# or switch to info #7caacc (the colour with real-page support). Change it HERE only; java_status_methods reads this table.
STATUS = {"+": COLOR["success"], "-": COLOR["error"], "=": COLOR["gold"]}

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
FONT_SECONDARY = "Secondary"      # window titles (@TitleStyle), display numbers (PortalDeviceSummon), tile names (Memories)
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
    "base": "the kit's core look inline: frame + ornaments + close X, button textures / states / inline Sounds / Disabled state, "
            "FlexWeight, LayoutMode Full / Right, LetterSpacing, WrapMaxLines, ShrinkTextToFit, the well (probe pages 1-2; "
            "no trial gate - the first restyle waits for these two pages)",
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


def java_append(parent, markup, b="b", page_root=True):
    """One Java statement: b.appendInline(<parent or (String) null>, <markup>); the markup is check_markup-ed first (a root append
    is checked as a page root: Anchor Width / Height only; page_root=False for a HUD root such as Anchor Full 0)."""
    require_verified()
    check_markup(markup, root=(parent is None and page_root))
    p = "(String) null" if parent is None else java_value(_sel(parent))
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


def java_status_methods(name_color="colorOf", name_text="textOf"):
    """Java source of two static methods (CtNewMethod.make each): the vanilla colour of a result line by its first character
    ("+" success #39f493, "-" error #ff6b6b, "=" STATUS["="], else the label colour) and the text without that mark."""
    c = ('public static String %s(String res) {\n  if (res == null || res.length() == 0) return "%s";\n  char c = res.charAt(0);\n'
         '  if (c == \'+\') return "%s";\n  if (c == \'-\') return "%s";\n  if (c == \'=\') return "%s";\n  return "%s";\n}'
         % (name_color, COLOR["text"], STATUS["+"], STATUS["-"], STATUS["="], COLOR["text"]))
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
    """The element ids of one markup that hold no J() value (runtime ids are never counted as duplicates)."""
    return [m.group(2) for m in _ELEM_OPEN.finditer(_strip_quoted(render(s, mark=True))) if m.group(2) and _DYN not in m.group(2)]


def check_markup(s, prefix=None, root=False, kit_paths=True):
    """Syntax / rule check of one inline markup string (raises ValueError). Mirrors SkyyRanks 0.1.1 _check_ui: balanced { } ( ),
    no underscore ids, ids start with the page prefix, no Anchow typo, no ';;', inline Text only [A-Za-z0-9 <>/-], no unfilled
    placeholder - plus: every { opens an element (Type or Type #Id), no duplicate static id, no @variables / $imports inline, every
    texture / sound path is one the kit verifies (kit_paths), and root=True: the page root's Anchor has Width and Height only."""
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
        for m in _ELEM_OPEN.finditer(_strip_quoted(render(mk))):
            if m.group(2):
                seen.add(m.group(2))
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


def text_style(size, col, bold=False, upper=False, italic=False, halign=None, valign="Center", wrap=False, max_lines=None,
               font=None, shrink=None, spacing=None):
    """A LabelStyle value (FontSize, TextColor, ...) in vanilla key order. spacing = LetterSpacing (float allowed: 0.5, 1.8)."""
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
    if spacing is not None:
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
    if max_lines is not None:
        parts.append("WrapMaxLines: %d" % max_lines)
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
    "display": (32, "white", False, False, None, False, False, "big number / display text (PortalDeviceSummon, font Secondary)"),
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
LABEL_MORE = {"display": (FONT_SECONDARY, None, "Center"), "tileName": (FONT_SECONDARY, None, "End"),
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
_need("PS", '@TimeLimitStyle = LabelStyle(FontSize: 32, FontName: "Secondary");', "label display")
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
          extra=""):
    """A Label in one of the vanilla LABELS kinds. Text is empty by default (b.set it); static text must be [A-Za-z0-9 <>/-].
    size defaults to fs(the vanilla size); h defaults to size + 10 (h=False: no Height, the label fills its parent / row);
    col / bold / font (Default / Secondary) / spacing (LetterSpacing, float) / valign (False = none) / ... override the kind."""
    if kind not in LABELS:
        raise ValueError("label kind %r (one of %s)" % (kind, ", ".join(sorted(LABELS))))
    vs, kc, kb, ku, ka, kw, ki, _where = LABELS[kind]
    kf, kml, kva = LABEL_MORE.get(kind, (None, None, "Center"))
    sz = size if size is not None else fs(vs)
    if h is None and isinstance(sz, int):
        h = sz + 10
    elif h is False:
        h = None                       # no Height: the label fills its parent (a row badge, a property value)
    st = text_style(sz, col if col is not None else kc, bold=kb if bold is None else bold, upper=ku if upper is None else upper,
                    italic=ki if italic is None else italic, halign=align if align is not None else ka,
                    valign=kva if valign is None else (None if valign is False else valign), wrap=kw if wrap is None else wrap,
                    max_lines=max_lines if max_lines is not None else kml, font=font if font is not None else kf, spacing=spacing)
    head = "Label #%s { " % check_id(ident) if ident else "Label { "
    return (head + _anchor(w, h, anchor) + _padding(padding) + _flex(flex) + 'Text: "%s"; ' % check_text(text)
            + "Style: %s; " % st + _extra(extra) + "}")


def status_line(ident, color_expr="colorOf(this.info)", h=30, size=16, wrap=False, max_lines=None, anchor=None):
    """The page's result line (SkyyRanks look: 16 px bold, centred) whose colour is picked at runtime by the mark of the result
    ("+" success, "-" error, "=" STATUS["="]: java_status_methods()). color_expr is the Java expression that gives the colour: the
    default assumes your page class keeps the result in a field named `info`. b.set its Text with textOf(...). wrap=True (with a
    taller h, e.g. 44 for two lines) for pages whose results can be longer than one line; max_lines = WrapMaxLines (a "base"
    probe property); anchor = its margins (e.g. {"top": 12})."""
    return label(ident, "", "default", h=h, size=size, bold=True, align="Center", col=J(color_expr, COLOR["success"]),
                 wrap=True if wrap else None, max_lines=max_lines, anchor=anchor)


def title_style():
    """The window title LabelStyle (@Title: ...@TitleStyle + HorizontalAlignment Center)."""
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
           anchor=None, flex=None, disable_element=False, trial=False, extra=""):
    """One vanilla TextButton (bind it with Activating on #ident). w defaults to 172 (normal / big), 92 (small) or 150 (a small
    Primary); a Primary is never narrower than 120 (PointInspectorPage; a J() width is checked by its sample, a flex width is not
    checked). disable_element=True also writes `Disabled: true;` (UNVERIFIED, trial=True)."""
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
    return ("TextButton #%s { " % ident + _anchor(w, h if h is not None else bh, anchor) + "Padding: (Horizontal: %d); " % bp
            + _flex(flex) + dp + 'Text: "%s"; ' % check_text(text)
            + button_style(kind, size, selected, disabled, sound) + " " + _extra(extra) + "}")


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


def button_row(ident, h=BTN_H, align="center", top=8, w=None, anchor=None):
    """A row for buttons (vanilla dialogs: LayoutMode Center, Top 8; give the buttons anchor right / left 6)."""
    lm = {"center": "Center", "left": "Left", "right": "Right"}.get(align)
    if lm is None:
        raise ValueError("align center / left / right")
    return "Group #%s { %s%s}" % (check_id(ident), _anchor(w, h, _merge({"top": top} if top else None, anchor)), _layout(lm))


_need("P", "LayoutMode: Center;\n        Anchor: (Top: 8);", "button row")


def spacer(w=None, h=None):
    """An empty Group of the given size (vanilla @ActionButtonSeparator / @VerticalActionButtonSeparator, EntitySpawnPage tab gap)."""
    if w is None and h is None:
        raise ValueError("spacer needs w or h")
    return "Group { %s}" % _anchor(w, h)


def group(ident=None, layout="Left", w=None, h=None, anchor=None, flex=None, pad=None, extra=""):
    """A plain layout container with NO look of its own (no background, no border): a row (layout "Left") or column ("Top") that
    holds kit elements, the way vanilla pages nest plain Groups (PrefabSavePage `Group { LayoutMode: Left; ... #SelectedPackBox
    ... #BrowsePackButton }`, WorldEventPanelPage #Body / #Panes / #Footer). layout = a LayoutMode (Left, Top, Right, Center,
    Middle, Full, TopScrolling, ... - Right / Center / Full are "base" probe properties; Left / Top are proven on Skyy pages);
    w / h / anchor (margins) / flex / pad (int or dict) / extra as the other builders. ident may be None (an anonymous row). Never a
    page root (page_shell builds that)."""
    head = ("Group #%s { " % check_id(ident)) if ident else "Group { "
    return head + _anchor(w, h, anchor) + _flex(flex) + _layout(layout) + _padding(pad) + _extra(extra) + "}"


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


def panel(ident, kind="simple", w=None, h=None, pad=None, layout="Top", flex=None, anchor=None, extra=""):
    """An inner panel: simple (@SimpleContainer ContainerPanelPatch Border 4, padding 12), full (@Panel ContainerFullPatch 20),
    secondary (ContainerBackgroundSecondary 5, PortalDevice info box), tooltip (the text tooltip frame, padding 24), well (THE vanilla
    inset for summaries / info boxes / form cards: #000000(0.15), padding 8 - WorldEventPanelPage #Summary, BlockSpawner entry
    rows), dark (#000000(0.3): the RespawnPage full-screen block only), row (the #101925(0.55) row panel), hud (a HUD widget:
    #000000(0.2), padding 20 / 10 - Hud/TimeLeft). pad = an int or a {left / right / top / bottom / horizontal / vertical / full} dict."""
    check_id(ident)
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
    p = pad if pad is not None else dpad
    return "Group #%s { %s%s%sBackground: %s; %s%s}" % (ident, _anchor(w, h, anchor), _flex(flex), _layout(layout), bg, _padding(p),
                                                      _extra(extra))


_need("C", '@SimpleContainer = Group {\n  Background: (TexturePath: "Common/ContainerPanelPatch.png", Border: 4);\n  Padding: 12;',
      "simple panel")
_need("C", '@Panel = Group {\n  Background: (TexturePath: "Common/ContainerFullPatch.png", Border: 20);', "full panel")
_need("PD", 'Background: (TexturePath: "../Common/ContainerBackgroundSecondary.png", Border: 5);', "secondary panel")
_need("BS", "LayoutMode: Top;\n  Anchor: (Bottom: 8);\n  Background: (Color: #000000(0.15));\n  Padding: (Full: 8);", "well form card")


# ================================================================= items
def item_icon(ident=None, item_id=None, size=ICON, anchor=None):
    """ItemIcon (metadata-free, proven on Skyy pages). item_id static (b.set "#Id.ItemId" for a runtime one)."""
    head = ("ItemIcon #%s { " % check_id(ident)) if ident else "ItemIcon { "
    iid = ""
    if item_id is not None:
        if has_j(item_id) or not re.fullmatch(r"[A-Za-z0-9_*]+", item_id):
            raise ValueError("static item id %r (letters, digits, _); b.set(\"#Id.ItemId\", id) for a runtime one" % item_id)
        iid = 'ItemId: "%s"; ' % item_id
    return head + _anchor(size, size, anchor) + iid + "}"


def item_frame(ident, size=SLOT_FRAME, border="slotBorder", icon_id=None, icon_size=None, anchor=None, extra=""):
    """The vanilla slot border (BarterTradeRow: a 68 x 68 #1a2530 group, padding 2) - with an ItemIcon inside when icon_id is given
    (icon = size - 4). border = "slotBorderHave" (green: you have it) or any kit colour."""
    check_id(ident)
    inner = (" " + item_icon(icon_id, None, icon_size or size - 4)) if icon_id else ""
    return "Group #%s { %sBackground: %s; Padding: (Full: 2); %s%s}" % (ident, _anchor(size, size, anchor), color(border), _extra(extra),
                                                                     (inner.strip() + " ") if inner else "")


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
    """A list of (parent id or None for the page root, markup). .java(b) = the Java statements, .check(prefix) = check_page."""

    def java(self, b="b", page_root=True):
        return "\n".join(java_append(p, mk, b, page_root) for p, mk in self)

    def check(self, prefix=None, known_parents=()):
        return check_page(self, prefix, known_parents)

    def markups(self):
        return [mk for _p, mk in self]


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


# ================================================================= probe pages: the in-game gate for everything UNVERIFIED
class Probe(object):
    """One in-game probe page: n (1-based), key (the UNVERIFIED key it proves), shell (appends + b.set lines), look (what Skyy
    should see / hear, in order), java_extra (extra Java statements with %B% for the builder variable)."""

    def __init__(self, n, key, shell, look, java_extra=()):
        self.n, self.key, self.shell, self.look, self.java_extra = n, key, shell, list(look), list(java_extra)

    def java(self, b="b", extra=True):
        return "\n".join([self.shell.java(b)] + ([x.replace("%B%", b) for x in self.java_extra] if extra else []))

    def check(self):
        return self.shell.appends.check(self.shell.prefix)


def _probe_shell(prefix, n, title, h, w=900, kind="plain"):
    return page_shell(prefix + str(n), w, h, title, kind=kind)


def probe_pages(prefix="SkyyPb"):
    """The in-game probe pages (engine review 7 / open question 8): pages 1-2 = the kit's core look ("base": every property the
    restyles rely on that no Skyy page has used inline yet), then ONE page per UNVERIFIED feature, so a page that fails to parse
    ("Failed to parse or resolve document" = a disconnect) names its culprit. A mod-side probe command opens page n with
    probe.java("b") inside a CustomUIPage build (no bindings needed). Order: 1, 2, then the rest; after a page works in game, add its
    key to PROBED (and tell the next builders). Returns [Probe, ...]."""
    check_id(prefix)
    pages = []
    t = True

    # ---- page 1: frame, ornaments, close X, buttons, tabs, text
    sh = page_shell(prefix + "1", 1100, 860, "Kit probe 1", close=True)
    P = prefix + "1"
    ap = sh.appends
    ap.extend(tab_row(sh.body, P + "Tabs", [P + "TabA", P + "TabB", P + "TabC"], ["Primary tab", "Second", "Third"], 0))
    ap.extend(tab_row(sh.body, P + "Tabt", [P + "TabD", P + "TabE"], ["Quiet on", "Quiet off"], 0, w=190, mode="tertiary"))
    ap.append((sh.body, label(P + "Head", "Buttons", "heading")))
    ap.append((sh.body, button_row(P + "Row1", align="left", top=0)))
    for i, (k, tx, extra) in enumerate((("primary", "Buy", {}), ("secondary", "Back", {"sound": "cancel"}),
                                        ("destructive", "Delete", {}), ("tertiary", "Tertiary", {}),
                                        ("secondary", "Locked", {"disabled": True}))):
        ap.append((P + "Row1", button(P + "B" + str(i), tx, k, anchor={"right": 6}, **extra)))
    ap.append((sh.body, button_row(P + "Row2", h=BTN_BIG_H, align="left")))
    ap.append((P + "Row2", button(P + "S0", "Save", "primary", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S1", "Edit", "secondary", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S2", "Remove", "destructive", "small", anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S3", "Reforge everything now", "primary", w=150, anchor={"right": 6})))
    ap.append((P + "Row2", button(P + "S4", "Big", "primary", "big")))
    ap.append((sh.body, "Group #%sTxt { Anchor: (Height: 52, Top: 12); LayoutMode: Left; }" % P))
    ap.append((P + "Txt", label(P + "Num", "12345", "display", w=220)))
    ap.append((P + "Txt", label(P + "Spc", "Letter spacing", "strong", w=300, font=FONT_SECONDARY, spacing=0.5)))
    ap.append((P + "Txt", label(P + "Gold", "Gold info", "gold", w=200)))
    ap.append((P + "Txt", label(P + "Ok", "Success", "success", w=200)))
    ap.append((sh.body, separator("content", anchor={"top": SEP_MARGIN, "bottom": SEP_MARGIN})))
    ap.append((sh.body, separator("fancy")))
    ap.append((sh.body, separator("form")))
    ap.append((sh.body, label(P + "Wrap", "One line only - this caption is long enough to wrap but WrapMaxLines keeps one line", "caption",
                              wrap=True, max_lines=1, w=500)))
    ap.append((sh.body, spacer(h=40)))
    ap.append((sh.body, button_row(P + "Foot", align="right")))
    ap.append((P + "Foot", button(P + "Close2", "Close", "secondary", sound="cancel")))
    pages.append(Probe(1, "base", sh, [
        "the page opens (no disconnect): every base property parses inline",
        "title bar: ContainerHeader with runes, KIT PROBE 1 in 15 px Secondary uppercase; the gold ornaments stick out 12 px above "
        "the bar and 6 px below the body and are NOT clipped",
        "the close X hangs 8 px outside the top-right corner; hover / click sound = cancel",
        "tab row 1: three equal-width tabs 5 px apart, the first gold Primary, the others Secondary; row 2 = tertiary, the first "
        "with the gold outline",
        "every button changes texture on hover / press and clicks (Back and Delete = cancel sound); LOCKED is grey and silent",
        "REFORGE EVERYTHING NOW shrinks to fit its 150 px instead of clipping; the small SAVE Primary is 150 wide",
        "12345 in the Secondary display font; Letter spacing is spaced out (0.5)",
        "separators: 1 px line (8 px above / below), the fancy line with its centre ornament, the gold-brown form line",
        "the long caption stays on one line (WrapMaxLines 1)",
        "the Close button sits at the bottom right (LayoutMode Right)"]))

    # ---- page 2: lists, well, rows, fields, panels (plain window)
    sh = page_shell(prefix + "2", 1200, 900, "Kit probe 2", kind="plain")
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
    sh.sets.append((P + "SetL", "Text", "Setting row"))
    pages.append(Probe(2, "base", sh, [
        "the page opens; the title bar has NO runes and NO ornaments (plain container)",
        "the list sits on a darker well (#000000(0.15), 4 px inset) with a slim scrollbar; rows: normal (hover lighter, click "
        "sound), selected (blue #4274a5), static (no hover); the first row shows its badge and a small EDIT button",
        "the property box: bold grey keys 150 wide, light blue values filling the rest, one line each",
        "two trade cards 10 px apart (5 px margin each), gold on hover; the second is covered dark (sold out)",
        "the three text fields: compare the typed text (kit white 16 / vanilla engine default / filter 13 px light blue) - tell "
        "the builder which matches the game; the value box stretches next to BROWSE",
        "option rows: the first tints on hover and is SILENT, the second has the selected frame; hover rows light up silently",
        "nav buttons: grey uppercase, hover light with a dark back; the selected one white bold on the dark back",
        "the setting row with ON (gold outline) / OFF; the flat bar is two thirds full",
        "the vertical separator between the columns starts 2 px above them (Top -2)"]))

    # ---- one page per UNVERIFIED feature
    def small(n, key, title, h, build, look, extra=(), w=900):
        s = _probe_shell(prefix, n, title, h, w)
        build(s, prefix + str(n))
        pages.append(Probe(n, key, s, look, extra))

    def b_checkbox(s, p):
        s.appends.append((s.body, checkbox(p + "C0", True, trial=t)))
        s.appends.append((s.body, checkbox(p + "C1", False, trial=t, anchor={"top": 8})))
        s.appends.append((s.body, checkbox_row(p + "Row", p + "RowL", p + "RowC", True, "Include entities", trial=t, anchor={"top": 12})))

    small(3, "checkbox", "Probe checkbox", 300, b_checkbox, [
        "the page opens", "two check boxes (checked / empty) in the vanilla frame; clicking toggles with the tick / untick sound",
        "the row: Include entities, 220 px label, then the box"])

    def b_number(s, p):
        s.appends.append((s.body, text_field(p + "Nb", p + "N", 200, number=True, trial=t)))

    small(4, "number-field", "Probe number field", 240, b_number, ["the page opens", "a number box in the input frame; typing "
                                                                   "letters is refused, digits work"])

    def b_tooltip(s, p):
        s.appends.append((s.body, button(p + "Tip", "Hover me", extra=tooltip("Sells for 20 coins", trial=t))))
        s.appends.append((s.body, label(p + "Tl", "Hover this label", "default", anchor={"top": 12}, extra=tooltip("A label tooltip", trial=t))))

    small(5, "tooltip", "Probe tooltip", 260, b_tooltip, ["the page opens", "hovering the button / label shows the vanilla "
                                                         "tooltip frame with the text", "Esc with a tooltip open closes the page "
                                                         "cleanly (no stuck tooltip)"])

    def b_progress(s, p):
        s.appends.append((s.body, progress(p + "Pr", value=0.6, trial=t)))
        s.sets.append((p + "Pr", "Value", 0.75))

    small(6, "progress-element", "Probe progress", 220, b_progress, ["the page opens", "a thin vanilla bar three quarters full "
                                                                    "(the b.set Value 0.75 float wins over the inline 0.6)"])

    def b_membar(s, p):
        s.appends.append((s.body, progress(p + "Mb", value=0.4, kind="memories", trial=t)))
        s.sets.append((p + "Mb", "Value", 0.5))
        s.sets.append((p + "MbTex", "Value", 0.5))

    small(7, "memories-bar", "Probe memories bar", 220, b_membar, ["the page opens", "the Memories bar: framed track, half filled, "
                                                                   "a glowing tip at the fill end"])

    def b_quality(s, p):
        s.appends.append((s.body, "Group #%sQs { Anchor: (Height: %d); LayoutMode: Left; }" % (p, SLOT_FRAME)))
        for i, q in enumerate(("Common", "Uncommon", "Rare", "Epic", "Legendary")):
            s.appends.append((p + "Qs", quality_frame(p + "Q" + str(i), q, icon_id=p + "Q" + str(i) + "I", trial=t, anchor={"right": 8})))
            s.sets.append((p + "Q" + str(i) + "I", "ItemId", "Weapon_Sword_Iron"))
        s.appends.append((s.body, tooltip_panel(p + "Tp", w=360, h=120, quality="Rare", trial=t, anchor={"top": 12})))
        s.appends.append((p + "Tp", label(p + "TpN", "Rare sword", "tipName", col=QUALITY["Rare"])))

    small(8, "quality-frame", "Probe quality frames", 340, b_quality, ["the page opens (the ../ItemQualities paths resolve)",
                                                                       "five swords on the Common / Uncommon / Rare / Epic / "
                                                                       "Legendary slot frames", "a Rare item tooltip frame with "
                                                                       "the name"])

    def b_itemslot(s, p):
        s.appends.append((s.body, item_slot(p + "Sb", p + "Sl", trial=t)))
        s.sets.append((p + "Sl", "ItemId", "Weapon_Sword_Iron"))

    small(9, "itemslot", "Probe item slot", 240, b_itemslot, ["the page opens", "the iron sword on its quality background in the "
                                                             "68 px border; no ItemStack sent"])

    def b_dropdown(s, p):
        s.appends.append((s.body, dropdown(p + "Dd", trial=t)))
        s.appends.append((s.body, dropdown(p + "Ds", search=True, trial=t, anchor={"top": 12})))

    small(10, "dropdown", "Probe dropdown", 260, b_dropdown, ["the page opens", "two dropdown boxes with the caret; clicking opens "
                                                             "the panel (no entries: the dim no-items line) with the tick sound; "
                                                             "the second has a search box"])

    def b_search(s, p):
        s.appends.append((s.body, search_field(p + "Sb", p + "Sf", 400, placeholder="search", trial=t)))

    small(11, "search-field", "Probe search field", 220, b_search, ["the page opens", "an input box with the magnifier on the left; "
                                                                   "typing shows the clear x on the right, clicking it empties the box"])

    def b_spinner(s, p):
        s.appends.append((s.body, spinner(p + "Sp", trial=t)))

    small(12, "spinner", "Probe spinner", 200, b_spinner, ["the page opens", "the loading spinner turns smoothly"])

    def b_tile(s, p):
        s.appends.append((s.body, "Group #%sTiles { Anchor: (Height: %d); LayoutMode: Left; }" % (p, TILE_H + TILE_GAP)))
        for i, st in enumerate(TILE_STATES):
            s.appends.append((p + "Tiles", tile(p + "T" + str(i), st.upper()[:8], st, trial=t)))

    small(13, "tile", "Probe tiles", 320, b_tile, ["the page opens", "four Memories tiles: default (lights on hover, click sound), "
                                                   "selected, complete, empty (dim, no click)"], w=900)

    def b_mask(s, p):
        s.appends.append((s.body, gradient_label(p + "G", "Gradient heading", trial=t)))
        s.appends.append((s.body, list_button(p + "Lb", "Nav selected", "selected", mask=True, trial=t)))

    small(14, "text-mask", "Probe text mask", 220, b_mask, ["the page opens", "the heading and the selected nav text fade with the "
                                                            "vanilla gradient"])

    def b_slotbg(s, p):
        s.appends.append((s.body, "ItemGrid #%sGrid { Anchor: (Width: 300, Height: 80); SlotsPerRow: 4; AreItemsDraggable: false; Style: %s; }"
                          % (p, item_grid_style(74, 64, 2, slot_bg=True, trial=t))))

    small(15, "slot-background", "Probe slot background", 240, b_slotbg, ["the page opens", "the empty grid shows the block selector "
                                                                          "slot backgrounds"])

    def b_disabled(s, p):
        s.appends.append((s.body, button(p + "D", "Disabled", disable_element=True, trial=t)))

    small(16, "disabled-prop", "Probe disabled", 200, b_disabled, ["the page opens", "the button shows the grey Disabled look by "
                                                                   "itself and does not click"])

    def b_ref(s, p):
        s.appends.append((s.body, button(p + "R", "By reference")))

    small(17, "value-ref", "Probe style reference", 200, b_ref, [
        "the page opens", "the button turns into the gold Primary (Value.ref Common.ui DefaultTextButtonStyle)"],
        extra=[java_ref_style(prefix + "17R", "DefaultTextButtonStyle", b="%B%", trial=t)])
    for pg in pages:
        pg.check()
    return pages


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
            print("  note: the kit's base look is not yet seen in game - open SUI.probe_pages() 1 and 2 before shipping a restyle")
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
