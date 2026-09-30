"""SkyyVault 0.1.5 - build script (javassist via jpype). COPY + EDIT of build_skyyvault_0.1.4.py (the live tools/deploy_set.py SET pin
since 2026-09-30 05:55; 0.1.4 was a copy of 0.1.3, itself a copy of the 0.1.2 script AS EDITED BY SKYY in commit ab75b6c). Vault has
no patch script: the next version copies this file.
Run:   python SkyyVault/build_skyyvault_0.1.5.py   -> SkyyVault/SkyyVault-0.1.5.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyVault/test_skyyvault_0.1.5.py   (bare-JVM harness, 0.1.4 and 0.1.5 side by side; commit-ready)

0.1.5 (2026-09-30) = THE ARROW CLICK. Skyy in game (0.1.4 live, page mode, verbatim): "arrow button works, but not when i click it, i
      have to set it back down". Research: research/Vault-Arrow-Click-Research.md (read it for the engine proof).
  WHY A PLAIN CLICK CANNOT TURN THE PAGE AT ONCE (engine fact, research sections 2-5): in a container window the CLIENT lifts the
    arrow onto the cursor by itself and tells the server nothing - none of the 139 client-to-server packets means "item lifted", the
    server has no cursor slot, and MoveItemStack names both ends of the move, so the client sends it only at the put-down. The server
    also cannot tell the client "this slot cannot be lifted": a slot on the wire is id / quantity / durability / quality / metadata
    only, and the only switch that stops lifting (ItemGrid AreItemsDraggable: false) is client markup of OUR custom pages, never of
    the vanilla chest grid. So "one plain click = page turns" (LOCKED 2026-09-25) is impossible for an arrow ITEM in the vault window;
    0.1.2's rule "the refused attempt is the click" already turns the page on the FIRST packet any gesture sends.
  WHAT 0.1.5 DOES (research ranks 2 = "do now"; everything else is 0.1.4 unchanged - byte-compared by the harness):
  - The instant gestures, now taught everywhere: SHIFT-CLICK an arrow (Transfer: SmartMoveItemStack, no destination, sent on the
    press) or hover it and press the DROP key (DropItemStack, sent on the press) turns the page at once; a PLAIN CLICK lifts the arrow
    on the client and the page turns when the arrow is put back / clicked down (the MoveItemStack at put-down - unchanged). A
    right-click (Take Half / Take One) is a client-side lift too, exactly like a plain click. In page mode the page's own < Prev /
    Next > buttons and page tabs were always one click (TextButton Activating); the page's help line now points at them first.
  - NEW VDropSys (EntityEventSystem on DropItemEvent$PlayerRequest, query Player; ONE registerSystem, in setup(), inside try/catch):
    the Drop key over a LIVE arrow / control slot of the player's OWN open vault window (current session, window registered in the
    player's WindowManager, the request's section id = that window's id) is noted exactly like the slot filter's refused REMOVE
    (VSession.noteHit -> the same one-batch VBtnTask -> the same btnBatch decision: restore row, re-send, sweep, one slot = a click)
    and the request is CANCELLED before the engine removes anything - so the engine's "<name> attempted to drop an empty ItemStack!"
    WARNING (0.1.4: one per Drop press, InventoryPacketHandler lambda$handle$4 offsets 151-185) is gone. shouldProcessEvent is
    overridden to true: a request that is ALREADY cancelled still turns the page - the engine itself pre-cancels every request when the
    game mode prevents item drops (GameModeTypes.preventsItemDrops, handler offsets 64-71; 0.1.4's Drop key then did NOTHING on such a
    server) and SkyyIslands GuardDrop cancels island visitors' drops; an arrow is a page button, never a drop, and nothing is ever
    un-cancelled. Every other request (any other window, a storage slot of the vault, the player's own inventory, a closed / retired
    session, arrows off) is left alone: the engine drops as in 0.1.4. If the system fails to register, the 0.1.4 path (the refused
    REMOVE in VBtnFilter) still turns the page on Drop (with the WARNING).
  - FIX (found by the 0.1.5 harness, in the click path since 0.1.2): VSessions.resync called the engine's PROTECTED Window.invalidate()
    from a class that is not a Window - an IllegalAccessError at run time, swallowed by its catch, so a click batch never re-sent the
    vault window itself. 0.1.4 still re-sent it whenever the batch rewrote a slot (a page turn, a row redraw: the engine's own container
    listener), but a batch that changed nothing (Take All over the arrow row on an empty page, a double hit, the gold arrow opening the
    confirm window) left the client's picture of a refused move uncorrected. NEW VWindow.resend() = its own invalidate(); resync calls
    it. The harness now scans the whole jar for engine members referenced without access (0.1.4: this one; 0.1.5: none; the other 22
    live Skyy jars: none).
  - Hint texts: the arrow tooltips (Prev / Next: "Shift-click to turn to page N of M at once." / "Your Drop key on it works too." /
    "A plain click lifts it - the page turns when you put it back."; gold Buy: "Shift-click to buy it at once." / "Shift-click - a
    window asks you to confirm." / "Shift-click to unlock it at once." + the Drop line + "A plain click lifts it - it buys / the window
    opens / it unlocks when you put it back."), the in-chest info item (+ "Arrows: shift-click one, or press your Drop key on it, to
    turn at once." / "A plain click lifts an arrow - the page turns when you put it back."), the chest-mode opening chat line, the vault
    page's help lines (page mode with arrow slots; the chest-mode /vault pages page when arrows are on), the /vault info help line (+
    " Shift-click one, or press Drop on it, to turn at once." after "The arrows in the vault window turn pages too.") and the three
    server.lang fallback descriptions. With pageArrows=false every text is 0.1.4's. First / Last page and the fillers are unchanged.
  - REVIEW FIXES (sonnet review 2026-09-30: PASS, low-severity text only): the /vault info line names the gestures too (it was the only
    text that did not); the chest-mode opening line is shorter ("...: shift-click an arrow (or press Drop on it) to turn pages at once,
    or click it twice. Esc saves. /vault <page> jumps." - about 165 characters instead of about 225, and no "in the bottom row", which
    was wrong with arrowLayout=inside); the gold arrow's server.lang fallback reads "Shift-click or press Drop: buys (or asks to
    confirm) the next vault page." (at or above buyConfirmCoins a window opens; a free page costs no coins). Not changed: every hint
    text states shift-click / Drop as instant - if in-game steps 3 / 4 fail (V1 / V2), revert that wording before wider use. Drop on
    the gold arrow buys a page below buyConfirmCoins even where the game mode prevents drops (0.1.4 did nothing there) - by design,
    the tooltip says so; a confirm for Drop-started buys can come later if Skyy wants one.
  - NOT BUILT (needs Skyy's OK - research section 7/10, OPEN-QUESTIONS "Do not add a second page-switch UI"): fix (e1) = the arrow row
    drawn by OUR page as a non-draggable ItemGrid bound to SlotClicking (a true one-click arrow, the SkyyMenu launcher pattern). NEW
    EVIDENCE for it (server + client log 2026-09-30 12:46 UTC, live config openMode=page): /vault was used twice in PAGE mode
    (openCustomPageWithWindows + VWindow; SkyySacks logged "craft link: windows=com.skyy.vault.VWindow" once per /vault and nothing else,
    so no Open-as-chest reopen) and Skyy's report is about the in-window arrow items - so the client most likely DOES draw the vault
    window's slots together with a custom page (probe P1 looks passed; where the page sits relative to the slots is still unknown).
  - Kept exactly: commands, permissions, config keys / rows / file text, the vault file format ("version" reads 0.1.5), vault.log,
    bridge keys, the buy path (buyConfirmCoins, BUY_GUARD_MS, the one-shot window), the profile busy / after-switch gates, saving,
    both pages' MARKUP (only b.set help texts change), the container window, VView, VBtnFilter (still refuses ADD / REMOVE / DROP on
    every control slot - the arrows never leave the row), the batch decision, the sweeps, the rescue, the asset items / quality / icons.
  CHECKED with SkyyVault/test_skyyvault_0.1.5.py (python SkyyVault/test_skyyvault_0.1.5.py) - 2026-09-30, kit skyyui 1.4 ac93356c4c60,
    pages 5ad38980408a: see the harness docstring for the sections. One JVM, -Xverify:all, 0.1.4 and 0.1.5 side by side. A 44 / 45
    classes load. B 36 classes byte-identical, CfgFn / CfgRows version-only, VStore = the version + infoLines (the one help text);
    VBtn.row, VaultPage.build, VSessions.open2 +
    resync (+ dropKey / dropEvent), VWindow (+ resend), SkyyVaultPlugin.setup changed exactly as pinned (string constants gone / new =
    the hint texts + the ready line; references new = the Drop-key registration, the arrows switch read, resend); VDropSys shaped as
    planned; setCancelled only with true; inaccessible engine calls 0.1.4 1 -> 0.1.5 0; server.lang 6 lines + manifest only. C 200
    page builds: every appended markup identical to 0.1.4's (so the proven look is unchanged), bindings / sel / offer / b.set order
    identical, the help lines exactly as planned per kind of page, every markup still the kit's. D the confirm window identical. E 220
    clicks identical (help lines as in C after each). F the widest help line 689 of 1006 px. G/H page id pinned, proofs pass. I 37
    gestures end to end on both jars (a real VSessions.open2, VView / VBtnFilter / VDropSys / VBtnTask / btnBatch / btnClick / swap,
    the engine's own container calls, a queued world task): put back / put down on an empty slot / on a stack / in the inventory /
    shift-click / Drop key / Drop key while drops are refused turn the page (0.1.4: the last does nothing), Prev, info, filler, Take
    All (no page action), storage moves / drops unaffected, stacks onto an arrow refused, other windows / players / a closed vault left
    alone, the gold arrow (cheap: buys once, a second press within the guard buys nothing; at buyConfirmCoins: the window), page
    mode, arrowLayout inside (incl. the full-vault blocked slot), busy / after-switch gates; no arrow outside the control row before,
    DURING or after any gesture, item counts equal before / after in every run, 0.1.4 = 0.1.5 except the planned Drop-key rows, the
    window re-sent after every click batch (0.1.4 left it unsent in 2 runs), the opening line and the tooltips as planned, the
    /vault info lines = 0.1.4's except the planned help-line tail (arrows on; arrows off: identical). J start
    twice on a scratch copy of the live Skyy_SkyyVault data: 3 stacks read, an open / close writes nothing, the second start reads
    and writes the same, 0.1.4 = 0.1.5. Mutation check (scratch jars): a filter that lets REMOVE through, a Drop request that is not
    cancelled, VView without its refused-move answer and the old resync each fail the harness (142 / 16 / 24 / 6 fails).
  UNVERIFIED (needs the game): V1 the client sends SmartMoveItemStack on the shift-click PRESS (expected: no destination to wait for);
    V2 the Drop key over a window slot sends DropItemStack at once and our cancel leaves the arrow drawn in its slot (the batch re-sends
    the window + inventory either way); V3 the new tooltip lines show on the arrows (per-stack ItemDisplayMetadata, as 0.1.2's did);
    V4 VDropSys is really called for window sections (bytecode: the event is invoked for every DropItemStack before getSectionById);
    V5 clicking outside the window while holding a lifted arrow sends a Drop from the arrow's slot (then it turns the page too).
  IN-GAME TEST (0.1.5; Skyy's live config is openMode=page):
    1 /vault: the page opens with the vault slots; read the three help lines under the tabs (they name < Prev / Next >, shift-click
      and the Drop key). Click Next > on the page once: the slots switch at once.
    2 In the vault slots, hover the Next arrow: its tooltip says "Shift-click to turn to page 2 of N at once." / "Your Drop key on it
      works too." / "A plain click lifts it - the page turns when you put it back." Hover the middle info item: 2 new lines.
    3 Shift-click the Next arrow: the page turns on the press, nothing sticks to the cursor, the arrow stays in place.
    4 Hover the Prev arrow and press your Drop key: the page turns, nothing is thrown, and the server log shows NO "attempted to drop an
      empty ItemStack!" warning.
    5 Plain-click an arrow (it lifts), then click the same slot again: the page turns and the arrow is back in its slot.
    6 Lift an arrow and click outside the vault window: the page should turn and the arrow come back (V5).
    7 Drop a stored stack from a vault slot with the Drop key: it is thrown as usual (only arrows are page buttons).
    8 Server Setup -> Vault -> Open /vault as: Chest window, then /vault: the chat line names shift-click / Drop; repeat 3-5 in the chest.
    9 On the last owned page (price below buyConfirmCoins): shift-click the gold arrow once - one page bought, the chest turns to it;
      at or above buyConfirmCoins the confirm window opens instead.
   10 /vault info: the last line ends "The arrows in the vault window turn pages too. Shift-click one, or press Drop on it, to turn
      at once."

0.1.4 (2026-09-29, the vanilla UI pass - Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them to look and
      feel vanilla"; HANDOFF section 2 rule 0; research/Vanilla-UI-Style-Guide.md sections 7 + 13; research/Skyy-UI-Inventory.md
      5.22). LOOK ONLY: the two custom pages change their markup, nothing else changes.
  - The build imports the shared kit tools/skyyui.py as SUI and calls SUI.verify() before anything else: every colour, font, texture
    and sound either page writes is proven against Assets.zip (read-only) at every build, and a game update that changes one stops
    the build. It REPLACES 0.1.3's own VANILLA_CHECK / VANILLA_FILES lists and the hand-copied DLG_* style strings. KIT_ID (kit
    version + file hash) and the page id (VAULT_PAGE_ID, a hash of the kit-made page code) are in the ready log line.
  - VaultPage (/vault in page mode, /vault pages, the Menu tile "Vault") - BEFORE: the old dark-blue panel (#SkyyVault 1040 x 640,
    a violet accent stripe, a 34 px violet title, blue / green / gold / grey custom button colours at 19 px, 17-26 px text, no
    textures, no sounds). AFTER: the PLAIN vanilla window (@Container: ContainerHeaderNoRunes title bar with VAULT in the 15 px
    Secondary title style, the ContainerPatch body, padding 17; the guide's frame for list pages), 1040 x 447 - the same width, the
    height is the sum of its parts (no FlexWeight filler; 0.1.3's root #SkyyVault is the body, so every 0.1.3 id is kept):
      * the profile hint line #SkyyVSub in the vanilla default label (16 px, #96a9be, centred);
      * a vanilla well (#SkyyVBox, #000000(0.15), padding 8) holding the kit pager #SkyyVNav (small Secondary "< Prev" / "Next >",
        the vanilla Disabled look at the ends - still bound, as 0.1.3's grey buttons were; Prev on page 1 / Next on the last page
        do nothing, as in 0.1.3 - around "Page n of m" in white bold), the page tabs #SkyyVNums (NORMAL tertiary tabs 90 x 44 with
        17 px labels, 5 apart, centred: the page on screen = Tertiary_Active, an owned page = Tertiary, a locked page = the
        Disabled look - the tab_row "tertiary" look of SkyyRanks / SkyySacks) and the slots line #SkyyVUsed (16 px bold);
      * the three help lines #SkyyVHelp0-2 (vanilla default label), the result line #SkyyVInfo (the kit status line: 16 px bold,
        two lines; + success #39f493, - error #ff6b6b, = the vanilla info blue #7caacc, none = label grey);
      * the vanilla footer (WorldEventPanelPage #Footer): the content separator, then #SkyyVAct = Open (Primary, 260) + Buy
        (Primary, 360) on the left and Close (Secondary + the vanilla cancel sound) on the right; Open / Buy show the Disabled look
        when unavailable (a locked page / all pages bought) and stay bound, as 0.1.3's grey buttons did. Every button has the
        vanilla hover / press / disabled textures and the ButtonsLight sounds.
      * the unreadable-file view (0.1.3 d == null): the same window, the red line #SkyyVErr (16 px bold, error red) on a well where
        the vault content would be, the separator and #SkyyVErrRow with Close in the same place as the vault view's Close.
      * every row is a plain LayoutMode Left row; a centred / right-aligned row gets its offset from its FIRST child's Anchor Left
        (the page tabs: the Java's centring pad on tab 1, 5 px on the others; Close: 834 in #SkyyVErrRow, 202 after Buy in
        #SkyyVAct), the way the kit pager centres Prev / page / Next - no kit 1.4 button_row(used= / left_margin=) Padding Left
        (probe page base4) and no LayoutMode Center / Right (vault_no_row_padding() asserts it on every state of both pages).
  - VBuyDlg (the "Buy page X for Y coins?" window) - BEFORE: 0.1.3's hand-copied PrefabEditorExitConfirm look (decorated window
    700 x 300, #ffcc00 30 px question, wrapped 16 px message, the 14 px purse note - #cc4444, the vanilla out-of-stock red, when
    short - Buy Primary + SaveSettings sounds, Cancel Secondary + ButtonsCancel sounds, centred). AFTER: the same window meant to
    look the same (same ids, sizes, colours, texts, sounds), now built from the kit (vault_dialog(): page_shell + label kinds +
    button kinds + a group row) instead of copied strings; the harness parses both windows and compares them property by property.
    The MARKUP SENT CHANGES in four ways (deployed-but-never-seen, so the window is UNVERIFIED again, like 0.1.3's V1): (1) both
    button styles carry the kit's full vanilla state set - ShrinkTextToFit / MinShrinkTextToFitFontSize 12 in every label style
    and a Disabled state nobody triggers; (2) the Buy / Cancel pair is centred by Buy's own Anchor Left 154 in a LayoutMode Left
    row instead of 0.1.3's LayoutMode Center (a "base" probe property; review fix: no kit 1.4 button_row Padding Left either);
    (3) the title label is nested inside the title bar Group's own append (the kit page_shell; deployed Bazaar / Auctions cells
    nest the same way); (4) the style keys come in the kit's order. 0.1.3's BTNP / BTNS fields are gone.
  - Kept exactly (asserted by SkyyVault/test_skyyvault_0.1.4.py): every element id of both pages (0.1.3's root #SkyyVault is the
    body; new ids: #SkyyVF / #SkyyVFBar / #SkyyVFTitle (frame), #SkyyVBox (well), #SkyyVErrBox), every b.set target and text in
    0.1.3's order (each after the append that creates its element), every event binding with its EventData ("a": prev / next /
    num:<n> / open / buy / close / dlgbuy / dlgno) in 0.1.3's order, the inline button labels (the page numbers, "Open page N" /
    "Open as chest", safe(buyTxt) exactly as 0.1.3 sends them), this.sel / this.offer, handleDataEvent / onDismiss / refreshWith /
    jsonStr / safe / the dialog's live / question / note (instruction-identical), page ids and lifetimes (CanDismiss), commands,
    aliases, permissions, config keys and rows, the vault file format (its "version" field now reads 0.1.4, as every version bump
    did; nothing reads it back), vault.log, bridge keys, buyConfirmCoins and the whole buy path (profile:busy, BUYING, the 1.5 s
    guard, the one-shot window), the container window, the in-chest arrow items, their per-slot filters and tooltips, the sweeps.
    VaultPage.style() is gone; VaultPage.colorOf / textOf are the kit's java_status_methods (same names and signatures; textOf
    gives 0.1.3's result for every input).
  - Uses only what deployed Skyy pages already use inline (SUI.assert_proven on every state of both pages) plus the kit's "base"
    look: LayoutMode Top / Left, fixed widths, Anchor margins, Padding (the frame body and the wells only), Wrap, the vanilla button
    / frame textures and inline Sounds; no FlexWeight, WrapMaxLines, LetterSpacing, LayoutMode Center / Right / Full, no kit 1.4
    builder (probe base4) and no UNVERIFIED (trial) kit element.
  - KIT-GAPs (composed from kit calls here, not added to the kit): (1) a TextButton whose label is a RUNTIME value of proven
    characters (page numbers, "Open page N", the Buy label): the kit refuses J() inside Text and ap.button() needs the UNVERIFIED
    b.set of a button's Text, so vault_rt_text() swaps the checked sample label of a kit button for the Java value (0.1.3 sent the
    same values inline) - every paged page restyle (Collections, Guilds, Islands, Exploration lists) will need the same; (2) a
    look picked at runtime among THREE markups (the page tab: on screen / owned / locked): choose() is binary and cannot nest, so
    the Java writes the ternary around three kit markups (a choose() over a list of (cond, markup) would fix it); (3)
    SUI.confirm_dialog cannot take the 30 px question, a runtime note colour or 0.1.3's 700 x 300 geometry and its button row is
    LayoutMode Center, so the window is composed from page_shell / label / group / button (+ color_by for the note colour); (4)
    pager() passes no label options (the caption is the "strong" kind: 16 px white bold) and no button size (Prev / Next stay
    small 32 px next to the normal 44 px page tabs); (5) no split-footer block (actions left, Close right: the WorldEventPanelPage
    #Footer shape) - close_left = W - Open - gap - Buy - BTN_MIN_W is computed here and asserted with used_width; (6) no base-only
    centred / right-aligned row: button_row(used= / left_margin=) centres with Padding Left (probe base4), so the offset is put on
    the first child's Anchor Left here, the pager's way; (7) assert_proven / the proof tables do not track a child element nested
    inside one appendInline string (the dialog's title label inside the title bar Group) - fine (deployed Bazaar / Auctions cells
    do it) but undocumented.
  CHECKED with SkyyVault/test_skyyvault_0.1.4.py (committed; re-run it: python SkyyVault/test_skyyvault_0.1.4.py) - 2026-09-29, kit
    skyyui 1.4 ac93356c4c60, pages 80f113b82aa1; 19699 ok, 0 fail. One JVM with -Xverify:all, HytaleServer.jar, 0.1.3 and 0.1.4 each
    in its own class loader: A all 44 classes of both jars load, verify and initialise. B 38 classes byte-identical; VStore and the
    config kit's CfgRows / CfgFn differ only by the embedded version string; SkyyVaultPlugin = 0.1.3's bytes once its ready-log
    constant is swapped back; VaultPage: the same fields, 7 methods instruction-identical (constructor, safe, jsonStr, refreshWith,
    refresh, handleDataEvent, onDismiss), changed build / colorOf / textOf (same signatures), style gone; VBuyDlg: BTNP / BTNS gone,
    6 methods instruction-identical (constructor, live, question, note, handleDataEvent, onDismiss), changed build. C 17 vault
    states x 5 result lines = 85 builds per jar: identical b.set lines in the same order, identical 1160 event bindings (type, id,
    EventData, lock, order), identical inline button labels, identical sel / offer, no 0.1.3 id missing; all 2400 appended 0.1.4
    markups equal the kit's markup (J() slots filled) and pass check_markup, 85 check_page, kit colours only, the body filled
    exactly in every state, the page tabs centred in the well by the first tab's Anchor Left, no Left row with a Padding; the
    result line green 16 / red 16 / info blue 16 / grey 32 by its mark; review fix: the LOOK of every stateful button asserted per
    state in C + E (tabs on screen 148 / owned 418 / locked 869, Open live 99 / greyed 49, Buy live 128 / greyed 20, Prev live
    98 / greyed 50, Next live 128 / greyed 20) and every b.set after its append (1080 lines in C + E). D the confirm window in 6
    states x 2 jars: identical texts (same order, after their appends) and bindings, 72 elements the same property by property (the invisible
    differences above aside), the note red when the purse is short, Buy / Unlock by the price. E 5 page states x 17 clicks + 4
    window click sequences on both jars: identical result line, selection, offer, purse, owned pages, vault file and vault.log
    after every click (2 page purchases from the page, 2 from the window, the 1.5 s guard, a dear page asking for the window, a
    poor purse, an unreadable file). F text fit on the client's NunitoSans tables: every button label fits (widest BUY PAGE 21 -
    500K COINS 230 of 312 px; page tabs 20 of 42 px, "1000" = 41 of 42 at the maxPages cap), every seen one-line text fits its
    box, every result fits the two-line line. G the page id in the jar's ready line = the kit's pages now = VAULT_PAGE_CHECKED.
    H assert_proven + check_page on both page states and the window on the current kit. The new look assertions were checked to
    bite: a scratch build with owned / locked tabs swapped, Open inverted and #SkyyVSub.Text set before its append failed 1606
    checks in C / E (the old harness passed all three).
    Also: python tools/ci/lint.py 0 fails / 0 warnings (404 files); python tools/skyyui_test.py --dir <scratch> 10061 ok, 0 fail.
    A rebuild is ENTRY-identical (every jar entry's bytes the same; the zip member timestamps carry the build time, so the jar's
    sha256 differs - compare entries, not the file hash).
  UNVERIFIED (needs the game): the whole look - the kit's "base" look has not been seen in game yet (probe pages base1 / base2 /
    base3: plain + decorated frame, button textures / inline Sounds / the Disabled look / ShrinkTextToFit, the well, the tertiary
    tabs). Neither page has a runtime fallback: a parse error disconnects on /vault, the Menu tile and every buy at or above
    buyConfirmCoins (every default page price: page 3 = 50,000 = the default threshold). DEPLOY GATE: keep tools/deploy_set.py
    SET at ("SkyyVault", "0.1.3") until Skyy has opened probe pages base1 / base2 / base3 cleanly (the build prints the gate while
    "base" is not in skyyui.PROBED; review fix: probe base4 is no longer needed). V1 (0.1.3: the confirm window draws in the
    vanilla look) is still open and now covers both pages; V2-V5 and U1-U7 below are unchanged. NEW: the page is 447 px high
    instead of 640 - in page mode (openCustomPageWithWindows) whether the client draws the vault slots NEXT to the page or under
    it was already UNVERIFIED in 0.1.3 (hence the hint "Vault slots not showing next to this page? Click Open as chest."); the
    smaller page changes where it sits relative to the slot window. A Buy label with a dot (a non-default price such as 12,500 ->
    "12.5k") is sent inline exactly as 0.1.3 sent it (not a kit-proven character).
  IN-GAME TEST (after probe pages base1 / base2 / base3; each step names what to look for):
    1 the confirm window FIRST, on its own: with a fresh vault (2 pages) and the default buyConfirmCoins 50,000, type /vault buy in
      the world - the "Buy page 3 for 50,000 coins?" window opens (decorated frame, gold question, grey message, purse note - red
      "not enough" when short), Buy and Cancel side by side and centred under the text; Cancel closes it, nothing charged. If it
      disconnects, the window alone needs a fix (the vault page is a separate test).
    2 /vault (page mode): the VAULT window opens; check that the vault slots are visible and NOT covered by the 447 px page (next
      to it, or wherever the client puts the slot window), and that the hint "Vault slots not showing next to this page? Click
      Open as chest." still makes sense; page 1 tab gold-outlined, Prev greyed, locked tabs greyed, the tabs big enough to read
      and click.
    3 click tab 2 / Next / Prev: the slots switch, the tab and "Page n of m" follow, the result line green.
    4 Prev on page 1, and Next on the last page (click tab 10, or your highest page, then Next): nothing happens - the page, the
      tabs and the result line stay as they were, no new line and no error.
    5 click a locked tab: the blue "=" line, the slots line says the price.
    6 Open as chest: the plain chest opens.
    7 Buy below buyConfirmCoins (set it to 100,000 in Server Setup -> Vault): one page bought, green line.
    8 Buy at or above it (back to 50,000): the confirm window -> Cancel returns to the vault page, Buy buys once and returns on the
      new page.
    9 with openMode chest: /vault pages shows the same window without slots, Open page N opens the chest.
    10 all pages bought: Buy greyed "ALL PAGES BOUGHT", a click says so in red.
    11 Close and Esc close the page (the vault saves).
    12 an unreadable vault file (admin test copy): the red line on the well + Close at the bottom right.

0.1.3 = BUY CONFIRM WINDOW (LOCKED Skyy 2026-09-25, OPEN-QUESTIONS "Vault arrows", research/Vault-Arrows-Spec.md section 1).
  Everything else is 0.1.2 unchanged (files, keys, data format, commands, arrows, sweeps); a 0.1.2 vault / config file loads as is.
  * ONE RULE for the gold arrow in the vault window, the page's Buy button and /vault buy (VStore.intent): a page price BELOW
    buyConfirmCoins (Server Setup row, default 50,000, VCfg.BUY_CONFIRM) buys at once; AT or ABOVE it the confirm window asks
    "Buy page X for Y coins?" (Buy / Cancel) and nothing is charged until Buy. With the locked prices (page 3 = 50,000, +25,000) every
    bought page asks. The 0.1.2 10 s second click (VStore.CONFIRM / buyKey / confirm / armed / disarm, VCfg.CONFIRM_MS) is gone.
  * VBuyDlg = our own INLINE page in the VANILLA LOOK (HANDOFF section 2 rules 0 + 2; no .ui file): a copy of the game's confirm page
    Pages/PrefabEditorExitConfirm (Assets.zip Common/UI/Custom/) - @DecoratedContainer frame (ContainerHeader title bar + decorations,
    ContainerPatch body, 20 px padding), #ffcc00 question, @DefaultLabelStyle message, a purse note (red when short), a centred row
    with the vanilla Primary button (Buy, SaveSettings sounds) and Secondary button (Cancel, ButtonsCancel sounds). Every copied value
    is proven against Assets.zip at build time (VANILLA_CHECK: 32 values, 13 textures / sounds); the jar check refuses any .ui file.
  * WHERE IT RETURNS (VBuyDlg.ret): the vault view on screen is RETIRED first (DENY_ALL + synced + closed - no late move can land in
    it), the window opens, then the old vault window is closed. Buy / Cancel then REPLACE the window (never close-then-open) with:
    page mode -> the vault page + slots (result on its info line); chest mode -> the vault chest again, on the NEW page after a buy
    (Skyy: "afterwards return to the vault on the new page"), on the page shown before after Cancel / a refused buy; /vault pages
    (chest mode) -> that page; nothing open (/vault buy from the world) -> the window just closes. Esc = nothing bought (chat line),
    the vault stays closed (a page opened from onDismiss would be wiped by the engine right after it). A second window never stacks:
    a click / /vault buy while one is open for that page says "Confirm or cancel the purchase in the window on your screen." The
    return page is always an OWNED page (a locked page that was selected on the vault page returns to the last owned page).
  * NEVER CHARGED TWICE: VStore.buyAt(u, name, expected page, shown price) buys only the page the click / window / command offered
    (a stale window finds it "already yours"; a later page never skips one); one purchase at a time per player (BUYING); the window is
    one-shot (done: a double click on Buy, Buy then Cancel, or Esc then Buy act once) and page events of a replaced page are dropped by
    the engine until the client acknowledges the new one; an admin price change while the window is open charges nothing (the player
    never pays a price the window did not name); BUY_GUARD_MS 1.5 s after a purchase every buy CLICK or COMMAND of that player is
    refused ("You just bought vault page N - nothing more was charged"): a double click or a shift-click arriving as two packets on the
    gold arrow buys one page, and window Buy + /vault buy never buy two. The gold arrow tooltip says which way it goes ("Click to buy
    it." / "Click - a window asks you to confirm.").
  * PLAIN CLICK = SHIFT-CLICK (LOCKED Skyy 2026-09-25): unchanged from 0.1.2 by design - the page turns (or the buy / window starts)
    on the FIRST packet any gesture on an arrow sends (the refused REMOVE is the click; one batch, one action). A plain click reaches
    the server when the client sends its move (MoveItemStack at put-down / drag / drop key); Hytale has no server-side cursor
    (spec E6: no packet exists for a lift that is only drawn on the client), so nothing earlier can be heard. In-game check: U2 below.
  * LOCKS KEPT: in-chest Prev / Next arrows stay the only page-switch UI added (the confirm window switches no pages); 2 free pages,
    max 10, page 3 = 50,000, +25,000 per page, pages shared across profiles; config kit KEEP = 10 old versions (LOCKED, was 20).
  0.1.3 CHECKED in a bare JVM (scratch harness under tools/dev/scratch/r9-vault/, deleted afterwards; an empty asset map stood in for
  the item store, a coins:fn:take / add / get stub for SkyyCoins; 59 checks, 0 fails): 44 classes load + link under -Xverify:all;
  defaults 2 / 10 / 50,000 / +25,000 / buyConfirmCoins 50,000, price table 0 0 50k 75k ... 225k, needsConfirm at 50,000 yes, 49,999
  no; AT the threshold /vault buy, the gold arrow and the page Buy button only open the window (0 coins taken); window Buy = one
  purchase (coins once, file 3 pages), Buy again / Cancel after Buy / Esc then Buy / Cancel then Buy ignored; window Buy then
  /vault buy or a gold-arrow click within 1.5 s refused; a stale window for an owned page and a window for a later page charge
  nothing; a price change while the window is open charges nothing; purchase already running, not enough coins, no SkyyCoins and
  profile:busy refuse without a charge; BELOW the threshold /vault buy buys at once, a second /vault buy or gold-arrow click right
  after is refused, after the guard the next page is a new purchase, a stale page Buy (offer) charges nothing; in a real 45-slot
  chest view the gold arrow tooltip follows the threshold, one click below it buys page 3 and turns the chest to page 3, a second
  click event buys nothing, Prev / Next turn at once; the window's inline document: 12 elements, balanced, unique ids without
  underscores, root anchor Width / Height only, vanilla frame / buttons / #ffcc00 / sounds, question set via Text, purse note warns,
  2 bindings (dlgbuy / dlgno), the free-page variant "Unlock page 3 for free?"; the vault page Buy button "Buy page 7 - 150k coins"
  (offer 7, no "Sure?"), at the threshold no charge on the click, below it one page for a double click; kit: 12 rows incl.
  buyConfirmCoins, KEEP 10, set 75,000 -> field + file (page 3 then buys at once), -5 refused, a player without skyyvault.admin
  denied, VCfg.load reads it back; 6 purchases = 6 vault.log BUY lines = 6 coin takes, 0 refunds.
  NOT checkable in a bare JVM (needs a player): the window opening over the chest / page (askBuy: retire, openCustomPage, closeWindow)
  and returning (dlgBack: open2 with the chest or the page), btnBatch deciding a click, the look of the window on a real client.
  0.1.3 UNVERIFIED (needs Skyy in game): V1 the window draws in the vanilla look (frame textures, Primary / Secondary buttons, sounds,
  FontName Secondary) - the inline texture / sound paths are the ones SkyySacks 0.7.7, HyUI and Clay Factoria use, not yet seen on
  Skyy's client; V2 chest mode: gold arrow -> window -> Buy -> the chest is back on the NEW page, no second (stale) chest window
  beside it; Cancel -> back on the old page; V3 page mode: the vault page + slots come back with the result on the info line; V4 the
  old vault window closing right after the window opened (CloseWindow while our page is up) does not close the window itself; V5 Esc
  on the window leaves nothing open and says "Nothing was bought."; U2 (0.1.2) whether a plain click reaches the server before the
  put-down.
  0.1.3 REVIEW FIXES (same version, rebuilt; bare-JVM harness under tools/dev/scratch/fx-vault/, deleted afterwards; 48 checks, 0
  fails: the buy-path checks above re-run on the real jar + dlgBack / askBuy / cmdBuy run with the engine calls stubbed):
    F1 VSessions.dlgBack clamps the return page to an owned page (1..unlocked) before anything opens: /vault buy while the vault
       page had a LOCKED page selected stored back = that page (cmdBuy, VaultPage branch), so Cancel tried open2 on a locked page and
       showed a red "Vault page N is locked" line instead of returning to the vault.
    F2 VBuyDlg remembers its world (wu) and open time (at); VBuyDlg.live(world now) = not acted, same world, under STALE_MS (2 min).
       cmdBuy and askBuy only treat a LIVE window for that page as "on your screen"; a dead one (kept by the page manager after a
       world switch, or simply old) is marked done and a fresh window opens (cmdBuy then returns nowhere: ret 0). cmdBuy's check also
       ignored done before (a done window for the same page blocked /vault buy).
    F3 the 0.1.2 notes below are marked HISTORICAL (their "10 s second click" is 0.1.2 behaviour, gone in 0.1.3).

0.1.2 notes (HISTORICAL - how 0.1.2 behaved; kept for reference. Where they differ, the 0.1.3 notes above win: the 10 s second click
and CONFIRM_MS are gone in 0.1.3):

0.1.2 = WYNNCRAFT-STYLE PAGE ARROWS INSIDE THE VAULT WINDOW (spec: research/Vault-Arrows-Spec.md Part A; Skyy 2026-09-25: "if possible
  could you add arrows in the chest to switch between vaults like wynncraft so i dont have to go back to select vault 2").
  Design lock kept: no custom UI on the vanilla inventory screen - the arrows are ITEMS inside OUR container, not buttons.
  Everything else is 0.1.1 unchanged (files, keys, data format, commands, config rows); pageArrows=false gives the 0.1.1 container.
  * LAYOUT (captured per window at newSession; a config change applies to windows opened afterwards):
      arrowLayout=row (default): capacity R + 9 (R = storage size S rounded up to a multiple of 9): all S storage slots stay usable,
        padding S..R-1 + the control row R..R+8 = [Prev|First page][3 fillers][page info][3 fillers][Next|gold Buy|Last page].
        Default S=36: 45 slots, Prev 36, info 40, Next 44.
      arrowLayout=inside (Wynncraft-exact): capacity S, Prev = first slot of the last row, Next = last slot (27 / 35 at S=36). Before a
        page is shown VData.clearReserved moves an item stored there to the first free slot of that page, then of any owned page
        (vault.log RESERVED-MOVE + chat), counted before and after (undone if the count differs). Whole vault full: the item stays,
        that page shows it instead of the arrow and the slot is normal storage (the filter lets it through).
  * NO LEAKS: VBtnFilter (SlotFilter, one per window) is registered for ADD, REMOVE and DROP on every non-storage index. It touches no
    container and always refuses, so the engine refuses the move BEFORE anything moves (the arrow never leaves its slot). A refused
    REMOVE is the click: it sets a hit bit and queues ONE VBtnTask per batch on the viewer's world thread. The task puts the canonical
    row back (a real item found in a control slot is rescued, never cleared: free vault slot -> inventory -> any owned page ->
    thrown at the feet), removes stray buttons from storage, re-sends the window (Window.invalidate) and ALL six inventory sections
    (InventoryComponent.markDirty: the engine only re-sends dirty sections), sweeps the viewer, then decides: exactly one distinct
    control slot hit and no storage change in the batch = a click; Take All / Sort / merge-stack always touch 2+ slots (the row
    always holds 2+ button items) = no page action; a storage change in the 100 ms before the first hit also counts as a storage
    change (review R4). Control items never enter VData (syncView copies storage indices only, a button
    in storage is saved as empty and removed), a Skyy_Vault_* stack in a vault file is dropped at load (vault.log STRAY-FILE), so a
    rollback to 0.1.1 is safe.
  * CLICK: Prev / Next = gate (profile busy / after-switch wait) + the existing swap (sync old page, fill new, read back, close
    noSync on a mismatch), which now also rebuilds the control row; page mode also refreshes our page. Gold Buy in 0.1.2 = the SAME 10 s
    confirm as the page's Buy button and /vault buy (VStore.buyKey / confirm / buy): first click arms (chat), a click in a LATER batch
    within 10 s buys (coins once) and the new page opens in place. LOCKED Skyy 2026-09-25 replaces that two-click with buyConfirmCoins
    (default 50000, VCfg.BUY_CONFIRM): below the threshold buy at once, at or above it a dialog asks "Buy page X for Y coins?". The
    0.1.2 build still used the 10 s second click and did not read the row (HISTORICAL - 0.1.3 reads it, see above). First page / Last page / page info / fillers: a chat line or
    nothing. The slot's action follows the CURRENT vault state (a row made stale by /vault buy or a freePages raise acts right and is
    redrawn). /vault buy and the page's buttons redraw an open row.
  * SAFETY SWEEP (VSweepTask, world thread; no events, no ECS systems - still none registered): on join (the 1 s ticker's online set),
    after every vault close, every straySweepSeconds (30) and after every click batch: every Skyy_Vault_* stack in the player's six
    inventory sections and open windows (their own vault window: storage indices only) is removed (vault.log STRAY + one WARN per
    sweep). Skipped while profile:busy:<uuid> is set (PROFILES-CONTRACT rule 5).
  * BUTTON ITEMS (the first Skyy mod with its own PNGs): Skyy_Vault_Prev / PrevOff / Next / NextOff / Buy / Info / Filler at
    Server/Item/Items/Utility/ - MaxStack 1, no Categories, Recipe, Interactions, BlockType or item-type block, vanilla map-scroll
    model; own quality Server/Item/Qualities/SkyyVaultButton.json (Technical textures, SlotTool frame, HideFromSearch, no drop
    sparkle); 64x64 RGBA icons drawn by this script (pure-Python PNG writer) at Common/Icons/ItemsGenerated/; server.lang names.
    Each stack carries its own tooltip (ItemDisplayMetadata, the SkyyRolls / SimpleEnchantments method) and a SkyyVaultBtn marker
    {k: kind, o: owner, s: window serial}. The manifest now sets IncludesAssetPack TRUE (0.1.1 set it false: it shipped no assets).
  * CONFIG (kit tools/skyycfg.py, 3 new rows -> 11): pageArrows bool true (new), arrowLayout choice row|inside (new,danger: asks,
    inside moves items), straySweepSeconds int 30 s 5-600 (live,adv, field VCfg.SWEEP_MS*1000).
  * Chest-mode opening line: "...the arrows in the bottom row turn pages, Esc saves. /vault <page> jumps." (0.1.1 line when off).
    Page-mode label and /vault info count usable slots (S - 2 with arrowLayout=inside).
  0.1.2 UNVERIFIED (needs Skyy in game): U1 a 45-slot chest drawn as 5 rows that fits the screen with the inventory (fallback:
  arrowLayout=inside); U2 which gesture reaches the server first (plain click may only lift the arrow on the client - the page then
  turns on put-down / drag; shift-click and the drop key turn it at once); U3 the refused pick-up snapping back cleanly; U4 the
  per-stack tooltip on items in a container slot; U5 HideFromSearch keeping the items out of the creative library; U6 our PNG icons
  loading from the jar; U7 Take All / Sort on the arrow row by eye.
  * ENGINE FINDING (this build pass, HytaleServer.jar bytecode + bare JVM; not in the spec): the whole-slot move primitive behind
    shift-click and Take All (ItemContainer.internal_moveItemStackFromSlot(slot, [qty,] to, ...)) returns NULL when the slot refuses
    removal and the wrapper then NPEs ("Failed to run task!" SEVERE; Take All stopped at the first arrow, so with empty storage it
    looked like a click on Prev). Windows with arrows therefore use VView (a SimpleItemContainer subclass) that answers such a refused
    move with the engine's own failed MoveTransaction; the filter still sees every attempt. Drag / put down and the drop key already
    return a failed transaction (the drop key then logs the engine's WARNING "<name> attempted to drop an empty ItemStack!" - nothing
    is thrown). Review fix: the /vaultadmin open copy and every session view (also pageArrows=false, so a retired DENY_ALL view) are
    VViews too, so no vault container NPEs on shift-click / Take All any more (0.1.1 did, under DENY_ALL).
  0.1.2 REVIEW FIXES (same version, rebuilt; 24 more bare-JVM checks, 0 fails, 43 classes under -Xverify:all):
    R1 adminView builds a VView (was a plain SimpleItemContainer + DENY_ALL: engine NPE on an admin's shift-click / Take All);
       newSession always builds a VView (identical for every allowed move).
    R2 rescue: a storage write that does not read back is undone before the next candidate slot (RESCUE-PARTIAL + stop if the undo
       fails), so a rescued stack can never be placed twice.
    R3 rescue returns whether the control slot is empty; restoreCtrl never overwrites a slot that still holds the real stack (the
       recount then fails and the view closes), and finalizeWorld's new keepCtrl moves a real stack still in a live control slot to
       the first free vault slot (else thrown at the feet, else RESCUE-LOST) before the view is emptied. Engine note: with filter=false
       removeItemStackFromSlot / setItemStackForSlot always succeed (bytecode), so R2 / R3 are defence in depth.
    R4 a storage change in the last 100 ms BEFORE a batch's first hit also marks the batch changed (VSession.lastChg / recentChg):
       the engine's bulk moves walk slots in index order inside one server call, so with arrowLayout=inside and one live arrow a
       Take All that filled the inventory before reaching the arrow (or a merge-stack) looked like a single click and turned the page.
  0.1.2 CHECKED in a bare JVM (scratch harness under tools/dev/scratch/vault/, deleted afterwards; an empty-asset-map stub stood in
  for the server's item store; 98 checks, 0 fails): 43 classes load under -Xverify:all; row layout 45 slots, page 1 row = PrevOff,
  3 fillers, Info, 3 fillers, Next; the arrow refuses slot-to-slot moves (to another container, onto a stored stack, a swap), the
  drop path (no output, nothing thrown) and the shift-click / whole-stack paths (no exception), each with ONE hit bit; ADD onto an
  arrow / the info item refused without a hit; sort keeps storage in 0-35 with 9 hits; a Take All loop empties storage, 9 hits,
  arrows stay; merge-stack pulls only real stacks (9 hits); a button in storage is saved as empty; restoreCtrl puts a wrong button
  back, removes a stray and rescues a real stack from a control slot into storage (count equal); swap 1->2->3->1 keeps every page;
  page 3 of 3 shows gold Buy, max pages grey Last page; refreshRow turns a stale Buy into Next; clicks: Next / Prev flip in place,
  First page / info / filler do nothing, the switch gate refuses; buy: first click arms, no SkyyCoins = nothing, a click in a later
  batch buys once (coins taken once) and page 4 opens in place; inside layout: stacks at 27 / 35 move to the first free slots
  (total equal), usable 34, sort + Take All + put all keep both arrows, a full vault keeps the stacks (filter allows the slot), a
  freed slot gets its arrow back; pageArrows=false = capacity 36, no buttons; fromDoc drops Skyy_Vault_* stacks and orphans
  (STRAY-FILE); the kit publishes 11 rows, straySweepSeconds 20 -> SWEEP_MS 20000 (3 refused), arrowLayout asks confirm, then
  inside, pageArrows off, the file lines are rewritten in place with the comments kept and VCfg.load reads them back; the jar holds
  7 item JSONs, the quality, 7 valid 64x64 RGBA PNGs and server.lang; manifest IncludesAssetPack true.
  NOT checkable in a bare JVM (needs a player): btnBatch (the world check, restore + re-send + sweep + decide), the sweeps (join,
  close, periodic, click) and the rescue steps 2-4.

0.1.1 notes (unchanged below):

0.1.1 = ADMIN CONFIG ADOPTION (research/Server-Setup-Spec.md 4.3 + section 7; kit tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md).
  Everything else is 0.1 unchanged: same files, keys, data format, commands and default behaviour until an admin changes a value.
  config:def:SkyyVault + config:fn:SkyyVault (+ config:epoch:SkyyVault) are published at the END of setup(), after VCfg.load(), so
  SkyyMenu 0.3 (SkyWynn Menu -> Server Setup, /modconfig) lists "Vault" with these rows (category vault, file
  Skyy_SkyyVault/config.properties, admin node skyyvault.admin - the node /vaultadmin already requires):
    key                 type    default  range        unit   flags              binding
    freePages           int     2        1-100        -      live,danger        field:VCfg.FREE_PAGES   check: <= maxPages; after: cached
                                                                                vaults get the new free pages now (in memory, like a fresh load)
    maxPages            int     10       1-1000       -      live,danger        field:VCfg.MAX_PAGES    check: >= freePages and never below
                                                                                a page that still holds items in any vault (the /vaultadmin
                                                                                setpages rule); only lowering scans the vault files
    slotsPerPage        int     36       9-90         -      new,danger         field:VCfg.SLOTS        (vaults loaded afterwards)
    pagePrice           int     50000    0-1e12       coins  live               field:VCfg.PRICE
    pagePriceStep       int     25000    0-1e12       coins  live               field:VCfg.STEP
    buyConfirmCoins     int     50000    0-1e12       coins  live               field:VCfg.BUY_CONFIRM
                                                                                LOCKED Skyy 2026-09-25. Below: buy at once. At or above:
                                                                                dialog "Buy page X for Y coins?". 0.1.2 does not read it.
    openMode            choice  page     page|chest   -      live               field:VCfg.OPEN_MODE (new String twin of PAGE_MODE; the
                                                                                after= hook and VCfg.load keep PAGE_MODE in step)
    afterSwitchSeconds  int     30       0-120        s      live,adv           field:VCfg.AFTER_SWITCH_MS*1000 (the field stores ms: typing
                                                                                20 puts 20000 in the field, the file keeps afterSwitchSeconds=20)
    saveDelayMillis     int     1000     100-30000    ms     live,adv           field:VCfg.SAVE_DELAY_MS (no scale)
  Flags = spec 4.3 exactly. afterSwitchSeconds / saveDelayMillis have NO confirm step (spec: L, A); their help text warns that lowering
  the wait / raising the delay widens the crash dupe/loss window. Proposal for Skyy (not built): danger + confirm=down / confirm=up there.
  maxPages check without a world-thread stall: the saved-vault part comes from a background scan (VScan, daemon thread
  "SkyyVault-scan", parse cache by modified time + size) no older than 2 min; without one, the check scans inline only while that fits
  in 40 ms, else it starts the background scan and answers "try again in a few seconds" (nothing changed). Loaded vaults: from memory.
  RELOAD = VHooks.reloadCfg (VCfg.load + the freePages raise): run by the kit after a hand edit of config.properties is noticed.
  Admin commands: /vaultadmin reload now goes through the kit's reload op (hand edits are logged via=file in config-changes.log and
  versioned); NEW /vaultadmin config lists every row, /vaultadmin config <key> <value> sets one through the kit (via=command, logged,
  versioned; the chat path for owners without SkyyMenu). /vaultadmin setpages is per-player data, not config: vault.log as before.
  Player Settings (research/Settings-Spec.md): none. The vault sends only replies to the player's own clicks/commands and the
  "your vault closed because your profile changed" safety notice (Settings-Spec 2.3: data-safety lines are never switchable).

NEW MOD (HANDOFF 2026-09-24 20:10 BETA BACKLOG item 5). Skyy: "a /vault that works like the ender chests in the bank in Wynncraft -
a chest you can open from ANY profile for saving and transferring items between profiles."
The vault is per PLAYER (keyed by the player UUID, never by the profile key pkey(uuid)): every profile of a player opens the same
vault, so it is how items move between profiles (tools/PROFILES-CONTRACT.md rule 6: per-player data unless noted). Zero hard
dependencies: coins come from SkyyCoins only through the JVM bridge (coins:fn:take / coins:fn:add); without SkyyCoins the free pages
work and buying says coins are missing. SkyyProfiles is read only through profile:busy:<uuid> and profile:epoch:<uuid>.

WHAT THE PLAYER SEES
  /vault            openMode=page (default): OUR vault page (inline, rebuilt only after a click) opened TOGETHER with a container
                    window of vault page 1 (PageManager.openCustomPageWithWindows + a ContainerWindow subclass - the SkyySacks /pd
                    pattern). The page: title, "Page 2 of 4", < Prev / Next >, a row of page-number buttons (current green, owned
                    blue, locked grey), "Page 2 - 14 of 36 slots used", Open as chest, Buy page N - <price> coins (0.1.3: below
                    buyConfirmCoins it buys at once, at or above it the confirm window asks first), Close, three help lines and a
                    result line. Prev / Next / a number swap the vault slots
                    in place (no window churn). "Open as chest" opens the same vault page in the VANILLA chest window (Page.Bench +
                    ContainerWindow - the proven vanilla /invsee, chest and TerrariaAddons pattern) - the fallback in case the
                    client does not draw window slots next to a custom page (UNVERIFIED, see below).
                    openMode=chest: /vault opens the vanilla chest window at once; /vault pages opens the page with the buttons,
                    whose Open button opens the selected page as a chest.
  /vault <page>     the same, on that page (usage variant, one required arg; the engine picks subcommands by name first).
  /vault next | prev    the next / previous page (swaps in place when the vault is already showing, else opens it).
  /vault pages      the page with the buttons (openMode=chest) - in page mode it is the same as /vault.
  /vault buy        buy the next page. /vault info  pages, slots used per page, next price.
                    LOCKED Skyy 2026-09-25 (built in 0.1.3): no 10 s second click. buyConfirmCoins (default 50000): a cheaper page
                    buys at once; this price or more asks "Buy page X for Y coins?" in a confirm window (Buy / Cancel). The gold
                    arrow, the page's Buy button and /vault buy share that ONE rule (VStore.intent). (0.1.2 armed a 10 s second
                    click, VStore.CONFIRM - gone.)
  Vault pages: freePages (2) free, more bought with coins up to maxPages (10): page N costs
  pagePrice + pagePriceStep x (N - freePages - 1) = 50k, 75k, 100k, ... (config). 36 slots per page (a large chest; config).
  LOCKED Skyy 2026-09-25: 2 free pages, max 10, page 3 = 50,000 coins, each next page +25,000, pages shared across all profiles
  (Wynncraft style). These were already the live defaults. Every number is in config.properties, so a later change needs no rebuild.
  Coins come from the ACTIVE profile's purse (coins:fn:take acts on the active profile) while the page belongs to the vault every
  profile shares - the Wynncraft pattern (one character's emeralds buy an account-wide bank page). The prices and the
  shared-pages rule are locked 2026-09-25. Not yet copied into tools/PROFILES-CONTRACT.md.
  ADMIN  /vaultadmin open <player> [page]   READ-ONLY snapshot of that vault page in a vanilla chest window: a COPY of the page in
                    a SimpleItemContainer with FilterType.DENY_ALL (vanilla /invsee read-only pattern: nothing can be taken or put
                    in, and it is a copy, so nothing can change the real vault).  /vaultadmin info <player>  /vaultadmin setpages
                    <player> <n> (never below the highest page that holds items)  /vaultadmin reload (config.properties,
                    through the config kit)  /vaultadmin config [<key> <value>] (0.1.1: list / set one config row).
                    <player> = online name, a name seen before (names.properties) or a UUID. requirePermission("skyyvault.admin")
                    on the root, on every subcommand and on the open <player> <page> variant.
  Every player command, subcommand and the /vault <page> variant call setPermissionGroups(new String[] { "hytale:Adventurer" }).

NO DUPES, NO LOSS (the design)
  * At rest a vault lives in memory as one ItemStack[] per page (VData) and on disk as vaults/<uuid>.json. While it is open, ONE
    session (VSession) per vault owner shows one page in its own SimpleItemContainer (the "view"); every change event of the view
    copies the view into that page's array at once (VSessions.syncView) and schedules a save. So the arrays always equal what the
    player sees, and the file follows within saveDelayMillis (1 s). Every close (Esc, window close, world change, disconnect - the
    engine's PlayerAddedSystem closes all windows when the entity leaves a world) syncs once more and writes at once.
  * ONE editable view per vault: SESSIONS is keyed by the owner UUID. A second /vault reuses the live session (same page type and
    still on screen: the slots are swapped in place); otherwise the old view is released BEFORE the new one exists: a window that is
    part of the page on screen is RETIRED (DENY_ALL, synced, marked closed - the new page replaces it, so a page is never closed
    right before another opens), a window that is not on screen is closed (its close syncs + saves), a session whose window is gone
    is finalized. The admin view never creates a session: it is a read-only copy (two viewers can never both edit one vault).
  * A closed session's view is made inert: marked closed (its change listener stops), unregistered, FilterType.DENY_ALL (a late
    client move into it is refused, so nothing can be put into a dead view and vanish) and emptied.
  * Page swap: sync the old page first, then clear + fill the view from the target page and read every slot back; if the view does
    not match exactly, the session closes WITHOUT syncing (noSync) - the arrays keep both pages untouched, nothing is lost.
  * Opening (and a page swap) is refused while profile:busy:<uuid> is set (SkyyProfiles crash recovery / switch transaction) and for
    afterSwitchSeconds (30) after profile:epoch:<uuid> changed or profile:busy went away. Why 30: SkyyProfiles keeps its switch marker
    (switching/<uuid>.properties) 30 s after EVERY switch and after every clean crash recovery (ClearLater), whatever islandOnSwitch
    says. A server crash while that marker exists rolls the player forward at the next join: inventory cleared and the snapshot taken
    at the switch loaded - every inventory change since the switch is undone. A vault move in that time would then exist twice (put
    in) or be gone (taken out), because the vault file keeps it. The vault notices a switch no earlier than it happened and the
    marker is armed before the epoch is published, so 30 s after the vault noticed is never earlier than the marker's deletion.
    Lowering afterSwitchSeconds shortens the wait but widens the crash window to (30 - afterSwitchSeconds) s after a switch. An open vault
    closes (world-thread task from the 1 s ticker) when profile:busy appears or the epoch changes; the window's
    ValidatedWindow.validate() (called by the engine on player movement) also closes it on busy, or when our page / the chest page is no
    longer on screen.
  * Buying: coins:fn:take FIRST (must return TRUE), then the page count goes up and the file is written synchronously and read back;
    if that write fails the page count goes back and the exact coins are refunded (coins:fn:add); every buy / failure / refund is in
    vault.log. 0.1.3: never twice for one intent - page-bound (expected page), one purchase at a time per player, the confirm
    window is one-shot and checks the price it showed, and every buy click / command within 1.5 s of a purchase is refused.
  * Files: tmp + fsync + ATOMIC_MOVE (5 x 20 ms retries on a Windows FileSystemException - SkyyProfiles 0.1 pattern), then read back
    and the slot count compared. Writes are ordered by a revision number under a per-vault IO lock, so an older snapshot can never
    overwrite a newer file. A vault file that exists but cannot be read keeps that vault SHUT (never overwritten, re-read on every
    try, warned once a minute). A stack that cannot be decoded (item removed from the game) is kept byte-for-byte in "orphans" and
    retried at every load - never dropped.
  * Lossless stacks: the SkyyProfiles 0.1 slot format - explicit id / qty / durability / max durability / quality / overrideAnim /
    metadata BsonDocument PLUS the engine's own ItemStack.CODEC encoding (decoded first, the explicit fields are the fallback), as
    EXTENDED JSON. SkyyRolls rolls (metadata "SkyyRolls") and graded dishes (Skyy_Cook_* ids + metadata) survive exactly.
  * Shutdown: every open view is made inert and synced (the container read lock makes that safe off the world thread), then every
    changed vault is written synchronously before the saver thread stops.

THREADS: /vault commands, page clicks, window close (GamePacketHandler.handleCloseWindow / PlayerAddedSystem) and the view change
  events run on the player's world thread. The ticker (1 s, shared scheduler) only reads the bridge and the session table and
  hands closes to the player's world thread (VCloseTask). That includes the last-resort finalize of a session whose viewer has been
  gone 10 s (normally the engine closed its window long before): it runs as a VCloseTask (offline=true) on the world the view was
  shown in, so it is serialized with any late engine close there. Only when that world no longer exists or refuses the task, or the
  task still has not run 10 s later (a dead world thread), does the ticker retire the view itself - then no thread can still reach
  the view (its player and world are gone). The other off-thread retire is plugin shutdown (below). File writes run on one daemon
  saver thread (VSaveJob); a buy / setpages writes on the calling world thread (it must know the result). 0.1.1: the maxPages check's
  folder walk runs on a short-lived daemon thread "SkyyVault-scan" (VScan, reads only; at most ~40 ms of it on the admin's thread).
  No ECS systems, no events registered - until 0.1.5: ONE ECS system, VDropSys (DropItemEvent$PlayerRequest), runs on the player's
  world thread inside the engine's DropItemStack packet task and touches only the vault's own session fields (noteHit / queueBtn).
COMMAND PERMISSIONS are checked by THIS SCRIPT at build time: tools/ci/lint.py only recognizes literal super("name" text, and every
  command here is generated by cmd(), so lint cannot see them. cmd() refuses a perm that is not @ADV@ / @ADMIN@, the generated
  constructor must contain setPermissionGroups / requirePermission, ADMIN_CMDS must match exactly the classes built with @ADMIN@
  (an admin command that forgot perm= fails the build instead of opening to players), and after compiling every command class file
  must reference setPermissionGroups + "hytale:Adventurer" or requirePermission + "skyyvault.admin".

DATA (<world>/mods/Skyy_SkyyVault/, stable across versions): vaults/<uuid>.json (EXTENDED JSON: format, mod, version, uuid, name,
  pages, capacity, savedAt, rev, count, content:[{page, slots:[{slot, id, qty, durability, maxDurability, quality, overrideAnim,
  meta, stack}]}], orphans:[{page, slot, ...}]); names.properties (lower-case name = uuid, for /vaultadmin with offline players);
  vault.log (BUY, BUY-FAIL, REFUND, SETPAGES, ADMIN-VIEW, WRITE-FAIL, FINALIZE-OFFLINE); config.properties (defaults written on first
  start; /vaultadmin reload re-reads it - slotsPerPage applies to vaults loaded afterwards); 0.1.1 kit files: config-changes.log (who
  changed what, via menu / command / file / import / restore / undo) and config-history/ (the last 20 versions of config.properties).

UNVERIFIED (needs Skyy in game): (1) whether the client draws the ContainerWindow's slots next to a CUSTOM page
  (openCustomPageWithWindows) - never confirmed for SkyySacks' /pd either; if not, the page's Open as chest button (and openMode=chest)
  is the working path; (2) the page layout on a real client; (3) that FilterType.DENY_ALL blocks the vanilla chest panel's Take all /
  Put all buttons for the admin copy (it does for vanilla /invsee, and the copy never touches the real vault anyway); (4) the client
  closing the window by itself when the custom page is closed (if it does not, onDismiss closes it 1.5 s later).
  0.1.1 CHECKED in a bare JVM (scratch harness, deleted afterwards; 101 checks, 0 fails): all 37 classes load under -Xverify:all;
  config:def / config:fn published with the 8 rows and flags above; every get equals the 0.1 defaults; an unchanged export imports as
  "nothing to change"; menu set without the node and a null UUID via=command are denied; afterSwitchSeconds 20 -> field 20000, file
  afterSwitchSeconds=20, VCfg.load reads it back as 20000, 121 refused; saveDelayMillis 50 refused (the confirm checks of that run were
  for the danger flags removed by the review fixes below); openMode chest/page flips PAGE_MODE, "book" refused; freePages above maxPages and maxPages below
  freePages refused; freePages 4 raises a loaded vault to 4 pages with no revision bump and price(4) = 0; maxPages 5 refused while a
  saved vault file holds items on page 7 (an unreadable vault file is skipped), 7 accepted, raising never scans, an orphan on page 9 of
  a loaded vault counts; slotsPerPage answers "applies to new ones"; 2k / 1,500 typed prices stored as 2000 / 1500; every line
  rewritten in place with the comments kept; a hand edit + the reload op is logged via=file, VHooks.reloadCfg applies it and the 0.1
  loader clamp (maxPages 3 below freePages 4 -> 4) is logged "clamped"; history versions exist; status ok.
  0.1.1 review fixes (bare JVM re-check listed in the build report): afterSwitchSeconds / saveDelayMillis lost danger + confirm= (spec
  4.3 flags); the maxPages lowering check never scans the vault folder for more than ~40 ms on the admin's thread (background VScan +
  "try again in a few seconds"); a comment at VStore.CACHE records that raiseTo() and the scan both rely on CACHE never being evicted.
  0.1.1 UNVERIFIED (needs Skyy in game): the Vault page in SkyyMenu 0.3 Server Setup (rows, ADV toggle, confirm questions, Changes /
  Undo / History / Export); /vaultadmin config + /vaultadmin config <key> <value> + /vaultadmin reload on a real server (engine
  command routing of the 0-arg base + 2-arg variant); the kit's permission re-check with a real op and a non-op; the first maxPages
  LOWERING on a server with many vault files (answers "try again in a few seconds" once, then from the background scan).
  KNOWN LIMIT (kit batches): an import / restore is checked against the CURRENT values, so a code that raises freePages above the
  current maxPages together with a higher maxPages is refused as a whole - raise Max pages first, then import.
KNOWN LIMIT: a SERVER CRASH (not a normal stop) within ~10 s after moving items between the inventory and the vault can duplicate or
  lose those stacks - the vault file is written within 1 s but the engine saves player inventories only every 10 s (the same window
  every Skyy storage mod has; tools/PROFILES-CONTRACT.md section 5). A normal stop / logout saves both sides. Right after a profile
  switch the window would be SkyyProfiles' 30 s marker instead (see the afterSwitchSeconds bullet); the default 30 s gate keeps the
  vault shut for exactly that time, so the ~10 s window stays the limit unless afterSwitchSeconds is lowered.
"""
import sys, os, re, json, zlib, struct, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI       # 0.1.4: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()               # proves every vanilla value / texture / sound the pages use against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line

VERSION = "0.1.5"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.vault"
# 0.1.4: colours that are NOT page chrome, kept exactly as 0.1.3 had them (research/Vanilla-UI-Style-Guide.md section 5; the lint rule
# for scripts that import the kit): the arrow items' own tooltips inside the vault chest (VBtn C_ARROW / C_OFF / C_GOLD / C_TEXT /
# C_DIM - the task keeps the container window, the arrow items and their filters untouched), the "+" / "-" / "=" CHAT line colours of
# VSessions.tell (chat, not a page) and the TextColor of the arrow items' own quality SkyyVaultButton.json.
UI_DATA_COLORS = ["#7cc4ff", "#9aa3ad", "#ffc94a", "#cfe3ff", "#7f8ea6",     # VBtn tooltips (the in-chest arrow items)
                  "#8fe39a", "#ff9d6b",                                    # VSessions.tell chat colours (+ / -; = and none use #cfe3ff)
                  "#d9b25c"]                                               # Server/Item/Qualities/SkyyVaultButton.json TextColor
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "CA":   "com.hypixel.hytale.component.ComponentAccessor",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGE":  "com.hypixel.hytale.protocol.packets.interface_.Page",
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC":  "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "FT":   "com.hypixel.hytale.server.core.inventory.container.filter.FilterType",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "CW":   "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow",
    "VWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow",
    "WIN":  "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "EREG": "com.hypixel.hytale.event.EventRegistration",
    # 0.1.2: per-slot filters, the player's inventory sections, windows, per-stack tooltips, the vanilla item throw
    "FAT":  "com.hypixel.hytale.server.core.inventory.container.filter.FilterActionType",
    "SF":   "com.hypixel.hytale.server.core.inventory.container.filter.SlotFilter",
    "STX":  "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
    "ISX":  "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "HOT":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "STO":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage",
    "BAK":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack",
    "ARM":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "UTI":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "TOO":  "com.hypixel.hytale.server.core.inventory.InventoryComponent$Tool",
    "CT":   "com.hypixel.hytale.component.ComponentType",
    "ICW":  "com.hypixel.hytale.server.core.entity.entities.player.windows.ItemContainerWindow",
    "IDM":  "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "IU":   "com.hypixel.hytale.server.core.entity.ItemUtils",
    "MT":   "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction",
    "MVT":  "com.hypixel.hytale.server.core.inventory.transaction.MoveType",
    "ACT":  "com.hypixel.hytale.server.core.inventory.transaction.ActionType",
    # 0.1.5: the Drop-key system (research/Vault-Arrow-Click-Research.md 4.5; the SkyyIslands GuardDrop / SkyyGear event_system shape)
    "EES":  "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "EV":   "com.hypixel.hytale.component.system.EcsEvent",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "DIRQ": "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest",
    "PKG":  PKG,
    "VERSION": VERSION,
    "ADV":  'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    "ADMIN": 'requirePermission("skyyvault.admin");',
}
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
WM  = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

# API probes: every engine member this mod calls (catches API drift at build time)
for c, m in ((T["UNI"], "get"), (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["UNI"], "getWorld"), (T["PR"], "getWorldUuid"),
             (T["PR"], "getUsername"), (T["PR"], "getUuid"), (T["PR"], "isValid"), (T["PR"], "sendMessage"), (T["PR"], "getReference"),
             (T["WLD"], "execute"), (T["HSV"], "SCHEDULED_EXECUTOR"), (PB, "shutdown"), (PB, "getDataDirectory"), (PB, "getCommandRegistry"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"),
             (T["ATY"], "STRING"), (T["CTX"], "get"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "onDismiss"), (T["PAGE"], "close"),
             (T["LIFE"], "CanDismiss"), (T["PLA"], "getPageManager"), (T["PLA"], "getWindowManager"), (T["PLA"], "getComponentType"),
             (PGM, "openCustomPage"), (PGM, "openCustomPageWithWindows"), (PGM, "setPageWithWindows"), (PGM, "getCustomPage"), (PGM, "setPage"),
             (WM, "getWindow"), (WM, "closeWindow"), (T["WIN"], "getId"), (T["CW"], "onClose0"), (T["CW"], "getItemContainer"),
             (T["VWIN"], "validate"), (T["PGE"], "Bench"), (T["PGE"], "None"), (T["FT"], "DENY_ALL"), (T["EREG"], "unregister"),
             (T["SIC"], "getItemStack"), (T["SIC"], "getCapacity"), (T["IC"], "setItemStackForSlot"), (T["IC"], "clear"),
             (T["IC"], "registerChangeEvent"), (T["SIC"], "setGlobalFilter"), (T["CA"], "getComponent"),
             (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "getDurability"), (T["IS"], "getMaxDurability"),
             (T["IS"], "getQualityIndex"), (T["IS"], "getMetadata"), (T["IS"], "getOverrideDroppedItemAnimation"),
             (T["IS"], "setOverrideDroppedItemAnimation"), (T["IS"], "isEmpty"), (T["CODEC"], "encode"), (T["CODEC"], "decode"),
             ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"), ("org.bson.json.JsonWriterSettings", "builder"),
             ("org.bson.json.JsonMode", "EXTENDED"),
             # 0.1.2 (arrows, filters, re-send, sweep, rescue, tooltips)
             (T["IC"], "setSlotFilter"), (T["SIC"], "setSlotFilter"), (T["FAT"], "ADD"), (T["FAT"], "REMOVE"), (T["FAT"], "DROP"),
             (T["SF"], "test"), (T["IC"], "removeItemStackFromSlot"), (T["IC"], "addItemStack"), (T["IC"], "getCapacity"),
             (T["IC"], "getItemStack"), (T["STX"], "succeeded"), (T["ISX"], "getRemainder"), (T["IS"], "withMetadata"),
             (T["IDM"], "KEYED_CODEC"), (T["MSG"], "empty"), (T["MSG"], "insert"), (T["WIN"], "invalidate"), (WM, "getWindows"),
             (T["ICW"], "getItemContainer"), (T["INVC"], "markDirty"), (T["INVC"], "getInventory"), (T["HOT"], "getComponentType"),
             (T["STO"], "getComponentType"), (T["BAK"], "getComponentType"), (T["ARM"], "getComponentType"),
             (T["UTI"], "getComponentType"), (T["TOO"], "getComponentType"), (T["IU"], "throwItem"), (T["REF"], "isValid"),
             (T["REF"], "getStore"), (T["PR"], "getUuid"), (T["IC"], "internal_moveItemStackFromSlot"), (T["IC"], "cantRemoveFromSlot"),
             (T["MVT"], "MOVE_FROM_SELF"), (T["ACT"], "REMOVE"), (T["ISX"], "FAILED_ADD"), (T["MT"], "toInverted"),
             # 0.1.5: the Drop-key system
             (T["EES"], "handle"), (T["DIRQ"], "getInventorySectionId"), (T["DIRQ"], "getSlotId"), (T["DIRQ"], "setCancelled"),
             (T["DIRQ"], "isCancelled"), (T["ACH"], "getReferenceTo"), (T["ST"], "getComponent"), (T["PR"], "getComponentType"),
             (PB, "getEntityStoreRegistry"), ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem")):
    B.probe(pool, c, m)
# 0.1.5: EventSystem.shouldProcessEvent is PROTECTED (B.probe sees public members only): VDropSys overrides it (true = also a request
# another system already cancelled); getDeclaredMethod fails the build if the engine renames it
for _c, _m, _sig in (("com.hypixel.hytale.component.system.EventSystem", "shouldProcessEvent", "(Lcom/hypixel/hytale/component/system/EcsEvent;)Z"),
                     (PB, "getEntityStoreRegistry", "()Lcom/hypixel/hytale/component/ComponentRegistryProxy;")):
    try:
        pool.get(_c).getMethod(_m, _sig)
    except Exception as _e:
        raise SystemExit("API probe failed: %s.%s%s not found (%s)" % (_c, _m, _sig, _e))

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


# ---- config defaults (edit here, rebuild; Skyy can also edit config.properties and /vaultadmin reload)
DEF_FREE, DEF_MAX, DEF_SLOTS = 2, 10, 36
DEF_PRICE, DEF_STEP, DEF_BUY_CONFIRM = 50000, 25000, 50000
DEF_AFTER_SWITCH_S, DEF_SAVE_DELAY_MS = 30, 1000   # 30 = SkyyProfiles 0.1 keeps its switch marker 30 s (ClearLater)
DEF_SWEEP_S = 30        # 0.1.2: stray arrow check period (straySweepSeconds)
MAX_CAP = 1024          # hard cap on slots per page (a hand-edited file cannot make a huge container)
MAX_PAGE = 1000         # hard cap on page numbers

cfg  = pool.makeClass(PKG + ".VCfg")
dat  = pool.makeClass(PKG + ".VData")
cod  = pool.makeClass(PKG + ".VCodec")
sto  = pool.makeClass(PKG + ".VStore")
sjob = pool.makeClass(PKG + ".VSaveJob")
thf  = pool.makeClass(PKG + ".VThreads")
ses  = pool.makeClass(PKG + ".VSession")
chg  = pool.makeClass(PKG + ".VChange")
win  = pool.makeClass(PKG + ".VWindow", pool.get(T["CW"]))
page = pool.makeClass(PKG + ".VaultPage", pool.get(T["PAGE"]))
clt  = pool.makeClass(PKG + ".VCloseTask")
vs   = pool.makeClass(PKG + ".VSessions")
tick = pool.makeClass(PKG + ".VTick")
hk   = pool.makeClass(PKG + ".VHooks")          # 0.1.1: config kit hooks (check= / after= / RELOAD)
scn  = pool.makeClass(PKG + ".VScan")           # 0.1.1 review: the background vault-file scan for the maxPages check (Runnable)
btn  = pool.makeClass(PKG + ".VBtn")            # 0.1.2: the arrow items (ids, kinds, canonical stacks, tooltips)
bfl  = pool.makeClass(PKG + ".VBtnFilter")      # 0.1.2: SlotFilter on every non-storage index (refuses everything, notes the click)
btk  = pool.makeClass(PKG + ".VBtnTask")        # 0.1.2: one click batch on the viewer's world thread (Runnable)
swt  = pool.makeClass(PKG + ".VSweepTask")      # 0.1.2: the stray-arrow sweep of one player on their world thread (Runnable)
vv   = pool.makeClass(PKG + ".VView", pool.get(T["SIC"]))   # 0.1.2: the arrow window's container (refused whole-slot moves never NPE)
dlg  = pool.makeClass(PKG + ".VBuyDlg", pool.get(T["PAGE"]))  # 0.1.3: the "Buy page X for Y coins?" confirm window (vanilla look)
drs  = pool.makeClass(PKG + ".VDropSys", pool.get(T["EES"]))  # 0.1.5: the Drop key on a vault arrow (DropItemEvent$PlayerRequest)
pl   = pool.makeClass(PKG + ".SkyyVaultPlugin", pool.get(T["JP"]))
ALL = [cfg, dat, cod, sto, sjob, thf, ses, chg, win, page, clt, vs, tick, hk, scn, btn, bfl, btk, swt, vv, dlg, drs]

# ================= VCfg: logger, bridge, config, atomic files =================
CFG_LINES = [
    "# SkyyVault config - change it in game (SkyWynn Menu -> Server Setup -> Vault, or /vaultadmin config <key> <value>),",
    "# or edit it here, then /vaultadmin reload (or restart the server)",
    "# LOCKED Skyy 2026-09-25: 2 free pages, max 10, page 3 = pagePrice (50000), each next page + pagePriceStep (25000).",
    "# Pages are shared across all profiles (Wynncraft style). In-chest Prev/Next arrows are the approved way to cycle pages.",
    "# freePages = vault pages every player owns for free (the vault is shared by all profiles of a player)",
    "freePages=%d" % DEF_FREE,
    "# maxPages = the most vault pages a player can own (free + bought)",
    "maxPages=%d" % DEF_MAX,
    "# slotsPerPage = slots on one vault page (36 = a large chest). Applies to vaults loaded after a reload / restart.",
    "# Lowering it never hides items: a vault that already uses a higher slot keeps its bigger pages.",
    "slotsPerPage=%d" % DEF_SLOTS,
    "# pagePrice = coins for the first bought page; each later page costs pagePriceStep more",
    "# (with freePages=2: page 3 = pagePrice, page 4 = pagePrice + pagePriceStep, ...)",
    "pagePrice=%d" % DEF_PRICE,
    "pagePriceStep=%d" % DEF_STEP,
    "# buyConfirmCoins = LOCKED Skyy 2026-09-25. A page cheaper than this buys at once.",
    "#   This price or more asks \"Buy page X for Y coins?\" before coins move.",
    "#   The gold arrow in the vault window, the page's Buy button and /vault buy all follow it (SkyyVault 0.1.3+).",
    "buyConfirmCoins=%d" % DEF_BUY_CONFIRM,
    "# openMode = page: /vault opens the vault page (buttons) together with the vault slots; its Open as chest button opens the plain chest",
    "#            chest: /vault opens the plain chest window at once; /vault pages opens the page with the buttons",
    "openMode=page",
    "# afterSwitchSeconds = the vault stays shut this many seconds after a profile switch (or a crash recovery at join).",
    "# SkyyProfiles keeps its switch marker 30 s: a server crash in that time undoes every inventory change since the switch,",
    "# so a vault move then would duplicate or lose items. Lower = less waiting but that crash window comes back.",
    "afterSwitchSeconds=%d" % DEF_AFTER_SWITCH_S,
    "# saveDelayMillis = how soon after a change the vault file is written (closing the vault writes it at once)",
    "saveDelayMillis=%d" % DEF_SAVE_DELAY_MS,
    "# pageArrows = arrow items inside the vault window turn pages (Wynncraft style): true or false. Applies to vault windows opened afterwards.",
    "# APPROVED Skyy 2026-09-25: these in-chest Prev/Next arrows are the way to cycle pages. Do not add a second page-switch UI.",
    "pageArrows=true",
    "# arrowLayout = row: an extra control row under the vault slots (every slot stays usable)",
    "#   or inside: the arrows use the first and last slot of the page's last row (an item stored there moves to a free slot first)",
    "arrowLayout=row",
    "# straySweepSeconds = how often online players are checked for stray vault arrow items (removed and written to vault.log)",
    "straySweepSeconds=%d" % DEF_SWEEP_S,
]
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path VDIR;", "public static java.nio.file.Path FILE;",
          "public static java.nio.file.Path LOGF;", "public static java.nio.file.Path NAMESF;", "public static @LOG@ LOG;",
          "public static volatile int FREE_PAGES = %d;" % DEF_FREE, "public static volatile int MAX_PAGES = %d;" % DEF_MAX,
          "public static volatile int SLOTS = %d;" % DEF_SLOTS, "public static volatile long PRICE = %dL;" % DEF_PRICE,
          "public static volatile long STEP = %dL;" % DEF_STEP,
          "public static volatile long BUY_CONFIRM = %dL;" % DEF_BUY_CONFIRM,
          "public static volatile long AFTER_SWITCH_MS = %dL;" % (DEF_AFTER_SWITCH_S * 1000),
          "public static volatile long SAVE_DELAY_MS = %dL;" % DEF_SAVE_DELAY_MS, "public static volatile boolean PAGE_MODE = true;",
          # 0.1.1: the config kit binds openMode to this String twin (a choice row cannot bind a boolean); VCfg.load and the kit's
          # after= hook (VHooks.afterOpenMode) keep PAGE_MODE, which the rest of the mod reads, in step with it
          "public static volatile String OPEN_MODE = \"page\";",
          # 0.1.2: page arrows (config kit rows pageArrows / arrowLayout / straySweepSeconds)
          "public static volatile boolean ARROWS = true;", "public static volatile String ARROW_LAYOUT = \"row\";",
          "public static volatile long SWEEP_MS = %dL;" % (DEF_SWEEP_S * 1000),
          # 0.1.3: the 10 s second click (CONFIRM_MS) is gone (LOCKED Skyy 2026-09-25: buyConfirmCoins + a confirm window). BUY_GUARD_MS =
          # after a purchase, another buy CLICK / command of the same player within this time is refused (a double click, or a
          # shift-click that reaches the server as two packets, never buys two pages). The window's own Buy button is not guarded.
          "public static volatile long BUY_GUARD_MS = 1500L;", "public static final int MAX_CAP = %d;" % MAX_CAP,
          "public static final int MAX_PAGE = %d;" % MAX_PAGE,
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();"):
    F(cfg, f)
F(cfg, "public static final String[] DEFAULT_LINES = %s;" % jarr(CFG_LINES))
M(cfg, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(cfg, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyVault] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyVault] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnOnce(String key, String msg) {
  long now = System.currentTimeMillis();
  Object last = WARNED.get(key);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  WARNED.put(key, Long.valueOf(now));
  warn(msg);
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d, long lo, long hi) {
  long v = d;
  try { String s = p.getProperty(k); if (s != null) v = Long.parseLong(s.trim()); } catch (Throwable t) { v = d; }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
# tmp file + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyProfiles 0.1 ProfCfg.atomicWrite)
M(cfg, r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(cfg, r"""
public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")
M(cfg, r"""
public static void appendLine(java.nio.file.Path f, String line) {
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(f, (line + "\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { warn("could not append to " + f + ": " + t); }
}""")
M(cfg, r"""
public static String summary() {
  return "free pages " + FREE_PAGES + ", max " + MAX_PAGES + ", " + SLOTS + " slots per page, price " + PRICE + " +" + STEP + " per page, confirm from " + BUY_CONFIRM + ", openMode " + (PAGE_MODE ? "page" : "chest") + ", page arrows " + (ARROWS ? ARROW_LAYOUT : "off") + ", stray check every " + (SWEEP_MS / 1000L) + " s";
}""")
# 0.1.2: storage slots a page offers for new windows (the arrows use 2 of them with arrowLayout=inside); labels only
M(cfg, r"""
public static int usable(int cap) {
  if (ARROWS && "inside".equals(ARROW_LAYOUT) && cap > 2) return cap - 2;
  return cap;
}""")
M(cfg, r"""
public static synchronized String load() {
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < DEFAULT_LINES.length; i++) sb.append(DEFAULT_LINES[i]).append("\n");
      atomicWrite(FILE, sb.toString().getBytes("UTF-8"));
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    int fp = (int) lng(p, "freePages", (long) FREE_PAGES, 1L, 100L);
    int mp = (int) lng(p, "maxPages", (long) MAX_PAGES, 1L, (long) MAX_PAGE);
    if (mp < fp) mp = fp;
    FREE_PAGES = fp;
    MAX_PAGES = mp;
    SLOTS = (int) lng(p, "slotsPerPage", (long) SLOTS, 9L, 90L);
    PRICE = lng(p, "pagePrice", PRICE, 0L, 1000000000000L);
    STEP = lng(p, "pagePriceStep", STEP, 0L, 1000000000000L);
    BUY_CONFIRM = lng(p, "buyConfirmCoins", BUY_CONFIRM, 0L, 1000000000000L);
    AFTER_SWITCH_MS = lng(p, "afterSwitchSeconds", AFTER_SWITCH_MS / 1000L, 0L, 120L) * 1000L;
    SAVE_DELAY_MS = lng(p, "saveDelayMillis", SAVE_DELAY_MS, 100L, 30000L);
    String om = p.getProperty("openMode");
    if (om != null) {
      om = om.trim().toLowerCase();
      if (om.equals("chest")) { PAGE_MODE = false; OPEN_MODE = "chest"; }
      else if (om.equals("page")) { PAGE_MODE = true; OPEN_MODE = "page"; }
    }
    String pa = p.getProperty("pageArrows");
    if (pa != null) {
      pa = pa.trim().toLowerCase();
      if (pa.equals("true") || pa.equals("on") || pa.equals("yes") || pa.equals("1")) ARROWS = true;
      else if (pa.equals("false") || pa.equals("off") || pa.equals("no") || pa.equals("0")) ARROWS = false;
    }
    String al = p.getProperty("arrowLayout");
    if (al != null) {
      if ("inside".equals(al.trim().toLowerCase())) ARROW_LAYOUT = "inside";
      else ARROW_LAYOUT = "row";
    }
    SWEEP_MS = lng(p, "straySweepSeconds", SWEEP_MS / 1000L, 5L, 600L) * 1000L;
  } catch (Throwable t) { warn("config.properties could not be read (defaults / previous values kept): " + t); }
  return summary();
}""")

# ================= 0.1.1: the admin config kit (research/Server-Setup-Spec.md 4.3; tools/CONFIG-CONTRACT.md) =================
# Row key = file key (spec 7: the file key never changes). The loader's ranges are the rows' min/max (typed values are refused, file
# values are clamped by VCfg.load exactly as in 0.1). Hooks live in VHooks (compiled after VStore; kit.write checks they exist).
CONFIG_TEXT = "".join(l + "\n" for l in CFG_LINES)     # = what VCfg.load writes on first start (DEFAULT_LINES, one "\n" each)
CATS = [("vault", "Vault")]
F_ = "@config.properties:"
ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("freePages", "Free pages", "vault", "int", str(DEF_FREE), "1", "100", "step=1", "", "live,danger",
     "Vault pages every player owns for free. Cannot be above Max pages.",
     "field:VCfg.FREE_PAGES" + F_ + "freePages;check=VHooks.checkFree;after=VHooks.afterFree"),
    ("maxPages", "Max pages", "vault", "int", str(DEF_MAX), "1", str(MAX_PAGE), "step=1", "", "live,danger",
     "Most pages a player can own. Never below Free pages or below a page that still holds items.",
     "field:VCfg.MAX_PAGES" + F_ + "maxPages;check=VHooks.checkMax"),
    ("slotsPerPage", "Slots per page", "vault", "int", str(DEF_SLOTS), "9", "90", "step=9", "", "new,danger",
     "36 = a large chest. Used for vaults loaded after the change; items are never hidden.",
     "field:VCfg.SLOTS" + F_ + "slotsPerPage"),
    ("pagePrice", "Price of the first bought page", "vault", "int", str(DEF_PRICE), "0", "1000000000000", "", "coins", "live",
     "Page N costs this + Price step x (N - Free pages - 1).",
     "field:VCfg.PRICE" + F_ + "pagePrice"),
    ("pagePriceStep", "Price step per page", "vault", "int", str(DEF_STEP), "0", "1000000000000", "", "coins", "live",
     "Each later bought page costs this many coins more than the one before.",
     "field:VCfg.STEP" + F_ + "pagePriceStep"),
    # LOCKED Skyy 2026-09-25 (row added by Skyy in commit ab75b6c). 0.1.3: VStore.intent reads it for the gold arrow, the page's Buy
    # button and /vault buy (price < value = buy at once, price >= value = the VBuyDlg confirm window).
    ("buyConfirmCoins", "Buy confirm threshold", "vault", "int", str(DEF_BUY_CONFIRM), "0", "1000000000000", "", "coins", "live",
     "A cheaper page buys at once. This price or more asks Buy page X for Y coins? first.",
     "field:VCfg.BUY_CONFIRM" + F_ + "buyConfirmCoins"),
    ("openMode", "Open /vault as", "vault", "choice", "page", "", "", "page|Page view,chest|Chest window", "", "live",
     "Page view: the vault page with buttons and slots. Chest window: the plain chest at once.",
     "field:VCfg.OPEN_MODE" + F_ + "openMode;after=VHooks.afterOpenMode"),
    # spec 4.3 flags exactly (L, A - no danger / confirm): the help text carries the crash warning. A confirm on the risky direction
    # (danger + confirm=down / confirm=up) is a proposal for Skyy, not built until spec 4.3 says so.
    ("afterSwitchSeconds", "Wait after a profile switch", "vault", "int", str(DEF_AFTER_SWITCH_S), "0", "120", "step=5", "s",
     "live,adv", "Vault stays shut this long after a profile switch. Under 30 s a server crash can dupe items.",
     "field:VCfg.AFTER_SWITCH_MS*1000" + F_ + "afterSwitchSeconds"),
    ("saveDelayMillis", "Vault save delay", "vault", "int", str(DEF_SAVE_DELAY_MS), "100", "30000", "step=100", "ms",
     "live,adv", "How soon a change is written to the vault file. Longer = more lost if the server crashes.",
     "field:VCfg.SAVE_DELAY_MS" + F_ + "saveDelayMillis"),
    # 0.1.2: page arrows (research/Vault-Arrows-Spec.md section 8, tuples exactly as specified)
    ("pageArrows", "Page arrows in the vault window", "vault", "bool", "true", "", "", "", "", "new",
     "Arrow items in the vault window turn pages. Applies to vault windows opened afterwards.",
     "field:VCfg.ARROWS" + F_ + "pageArrows"),
    ("arrowLayout", "Where the page arrows go", "vault", "choice", "row", "", "", "row|Extra row,inside|Inside the page", "", "new,danger",
     "Extra row: a control row under the slots. Inside: arrows use 2 page slots (items there move).",
     "field:VCfg.ARROW_LAYOUT" + F_ + "arrowLayout"),
    ("straySweepSeconds", "Stray arrow check every", "vault", "int", str(DEF_SWEEP_S), "5", "600", "step=5", "s", "live,adv",
     "Online players are checked this often for stray vault arrow items, which are removed.",
     "field:VCfg.SWEEP_MS*1000" + F_ + "straySweepSeconds"),
]
kit = CFG.emit(pool, PKG, MOD="SkyyVault", TITLE="Vault", VERSION=VERSION, NODE="skyyvault.admin", CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyVault/config.properties"], RELOAD="VHooks.reloadCfg", KEEP=10,   # 0.1.3: 10 old versions (LOCKED, was 20)
               NOTE="Player pages: /vaultadmin setpages <player> <n>. Look inside: /vaultadmin open <player>.",
               DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= VData: one player's vault in memory (arrays = what the player sees) =================
for f in ("public java.util.UUID owner;", "public String name;", "public int unlocked;", "public int cap;",
          "public java.util.ArrayList pages;", "public org.bson.BsonArray orphans;", "public volatile long rev;",
          "public volatile long writtenRev;", "public Object ioLock;"):
    F(dat, f)
C(dat, r"""
public VData(java.util.UUID o, int cap) {
  this.owner = o; this.name = ""; this.unlocked = 0; this.cap = cap;
  this.pages = new java.util.ArrayList(); this.orphans = new org.bson.BsonArray();
  this.rev = 0L; this.writtenRev = 0L; this.ioLock = new Object();
}""")
M(dat, r"""
public synchronized @IS@[] page(int n) {
  while (this.pages.size() < n) this.pages.add(new @IS@[this.cap]);
  return (@IS@[]) this.pages.get(n - 1);
}""")
M(dat, r"""
public synchronized int used(int n) {
  if (n < 1 || n > this.pages.size()) return 0;
  @IS@[] a = (@IS@[]) this.pages.get(n - 1);
  int c = 0;
  for (int i = 0; i < a.length; i++) if (a[i] != null && !a[i].isEmpty()) c++;
  return c;
}""")
M(dat, r"""
public synchronized int highestUsed() {
  for (int p = this.pages.size(); p >= 1; p--) if (used(p) > 0) return p;
  return 0;
}""")
M(dat, r"""
public synchronized int total() {
  int c = 0;
  for (int p = 1; p <= this.pages.size(); p++) c = c + used(p);
  return c;
}""")
M(dat, r"""
public synchronized @IS@[] pageCopy(int n) {
  @IS@[] a = page(n);
  @IS@[] c = new @IS@[a.length];
  System.arraycopy(a, 0, c, 0, a.length);
  return c;
}""")
# the view -> page array copy (every change event); true when anything changed (then rev + 1)
M(dat, r"""
public synchronized boolean copyIn(int n, @IS@[] now) {
  @IS@[] a = page(n);
  boolean ch = false;
  for (int i = 0; i < a.length && i < now.length; i++) {
    if (a[i] != now[i]) { a[i] = now[i]; ch = true; }
  }
  if (ch) this.rev = this.rev + 1L;
  return ch;
}""")
# 0.1.2 arrowLayout=inside: before page pg is shown, a stack stored in a reserved arrow slot (ra / rb) moves to the first free
# non-reserved slot of that page, else of any other owned page; whole vault full = it stays (that page shows it instead of the arrow,
# VSessions.blockedNote tells the player).
# Counted before and after (total()); a different count undoes every move. Returns String[] { vault.log line or null, chat line or
# null } per stack looked at; rev + 1 when anything moved (the caller schedules the save).
M(dat, r"""
public synchronized java.util.ArrayList clearReserved(int pg, int ra, int rb) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (pg < 1 || pg > this.unlocked) return out;
  @IS@[] p = page(pg);
  int before = total();
  java.util.ArrayList undo = new java.util.ArrayList();
  for (int k = 0; k < 2; k++) {
    int r = k == 0 ? ra : rb;
    if (r < 0 || r >= p.length) continue;
    @IS@ it = p[r];
    if (it == null || it.isEmpty()) continue;
    int tp = -1;
    int ts = -1;
    for (int i = 0; i < p.length && ts < 0; i++) {
      if (i != ra && i != rb && (p[i] == null || p[i].isEmpty())) { tp = pg; ts = i; }
    }
    for (int q = 1; q <= this.unlocked && ts < 0; q++) {
      if (q == pg) continue;
      @IS@[] o = page(q);
      for (int i = 0; i < o.length && ts < 0; i++) {
        if (i != ra && i != rb && (o[i] == null || o[i].isEmpty())) { tp = q; ts = i; }
      }
    }
    if (ts < 0) continue;
    @IS@[] dst = page(tp);
    dst[ts] = it;
    p[r] = null;
    undo.add(new int[] { tp, ts, r });
    out.add(new String[] { "RESERVED-MOVE " + this.owner + " " + pg + ":" + r + " -> " + tp + ":" + ts + " " + it.getItemId() + " x" + it.getQuantity(),
                           "=Moved " + it.getQuantity() + " " + it.getItemId() + " from page " + pg + " slot " + (r + 1) + " to page " + tp + " slot " + (ts + 1) + " to make room for the page arrow." });
  }
  if (undo.size() == 0) return out;
  if (total() != before) {
    for (int j = undo.size() - 1; j >= 0; j--) {
      int[] m = (int[]) undo.get(j);
      @IS@[] dst = page(m[0]);
      p[m[2]] = dst[m[1]];
      dst[m[1]] = null;
    }
    out.clear();
    out.add(new String[] { "RESERVED-UNDO " + this.owner + " page " + pg + " (the stack count changed - every move was undone)", null });
    return out;
  }
  this.rev = this.rev + 1L;
  return out;
}""")
# 0.1.2 rescue step 3: the first free slot of any owned page except `skip` (the page on screen: the view is its truth); ra / rb =
# reserved arrow slots (-1 = none). Returns "page:slot" or null (no free slot); rev + 1 when placed.
M(dat, r"""
public synchronized String putFirstFree(int skip, int ra, int rb, @IS@ st) {
  for (int q = 1; q <= this.unlocked; q++) {
    if (q == skip) continue;
    @IS@[] o = page(q);
    for (int i = 0; i < o.length; i++) {
      if (i != ra && i != rb && (o[i] == null || o[i].isEmpty())) {
        o[i] = st;
        this.rev = this.rev + 1L;
        return q + ":" + i;
      }
    }
  }
  return null;
}""")

# ================= VCodec: the SkyyProfiles 0.1 lossless slot format =================
M(cod, r"""
public static int intOf(org.bson.BsonDocument d, String k, int def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(cod, r"""
public static double dblOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return 0.0;
}""")
M(cod, r"""
public static String strOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return null;
}""")
# 0.1.2: a vault arrow item id (UI items of this mod: never stored, never saved, removed wherever found)
M(cod, r"""
public static boolean btnId(String id) {
  return id != null && id.startsWith("Skyy_Vault_");
}""")
M(cod, r"""
public static org.bson.BsonDocument slotDoc(int slot, @IS@ s) {
  org.bson.BsonDocument d = new org.bson.BsonDocument();
  d.put("slot", new org.bson.BsonInt32(slot));
  d.put("id", new org.bson.BsonString(s.getItemId()));
  d.put("qty", new org.bson.BsonInt32(s.getQuantity()));
  d.put("durability", new org.bson.BsonDouble(s.getDurability()));
  d.put("maxDurability", new org.bson.BsonDouble(s.getMaxDurability()));
  d.put("quality", new org.bson.BsonInt32(s.getQualityIndex()));
  d.put("overrideAnim", new org.bson.BsonBoolean(s.getOverrideDroppedItemAnimation()));
  org.bson.BsonDocument m = s.getMetadata();
  if (m != null) d.put("meta", (org.bson.BsonDocument) m.clone());
  try {
    org.bson.BsonValue enc = ((@CODEC@) @IS@.CODEC).encode(s);
    if (enc != null) d.put("stack", enc);
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("enc-" + s.getItemId(), "ItemStack.CODEC could not encode " + s.getItemId() + " (explicit fields kept): " + t); }
  return d;
}""")
# engine codec first (exact engine persistence semantics), explicit fields as the fallback; null = cannot be rebuilt (kept as orphan)
M(cod, r"""
public static @IS@ stackOf(org.bson.BsonDocument d) {
  String id = strOf(d, "id");
  int qty = intOf(d, "qty", 0);
  if (id == null || id.length() == 0 || qty <= 0) return null;
  try {
    org.bson.BsonValue enc = (org.bson.BsonValue) d.get("stack");
    if (enc != null && enc.isDocument()) {
      Object o = ((@CODEC@) @IS@.CODEC).decode(enc);
      if (o instanceof @IS@) {
        @IS@ s = (@IS@) o;
        if (!s.isEmpty() && id.equals(s.getItemId()) && s.getQuantity() == qty) return s;
      }
    }
  } catch (Throwable t) { }
  org.bson.BsonDocument meta = null;
  try { org.bson.BsonValue mv = (org.bson.BsonValue) d.get("meta"); if (mv != null && mv.isDocument()) meta = mv.asDocument(); } catch (Throwable t) { }
  @IS@ s2 = null;
  try { s2 = new @IS@(id, qty, dblOf(d, "durability"), dblOf(d, "maxDurability"), intOf(d, "quality", 0), meta); }
  catch (Throwable t) { return null; }
  try {
    org.bson.BsonValue a = (org.bson.BsonValue) d.get("overrideAnim");
    if (a != null && a.isBoolean() && a.asBoolean().getValue()) s2.setOverrideDroppedItemAnimation(true);
  } catch (Throwable t) { }
  return s2;
}""")
M(cod, r"""
public static String toJson(org.bson.BsonDocument d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")
M(cod, r"""
public static int countSlots(org.bson.BsonDocument doc) {
  if (doc == null) return -1;
  int n = 0;
  org.bson.BsonArray c = doc.getArray("content", new org.bson.BsonArray());
  for (int i = 0; i < c.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) c.get(i);
    if (v != null && v.isDocument()) n = n + v.asDocument().getArray("slots", new org.bson.BsonArray()).size();
  }
  return n + doc.getArray("orphans", new org.bson.BsonArray()).size();
}""")

# ================= VStore: cache, load, files, saver, buy =================
# CACHE is NEVER evicted (nothing calls CACHE.remove): every vault loaded since the start stays in memory until the JVM exits. Two 0.1.1
# config hooks rely on that: (1) VData.raiseTo (a freePages raise) is memory-only - no rev bump, no file write - and is persisted by the
# next real vault write; (2) the maxPages scan (VHooks.scanDir) skips the files of loaded vaults and reads those from memory. Any future
# eviction (idle unload, memory sweep) must FIRST save the vault's current in-memory state (bump rev so the grant is written, then write
# it) and only then remove it from CACHE - otherwise a freePages raise vanishes for that player at the next load.
for f in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",
          # 0.1.3: BUYING = players with a purchase in progress (one at a time per player); LASTBUY = uuid -> Long time of the player's
          # last bought page (the BUY_GUARD_MS double-click guard). The 0.1.2 CONFIRM map (10 s second click) is gone.
          "public static final java.util.concurrent.ConcurrentHashMap BUYING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LASTBUY = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile boolean NAMES_DIRTY = false;",
          "public static volatile java.util.concurrent.ScheduledExecutorService SAVER = null;",
          "public static volatile boolean STOPPING = false;"):
    F(sto, f)
M(sto, r"""
public static java.nio.file.Path fileOf(java.util.UUID u) {
  return @PKG@.VCfg.VDIR.resolve(u.toString() + ".json");
}""")
M(sto, r"""
public static void log(String line) {
  @PKG@.VCfg.appendLine(@PKG@.VCfg.LOGF, java.time.Instant.now().toString() + " " + line);
}""")
M(sto, r"""
public static String grp(long n) {
  String s = Long.toString(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
# compact amount for button text (inline Text avoids commas): 50000 -> 50k, 1500000 -> 1.5m
M(sto, r"""
public static String shortAmt(long n) {
  if (n >= 1000000L) {
    long t = n / 100000L;
    return (t % 10L == 0L) ? (t / 10L) + "m" : (t / 10L) + "." + (t % 10L) + "m";
  }
  if (n >= 1000L) {
    long t = n / 100L;
    return (t % 10L == 0L) ? (t / 10L) + "k" : (t / 10L) + "." + (t % 10L) + "k";
  }
  return String.valueOf(n);
}""")
M(sto, r"""
public static long price(int page) {
  if (page <= @PKG@.VCfg.FREE_PAGES) return 0L;
  long p = @PKG@.VCfg.PRICE + @PKG@.VCfg.STEP * (long) (page - @PKG@.VCfg.FREE_PAGES - 1);
  return p < 0L ? 0L : p;
}""")
M(sto, r"""
public static String nameOf(@PKG@.VData d) {
  if (d == null) return "?";
  if (d.name != null && d.name.length() > 0) return d.name;
  return d.owner.toString();
}""")
# the whole vault as one BsonDocument; the caller holds the VData monitor (VData.snap)
M(sto, r"""
public static org.bson.BsonDocument toDoc(@PKG@.VData d) {
  org.bson.BsonDocument doc = new org.bson.BsonDocument();
  doc.put("format", new org.bson.BsonInt32(1));
  doc.put("mod", new org.bson.BsonString("SkyyVault"));
  doc.put("version", new org.bson.BsonString("@VERSION@"));
  doc.put("uuid", new org.bson.BsonString(d.owner.toString()));
  doc.put("name", new org.bson.BsonString(d.name == null ? "" : d.name));
  doc.put("pages", new org.bson.BsonInt32(d.unlocked));
  doc.put("capacity", new org.bson.BsonInt32(d.cap));
  doc.put("savedAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  doc.put("rev", new org.bson.BsonInt64(d.rev));
  org.bson.BsonArray content = new org.bson.BsonArray();
  int count = 0;
  for (int p = 0; p < d.pages.size(); p++) {
    @IS@[] a = (@IS@[]) d.pages.get(p);
    org.bson.BsonArray slots = new org.bson.BsonArray();
    for (int i = 0; i < a.length; i++) {
      if (a[i] == null || a[i].isEmpty()) continue;
      slots.add(@PKG@.VCodec.slotDoc(i, a[i]));
      count++;
    }
    if (slots.size() > 0) {
      org.bson.BsonDocument pd = new org.bson.BsonDocument();
      pd.put("page", new org.bson.BsonInt32(p + 1));
      pd.put("slots", slots);
      content.add(pd);
    }
  }
  doc.put("content", content);
  doc.put("count", new org.bson.BsonInt32(count));
  doc.put("orphans", d.orphans);
  return doc;
}""")
# one saved slot into the arrays; anything that cannot be placed (unknown item, bad page/slot, slot taken) is kept as an orphan
M(sto, r"""
public static void place(@PKG@.VData d, int pg, org.bson.BsonDocument sd) {
  int s = @PKG@.VCodec.intOf(sd, "slot", -1);
  @IS@ st = null;
  if (pg >= 1 && pg <= @PKG@.VCfg.MAX_PAGE && s >= 0 && s < d.cap) st = @PKG@.VCodec.stackOf(sd);
  if (st != null) {
    @IS@[] a = d.page(pg);
    if (a[s] == null) { a[s] = st; return; }
  }
  org.bson.BsonDocument o = (org.bson.BsonDocument) sd.clone();
  o.put("page", new org.bson.BsonInt32(pg));
  d.orphans.add(o);
  @PKG@.VCfg.warn("kept a vault stack that cannot be placed for " + d.owner + " (page " + pg + " slot " + s + ", " + @PKG@.VCodec.strOf(sd, "id") + ") - saved unchanged, retried at every load");
}""")
# 0.1.2: a vault arrow item found in a vault file (a UI item with no value) is dropped at load and logged; the file loses it at the
# next write
M(sto, r"""
public static void strayFile(java.util.UUID u, int pg, int slot, String id) {
  log("STRAY-FILE " + u + " page " + pg + " slot " + slot + " " + id + " (vault arrow item dropped at load)");
  @PKG@.VCfg.warn("dropped a vault arrow item (" + id + ") found in the vault file of " + u + " (page " + pg + " slot " + slot + ") - see vault.log");
}""")
M(sto, r"""
public static @PKG@.VData fromDoc(java.util.UUID u, org.bson.BsonDocument doc) {
  org.bson.BsonArray content = doc.getArray("content", new org.bson.BsonArray());
  org.bson.BsonArray orph = doc.getArray("orphans", new org.bson.BsonArray());
  int maxSlot = -1;
  int maxPage = 0;
  for (int i = 0; i < content.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) content.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument pd = v.asDocument();
    int pg = @PKG@.VCodec.intOf(pd, "page", 0);
    org.bson.BsonArray sl = pd.getArray("slots", new org.bson.BsonArray());
    if (sl.size() > 0 && pg > maxPage && pg <= @PKG@.VCfg.MAX_PAGE) maxPage = pg;
    for (int k = 0; k < sl.size(); k++) {
      org.bson.BsonValue sv = (org.bson.BsonValue) sl.get(k);
      if (sv == null || !sv.isDocument()) continue;
      if (@PKG@.VCodec.btnId(@PKG@.VCodec.strOf(sv.asDocument(), "id"))) continue;
      int s = @PKG@.VCodec.intOf(sv.asDocument(), "slot", -1);
      if (s > maxSlot && s < @PKG@.VCfg.MAX_CAP) maxSlot = s;
    }
  }
  for (int i = 0; i < orph.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) orph.get(i);
    if (v == null || !v.isDocument()) continue;
    if (@PKG@.VCodec.btnId(@PKG@.VCodec.strOf(v.asDocument(), "id"))) continue;
    int pg = @PKG@.VCodec.intOf(v.asDocument(), "page", 0);
    int s = @PKG@.VCodec.intOf(v.asDocument(), "slot", -1);
    if (pg > maxPage && pg <= @PKG@.VCfg.MAX_PAGE) maxPage = pg;
    if (s > maxSlot && s < @PKG@.VCfg.MAX_CAP) maxSlot = s;
  }
  int cap = @PKG@.VCfg.SLOTS;
  if (maxSlot + 1 > cap) cap = maxSlot + 1;
  @PKG@.VData d = new @PKG@.VData(u, cap);
  String nm = @PKG@.VCodec.strOf(doc, "name");
  d.name = nm == null ? "" : nm;
  int pages = @PKG@.VCodec.intOf(doc, "pages", @PKG@.VCfg.FREE_PAGES);
  if (pages < @PKG@.VCfg.FREE_PAGES) pages = @PKG@.VCfg.FREE_PAGES;
  if (pages < maxPage) pages = maxPage;
  if (pages > @PKG@.VCfg.MAX_PAGE) pages = @PKG@.VCfg.MAX_PAGE;
  d.unlocked = pages;
  d.page(pages);
  for (int i = 0; i < content.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) content.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument pd = v.asDocument();
    int pg = @PKG@.VCodec.intOf(pd, "page", 0);
    org.bson.BsonArray sl = pd.getArray("slots", new org.bson.BsonArray());
    for (int k = 0; k < sl.size(); k++) {
      org.bson.BsonValue sv = (org.bson.BsonValue) sl.get(k);
      if (sv == null || !sv.isDocument()) continue;
      String bid = @PKG@.VCodec.strOf(sv.asDocument(), "id");
      if (@PKG@.VCodec.btnId(bid)) { strayFile(u, pg, @PKG@.VCodec.intOf(sv.asDocument(), "slot", -1), bid); continue; }
      place(d, pg, sv.asDocument());
    }
  }
  for (int i = 0; i < orph.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) orph.get(i);
    if (v == null || !v.isDocument()) continue;
    String bid = @PKG@.VCodec.strOf(v.asDocument(), "id");
    if (@PKG@.VCodec.btnId(bid)) { strayFile(u, @PKG@.VCodec.intOf(v.asDocument(), "page", 0), @PKG@.VCodec.intOf(v.asDocument(), "slot", -1), bid); continue; }
    place(d, @PKG@.VCodec.intOf(v.asDocument(), "page", 0), v.asDocument());
  }
  return d;
}""")
# first use: missing file = a fresh vault (no file is written until something changes); unreadable file = null (vault stays shut,
# never cached, re-read on the next try, never overwritten)
M(sto, r"""
public static synchronized @PKG@.VData loadLocked(java.util.UUID u) {
  Object c = CACHE.get(u);
  if (c != null) return (@PKG@.VData) c;
  java.nio.file.Path f = fileOf(u);
  @PKG@.VData d = null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      d = new @PKG@.VData(u, @PKG@.VCfg.SLOTS);
      d.unlocked = @PKG@.VCfg.FREE_PAGES;
      d.page(d.unlocked);
    } else {
      d = fromDoc(u, org.bson.BsonDocument.parse(@PKG@.VCfg.readText(f)));
    }
  } catch (Throwable t) {
    @PKG@.VCfg.warnOnce("read-" + u, "vault file " + f + " cannot be read - that vault stays shut and the file is not touched until it reads again: " + t);
    return null;
  }
  if (d == null) return null;
  CACHE.put(u, d);
  return d;
}""")
M(sto, r"""
public static @PKG@.VData load(java.util.UUID u) {
  if (u == null) return null;
  Object c = CACHE.get(u);
  if (c != null) return (@PKG@.VData) c;
  return loadLocked(u);
}""")

# ---- VData methods that need VStore.toDoc (synchronized instance methods: no synchronized blocks)
M(dat, r"""
public synchronized Object[] snap() {
  return new Object[] { @PKG@.VStore.toDoc(this), Long.valueOf(this.rev) };
}""")
M(dat, r"""
public synchronized Object[] unlockTo(int next) {
  if (this.unlocked != next - 1) return null;
  this.unlocked = next;
  page(next);
  this.rev = this.rev + 1L;
  return snap();
}""")
M(dat, r"""
public synchronized boolean relock(int next) {
  if (this.unlocked != next || used(next) > 0) return false;
  this.unlocked = next - 1;
  this.rev = this.rev + 1L;
  return true;
}""")
M(dat, r"""
public synchronized Object[] setUnlocked(int n) {
  this.unlocked = n;
  page(n);
  this.rev = this.rev + 1L;
  return snap();
}""")

# ---- file writes: ordered by revision under the per-vault IO lock (an older snapshot never overwrites a newer file)
M(sto, r"""
public static boolean write0(@PKG@.VData d, org.bson.BsonDocument doc, long r) {
  if (r <= d.writtenRev) return true;
  java.nio.file.Path f = fileOf(d.owner);
  try {
    int want = @PKG@.VCodec.countSlots(doc);
    @PKG@.VCfg.atomicWrite(f, @PKG@.VCodec.toJson(doc).getBytes("UTF-8"));
    org.bson.BsonDocument back = org.bson.BsonDocument.parse(@PKG@.VCfg.readText(f));
    if (@PKG@.VCodec.countSlots(back) != want) { @PKG@.VCfg.warn("vault file " + f + " did not read back correctly (kept in memory, retrying)"); return false; }
    d.writtenRev = r;
    return true;
  } catch (Throwable t) {
    @PKG@.VCfg.warnOnce("write-" + d.owner, "could not write vault file " + f + " (kept in memory, retrying): " + t);
    return false;
  }
}""")
M(sto, r"""
public static boolean writeDoc(@PKG@.VData d, org.bson.BsonDocument doc, long r) {
  synchronized (d.ioLock) {
    return write0(d, doc, r);
  }
}""")
F(sjob, "public java.util.UUID owner;")
C(sjob, "public VSaveJob(java.util.UUID o) { this.owner = o; }")
sjob.addInterface(pool.get("java.lang.Runnable"))
M(sto, r"""
public static void retryLater(java.util.UUID u) {
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) return;
  if (PENDING.putIfAbsent(u, Boolean.TRUE) != null) return;
  try { ex.schedule(new @PKG@.VSaveJob(u), 5000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { PENDING.remove(u); }
}""")
M(sto, r"""
public static void saveJob(java.util.UUID u) {
  PENDING.remove(u);
  @PKG@.VData d = (@PKG@.VData) CACHE.get(u);
  if (d == null) return;
  if (d.rev == d.writtenRev) return;
  Object[] sn = d.snap();
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) { log("WRITE-FAIL " + u + " rev " + sn[1] + " (kept in memory, retrying in 5 s)"); retryLater(u); }
}""")
M(sto, r"""
public static void saveSoon(java.util.UUID u, long delay) {
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveJob(u); return; }
  try {
    if (delay <= 0L) { ex.execute(new @PKG@.VSaveJob(u)); return; }
    if (PENDING.putIfAbsent(u, Boolean.TRUE) != null) return;
    ex.schedule(new @PKG@.VSaveJob(u), delay, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { PENDING.remove(u); saveJob(u); }
}""")
M(sto, r"""
public static void saveNames() {
  try {
    NAMES_DIRTY = false;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = NAMES.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), (String) e.getValue());
    }
    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    p.store(bo, "SkyyVault: lower-case player name = uuid (for /vaultadmin with offline players)");
    @PKG@.VCfg.atomicWrite(@PKG@.VCfg.NAMESF, bo.toByteArray());
  } catch (Throwable t) { NAMES_DIRTY = true; @PKG@.VCfg.warnOnce("names", "could not write names.properties: " + t); }
}""")
M(sjob, r"""
public void run() {
  try {
    if (this.owner == null) @PKG@.VStore.saveNames();
    else @PKG@.VStore.saveJob(this.owner);
  } catch (Throwable t) { @PKG@.VCfg.warn("vault save job failed: " + t); }
}""")
M(sto, r"""
public static void flushAll() {
  java.util.Iterator it = CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.VData d = (@PKG@.VData) it.next();
    try {
      if (d.rev != d.writtenRev) {
        Object[] sn = d.snap();
        if (!writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue())) log("SHUTDOWN-WRITE-FAIL " + d.owner + " rev " + sn[1]);
      }
    } catch (Throwable t) { @PKG@.VCfg.warn("vault flush failed for " + d.owner + ": " + t); }
  }
  if (NAMES_DIRTY) saveNames();
}""")
M(sto, r"""
public static void loadNames() {
  try {
    if (!java.nio.file.Files.exists(@PKG@.VCfg.NAMESF, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(@PKG@.VCfg.NAMESF, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); NAMES.put(k, p.getProperty(k)); }
  } catch (Throwable t) { @PKG@.VCfg.warn("names.properties could not be read: " + t); }
}""")
M(sto, r"""
public static void noteName(@PKG@.VData d, String name) {
  if (d == null || name == null || name.length() == 0 || name.equals(d.name)) return;
  d.name = name;
  NAMES.put(name.toLowerCase(), d.owner.toString());
  NAMES_DIRTY = true;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveNames(); return; }
  try { ex.execute(new @PKG@.VSaveJob((java.util.UUID) null)); } catch (Throwable t) { }
}""")
M(sto, r"""
public static java.util.UUID resolve(String who) {
  if (who == null) return null;
  String w = who.trim();
  if (w.length() == 0) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.getUsername() != null && p.getUsername().equalsIgnoreCase(w)) return p.getUuid();
    }
  } catch (Throwable t) { }
  try { return java.util.UUID.fromString(w); } catch (Throwable t) { }
  Object s = NAMES.get(w.toLowerCase());
  if (s instanceof String) { try { return java.util.UUID.fromString((String) s); } catch (Throwable t) { } }
  return null;
}""")
# 0.1.3 (LOCKED Skyy 2026-09-25): no 10 s second click any more (0.1.2's buyKey / confirm / armed / disarm are gone). ONE rule for the
# gold arrow in the vault window, the page's Buy button and /vault buy: a price below VCfg.BUY_CONFIRM (buyConfirmCoins, default 50000)
# buys at once, a price at or above it opens the VBuyDlg confirm window ("Buy page X for Y coins?", Buy / Cancel). Never charged twice:
#   * VStore.buy takes an EXPECTED page number (the page the click / window / command offered): it only buys when that is exactly the
#     next page, so a window for page 5 never buys page 6 and a second confirm of page 5 finds it already owned (nothing charged);
#   * one purchase at a time per player (BUYING), so no two threads can both take coins for one page;
#   * BUY_GUARD_MS (1.5 s) after a purchase every buy CLICK or COMMAND of that player is refused with a chat line (a double click on
#     the gold arrow / Buy button, or a shift-click that reaches the server as two packets, buys one page, never two). The confirm
#     window's own Buy button is not guarded (it is the confirmation), but it is one-shot (VBuyDlg.done) and page-bound (expected page).
M(sto, r"""
public static boolean needsConfirm(long cost) {
  return cost >= @PKG@.VCfg.BUY_CONFIRM;
}""")
M(sto, r"""
public static String guard(java.util.UUID u, @PKG@.VData d) {
  Object t = LASTBUY.get(u);
  if (!(t instanceof Long)) return null;
  long ago = System.currentTimeMillis() - ((Long) t).longValue();
  if (ago < 0L || ago >= @PKG@.VCfg.BUY_GUARD_MS) return null;
  return "-You just bought vault page " + d.unlocked + " - nothing more was charged. Wait a moment, then buy page " + (d.unlocked + 1) + " if you want it.";
}""")
M(sto, r"""
public static void pruneBuys(long now) {
  java.util.Iterator it = LASTBUY.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || now - ((Long) v).longValue() > 60000L) it.remove();
  }
}""")
M(sto, r"""
public static String refund(java.util.UUID u, long cost) {
  if (cost <= 0L) return "";
  Object add = @PKG@.VCfg.bridge().get("coins:fn:add");
  Object r = null;
  try { if (add instanceof java.util.function.Function) r = ((java.util.function.Function) add).apply(new Object[] { u, Long.valueOf(cost) }); } catch (Throwable t) { r = null; }
  if (r instanceof Long) { log("REFUND " + u + " " + cost); return " Your " + grp(cost) + " coins were refunded."; }
  log("REFUND-ERROR " + u + " " + cost + " coins could not be refunded - give them back by hand");
  @PKG@.VCfg.warn("REFUND-ERROR: " + cost + " coins for " + u + " could not be refunded (see vault.log)");
  return " The refund failed - an admin has been told (vault.log).";
}""")
# buy page `expect` (it must be the next page): coins first (must be TRUE), then the page, written and read back; a failed write reverts
# + refunds (the 0.1.2 body). The caller holds BUYING for this player (buyAt() below). shown = the price the confirm window showed
# (-1 = no window): when an admin changed the price while the window was open, nothing is charged (the player never pays a price the
# window did not name).
M(sto, r"""
public static String buy0(java.util.UUID u, String name, int expect, long shown, @PKG@.VData d) {
  int next = d.unlocked + 1;
  if (expect > 0 && expect < next) return "-Vault page " + expect + " is already yours - nothing was charged.";
  if (expect > next) return "-Buy vault page " + next + " first - nothing was charged.";
  if (next > @PKG@.VCfg.MAX_PAGES) return "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ").";
  if (@PKG@.VCfg.bridge().get("profile:busy:" + u) != null) return "-Your profile is still loading - try again in a moment. Nothing was charged.";
  long cost = price(next);
  if (shown >= 0L && cost != shown) return "-The price of vault page " + next + " changed to " + grp(cost) + " coins - nothing was charged. Click Buy again to see the new price.";
  if (cost > 0L) {
    Object take = @PKG@.VCfg.bridge().get("coins:fn:take");
    if (!(take instanceof java.util.function.Function)) return "-Coins are not available on this server (SkyyCoins is missing) - nothing changed.";
    Object r = null;
    try { r = ((java.util.function.Function) take).apply(new Object[] { u, Long.valueOf(cost) }); } catch (Throwable t) { r = null; }
    if (r == null) return "-Your purse could not be read right now - nothing was charged.";
    if (!Boolean.TRUE.equals(r)) return "-Vault page " + next + " costs " + grp(cost) + " coins - you do not have enough.";
  }
  Object[] sn = d.unlockTo(next);
  if (sn == null) return "-Your vault changed while buying - nothing bought." + refund(u, cost);
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) {
    boolean back = d.relock(next);
    saveSoon(u, 0L);
    log("BUY-FAIL " + u + " " + name + " page " + next + " cost " + cost + (back ? " (page taken back)" : " (page kept - it already held items)"));
    if (!back) { LASTBUY.put(u, Long.valueOf(System.currentTimeMillis())); return "+Bought vault page " + next + " - the file will be saved on the next try."; }
    return "-The vault file could not be saved - page " + next + " was not bought." + refund(u, cost);
  }
  LASTBUY.put(u, Long.valueOf(System.currentTimeMillis()));
  log("BUY " + u + " " + name + " page " + next + " cost " + cost);
  return "+Bought vault page " + next + " for " + grp(cost) + " coins - you now own " + next + " of " + @PKG@.VCfg.MAX_PAGES + " pages.";
}""")
# expect = the page number the click / window / command offered (0 = whatever page is next); shown = the price the confirm window
# named (-1 = none). One purchase at a time per player.
M(sto, r"""
public static String buyAt(java.util.UUID u, String name, int expect, long shown) {
  if (u == null) return "-Could not tell who is buying - nothing was charged.";
  @PKG@.VData d = load(u);
  if (d == null) return "-Your vault file cannot be read - nothing was charged. Please tell an admin.";
  if (BUYING.putIfAbsent(u, Boolean.TRUE) != null) return "-A vault page purchase is already running - nothing more was charged.";
  try {
    return buy0(u, name, expect, shown, d);
  } finally {
    BUYING.remove(u);
  }
}""")
M(sto, r"""
public static String buy(java.util.UUID u, String name, int expect) {
  return buyAt(u, name, expect, -1L);
}""")
# the ONE entry of every buy click / command (gold arrow, page Buy button, /vault buy): "?<page>" = open the confirm window for that
# page (nothing charged yet); anything else is the result line ("+" bought at once, "-" refused, nothing charged).
M(sto, r"""
public static String intent(java.util.UUID u, String name, int expect) {
  if (u == null) return "-Could not tell who is buying - nothing was charged.";
  @PKG@.VData d = load(u);
  if (d == null) return "-Your vault file cannot be read - nothing was charged. Please tell an admin.";
  int next = d.unlocked + 1;
  if (next > @PKG@.VCfg.MAX_PAGES) return "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ").";
  if (expect > 0 && expect < next) return "-Vault page " + expect + " is already yours - nothing was charged.";
  if (expect > next) return "-Buy vault page " + next + " first - nothing was charged.";
  String g = guard(u, d);
  if (g != null) return g;
  if (needsConfirm(price(next))) return "?" + next;
  return buy(u, name, next);
}""")
M(sto, r"""
public static String setPages(String admin, java.util.UUID u, int n, int viewing) {
  @PKG@.VData d = load(u);
  if (d == null) return "-That vault file cannot be read (it was not touched).";
  if (n < 1 || n > @PKG@.VCfg.MAX_PAGE) return "-Pages must be 1 to " + @PKG@.VCfg.MAX_PAGE + ".";
  int hi = d.highestUsed();
  if (n < hi) return "-Page " + hi + " still holds items - it cannot be removed (items are never hidden).";
  if (viewing > n) return "-" + nameOf(d) + " is looking at vault page " + viewing + " right now - try again when they close it.";
  int old = d.unlocked;
  Object[] sn = d.setUnlocked(n);
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) retryLater(u);
  log("SETPAGES " + admin + " " + u + " " + old + " -> " + n + (ok ? "" : " (write failed - retrying)"));
  return "+" + nameOf(d) + " now owns " + n + " vault pages (was " + old + ").";
}""")
M(sto, r"""
public static String[] infoLines(java.util.UUID u, int viewing, boolean admin) {
  @PKG@.VData d = load(u);
  if (d == null) return new String[] { "-That vault file cannot be read - nothing in it was changed. " + (admin ? "Check the server log." : "Please tell an admin.") };
  java.util.ArrayList out = new java.util.ArrayList();
  int max = d.unlocked > @PKG@.VCfg.MAX_PAGES ? d.unlocked : @PKG@.VCfg.MAX_PAGES;
  int per = @PKG@.VCfg.usable(d.cap);
  out.add("=" + (admin ? "Vault of " + nameOf(d) + " (" + d.owner + ")" : "Your vault") + ": " + d.unlocked + " of " + max + " pages, " + per + " slots each, " + d.total() + " stacks - shared by all profiles.");
  StringBuilder sb = new StringBuilder();
  for (int p = 1; p <= d.unlocked; p++) {
    if (sb.length() > 0) sb.append("  |  ");
    sb.append("Page ").append(p).append(": ").append(d.used(p)).append("/").append(per);
    if (p == viewing) sb.append(" (open)");
    if (p % 5 == 0 || p == d.unlocked) { out.add("=" + sb.toString()); sb = new StringBuilder(); }
  }
  if (d.orphans.size() > 0) out.add("-" + d.orphans.size() + " stack(s) belong to items this server does not have right now - kept safe in the file" + (admin ? " (orphans)." : ", tell an admin."));
  if (d.unlocked < @PKG@.VCfg.MAX_PAGES) out.add("=Next page (" + (d.unlocked + 1) + ") costs " + grp(price(d.unlocked + 1)) + " coins" + (admin ? "." : " - /vault buy"));
  if (!admin) out.add("=/vault opens it, /vault 2 opens page 2, /vault next | prev switch pages, /vault pages shows the page buttons." + (@PKG@.VCfg.ARROWS ? " The arrows in the vault window turn pages too. Shift-click one, or press Drop on it, to turn at once." : ""));
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")

# ================= VThreads: daemon saver thread =================
thf.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
C(thf, "public VThreads() { }")
M(thf, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyVault-saver");
  t.setDaemon(true);
  return t;
}""")

# ================= VSession: one open (editable) view of a vault =================
for f in ("public java.util.UUID owner;", "public java.util.UUID viewer;", "public @PR@ pr;", "public int page;", "public int mode;",
          "public @SIC@ view;", "public @PKG@.VWindow window;", "public @EREG@ reg;", "public volatile boolean closed;",
          "public volatile boolean swapping;", "public volatile boolean noSync;", "public Object epoch;", "public Object pageObj;",
          "public long askedClose;", "public int offline;",
          # 0.1.2 page arrows. layout 0 = none (0.1.1 container), 1 = extra control row, 2 = inside the page. store = storage size
          # S (VData.cap); base = first control index (row: S; inside: the Prev slot); span = indices base..base+span-1 covered by
          # ctrl / live (row: padding + control row; inside: Prev..Next, only those two are controls); ctrl = the canonical stack
          # per covered index (null = none); live = that index holds our button on this page (inside: false while a stored item
          # blocks it); usable = storage slots offered on this page (labels). Hit fields are guarded by the VSession monitor.
          "public int layout;", "public int store;", "public int base;", "public int span;", "public int prevIdx;",
          "public int infoIdx;", "public int nextIdx;", "public int usable;", "public long sid;",
          "public volatile @IS@[] ctrl;", "public volatile boolean[] live;",
          "public int hitMask;", "public boolean batchQueued;", "public boolean batchChanged;", "public boolean inBatch;",
          # 0.1.2 review: System.nanoTime() of the last storage change (0 = none yet), see noteHit
          "public long lastChg;"):
    F(ses, f)
C(ses, r"""
public VSession() {
  this.page = 1; this.mode = 1; this.closed = false; this.swapping = false; this.noSync = false;
  this.epoch = null; this.pageObj = null; this.askedClose = 0L; this.offline = 0;
  this.layout = 0; this.store = 0; this.base = 0; this.span = 0; this.prevIdx = -1; this.infoIdx = -1; this.nextIdx = -1;
  this.usable = 0; this.sid = 0L; this.ctrl = new @IS@[0]; this.live = new boolean[0];
  this.hitMask = 0; this.batchQueued = false; this.batchChanged = false; this.inBatch = false; this.lastChg = 0L;
}""")
M(ses, r"""
public synchronized boolean close1() {
  if (this.closed) return false;
  this.closed = true;
  return true;
}""")
# 0.1.2 click batching (VBtnFilter.test -> noteHit; VSessions.onChange -> noteChanged; VBtnTask -> takeHits). true = the caller queues
# the ONE batch task of this batch (the first hit or stray of a batch).
# 0.1.2 review: a batch also counts as "storage changed" when storage changed in the last 100 ms BEFORE its first hit. The engine's
# bulk actions (Take All, merge-stack) walk the slots in index order inside ONE server call, so storage moves at lower indices land
# microseconds before the first refused control slot; with arrowLayout=inside and only one live arrow (the other blocked, vault full)
# such a Take All would otherwise look like a single click and turn the page. A player cannot move an item and then click an arrow
# within 100 ms; if two packets arrive bunched that closely, the click is only ignored (the arrow snaps back, click again).
M(ses, r"""
public boolean recentChg() {
  if (this.lastChg == 0L) return false;
  long d = System.nanoTime() - this.lastChg;
  return d >= 0L && d < 100000000L;
}""")
M(ses, r"""
public synchronized boolean noteHit(int slot) {
  int b = slot - this.base;
  if (b >= 0 && b < 31) this.hitMask = this.hitMask | (1 << b);
  if (this.batchQueued) return false;
  this.batchQueued = true;
  this.batchChanged = recentChg();
  return true;
}""")
M(ses, r"""
public synchronized boolean wantBatch() {
  if (this.batchQueued) return false;
  this.batchQueued = true;
  this.batchChanged = recentChg();
  return true;
}""")
M(ses, r"""
public synchronized void noteChanged() {
  if (this.batchQueued) this.batchChanged = true;
  long t = System.nanoTime();
  this.lastChg = t == 0L ? 1L : t;
}""")
# low 32 bits = hit mask (bit i = slot base + i), bit 32 = storage changed during the batch; clears the batch
M(ses, r"""
public synchronized long takeHits() {
  long r = ((long) this.hitMask) & 0xFFFFFFFFL;
  if (this.batchChanged) r = r | (1L << 32);
  this.hitMask = 0;
  this.batchChanged = false;
  this.batchQueued = false;
  return r;
}""")
M(ses, r"""
public synchronized void clearQueued() {
  this.hitMask = 0;
  this.batchChanged = false;
  this.batchQueued = false;
}""")
# true = index `slot` holds our button on the page shown (touches no container: called from the slot filter)
M(ses, r"""
public boolean ctrlLive(int slot) {
  boolean[] lv = this.live;
  int b = slot - this.base;
  if (this.layout == 0 || lv == null || b < 0 || b >= lv.length) return false;
  return lv[b];
}""")
M(ses, r"""
public boolean isStorage(int slot) {
  if (slot < 0 || slot >= this.store) return false;
  return !ctrlLive(slot);
}""")

# ================= VChange / VWindow constructors (bodies that call VSessions come later) =================
chg.addInterface(pool.get("java.util.function.Consumer"))
F(chg, "public @PKG@.VSession sess;")
C(chg, "public VChange(@PKG@.VSession s) { this.sess = s; }")
win.addInterface(pool.get(T["VWIN"]))
F(win, "public @PKG@.VSession sess;")
C(win, "public VWindow(@IC@ c, @PKG@.VSession s) { super(c); this.sess = s; }")
# 0.1.5 fix (found by SkyyVault/test_skyyvault_0.1.5.py): Window.invalidate() is PROTECTED, so 0.1.2-0.1.4's VSessions.resync call
# s.window.invalidate() (from a class that is not a Window) threw IllegalAccessError at run time - swallowed by its catch, so the click
# batch never re-sent the vault window after a refused arrow move. A subclass may call its own protected invalidate(): the engine then
# sends one UpdateWindow on its next window tick (WindowManager.updateWindows -> consumeIsDirty), exactly what it does after every
# successful container change (WindowManager.markWindowChanged).
M(win, "public void resend() { invalidate(); }")

# ================= 0.1.2 VBtn: the page-arrow items (research/Vault-Arrows-Spec.md 4.1) =================
# Kinds (an int, no String switch): 1 PREV, 2 PREV_OFF, 3 NEXT, 4 BUY, 5 NEXT_OFF, 6 INFO, 7 FILLER. IDS[kind] = the item id shipped in
# this jar's asset pack. Every canonical stack = new ItemStack(id, 1) + marker "SkyyVaultBtn" {k: kind, o: owner uuid, s: window
# serial} + ItemDisplayMetadata (per-stack tooltip name / description, the SkyyRolls 0.1.3+ method).
BTN_IDS = ["", "Skyy_Vault_Prev", "Skyy_Vault_PrevOff", "Skyy_Vault_Next", "Skyy_Vault_Buy", "Skyy_Vault_NextOff", "Skyy_Vault_Info",
           "Skyy_Vault_Filler"]
for f in ("public static final String MARK = \"SkyyVaultBtn\";", "public static final int PREV = 1;", "public static final int PREV_OFF = 2;",
          "public static final int NEXT = 3;", "public static final int BUY = 4;", "public static final int NEXT_OFF = 5;",
          "public static final int INFO = 6;", "public static final int FILLER = 7;",
          "public static final String C_ARROW = \"#7cc4ff\";", "public static final String C_OFF = \"#9aa3ad\";",
          "public static final String C_GOLD = \"#ffc94a\";", "public static final String C_TEXT = \"#cfe3ff\";",
          "public static final String C_DIM = \"#7f8ea6\";"):
    F(btn, f)
F(btn, "public static final String[] IDS = %s;" % jarr(BTN_IDS))
M(btn, r"""
public static boolean isButton(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  return @PKG@.VCodec.btnId(s.getItemId());
}""")
M(btn, r"""
public static org.bson.BsonDocument mark(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    org.bson.BsonDocument m = s.getMetadata();
    if (m == null) return null;
    org.bson.BsonValue v = (org.bson.BsonValue) m.get(MARK);
    if (v == null || !v.isDocument()) return null;
    return v.asDocument();
  } catch (Throwable t) { return null; }
}""")
M(btn, r"""
public static int kindOf(@IS@ s) {
  org.bson.BsonDocument d = mark(s);
  if (d == null) return 0;
  return @PKG@.VCodec.intOf(d, "k", 0);
}""")
M(btn, r"""
public static long sidOf(@IS@ s) {
  org.bson.BsonDocument d = mark(s);
  if (d == null) return -1L;
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get("s"); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return -1L;
}""")
# the view slot v holds exactly the canonical stack w (item id, quantity, marker kind and window serial)
M(btn, r"""
public static boolean same(@IS@ v, @IS@ w) {
  if (w == null) return v == null || v.isEmpty();
  if (v == null || v.isEmpty()) return false;
  if (!v.getItemId().equals(w.getItemId()) || v.getQuantity() != w.getQuantity()) return false;
  return kindOf(v) == kindOf(w) && sidOf(v) == sidOf(w);
}""")
M(btn, r"""
public static @MSG@ lines(String[] ls) {
  @MSG@ m = @MSG@.empty();
  for (int i = 0; i < ls.length; i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    m.insert(@MSG@.raw(ls[i]).color(i == 0 ? C_TEXT : C_DIM));
  }
  return m;
}""")
M(btn, r"""
public static @IS@ make(int kind, String name, String ncol, String[] desc, java.util.UUID owner, long sid) {
  @IS@ s = new @IS@(IDS[kind], 1);
  org.bson.BsonDocument mk = new org.bson.BsonDocument();
  mk.put("k", new org.bson.BsonInt32(kind));
  mk.put("o", new org.bson.BsonString(owner == null ? "" : owner.toString()));
  mk.put("s", new org.bson.BsonInt64(sid));
  s = s.withMetadata(MARK, (org.bson.BsonValue) mk);
  try {
    @MSG@ nm = @MSG@.raw(name).color(ncol);
    @MSG@ ds = (desc == null || desc.length == 0) ? (@MSG@) null : lines(desc);
    s = s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(nm, ds));
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("btn-disp", "a vault arrow tooltip could not be set (the arrow still works, it shows its plain name): " + t); }
  return s;
}""")
# the canonical control row of page `page` for session s (s.ctrl / s.live / s.usable). recompute = decide which covered indices are
# live controls from src (the page's stored stacks; inside: a reserved slot that still holds an item is NOT live); false = keep s.live
# (a redraw of the page on screen). Texts follow the vault's CURRENT state, so every rebuild is up to date.
M(btn, r"""
public static void row(@PKG@.VSession s, @PKG@.VData d, int page, @IS@[] src, boolean recompute) {
  int n = s.span;
  @IS@[] c = new @IS@[n < 0 ? 0 : n];
  boolean[] lv = s.live;
  if (recompute || lv == null || lv.length != c.length) {
    lv = new boolean[c.length];
    for (int i = 0; i < c.length; i++) {
      int slot = s.base + i;
      if (s.layout == 1) lv[i] = true;
      else if (s.layout == 2 && (slot == s.prevIdx || slot == s.nextIdx)) lv[i] = src == null || slot >= src.length || src[slot] == null || src[slot].isEmpty();
      else lv[i] = false;
    }
  }
  if (s.layout == 0 || c.length == 0) { s.usable = s.store; s.ctrl = c; s.live = lv; return; }
  int unlocked = d.unlocked;
  int max = unlocked > @PKG@.VCfg.MAX_PAGES ? unlocked : @PKG@.VCfg.MAX_PAGES;
  int usable = s.store;
  if (s.layout == 2) {
    if (lv[s.prevIdx - s.base]) usable--;
    if (lv[s.nextIdx - s.base]) usable--;
  }
  s.usable = usable;
  int used = d.used(page);
  String here = "You are on page " + page + " of " + unlocked + " - " + used + " of " + usable + " slots used.";
  boolean inside = s.layout == 2;
  // 0.1.5 (Skyy 2026-09-30 "arrow button works, but not when i click it, i have to set it back down"): every live arrow says HOW to
  // press it. The client lifts an item on a plain click and tells the server only at the put-down (research/Vault-Arrow-Click-
  // Research.md), so shift-click (Transfer) and the Drop key are the instant gestures; a plain click acts at the put-down.
  String how2 = "Your Drop key on it works too.";
  String how3 = "A plain click lifts it - the page turns when you put it back.";
  @IS@ prev = null;
  if (page > 1) prev = make(PREV, "< Page " + (page - 1), C_ARROW, inside ? new String[] { "Shift-click to turn to page " + (page - 1) + " of " + unlocked + " at once.", how2, how3, here } : new String[] { "Shift-click to turn to page " + (page - 1) + " of " + unlocked + " at once.", how2, how3 }, s.owner, s.sid);
  else prev = make(PREV_OFF, "First page", C_OFF, inside ? new String[] { here } : new String[] { "You are on page 1 of " + unlocked + "." }, s.owner, s.sid);
  @IS@ next = null;
  if (page < unlocked) {
    next = make(NEXT, "Page " + (page + 1) + " >", C_ARROW, inside ? new String[] { "Shift-click to turn to page " + (page + 1) + " of " + unlocked + " at once.", how2, how3, here } : new String[] { "Shift-click to turn to page " + (page + 1) + " of " + unlocked + " at once.", how2, how3 }, s.owner, s.sid);
  } else if (unlocked < @PKG@.VCfg.MAX_PAGES) {
    int nx = unlocked + 1;
    long cost = @PKG@.VStore.price(nx);
    String nm = cost > 0L ? "Buy page " + nx : "Unlock page " + nx + " - free";
    String l1 = cost > 0L ? @PKG@.VStore.grp(cost) + " coins from your active profile." : "Free - no coins needed.";
    // 0.1.3: buyConfirmCoins decides what one click does (at once below it, a confirm window at or above it); 0.1.5: the gestures
    boolean ask = @PKG@.VStore.needsConfirm(cost);
    String l2 = ask ? "Shift-click - a window asks you to confirm." : (cost > 0L ? "Shift-click to buy it at once." : "Shift-click to unlock it at once.");
    String l3 = ask ? "A plain click lifts it - the window opens when you put it back." : (cost > 0L ? "A plain click lifts it - it buys when you put it back." : "A plain click lifts it - it unlocks when you put it back.");
    next = make(BUY, nm, C_GOLD, inside ? new String[] { l1, l2, how2, l3, here } : new String[] { l1, l2, how2, l3 }, s.owner, s.sid);
  } else {
    next = make(NEXT_OFF, "Last page", C_OFF, inside ? new String[] { "You own every vault page (" + unlocked + " of " + max + ").", here } : new String[] { "You own every vault page (" + unlocked + " of " + max + ")." }, s.owner, s.sid);
  }
  @IS@ info = null;
  @IS@ fill = null;
  if (!inside) {
    info = make(INFO, "Page " + page + " of " + unlocked, C_GOLD, new String[] { "" + used + " of " + usable + " slots used", "Shared by all your profiles", "/vault <page> jumps to a page", "Arrows: shift-click one, or press your Drop key on it, to turn at once.", "A plain click lifts an arrow - the page turns when you put it back." }, s.owner, s.sid);
    fill = make(FILLER, "Vault", C_DIM, (String[]) null, s.owner, s.sid);
  }
  for (int i = 0; i < c.length; i++) {
    if (!lv[i]) continue;
    int slot = s.base + i;
    if (slot == s.prevIdx) c[i] = prev;
    else if (slot == s.nextIdx) c[i] = next;
    else if (slot == s.infoIdx) c[i] = info;
    else c[i] = fill;
  }
  s.ctrl = c;
  s.live = lv;
}""")

# ================= 0.1.2 VView: the container of a window with arrows =================
# Engine fact (HytaleServer.jar bytecode, this build pass): ItemContainer.internal_moveItemStackFromSlot(slot, [qty,] to, allOrNothing,
# filter) - the "move this slot into that container" primitive behind shift-click (InventoryUtils.smartMoveItem) and the chest's
# Take All (takeAllWithPriority -> moveItemFromCheckToInventory) - returns NULL when cantRemoveFromSlot(slot) is true, and the public
# wrapper then calls sendUpdate(null): a NullPointerException ("Failed to run task!" SEVERE in the server log), and Take All stops at
# that slot. The slot-to-slot move (drag / put down) and the drop key return a proper failed transaction. VView answers a refused
# whole-slot move with the same failed MoveTransaction the engine builds for its own cantMoveToSlot refusal, so shift-click and Take
# All run to the end, and every control slot they touch still reaches VBtnFilter (hits). Allowed moves go to the engine unchanged.
C(vv, "public VView(short cap) { super(cap); }")
M(vv, r"""
public @MT@ refused(short slot, @IC@ to, boolean filter) {
  @IS@ cur = getItemStack(slot);
  @STX@ rm = new @STX@(false, @ACT@.REMOVE, slot, cur, cur, (@IS@) null, false, false, filter);
  return new @MT@(false, rm, @MVT@.MOVE_FROM_SELF, to, @ISX@.FAILED_ADD);
}""")
M(vv, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, to, allOrNothing, filter);
}""")
M(vv, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, int qty, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, qty, to, allOrNothing, filter);
}""")

# ================= 0.1.2 VBtnFilter / VBtnTask / VSweepTask constructors (bodies that call VSessions come later) =================
bfl.addInterface(pool.get(T["SF"]))
F(bfl, "public @PKG@.VSession sess;")
C(bfl, "public VBtnFilter(@PKG@.VSession s) { this.sess = s; }")
# both tasks carry the world they were queued on: a player who changed worlds meanwhile is never touched from the old world's thread
btk.addInterface(pool.get("java.lang.Runnable"))
F(btk, "public @PKG@.VSession sess;")
F(btk, "public java.util.UUID wu;")
C(btk, "public VBtnTask(@PKG@.VSession s, java.util.UUID wu) { this.sess = s; this.wu = wu; }")
swt.addInterface(pool.get("java.lang.Runnable"))
F(swt, "public @PR@ pr;")
F(swt, "public String why;")
F(swt, "public java.util.UUID wu;")
F(swt, "public int tries;")
C(swt, "public VSweepTask(@PR@ pr, String why, java.util.UUID wu, int tries) { this.pr = pr; this.why = why; this.wu = wu; this.tries = tries; }")

# ================= VaultPage part 1 (0.1.3 logic; 0.1.4 look = the vanilla UI kit tools/skyyui.py; inline, rebuilt only after a click; never periodic updates) =================
# 0.1.3: offer = the page number the Buy button showed at the last build (0 = none): a click buys exactly that page or nothing
for f in ("public @PKG@.VSession sess;", "public int sel;", "public String info;", "public int offer;"):
    F(page, f)
C(page, r"""
public VaultPage(@PR@ pr, @PKG@.VSession s, int sel) {
  super(pr, @LIFE@.CanDismiss);
  this.sess = s; this.sel = sel < 1 ? 1 : sel; this.info = ""; this.offer = 0;
}""")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 / SkyyGuilds 0.1 jsonStr)
M(page, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# 0.1.4: the result-line helpers are the kit's (same names and signatures as 0.1.3): colorOf picks the vanilla colour by the mark
# ("+" success #39f493, "-" error #ff6b6b, "=" SUI.STATUS["="] = the vanilla info blue #7caacc, none = the label grey #96a9be),
# textOf strips the mark (same result as 0.1.3's textOf for every input).
for _src in SUI.java_status_methods("colorOf", "textOf"):
    M(page, _src)
M(page, r"""
public void refreshWith(String res) {
  if (this.sess != null && !this.sess.closed) this.sel = this.sess.page;
  this.info = res == null ? "" : res;
  rebuild();
}""")
M(page, r"""
public void refresh() {
  refreshWith((String) null);
}""")
# ---- 0.1.4: VaultPage's LOOK from the vanilla UI kit (tools/skyyui.py; research/Vanilla-UI-Style-Guide.md sections 7 + 13). ----
# vault_page() builds every piece of the page with kit calls when this script runs (every value proven by SUI.verify() above), runs
# both page states (the vault, the unreadable-file view) through SUI.check_page, SUI.assert_proven (only properties deployed pages
# already use: no FlexWeight, WrapMaxLines, LetterSpacing, LayoutMode Center / Right / Full, nothing UNVERIFIED) and an exact
# height budget read back out of the markup (SUI.used_height / used_width), and returns the Java of each piece. The Java around the
# pieces - the 0.1.3 prelude, every b.set text, every event binding + EventData and their order, this.offer, the page maths - is
# 0.1.3's (SkyyVault/test_skyyvault_0.1.4.py builds both versions side by side and compares them).
VAULT_W = 1040                    # 0.1.3's width (the page sits over the vault slots in page mode); the height = the sum of the parts
VAULT_PREFIX = "SkyyV"            # every element id starts with it (the 0.1.3 ids already did)
VAULT_NUM_W = 90                  # page number buttons: NORMAL tertiary tabs (44 px, 17 px labels - the page's main navigation, BIG
VAULT_NUM_GAP = SUI.TAB_GAP       # readable; review fix 2): the tab_row "tertiary" look of SkyyRanks / SkyySacks, 5 px apart (the tab
                                  # row's spacer); the page on screen = Tertiary_Active, a locked page = Disabled; 90 px so "1000"
                                  # (maxPages hard cap) fits the 42 px of label room at 17 px without shrinking
VAULT_OPEN_W, VAULT_BUY_W = 260, 360     # Primary buttons; "BUY PAGE 10 - 225K COINS" (17 px bold uppercase) needs ~270 of 312 px
VAULT_ACT_GAP = 12                # between Open and Buy (a vanilla spacing step)
VAULT_LINE_H = 26                 # a 16 px label line (16 + 10, the kit default)
VAULT_TWO_LINES = 46              # two 16 px lines of the game font (2 x 16 x 1.364 = 43.7) + 2 px (the SkyyBank 0.1.4 box)
VAULT_CAPTION_W = 400             # the "Page n of m  (locked)" caption between Prev and Next
# every element id 0.1.3's VaultPage created (SkyyVNum<n> / SkyyVHelp<i> are made per page / line) - all kept, asserted below
VAULT_IDS_013 = ["SkyyVault", "SkyyVSub", "SkyyVErr", "SkyyVErrRow", "SkyyVClose", "SkyyVNav", "SkyyVPrev", "SkyyVPageLbl", "SkyyVNext",
                 "SkyyVNums", "SkyyVNum", "SkyyVUsed", "SkyyVAct", "SkyyVOpen", "SkyyVBuy", "SkyyVHelp", "SkyyVInfo"]
# review aid: the b.set targets of each state (the Java below writes exactly 0.1.3's b.set lines; asserted to exist on the page)
VAULT_SETS = {"unreadable": ["SkyyVSub", "SkyyVErr"], "vault": ["SkyyVSub", "SkyyVPageLbl", "SkyyVUsed", "SkyyVHelp0", "SkyyVHelp1",
                                                                "SkyyVHelp2", "SkyyVInfo"]}


def vault_rt_text(mk, sample, expr):
    """KIT-GAP (reported): a TextButton whose label is a RUNTIME value of proven characters - the page numbers, "Open page N" and
    0.1.3's Buy label safe(buyTxt), sent inline exactly as 0.1.3 sends them. The kit refuses J() inside Text (check_text) and
    ap.button() would b.set a TextButton's Text (UNVERIFIED "button-text", probe page 20), so the kit button is built with a proven
    sample label, checked, and only the sample is swapped for the Java value (0.1.3 concatenated the same values inline)."""
    t = 'Text: "%s";' % sample
    if not SUI.TEXT_OK.fullmatch(sample) or mk.count(t) != 1:
        raise SystemExit("vault_rt_text: the sample label %r is not in the markup exactly once: %s" % (sample, mk[:80]))
    SUI.check_markup(mk, VAULT_PREFIX)
    return mk.replace(t, 'Text: "' + SUI.J(expr, sample) + '";')


def vault_rt_java(mk):
    """The Java String expression of a vault_rt_text markup: its rendered sample passes check_markup first (java_append refuses the
    J() inside Text on purpose, so this is the one place the page emits such a markup)."""
    SUI.check_markup(SUI.render(mk), VAULT_PREFIX)
    return SUI.java_expr(mk)


def vault_no_row_padding(ap, what):
    """Review fix (the DEPLOY GATE below needs only the base probe pages): no LayoutMode Left row of the page carries a Padding (the
    kit 1.4 button_row(used= / left_margin=) centring, probe page base4) - a row is centred / right-aligned by its first child's
    Anchor Left instead, the way the kit pager centres Prev / page / Next."""
    for _p, mk in ap:
        for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,)):
            r = SUI._strip_quoted(SUI.render(v))
            for m in re.finditer(r"Group #([A-Za-z0-9]+) \{[^{}]*LayoutMode: Left;[^{}]*\}", r):
                if "Padding:" in m.group(0):
                    raise SystemExit("%s: row #%s has a Padding (kit 1.4 button_row, probe base4): %s" % (what, m.group(1), m.group(0)))


def vault_indent(src, n=2):
    return "\n".join(" " * n + ln for ln in src.split("\n"))


def vault_page():
    """(shell, java pieces, checked states, pieces, check copies, runtime-label buttons): VaultPage's markup from the kit. Every
    state fills the body exactly (no FlexWeight), every row / well is filled exactly, every 0.1.3 id is created, only proven
    properties (assert_proven)."""
    J = SUI.J
    PAD = SUI.WELL_PAD                                   # 8: the well's own padding (WorldEventPanelPage #Summary)
    sub_h, sub_gap = VAULT_LINE_H, 10
    nav_h = SUI.BTN_SMALL_H                              # the pager row: small Secondary Prev / Next (32)
    nums_top, nums_h = 8, SUI.BTN_H                      # the page tabs row (normal buttons, 44)
    used_top, used_h = 8, VAULT_LINE_H
    box_h = 2 * PAD + nav_h + nums_top + nums_h + used_top + used_h
    box_gap, help_n = 12, 3
    info_top, info_h = 8, VAULT_TWO_LINES
    sep_h = 1 + 2 * SUI.SEP_MARGIN                       # the content separator, 8 above and below (WorldEventPanelPage)
    act_h = SUI.BTN_H
    inner_h = sub_h + sub_gap + box_h + box_gap + help_n * VAULT_LINE_H + info_top + info_h + sep_h + act_h
    sh = SUI.page_shell("SkyyVF", VAULT_W, SUI.TITLE_H + 2 * SUI.CONTENT_PAD + inner_h, "Vault", kind="plain", body_id="SkyyVault")
    body, W = sh.body, sh.inner_w
    assert sh.inner_h == inner_h
    BW = W - 2 * PAD                                     # inside the navigation well
    pc = {}
    chk = {}                                             # check copies of the runtime-label buttons (proven sample labels)

    def piece(name):
        pc[name] = SUI.Appends()
        return pc[name]
    piece("shell").extend(sh.appends)
    # 1. the profile hint line (0.1.3 #SkyyVSub, same text): the vanilla default label, centred
    piece("sub").add(body, SUI.label("SkyyVSub", "", "default", h=sub_h, align="Center", anchor={"bottom": sub_gap}))
    # 2a. unreadable vault file (0.1.3 d == null): the red line on a well where the vault content would be; separator + #SkyyVErrRow
    #     with Close at the same place as the vault view's Close
    err_h = inner_h - (sub_h + sub_gap) - sep_h - act_h
    e = piece("err")
    e.add(body, SUI.panel("SkyyVErrBox", "well", h=err_h))
    e.add("SkyyVErrBox", SUI.label("SkyyVErr", "", "error", h=err_h - 2 * PAD, bold=True, wrap=True, align="Center"))
    e.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    # review fix: a plain LayoutMode Left row and Close's own Anchor Left (the margin the pager's Prev and the vault view's Close
    # use) instead of the kit 1.4 button_row(used=) Padding Left (probe base4): the page needs only the base probe pages
    e.add(body, SUI.group("SkyyVErrRow", "Left", h=act_h))
    e.add("SkyyVErrRow", SUI.button("SkyyVClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel",
                                    anchor={"left": SUI.right_margin(W, SUI.BTN_MIN_W)}))
    # 2b. the navigation well: pager (< Prev | Page n of m | Next >; the vanilla Disabled look at the ends, still bound like 0.1.3's
    #     grey buttons), the page number tabs, the slots line
    piece("box").add(body, SUI.panel("SkyyVBox", "well", h=box_h, anchor={"bottom": box_gap}))
    nav = SUI.pager("SkyyVBox", "SkyyVNav", BW, text=None, prev_on=J("this.sel > 1"), next_on=J("this.sel < max"),
                    caption_w=VAULT_CAPTION_W, top=0, kind="strong",
                    ids={"row": "SkyyVNav", "prev": "SkyyVPrev", "page": "SkyyVPageLbl", "next": "SkyyVNext"})
    assert nav.h == nav_h
    piece("nav").extend(nav)
    row_w = 10 * VAULT_NUM_W + 9 * VAULT_NUM_GAP
    # review fix: a plain LayoutMode Left row; the FIRST tab's Anchor Left = the Java's centring pad, the others the 5 px gap (the
    # pager's own centring margin) - no kit 1.4 button_row(left_margin=) Padding Left (probe base4)
    piece("nums").add("SkyyVBox", SUI.group("SkyyVNums", "Left", h=nums_h, anchor={"top": nums_top}))
    # the page tabs: SEL = the page on screen (Tertiary_Active), ON = an owned page, OFF = a locked page (Disabled look, still bound)
    nid, nanc = "SkyyVNum" + J("n", "7"), {"left": J("i > 0 ? %d : pad" % VAULT_NUM_GAP, str(VAULT_NUM_GAP))}
    nums = {}
    for key, kw in (("sel", {"selected": True}), ("on", {}), ("off", {"disabled": True})):
        mk = SUI.button(nid, "7", "tertiary", w=VAULT_NUM_W, anchor=nanc, **kw)
        chk["num" + key] = mk
        nums[key] = vault_rt_text(mk, "7", "n")
    piece("used").add("SkyyVBox", SUI.label("SkyyVUsed", "", "bold", h=used_h, align="Center", anchor={"top": used_top}))
    # 3. the three help lines (0.1.3 texts), the vanilla default label
    help_mk = SUI.label("SkyyVHelp" + J("i", "0"), "", "default", h=VAULT_LINE_H, align="Center")
    piece("help").add(body, help_mk)
    # 4. the result line (+ / - / = in the vanilla colours, two lines)
    piece("info").add(body, SUI.status_line("SkyyVInfo", "colorOf(this.info)", h=info_h, wrap=True, anchor={"top": info_top}))
    # 5. footer (WorldEventPanelPage #Footer): separator, then #SkyyVAct = Open + Buy (Primary; the Disabled look when unavailable, still
    #    bound like 0.1.3's grey) on the left, Close (Secondary + the vanilla cancel sound) on the right
    f = piece("foot")
    f.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    f.add(body, SUI.group("SkyyVAct", "Left", h=act_h))
    acts = {}
    for key, ident, sample, expr, w, anc in (("open", "SkyyVOpen", "Open page 2", "openTxt", VAULT_OPEN_W, None),
                                             ("buy", "SkyyVBuy", "Buy page 3 - 50k coins", "safe(buyTxt)", VAULT_BUY_W,
                                              {"left": VAULT_ACT_GAP})):
        for on in (True, False):
            mk = SUI.button(ident, sample, "primary", w=w, anchor=anc, disabled=not on)
            chk[key + ("on" if on else "off")] = mk
            acts[key + ("on" if on else "off")] = vault_rt_text(mk, sample, expr)
    close_left = W - VAULT_OPEN_W - VAULT_ACT_GAP - VAULT_BUY_W - SUI.BTN_MIN_W
    piece("close").add("SkyyVAct", SUI.button("SkyyVClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel",
                                              anchor={"left": close_left}))

    # ---- both states, as the Java builds them (10 page tabs, 3 help lines): check_page (ids, prefix, parents, duplicates, markup
    #      rules), assert_proven, the body / well / rows filled exactly, every 0.1.3 id created
    def fix(mk, pairs):
        for a, b in pairs:
            mk = mk.replace(a, b)
        return mk
    states = {}
    ap = SUI.Appends()
    for nm in ("shell", "sub", "err"):
        ap.extend(pc[nm])
    states["unreadable"] = ap
    ap = SUI.Appends()
    for nm in ("shell", "sub", "box", "nav", "nums"):
        ap.extend(pc[nm])
    for k in range(10):
        look = "numsel" if k == 2 else ("numon" if k < 5 else "numoff")
        ap.append(("SkyyVNums", fix(chk[look], [(J("n", "7"), str(k + 1)), (J("i > 0 ? %d : pad" % VAULT_NUM_GAP, str(VAULT_NUM_GAP)),
                                                                            str(VAULT_NUM_GAP if k else SUI.centre_margin(BW, row_w)))])))
    ap.extend(pc["used"])
    for k in range(help_n):
        ap.append((body, fix(help_mk, [(J("i", "0"), str(k))])))
    for nm in ("info", "foot"):
        ap.extend(pc[nm])
    ap.append(("SkyyVAct", chk["openon"]))
    ap.append(("SkyyVAct", chk["buyon"]))
    ap.extend(pc["close"])
    states["vault"] = ap
    made = set()
    for name, ap in states.items():
        SUI.check_page(ap, VAULT_PREFIX)
        SUI.assert_proven(ap, what="vault page (%s)" % name)
        vault_no_row_padding(ap, "vault page (%s)" % name)
        left = sh.fit([SUI.used_height(ap, body)], "vault page body (%s)" % name)
        assert left == 0, "the vault page body (%s) must be filled exactly (no FlexWeight filler): %d px left" % (name, left)
        ids = set(i for _p, mk in ap for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,))
                  for i in re.findall(r"#([A-Za-z0-9]+)\s*\{", SUI.render(v)))
        missing = [x for x in VAULT_SETS[name] if x not in ids]
        assert not missing, "vault page (%s): b.set targets not on the page: %s" % (name, missing)
        made |= ids
    va, ua = states["vault"], states["unreadable"]
    assert SUI.used_height(ua, "SkyyVErrBox") == err_h - 2 * PAD, "the error well must be filled exactly"
    assert SUI.used_width(ua, "SkyyVErrRow") == W, "#SkyyVErrRow: Close right-aligned (its Anchor Left + its width = the body width)"
    assert SUI.used_height(va, "SkyyVBox") == box_h - 2 * PAD, "the navigation well must be filled exactly"
    assert SUI.used_width(va, "SkyyVAct") == W, "#SkyyVAct (Open + Buy | Close) must fill the body width"
    assert SUI.used_width(va, "SkyyVNums") == row_w + SUI.centre_margin(BW, row_w), "page tabs centred by the first tab's Anchor Left"
    assert SUI.used_width(va, "SkyyVNav") <= BW, "the pager fits the well"
    missing = [x for x in VAULT_IDS_013 if not any(i == x or (x in ("SkyyVNum", "SkyyVHelp") and re.fullmatch(x + r"\d+", i))
                                                   for i in made)]
    assert not missing, "0.1.4 dropped 0.1.3 element ids: %s" % missing
    java = dict((nm, vault_indent(pc[nm].java("b"))) for nm in pc)
    rt = {}
    for key in nums:
        rt["num" + key] = nums[key]
    rt.update(acts)
    for key in rt:
        java[key] = vault_rt_java(rt[key])
    return sh, java, states, pc, chk, rt


VAULT_SH, VAULT_JAVA, VAULT_STATES, VAULT_PIECES, VAULT_CHECK, VAULT_RT = vault_page()
VAULT_H, VAULT_BOX_W = VAULT_SH.h, VAULT_SH.inner_w - 2 * SUI.WELL_PAD
# text fit (kit 1.4, the client's own font tables): the runtime labels at their longest 0.1.3 form
for _t, _w in (("Buy page 10 - 225k coins", VAULT_BUY_W), ("Unlock page 10 - free", VAULT_BUY_W), ("All pages bought", VAULT_BUY_W),
               ("Open as chest", VAULT_OPEN_W), ("Open page 10", VAULT_OPEN_W)):
    if SUI.text_width(_t, 17, True, upper=True) > _w - 2 * SUI.BTN_PAD:
        print("skyyui WARNING: vault button label %r does not fit %d px" % (_t, _w))
if SUI.text_width(str(MAX_PAGE), 17, True, upper=True) > VAULT_NUM_W - 2 * SUI.BTN_PAD:
    print("skyyui WARNING: page number %d does not fit the %d px page tabs" % (MAX_PAGE, VAULT_NUM_W))
print("vault page (%s): %d x %d, %d states checked, %d pieces" % (KIT_ID, VAULT_W, VAULT_H, len(VAULT_STATES), len(VAULT_JAVA)))
VAULT_BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  boolean live = this.sess != null && !this.sess.closed;
  // ---- 0.1.4 frame: the plain vanilla window (0.1.3's root #SkyyVault is its body) + the profile hint line
""" + VAULT_JAVA["shell"] + "\n" + VAULT_JAVA["sub"] + r"""
  b.set("#SkyyVSub.Text", "One chest shared by ALL your profiles - put items in on one profile and take them out on another.");
  if (d == null) {
""" + vault_indent(VAULT_JAVA["err"]) + r"""
    b.set("#SkyyVErr.Text", "Your vault file cannot be read right now. Nothing in it was changed - please tell an admin.");
    ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
    return;
  }
  int unlocked = d.unlocked;
  int max = unlocked > @PKG@.VCfg.MAX_PAGES ? unlocked : @PKG@.VCfg.MAX_PAGES;
  if (this.sel < 1) this.sel = 1;
  if (this.sel > max) this.sel = max;
  boolean showing = live && this.sess.page == this.sel;
  // ---- the navigation well: pager, page tabs, slots line
""" + VAULT_JAVA["box"] + "\n" + VAULT_JAVA["nav"] + r"""
  b.set("#SkyyVPageLbl.Text", "Page " + this.sel + " of " + unlocked + (this.sel > unlocked ? "  (locked)" : ""));
  ev.addEventBinding(@BT@.Activating, "#SkyyVPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVNext", @EVD@.of("a", "next"));
  int shown = max < 10 ? max : 10;
  int start = 1;
  if (max > 10) {
    start = this.sel - 4;
    if (start < 1) start = 1;
    if (start + 9 > max) start = max - 9;
  }
  int pad = (""" + str(VAULT_BOX_W) + " - (shown * " + str(VAULT_NUM_W + VAULT_NUM_GAP) + " - " + str(VAULT_NUM_GAP) + r""")) / 2;
""" + VAULT_JAVA["nums"] + r"""
  for (int i = 0; i < shown; i++) {
    int n = start + i;
    b.appendInline("#SkyyVNums", n == this.sel ? (""" + VAULT_JAVA["numsel"] + r""") : (n <= unlocked ? (""" + VAULT_JAVA["numon"] + r""") : (""" + VAULT_JAVA["numoff"] + r""")));
    ev.addEventBinding(@BT@.Activating, "#SkyyVNum" + n, @EVD@.of("a", "num:" + n));
  }
""" + VAULT_JAVA["used"] + r"""
  String used = "";
  if (this.sel <= unlocked) {
    used = "Page " + this.sel + " - " + d.used(this.sel) + " of " + (live ? this.sess.usable : @PKG@.VCfg.usable(d.cap)) + " slots used" + (showing ? " - showing now" : "");
    if (live && !showing) used = used + " (the slots still show page " + this.sess.page + ")";
  } else if (this.sel == unlocked + 1) {
    used = "Page " + this.sel + " is locked - it costs " + @PKG@.VStore.grp(@PKG@.VStore.price(this.sel)) + " coins";
  } else {
    used = "Page " + this.sel + " is locked - buy page " + (unlocked + 1) + " first";
  }
  b.set("#SkyyVUsed.Text", used);
  // ---- the help lines and the result line
  String[] help = null;
  if (live && this.sess.layout != 0) {
    // 0.1.5: the vault slots carry arrows - say which presses turn a page at once (a plain click on an arrow item only lifts it on
    // the client; the server hears it at the put-down - research/Vault-Arrow-Click-Research.md)
    help = new String[] { "Drag items in and out - Esc saves. No vault slots next to this page? Click Open as chest.",
                          "One click turns pages: < Prev / Next > or a page number above. In the slots: shift-click an arrow.",
                          "A plain click on an arrow only lifts it - the page turns when you put it back. Drop key works too." };
  } else if (live) {
    help = new String[] { "Drag items between your inventory and the vault slots. Close or Esc saves your vault.",
                          "Vault slots not showing next to this page? Click Open as chest.",
                          "Commands: /vault 2 opens page 2, /vault next and /vault prev switch pages, /vault info" };
  } else if (@PKG@.VCfg.ARROWS) {
    // 0.1.5: chest mode's /vault pages page - the chest it opens has the arrow row
    help = new String[] { "Pick a page, then click Open to see its items as a chest.",
                          "In the chest: shift-click an arrow (or press Drop on it) to turn pages at once - Esc saves.",
                          "Every profile opens this same vault. Commands: /vault buy, /vault info" };
  } else {
    help = new String[] { "Pick a page, then click Open to see its items as a chest.",
                          "In the chest: drag items in and out - Esc saves. /vault 2 or /vault next switches pages.",
                          "Every profile opens this same vault. Commands: /vault buy, /vault info" };
  }
  for (int i = 0; i < help.length; i++) {
""" + vault_indent(VAULT_JAVA["help"]) + r"""
    b.set("#SkyyVHelp" + i + ".Text", help[i]);
  }
""" + VAULT_JAVA["info"] + r"""
  b.set("#SkyyVInfo.Text", textOf(this.info));
  // ---- footer: separator, Open + Buy | Close (0.1.3's texts, bindings and offer)
""" + VAULT_JAVA["foot"] + r"""
  String openTxt = live ? "Open as chest" : ("Open page " + this.sel);
  b.appendInline("#SkyyVAct", this.sel <= unlocked ? (""" + VAULT_JAVA["openon"] + r""") : (""" + VAULT_JAVA["openoff"] + r"""));
  ev.addEventBinding(@BT@.Activating, "#SkyyVOpen", @EVD@.of("a", "open"));
  int next = unlocked + 1;
  String buyTxt = "";
  boolean buyOn = false;
  this.offer = 0;
  if (next <= @PKG@.VCfg.MAX_PAGES) {
    long c = @PKG@.VStore.price(next);
    buyTxt = c > 0L ? ("Buy page " + next + " - " + @PKG@.VStore.shortAmt(c) + " coins") : ("Unlock page " + next + " - free");
    buyOn = true;
    this.offer = next;
  } else {
    buyTxt = "All pages bought";
    buyOn = false;
  }
  b.appendInline("#SkyyVAct", buyOn ? (""" + VAULT_JAVA["buyon"] + r""") : (""" + VAULT_JAVA["buyoff"] + r"""));
  ev.addEventBinding(@BT@.Activating, "#SkyyVBuy", @EVD@.of("a", "buy"));
""" + VAULT_JAVA["close"] + r"""
  ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
}"""
M(page, VAULT_BUILD_SRC)

# ================= 0.1.3 VBuyDlg part 1: the "Buy page X for Y coins?" confirm window (vanilla look) =================
# VANILLA LOOK (HANDOFF section 2 rule 0, tools/AGENT-BRIEF.md "UI LOOK"): the game's own confirm page
# Common/UI/Custom/Pages/PrefabEditorExitConfirm.ui (Assets.zip), built from Common/UI/Custom/Common.ui + Sounds.ui:
#   @DecoratedContainer = ContainerHeader title bar (38 px, HorizontalBorder 50) with the @TitleStyle label (15 px, bold, uppercase,
#   FontName Secondary, #b4c8c9), ContainerDecorationTop / Bottom, ContainerPatch body (Border 23) with the confirm page's 20 px padding;
#   the question = the confirm page's #WarningTitle (#ffcc00, 32 px there, 30 here so "Buy page 10 for 1,250,000 coins?" fits one line),
#   the message = @DefaultLabelStyle (16 px, #96a9be, wrapped), the note = its small caption line (14 px; #cc4444 = the vanilla
#   out-of-stock red of BarterTradeRow when the purse is short); Buy = @TextButton (Primary, the SaveSettings sounds the confirm page
#   gives its main button), Cancel = @SecondaryTextButton (ButtonsCancel sounds), centred.
# 0.1.4: the SAME window, now made by the kit (tools/skyyui.py) instead of 0.1.3's hand-copied DLG_* strings + VANILLA_CHECK list:
# SUI.verify() (top of this script) proves every value, texture and sound against Assets.zip at every build. vault_dialog() composes
# it from page_shell (decorated, padding 20 = SUI.DIALOG_PAD) + label kinds (warning 30 px, message, default 14 px) + button kinds
# (primary / save sound, secondary / cancel sound) + a plain group row: meant to look like 0.1.3 element for element (the harness
# compares every property), but the MARKUP SENT changes in four ways that no one has seen in game (review: not "exactly as before"):
# the button styles carry the kit's full vanilla state set (ShrinkTextToFit / MinShrinkTextToFitFontSize 12 - the labels fit anyway -
# and the Disabled state no one triggers); the two buttons are centred by Buy's own Anchor Left 154 in a LayoutMode Left row instead
# of LayoutMode Center (a "base" probe property the kit keeps behind the probe pages; review fix: not the kit 1.4 button_row Padding
# Left of probe base4 either); the title label is nested inside the title bar Group's append (kit page_shell); the style keys come in
# the kit's order. In-game test step 1 opens this window on its own first.
# KIT-GAP (reported): SUI.confirm_dialog cannot take the 30 px question, the runtime note colour or a 700 x 300 window with the
# 0.1.3 heights, and its button row is LayoutMode Center - hence composed here from the kit's builders.
# Not copied (as in 0.1.3): the full-screen 45 % dark @PageOverlay (page roots are Width / Height only) and the bottom-left BackButton
# (Esc closes the window, like every page).
VDLG_W, VDLG_H = 700, 300         # 0.1.3's window
VDLG_BTN_W, VDLG_BTN_GAP = 170, 6  # 0.1.3's buttons (Width 170, Right / Left 6)
VAULT_DLG_IDS_013 = ["SkyyVDlg", "SkyyVDlgHead", "SkyyVDlgTitle", "SkyyVDlgBody", "SkyyVDlgQ", "SkyyVDlgMsg", "SkyyVDlgNote",
                     "SkyyVDlgBtns", "SkyyVDlgBuy", "SkyyVDlgNo"]


def vault_dialog():
    """(shell, java): the confirm window's markup from the kit - 0.1.3's ids, sizes, colours and texts (see above)."""
    sh = SUI.page_shell("SkyyVDlg", VDLG_W, VDLG_H, "Vault", pad=SUI.DIALOG_PAD, bar_id="SkyyVDlgHead", title_id="SkyyVDlgTitle",
                        body_id="SkyyVDlgBody")
    ap, body, W = sh.appends, sh.body, sh.inner_w
    ap.add(body, SUI.label("SkyyVDlgQ", "", "warning", size=30, h=46, anchor={"bottom": 12}))
    ap.add(body, SUI.label("SkyyVDlgMsg", "", "message", h=48, anchor={"bottom": 12}))
    ap.add(body, SUI.label("SkyyVDlgNote", "", "default", size=14, h=24, align="Center", anchor={"bottom": 16},
                           col=SUI.color_by([("poor", "outOfStock")], "text")))
    used = 2 * (VDLG_BTN_W + VDLG_BTN_GAP)
    # review fix: a plain LayoutMode Left row; the first button's Anchor Left centres the pair (the pager's centring margin) - not
    # the kit 1.4 button_row(used=) Padding Left (probe base4) nor 0.1.3's LayoutMode Center (a "base" probe property)
    ap.add(body, SUI.group("SkyyVDlgBtns", "Left", h=SUI.BTN_H))
    yes = [SUI.button("SkyyVDlgBuy", t, "primary", w=VDLG_BTN_W, sound="save",
                      anchor={"left": SUI.centre_margin(W, used), "right": VDLG_BTN_GAP}) for t in ("Buy", "Unlock")]
    ap.add("SkyyVDlgBtns", SUI.choose(SUI.J("this.cost > 0L"), yes[0], yes[1]))
    ap.add("SkyyVDlgBtns", SUI.button("SkyyVDlgNo", "Cancel", "secondary", w=VDLG_BTN_W, sound="cancel", anchor={"left": VDLG_BTN_GAP}))
    SUI.check_page(ap, "SkyyVDlg")
    SUI.assert_proven(ap, what="vault confirm window")
    vault_no_row_padding(ap, "vault confirm window")
    assert SUI.used_width(ap, "SkyyVDlgBtns") == used + SUI.centre_margin(W, used), "the Buy / Cancel pair is centred"
    # 0.1.3's window kept its 20 px under the buttons (300 px high): the same here (the body is NOT filled exactly on purpose)
    left = sh.fit([SUI.used_height(ap, body)], "vault confirm window body")
    assert left == 20, "the confirm window must keep 0.1.3's geometry (20 px under the buttons): %d" % left
    have = set(i for _p, mk in ap for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,))
               for i in re.findall(r"#([A-Za-z0-9]+)\s*\{", SUI.render(v)))
    missing = [x for x in VAULT_DLG_IDS_013 if x not in have]
    assert not missing, "0.1.4 dropped confirm window ids: %s" % missing
    return sh, vault_indent(ap.java("b"))


VDLG_SH, VDLG_JAVA = vault_dialog()
# ret = where the window returns after Buy / Cancel: 0 nothing (the vault was not open), 1 the vault page view (page mode), 2 the vault
# chest window (chest mode: "afterwards return to the vault on the new page"), 3 the vault page without slots (/vault pages in chest
# mode). back = the vault page shown before (Cancel / a refused buy return there). done = the window already acted (one-shot: a double
# click on Buy, or Esc after Buy, can never act twice).
# 0.1.3 review hardening: wu = the world the window opened in, at = when it opened. A window the page manager still reports after a
# world switch or after STALE_MS (2 min) no longer counts as "on your screen" (live()): /vault buy and a buy click drop it (done) and
# open a fresh one instead of being blocked by a dead window.
for f in ("public @PR@ pr;", "public java.util.UUID u;", "public int page;", "public long cost;", "public int ret;", "public int back;",
          "public volatile boolean done;", "public java.util.UUID wu;", "public long at;",
          "public static final long STALE_MS = 120000L;"):       # 0.1.4: 0.1.3's BTNP / BTNS style strings are gone (the kit's buttons)
    F(dlg, f)
C(dlg, r"""
public VBuyDlg(@PR@ pr, int page, long cost, int ret, int back) {
  super(pr, @LIFE@.CanDismiss);
  this.pr = pr; this.u = pr == null ? null : pr.getUuid(); this.page = page; this.cost = cost; this.ret = ret; this.back = back < 1 ? 1 : back;
  this.done = false;
  java.util.UUID w = null;
  try { if (pr != null) w = pr.getWorldUuid(); } catch (Throwable t) { w = null; }
  this.wu = w;
  this.at = System.currentTimeMillis();
}""")
# true = this window still blocks a new one for its page: not acted yet, opened in the player's CURRENT world (now = pr.getWorldUuid()
# at the caller), and younger than STALE_MS (a clock that jumped back counts as stale too)
M(dlg, r"""
public boolean live(java.util.UUID now) {
  if (this.done) return false;
  long age = System.currentTimeMillis() - this.at;
  if (age < 0L || age > STALE_MS) return false;
  if (this.wu == null) return now == null;
  return this.wu.equals(now);
}""")
# the question, the message and the purse note; all dynamic text goes through set() (HANDOFF section 2)
M(dlg, r"""
public String question() {
  if (this.cost > 0L) return "Buy page " + this.page + " for " + @PKG@.VStore.grp(this.cost) + " coins?";
  return "Unlock page " + this.page + " for free?";
}""")
M(dlg, r"""
public String note() {
  @PKG@.VData d = this.u == null ? null : @PKG@.VStore.load(this.u);
  String own = d == null ? "" : ("You own " + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + " vault pages.");
  if (this.cost <= 0L) return own;
  Object get = @PKG@.VCfg.bridge().get("coins:fn:get");
  Object r = null;
  try { if (get instanceof java.util.function.Function) r = ((java.util.function.Function) get).apply(this.u); } catch (Throwable t) { r = null; }
  if (!(r instanceof Long)) return own;
  long have = ((Long) r).longValue();
  return own + (own.length() > 0 ? " " : "") + "Your purse: " + @PKG@.VStore.grp(have) + " coins" + (have < this.cost ? " - not enough." : ".");
}""")
# 0.1.4: the markup comes from vault_dialog() (the kit); the texts (b.set), poor, the Buy / Unlock label choice and both bindings are
# 0.1.3's
VDLG_BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  String nt = "";
  try { nt = note(); } catch (Throwable t) { nt = ""; }
  boolean poor = nt.endsWith("not enough.");
""" + VDLG_JAVA + r"""
  b.set("#SkyyVDlgQ.Text", question());
  b.set("#SkyyVDlgMsg.Text", this.cost > 0L ? "The coins come from the purse of the profile you are playing now. Vault pages are shared by all your profiles." : "Vault pages are shared by all your profiles.");
  b.set("#SkyyVDlgNote.Text", nt);
  ev.addEventBinding(@BT@.Activating, "#SkyyVDlgBuy", @EVD@.of("a", "dlgbuy"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVDlgNo", @EVD@.of("a", "dlgno"));
}"""
M(dlg, VDLG_BUILD_SRC)
# the page id = a hash of every piece of page code the kit makes (VaultPage.build + colorOf / textOf, VBuyDlg.build): a later kit
# change that alters a page changes it. It is in the ready log line; VAULT_PAGE_CHECKED = the page id SkyyVault/test_skyyvault_0.1.5.py
# last passed on (a build whose pages differ warns; the harness fails until the new pages are checked). 0.1.5: the id moved because
# the help texts are part of VaultPage.build (the markup is unchanged - the harness compares every appended markup with 0.1.4's).
import hashlib
VAULT_PAGE_ID = hashlib.sha256("\n".join(list(SUI.java_status_methods("colorOf", "textOf")) + [VAULT_BUILD_SRC, VDLG_BUILD_SRC])
                               .encode("utf8")).hexdigest()[:12]
VAULT_PAGE_CHECKED = "5ad38980408a"
if VAULT_PAGE_ID == VAULT_PAGE_CHECKED:
    print("vault pages %s = the pages SkyyVault/test_skyyvault_0.1.5.py last passed on" % VAULT_PAGE_ID)
else:
    print("WARNING: vault pages %s are NOT the pages SkyyVault/test_skyyvault_0.1.5.py last passed on (%s): run the harness, then set "
          "VAULT_PAGE_CHECKED in this script and rebuild; never deploy unchecked pages" % (VAULT_PAGE_ID, VAULT_PAGE_CHECKED))
# DEPLOY GATE: both pages are the kit's "base" look, not yet seen in game; a parse error disconnects the client the moment /vault,
# the Menu tile or a buy opens them. Keep tools/deploy_set.py SET at ("SkyyVault", "0.1.3") until Skyy has opened probe pages base1 /
# base2 / base3 without a disconnect. Review fix: neither page uses a kit 1.4 builder any more (no button_row(used= / left_margin=)
# Padding Left: every row is a plain LayoutMode Left row centred / right-aligned by its first child's Anchor Left, the way the kit
# pager centres), so probe page base4 is NOT part of the gate (vault_no_row_padding() asserts it on every state of both pages).
# 0.1.5: the gate is MET - Skyy opened probe pages base1-4 in game (HANDOFF 2026-09-30 05:55: "19 work - base1-4 ...") and 0.1.4 with
# this exact look is live since then; the kit's own skyyui.PROBED set (tools/skyyui.py, not this script's file) does not list "base" yet
if "base" not in SUI.PROBED:
    print("note: skyyui.PROBED does not list 'base' yet, but probe pages base1-4 passed in game on 2026-09-30 and SkyyVault 0.1.4 "
          "(this look) is live - the 0.1.4 deploy gate is met")

# ================= VCloseTask constructor (run() comes after VSessions) =================
clt.addInterface(pool.get("java.lang.Runnable"))
# offline = true: the last-resort finalize of a session whose viewer is gone (VSessions.dispatchOffline), run on that world's thread
for f in ("public @PKG@.VSession sess;", "public String reason;", "public java.util.UUID wu;", "public boolean onlyIfPageGone;",
          "public boolean hop;", "public int tries;", "public boolean offline;"):
    F(clt, f)
C(clt, r"""
public VCloseTask(@PKG@.VSession s, String reason, java.util.UUID wu, boolean onlyIfPageGone, boolean hop) {
  this.sess = s; this.reason = reason; this.wu = wu; this.onlyIfPageGone = onlyIfPageGone; this.hop = hop; this.tries = 0;
  this.offline = false;
}""")

# ================= VSessions: the one-editable-view-per-vault logic =================
for f in ("public static final java.util.concurrent.ConcurrentHashMap SESSIONS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EPOCHS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SWITCHED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BUSYSEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final int PAGE = 1;", "public static final int CHEST = 2;",
          # 0.1.2: window serials (seeded with the start time, so a stray from an earlier run never matches a new window), the
          # online set for the join sweep, the last periodic sweep, the inventory section names for vault.log
          "public static final java.util.concurrent.atomic.AtomicLong SERIAL = new java.util.concurrent.atomic.AtomicLong(System.currentTimeMillis());",
          "public static final java.util.concurrent.ConcurrentHashMap ONLINE = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long LAST_SWEEP = 0L;",
          "public static final String[] SECTIONS = new String[] { \"hotbar\", \"storage\", \"backpack\", \"armor\", \"utility\", \"tools\" };"):
    F(vs, f)
M(vs, r"""
public static void tell(@PR@ pr, String res) {
  if (pr == null || res == null || res.length() == 0) return;
  String col = "#cfe3ff";
  String txt = res;
  char c = res.charAt(0);
  if (c == '+') { col = "#8fe39a"; txt = res.substring(1); }
  else if (c == '-') { col = "#ff9d6b"; txt = res.substring(1); }
  else if (c == '=') { txt = res.substring(1); }
  try { pr.sendMessage(@MSG@.raw("[Vault] " + txt).color(col)); } catch (Throwable t) { }
}""")
M(vs, r"""
public static void tellAll(@PR@ pr, String[] lines) {
  if (lines == null) return;
  for (int i = 0; i < lines.length; i++) tell(pr, lines[i]);
}""")
# first sight of an epoch = baseline (contract section 4 rule 2); a later different value = a switch
M(vs, r"""
public static boolean noteEpoch(java.util.UUID u) {
  Object cur = @PKG@.VCfg.bridge().get("profile:epoch:" + u);
  if (cur == null) return false;
  Object prev = EPOCHS.put(u, cur);
  if (prev != null && !prev.equals(cur)) { SWITCHED.put(u, Long.valueOf(System.currentTimeMillis())); return true; }
  return false;
}""")
# profile:busy seen, then gone = a switch or a crash recovery at join finished: SkyyProfiles keeps its marker 30 s after both, so the
# settle window starts again (a recovery keeps the epoch, so noteEpoch alone would not see it)
M(vs, r"""
public static boolean noteBusy(java.util.UUID u) {
  if (@PKG@.VCfg.bridge().get("profile:busy:" + u) != null) { BUSYSEEN.put(u, Boolean.TRUE); return true; }
  if (BUSYSEEN.remove(u) != null) SWITCHED.put(u, Long.valueOf(System.currentTimeMillis()));
  return false;
}""")
# seconds the vault still stays shut after a switch / recovery (0 = open)
M(vs, r"""
public static long settleLeft(java.util.UUID u) {
  Object at = SWITCHED.get(u);
  if (!(at instanceof Long)) return 0L;
  long left = @PKG@.VCfg.AFTER_SWITCH_MS - (System.currentTimeMillis() - ((Long) at).longValue());
  if (left <= 0L) return 0L;
  return (left + 999L) / 1000L;
}""")
M(vs, r"""
public static String gate(java.util.UUID u) {
  if (noteBusy(u)) return "-Your profile is still loading - try /vault again in a moment.";
  noteEpoch(u);
  long left = settleLeft(u);
  if (left > 0L) return "-Your profile just changed - your vault opens in " + left + " s (your switch is still being saved).";
  return null;
}""")
M(vs, r"""
public static @PKG@.VSession current(java.util.UUID u) {
  Object o = SESSIONS.get(u);
  if (o == null) return null;
  @PKG@.VSession s = (@PKG@.VSession) o;
  if (s.closed) return null;
  return s;
}""")
M(vs, r"""
public static boolean registered(@PLA@ p, @PKG@.VSession s) {
  try {
    if (p == null || s == null || s.window == null) return false;
    int id = s.window.getId();
    if (id <= 0) return false;
    return p.getWindowManager().getWindow(id) == s.window;
  } catch (Throwable t) { return false; }
}""")
# 0.1.2: queue the ONE click batch of session s on its viewer's world thread (the dispatchClose pattern); no world = the batch is
# dropped (the next fill places a fresh row anyway)
M(vs, r"""
public static void queueBtn(@PKG@.VSession s) {
  try {
    java.util.UUID wu = s.pr == null ? null : s.pr.getWorldUuid();
    @WLD@ w = null;
    if (wu != null) w = @UNI@.get().getWorld(wu);
    if (w == null) { s.clearQueued(); return; }
    w.execute(new @PKG@.VBtnTask(s, wu));
  } catch (Throwable t) {
    s.clearQueued();
    @PKG@.VCfg.warnOnce("btnq-" + s.owner, "could not schedule the vault arrow click for " + s.owner + ": " + t);
  }
}""")
# the view -> the page array (explicit; the change listener calls it too); schedules the save when anything changed.
# 0.1.2: storage indices only (never the control row or a live inside arrow); a vault arrow item found in a storage index is saved as
# EMPTY and a batch is queued that removes it from the view
M(vs, r"""
public static boolean syncView(@PKG@.VSession s) {
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d == null || s.view == null) return false;
  int cap = s.view.getCapacity();
  int n = s.store > 0 && s.store < cap ? s.store : cap;
  @IS@[] now = new @IS@[n];
  boolean stray = false;
  for (int i = 0; i < n; i++) {
    if (s.ctrlLive(i)) continue;
    @IS@ x = s.view.getItemStack((short) i);
    if (x == null || x.isEmpty()) continue;
    if (@PKG@.VBtn.isButton(x)) { stray = true; continue; }
    now[i] = x;
  }
  boolean ch = d.copyIn(s.page, now);
  if (ch) @PKG@.VStore.saveSoon(s.owner, @PKG@.VCfg.SAVE_DELAY_MS);
  if (stray && !s.closed && !s.inBatch && s.wantBatch()) queueBtn(s);
  return ch;
}""")
# 0.1.2 arrowLayout=inside: a reserved arrow slot that showed a stored stack (vault full) and is empty now
M(vs, r"""
public static boolean freed(@PKG@.VSession s, int slot) {
  if (s.layout != 2 || slot < 0 || s.ctrlLive(slot)) return false;
  @IS@ x = s.view.getItemStack((short) slot);
  return x == null || x.isEmpty();
}""")
# 0.1.2: a storage move during a click batch marks the batch (then it is not a click); a freed inside arrow slot queues a batch that
# puts the arrow back (relive)
M(vs, r"""
public static void onChange(@PKG@.VSession s) {
  if (s == null || s.closed || s.swapping) return;
  s.noteChanged();
  syncView(s);
  if (s.layout == 2 && !s.inBatch && (freed(s, s.prevIdx) || freed(s, s.nextIdx)) && s.wantBatch()) queueBtn(s);
}""")
# 0.1.2: one stray-arrow sweep of player pr on their world thread (VSweepTask -> sweepRun -> sweepPlayer); tries = re-dispatches after
# a world change (the VCloseTask pattern)
M(vs, r"""
public static void dispatchSweep2(@PR@ pr, String why, int tries) {
  try {
    if (pr == null) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null) return;
    w.execute(new @PKG@.VSweepTask(pr, why, wu, tries));
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("sweepq", "could not schedule the vault stray-arrow check: " + t); }
}""")
M(vs, r"""
public static void dispatchSweep(@PR@ pr, String why) {
  dispatchSweep2(pr, why, 0);
}""")
# 0.1.2 review: world thread, right before finalizeWorld empties the view. A REAL stack in a live control slot (only if the batch rescue
# could not move it - restoreCtrl then leaves it and closes the view) is never in VData (syncView skips control slots), so it goes to
# the first free slot of any owned page now (vault.log RESCUE ... at close) instead of being emptied with the view. No-op normally.
M(vs, r"""
public static void keepCtrl(@PKG@.VSession s) {
  if (s == null || s.layout == 0 || s.view == null) return;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  String who = (s.pr == null ? "?" : s.pr.getUsername()) + " " + s.owner;
  int cap = s.view.getCapacity();
  for (int i = s.base; i < s.base + s.span && i < cap; i++) {
    if (!s.ctrlLive(i)) continue;
    @IS@ x = s.view.getItemStack((short) i);
    if (x == null || x.isEmpty() || @PKG@.VBtn.isButton(x)) continue;
    String at = null;
    if (d != null) at = d.putFirstFree(-1, s.layout == 2 ? s.prevIdx : -1, s.layout == 2 ? s.nextIdx : -1, x);
    if (at != null) {
      @PKG@.VStore.log("RESCUE " + who + " control slot " + i + " at close -> vault page:slot " + at + " " + x.getItemId() + " x" + x.getQuantity());
      @PKG@.VStore.saveSoon(s.owner, 0L);
      continue;
    }
    boolean thrown = false;
    try {
      @REF@ ref = null;
      @ST@ st = null;
      if (s.pr != null && s.pr.isValid()) ref = s.pr.getReference();
      if (ref != null && ref.isValid()) st = ref.getStore();
      if (st != null) {
        @IU@.throwItem(ref, x, 6.0F, st);
        thrown = true;
        @PKG@.VStore.log("RESCUE " + who + " control slot " + i + " at close -> thrown at the player's feet " + x.getItemId() + " x" + x.getQuantity());
      }
    } catch (Throwable t) { @PKG@.VCfg.warn("vault close-time rescue throw failed for " + who + ": " + t); }
    if (!thrown) {
      @PKG@.VStore.log("RESCUE-LOST " + who + " control slot " + i + " at close " + x.getItemId() + " x" + x.getQuantity() + " (vault full - restore by hand)");
      @PKG@.VCfg.warn("RESCUE-LOST: a " + x.getItemId() + " x" + x.getQuantity() + " of " + who + " had nowhere to go when the vault closed - see vault.log");
    }
  }
}""")
# world thread: last sync (unless the view is known bad), then the view is made inert: listener off, DENY_ALL, emptied.
# 0.1.2: then the viewer is swept (as its own world task - never in the middle of an engine window close)
M(vs, r"""
public static void finalizeWorld(@PKG@.VSession s) {
  if (s == null || !s.close1()) return;
  if (!s.noSync) { try { syncView(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault final sync failed for " + s.owner + ": " + t); } }
  try { keepCtrl(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault close-time rescue failed for " + s.owner + ": " + t); }
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  try { s.view.setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
  try { s.view.clear(); } catch (Throwable t) { }
  SESSIONS.remove(s.owner, s);
  LAST.put(s.owner, Integer.valueOf(s.page));
  @PKG@.VStore.saveSoon(s.owner, 0L);
  if (!@PKG@.VStore.STOPPING) dispatchSweep(s.pr, "close");
}""")
# retire a view WITHOUT closing its window (any thread: viewer gone, plugin shutdown, or a view that is on screen and about to be
# replaced by a new page): DENY_ALL FIRST (no client move can land after the last sync), then sync, then marked closed. The view is not
# emptied (the client may still show it until the new page replaces it); its window is closed by the client, by validate() on the next
# movement (closed session = false) or by the engine on a world change.
M(vs, r"""
public static void retire(@PKG@.VSession s) {
  if (s == null) return;
  try { s.view.setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
  if (!s.close1()) return;
  if (!s.noSync) { try { syncView(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault final sync failed for " + s.owner + ": " + t); } }
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  SESSIONS.remove(s.owner, s);
  LAST.put(s.owner, Integer.valueOf(s.page));
  @PKG@.VStore.saveSoon(s.owner, 0L);
}""")
M(vs, r"""
public static void closeRegistered(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  try { p.getWindowManager().closeWindow(ref, s.window.getId(), st); } catch (Throwable t) { @PKG@.VCfg.warn("vault window close failed for " + s.owner + ": " + t); }
  finalizeWorld(s);
}""")
M(vs, r"""
public static void closeAny(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  if (s == null || s.closed) return;
  if (registered(p, s)) closeRegistered(p, ref, st, s);
  else finalizeWorld(s);
}""")
# 0.1.2 arrowLayout=inside: before page `page` is shown, stacks stored in its two arrow slots move to free slots (VData.clearReserved:
# vault.log + one chat line each, counted before and after)
M(vs, r"""
public static void reserve(@PKG@.VSession s, @PKG@.VData d, int page) {
  if (s.layout != 2) return;
  java.util.ArrayList out = d.clearReserved(page, s.prevIdx, s.nextIdx);
  boolean moved = false;
  for (int i = 0; i < out.size(); i++) {
    String[] e = (String[]) out.get(i);
    if (e[0] != null) { @PKG@.VStore.log(e[0]); moved = true; }
    if (e[1] != null) tell(s.pr, e[1]);
  }
  if (moved) @PKG@.VStore.saveSoon(s.owner, @PKG@.VCfg.SAVE_DELAY_MS);
}""")
# clear + fill the view from a page and read every slot back; false = the view does not match (caller must not sync it).
# 0.1.2: storage indices from src (never over a live arrow), then the canonical control row (s.ctrl, built by VBtn.row for this page),
# then BOTH are read back: storage against src, every live control against s.ctrl (a live control over a stored stack = false, so a
# stack can never be hidden under an arrow and lost from the save)
M(vs, r"""
public static boolean fill(@PKG@.VSession s, @IS@[] src) {
  s.view.clear();
  int cap = s.view.getCapacity();
  int n = s.store > 0 && s.store < cap ? s.store : cap;
  for (int i = 0; i < n && i < src.length; i++) {
    if (src[i] != null && !s.ctrlLive(i)) s.view.setItemStackForSlot((short) i, src[i], false);
  }
  @IS@[] c = s.ctrl;
  for (int i = 0; i < c.length; i++) {
    int slot = s.base + i;
    if (c[i] != null && s.ctrlLive(slot)) s.view.setItemStackForSlot((short) slot, c[i], false);
  }
  for (int i = 0; i < cap; i++) {
    @IS@ v = s.view.getItemStack((short) i);
    @IS@ w = null;
    if (i < n && i < src.length) w = src[i];
    boolean we = w == null || w.isEmpty();
    if (s.ctrlLive(i)) {
      if (!we) return false;
      if (!@PKG@.VBtn.same(v, c[i - s.base])) return false;
      continue;
    }
    boolean ve = v == null || v.isEmpty();
    if (ve != we) return false;
    if (!ve && (!v.getItemId().equals(w.getItemId()) || v.getQuantity() != w.getQuantity())) return false;
  }
  return true;
}""")
# 0.1.2 arrowLayout=inside, whole vault full: this page shows a stored stack instead of an arrow
M(vs, r"""
public static void blockedNote(@PKG@.VSession s) {
  if (s.layout != 2) return;
  if (!s.ctrlLive(s.prevIdx) || !s.ctrlLive(s.nextIdx)) tell(s.pr, "-Your vault is full - free a slot on this page to get the arrow back. /vault next still works.");
}""")
# 0.1.2 review: every session view is a VView, also with pageArrows=false (identical for every allowed move; a retired DENY_ALL view
# that is still on screen answers a shift-click / Take All with a failed transaction instead of the engine's NullPointerException)
M(vs, r"""
public static @PKG@.VSession newSession(@PR@ pr, java.util.UUID u, @PKG@.VData d, int page, int mode) {
  @PKG@.VSession s = new @PKG@.VSession();
  s.owner = u; s.viewer = u; s.pr = pr; s.page = page; s.mode = mode;
  int sz = d.cap;
  int cap = sz;
  s.store = sz; s.usable = sz; s.layout = 0; s.base = sz; s.span = 0;
  if (@PKG@.VCfg.ARROWS) {
    if ("inside".equals(@PKG@.VCfg.ARROW_LAYOUT)) {
      int lo = ((sz - 1) / 9) * 9;
      if (sz - lo < 2) lo = sz - 2;
      if (lo >= 0 && sz >= 2) { s.layout = 2; s.base = lo; s.span = sz - lo; s.prevIdx = lo; s.infoIdx = -1; s.nextIdx = sz - 1; }
    } else {
      int r9 = ((sz + 8) / 9) * 9;
      if (r9 + 9 <= 30000) { s.layout = 1; s.base = sz; s.span = r9 + 9 - sz; s.prevIdx = r9; s.infoIdx = r9 + 4; s.nextIdx = r9 + 8; cap = r9 + 9; }
    }
  }
  s.sid = SERIAL.incrementAndGet();
  s.view = new @PKG@.VView((short) cap);
  s.epoch = @PKG@.VCfg.bridge().get("profile:epoch:" + u);
  if (s.layout != 0) {
    @PKG@.VBtnFilter f = new @PKG@.VBtnFilter(s);
    for (int i = s.base; i < s.base + s.span; i++) {
      if (s.layout == 2 && i != s.prevIdx && i != s.nextIdx) continue;
      s.view.setSlotFilter(@FAT@.ADD, (short) i, f);
      s.view.setSlotFilter(@FAT@.REMOVE, (short) i, f);
      s.view.setSlotFilter(@FAT@.DROP, (short) i, f);
    }
  }
  s.swapping = true;
  boolean ok = false;
  try {
    reserve(s, d, page);
    @IS@[] src = d.pageCopy(page);
    @PKG@.VBtn.row(s, d, page, src, true);
    ok = fill(s, src);
  } catch (Throwable t) { @PKG@.VCfg.warn("vault view fill failed for " + u + ": " + t); ok = false; }
  s.swapping = false;
  if (!ok) return null;
  blockedNote(s);
  s.window = new @PKG@.VWindow(s.view, s);
  s.reg = s.view.registerChangeEvent(new @PKG@.VChange(s));
  return s;
}""")
# show another page in the SAME view: old page synced first; a view that does not read back exactly closes without syncing.
# 0.1.2: then (inside layout) the target page's arrow slots are cleared, the control row is rebuilt for the target page and filled
M(vs, r"""
public static String swap(@PKG@.VSession s, int page) {
  if (s == null || s.closed) return "-Your vault is not open.";
  if (page == s.page) return null;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d == null) return "-Your vault is not loaded.";
  if (page < 1 || page > d.unlocked) return "-Vault page " + page + " is locked.";
  s.swapping = true;
  try { syncView(s); }
  catch (Throwable t) { s.swapping = false; @PKG@.VCfg.warn("vault sync before swap failed for " + s.owner + ": " + t); return "-Could not switch pages right now - try again."; }
  String r = null;
  try {
    reserve(s, d, page);
    @IS@[] src = d.pageCopy(page);
    @PKG@.VBtn.row(s, d, page, src, true);
    if (fill(s, src)) s.page = page;
    else { s.noSync = true; r = "-Could not show page " + page + " - your vault closed to keep your items safe (nothing was lost)."; }
  } catch (Throwable t) {
    s.noSync = true;
    r = "-Could not show page " + page + " - your vault closed to keep your items safe (nothing was lost).";
    @PKG@.VCfg.warn("vault swap failed for " + s.owner + ": " + t);
  }
  s.swapping = false;
  if (r == null) { LAST.put(s.owner, Integer.valueOf(page)); blockedNote(s); }
  return r;
}""")
M(vs, r"""
public static boolean visible(@PLA@ p, @PKG@.VSession s) {
  try {
    Object cp = p.getPageManager().getCustomPage();
    if (s.mode == 1) return cp != null && cp == s.pageObj;
    return cp == null;
  } catch (Throwable t) { return false; }
}""")
M(vs, r"""
public static void refreshPage(@PLA@ p, @PKG@.VSession s) {
  try {
    Object cp = p.getPageManager().getCustomPage();
    if (cp != null && cp == s.pageObj && cp instanceof @PKG@.VaultPage) ((@PKG@.VaultPage) cp).refresh();
  } catch (Throwable t) { }
}""")
# 0.1.2 (world thread): redraw the control row of the page on screen from the vault's current state (after a buy, a stale click);
# storage is not touched. A live control slot that holds a real item is left to the next click batch (rescue, never cleared).
M(vs, r"""
public static void refreshRow(@PKG@.VSession s) {
  if (s == null || s.closed || s.layout == 0) return;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d == null) return;
  s.swapping = true;
  try {
    @PKG@.VBtn.row(s, d, s.page, (@IS@[]) null, false);
    @IS@[] c = s.ctrl;
    for (int i = 0; i < c.length; i++) {
      int slot = s.base + i;
      if (c[i] == null || !s.ctrlLive(slot)) continue;
      @IS@ v = s.view.getItemStack((short) slot);
      if (v != null && !v.isEmpty() && !@PKG@.VBtn.isButton(v)) continue;
      s.view.setItemStackForSlot((short) slot, c[i], false);
    }
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("row-" + s.owner, "vault arrow row redraw failed for " + s.owner + ": " + t); }
  s.swapping = false;
}""")
# make room for a new view: a window that is part of the page on screen is RETIRED (the new page replaces it - never close a page right
# before opening another), a window that is not on screen is closed now, a session without a window is finalized
M(vs, r"""
public static void release(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  if (s == null || s.closed) return;
  if (!registered(p, s)) { finalizeWorld(s); return; }
  if (visible(p, s)) { retire(s); return; }
  closeRegistered(p, ref, st, s);
}""")
# open (or re-show) the vault. Returns null (page opened, nothing to say) or a "+/-/=" line for chat.
# 0.1.3: info = the result line a NEW page-mode VaultPage shows at once (the confirm window returning to the vault; null = none)
M(vs, r"""
public static String open2(@PR@ pr, @REF@ ref, @ST@ st, int page, int mode, String info) {
  java.util.UUID u = pr.getUuid();
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  String g = gate(u);
  if (g != null) return g;
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  @PKG@.VStore.noteName(d, pr.getUsername());
  if (page < 1) page = 1;
  if (page > d.unlocked) {
    if (d.unlocked < @PKG@.VCfg.MAX_PAGES) return "-Vault page " + page + " is locked - you own " + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + " pages. Page " + (d.unlocked + 1) + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(d.unlocked + 1)) + " coins - /vault buy";
    return "-You own " + d.unlocked + " vault pages - there is no page " + page + ".";
  }
  @PKG@.VSession ex = current(u);
  if (ex != null) {
    boolean reg = registered(p, ex);
    if (reg && ex.mode == mode && visible(p, ex)) {
      String r = swap(ex, page);
      if (r != null) { closeAny(p, ref, st, ex); return r; }
      if (mode == 1) refreshPage(p, ex);
      return "=Showing vault page " + page + " of " + d.unlocked + ".";
    }
    release(p, ref, st, ex);
  }
  @PKG@.VSession s = newSession(pr, u, d, page, mode);
  if (s == null) return "-Could not show vault page " + page + " - nothing was changed.";
  SESSIONS.put(u, s);
  LAST.put(u, Integer.valueOf(page));
  boolean ok = false;
  try {
    if (mode == 1) {
      @PKG@.VaultPage vp = new @PKG@.VaultPage(pr, s, page);
      if (info != null) vp.info = info;
      s.pageObj = vp;
      ok = p.getPageManager().openCustomPageWithWindows(ref, st, vp, new @WIN@[] { s.window });
    } else {
      ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Bench, true, new @WIN@[] { s.window });
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault open failed for " + u + ": " + t); ok = false; }
  if (!ok) {
    closeAny(p, ref, st, s);
    return "-The vault window could not open - nothing was changed.";
  }
  // 0.1.5: the opening line names the instant gestures (a plain click on an arrow item only lifts it until it is put back)
  if (mode == 2 && s.layout != 0) return "=Vault page " + page + " of " + d.unlocked + " (shared by all your profiles): shift-click an arrow (or press Drop on it) to turn pages at once, or click it twice. Esc saves. /vault <page> jumps.";
  if (mode == 2) return "=Vault page " + page + " of " + d.unlocked + " (shared by all your profiles): drag items in and out, Esc saves. /vault next or /vault <page> switches pages.";
  return null;
}""")
M(vs, r"""
public static String open(@PR@ pr, @REF@ ref, @ST@ st, int page, int mode) {
  return open2(pr, ref, st, page, mode, (String) null);
}""")
M(vs, r"""
public static String openDefault(@PR@ pr, @REF@ ref, @ST@ st, int page) {
  return open(pr, ref, st, page, @PKG@.VCfg.PAGE_MODE ? 1 : 2);
}""")
M(vs, r"""
public static int lastPage(java.util.UUID u) {
  Object l = LAST.get(u);
  if (l instanceof Integer) return ((Integer) l).intValue();
  return 1;
}""")
# /vault pages: page mode = the normal page; chest mode = the page with the buttons and no slots (its Open button opens a chest)
M(vs, r"""
public static String openNav(@PR@ pr, @REF@ ref, @ST@ st) {
  java.util.UUID u = pr.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  int pg = lastPage(u);
  if (pg < 1 || pg > d.unlocked) pg = 1;
  if (@PKG@.VCfg.PAGE_MODE) return open(pr, ref, st, pg, 1);
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  @PKG@.VSession s = current(u);
  if (s != null) { pg = s.page; release(p, ref, st, s); }
  p.getPageManager().openCustomPage(ref, st, new @PKG@.VaultPage(pr, (@PKG@.VSession) null, pg));
  return null;
}""")
M(vs, r"""
public static String step(@PR@ pr, @REF@ ref, @ST@ st, int delta) {
  java.util.UUID u = pr.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  @PKG@.VSession s = current(u);
  int base = s != null ? s.page : lastPage(u);
  int t = base + delta;
  if (t < 1) return "-You are on the first vault page.";
  if (t > d.unlocked) {
    if (t <= @PKG@.VCfg.MAX_PAGES) return "-Vault page " + t + " is locked - /vault buy unlocks it for " + @PKG@.VStore.grp(@PKG@.VStore.price(t)) + " coins.";
    return "-That is your last vault page.";
  }
  int mode = s != null ? s.mode : (@PKG@.VCfg.PAGE_MODE ? 1 : 2);
  return open(pr, ref, st, t, mode);
}""")
# a page click on a live page-mode session; a failed swap closes the session (without syncing a bad view)
M(vs, r"""
public static String pageSwap(@PKG@.VaultPage vp, @REF@ ref, @ST@ st, int t) {
  @PKG@.VSession s = vp.sess;
  if (s == null || s.closed) return "-Your vault slots closed - click a page to open them again.";
  String g = gate(s.owner);
  if (g != null) return g;
  String r = swap(s, t);
  if (r != null) {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) closeAny(p, ref, st, s); else finalizeWorld(s);
  }
  return r;
}""")
# after /vault buy (bought or refused): the player's own vault page on screen (with or without slots) shows the new state + the result
M(vs, r"""
public static void afterBuy(@PR@ pr, @REF@ ref, @ST@ st, String res) {
  try { refreshRow(current(pr.getUuid())); } catch (Throwable t) { }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    Object cp = p.getPageManager().getCustomPage();
    if (cp instanceof @PKG@.VaultPage) ((@PKG@.VaultPage) cp).refreshWith(res);
  } catch (Throwable t) { }
}""")
# ================= 0.1.3: the confirm window flow (LOCKED Skyy 2026-09-25: buyConfirmCoins) =================
# open the "Buy page X for Y coins?" window for page `page` (world thread). The vault view on screen (page mode or the chest window) is
# RETIRED first (DENY_ALL + synced + marked closed, the 0.1.1 "the new page replaces it" rule: a page is never closed right before
# another opens), then the window opens, and only then the retired vault window is closed (a stale window must not come back next to
# the chest when the window returns to the vault; a second click / shift-click packet on the old arrows can never reach a filter again).
# A window already on screen for the same page is kept (a second /vault buy or click never stacks windows or charges) while it is
# live (VBuyDlg.live: not acted, same world, under 2 min old); a dead one is marked done and a fresh window replaces it. Returns null
# (window opened) or a chat line (nothing was charged).
M(vs, r"""
public static String askBuy(@PR@ pr, @REF@ ref, @ST@ st, @PLA@ p, @PKG@.VSession s, int page, int ret, int back) {
  if (pr == null || p == null || ref == null || st == null) return "-The confirm window cannot open right now - nothing was charged.";
  try {
    Object cp = p.getPageManager().getCustomPage();
    if (cp instanceof @PKG@.VBuyDlg) {
      @PKG@.VBuyDlg o = (@PKG@.VBuyDlg) cp;
      java.util.UUID now = null;
      try { now = pr.getWorldUuid(); } catch (Throwable t2) { now = null; }
      if (o.page == page && o.live(now)) return "=Confirm or cancel the purchase in the window on your screen.";
      o.done = true;
    }
  } catch (Throwable t) { }
  @PKG@.VWindow old = null;
  if (s != null && !s.closed) {
    if (registered(p, s)) old = s.window;
    release(p, ref, st, s);
  }
  @PKG@.VBuyDlg dlg = new @PKG@.VBuyDlg(pr, page, @PKG@.VStore.price(page), ret, back);
  boolean shown = false;
  try { p.getPageManager().openCustomPage(ref, st, dlg); shown = true; }
  catch (Throwable t) { @PKG@.VCfg.warn("vault confirm window failed for " + pr.getUuid() + ": " + t); }
  // the retired vault window is closed either way (a dead DENY_ALL chest must not stay on screen when the window could not open)
  if (old != null && s != null && s.closed && registered(p, s)) {
    try { p.getWindowManager().closeWindow(ref, old.getId(), st); } catch (Throwable t) { @PKG@.VCfg.warnOnce("dlgclose-" + s.owner, "vault: the old vault window could not be closed behind the confirm window: " + t); }
    dispatchSweep(pr, "close");
  }
  if (!shown) return "-The confirm window could not open - nothing was charged. /vault opens your vault.";
  return null;
}""")
# the window's Buy (world thread): one purchase of exactly dlg.page (VStore.buy: expected page, one at a time per player, profile:busy
# refused, coins first). The window is one-shot (done is set by the caller before this runs).
M(vs, r"""
public static String dlgBuy(@PKG@.VBuyDlg dlg) {
  String name = "";
  try { if (dlg.pr != null) name = dlg.pr.getUsername(); } catch (Throwable t) { name = ""; }
  return @PKG@.VStore.buyAt(dlg.u, name, dlg.page, dlg.cost);
}""")
# after Buy / Cancel (world thread, inside the window's click): back to where the player came from, on page `pg` (the new page after a
# buy, else dlg.back). Opening the vault REPLACES the window (never closed first). res = the result line: chat always for a purchase or
# a refusal (+/-), and on the vault page's info line in page mode.
# 0.1.3 review fix: pg is clamped to an OWNED page first - dlg.back can be a locked page (/vault buy while the vault page had a locked
# page selected sets back = that selection), and Cancel must return to the vault, not show a red "locked" line from open2.
M(vs, r"""
public static void dlgBack(@PKG@.VBuyDlg dlg, @REF@ ref, @ST@ st, int pg, String res) {
  @PKG@.VData d = @PKG@.VStore.load(dlg.u);
  if (d != null && pg > d.unlocked) pg = d.unlocked;
  if (pg < 1) pg = 1;
  @PR@ pr = dlg.pr;
  boolean loud = res != null && res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-');
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { tell(pr, res); return; }
  String r = null;
  if (dlg.ret == 1) {
    if (loud) tell(pr, res);
    r = open2(pr, ref, st, pg, 1, res);
  } else if (dlg.ret == 2) {
    tell(pr, res);
    r = open2(pr, ref, st, pg, 2, (String) null);
  } else if (dlg.ret == 3) {
    if (loud) tell(pr, res);
    try {
      @PKG@.VaultPage vp = new @PKG@.VaultPage(pr, (@PKG@.VSession) null, pg);
      vp.info = res == null ? "" : res;
      p.getPageManager().openCustomPage(ref, st, vp);
    } catch (Throwable t) { r = "-The vault page could not open - /vault pages opens it."; }
  } else {
    tell(pr, res);
    try { p.getPageManager().setPage(ref, st, @PGE@.None); } catch (Throwable t) { }
    return;
  }
  if (r == null) return;
  tell(pr, r);
  if (!r.startsWith("=")) {
    try {
      if (p.getPageManager().getCustomPage() == dlg) p.getPageManager().setPage(ref, st, @PGE@.None);
    } catch (Throwable t) { }
  }
}""")
# /vault buy (world thread): the shared rule. At or above buyConfirmCoins the window opens and returns to what was on screen (the
# vault page view, the vault chest, the /vault pages page, or nothing).
M(vs, r"""
public static void cmdBuy(@PR@ pr, @REF@ ref, @ST@ st) {
  java.util.UUID u = pr.getUuid();
  String res = @PKG@.VStore.intent(u, pr.getUsername(), 0);
  if (res == null || !res.startsWith("?")) {
    tell(pr, res);
    afterBuy(pr, ref, st, res);
    return;
  }
  int pg = 0;
  try { pg = Integer.parseInt(res.substring(1)); } catch (Throwable t) { pg = 0; }
  if (pg < 1) { tell(pr, "-Nothing was charged - try again."); return; }
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @PKG@.VSession s = current(u);
  int ret = 0;
  int back = 1;
  if (p != null) {
    Object cp = null;
    try { cp = p.getPageManager().getCustomPage(); } catch (Throwable t) { cp = null; }
    if (s != null && registered(p, s) && visible(p, s)) { ret = s.mode == 1 ? 1 : 2; back = s.page; }
    else if (cp instanceof @PKG@.VaultPage) {
      @PKG@.VaultPage vp = (@PKG@.VaultPage) cp;
      ret = (vp.sess != null && @PKG@.VCfg.PAGE_MODE) ? 1 : 3;
      back = vp.sel;
    } else if (cp instanceof @PKG@.VBuyDlg && ((@PKG@.VBuyDlg) cp).page == pg) {
      // 0.1.3 review hardening: only a LIVE window (not acted, same world, under 2 min old) blocks; a dead one falls through to askBuy,
      // which marks it done and opens a fresh window (ret 0: the vault is not on screen)
      java.util.UUID now = null;
      try { now = pr.getWorldUuid(); } catch (Throwable t) { now = null; }
      if (((@PKG@.VBuyDlg) cp).live(now)) { tell(pr, "=Confirm or cancel the purchase in the window on your screen."); return; }
    }
  }
  String r = askBuy(pr, ref, st, p, s, pg, ret, back);
  if (r != null) tell(pr, r);
}""")
M(vs, r"""
public static void windowClosed(@PKG@.VSession s) {
  finalizeWorld(s);
}""")
# ValidatedWindow.validate (engine calls it on player movement): false closes the window
M(vs, r"""
public static boolean stillValid(@PKG@.VSession s, @REF@ ref, @CA@ a) {
  if (s == null || s.closed) return false;
  try { if (@PKG@.VCfg.bridge().get("profile:busy:" + s.owner) != null) return false; } catch (Throwable t) { }
  try {
    @PLA@ p = (@PLA@) a.getComponent(ref, @PLA@.getComponentType());
    if (p != null) {
      Object cp = p.getPageManager().getCustomPage();
      if (s.mode == 1 && cp != s.pageObj) return false;
      if (s.mode == 2 && cp != null) return false;
    }
  } catch (Throwable t) { }
  return true;
}""")
M(vs, r"""
public static void dispatchClose(@PKG@.VSession s, String why, boolean onlyIfPageGone) {
  try {
    java.util.UUID wu = s.pr.getWorldUuid();
    @WLD@ w = null;
    if (wu != null) w = @UNI@.get().getWorld(wu);
    if (w == null) return;
    w.execute(new @PKG@.VCloseTask(s, why, wu, onlyIfPageGone, false));
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("close-" + s.owner, "could not schedule the vault close for " + s.owner + ": " + t); }
}""")
# a session whose viewer has been gone 10 s: retire the view (its window died with the entity; the view is only synced + made inert)
M(vs, r"""
public static void offlineFinalize(@PKG@.VSession s) {
  if (s == null || s.closed) return;
  retire(s);
  @PKG@.VStore.log("FINALIZE-OFFLINE " + s.owner + " page " + s.page);
}""")
# ... on the world thread the view was shown in (serialized with a late engine close there). No such world any more, or it refuses the
# task = nothing can still reach the view: retire it here. tickOne retires it itself if the task has not run 10 s later.
M(vs, r"""
public static void dispatchOffline(@PKG@.VSession s) {
  @WLD@ w = null;
  java.util.UUID wu = null;
  try {
    wu = s.pr.getWorldUuid();
    if (wu != null) w = @UNI@.get().getWorld(wu);
  } catch (Throwable t) { w = null; }
  if (w != null) {
    try {
      @PKG@.VCloseTask ct = new @PKG@.VCloseTask(s, (String) null, wu, false, false);
      ct.offline = true;
      w.execute(ct);
      return;
    } catch (Throwable t) { @PKG@.VCfg.warnOnce("offline-" + s.owner, "world " + wu + " refused the vault finalize for " + s.owner + " (finalized here): " + t); }
  }
  offlineFinalize(s);
}""")
# world thread (or a scheduler hop first): close the session's window and our page; tell the player why
M(vs, r"""
public static void closeTask(@PKG@.VCloseTask t) {
  @PKG@.VSession s = t.sess;
  if (s == null || s.closed) return;
  if (t.offline) { offlineFinalize(s); return; }
  if (t.hop) { dispatchClose(s, t.reason, t.onlyIfPageGone); return; }
  @PR@ pr = s.pr;
  java.util.UUID wu = pr.getWorldUuid();
  if (wu == null || !wu.equals(t.wu)) {
    if (t.tries < 3) { t.tries = t.tries + 1; dispatchClose(s, t.reason, t.onlyIfPageGone); }
    return;
  }
  @REF@ ref = pr.getReference();
  if (ref == null) return;
  @ST@ st = ref.getStore();
  if (st == null) return;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  Object cp = p.getPageManager().getCustomPage();
  boolean ours = s.pageObj != null && cp == s.pageObj;
  if (t.onlyIfPageGone && ours) return;
  closeAny(p, ref, st, s);
  if (ours) { try { p.getPageManager().setPage(ref, st, @PGE@.None); } catch (Throwable e) { } }
  if (t.reason != null) tell(pr, t.reason);
}""")
# our page was dismissed (Esc / replaced): if the client did not close the slots with it, close them 1.5 s later
M(vs, r"""
public static void dismissed(@PKG@.VSession s) {
  if (s == null || s.closed) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.VCloseTask(s, (String) null, (java.util.UUID) null, true, true), 1500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { dispatchClose(s, (String) null, true); }
}""")
# ================= 0.1.2: stray sweep, re-send, rescue, click batches (all WORLD THREAD) =================
M(vs, r"""
public static @CT@ invType(int i) {
  if (i == 0) return @HOT@.getComponentType();
  if (i == 1) return @STO@.getComponentType();
  if (i == 2) return @BAK@.getComponentType();
  if (i == 3) return @ARM@.getComponentType();
  if (i == 4) return @UTI@.getComponentType();
  if (i == 5) return @TOO@.getComponentType();
  return null;
}""")
M(vs, r"""
public static @IC@ section(@ST@ st, @REF@ ref, int i) {
  @CT@ t = invType(i);
  if (t == null) return null;
  @INVC@ c = (@INVC@) st.getComponent(ref, t);
  return c == null ? null : c.getInventory();
}""")
# the engine re-sends only the inventory sections whose component is dirty (PlayerSendInventorySystem), so all six are marked
M(vs, r"""
public static void markInv(@ST@ st, @REF@ ref) {
  for (int i = 0; i < 6; i++) {
    try {
      @INVC@ c = (@INVC@) st.getComponent(ref, invType(i));
      if (c != null) c.markDirty();
    } catch (Throwable t) { }
  }
}""")
# the truth to the client next tick: the vault window (Window.invalidate -> UpdateWindow) and the whole player inventory (markDirty)
# 0.1.5 fix: through VWindow.resend() - the direct call of the protected Window.invalidate() here was an IllegalAccessError (0.1.2-0.1.4)
M(vs, r"""
public static void resync(@PKG@.VSession s, @REF@ ref, @ST@ st) {
  try { if (s.window != null) s.window.resend(); } catch (Throwable t) { }
  try { markInv(st, ref); } catch (Throwable t) { }
}""")
# every vault arrow item in container c is removed (own = the player's own live vault view: storage indices only); vault.log STRAY
M(vs, r"""
public static int sweepBox(@IC@ c, @PKG@.VSession own, String where, String who) {
  if (c == null) return 0;
  int cap = c.getCapacity();
  int n = 0;
  for (int i = 0; i < cap; i++) {
    if (own != null && !own.isStorage(i)) continue;
    @IS@ x = c.getItemStack((short) i);
    if (!@PKG@.VBtn.isButton(x)) continue;
    long sid = @PKG@.VBtn.sidOf(x);
    boolean ok = false;
    try { @STX@ t = c.removeItemStackFromSlot((short) i, false); ok = t != null && t.succeeded(); } catch (Throwable e) { ok = false; }
    if (ok) { n++; @PKG@.VStore.log("STRAY " + who + " " + where + ":" + i + " " + x.getItemId() + " sid=" + sid); }
  }
  return n;
}""")
M(vs, r"""
public static int countBtns(@IC@ c, @PKG@.VSession own) {
  if (c == null) return 0;
  int cap = c.getCapacity();
  int n = 0;
  for (int i = 0; i < cap; i++) {
    if (own != null && !own.isStorage(i)) continue;
    if (@PKG@.VBtn.isButton(c.getItemStack((short) i))) n++;
  }
  return n;
}""")
# one sweep of player pr: the six inventory sections + every open item-container window (own vault window: storage only). Skipped
# while profile:busy (crash recovery is about to replace the inventory; the next period retries). Counted after: a rescan must find 0.
# Caller: the player's CURRENT world thread (sweepRun checks it; btnBatch checks it).
M(vs, r"""
public static void sweepPlayer(@PR@ pr, String why) {
  if (pr == null || !pr.isValid()) return;
  java.util.UUID u = pr.getUuid();
  if (u == null || @PKG@.VCfg.bridge().get("profile:busy:" + u) != null) return;
  @REF@ ref = pr.getReference();
  if (ref == null || !ref.isValid()) return;
  @ST@ st = ref.getStore();
  if (st == null) return;
  String who = pr.getUsername() + " " + u;
  int found = 0;
  int left = 0;
  for (int i = 0; i < 6; i++) {
    @IC@ c = null;
    try { c = section(st, ref, i); } catch (Throwable t) { c = null; }
    if (c == null) continue;
    found = found + sweepBox(c, (@PKG@.VSession) null, SECTIONS[i], who);
    left = left + countBtns(c, (@PKG@.VSession) null);
  }
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p != null) {
    try {
      @PKG@.VSession own = current(u);
      java.util.List ws = p.getWindowManager().getWindows();
      for (int k = 0; ws != null && k < ws.size(); k++) {
        Object w = ws.get(k);
        if (!(w instanceof @ICW@)) continue;
        @IC@ c = ((@ICW@) w).getItemContainer();
        @PKG@.VSession o = null;
        if (own != null && w == own.window) o = own;
        String where = "window" + ((@WIN@) w).getId();
        found = found + sweepBox(c, o, where, who);
        left = left + countBtns(c, o);
      }
    } catch (Throwable t) { @PKG@.VCfg.warnOnce("sweepw-" + u, "vault stray check of the open windows of " + who + " failed: " + t); }
  }
  if (found > 0) {
    @PKG@.VCfg.warn("removed " + found + " stray vault arrow item(s) from " + who + " (" + why + ") - see vault.log");
    markInv(st, ref);
  }
  if (left > 0) @PKG@.VCfg.warnOnce("strayleft-" + u, "could not remove " + left + " vault arrow item(s) from " + who + " (" + why + ") - see vault.log");
}""")
M(vs, r"""
public static void sweepRun(@PKG@.VSweepTask t) {
  if (t == null || t.pr == null || !t.pr.isValid()) return;
  java.util.UUID now = t.pr.getWorldUuid();
  if (now == null || !now.equals(t.wu)) {
    if (t.tries < 3) dispatchSweep2(t.pr, t.why, t.tries + 1);
    return;
  }
  sweepPlayer(t.pr, t.why);
}""")
# a REAL stack found in a live control slot (impossible while ADD is refused - defensive): never cleared. In order: the first free
# storage slot of the page on screen, the player's storage / hotbar, the first free slot of any other owned page, thrown at the
# player's feet (the vanilla drop call). Each step is read back / counted and logged (vault.log RESCUE ...).
# 0.1.2 review: returns true = control slot `slot` no longer holds the real stack (the caller may put the arrow back); false = it is
# still there (the caller must NOT overwrite it). A storage write that does not read back is undone before the next candidate slot,
# so the stack can never sit in an earlier slot AND go on to a later step (no duplicate).
M(vs, r"""
public static boolean rescue(@PKG@.VSession s, int slot, @IS@ v, @REF@ ref, @ST@ st) {
  String who = (s.pr == null ? "?" : s.pr.getUsername()) + " " + s.owner;
  String what = v.getItemId() + " x" + v.getQuantity();
  @STX@ out = null;
  try { out = s.view.removeItemStackFromSlot((short) slot, false); } catch (Throwable t) { out = null; }
  if (out == null || !out.succeeded()) {
    @IS@ still = null;
    try { still = s.view.getItemStack((short) slot); } catch (Throwable t) { still = v; }
    if (still != null && !still.isEmpty()) { @PKG@.VStore.log("RESCUE-FAIL " + who + " control slot " + slot + " " + what + " (left in place)"); return false; }
    @PKG@.VStore.log("RESCUE-FAIL " + who + " control slot " + slot + " " + what + " (the removal failed but the slot is empty - nothing moved)");
    return true;
  }
  int cap = s.view.getCapacity();
  for (int i = 0; i < cap; i++) {
    if (!s.isStorage(i)) continue;
    @IS@ x = s.view.getItemStack((short) i);
    if (x != null && !x.isEmpty()) continue;
    s.view.setItemStackForSlot((short) i, v, false);
    @IS@ back = s.view.getItemStack((short) i);
    if (back != null && !back.isEmpty() && back.getItemId().equals(v.getItemId()) && back.getQuantity() == v.getQuantity()) {
      @PKG@.VStore.log("RESCUE " + who + " control slot " + slot + " -> page " + s.page + " slot " + i + " " + what);
      return true;
    }
    if (back != null && !back.isEmpty()) {
      try { s.view.removeItemStackFromSlot((short) i, false); } catch (Throwable t) { }
      @IS@ gone = s.view.getItemStack((short) i);
      if (gone != null && !gone.isEmpty()) {
        @PKG@.VStore.log("RESCUE-PARTIAL " + who + " control slot " + slot + " -> page " + s.page + " slot " + i + " holds " + gone.getItemId() + " x" + gone.getQuantity() + " of " + what + " (did not read back and could not be undone - check by hand)");
        @PKG@.VCfg.warn("vault rescue for " + who + " left " + gone.getItemId() + " x" + gone.getQuantity() + " in page " + s.page + " slot " + i + " (wanted " + what + ") - see vault.log");
        return true;
      }
    }
  }
  @IS@ rest = v;
  if (ref != null && st != null) {
    for (int k = 0; k < 2; k++) {
      if (rest == null || rest.isEmpty()) break;
      @IC@ c = null;
      try { c = section(st, ref, k == 0 ? 1 : 0); } catch (Throwable t) { c = null; }
      if (c == null) continue;
      try {
        @ISX@ tx = c.addItemStack(rest);
        if (tx != null && tx.succeeded()) rest = tx.getRemainder();
      } catch (Throwable t) { }
    }
    if (rest == null || rest.isEmpty()) {
      @PKG@.VStore.log("RESCUE " + who + " control slot " + slot + " -> inventory " + what);
      markInv(st, ref);
      return true;
    }
  }
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d != null) {
    String at = d.putFirstFree(s.page, s.layout == 2 ? s.prevIdx : -1, s.layout == 2 ? s.nextIdx : -1, rest);
    if (at != null) {
      @PKG@.VStore.log("RESCUE " + who + " control slot " + slot + " -> vault page:slot " + at + " " + rest.getItemId() + " x" + rest.getQuantity());
      @PKG@.VStore.saveSoon(s.owner, 0L);
      return true;
    }
  }
  try {
    if (ref != null && st != null) {
      @IU@.throwItem(ref, rest, 6.0F, st);
      @PKG@.VStore.log("RESCUE " + who + " control slot " + slot + " -> thrown at the player's feet " + rest.getItemId() + " x" + rest.getQuantity());
      return true;
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault rescue throw failed for " + who + ": " + t); }
  @PKG@.VStore.log("RESCUE-LOST " + who + " control slot " + slot + " " + rest.getItemId() + " x" + rest.getQuantity() + " (nowhere to put it - restore by hand)");
  @PKG@.VCfg.warn("RESCUE-LOST: a " + rest.getItemId() + " x" + rest.getQuantity() + " of " + who + " had nowhere to go - see vault.log");
  return true;
}""")
# the canonical row back (count before and after): stray buttons in storage removed, every live control slot = its canonical stack
# (a real stack there is rescued first; one the rescue could not move is left in place, never overwritten: the recount then fails,
# the caller closes the view and finalizeWorld's keepCtrl moves it into the vault). 0 = the view matches; -1 = it does not.
M(vs, r"""
public static int restoreCtrl(@PKG@.VSession s, @REF@ ref, @ST@ st) {
  int cap = s.view.getCapacity();
  String who = (s.pr == null ? "?" : s.pr.getUsername()) + " " + s.owner;
  @IS@[] c = s.ctrl;
  for (int i = 0; i < cap; i++) {
    if (!s.isStorage(i)) continue;
    @IS@ x = s.view.getItemStack((short) i);
    if (!@PKG@.VBtn.isButton(x)) continue;
    @STX@ t = null;
    try { t = s.view.removeItemStackFromSlot((short) i, false); } catch (Throwable e) { t = null; }
    if (t != null && t.succeeded()) @PKG@.VStore.log("STRAY view " + who + " page " + s.page + " slot " + i + " " + x.getItemId() + " sid=" + @PKG@.VBtn.sidOf(x));
  }
  if (s.layout == 0) return 0;
  for (int i = 0; i < c.length; i++) {
    int slot = s.base + i;
    if (c[i] == null || !s.ctrlLive(slot)) continue;
    @IS@ v = s.view.getItemStack((short) slot);
    if (@PKG@.VBtn.same(v, c[i])) continue;
    if (v != null && !v.isEmpty() && !@PKG@.VBtn.isButton(v)) {
      boolean gone = rescue(s, slot, v, ref, st);
      @IS@ after = s.view.getItemStack((short) slot);
      if (!gone || (after != null && !after.isEmpty() && !@PKG@.VBtn.isButton(after))) continue;
    }
    s.view.setItemStackForSlot((short) slot, c[i], false);
  }
  int btns = 0;
  int want = 0;
  for (int i = 0; i < cap; i++) {
    @IS@ x = s.view.getItemStack((short) i);
    if (@PKG@.VBtn.isButton(x)) btns++;
    if (s.ctrlLive(i)) {
      want++;
      if (!@PKG@.VBtn.same(x, c[i - s.base])) return -1;
    }
  }
  return btns == want ? 0 : -1;
}""")
# arrowLayout=inside: an arrow slot that was blocked by a stored stack and is empty now becomes an arrow again
M(vs, r"""
public static boolean relive(@PKG@.VSession s) {
  if (s.layout != 2) return false;
  boolean[] lv = s.live;
  boolean[] nl = new boolean[lv.length];
  for (int i = 0; i < lv.length; i++) nl[i] = lv[i];
  boolean ch = false;
  int b1 = s.prevIdx - s.base;
  int b2 = s.nextIdx - s.base;
  if (freed(s, s.prevIdx) && b1 >= 0 && b1 < nl.length) { nl[b1] = true; ch = true; }
  if (freed(s, s.nextIdx) && b2 >= 0 && b2 < nl.length) { nl[b2] = true; ch = true; }
  if (!ch) return false;
  syncView(s);
  s.live = nl;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d != null) @PKG@.VBtn.row(s, d, s.page, (@IS@[]) null, false);
  return true;
}""")
# one click on control slot `slot` (the batch decided it was exactly one). The action follows the vault's CURRENT state, not the item
# drawn (a row made stale by /vault buy or a freePages raise acts right and is redrawn).
M(vs, r"""
public static void btnClick(@PKG@.VSession s, @PLA@ p, @REF@ ref, @ST@ st, int slot) {
  @PR@ pr = s.pr;
  java.util.UUID u = s.owner;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(u);
  if (d == null) return;
  int unlocked = d.unlocked;
  int max = unlocked > @PKG@.VCfg.MAX_PAGES ? unlocked : @PKG@.VCfg.MAX_PAGES;
  int next = unlocked + 1;
  int want = @PKG@.VBtn.FILLER;
  if (slot == s.prevIdx) want = s.page > 1 ? @PKG@.VBtn.PREV : @PKG@.VBtn.PREV_OFF;
  else if (slot == s.nextIdx) {
    if (s.page < unlocked) want = @PKG@.VBtn.NEXT;
    else if (unlocked < @PKG@.VCfg.MAX_PAGES) want = @PKG@.VBtn.BUY;
    else want = @PKG@.VBtn.NEXT_OFF;
  } else if (slot == s.infoIdx) want = @PKG@.VBtn.INFO;
  if (want == @PKG@.VBtn.PREV || want == @PKG@.VBtn.NEXT) {
    int t = want == @PKG@.VBtn.PREV ? s.page - 1 : s.page + 1;
    String g = gate(u);
    if (g != null) { tell(pr, g); refreshRow(s); return; }
    String r = swap(s, t);
    if (r != null) { closeAny(p, ref, st, s); tell(pr, r); return; }
    if (s.mode == 1) refreshPage(p, s);
    tell(pr, "=Vault page " + t + " of " + unlocked + ".");
    return;
  }
  if (want == @PKG@.VBtn.BUY) {
    // 0.1.3 (LOCKED Skyy 2026-09-25): below buyConfirmCoins this click buys at once; at or above it the confirm window opens (the
    // vault view is retired first and the window returns to the vault on the new page). VStore.intent refuses a click within
    // BUY_GUARD_MS of a purchase, so a double click / a shift-click that arrives as two packets never buys two pages.
    String g = gate(u);
    if (g != null) { tell(pr, g); refreshRow(s); return; }
    String res = @PKG@.VStore.intent(u, pr == null ? "" : pr.getUsername(), next);
    if (res != null && res.startsWith("?")) {
      String r = askBuy(pr, ref, st, p, s, next, s.mode == 1 ? 1 : 2, s.page);
      if (r != null) {
        tell(pr, r);
        refreshRow(s);
        if (s.mode == 1 && !s.closed) refreshPage(p, s);
      }
      return;
    }
    tell(pr, res);
    if (res != null && res.startsWith("+") && d.unlocked >= next) {
      String r = swap(s, next);
      if (r != null) { closeAny(p, ref, st, s); tell(pr, r); return; }
    } else refreshRow(s);
    if (s.mode == 1) refreshPage(p, s);
    return;
  }
  if (want == @PKG@.VBtn.PREV_OFF) tell(pr, "=This is your first page.");
  else if (want == @PKG@.VBtn.NEXT_OFF) tell(pr, "=This is your last page (" + unlocked + " of " + max + ").");
  else if (want == @PKG@.VBtn.INFO) tell(pr, "=Vault page " + s.page + " of " + unlocked + " - " + d.used(s.page) + " of " + s.usable + " slots used. /vault <page> jumps to a page.");
  refreshRow(s);
  if (s.mode == 1 && want != @PKG@.VBtn.FILLER) refreshPage(p, s);
}""")
# VBtnTask: one batch of refused attempts / strays of session s (world thread, after the packet task that caused it): restore the row,
# re-send the truth, sweep the viewer, then decide. Exactly one distinct control slot and no storage move in the batch (or in the
# 100 ms before its first hit, review R4) = a click;
# anything else (Take All, Sort, merge-stack: 2+ slots; a storage move) = no page action. Hit counts are never used.
M(vs, r"""
public static void btnBatch(@PKG@.VSession s, java.util.UUID wu) {
  if (s == null) return;
  long packed = s.takeHits();
  if (s.closed || s.swapping) return;
  int mask = (int) (packed & 0xFFFFFFFFL);
  boolean changed = (packed >>> 32) != 0L;
  @PR@ pr = s.pr;
  if (pr == null || !pr.isValid()) return;
  java.util.UUID now = pr.getWorldUuid();
  if (wu == null || now == null || !now.equals(wu)) return;
  @REF@ ref = pr.getReference();
  if (ref == null || !ref.isValid()) return;
  @ST@ st = ref.getStore();
  if (st == null) return;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  int ok = -1;
  s.inBatch = true;
  try {
    relive(s);
    s.swapping = true;
    try { ok = restoreCtrl(s, ref, st); } catch (Throwable t) { @PKG@.VCfg.warn("vault arrow row restore failed for " + s.owner + ": " + t); ok = -1; }
    s.swapping = false;
    syncView(s);
  } catch (Throwable t) { s.swapping = false; @PKG@.VCfg.warn("vault click batch failed for " + s.owner + ": " + t); }
  s.inBatch = false;
  resync(s, ref, st);
  try { sweepPlayer(pr, "click"); } catch (Throwable t) { }
  if (ok < 0) {
    @PKG@.VStore.log("ROW-MISMATCH " + s.owner + " page " + s.page + " (the vault window closed, nothing lost)");
    @PKG@.VCfg.warn("the vault arrow row of " + s.owner + " did not read back - the vault window closed to keep the items safe");
    closeAny(p, ref, st, s);
    tell(pr, "-Your vault closed to keep your items safe (nothing was lost). /vault opens it again.");
    return;
  }
  if (mask == 0 || changed || Integer.bitCount(mask) != 1) return;
  int slot = s.base + Integer.numberOfTrailingZeros(mask);
  if (!s.ctrlLive(slot)) return;
  if (current(s.owner) != s || !registered(p, s) || !visible(p, s)) return;
  btnClick(s, p, ref, st, slot);
}""")
# 0.1.5: the Drop key over a vault window slot (VDropSys, DropItemEvent$PlayerRequest: the player's world thread, inside the engine's
# DropItemStack task, BEFORE anything is removed). sec = the request's inventory section id (a window id for a window slot; the
# player's own sections are negative). Only a LIVE control slot (an arrow, the info item, a filler) of the player's OWN current vault
# window counts: the session is current (not closed / retired), its window is registered in the player's WindowManager and has
# exactly that id. Then the press is noted exactly like VBtnFilter's refused REMOVE (noteHit -> the ONE batch -> btnBatch: restore
# the row, re-send, sweep, and one control slot = a click) and true tells the caller to cancel the request: nothing is removed, so
# the engine logs no "attempted to drop an empty ItemStack!" WARNING. Everything else = false and the engine goes on as in 0.1.4
# (a vault storage slot drops its item; the arrow filter still refuses a control slot if this check ever misses one).
M(vs, r"""
public static boolean dropKey(@PR@ pr, @PLA@ p, int sec, int slot) {
  if (pr == null || p == null || sec <= 0 || slot < 0) return false;
  @PKG@.VSession s = current(pr.getUuid());
  if (s == null || s.closed || s.layout == 0 || s.window == null) return false;
  if (!registered(p, s) || s.window.getId() != sec) return false;
  if (!s.ctrlLive(slot)) return false;
  if (s.noteHit(slot)) queueBtn(s);
  return true;
}""")
# VDropSys.handle -> here: true = the request was ours and is now cancelled (never un-cancels anything)
M(vs, r"""
public static boolean dropEvent(@PR@ pr, @PLA@ p, @DIRQ@ e) {
  if (e == null) return false;
  if (!dropKey(pr, p, e.getInventorySectionId(), (int) e.getSlotId())) return false;
  e.setCancelled(true);
  return true;
}""")
M(vs, r"""
public static void tickOne(@UNI@ un, @PKG@.VSession s, long now) {
  if (s.closed) { SESSIONS.remove(s.owner, s); return; }
  @PR@ pr = un.getPlayer(s.viewer);
  if (pr == null || !pr.isValid()) {
    s.offline = s.offline + 1;
    if (s.offline == 10) dispatchOffline(s);
    else if (s.offline >= 20) offlineFinalize(s);
    return;
  }
  s.offline = 0;
  java.util.Map b = @PKG@.VCfg.bridge();
  String why = null;
  if (b.get("profile:busy:" + s.owner) != null) why = "=Your vault closed while your profile loads. Your items are safe.";
  else {
    Object ep = b.get("profile:epoch:" + s.owner);
    if (ep != null && s.epoch == null) s.epoch = ep;
    else if (ep != null && !ep.equals(s.epoch)) why = "=Your vault closed because your profile changed. Your items are safe - /vault opens it again in " + (@PKG@.VCfg.AFTER_SWITCH_MS / 1000L) + " s.";
  }
  if (why != null && now - s.askedClose > 5000L) { s.askedClose = now; dispatchClose(s, why, false); }
}""")
M(vs, r"""
public static void tick() {
  @UNI@ un = null;
  try { un = @UNI@.get(); } catch (Throwable t) { un = null; }
  if (un == null) return;
  long now = System.currentTimeMillis();
  try {
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid()) { noteBusy(p.getUuid()); noteEpoch(p.getUuid()); }
    }
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick-players", "vault tick (players) failed: " + t); }
  try {
    java.util.Iterator w = SWITCHED.entrySet().iterator();
    while (w.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) w.next();
      if (now - ((Long) e.getValue()).longValue() > 130000L) w.remove();
    }
  } catch (Throwable t) { }
  try { @PKG@.VStore.pruneBuys(now); } catch (Throwable t) { }
  // 0.1.2: stray-arrow sweeps - once when a player is first seen online (again after being offline; waits while profile:busy), and
  // every straySweepSeconds for every online player, each as a VSweepTask on that player's world thread
  try {
    boolean periodic = now - LAST_SWEEP >= @PKG@.VCfg.SWEEP_MS;
    if (periodic) LAST_SWEEP = now;
    java.util.HashSet seen = new java.util.HashSet();
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      java.util.UUID pu = p.getUuid();
      if (pu == null) continue;
      seen.add(pu);
      if (p.getWorldUuid() == null) continue;
      boolean first = !ONLINE.containsKey(pu);
      if (first) {
        if (@PKG@.VCfg.bridge().get("profile:busy:" + pu) != null) continue;
        ONLINE.put(pu, Long.valueOf(now));
        dispatchSweep(p, "join");
      } else if (periodic) dispatchSweep(p, "periodic");
    }
    java.util.Iterator oi = ONLINE.keySet().iterator();
    while (oi.hasNext()) { if (!seen.contains(oi.next())) oi.remove(); }
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick-sweep", "vault tick (stray check) failed: " + t); }
  java.util.Iterator si = SESSIONS.values().iterator();
  while (si.hasNext()) {
    @PKG@.VSession s = (@PKG@.VSession) si.next();
    try { tickOne(un, s, now); } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick-" + s.owner, "vault tick failed for " + s.owner + ": " + t); }
  }
}""")
# /vaultadmin open: a READ-ONLY COPY of one page (DENY_ALL, vanilla /invsee pattern); never a session, never saved.
# 0.1.2 review: the copy is a VView (no slot filters, no arrows), so an admin's shift-click / Take All on it gets a failed transaction
# instead of the engine's NullPointerException ("Failed to run task!") that the 0.1.1 plain SimpleItemContainer caused under DENY_ALL
M(vs, r"""
public static String adminView(@PR@ admin, @REF@ ref, @ST@ st, String who, int page) {
  java.util.UUID tu = @PKG@.VStore.resolve(who);
  if (tu == null) return "-No player or vault found for " + who + " - use an online name, a name seen before or a UUID.";
  @PKG@.VData d = @PKG@.VStore.load(tu);
  if (d == null) return "-That vault file cannot be read (it was not touched) - see the server log.";
  if (page < 1 || page > d.unlocked) return "-" + @PKG@.VStore.nameOf(d) + " owns vault pages 1 to " + d.unlocked + ".";
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  @PKG@.VSession own = current(admin.getUuid());
  if (own != null) release(p, ref, st, own);
  @IS@[] src = d.pageCopy(page);
  @SIC@ c = new @PKG@.VView((short) d.cap);
  for (int i = 0; i < src.length && i < d.cap; i++) {
    if (src[i] != null) c.setItemStackForSlot((short) i, src[i], false);
  }
  c.setGlobalFilter(@FT@.DENY_ALL);
  boolean ok = false;
  try { ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Bench, true, new @WIN@[] { new @CW@(c) }); } catch (Throwable t) { ok = false; }
  if (!ok) return "-The read-only window could not open.";
  @PKG@.VStore.log("ADMIN-VIEW " + admin.getUsername() + " viewed " + tu + " (" + @PKG@.VStore.nameOf(d) + ") page " + page);
  @PKG@.VSession live = current(tu);
  return "=READ-ONLY view of " + @PKG@.VStore.nameOf(d) + "'s vault page " + page + " of " + d.unlocked + " (" + d.used(page) + " of " + d.cap + " slots used)" + (live != null ? " - they have their vault open on page " + live.page + " right now, this is a snapshot." : ".");
}""")
M(vs, r"""
public static void shutdownSync() {
  java.util.Iterator it = SESSIONS.values().iterator();
  while (it.hasNext()) {
    @PKG@.VSession s = (@PKG@.VSession) it.next();
    try { retire(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault shutdown sync failed for " + s.owner + ": " + t); }
  }
}""")

# ================= bodies that call VSessions =================
M(clt, r"""
public void run() {
  try { @PKG@.VSessions.closeTask(this); } catch (Throwable t) { @PKG@.VCfg.warn("vault close task failed: " + t); }
}""")
M(chg, r"""
public void accept(Object ev) {
  try { @PKG@.VSessions.onChange(this.sess); } catch (Throwable t) { @PKG@.VCfg.warnOnce("chg", "vault change sync failed: " + t); }
}""")
M(win, r"""
public void onClose0(@REF@ ref, @CA@ a) {
  try { super.onClose0(ref, a); } catch (Throwable t) { }
  try { @PKG@.VSessions.windowClosed(this.sess); } catch (Throwable t) { @PKG@.VCfg.warn("vault window close handling failed: " + t); }
}""")
M(win, r"""
public boolean validate(@REF@ ref, @CA@ a) {
  try { return @PKG@.VSessions.stillValid(this.sess, ref, a); } catch (Throwable t) { return true; }
}""")
# 0.1.2: the slot filter. Touches NO container (the engine calls it inside the container's write lock): only the session's small
# fields. ADD, REMOVE and DROP are always refused on a live control slot, so the arrow never moves; a REMOVE attempt (every player
# gesture on the slot lands on it) is the click: the first hit of a batch queues ONE VBtnTask. A reserved inside slot that holds a
# stored stack (vault full) is plain storage: allowed. A closed session refuses (a DENY_ALL view never even asks).
M(bfl, r"""
public boolean test(@FAT@ a, @IC@ c, short slot, @IS@ st) {
  try {
    @PKG@.VSession s = this.sess;
    if (s == null || s.closed) return false;
    if (!s.ctrlLive(slot)) return true;
    if (a == @FAT@.REMOVE && s.noteHit(slot)) @PKG@.VSessions.queueBtn(s);
  } catch (Throwable t) { }
  return false;
}""")
M(btk, r"""
public void run() {
  try { @PKG@.VSessions.btnBatch(this.sess, this.wu); } catch (Throwable t) { @PKG@.VCfg.warnOnce("btn", "vault arrow click failed: " + t); }
}""")
M(swt, r"""
public void run() {
  try { @PKG@.VSessions.sweepRun(this); } catch (Throwable t) { @PKG@.VCfg.warnOnce("sweep", "vault stray-arrow check failed: " + t); }
}""")
# 0.1.5: VDropSys - the Drop key on a vault arrow (research/Vault-Arrow-Click-Research.md 4.5; SkyyIslands GuardDrop / SkyyGear
# event_system shape). ONE registerSystem (SkyyVaultPlugin.setup). Query = Player entities. shouldProcessEvent = true: EventSystem skips
# a request that is already cancelled - the engine pre-cancels EVERY request when the game mode prevents item drops (GameModeTypes.
# preventsItemDrops, InventoryPacketHandler lambda$handle$4 offsets 64-71) and SkyyIslands GuardDrop refuses island visitors' drops -
# but a press on OUR arrow is a page button, not a drop: it still turns the page (dropEvent only ever sets cancelled, never clears it).
# A fast exit when no vault is open.
C(drs, "public VDropSys() { super(@DIRQ@.class); }")
M(drs, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(drs, "protected boolean shouldProcessEvent(@EV@ ev) { return true; }")
M(drs, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DIRQ@)) return;
    if (@PKG@.VSessions.SESSIONS.isEmpty()) return;
    @DIRQ@ e = (@DIRQ@) ev;
    if (e.getInventorySectionId() <= 0) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    @PKG@.VSessions.dropEvent(pr, p, e);
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("drop", "vault Drop-key check failed (the arrow filter still refuses the drop): " + t); }
}""")
tick.addInterface(pool.get("java.lang.Runnable"))
C(tick, "public VTick() { }")
M(tick, r"""
public void run() {
  try { @PKG@.VSessions.tick(); } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick", "vault tick failed: " + t); }
}""")

# ================= VaultPage part 2: clicks + dismiss =================
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (a.equals("close")) { close(); return; }
    @PKG@.VData d = @PKG@.VStore.load(u);
    if (d == null) { this.info = "-Your vault file cannot be read - please tell an admin."; rebuild(); return; }
    boolean live = this.sess != null && !this.sess.closed;
    int max = d.unlocked > @PKG@.VCfg.MAX_PAGES ? d.unlocked : @PKG@.VCfg.MAX_PAGES;
    int tp = 0;
    if (a.equals("prev")) tp = this.sel - 1;
    else if (a.equals("next")) tp = this.sel + 1;
    else if (a.startsWith("num:")) { try { tp = Integer.parseInt(a.substring(4)); } catch (Throwable e) { tp = 0; } }
    if (a.equals("prev") || a.equals("next") || a.startsWith("num:")) {
      if (tp < 1 || tp > max) return;
      if (tp > d.unlocked) {
        this.sel = tp;
        if (tp == d.unlocked + 1) this.info = "=Page " + tp + " is locked. Click Buy to unlock it for " + @PKG@.VStore.grp(@PKG@.VStore.price(tp)) + " coins.";
        else this.info = "=Page " + tp + " is locked. Buy page " + (d.unlocked + 1) + " first.";
        rebuild();
        return;
      }
      if (live && this.sess.mode == 1) {
        String r = @PKG@.VSessions.pageSwap(this, ref, store, tp);
        this.sel = tp;
        this.info = r == null ? "+Showing page " + tp + "." : r;
        rebuild();
        return;
      }
      if (this.sess != null && @PKG@.VCfg.PAGE_MODE) {
        String r = @PKG@.VSessions.open(this.playerRef, ref, store, tp, 1);
        if (r != null) { this.sel = tp; this.info = r; rebuild(); }
        return;
      }
      this.sel = tp;
      this.info = "";
      rebuild();
      return;
    }
    if (a.equals("open")) {
      if (this.sel > d.unlocked) { this.info = "-Page " + this.sel + " is locked - buy it first."; rebuild(); return; }
      String r = @PKG@.VSessions.open(this.playerRef, ref, store, this.sel, 2);
      if (r != null && r.startsWith("=")) @PKG@.VSessions.tell(this.playerRef, r);
      else if (r != null) { this.info = r; rebuild(); }
      return;
    }
    if (a.equals("buy")) {
      // 0.1.3 (LOCKED Skyy 2026-09-25): the shared rule - below buyConfirmCoins the page is bought at once, at or above it the
      // confirm window opens and returns to this page view (page mode) or to the page without slots (/vault pages in chest mode).
      // this.offer = the page the button showed, so a stale button never buys a later page.
      int next = d.unlocked + 1;
      if (next > @PKG@.VCfg.MAX_PAGES) { this.info = "-You already own every vault page."; rebuild(); return; }
      String r = @PKG@.VStore.intent(u, this.playerRef.getUsername(), this.offer > 0 ? this.offer : next);
      if (r.startsWith("?")) {
        @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
        int ret = (live && this.sess.mode == 1) ? 1 : ((this.sess != null && @PKG@.VCfg.PAGE_MODE) ? 1 : 3);
        int back = live ? this.sess.page : (this.sel <= d.unlocked ? this.sel : d.unlocked);
        String r2 = @PKG@.VSessions.askBuy(this.playerRef, ref, store, p, live ? this.sess : (@PKG@.VSession) null, next, ret, back);
        if (r2 != null) { this.info = r2; rebuild(); }
        return;
      }
      this.info = r;
      if (r.startsWith("+")) {
        this.sel = next;
        if (live && this.sess.mode == 1) {
          String r2 = @PKG@.VSessions.pageSwap(this, ref, store, next);
          if (r2 != null) this.info = r2;
        }
      }
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault page click failed: " + t); }
}""")
M(page, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try { if (this.sess != null && !this.sess.closed && this.sess.mode == 1) @PKG@.VSessions.dismissed(this.sess); } catch (Throwable t) { }
}""")

# ================= 0.1.3 VBuyDlg part 2: Buy / Cancel / Esc =================
# Buy and Cancel act once (done); both return to where the player came from (VSessions.dlgBack): after a purchase on the NEW page, else
# on the page shown before. Esc (or another page replacing the window) buys nothing and says so; the vault stays closed.
M(dlg, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null || this.done) return;
    String a = @PKG@.VaultPage.jsonStr(data, "a");
    if (a.equals("dlgno")) {
      this.done = true;
      @PKG@.VSessions.dlgBack(this, ref, store, this.back, "=Nothing was bought.");
      return;
    }
    if (a.equals("dlgbuy")) {
      this.done = true;
      String res = @PKG@.VSessions.dlgBuy(this);
      @PKG@.VData d = this.u == null ? null : @PKG@.VStore.load(this.u);
      int pg = (res != null && res.startsWith("+") && d != null && d.unlocked >= this.page) ? this.page : this.back;
      if (d != null && pg > d.unlocked) pg = d.unlocked;
      @PKG@.VSessions.dlgBack(this, ref, store, pg, res);
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault confirm window click failed: " + t); }
}""")
M(dlg, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try {
    if (this.done) return;
    this.done = true;
    @PKG@.VSessions.tell(this.pr, "=Nothing was bought. /vault opens your vault.");
  } catch (Throwable t) { }
}""")

# ================= 0.1.1 VHooks: the config kit's check= / after= hooks and its RELOAD routine =================
# The kit calls them by reflection OUTSIDE its own locks (tools/CONFIG-CONTRACT.md "Locks"): check= on the caller's thread before a
# change (SkyyMenu click / command, import and restore plans), after= right after a field: set, RELOAD on the kit's save task after
# it noticed a hand edit of config.properties. None of them touches ECS, worlds or inventories.
# maxPages scan state. SCAN = parse cache (path -> { Long mtime, Long size, Integer high, String name }). LAST = the newest COMPLETE walk
# of the vault folder: { Long finishedAt, java.util.Map path -> { Integer high, String name, java.util.UUID owner or null } } (files of
# vaults loaded at walk time are not in it - memory is the truth for them). SCANNING = the background VScan thread is running.
for f in ("public static final java.util.concurrent.ConcurrentHashMap SCAN = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile Object[] LAST = null;", "public static volatile boolean SCANNING = false;",
          "public static final long SCAN_BUDGET_MS = 40L;",     # the most the admin's world thread spends walking the folder
          "public static final long SCAN_FRESH_MS = 120000L;"):  # how old a background walk may be and still answer the check
    F(hk, f)
# highest page that still holds a stack the server cannot place right now (kept in the file, counts as used)
M(dat, r"""
public synchronized int orphanHigh() {
  int h = 0;
  for (int i = 0; i < this.orphans.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) this.orphans.get(i);
    if (v == null || !v.isDocument()) continue;
    int p = @PKG@.VCodec.intOf(v.asDocument(), "page", 0);
    if (p > h) h = p;
  }
  return h;
}""")
# freePages raised: a loaded vault gets the pages exactly as a fresh load would (fromDoc: pages = max(saved, freePages)) - memory
# only, no revision bump, so no file is written for it; the next real change saves the new count, as after a restart.
# SAFE ONLY because VStore.CACHE is never evicted (see the comment there): an eviction path must save first.
M(dat, r"""
public synchronized boolean raiseTo(int n) {
  if (n <= this.unlocked || n > @PKG@.VCfg.MAX_PAGE) return false;
  this.unlocked = n;
  page(n);
  return true;
}""")
M(hk, r"""
public static int num(String v, int def) {
  if (v == null) return def;
  try { return Integer.parseInt(v.trim()); } catch (Throwable t) { return def; }
}""")
# highest page with a slot or an orphan in a saved vault document (the fromDoc rule)
M(hk, r"""
public static int docHigh(org.bson.BsonDocument doc) {
  int h = 0;
  org.bson.BsonArray c = doc.getArray("content", new org.bson.BsonArray());
  for (int i = 0; i < c.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) c.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument pd = v.asDocument();
    int pg = @PKG@.VCodec.intOf(pd, "page", 0);
    if (pd.getArray("slots", new org.bson.BsonArray()).size() > 0 && pg > h) h = pg;
  }
  org.bson.BsonArray o = doc.getArray("orphans", new org.bson.BsonArray());
  for (int i = 0; i < o.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) o.get(i);
    if (v == null || !v.isDocument()) continue;
    int pg = @PKG@.VCodec.intOf(v.asDocument(), "page", 0);
    if (pg > h) h = pg;
  }
  return h;
}""")
# one vault file -> { Integer highest used page, String owner name }, cached by modified time + size (a repeat check reads only the
# files that changed); null = unreadable (skipped: an unreadable vault stays shut anyway and lowering Max pages hides nothing)
M(hk, r"""
public static Object[] fileHigh(java.nio.file.Path f) {
  String fn = f.getFileName().toString();
  try {
    long mt = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    long sz = java.nio.file.Files.size(f);
    String k = f.toString();
    Object o = SCAN.get(k);
    if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (((Long) a[0]).longValue() == mt && ((Long) a[1]).longValue() == sz) return new Object[] { a[2], a[3] };
    }
    org.bson.BsonDocument doc = org.bson.BsonDocument.parse(@PKG@.VCfg.readText(f));
    int h = docHigh(doc);
    String nm = @PKG@.VCodec.strOf(doc, "name");
    if (nm == null || nm.length() == 0) nm = fn.endsWith(".json") ? fn.substring(0, fn.length() - 5) : fn;
    SCAN.put(k, new Object[] { Long.valueOf(mt), Long.valueOf(sz), Integer.valueOf(h), nm });
    return new Object[] { Integer.valueOf(h), nm };
  } catch (Throwable t) {
    @PKG@.VCfg.warnOnce("scan-" + fn, "Max pages check skipped the unreadable vault file " + f + ": " + t);
    return null;
  }
}""")
# one walk of the vault folder: every saved vault that is NOT loaded -> its highest used page (fileHigh: only new / changed files are
# parsed). budgetMs > 0 = on the admin's world thread: give up (null) once that much time went by - what was parsed stays in SCAN and
# the background walk finishes the job. 0 = no budget (VScan's daemon thread). A complete walk becomes LAST and prunes SCAN.
M(hk, r"""
public static java.util.Map scanDir(long budgetMs) throws java.io.IOException {
  long t0 = System.nanoTime();
  java.util.HashMap res = new java.util.HashMap();
  boolean over = false;
  java.nio.file.Path dir = @PKG@.VCfg.VDIR;
  if (dir != null && java.nio.file.Files.isDirectory(dir, new java.nio.file.LinkOption[0])) {
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(dir, "*.json");
    try {
      java.util.Iterator fi = ds.iterator();
      while (!over && fi.hasNext()) {
        if (budgetMs > 0L && System.nanoTime() - t0 > budgetMs * 1000000L) over = true;
        else {
          java.nio.file.Path f = (java.nio.file.Path) fi.next();
          String fn = f.getFileName().toString();
          java.util.UUID u = null;
          try { u = java.util.UUID.fromString(fn.substring(0, fn.length() - 5)); } catch (Throwable t) { u = null; }
          if (u == null || !@PKG@.VStore.CACHE.containsKey(u)) {
            Object[] r = fileHigh(f);
            if (r != null) res.put(f.toString(), new Object[] { r[0], r[1], u });
          }
        }
      }
    } finally { ds.close(); }
  }
  if (over) return null;
  java.util.Iterator it = SCAN.keySet().iterator();
  while (it.hasNext()) { if (!res.containsKey(it.next())) it.remove(); }
  LAST = new Object[] { Long.valueOf(System.currentTimeMillis()), res };
  return res;
}""")
# VScan: the background walk (a fresh daemon thread per run, lowest priority; reads files only, never touches ECS / worlds)
scn.addInterface(pool.get("java.lang.Runnable"))
C(scn, "public VScan() { }")
M(scn, r"""
public void run() {
  try { @PKG@.VHooks.scanDir(0L); }
  catch (Throwable t) { @PKG@.VCfg.warnOnce("scan", "the vault file check (Max pages) failed: " + t); }
  @PKG@.VHooks.SCANNING = false;
}""")
M(hk, r"""
public static synchronized void startScan() {
  if (SCANNING) return;
  SCANNING = true;
  try {
    Thread t = new Thread(new @PKG@.VScan(), "SkyyVault-scan");
    t.setDaemon(true);
    t.setPriority(Thread.MIN_PRIORITY);
    t.start();
  } catch (Throwable e) { SCANNING = false; @PKG@.VCfg.warn("could not start the vault file check (Max pages): " + e); }
}""")
# the saved-vault part of the Max pages check without a long stall on the admin's world thread: a complete walk from the last
# SCAN_FRESH_MS (a refresh starts for the next ask, e.g. the confirm click), else a walk right here if it fits in SCAN_BUDGET_MS, else
# null (the background walk starts; the admin is asked to try again in a few seconds)
M(hk, r"""
public static java.util.Map freshFiles() throws java.io.IOException {
  Object[] last = LAST;
  if (last != null && System.currentTimeMillis() - ((Long) last[0]).longValue() <= SCAN_FRESH_MS) {
    startScan();
    return (java.util.Map) last[1];
  }
  if (SCANNING) return null;
  java.util.Map m = scanDir(SCAN_BUDGET_MS);
  if (m == null) startScan();
  return m;
}""")
# the highest used page over EVERY vault: saved vaults from the walk (skipping any loaded since), then the loaded vaults from memory
# (what the player sees, unsaved changes included). Files first: a vault loaded in between is then counted at least once.
M(hk, r"""
public static Object[] highestUsedAll(java.util.Map files) {
  int best = 0;
  String who = "";
  java.util.Iterator fi = files.values().iterator();
  while (fi.hasNext()) {
    Object[] e = (Object[]) fi.next();
    java.util.UUID u = (java.util.UUID) e[2];
    if (u == null || !@PKG@.VStore.CACHE.containsKey(u)) {
      int h = ((Integer) e[0]).intValue();
      if (h > best) { best = h; who = (String) e[1]; }
    }
  }
  java.util.Iterator it = @PKG@.VStore.CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.VData d = (@PKG@.VData) it.next();
    int h = d.highestUsed();
    int oh = d.orphanHigh();
    if (oh > h) h = oh;
    if (h > best) { best = h; who = @PKG@.VStore.nameOf(d); }
  }
  return new Object[] { Integer.valueOf(best), who };
}""")
# check= freePages: never above Max pages (VCfg.load raises Max pages to Free pages when a hand edit breaks the rule)
M(hk, r"""
public static String checkFree(String key, String value) {
  int n = num(value, -1);
  if (n < 1) return null;
  int mx = @PKG@.VCfg.MAX_PAGES;
  if (n > mx) return "Free pages cannot be above Max pages (" + mx + ") - raise Max pages first.";
  return null;
}""")
# check= maxPages: never below Free pages, and (only when lowering) never below a page that still holds items in any vault
M(hk, r"""
public static String checkMax(String key, String value) {
  int n = num(value, -1);
  if (n < 1) return null;
  int fp = @PKG@.VCfg.FREE_PAGES;
  if (n < fp) return "Max pages cannot be below Free pages (" + fp + ") - lower Free pages first.";
  if (n >= @PKG@.VCfg.MAX_PAGES) return null;
  java.util.Map files = null;
  try { files = freshFiles(); }
  catch (Throwable t) {
    @PKG@.VCfg.warn("Max pages check could not list the vault files: " + t);
    return "Could not check the vault files - see the server log. Nothing was changed.";
  }
  if (files == null) return "Checking every saved vault for items above page " + n + " - try again in a few seconds. Nothing was changed.";
  Object[] r = highestUsedAll(files);
  int h = ((Integer) r[0]).intValue();
  if (h > n) return "Page " + h + " of " + r[1] + "'s vault still holds items - Max pages cannot go below " + h + " (items are never hidden).";
  return null;
}""")
M(hk, r"""
public static int raiseFree() {
  int n = @PKG@.VCfg.FREE_PAGES;
  int c = 0;
  java.util.Iterator it = @PKG@.VStore.CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.VData d = (@PKG@.VData) it.next();
    try { if (d.raiseTo(n)) c++; } catch (Throwable t) { }
  }
  return c;
}""")
# after= freePages (the field is already set): loaded vaults get the new free pages now, not only after a restart
M(hk, r"""
public static void afterFree(String key) {
  int c = raiseFree();
  if (c > 0) @PKG@.VCfg.info("free pages now " + @PKG@.VCfg.FREE_PAGES + ": " + c + " loaded vault(s) got the new free pages");
}""")
# after= openMode: PAGE_MODE (read by /vault) follows the String the kit just set
M(hk, r"""
public static void afterOpenMode(String key) {
  @PKG@.VCfg.PAGE_MODE = !"chest".equals(@PKG@.VCfg.OPEN_MODE);
}""")
# RELOAD: the kit noticed a hand edit (or the reload op found one): the mod's own loader re-reads the file with its 0.1 clamps
# (maxPages raised to freePages, openMode word check), then loaded vaults get raised free pages like afterFree
M(hk, r"""
public static void reloadCfg() {
  String s = @PKG@.VCfg.load();
  int c = raiseFree();
  @PKG@.VCfg.info("config.properties re-read: " + s + (c > 0 ? " (" + c + " loaded vaults got the new free pages)" : ""));
}""")

# ================= commands =================
EXEC ="protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []
CMD_PERM = {}   # class name -> "@ADV@" | "@ADMIN@" (checked against ADMIN_CMDS and the compiled class files at the end)
# EVERY admin command class (root, subcommands, usage variants). A cmd(...) that is not listed here must be a player command (@ADV@)
# and every listed one must be built with perm=A - so an admin command that forgets perm= fails the build instead of opening to players.
ADMIN_CMDS = {"VAOpenPageCmd", "VAOpenCmd", "VAInfoCmd", "VASetPagesCmd", "VAReloadCmd", "VAConfigSetCmd", "VAConfigCmd",
              "VaultAdminCmd"}


def cmd(clsname, name, desc, args, body, perm="@ADV@", subs=(), variant=None):
    """One AbstractPlayerCommand. name=None -> usage variant (description-only constructor). args = [(field, argName, argDesc)] STRING,
    read into a0, a1, ...
    Permission self-check (tools/ci/lint.py cannot see these templated constructors): perm must be @ADV@ or @ADMIN@ and the generated
    constructor must contain the permission call."""
    if perm not in ("@ADV@", "@ADMIN@"):
        raise SystemExit("command %s: perm must be @ADV@ or @ADMIN@ (COMMAND RULES), got %r" % (clsname, perm))
    if clsname in CMD_PERM:
        raise SystemExit("command class %s defined twice" % clsname)
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = [('super("%s", "%s");' % (name, desc)) if name else ('super("%s");' % desc), perm]
    for (fld, an, ad) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.STRING);' % (fld, an, ad))
    if variant:
        lines.append("addUsageVariant(new @PKG@.%s());" % variant)
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    ctor = "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines))
    want = 'setPermissionGroups(new String[] { "hytale:Adventurer" });' if perm == "@ADV@" else 'requirePermission("skyyvault.admin");'
    if want not in jv(ctor):
        raise SystemExit("command %s: generated constructor lacks %s:\n%s" % (clsname, want, jv(ctor)))
    CMD_PERM[clsname] = perm
    C(c, ctor)
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s)).trim();\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.VCfg.warn(\"" + clsname + " failed: \" + t);\n"
      "    @PKG@.VSessions.tell(pr, \"-Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


VS = "@PKG@.VSessions."
PARSE = ("int n = 0; try { n = Integer.parseInt(a%d); } catch (Throwable e) { n = 0; } "
         "if (n < 1) { " + VS + "tell(pr, \"-%s\"); return; } ")
cmd("VaultPageCmd", None, "Open one vault page: /vault <page>", [("pageArg", "page", "Vault page number")],
    PARSE % (0, "Use /vault <page number> - for example /vault 2") + VS + "tell(pr, " + VS + "openDefault(pr, ref, store, n));")
# 0.1.3 (LOCKED Skyy 2026-09-25): below buyConfirmCoins it buys at once, at or above it the confirm window opens (VSessions.cmdBuy)
cmd("VaultBuyCmd", "buy", "Buy the next vault page with coins", [],
    r"""@PKG@.VSessions.cmdBuy(pr, ref, store);""")
cmd("VaultInfoCmd", "info", "Your vault pages, slots used and the next page price", [],
    r"""@PKG@.VSession s = @PKG@.VSessions.current(pr.getUuid());
    @PKG@.VSessions.tellAll(pr, @PKG@.VStore.infoLines(pr.getUuid(), s == null ? 0 : s.page, false));""")
cmd("VaultPagesCmd", "pages", "Open the vault page with the page buttons", [], VS + "tell(pr, " + VS + "openNav(pr, ref, store));")
cmd("VaultNextCmd", "next", "Show the next vault page", [], VS + "tell(pr, " + VS + "step(pr, ref, store, 1));")
cmd("VaultPrevCmd", "prev", "Show the previous vault page", [], VS + "tell(pr, " + VS + "step(pr, ref, store, -1));")
cmd("VaultCmd", "vault", "Your vault - one chest shared by all your profiles (/vault 2 opens page 2)", [],
    VS + "tell(pr, " + VS + "openDefault(pr, ref, store, 1));", variant="VaultPageCmd",
    subs=("VaultBuyCmd", "VaultInfoCmd", "VaultPagesCmd", "VaultNextCmd", "VaultPrevCmd"))

# ---- admin (requirePermission on the root, on every subcommand and on the open variant)
A = "@ADMIN@"
cmd("VAOpenPageCmd", None, "Admin: read-only view of one vault page: /vaultadmin open <player> <page>",
    [("playerArg", "player", "Online name, known name or UUID"), ("pageArg", "page", "Vault page number")],
    PARSE % (1, "Use /vaultadmin open <player> <page number>") + VS + "tell(pr, " + VS + "adminView(pr, ref, store, a0, n));", perm=A)
cmd("VAOpenCmd", "open", "Admin: read-only view of a player's vault (page 1; /vaultadmin open <player> <page>)",
    [("playerArg", "player", "Online name, known name or UUID")], VS + "tell(pr, " + VS + "adminView(pr, ref, store, a0, 1));",
    perm=A, variant="VAOpenPageCmd")
cmd("VAInfoCmd", "info", "Admin: a player's vault pages and slots used", [("playerArg", "player", "Online name, known name or UUID")],
    r"""java.util.UUID tu = @PKG@.VStore.resolve(a0);
    if (tu == null) { @PKG@.VSessions.tell(pr, "-No player or vault found for " + a0 + "."); return; }
    @PKG@.VSession s = @PKG@.VSessions.current(tu);
    @PKG@.VSessions.tellAll(pr, @PKG@.VStore.infoLines(tu, s == null ? 0 : s.page, true));
    if (s != null) @PKG@.VSessions.tell(pr, "=Their vault is open right now on page " + s.page + ".");""", perm=A)
cmd("VASetPagesCmd", "setpages", "Admin: set how many vault pages a player owns (never below a page that holds items)",
    [("playerArg", "player", "Online name, known name or UUID"), ("pagesArg", "pages", "Number of pages")],
    PARSE % (1, "Use /vaultadmin setpages <player> <number of pages>") +
    r"""java.util.UUID tu = @PKG@.VStore.resolve(a0);
    if (tu == null) { @PKG@.VSessions.tell(pr, "-No player or vault found for " + a0 + "."); return; }
    @PKG@.VSession s = @PKG@.VSessions.current(tu);
    @PKG@.VSessions.tell(pr, @PKG@.VStore.setPages(pr.getUsername(), tu, n, s == null ? 0 : s.page));""", perm=A)
# 0.1.1: through the config kit's reload op (never read config.properties here directly: a value set a moment ago may still wait for
# the kit's 500 ms save). Hand edits are logged via=file, versioned, and applied by VHooks.reloadCfg on the kit's save task. Without a
# running kit (it failed to start - see the server log) the 0.1 path (VCfg.load) still works.
cmd("VAReloadCmd", "reload", "Admin: re-read config.properties (hand edits are logged)", [],
    r"""if (!@PKG@.CfgPub.STARTED) { @PKG@.VSessions.tell(pr, "+config.properties re-read: " + @PKG@.VCfg.load()); return; }
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
    boolean ok = false;
    String m = "could not be re-read - see the server log.";
    if (o instanceof Object[] && ((Object[]) o).length > 2) {
      Object[] r = (Object[]) o;
      ok = "ok".equals(r[0]);
      if (r[2] != null) m = String.valueOf(r[2]);
    }
    @PKG@.VSessions.tell(pr, (ok ? "+" : "-") + "config.properties: " + m + (ok ? " /vaultadmin config shows the values." : ""));""", perm=A)
# 0.1.1: the chat twin of the Server Setup page (for owners without SkyyMenu): the kit's own set op with via=command (the confirm step
# is implied for commands, as for every Skyy admin command), so it is validated, logged in config-changes.log and versioned
cmd("VAConfigSetCmd", None, "Admin: change one vault setting: /vaultadmin config <key> <value>",
    [("keyArg", "key", "Setting key, e.g. maxPages"), ("valueArg", "value", "New value, e.g. 12")],
    r"""if (pr.getUuid() == null) { @PKG@.VSessions.tell(pr, "-Could not tell who sent this command - nothing was changed."); return; }
    Object o = new @PKG@.CfgFn().apply(new Object[] { "set", a0, a1, pr.getUuid(), pr.getUsername(), "yes", "command" });
    if (!(o instanceof Object[]) || ((Object[]) o).length < 3) { @PKG@.VSessions.tell(pr, "-Nothing was changed - see the server log."); return; }
    Object[] r = (Object[]) o;
    String st = String.valueOf(r[0]);
    String m = r[2] == null ? "" : String.valueOf(r[2]);
    if (st.equals("ok") || st.equals("restart")) @PKG@.VSessions.tell(pr, "+" + m);
    else if (st.equals("unknown")) @PKG@.VSessions.tell(pr, "-" + m + " /vaultadmin config lists the settings.");
    else @PKG@.VSessions.tell(pr, "-" + m);""", perm=A)
cmd("VAConfigCmd", "config", "Admin: list the vault settings (/vaultadmin config <key> <value> changes one)", [],
    r"""String[] ks = @PKG@.CfgRows.KEYS;
    @PKG@.VSessions.tell(pr, "=Vault settings - change them in SkyWynn Menu -> Server Setup -> Vault or with /vaultadmin config <key> <value>:");
    for (int i = 0; i < ks.length; i++) {
      String v = @PKG@.CfgFn.cmdGet(ks[i]);
      String u = @PKG@.CfgRows.UNITS[i];
      @PKG@.VSessions.tell(pr, "=" + ks[i] + " = " + (v == null ? "?" : v) + (u.length() > 0 ? " " + u : "") + " - " + @PKG@.CfgRows.LABELS[i]);
    }""", perm=A, variant="VAConfigSetCmd")
cmd("VaultAdminCmd", "vaultadmin", "Vault admin: open <player> [page] | info <player> | setpages <player> <n> | config | reload", [],
    VS + "tellAll(pr, new String[] { \"=/vaultadmin open <player> [page] - read-only view of a vault page\", "
    "\"=/vaultadmin info <player> - pages and slots used\", \"=/vaultadmin setpages <player> <pages> - set owned pages\", "
    "\"=/vaultadmin config [<key> <value>] - list or change the vault settings (also SkyWynn Menu -> Server Setup)\", "
    "\"=/vaultadmin reload - re-read config.properties after a hand edit\" });",
    perm=A, subs=("VAOpenCmd", "VAInfoCmd", "VASetPagesCmd", "VAConfigCmd", "VAReloadCmd"))

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyVaultPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.VCfg.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyVault");
  @PKG@.VCfg.DIR = dir;
  @PKG@.VCfg.VDIR = dir.resolve("vaults");
  @PKG@.VCfg.FILE = dir.resolve("config.properties");
  @PKG@.VCfg.LOGF = dir.resolve("vault.log");
  @PKG@.VCfg.NAMESF = dir.resolve("names.properties");
  String cfg = @PKG@.VCfg.load();
  @PKG@.VStore.loadNames();
  @PKG@.VStore.STOPPING = false;
  @PKG@.VStore.SAVER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.VThreads());
  getCommandRegistry().registerCommand(new @PKG@.VaultCmd());
  getCommandRegistry().registerCommand(new @PKG@.VaultAdminCmd());
  // 0.1.5: the Drop key on a vault arrow turns the page with no engine WARNING (ONE registerSystem per class). If it cannot register,
  // the 0.1.4 path still works: the arrow filter refuses the drop and that refused REMOVE is the click (the engine then warns).
  try { getEntityStoreRegistry().registerSystem(new @PKG@.VDropSys()); }
  catch (Throwable t) { @PKG@.VCfg.warn("the vault Drop-key system could not be registered (Drop on an arrow still turns the page through the arrow filter): " + t); }
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.VTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyVault] @VERSION@ ready (""" + KIT_ID + ", page " + VAULT_PAGE_ID + r""") - /vault (shared by all profiles), /vaultadmin; " + cfg + "; data in " + dir);
  // 0.1.1, LAST in setup() after the config load: config:def:SkyyVault + config:fn:SkyyVault for SkyyMenu's Server Setup (the kit
  // reads config.properties itself, logs clamped values once and never throws)
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  @PKG@.VStore.STOPPING = true;
  try { @PKG@.VSessions.shutdownSync(); } catch (Throwable t) { }
  try { @PKG@.VStore.flushAll(); } catch (Throwable t) { }
  try {
    java.util.concurrent.ScheduledExecutorService ex = @PKG@.VStore.SAVER;
    if (ex != null) { ex.shutdown(); ex.awaitTermination(3L, java.util.concurrent.TimeUnit.SECONDS); }
  } catch (Throwable t) { }
  try { @PKG@.VStore.flushAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

# ---- command permission self-check, part 2 (part 1 is in cmd()): the admin set is exact, nothing else is a command, and the COMPILED
# constructors really reference the permission call + its argument
built_admin = set(k for k, v in CMD_PERM.items() if v == "@ADMIN@")
if built_admin != ADMIN_CMDS:
    raise SystemExit("ADMIN_CMDS mismatch - built with @ADMIN@: %s, listed: %s" % (sorted(built_admin), sorted(ADMIN_CMDS)))
for c in ALL + [pl]:
    if str(c.getSuperclass().getName()) == T["APC"]:
        raise SystemExit("%s is a command but was not built by cmd() (no permission self-check)" % c.getName())

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
kit.write(OUT)      # the kit's deferred checks (VHooks.checkFree/checkMax/afterFree/afterOpenMode/reloadCfg exist with the right
                    # signatures), then its 7 classes
print("classes written:", len(ALL + CMDS) + 1 + len(kit.classes), "(%d kit)" % len(kit.classes))

for c in CMDS:
    short = str(c.getSimpleName())
    with open(os.path.join(OUT, *(PKG.split(".") + [short + ".class"])), "rb") as fh:
        raw = fh.read()
    need = (b"setPermissionGroups", b"hytale:Adventurer") if CMD_PERM[short] == "@ADV@" else (b"requirePermission", b"skyyvault.admin")
    if not all(n in raw for n in need):
        raise SystemExit("compiled command %s lacks %s" % (short, " + ".join(n.decode() for n in need)))
print("command permissions checked:", len(CMDS), "commands (%d player, %d admin)" % (len(CMDS) - len(built_admin), len(built_admin)))

# ================= 0.1.2 asset pack: 7 arrow items, 1 quality, 7 icons, server.lang (research/Vault-Arrows-Spec.md section 9) =================
# Icons: 64x64 RGBA drawn here with a tiny pure-Python PNG writer (PIL is not installed): our own art, no license question.
def png_bytes(w, h, rows):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rows[y])
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def seg_d2(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == 0 and dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy)))
    qx, qy = ax + t * dx - px, ay + t * dy - py
    return qx * qx + qy * qy


def draw_icon(layers, size=64, ss=4):
    """layers: list of (inside(x, y) -> bool, (r, g, b, a)), bottom first. 4x4 supersampling; straight-alpha result."""
    rows = []
    n = ss * ss
    for y in range(size):
        row = bytearray()
        for x in range(size):
            ar = ag = ab = aa = 0.0
            for sy in range(ss):
                for sx in range(ss):
                    fx, fy = x + (sx + 0.5) / ss, y + (sy + 0.5) / ss
                    col = None
                    for inside, c in layers:
                        if inside(fx, fy):
                            col = c
                    if col is not None:
                        a = col[3] / 255.0
                        ar += col[0] * a; ag += col[1] * a; ab += col[2] * a; aa += a
            if aa <= 0.0:
                row.extend((0, 0, 0, 0))
            else:
                row.extend((int(round(ar / aa)), int(round(ag / aa)), int(round(ab / aa)), int(round(255 * aa / n))))
        rows.append(bytes(row))
    return png_bytes(size, size, rows)


def arrow_shape(right, r):
    # a shaft plus a two-stroke head, round caps; r = stroke half-width
    segs = [(14, 32, 48, 32), (48, 32, 33, 17), (48, 32, 33, 47)]
    if not right:
        segs = [(64 - a, b, 64 - c, d) for (a, b, c, d) in segs]
    r2 = r * r
    return lambda x, y: any(seg_d2(x, y, *s) <= r2 for s in segs)


def rect(x0, y0, x1, y1):
    return lambda x, y: x0 <= x <= x1 and y0 <= y <= y1


def rrect(x0, y0, x1, y1, rad):
    def f(x, y):
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return False
        cx = min(max(x, x0 + rad), x1 - rad)
        cy = min(max(y, y0 + rad), y1 - rad)
        return (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad
    return f


BLUE, BLUE_EDGE = (124, 196, 255, 255), (22, 52, 86, 255)
GREY, GREY_EDGE = (160, 168, 178, 105), (40, 46, 54, 95)
GOLD, GOLD_EDGE = (255, 201, 74, 255), (96, 62, 8, 255)
ICONS = {
    "Prev":    [(arrow_shape(False, 8.5), BLUE_EDGE), (arrow_shape(False, 5.5), BLUE)],
    "Next":    [(arrow_shape(True, 8.5), BLUE_EDGE), (arrow_shape(True, 5.5), BLUE)],
    "PrevOff": [(arrow_shape(False, 8.5), GREY_EDGE), (arrow_shape(False, 5.5), GREY)],
    "NextOff": [(arrow_shape(True, 8.5), GREY_EDGE), (arrow_shape(True, 5.5), GREY)],
    "Buy":     [(arrow_shape(True, 8.5), GOLD_EDGE), (arrow_shape(True, 5.5), GOLD),
                (rect(6, 8, 24, 16), GOLD_EDGE), (rect(11, 3, 19, 21), GOLD_EDGE),
                (rect(8, 10, 22, 14), (255, 244, 196, 255)), (rect(13, 5, 17, 19), (255, 244, 196, 255))],
    "Info":    [(rrect(14, 8, 50, 56, 4), (110, 90, 60, 255)), (rrect(16, 10, 48, 54, 3), (243, 231, 201, 255)),
                (rect(21, 21, 43, 24), (138, 122, 90, 255)), (rect(21, 30, 43, 33), (138, 122, 90, 255)),
                (rect(21, 39, 37, 42), (138, 122, 90, 255))],
    "Filler":  [(rrect(6, 6, 58, 58, 6), (70, 82, 98, 150)), (rrect(9, 9, 55, 55, 4), (38, 46, 58, 150))],
}
# (suffix, lang name, lang description or None). The per-stack ItemDisplay text replaces both in the vault window.
# 0.1.5: the fallback descriptions name the instant gestures too (shift-click / the Drop key; a plain click acts at the put-down)
BTN_ITEMS = [
    ("Prev", "Previous page", "Shift-click or press Drop: turns the vault window to the previous page."),
    ("PrevOff", "First page", "You are on the first vault page."),
    ("Next", "Next page", "Shift-click or press Drop: turns the vault window to the next page."),
    ("NextOff", "Last page", "You own every vault page."),
    ("Buy", "Buy next page", "Shift-click or press Drop: buys (or asks to confirm) the next vault page."),
    ("Info", "Vault page", "The vault page you are on."),
    ("Filler", "Vault", None),
]
if set("Skyy_Vault_" + b[0] for b in BTN_ITEMS) != set(BTN_IDS[1:]):
    raise SystemExit("BTN_ITEMS and BTN_IDS name different items")
QUALITY_ID = "SkyyVaultButton"
ITEM_MODEL, ITEM_TEXTURE = "Items/Consumables/Scrolls/Map.blockymodel", "Items/Consumables/Scrolls/Map_Wood.png"   # vanilla map scroll
FORBIDDEN_KEYS = ("Categories", "Recipe", "Interactions", "BlockType", "ResourceTypes", "Consumable", "Tool", "Weapon", "Armor", "Utility")


def btn_item(suffix, has_desc):
    iid = "Skyy_Vault_" + suffix
    tp = {"Name": "server.items.%s.name" % iid}
    if has_desc:
        tp["Description"] = "server.items.%s.description" % iid
    return {"TranslationProperties": tp,
            "Icon": "Icons/ItemsGenerated/%s.png" % iid,
            "Model": ITEM_MODEL,
            "Texture": ITEM_TEXTURE,
            "PlayerAnimationsId": "Item",
            "Quality": QUALITY_ID,
            "MaxStack": 1}


QUALITY = {"QualityValue": 8,
           "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltipTechnical.png",
           "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltipTechnicalArrow.png",
           "SlotTexture": "UI/ItemQualities/Slots/SlotTool.png",
           "BlockSlotTexture": "UI/ItemQualities/Slots/SlotTool.png",
           "SpecialSlotTexture": "UI/ItemQualities/Slots/SlotTool.png",
           "TextColor": "#d9b25c",
           "LocalizationKey": "server.general.qualities." + QUALITY_ID,
           "VisibleQualityLabel": False,
           "RenderSpecialSlot": True,
           "HideFromSearch": True}
files = {}
lang = []
for suffix, name, desc in BTN_ITEMS:
    iid = "Skyy_Vault_" + suffix
    files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(btn_item(suffix, desc is not None), indent=2)
    files["Common/Icons/ItemsGenerated/%s.png" % iid] = draw_icon(ICONS[suffix])
    lang.append("items.%s.name=%s" % (iid, name))
    lang.append("server.items.%s.name=%s" % (iid, name))
    if desc is not None:
        lang.append("items.%s.description=%s" % (iid, desc))
        lang.append("server.items.%s.description=%s" % (iid, desc))
files["Server/Item/Qualities/%s.json" % QUALITY_ID] = json.dumps(QUALITY, indent=2)
lang.append("general.qualities.%s=Vault" % QUALITY_ID)             # vanilla server.lang style (key without the server. prefix)
lang.append("server.general.qualities.%s=Vault" % QUALITY_ID)      # + the prefixed twin (the SkyySacks pattern writes both)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"

# ---- asset build checks (spec 9 + 10 l): JSON keys, MaxStack 1, no forbidden keys, every Model / Texture / quality texture exists in
# Assets.zip, every Icon is shipped here, 7 valid 64x64 RGBA PNGs, lang lines for every id
def png_ok(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return "bad signature"
    pos, idat, ihdr = 8, b"", None
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        tag, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + ln]
        crc, = struct.unpack(">I", data[pos + 8 + ln:pos + 12 + ln])
        if zlib.crc32(tag + body) & 0xFFFFFFFF != crc:
            return "bad crc in " + tag.decode()
        if tag == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    if ihdr != (64, 64, 8, 6, 0, 0, 0):
        return "IHDR %r" % (ihdr,)
    if len(zlib.decompress(idat)) != 64 * (1 + 64 * 4):
        return "bad pixel data length"
    return None


ASSETS_ZIP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
assets = None
if os.path.exists(ASSETS_ZIP):
    with zipfile.ZipFile(ASSETS_ZIP) as az:
        assets = set(az.namelist())
else:
    print("WARNING: Assets.zip not found - the Model / Texture path checks were skipped")


def asset_exists(p):
    if assets is None:
        return True
    q = "Common/" + p
    return q in assets or (q.endswith(".png") and q[:-4] + "@2x.png" in assets)


lang_text = files["Server/Languages/en-US/server.lang"]
n_png = 0
for path, data in files.items():
    if path.startswith("Server/Item/Items/"):
        node = json.loads(data)
        bad = [k for k in FORBIDDEN_KEYS if k in node]
        if bad or node.get("MaxStack") != 1 or node.get("Quality") != QUALITY_ID:
            raise SystemExit("asset check failed for %s: forbidden keys %s / MaxStack %r / Quality %r" % (path, bad, node.get("MaxStack"), node.get("Quality")))
        for k in ("Model", "Texture"):
            if not asset_exists(node[k]):
                raise SystemExit("asset check failed for %s: %s %s is not in Assets.zip" % (path, k, node[k]))
        if "Common/" + node["Icon"] not in files:
            raise SystemExit("asset check failed for %s: icon %s is not shipped" % (path, node["Icon"]))
        iid = path.rsplit("/", 1)[1][:-5]
        if ("server.items.%s.name=" % iid) not in lang_text:
            raise SystemExit("asset check failed: no lang name for " + iid)
        if "Description" in node["TranslationProperties"] and ("server.items.%s.description=" % iid) not in lang_text:
            raise SystemExit("asset check failed: no lang description for " + iid)
    elif path.endswith(".png"):
        err = png_ok(data)
        if err:
            raise SystemExit("asset check failed for %s: %s" % (path, err))
        n_png += 1
for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture", "BlockSlotTexture", "SpecialSlotTexture"):
    if not asset_exists(QUALITY[k]):
        raise SystemExit("asset check failed: quality %s %s is not in Assets.zip" % (k, QUALITY[k]))
n_items = sum(1 for p in files if p.startswith("Server/Item/Items/"))
if n_items != 7 or n_png != 7 or ("Server/Item/Qualities/%s.json" % QUALITY_ID) not in files:
    raise SystemExit("asset check failed: %d items, %d icons" % (n_items, n_png))
print("assets checked: %d items, 1 quality, %d icons (64x64 RGBA), %d lang lines" % (n_items, n_png, len(lang)))

jar = os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)
man = B.manifest("SkyyVault", VERSION, "SkyWynn vault: /vault is one chest shared by all your profiles (Wynncraft bank style) - pages, arrows in the vault window, buy more with coins (SkyyCoins bridge), lossless item storage. Per player. Zero dependencies.", PKG + ".SkyyVaultPlugin")
man["IncludesAssetPack"] = True     # 0.1.2: the arrow items, their quality, icons and lang lines (0.1.1 shipped no assets: False)
# 0.1.3: HANDOFF section 2 rule 2 - never ship a UI document; every page (the vault page, the confirm window) is built inline
_bad = [p for p in files if p.lower().endswith(".ui") or "/UI/" in p]
if _bad:
    raise SystemExit("this mod must not ship UI documents (build pages inline): %s" % _bad)
B.assemble(jar, man, OUT, files)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
if _bad:
    os.remove(jar)
    raise SystemExit("the jar held UI documents %s - removed it (build pages inline)" % _bad)
