"""SkyyVault 0.1.2 - build script (javassist via jpype). Copied from the LIVE build_skyyvault_0.1.1.py (no patch script) and edited.
Run:   python build_skyyvault_0.1.2.py          -> SkyyVault/SkyyVault-0.1.2.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)

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
    noSync on a mismatch), which now also rebuilds the control row; page mode also refreshes our page. Gold Buy = the SAME 10 s
    confirm as the page's Buy button and /vault buy (VStore.buyKey / confirm / buy): first click arms (chat), a click in a LATER batch
    within 10 s buys (coins once) and the new page opens in place. First page / Last page / page info / fillers: a chat line or
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
                    blue, locked grey), "Page 2 - 14 of 36 slots used", Open as chest, Buy page N - <price> coins (second click
                    confirms within 10 s), Close, three help lines and a result line. Prev / Next / a number swap the vault slots
                    in place (no window churn). "Open as chest" opens the same vault page in the VANILLA chest window (Page.Bench +
                    ContainerWindow - the proven vanilla /invsee, chest and TerrariaAddons pattern) - the fallback in case the
                    client does not draw window slots next to a custom page (UNVERIFIED, see below).
                    openMode=chest: /vault opens the vanilla chest window at once; /vault pages opens the page with the buttons,
                    whose Open button opens the selected page as a chest.
  /vault <page>     the same, on that page (usage variant, one required arg; the engine picks subcommands by name first).
  /vault next | prev    the next / previous page (swaps in place when the vault is already showing, else opens it).
  /vault pages      the page with the buttons (openMode=chest) - in page mode it is the same as /vault.
  /vault buy        buy the next page (type it twice within 10 s). /vault info  pages, slots used per page, next price.
                    The page's Buy button and /vault buy share ONE confirmation (VStore.CONFIRM, key buy:<uuid>:<page number>): a
                    click then a typed /vault buy (or the reverse) is the two-step confirm; arming by command refreshes an open vault
                    page so its button shows "Sure?". The key names the page, so a confirm armed for page 3 never buys page 4.
  Vault pages: freePages (2) free, more bought with coins up to maxPages (10): page N costs
  pagePrice + pagePriceStep x (N - freePages - 1) = 50k, 75k, 100k, ... (config). 36 slots per page (a large chest; config).
  PROPOSED NUMBERS, NOT SIGNED OFF BY SKYY: the backlog asks for "Wynncraft bank-style" storage (Wynncraft bank pages are bought, and
  its bank is shared by every character) but names no prices. Every number is in config.properties, so a decision needs no rebuild.
  Coins come from the ACTIVE profile's purse (coins:fn:take acts on the active profile) while the page belongs to the vault every
  profile shares - the Wynncraft pattern (one character's emeralds buy an account-wide bank page). Not yet written into
  tools/PROFILES-CONTRACT.md as a sanctioned pattern; Skyy decides.
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
    vault.log.
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
  No ECS systems, no events registered.
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

VERSION = "0.1.2"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.vault"
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
             (T["MVT"], "MOVE_FROM_SELF"), (T["ACT"], "REMOVE"), (T["ISX"], "FAILED_ADD"), (T["MT"], "toInverted")):
    B.probe(pool, c, m)

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
DEF_PRICE, DEF_STEP = 50000, 25000
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
pl   = pool.makeClass(PKG + ".SkyyVaultPlugin", pool.get(T["JP"]))
ALL = [cfg, dat, cod, sto, sjob, thf, ses, chg, win, page, clt, vs, tick, hk, scn, btn, bfl, btk, swt, vv]

# ================= VCfg: logger, bridge, config, atomic files =================
CFG_LINES = [
    "# SkyyVault config - change it in game (SkyWynn Menu -> Server Setup -> Vault, or /vaultadmin config <key> <value>),",
    "# or edit it here, then /vaultadmin reload (or restart the server)",
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
          "public static volatile long STEP = %dL;" % DEF_STEP, "public static volatile long AFTER_SWITCH_MS = %dL;" % (DEF_AFTER_SWITCH_S * 1000),
          "public static volatile long SAVE_DELAY_MS = %dL;" % DEF_SAVE_DELAY_MS, "public static volatile boolean PAGE_MODE = true;",
          # 0.1.1: the config kit binds openMode to this String twin (a choice row cannot bind a boolean); VCfg.load and the kit's
          # after= hook (VHooks.afterOpenMode) keep PAGE_MODE, which the rest of the mod reads, in step with it
          "public static volatile String OPEN_MODE = \"page\";",
          # 0.1.2: page arrows (config kit rows pageArrows / arrowLayout / straySweepSeconds)
          "public static volatile boolean ARROWS = true;", "public static volatile String ARROW_LAYOUT = \"row\";",
          "public static volatile long SWEEP_MS = %dL;" % (DEF_SWEEP_S * 1000),
          "public static final long CONFIRM_MS = 10000L;", "public static final int MAX_CAP = %d;" % MAX_CAP,
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
  return "free pages " + FREE_PAGES + ", max " + MAX_PAGES + ", " + SLOTS + " slots per page, price " + PRICE + " +" + STEP + " per page, openMode " + (PAGE_MODE ? "page" : "chest") + ", page arrows " + (ARROWS ? ARROW_LAYOUT : "off") + ", stray check every " + (SWEEP_MS / 1000L) + " s";
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
               FILES=["Skyy_SkyyVault/config.properties"], RELOAD="VHooks.reloadCfg", KEEP=20,
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
          "public static final java.util.concurrent.ConcurrentHashMap CONFIRM = new java.util.concurrent.ConcurrentHashMap();",
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
# arm on the first call, true on a second call within CONFIRM_MS. ONE key for the page's Buy button AND /vault buy, naming the page
# number, so a click and a typed command combine and a confirm armed for page N never buys page N + 1.
M(sto, r"""
public static String buyKey(java.util.UUID u, int page) {
  return "buy:" + u + ":" + page;
}""")
M(sto, r"""
public static boolean confirm(String key) {
  long now = System.currentTimeMillis();
  Object o = CONFIRM.get(key);
  if (o instanceof Long && ((Long) o).longValue() >= now) { CONFIRM.remove(key); return true; }
  CONFIRM.put(key, Long.valueOf(now + @PKG@.VCfg.CONFIRM_MS));
  return false;
}""")
M(sto, r"""
public static boolean armed(String key) {
  Object o = CONFIRM.get(key);
  return o instanceof Long && ((Long) o).longValue() >= System.currentTimeMillis();
}""")
M(sto, r"""
public static void disarm(String key) {
  CONFIRM.remove(key);
}""")
M(sto, r"""
public static void pruneConfirms(long now) {
  java.util.Iterator it = CONFIRM.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || ((Long) v).longValue() < now) it.remove();
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
# buy the next page: coins first (must be TRUE), then the page, written and read back; a failed write reverts + refunds
M(sto, r"""
public static String buy(java.util.UUID u, String name) {
  @PKG@.VData d = load(u);
  if (d == null) return "-Your vault file cannot be read - nothing was charged. Please tell an admin.";
  int next = d.unlocked + 1;
  if (next > @PKG@.VCfg.MAX_PAGES) return "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ").";
  long cost = price(next);
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
    if (!back) return "+Bought vault page " + next + " - the file will be saved on the next try.";
    return "-The vault file could not be saved - page " + next + " was not bought." + refund(u, cost);
  }
  log("BUY " + u + " " + name + " page " + next + " cost " + cost);
  return "+Bought vault page " + next + " for " + grp(cost) + " coins - you now own " + next + " of " + @PKG@.VCfg.MAX_PAGES + " pages.";
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
  if (!admin) out.add("=/vault opens it, /vault 2 opens page 2, /vault next | prev switch pages, /vault pages shows the page buttons." + (@PKG@.VCfg.ARROWS ? " The arrows in the vault window turn pages too." : ""));
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
  @IS@ prev = null;
  if (page > 1) prev = make(PREV, "< Page " + (page - 1), C_ARROW, inside ? new String[] { "Click to turn to page " + (page - 1) + " of " + unlocked + ".", here } : new String[] { "Click to turn to page " + (page - 1) + " of " + unlocked + "." }, s.owner, s.sid);
  else prev = make(PREV_OFF, "First page", C_OFF, inside ? new String[] { here } : new String[] { "You are on page 1 of " + unlocked + "." }, s.owner, s.sid);
  @IS@ next = null;
  if (page < unlocked) {
    next = make(NEXT, "Page " + (page + 1) + " >", C_ARROW, inside ? new String[] { "Click to turn to page " + (page + 1) + " of " + unlocked + ".", here } : new String[] { "Click to turn to page " + (page + 1) + " of " + unlocked + "." }, s.owner, s.sid);
  } else if (unlocked < @PKG@.VCfg.MAX_PAGES) {
    int nx = unlocked + 1;
    long cost = @PKG@.VStore.price(nx);
    String nm = cost > 0L ? "Buy page " + nx : "Unlock page " + nx + " - free";
    String l1 = cost > 0L ? @PKG@.VStore.grp(cost) + " coins from your active profile." : "Free - no coins needed.";
    next = make(BUY, nm, C_GOLD, inside ? new String[] { l1, "Click, then click again within 10 s.", here } : new String[] { l1, "Click, then click again within 10 s." }, s.owner, s.sid);
  } else {
    next = make(NEXT_OFF, "Last page", C_OFF, inside ? new String[] { "You own every vault page (" + unlocked + " of " + max + ").", here } : new String[] { "You own every vault page (" + unlocked + " of " + max + ")." }, s.owner, s.sid);
  }
  @IS@ info = null;
  @IS@ fill = null;
  if (!inside) {
    info = make(INFO, "Page " + page + " of " + unlocked, C_GOLD, new String[] { "" + used + " of " + usable + " slots used", "Shared by all your profiles", "/vault <page> jumps to a page" }, s.owner, s.sid);
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

# ================= VaultPage part 1 (inline, rebuilt only after a click; never periodic updates) =================
for f in ("public @PKG@.VSession sess;", "public int sel;", "public String info;"):
    F(page, f)
C(page, r"""
public VaultPage(@PR@ pr, @PKG@.VSession s, int sel) {
  super(pr, @LIFE@.CanDismiss);
  this.sess = s; this.sel = sel < 1 ? 1 : sel; this.info = "";
}""")
M(page, r"""
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
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
M(page, r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(page, r"""
public static String textOf(String res) {
  if (res == null || res.length() == 0) return "";
  char c = res.charAt(0);
  if (c == '+' || c == '-' || c == '=') return res.substring(1);
  return res;
}""")
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
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  boolean live = this.sess != null && !this.sess.closed;
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 19);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 19);
  String ys = style("#6a4a12", "#8a641a", "#3e2a08", "#fff2d6", 19);
  String ds = style("#262f3d", "#303b4c", "#1a212c", "#7f8ea6", 19);
  b.appendInline((String) null, "Group #SkyyVault { Anchor: (Width: 1040, Height: 640); Background: #0b1524(0.96); Padding: (Horizontal: 26, Vertical: 16); LayoutMode: Top; }");
  b.appendInline("#SkyyVault", "Group { Anchor: (Height: 3); Background: #b48cff; }");
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 58); Text: \"Vault\"; Style: (FontSize: 34, RenderBold: true, TextColor: #dccaff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyVault", "Label #SkyyVSub { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 18, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVSub.Text", "One chest shared by ALL your profiles - put items in on one profile and take them out on another.");
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 12); Text: \"\"; }");
  if (d == null) {
    b.appendInline("#SkyyVault", "Label #SkyyVErr { Anchor: (Height: 80); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ff9d6b, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyVErr.Text", "Your vault file cannot be read right now. Nothing in it was changed - please tell an admin.");
    b.appendInline("#SkyyVault", "Group #SkyyVErrRow { Anchor: (Height: 60); LayoutMode: Left; }");
    b.appendInline("#SkyyVErrRow", "Label { Anchor: (Width: 419, Height: 52); Text: \"\"; }");
    b.appendInline("#SkyyVErrRow", "TextButton #SkyyVClose { Anchor: (Width: 150, Height: 52); Text: \"Close\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
    return;
  }
  int unlocked = d.unlocked;
  int max = unlocked > @PKG@.VCfg.MAX_PAGES ? unlocked : @PKG@.VCfg.MAX_PAGES;
  if (this.sel < 1) this.sel = 1;
  if (this.sel > max) this.sel = max;
  boolean showing = live && this.sess.page == this.sel;
  b.appendInline("#SkyyVault", "Group #SkyyVNav { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyVNav", "Label { Anchor: (Width: 65, Height: 52); Text: \"\"; }");
  b.appendInline("#SkyyVNav", "TextButton #SkyyVPrev { Anchor: (Width: 190, Height: 52); Text: \"< Prev\"; " + (this.sel > 1 ? bs : ds) + " }");
  b.appendInline("#SkyyVNav", "Label #SkyyVPageLbl { Anchor: (Width: 478, Height: 52); Text: \"\"; Style: (FontSize: 26, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVPageLbl.Text", "Page " + this.sel + " of " + unlocked + (this.sel > unlocked ? "  (locked)" : ""));
  b.appendInline("#SkyyVNav", "TextButton #SkyyVNext { Anchor: (Width: 190, Height: 52); Text: \"Next >\"; " + (this.sel < max ? bs : ds) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVNext", @EVD@.of("a", "next"));
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 10); Text: \"\"; }");
  int shown = max < 10 ? max : 10;
  int start = 1;
  if (max > 10) {
    start = this.sel - 4;
    if (start < 1) start = 1;
    if (start + 9 > max) start = max - 9;
  }
  int rowW = shown * 84 - 8;
  int pad = (988 - rowW) / 2;
  b.appendInline("#SkyyVault", "Group #SkyyVNums { Anchor: (Height: 58); LayoutMode: Left; }");
  if (pad > 0) b.appendInline("#SkyyVNums", "Label { Anchor: (Width: " + pad + ", Height: 52); Text: \"\"; }");
  for (int i = 0; i < shown; i++) {
    int n = start + i;
    String st = n == this.sel ? gs : (n <= unlocked ? bs : ds);
    if (i > 0) b.appendInline("#SkyyVNums", "Label { Anchor: (Width: 8, Height: 52); Text: \"\"; }");
    b.appendInline("#SkyyVNums", "TextButton #SkyyVNum" + n + " { Anchor: (Width: 76, Height: 52); Text: \"" + n + "\"; " + st + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyVNum" + n, @EVD@.of("a", "num:" + n));
  }
  b.appendInline("#SkyyVault", "Label #SkyyVUsed { Anchor: (Height: 44); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
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
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 6); Text: \"\"; }");
  b.appendInline("#SkyyVault", "Group #SkyyVAct { Anchor: (Height: 66); LayoutMode: Left; }");
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 44, Height: 58); Text: \"\"; }");
  String openTxt = live ? "Open as chest" : ("Open page " + this.sel);
  b.appendInline("#SkyyVAct", "TextButton #SkyyVOpen { Anchor: (Width: 330, Height: 58); Text: \"" + openTxt + "\"; " + (this.sel <= unlocked ? gs : ds) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVOpen", @EVD@.of("a", "open"));
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 20, Height: 58); Text: \"\"; }");
  int next = unlocked + 1;
  String buyTxt = "";
  String buySt = ds;
  if (next <= @PKG@.VCfg.MAX_PAGES) {
    long c = @PKG@.VStore.price(next);
    buyTxt = @PKG@.VStore.armed(@PKG@.VStore.buyKey(u, next)) ? ("Sure? Buy page " + next) : ("Buy page " + next + " - " + @PKG@.VStore.shortAmt(c) + " coins");
    buySt = ys;
  } else {
    buyTxt = "All pages bought";
    buySt = ds;
  }
  b.appendInline("#SkyyVAct", "TextButton #SkyyVBuy { Anchor: (Width: 380, Height: 58); Text: \"" + safe(buyTxt) + "\"; " + buySt + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVBuy", @EVD@.of("a", "buy"));
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 20, Height: 58); Text: \"\"; }");
  b.appendInline("#SkyyVAct", "TextButton #SkyyVClose { Anchor: (Width: 150, Height: 58); Text: \"Close\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 12); Text: \"\"; }");
  String[] help = null;
  if (live) {
    help = new String[] { "Drag items between your inventory and the vault slots. Close or Esc saves your vault.",
                          "Vault slots not showing next to this page? Click Open as chest.",
                          "Commands: /vault 2 opens page 2, /vault next and /vault prev switch pages, /vault info" };
  } else {
    help = new String[] { "Pick a page, then click Open to see its items as a chest.",
                          "In the chest: drag items in and out - Esc saves. /vault 2 or /vault next switches pages.",
                          "Every profile opens this same vault. Commands: /vault buy, /vault info" };
  }
  for (int i = 0; i < help.length; i++) {
    b.appendInline("#SkyyVault", "Label #SkyyVHelp" + i + " { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyVHelp" + i + ".Text", help[i]);
  }
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyVault", "Label #SkyyVInfo { Anchor: (Height: 36); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVInfo.Text", textOf(this.info));
}""")

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
M(vs, r"""
public static String open(@PR@ pr, @REF@ ref, @ST@ st, int page, int mode) {
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
  if (mode == 2 && s.layout != 0) return "=Vault page " + page + " of " + d.unlocked + " (shared by all your profiles): the arrows in the bottom row turn pages, Esc saves. /vault <page> jumps.";
  if (mode == 2) return "=Vault page " + page + " of " + d.unlocked + " (shared by all your profiles): drag items in and out, Esc saves. /vault next or /vault <page> switches pages.";
  return null;
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
# after /vault buy (armed or bought): the player's own vault page on screen (with or without slots) shows the new state + the result
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
M(vs, r"""
public static void resync(@PKG@.VSession s, @REF@ ref, @ST@ st) {
  try { if (s.window != null) s.window.invalidate(); } catch (Throwable t) { }
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
  String bkey = @PKG@.VStore.buyKey(u, next);
  int want = @PKG@.VBtn.FILLER;
  if (slot == s.prevIdx) want = s.page > 1 ? @PKG@.VBtn.PREV : @PKG@.VBtn.PREV_OFF;
  else if (slot == s.nextIdx) {
    if (s.page < unlocked) want = @PKG@.VBtn.NEXT;
    else if (unlocked < @PKG@.VCfg.MAX_PAGES) want = @PKG@.VBtn.BUY;
    else want = @PKG@.VBtn.NEXT_OFF;
  } else if (slot == s.infoIdx) want = @PKG@.VBtn.INFO;
  if (want == @PKG@.VBtn.PREV || want == @PKG@.VBtn.NEXT) {
    @PKG@.VStore.disarm(bkey);
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
    long cost = @PKG@.VStore.price(next);
    if (!@PKG@.VStore.confirm(bkey)) {
      if (cost > 0L) tell(pr, "=Buy vault page " + next + " for " + @PKG@.VStore.grp(cost) + " coins? Click the gold arrow again within 10 s (or type /vault buy).");
      else tell(pr, "=Unlock vault page " + next + " for free? Click the gold arrow again within 10 s (or type /vault buy).");
      refreshRow(s);
      if (s.mode == 1) refreshPage(p, s);
      return;
    }
    String g = gate(u);
    if (g != null) { tell(pr, g); refreshRow(s); return; }
    String res = @PKG@.VStore.buy(u, pr == null ? "" : pr.getUsername());
    tell(pr, res);
    if (res != null && res.startsWith("+") && d.unlocked >= next) {
      String r = swap(s, next);
      if (r != null) { closeAny(p, ref, st, s); tell(pr, r); return; }
    } else refreshRow(s);
    if (s.mode == 1) refreshPage(p, s);
    return;
  }
  if (want != @PKG@.VBtn.FILLER) @PKG@.VStore.disarm(bkey);
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
  try { @PKG@.VStore.pruneConfirms(now); } catch (Throwable t) { }
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
    String bkey = @PKG@.VStore.buyKey(u, d.unlocked + 1);
    if (a.equals("prev") || a.equals("next") || a.startsWith("num:")) {
      if (tp < 1 || tp > max) return;
      @PKG@.VStore.disarm(bkey);
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
      @PKG@.VStore.disarm(bkey);
      if (this.sel > d.unlocked) { this.info = "-Page " + this.sel + " is locked - buy it first."; rebuild(); return; }
      String r = @PKG@.VSessions.open(this.playerRef, ref, store, this.sel, 2);
      if (r != null && r.startsWith("=")) @PKG@.VSessions.tell(this.playerRef, r);
      else if (r != null) { this.info = r; rebuild(); }
      return;
    }
    if (a.equals("buy")) {
      int next = d.unlocked + 1;
      if (next > @PKG@.VCfg.MAX_PAGES) { this.info = "-You already own every vault page."; rebuild(); return; }
      if (!@PKG@.VStore.confirm(@PKG@.VStore.buyKey(u, next))) {
        this.info = "=Page " + next + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(next)) + " coins - click Sure? or type /vault buy within 10 s.";
        rebuild();
        return;
      }
      String r = @PKG@.VStore.buy(u, this.playerRef.getUsername());
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
cmd("VaultBuyCmd", "buy", "Buy the next vault page with coins (type it twice to confirm)", [],
    r"""@PKG@.VData d = @PKG@.VStore.load(pr.getUuid());
    if (d == null) { @PKG@.VSessions.tell(pr, "-Your vault file cannot be read - nothing was charged. Please tell an admin."); return; }
    int next = d.unlocked + 1;
    if (next > @PKG@.VCfg.MAX_PAGES) { @PKG@.VSessions.tell(pr, "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ")."); return; }
    if (!@PKG@.VStore.confirm(@PKG@.VStore.buyKey(pr.getUuid(), next))) {
      String arm = "=Page " + next + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(next)) + " coins - type /vault buy again or click Sure? within 10 s.";
      @PKG@.VSessions.tell(pr, arm);
      @PKG@.VSessions.afterBuy(pr, ref, store, arm);
      return;
    }
    String res = @PKG@.VStore.buy(pr.getUuid(), pr.getUsername());
    @PKG@.VSessions.tell(pr, res);
    @PKG@.VSessions.afterBuy(pr, ref, store, res);""")
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
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.VTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyVault] @VERSION@ ready - /vault (shared by all profiles), /vaultadmin; " + cfg + "; data in " + dir);
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
BTN_ITEMS = [
    ("Prev", "Previous page", "Turns the vault window to the previous page."),
    ("PrevOff", "First page", "You are on the first vault page."),
    ("Next", "Next page", "Turns the vault window to the next page."),
    ("NextOff", "Last page", "You own every vault page."),
    ("Buy", "Buy next page", "Buys the next vault page with coins: click, then click again within 10 s."),
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
B.assemble(jar, man, OUT, files)
