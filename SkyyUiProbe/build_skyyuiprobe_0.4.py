"""SkyyUiProbe 0.4 - build script (javassist via jpype). A small DEV / TEST mod: the vanilla-look kit's probe pages (0.1 / 0.2), the
two VAULT WINDOW probes (0.3 / 0.3.1) and, new in 0.4, the MINIMAP probes P1-P5 of research/Minimap-Research.md section 9.
Run:   python SkyyUiProbe/build_skyyuiprobe_0.4.py            -> SkyyUiProbe/SkyyUiProbe-0.4.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
       --dump <file.json> also writes what every view sends (appends + b.set lines + extra Java lines, the index bindings, and since
       0.4 the map probe constants under "map") for the harness; nothing else changes. --dump-only <file.json> writes it and stops
       before the Java (no JVM, no class / jar written).
Check: python SkyyUiProbe/test_skyyuiprobe_0.4.py   (bare JVM, -Xverify:all; every 0.3.1 check plus the map probe checks; re-run it
       after every build and whenever the kit id changes - it refuses a jar built with another kit).

WHY 0.4 (copy + edit of build_skyyuiprobe_0.3.1.py, the SET pin; Skyy 2026-10-03, OPEN-QUESTIONS "ANSWERED 2026-10-03 (Skyy,
research/Minimap-Research.md questions)", LOCKED): skip Cartographer and DapperMap, keep BetterMap for the big map, "a quick
SkyyUiProbe test build first (server-sent map pictures in a HUD, probe steps P1-P5), then OUR OWN MINIMAP WIDGET in SkyyHud" -
round, top-right, ~160 px, north-up, no world-thread map work (DapperMap's world-thread tick took 37-57 ms = lag).
Everything of 0.3.1 stays as it was (pages 1-24 with the same markup, the window probes, /skyprobe, /skyprobe <page | list>, the
permissions, the access audit). NEW: every map probe is started ONLY by an op's command for THAT player, is OFF by default, and each
step prints ONE chat line that says what to look at. /skyprobe map lists them; /skyprobe map <step> (a 2-word usage variant, admin):
  p1a       P1 A: a small HUD box top-right with ONE runtime PNG (128 x 128, made on the server: no vanilla pixels) in an AssetImage -
            MapAsset (a CommonAsset subclass) sent as AssetInitialize + AssetPart + AssetFinalize in ONE write to that player (the
            engine's CommonAssetModule.sendAsset sequence, not broadcast), NO RequestCommonAssetsRebuild
  p1b       P1 B: a NEW picture (other colours = a new asset) + ONE RequestCommonAssetsRebuild after it
  p2        P2: a 160 px ROUND minimap top-right, north-up: a 9 x 9 grid of 32 px map tiles (one tile = one 32-block chunk, 1 px per
            block) in a Group masked by a circle PNG made here (MaskTexturePath), a ring and a centre arrow (8 headings) made here;
            panned up to 4 times a second with ONE Anchor set (the grid Group), and when a chunk border is crossed only the 9 tiles
            that enter the window change (a 9 x 9 ring buffer: slot = cx mod 9 + 9 * (cz mod 9) - their Anchor + AssetPath); the
            grid Group holds 17 x 17 tile positions, so it re-bases (81 Anchor sets) only every 4 or more chunks. Tile pictures:
            the REAL map pieces the outbound tap captured for this player (BetterMap's own tiles and cave tiles included), else the
            engine's shared tile cache (WorldMapManager.getImageIfInMemory - a ConcurrentHashMap read; never getImageAsync, so the
            server never generates a tile for us), else a test pattern made here. The first P2 of a connection sends ONE
            RequestCommonAssetsRebuild after its first batch (the mask is a texture path - Cartographer does the same for its mask);
            later tiles never rebuild.
  p2sharp   P2 with the tiles enlarged on the SERVER (nearest neighbour to 32 px) instead of by the client: the blur check
  p3        P3: arms the reconnect / world-switch check: the P3 picture is sent and shown now; after the NEXT world change or
            reconnect (PlayerReadyEvent + 1.5 s, SkyyHud's attach delay) the box comes back with the SAME picture path WITHOUT
            sending it again - Skyy says whether the picture is still there
  p3resend  P3 with the re-deliver option ON: the picture is sent again (forced) on the ready event first
  p4        P4: the OUTBOUND packet tap counts what the server sends this player for 60 s: UpdateWorldMap packets, chunks, null
            chunks (unloads), markers added / removed, protocol bytes (computeSize, before netty compression), ClearWorldMap, the
            biggest burst per 0.25 s tick, the picture sizes / palettes seen - BetterMap on vs off = two server sessions (the mod list)
  p5        P5: the same counts per WORLD for up to 3 worlds: the engine sends ClearWorldMap at every world change
            (Universe.resetPlayer -> Player.resetManagers -> WorldMapTracker.clear), which starts the next 60 s segment, and the
            ready event names the world (map on / OFF, generator class, image scale): enter an island and the Zone 1 world
  off       everything off for this player: the HUD removed through the HudManager (world thread), counting stopped with its summary,
            P3 disarmed
  status    one chat line from the server tick: what runs, the tile sources, pictures sent, counts so far

HUD SLOT (critical; HytaleServer.jar 0.6.8 bytecode, re-checked by this build's ENGINE FACTS): a player has MANY custom HUDs, keyed.
HudManager.customHuds is a LinkedHashMap keyed by CustomUIHud.getKey(); addCustomHud(pr, hud) replaces only an entry with the SAME key
(old.onRemove(), CustomHud(key, 0, clear=true, null), put, hud.show()), removeCustomHud(pr, key) clears that key only, and the
CustomHud packet carries hudId + zOrder (the client keeps one document per hudId). The engine itself shows several at once
(GameModeTypeState, InstanceRemovalHudSystem). SkyyHud shows its HUD with show() under key "skyyhud_main" (never registered in the
HudManager). So this probe uses its OWN key "SkyyUiProbeMap" (zOrder 5) through the documented HudManager path and never sends a
packet for "skyyhud_main": nothing is borrowed, so nothing has to be given back. World change: Universe.resetPlayer ->
Player.resetManagers sends ResetUserInterfaceState and clears every REGISTERED HUD (onRemove) - every custom HUD must be shown again
after a world change (SkyyHud does that on PlayerReadyEvent); the probe's MapHud.onRemove ends its session there. The harness drives
both HUDs through the real HudManager and proves it. RECOMMENDATION for the SkyyHud minimap widget: a SECOND keyed HUD owned by
SkyyHud (e.g. key "SkyyHudMinimap"), placed from the SkyyHud layout / editor and re-shown on PlayerReadyEvent like the main one -
not inside "skyyhud_main", whose full re-sends (show() = clear + every widget, on shape changes) would wipe and re-append 81+
AssetImages, and whose 1 s widget tick should stay apart from the map's 4 Hz pans.

MAPIMAGE (protocol.packets.worldmap.MapImage, 0.6.8 bytecode of ImageBuilder.encodeToPalette / $Color.pack / BitFieldArr): fields
width, height, int[] palette (each 0xRRGGBBAA: r << 24 | g << 16 | b << 8 | a), byte bitsPerIndex (4 for <= 16 colours, 8 <= 256,
12 <= 4096, else 16), byte[] packedIndices = BitFieldArr bytes: index i takes bits [i * bits, i * bits + bits), LSB first (bit p =
byte p / 8, bit p % 8; a value split over two bytes keeps its low bits in the first); pixel order i = z * width + x (row 0 = the
north edge: -Z is north, engine ParticleAttractor docs). Vanilla imageScale 0.5 = 16 x 16 per 32-block chunk (BetterMap MEDIUM 0.5,
HIGH 1.0 = 32 x 32, LOW 0.25 = 8 x 8). MapPng (java.util.zip Deflater + CRC32, no java.awt) writes <= 256 colours as an indexed PNG
(bit depth 1 / 2 / 4 / 8, PLTE + tRNS for the alpha), more colours as 8-bit RGBA; every picture this mod makes (P1 / P3 pictures,
mask, ring, arrows, test tiles) is built AS a MapImage first, so the real tiles and the generated ones take the same encoder.

THREADS (no map work on the world thread): commands and the ready / disconnect events only read the player's position / heading /
world (cheap reads) and queue a request; ONE 0.25 s tick on HytaleServer.SCHEDULED_EXECUTOR (started by the first request, cancelled
when nothing runs: off by default) does everything else under one lock: it drains the tap queues, handles the requests, encodes and
sends the pictures (at most 40 new tile PNGs per tick, 120 for the first P2 build), pans the HUD (CustomUIHud.update from this thread,
as SkyyHud's tick does) and posts ONE world-thread read per world for the next tick's positions. HudManager calls (a LinkedHashMap)
run on the world thread only (MapAttach / MapDetach). The tap (MapTap, a PlayerPacketWatcher registered in start(), deregistered in
shutdown() - the SkyySacks pattern) runs on whatever thread writes the packet (the WorldMapManager's own ticking thread for the vanilla
stream; BetterMap's threads for its own): when nothing asked for packets it returns after one volatile read; else two instanceof
checks, one ConcurrentHashMap get, an AtomicInteger bound (20,000 per player per tick, beyond = counted as dropped) and a lock-free
ConcurrentLinkedQueue add - it never blocks, never throws (every Throwable is counted), never reads the packet.
CLEANUP: off, a world change (MapHud.onRemove from the engine's resetHud, the world-thread read seeing another store, the ready event
in another world), a disconnect (PlayerDisconnectEvent: sessions end without packets, the per-connection "already sent" list is
cleared; P3 stays armed on purpose - it is the reconnect test - for 10 minutes or until off) and the plugin shutdown (the tap
deregistered, the tick cancelled, every HUD removed through the world thread). P5 is the one probe that follows the player through
world changes (that is its test); P4 stops at the first world change with a partial summary.
No data files, no config rows, no bridge keys, nothing written anywhere (the harness starts it twice on a copy of the live data).
UNVERIFIED (that is what the probes are for): AssetImage with a runtime asset in a HUD; whether 0.6.8 shows runtime assets without a
RequestCommonAssetsRebuild and what the rebuild costs on the client; MaskTexturePath with a runtime PNG on a Group; the client's
scaling filter for 16 px tiles shown at 32 px (p2 vs p2sharp); runtime assets after a reconnect / world switch; which way the client
stacks zOrder 5 against SkyyHud's 0; the measured stream with BetterMap on / off; whether island worlds stream a map at all.

WHY 0.3.1 (copy + edit of build_skyyuiprobe_0.3.py, the SET pin; HANDOFF 2026-10-02 "PROBE P2 (/skyprobe secgrid) did NOT run"):
Skyy's /skyprobe secgrid (probe 24) failed in game with "java.lang.IllegalAccessError: class com.skyy.uiprobe.ProbeWin tried to access
protected method ... CustomUIPage.sendUpdate(UICommandBuilder)". ProbeWin.open called pg.sendUpdate(ub) on the page, and sendUpdate is
PROTECTED: javassist compiled the call, but the JVM lets a protected member be used only from a subclass of its class (an instance
member only on a reference of that subclass), and it checks that when the line first RUNS. The 0.3 harness loaded every class
(-Xverify:all does not resolve method calls) and drove ProbeWin.open only without a player component, so it never reached the line.
  FIX     ProbePage.sendSection(int windowId) (public) builds the one "#SkyyPbSgGrid.InventorySectionId" update and calls
          this.sendUpdate(ub) on itself; ProbeWin.open calls pg.sendSection(s.winId) at the same place (right after
          openCustomPageWithWindows returned, before the change listener and the count baseline): same command, same packet, same
          order, same log line. Probe 24 keeps its purpose (research P2: the page's 9-slot draggable ItemGrid bound to the window's
          section - does the client show and drag the window's real slots? every MoveItemStack handled by the engine, items counted
          before and after every move).
  SCAN    every engine member the 16 classes reference was checked (this build's ACCESS AUDIT + the harness's audit with the JVM's
          own MethodHandles.Lookup): that sendUpdate was the only one the JVM refuses. The other non-public engine members are all
          used from their own subclass, on this / super: ProbePage rebuild() / close() / playerRef (CustomUIPage), ProbeWindow
          invalidate() (Window), ProbeBox internal_getSlot() + super.cantAddToSlot / cantDropFromSlot / cantRemoveFromSlot /
          internal_moveItemStackFromSlot x2 (SimpleItemContainer / ItemContainer), both command constructors setPermissionGroups()
          (AbstractCommand), SkyyUiProbePlugin super.shutdown() (PluginBase). Nothing else needed a change.
  GUARD   the build refuses such a call itself now (ACCESS AUDIT on the class files as written, before the jar is assembled): a
          protected engine member used from a class that is not its subclass, a package-private / private engine member, a
          non-public engine class -> SystemExit, no jar. A self-test compiles the 0.3 call (a non-subclass calling
          CustomUIPage.sendUpdate) into a throw-away class first and asserts the audit names it. Run on the 0.3 jar's classes, the
          audit names exactly ProbeWin.open -> CustomUIPage.sendUpdate.
  HARNESS test_skyyuiprobe_0.3.1.py now EXECUTES the open paths of probes 23 and 24 (/skyprobe win | secgrid and the list's Open
          buttons) and what follows them (arrow click, a drag + count, the re-send, Back, Close, Esc, a client close, a world change)
          through the REAL PageManager, WindowManager, ContainerWindow and CustomUIPage code with a stand-in player, store and
          inventory (its section O) - the 0.3 jar fails it with the game's exact IllegalAccessError - and checks every reference in
          the jar's bytecode with the JVM's own access rules (its section X).
Unchanged from 0.3: pages 1-24 (markup, texts, sizes, the index's "New in 0.3" line - the window probes came with 0.3), commands,
permissions, the probe box and its locks, the packet watcher, the re-send gate, the return on close, the 16 classes, every log line
except the version in the ready line.

WHY 0.3 (made by copy + edit of build_skyyuiprobe_0.2.py, the SET pin; Skyy 2026-10-02, OPEN-QUESTIONS "Q&A with Skyy 2026-10-02" R2
LOCKED: "try the one-click vault arrow row on our own vanilla-look page next to the vault slots (one probe first; the in-chest arrows
stay as a fallback)"). The vanilla chest never tells the server when an item is LIFTED, so a one-click arrow needs our own page next to
the vault window - and nobody has seen the client draw a window next to a CUSTOM page yet. Two probes answer that, ~30 s each:
  P1 /skyprobe win      (probe 23) a small custom page opened with PageManager.openCustomPageWithWindows(page, ProbeWindow), a
                        ContainerWindow over a SCRATCH 9-slot container (the "probe box"): does the client draw the chest panel and the
                        player's inventory next to the page, can you drag between them, where does the panel sit? Folded in (research
                        P3): a 3-slot non-draggable arrow grid (AreItemsDraggable false, InfoDisplay None, SlotClicking with
                        locksInterface=false - the SkyyMenu launcher pattern, the vault 0.1.6 plan): one press = one chat line, nothing
                        lifts. The arrows are SkyyVault's own Skyy_Vault_Prev / Info / Next items when the server knows them (so this
                        also shows the 0.1.6 icons), else the vanilla stand-ins Weapon_Arrow_Crude / Ingredient_Bar_Iron /
                        Weapon_Arrow_Iron - each slot is new ItemGridSlot(new ItemStack(id, 1)) + setName / setDescription /
                        setActivatable(true), never a stack that can carry metadata.
  P2 /skyprobe secgrid  (probe 24) the same window + page, plus a 9-slot DRAGGABLE ItemGrid on the page bound to the window's section:
                        b.set("#SkyyPbSgGrid.InventorySectionId", <window id>) - does it show and drag the window's real slots? Every
                        move is handled by the ENGINE (MoveItemStack -> InventoryUtils.moveItem -> the probe box); the mod logs each
                        inventory packet the client sends while a probe window is open (section ids, slots, quantity) and its move
                        handler counts the items (probe box + the player's whole inventory, per item id) before and after every
                        change: a chat line + a log line per move, a WARNING when the count changes or a probe item leaves the box.
  Kept from 0.2 unchanged: kit probe pages 1-22 (same numbers, names, content, footer), /skyprobe list, the flat index (now 24
  entries in two columns of 12; the two window probes first, green).

DECISIONS (where the spec left room):
  * InventorySectionId is SET (b.set, int), not written inline: the two libraries that use it (HyUI ItemGridBuilder, ktaleui
    ItemGridRef, installed mods read-only) both set it through "#Id.InventorySectionId". It is sent as ONE page update right after
    openCustomPageWithWindows returned, i.e. after the OpenWindow packet (the engine writes CustomPage first, then OpenWindow), so the
    client never gets a grid bound to a window it does not have yet. The page markup itself is proven properties only (assert_proven
    passes with nothing allowed), so a disconnect on P2 names the binding. 0.3.1: the page sends that update itself
    (ProbePage.sendSection -> this.sendUpdate; sendUpdate is protected - see WHY 0.3.1).
  * P2 binds ONLY the window's section - no grid on the player's storage (-2) as the research suggested: the task says scratch
    containers only, never real player storage. P2 has no arrow grid (P3 is in P1) so P2 tests one thing.
  * The probe box (com.skyy.uiprobe.ProbeBox, a SimpleItemContainer subclass, 9 slots) holds 3 LOCKED probe items - Weapon_Mace_Iron,
    Armor_Iron_Head, Tool_Shovel_Iron: weapon / armor / tool = MaxStack 1 (Item.processConfig), so nothing can ever merge with them -
    plus 6 free slots for the admin's OWN items. ProbeBox refuses (by item id, wherever the probe item sits, so Sort cannot unlock
    one): removing or dropping a probe item (cantRemoveFromSlot / cantDropFromSlot), adding anything onto a probe item or adding a
    stack with a probe item's id (cantAddToSlot - this also blocks the engine's swap path, which never asks the TARGET slot
    cantRemoveFromSlot), and answers a refused whole-slot move (shift-click / Take All) with the engine's own failed MoveTransaction
    instead of null (SkyyVault VView, live since 0.1.2: no "Failed to run task!" NPE). The probe items are made once per admin and
    never leave the box, so the probe creates nothing.
  * One probe box per admin for the server's life (never shared). When its window closes - Esc, Close, Back, a world change or a
    disconnect (the engine's closeAllWindows) - ProbeWindow.onClose0 returns the admin's own items exactly like vanilla's crafting
    windows do (StructuralCraftingWindow.onClose0), but storage first (InventoryComponent.STORAGE_HOTBAR_BACKPACK) and counted before
    and after; what does not fit STAYS in the box (nothing is dropped in the world) and the admin is told to make room and reopen.
    A box that still holds an admin's items at plugin shutdown is logged item by item (WARNING). Kept on purpose after the 2026-10-02
    review (finding 2, the safe option): closeAllWindows also runs on a WORLD CHANGE, where vanilla's addOrDropItemStacks would drop
    the leftovers into the world the admin is leaving (an instance world may unload) - the box keeps them for /skyprobe win in any
    world; the only loss left is a server stop / crash while the box holds items (it lives in RAM), which the test steps rule out
    (bread or stone only, 6+ free inventory slots).
  * A refused move (a locked probe item) changes nothing, so the engine sends nothing back and the client could keep its own guess (an
    item shown moved, a ghost in the inventory). So after every client packet for the probe window the server re-sends the truth: the
    window (Window.invalidate through ProbeWindow.resend) and the player's six inventory sections (markDirty) - SkyyVault 0.1.5's
    resync. ProbeWindow is a ValidatedWindow and validate() always answers true (it never closes the window), but the engine calls it
    far more often than once per packet: InventoryUtils.getSectionById (every inventory packet that names the window) AND
    Player.moveTo -> WindowManager.validateWindows (every movement tick, knockback, teleport). So validate() alone never re-sends
    (review 2026-10-02, finding 1): the packet watcher (netty thread, PlayerChannelHandler.channelRead runs the inbound filters BEFORE
    the engine's handler queues its world task) stamps ProbeSession.sawAt when a packet names the probe window (MoveItemStack either
    end, DropItemStack, InventoryAction, SendWindowAction) or is a shift-click (SmartMoveItemStack: its target may be the window), and
    validate() queues ONE re-send per stamp, SYNC_DELAY_MS later on the world thread (World.scheduleAfter: it lands after that
    packet's handler even when a movement validate saw the stamp first); a stamp older than SAW_MS is dropped. Without the watcher
    (registerInbound failed - logged) the fallback is at most one re-send per SYNC_RATE_MS.
  * Esc on a window page: PageManager only calls onDismiss (it never closes windows), so the page schedules a check 1.5 s later on
    the world thread (World.scheduleAfter): still open -> the server closes it; already closed -> the log says the client did it.
    WindowManager.closeWindow throws when the id is gone, so the server only closes its OWN registered window (getWindow(id) == ours).
    Back: the page rebuilds to the list first, then closes the window. Close (review finding 3): the page detaches its session, closes
    itself, then the server closes the window AT ONCE (no 1.5 s with a draggable chest panel and no page; the log says "Close button"
    instead of the Esc line). A second window probe replaces the first: new page + window first, then the old window closes (the
    SkyyVault askBuy order); the old window returns nothing while the new one shows the box.
  * A closed session lets go of its World / Store / PlayerRef / window / listener (review finding 4: SESS keeps the newest session per
    admin, and a kept World would keep an unloaded SkyyIslands instance alive) and leaves SESS on that admin's first client packet
    after the 5 s grace.
  * Client packets are watched with PacketAdapters.registerInbound(PlayerPacketWatcher) - registered once at the first window probe,
    removed at plugin shutdown, log only (netty thread: no inventory / component access), and silent unless that player has a probe
    window open (or closed less than 5 s ago): MoveItemStack, SmartMoveItemStack, DropItemStack, InventoryAction, CloseWindow,
    SendWindowAction, ClientOpenWindow, CustomPageEvent.
  * The window pages use the kit (page_shell decorated frame, label kinds, item_grid) + the same flat Back / Close footer as pages
    1-22; each says in ONE line what to look for and how to report it, then four numbered checks.

REVIEW FIXES (2026-10-02 review of 0.3, verdict PASS - same version, same 16 classes; every fix has harness checks that fail on the
first 0.3 build):
  1 (MEDIUM) the window re-send is gated by the packet watcher's stamp (above) - movement / knockback / teleports never re-send.
  2 (LOW)    leftovers stay in the box (above, the safe option); the test steps ask for bread or stone and 6+ free inventory slots.
  3 (LOW)    the Close button closes the window at once (above).
  4 (LOW)    a closed session lets go of its world refs and leaves SESS after the grace (above); closedAt is written before the volatile
             closed flag, so the netty thread's grace check never reads a stale 0.
  5 (LOW)    the checks name the items to use: "bread or stone (not an iron mace, helmet or shovel ...)" - the admin's own iron gear
             shares the probe item ids and is refused without a chat line.
  6 (INFO)   "Move seen, but the count changed" also names a bag sweep (the count compares with the previous move's count).
  7 (INFO)   P2 check 3 ends "No inventory showing? Say so." (no grid on the player's storage - scratch containers only).
  8 (INFO)   the note on both window pages says "if the buttons do nothing, press Esc" (a pending page acknowledgement drops clicks).
  9 (INFO)   no change: a profile switch inside the 1.5 s Esc gap cannot be reached by hand, and Close now closes at once.

COMMANDS (unchanged from 0.2 - no new command classes; ADMIN ONLY: requirePermission("skyyuiprobe.admin") AND setPermissionGroups(new
String[0]) on the command and its usage variant - ops pass through "*", plain hytale:Adventurer players are refused; lint rule
perm_group_leaks):
  /skyprobe  (alias /uiprobe)     -> the INDEX page (every probe page: number, name, what it proves, an Open button)
  /skyprobe <n>  or <name>        -> probe page n directly (1-24, or its stable name: base1, checkbox, ..., layout-right, win, secgrid)
  /skyprobe list                  -> the same list in chat, in the order to open them
Any other token count gets the engine's usage error.

PAGES (inline only, HANDOFF section 2): ONE CustomUIPage class (ProbePage) with a view number. Views 1-22 + the index switch with
rebuild() after a click (0.2); views 23 / 24 are opened as a NEW ProbePage through ProbeWin.open -> openCustomPageWithWindows (never a
page closed right before another opens, never a timer update; P2's one InventorySectionId update is sent once, right after the open,
by the page itself - ProbePage.sendSection, 0.3.1).
A window view without its open window (built any other way) shows the index with the line "Probe 23 needs its window ...".
LOGS (server log, INFO): 0.2's "opening probe <n> (<name>) for <player>" / "sent probe <n>"; window probes add the window id, the box
contents and the count at open, every client packet (above), every counted move, who closed the window and how long after the page,
and the return line ("returned N item(s) ...; counted X items before and X after - nothing created or lost").
No data files, no config kit rows, no bridge keys, no player switches, no event systems (one packet watcher, see above). Ready line:
  "[SkyyUiProbe] 0.3.1 ready - /skyprobe (admin): 24 probe pages (kit skyyui 1.4 <blob12>)".
BUILD CHECKS: everything 0.2 checks (SUI.verify, Probe.with_footer + check_page on pages 1-22, the index: check_page, assert_proven,
flat-only asserts, used_height / used_width budgets, text_width fits), plus for pages 23 / 24: check_page with every b.set target,
assert_proven with NOTHING allowed, used_height == the body, every text measured (the one line fits ONE line), item_grid_java_is_safe on
all Java, no .ui file in the jar; 0.3.1: the ACCESS AUDIT (every engine class / member the compiled bytecode references, with the JVM's
access rules - see WHY 0.3.1) and its self-test.
UNVERIFIED (needs the game - that is what the probes are for): (V5) the client draws a ContainerWindow next to a custom page; (V6) an
ItemGrid with InventorySectionId shows / drags a window's slots; whether the client closes the window itself on Esc; where the chest
panel sits; the vault arrow icons in an ItemGridSlot; that the client sends MoveItemStack (not something else) for the bound grid; that
the re-send after a refused move corrects the chest panel and the custom grid (SkyyVault 0.1.5's pattern for its chest); the return on a
DISCONNECT rests on the same engine path as vanilla's crafting windows (PlayerAddedSystem.onEntityRemove -> closeAllWindows -> onClose0);
the re-send timing in a live world (review fix 1: the decision logic is harness-checked with a recording stand-in World; that the
100 ms World.scheduleAfter lands after the packet's own world task rests on the bytecode - channelRead runs the inbound filters, then
the handler queues World.execute - and on SCHEDULED_EXECUTOR offering the task to the same world task queue 100 ms later; the log's
"N window re-send(s)" count shows it in game).
CHECKED in a bare JVM by the kept harness SkyyUiProbe/test_skyyuiprobe_0.3.1.py (see its header).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI

if "--deploy" in sys.argv:
    raise SystemExit("SkyyUiProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")
DUMP, DUMP_ONLY = None, False
for _flag in ("--dump", "--dump-only"):
    if _flag in sys.argv:
        i = sys.argv.index(_flag)
        if i + 1 >= len(sys.argv) or sys.argv[i + 1].startswith("--"):
            raise SystemExit("%s needs a file path" % _flag)
        if DUMP is not None:
            raise SystemExit("use --dump or --dump-only, not both")
        DUMP, DUMP_ONLY = sys.argv[i + 1], _flag == "--dump-only"

VERSION = "0.4"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()                       # every vanilla value the kit emits, proven against Assets.zip (read-only) - never caught
KIT_ID = SUI.kit_id()
assert SUI.KIT_VERSION == "1.4", "SkyyUiProbe 0.4 is made for kit 1.4 (Probe.summary, Probe.with_footer, PROBE_OPEN_FIRST)"
PREFIX = "SkyyPb"                  # the kit's default probe prefix; the index / footer / window page ids (SkyyPbIx..., SkyyPbNav...,
                                   # SkyyPbWin..., SkyyPbSg...) share it
PAGES = SUI.probe_pages(PREFIX)    # the kit pages 1-22, number order (0.2's pages, unchanged)
assert [p.n for p in PAGES] == list(range(1, 23)), "kit 1.4 builds probe pages 1-22"


class WinProbe(object):
    """A vault WINDOW probe (0.3): a page of this mod (not a kit page) opened with openCustomPageWithWindows."""

    def __init__(self, n, name, title, summary):
        self.n, self.name, self.key, self.title, self.summary = n, name, name, title, summary


WINP = [WinProbe(23, "win", "Probe 23 - window", "Chest window next to a custom page, plus a one-click arrow grid (vault idea)"),
        WinProbe(24, "secgrid", "Probe 24 - section grid", "Item grid bound to the window slots (InventorySectionId): show, drag, count")]
WIN_N = [w.n for w in WINP]
PROBES = list(PAGES) + list(WINP)
BY_N = dict((p.n, p) for p in PROBES)
BY_NAME = dict((p.name, p) for p in PROBES)
assert sorted(BY_N) == list(range(1, len(PROBES) + 1)) and len(BY_NAME) == len(PROBES), "probe numbers 1..n, names unique"
for p in PROBES:
    assert re.fullmatch(r"[a-z0-9-]+", p.name), "probe name %r (a command argument): a-z 0-9 -" % p.name
    assert len(p.summary) <= 95, "probe %d summary over 95 characters" % p.n

# the order to open them: the two window probes (new in 0.3), then SUI.PROBE_OPEN_FIRST (base1..base4), then the rest by number
NEW = [w.name for w in WINP]
FIRST = list(SUI.PROBE_OPEN_FIRST)
assert all(x in BY_NAME for x in FIRST), "PROBE_OPEN_FIRST names a page the kit does not build: %s" % FIRST
ORDER = [BY_NAME[x].n for x in NEW] + [p.n for p in sorted(PAGES, key=lambda p: (0, FIRST.index(p.name)) if p.name in FIRST
                                                             else (1, p.n))]
assert sorted(ORDER) == sorted(BY_N) and [BY_N[n].name for n in ORDER[:len(NEW) + len(FIRST)]] == NEW + FIRST

# ================= the old flat look (live SkyyBank 0.1.3 BankPage + SkyyCollections 0.2 CollPage, both seen in game) =================
FLAT = {
    "root": "#0b1524(0.96)", "stripe": "#ffd070", "title": "#ffe08a", "sub": "#cfe3ff", "caption": "#9fb8d0",
    "row": "#142030(0.92)", "name": "#e6f2ff", "num": "#ffe08a",
    "gBg": "#1f5a34", "gHov": "#2c7a48", "gPress": "#133a22", "gFg": "#e6ffe8",      # BankPage green (Deposit)
    "bBg": "#1d3a5f", "bHov": "#2f5a8f", "bPress": "#0f2038", "bFg": "#e6f2ff",      # BankPage blue (Withdraw)
    "nBg": "#2a3444", "nHov": "#3a475c", "nPress": "#1a2230", "nFg": "#e6f2ff",      # BankPage grey (Refresh / Close)
}
UI_DATA_COLORS = list(FLAT.values())    # the proven OLD look, used on purpose by the index and the probe footer only


def f_style(kind, fs):
    """BankPage.style(bg, hov, press, fg, fs) of SkyyBank 0.1.3, character for character."""
    bg, hov, press, fg = FLAT[kind + "Bg"], FLAT[kind + "Hov"], FLAT[kind + "Press"], FLAT[kind + "Fg"]
    ls = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)" % (fs, fg)
    return "Style: TextButtonStyle(Default: (Background: %s, %s), Hovered: (Background: %s, %s), Pressed: (Background: %s, %s));" % (
        bg, ls, hov, ls, press, ls)


def f_button(ident, text, w, h, kind, fs=18):
    SUI.check_text(text, "button text")
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (ident, w, h, text, f_style(kind, fs))


def f_label(ident, text, h, fs, col, bold=False, center=False, w=None):
    """A BankPage / CollPage label (lab()): Anchor (Width,) Height; Style FontSize (RenderBold) TextColor (HorizontalAlignment Center)
    VerticalAlignment Center. text must be proven inline text ("" for a b.set label)."""
    SUI.check_text(text, "label text")
    anc = ("Width: %d, " % w if w else "") + "Height: %d" % h
    return 'Label%s { Anchor: (%s); Text: "%s"; Style: (FontSize: %d%s, TextColor: %s%s, VerticalAlignment: Center); }' % (
        " #" + ident if ident else "", anc, text, fs, ", RenderBold: true" if bold else "", FLAT.get(col, col),
        ", HorizontalAlignment: Center" if center else "")


def f_spacer(w, h):
    return "Group { Anchor: (Width: %d, Height: %d); }" % (w, h)                   # CollPage sp(w, h)


def f_group(ident, layout, h, w=None, bg=None):
    """A plain Group row / column (BankPage / CollPage): Anchor (Width,) Height, an optional flat Background, LayoutMode Top / Left."""
    assert layout in ("Top", "Left"), "flat groups use the proven LayoutMode Top / Left only"
    anc = ("Width: %d, " % w if w else "") + "Height: %d" % h
    return "Group #%s { Anchor: (%s);%s LayoutMode: %s; }" % (ident, anc, " Background: %s;" % FLAT[bg] if bg else "", layout)


def f_text(ap, parent, ident, text, h, fs, col, bold=False, center=False, w=None):
    """A flat label with any text: proven text inline, anything else as an empty label + a b.set line (the #SkyyBCapMid pattern)."""
    if SUI.TEXT_OK.fullmatch(text) and not SUI.has_j(text):
        ap.append((parent, f_label(ident, text, h, fs, col, bold, center, w)))
    else:
        ap.append((parent, f_label(ident, "", h, fs, col, bold, center, w)))
        ap.sets.append((ident, "Text", text))


# ================= the index geometry (proven below with SUI.used_height / used_width / fit / text_width) =================
IX = PREFIX + "Ix"
IX_W, IX_H, IX_PADH, IX_PADV = 1600, 980, 20, 14         # 0.3: 980 high (was 960) for 2 x 12 entries; MAX_PAGE_H, flat root (no
                                                         # ornaments: the 980 ceiling keeps the kit's 18 px for them anyway)
IX_IN_W = IX_W - 2 * IX_PADH                    # 1560
COL_GAP = 16
COL_W = (IX_IN_W - COL_GAP) // 2                # 772: two columns of entries
PER_COL = (len(ORDER) + 1) // 2                 # 12 + 12
ENT_H, ENT_GAP, ENT_TOP = 56, 4, 2              # entry: 2 px, line one 30, line two 24 (0.2: 60 = 2 + 32 + 24 + 2)
L1_H, L2_H = 30, 24
EDGE, NUM_W, GAP_W, OPEN_W = 10, 46, 8, 130
NAME_W = COL_W - EDGE - NUM_W - GAP_W - OPEN_W - EDGE    # line one: 10 | number | name | 8 | Open | 10
WHAT_X = EDGE + NUM_W                                    # line two: the summary starts under the name
WHAT_W = COL_W - WHAT_X - GAP_W
WHAT_FS, NAME_FS, NUM_FS = 15, 18, 20
FIT_MARGIN = 8                                   # px kept free after the widest text (the client's glyph advances vary a little)


def summary(pg):
    """The one-line purpose of a probe page: the kit's Probe.summary (a window probe: its own). Kit 1.4 cuts a PROBE_SUMMARY line longer
    than 95 characters to 92 + "..." (base2); when the kit's whole line still fits the index row, that whole line is shown instead."""
    s = pg.summary
    full = SUI.PROBE_SUMMARY.get(pg.name, "")
    if s.endswith("...") and full.startswith(s[:-3]) and SUI.text_width(full, WHAT_FS) <= WHAT_W - FIT_MARGIN:
        return full
    return s


WHAT = dict((p.n, summary(p)) for p in PROBES)
for p in PAGES:
    if WHAT[p.n] != p.summary:
        print("note: probe %d (%s): the index shows the kit's whole PROBE_SUMMARY line (Probe.summary is cut at 95 characters)"
              % (p.n, p.name))


# ================= the kit probe pages + their flat footer (the kit's public footer hook) =================
FOOT_H = 56                      # BankPage bottom row: Group Height 56, LayoutMode Left, Padding Top 8; 46 px buttons
FOOT_SLACK = 4                   # px kept free under the footer's container end (0.1 review: a clipped footer would still leave
                                 # Esc, but Back / Close must stay whole)
FOOT_W = 240 + 16 + 170
NAV, NAV_BACK, NAV_CLOSE = PREFIX + "Nav", PREFIX + "NavBack", PREFIX + "NavClose"


def footer(container):
    return [(container, "Group #%s { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 8); }" % (NAV, FOOT_H)),
            (NAV, f_button(NAV_BACK, "Back to the list", 240, 46, "b")),
            (NAV, f_spacer(16, 46)),
            (NAV, f_button(NAV_CLOSE, "Close", 170, 46, "n"))]


def probe_view(pg):
    """(appends with the footer, sets, java statements, how the footer was placed, page height, extra Java lines) for one page:
    SUI.probe_page(name) (the kit's lookup by stable name - what /skyprobe <name> means) + Probe.with_footer."""
    kp = SUI.probe_page(pg.name, PREFIX)
    assert kp.n == pg.n and kp.key == pg.key and kp.name == pg.name, "probe_page(%r) is not probe %d" % (pg.name, pg.n)
    view = kp.with_footer(footer, FOOT_H, foot_w=FOOT_W, slack=FOOT_SLACK, prefix=PREFIX)
    ap = view.appends
    assert all(isinstance(mk, str) and not isinstance(mk, SUI.Choice) for _p, mk in ap), "probe %d: a runtime choice" % pg.n
    assert [x for x in ap[-4:]] == footer(view.container), "probe %d: the footer is the last 4 appends" % pg.n
    assert view.h <= SUI.MAX_PAGE_H, "probe %d: %d px high" % (pg.n, view.h)
    java = view.java("b")
    kit_java, shell_java = kp.java("b"), kp.shell.java("b")
    assert kit_java.startswith(shell_java), "probe %d: Probe.java must start with the shell's Java" % pg.n
    extra = [l for l in kit_java[len(shell_java):].strip("\n").splitlines() if l.strip()]
    # nothing of the kit markup changed except the root height line and the footer lines
    mine = [l for l in java.splitlines() if not (NAV in l and "appendInline" in l)]
    kit_lines = kit_java.splitlines()
    assert len(java.splitlines()) - len(mine) == 4, "probe %d: exactly 4 footer appends" % pg.n
    assert len(mine) == len(kit_lines) and mine[1:] == kit_lines[1:] and "appendInline((String) null" in mine[0], \
        "probe %d: the page Java differs from the kit's in more than the root height + footer" % pg.n
    assert SUI.item_grid_java_is_safe(java), "probe %d fills a grid slot with a held stack" % pg.n
    return ap, list(view.sets), java, view.how, view.h, extra


def flex_kids(ap):
    """The FlexWeight children of the footer's container (not the footer itself): SUI.used_height counts them as 0 px."""
    cont = ap[-4][0]
    return [m for p, m in ap[:-4] if p == cont and "FlexWeight" in SUI.render(m)]


VIEWS = {}
for pg in PAGES:
    VIEWS[pg.n] = probe_view(pg)
    how = VIEWS[pg.n][3]
    if flex_kids(VIEWS[pg.n][0]):
        # base2: the body is one FlexWeight column + the footer - the kit's slack figure counts that column as 0 px (0.2 review)
        how += " (slack NOT meaningful: the body holds a FlexWeight child, counted as 0 px; if the page shows only the footer, " \
               "FlexWeight failed)"
    print("probe %2d %-16s key %-16s footer: %s" % (pg.n, pg.name, pg.key, how))
FLEX_VIEWS = [n for n in sorted(VIEWS) if flex_kids(VIEWS[n][0])]
assert FLEX_VIEWS == [BY_NAME["base2"].n], "only base2 has a FlexWeight child next to the footer (the header's base2 note): %s" % (
    FLEX_VIEWS,)

# ================= 0.3: the two vault WINDOW probe pages (kit look; markup = proven properties only) =================
WIN_PAGE_W = 800
WP_ARROWS = PREFIX + "WinArrows"                        # P1: the 3-slot arrow grid (SlotClicking)
WP_GRID = PREFIX + "SgGrid"                             # P2: the 9-slot grid bound to the window's section (InventorySectionId)
PROBE_ITEMS = ["Weapon_Mace_Iron", "Armor_Iron_Head", "Tool_Shovel_Iron"]   # the 3 LOCKED probe items (MaxStack 1: weapon / armor /
                                                                            # tool - Item.processConfig), slots 0-2 of the box
BOX_SLOTS = 9
ARROW_IDS_VAULT = ["Skyy_Vault_Prev", "Skyy_Vault_Info", "Skyy_Vault_Next"]  # SkyyVault's own items (its asset pack), when loaded
ARROW_IDS_VANILLA = ["Weapon_Arrow_Crude", "Ingredient_Bar_Iron", "Weapon_Arrow_Iron"]   # stand-ins when SkyyVault is not loaded
ARROW_NAMES = ["Previous page", "Page 1 of 3", "Next page"]
ARROW_DESC = "Probe arrow: one click prints one chat line, and nothing sticks to your cursor."
LATE_CLOSE_MS = 1500                                    # Esc: the server closes a window the client left open after this long
NET_GRACE_MS = 5000                                     # client packets are still logged this long after the window closed
SYNC_DELAY_MS = 100                                     # review fix 1: the re-send runs this long after the stamp (behind the
                                                        # packet's own handler, which the netty thread queues right after the stamp)
SAW_MS = 1500                                           # a watcher stamp older than this is dropped (never re-sent for)
SYNC_RATE_MS = 250                                      # fallback without the packet watcher: at most one re-send per this long
assert 0 < SYNC_DELAY_MS < SAW_MS and SYNC_RATE_MS > 0
WIN_TEXT = {
    23: {"one": "Look for a chest panel with 3 iron items and your inventory. Tell Claude 1-4 + a screenshot.",
         "checks": ["1. Do you see the 9-slot chest panel with the 3 iron items, and your own inventory?",
                    "2. Drag bread or stone (not an iron mace, helmet or shovel - those 3 are locked) into a free slot of "
                    "that panel and back out: does it move?",
                    "3. Where does the panel sit: left, right, below, above or on top of this page?",
                    "4. Click each arrow below once: one chat line per click, and nothing sticks to your cursor?"],
         "head": "Vault arrow test - click each one once:"},
    24: {"one": "The 9 slots below should copy the chest panel (3 iron items). Tell Claude 1-4 + a screenshot.",
         "checks": ["1. Do the 9 slots below show the 3 iron items (the same as the chest panel, if one shows)?",
                    "2. Drag an iron item inside the 9 slots: it must snap back (the probe items are locked).",
                    "3. Drag bread or stone (not an iron mace, helmet or shovel) into the 9 slots, on to another slot, then "
                    "back: does each move stick? No inventory showing? Say so.",
                    "4. After each move, does chat say Move seen, with the same count before and after?"],
         "head": "The window's 9 slots, drawn by this page:"},
}
# review fix 5: the check that asks for the admin's OWN item names what to use - their own iron mace / helmet / shovel share the probe
# item ids and are refused with no chat line (a refused drag must not read as "the grid does not work"); fix 7: P2 asks to say so when
# no inventory shows (P2 binds only the window section)
for _n, _c in ((23, 1), (24, 2)):
    assert "bread or stone (not an iron mace, helmet or shovel" in WIN_TEXT[_n]["checks"][_c], "window probe %d: fix 5 text" % _n
assert WIN_TEXT[24]["checks"][2].endswith("No inventory showing? Say so."), "window probe 24: fix 7 text"
WIN_NOTE = "Esc, Close or Back ends the probe; if the buttons do nothing, press Esc. Your items go back to your inventory."
assert "if the buttons do nothing, press Esc" in WIN_NOTE        # review fix 8: a pending page acknowledgement drops button clicks
LINE_PX = 21                                            # a 16 px line (the kit's look-list figure); + 4 px per label


def text_h(text, w, size=16, bold=False):
    """Height of a wrapped default label holding `text` in w px (the kit's look-list rule: 21 px per line + 4)."""
    return SUI.text_lines(text, w - 4, size, bold=bold) * LINE_PX + 4


def win_page(wp, page_h=None):
    """(shell, appends + b.set lines, extra Java lines, body height used) of window probe page wp at page height page_h (None = a tall
    first pass; the caller rebuilds it at the exact height)."""
    n = wp.n
    P = PREFIX + ("Win" if n == 23 else "Sg")
    sh = SUI.page_shell(P, WIN_PAGE_W, page_h or SUI.MAX_PAGE_H, wp.title, kind="decorated")
    ap = sh.appends
    body, w = sh.body, sh.inner_w
    tx = WIN_TEXT[n]
    # the ONE line: what to look for + how to report it (it must fit one line - asserted below)
    ap.text(body, P + "One", tx["one"], "strong", h=26, w=w)
    ap.append((body, SUI.spacer(h=6)))
    for i, t in enumerate(tx["checks"]):
        ap.text(body, P + "C" + str(i + 1), t, "default", h=text_h(t, w), w=w, wrap=True)
    ap.append((body, SUI.spacer(h=10)))
    ap.text(body, P + "Hd", tx["head"], "bold", h=26, w=w)
    extra = []
    if n == 23:
        ap.append((body, SUI.item_grid(WP_ARROWS, len(ARROW_IDS_VAULT), 1, drag=False, tooltips=False)))
        extra = [
            "java.util.ArrayList pbArrowSlots = new java.util.ArrayList();",
            "String[] pbAid = @PKG@.ProbeViews.arrowIds();",
            "String[] pbAnm = @PKG@.ProbeViews.arrowNames();",
            "for (int i = 0; i < pbAid.length; i++) {",
            "  @IGS@ pbG = new @IGS@(new @IS@(pbAid[i], 1));",
            "  pbG.setName(pbAnm[i]);",
            "  pbG.setDescription(%s);" % SUI.java_lit(ARROW_DESC),
            "  pbG.setActivatable(true);",
            "  pbArrowSlots.add(pbG);",
            "}",
            'b.set("#%s.Slots", pbArrowSlots);' % WP_ARROWS,
        ]
    else:
        ap.append((body, SUI.item_grid(WP_GRID, BOX_SLOTS, 1, drag=True, tooltips=False)))
    ap.append((body, SUI.spacer(h=10)))
    ap.text(body, P + "Note", WIN_NOTE, "caption", h=22, w=w)
    ap.extend(footer(body))
    used = SUI.used_height(ap, body)
    return sh, ap, extra, used


WVIEWS = {}
for wp in WINP:
    _sh, _ap, _extra, _used = win_page(wp)
    _h = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + _used + FOOT_SLACK
    sh, ap, extra, used = win_page(wp, _h)
    assert used == _used and sh.h == _h <= SUI.MAX_PAGE_H, "window probe %d: the height pass changed the body" % wp.n
    left = SUI.fit([used], sh.inner_h, "window probe %d body" % wp.n)
    assert left == FOOT_SLACK, "window probe %d: %d px left under the footer" % (wp.n, left)
    chk = SUI.Appends(ap)
    chk.sets = list(ap.sets) + list(sh.sets)
    SUI.check_page(chk, PREFIX)                       # markup rules, parents, no duplicate id, every b.set target exists
    SUI.assert_page_size(sh.w, sh.h)
    toks = SUI.assert_proven(chk, allow=(), what="window probe %d" % wp.n)    # proven properties only (InventorySectionId is a b.set
    assert all(g is None for g in toks.values()), "window probe %d: an unproven token %s" % (wp.n, toks)   # after the open, not markup)
    assert [x for x in ap[-4:]] == footer(sh.body), "window probe %d: the footer is the last 4 appends" % wp.n
    for _p, mk in ap:
        assert "InventorySectionId" not in mk, "window probe %d: InventorySectionId is set after the open, never inline" % wp.n
    tx = WIN_TEXT[wp.n]
    SUI.fit([SUI.text_width(tx["one"], 16, bold=True), FIT_MARGIN], sh.inner_w, "window probe %d one line" % wp.n)
    for t in [tx["head"]]:
        SUI.fit([SUI.text_width(t, 16, bold=True), FIT_MARGIN], sh.inner_w, "window probe %d heading" % wp.n)
    SUI.fit([SUI.text_width(WIN_NOTE, SUI.fs(12)), FIT_MARGIN], sh.inner_w, "window probe %d note" % wp.n)   # caption = fs(12)
    for t in tx["checks"]:
        assert SUI.text_lines(t, sh.inner_w - 4, 16) <= 2, "window probe %d: a check line takes 3+ lines: %r" % (wp.n, t)
    java = (sh.appends.java("b", sets=list(sh.sets)) + ("\n" + "\n".join(extra) if extra else ""))
    assert SUI.item_grid_java_is_safe(java.replace("@IGS@", SUI.GRID_SLOT_CLASS).replace("@IS@", SUI.ITEM_STACK_CLASS)), \
        "window probe %d fills a grid slot with a held stack" % wp.n
    WVIEWS[wp.n] = (ap, list(ap.sets) + list(sh.sets), java, "body end, page %d px high, %d px slack" % (sh.h, left), sh.h, extra)
    print("probe %2d %-16s key %-16s footer: %s (window probe, %d appends, %d b.set lines)" % (
        wp.n, wp.name, wp.key, WVIEWS[wp.n][3], len(ap), len(WVIEWS[wp.n][1])))
assert SUI.item_grid(WP_GRID, BOX_SLOTS, 1, drag=True, tooltips=False).count("AreItemsDraggable: true") == 1
assert SUI.item_grid(WP_ARROWS, 3, 1, drag=False, tooltips=False).count("AreItemsDraggable: false; InfoDisplay: None;") == 1
assert len(PROBE_ITEMS) == 3 and len(set(PROBE_ITEMS)) == 3 and BOX_SLOTS - len(PROBE_ITEMS) == 6
assert len(ARROW_IDS_VAULT) == len(ARROW_IDS_VANILLA) == len(ARROW_NAMES) == 3

# ================= the index (flat, proven markup only) =================
FIRST_LINE = "New in 0.3: open %s (23), then %s (24) - the vault window probes. Pages 1-22 are the 0.2 kit probes. Back returns " \
             "here, Esc or Close leaves." % (NEW[0], NEW[1])
FIRST_TXT = "Nothing opened yet - start with %s, then %s (probes %s)." % (
    NEW[0], NEW[1], ", ".join(str(BY_NAME[x].n) for x in NEW))
TITLE = "SkyyUiProbe - kit and window probe pages"
SUB2 = "A disconnect right after you click Open means that page failed - note its number (the server log names it too)."
HEADS = ("Start here - the two window probes first (green Open)", "Then continue here, top to bottom")
KIT_LINE = "Kit %s  |  %d pages  |  chat: /skyprobe list, /skyprobe number or name" % (KIT_ID, len(PROBES))
KIT_W = IX_IN_W - 16 - 170                      # the bottom row: kit line | 16 | Close 170
TITLE_FS, SUB_FS, HEAD_FS, INFO_FS, KIT_FS = 30, 16, 17, 17, 15


def last_text(n):
    """What ProbePage.lastText(n) returns (the Java below builds the same string; the harness compares them)."""
    if n not in BY_N:
        return FIRST_TXT
    nx = ORDER[ORDER.index(n) + 1] if ORDER.index(n) + 1 < len(ORDER) else -1
    return "Last opened: probe %d (%s). Did it look right? " % (n, BY_N[n].name) + (
        "Next: probe %d (%s)." % (nx, BY_N[nx].name) if nx > 0 else "That was the last one.")


def fail_text(n):
    """The Info text after probe n could not be built (ProbePage.handleDataEvent's catch)."""
    return "Probe %d could not be built - see the server log." % n


def nowin_text(n):
    """The Info text when a window probe view is built without its open window (ProbePage.build)."""
    return "Probe %d needs its window - open it with its Open button or /skyprobe %s." % (n, BY_N[n].name)


def entry(ap, col, n, kind):
    """One index entry in column col: line one = number, name, Open; line two = the summary (a b.set label: it has punctuation)."""
    pg = BY_N[n]
    row, top, low = IX + "Row" + str(n), IX + "Top" + str(n), IX + "Low" + str(n)
    ap.append((col, f_group(row, "Top", ENT_H, bg="row")))
    ap.append((row, f_spacer(EDGE, ENT_TOP)))
    ap.append((row, f_group(top, "Left", L1_H)))
    ap.append((top, f_spacer(EDGE, L1_H)))
    ap.append((top, f_label(IX + "Num" + str(n), str(n), L1_H, NUM_FS, "num", bold=True, center=True, w=NUM_W)))
    ap.append((top, f_label(IX + "Name" + str(n), pg.name, L1_H, NAME_FS, "name", bold=True, w=NAME_W)))
    ap.append((top, f_spacer(GAP_W, L1_H)))
    ap.append((top, f_button(IX + "Open" + str(n), "Open", OPEN_W, L1_H, kind)))
    ap.append((row, f_group(low, "Left", L2_H)))
    ap.append((low, f_spacer(WHAT_X, L2_H)))
    f_text(ap, low, IX + "What" + str(n), WHAT[n], L2_H, WHAT_FS, "sub", w=WHAT_W)
    return row, top, low


def build_index():
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; Padding: (Horizontal: %d, Vertical: %d); LayoutMode: Top; }"
               % (IX, IX_W, IX_H, FLAT["root"], IX_PADH, IX_PADV)))
    ap.append((IX, "Group { Anchor: (Height: 3); Background: %s; }" % FLAT["stripe"]))
    ap.append((IX, f_label(None, TITLE, 44, TITLE_FS, "title", bold=True, center=True)))
    f_text(ap, IX, IX + "Sub1", FIRST_LINE, 26, SUB_FS, "sub", center=True)
    f_text(ap, IX, IX + "Sub2", SUB2, 26, SUB_FS, "sub", center=True)
    ap.append((IX, f_spacer(10, 8)))
    cols_h = 28 + 4 + PER_COL * ENT_H + (PER_COL - 1) * ENT_GAP
    ap.append((IX, f_group(IX + "Cols", "Left", cols_h)))
    rows = []
    for ci, chunk in enumerate((ORDER[:PER_COL], ORDER[PER_COL:])):
        col = IX + "Col" + "AB"[ci]
        if ci:
            ap.append((IX + "Cols", f_spacer(COL_GAP, cols_h)))
        ap.append((IX + "Cols", f_group(col, "Top", cols_h, w=COL_W)))
        f_text(ap, col, IX + "Head" + "AB"[ci], HEADS[ci], 28, HEAD_FS, "caption", bold=True)
        ap.append((col, f_spacer(10, 4)))
        for j, n in enumerate(chunk):
            if j:
                ap.append((col, f_spacer(10, ENT_GAP)))
            rows.append(entry(ap, col, n, "g" if BY_N[n].name in NEW else "b"))
    ap.append((IX, f_spacer(10, 8)))
    ap.append((IX, f_label(IX + "Info", "", 28, INFO_FS, "title", bold=True, center=True)))  # b.set from ProbePage.info at runtime
    ap.append((IX, "Group #%sBottom { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }" % IX))
    f_text(ap, IX + "Bottom", IX + "Kit", KIT_LINE, 46, KIT_FS, "caption", w=KIT_W)
    ap.append((IX + "Bottom", f_spacer(16, 46)))
    ap.append((IX + "Bottom", f_button(IX + "Close", "Close", 170, 46, "n")))
    return ap, rows, cols_h


IXA, IX_ROWS, COLS_H = build_index()
INFO_SET = (IX + "Info", "Text", SUI.J("info", "Nothing opened yet"))     # the runtime line under the columns (ProbePage.info)
_ixchk = SUI.Appends(IXA)
_ixchk.sets.append(INFO_SET)
SUI.check_page(_ixchk, PREFIX)          # markup rules, every parent exists, no duplicate id, every b.set target exists
SUI.assert_page_size(IX_W, IX_H)
IX_USED = SUI.used_height(IXA, IX)
IX_FREE = SUI.fit([IX_USED], IX_H - 2 * IX_PADV, "index body")
SUI.fit([SUI.used_width(IXA, IX + "Cols")], IX_IN_W, "index columns")
SUI.fit([SUI.used_width(IXA, IX + "Bottom")], IX_IN_W, "index bottom row")
for _c in ("A", "B"):
    SUI.fit([SUI.used_height(IXA, IX + "Col" + _c)], COLS_H, "index column " + _c)
for _row, _top, _low in IX_ROWS:
    SUI.fit([SUI.used_height(IXA, _row)], ENT_H, "index entry " + _row)
    SUI.fit([SUI.used_width(IXA, _top)], COL_W, "index entry line one " + _top)
    SUI.fit([SUI.used_width(IXA, _low)], COL_W, "index entry line two " + _low)
assert len(IX_ROWS) == len(PROBES) == 24 and PER_COL == 12 and len(ORDER) - PER_COL == 12, "24 entries in two columns of 12"
# every text fits its label (the client's font tables, SUI.text_width)
for n in ORDER:
    SUI.fit([SUI.text_width(WHAT[n], WHAT_FS), FIT_MARGIN], WHAT_W, "probe %d summary line" % n)
    SUI.fit([SUI.text_width(BY_N[n].name, NAME_FS, bold=True), FIT_MARGIN], NAME_W, "probe %d name" % n)
IX_TEXTS = [(TITLE, TITLE_FS, True, IX_IN_W), (FIRST_LINE, SUB_FS, False, IX_IN_W), (SUB2, SUB_FS, False, IX_IN_W),
            (HEADS[0], HEAD_FS, True, COL_W), (HEADS[1], HEAD_FS, True, COL_W), (KIT_LINE, KIT_FS, False, KIT_W),
            (FIRST_TXT, INFO_FS, True, IX_IN_W)]
IX_TEXTS += [(last_text(n), INFO_FS, True, IX_IN_W) for n in ORDER] + [(fail_text(n), INFO_FS, True, IX_IN_W) for n in ORDER]
IX_TEXTS += [(nowin_text(n), INFO_FS, True, IX_IN_W) for n in WIN_N]
IX_WIDEST = {}
for _t, _fs, _b, _w in IX_TEXTS:
    _tw = SUI.text_width(_t, _fs, bold=_b)
    SUI.fit([_tw, FIT_MARGIN], _w, "index text %r" % _t[:40])
    if _tw > IX_WIDEST.get(_w, (0, ""))[0]:
        IX_WIDEST[_w] = (_tw, _t)
print("index texts: %d measured, widest per label width: %s" % (len(IX_TEXTS), ", ".join(
    "%.0f / %d px" % (IX_WIDEST[w][0], w) for w in sorted(IX_WIDEST))))
# flat only: the proven table (independent of PROBED: the index never uses a base / trial property, even after it is probed)
IX_TOKENS = SUI.assert_proven(IXA, what="SkyyUiProbe index")
for _p, mk in IXA:
    for bad in ("Common/", "Sounds/", "FontName", "LetterSpacing", "FlexWeight", "Wrap", "TexturePath", "Disabled", "Visible"):
        assert bad not in mk, "index: flat only (%s): %s" % (bad, mk[:100])
    for lm in re.findall(r"LayoutMode:\s*([A-Za-z]+)", mk):
        assert lm in ("Top", "Left"), "index: LayoutMode Top / Left only, not %s" % lm
    assert not re.search(r"Anchor: \([^)]*\b(Top|Bottom|Left|Right|Horizontal|Vertical|Full):", SUI.render(mk)), \
        "index: no Anchor margins (only Width / Height, like the proven flat pages): %s" % mk[:100]
    assert re.match(r"(Group|Label|TextButton)\b", mk), "index: Group / Label / TextButton only: %s" % mk[:60]
for _i, _pr, _v in IXA.sets:
    # < and > are proven only as INLINE text ("< Back"), not through b.set (review 2026-09-29): keep them out of b.set texts
    assert not (isinstance(_v, str) and re.search(r"[<>]", SUI.render(_v))), "index b.set text with < or >: %r" % _v
for _t in [FIRST_TXT] + [last_text(n) for n in ORDER] + [fail_text(n) for n in ORDER] + [nowin_text(n) for n in WIN_N]:
    assert not re.search(r"[<>]", _t), "runtime Info text (b.set) with < or >: %r" % _t
for _n in WIN_N:
    for _i, _pr, _v in WVIEWS[_n][1]:
        assert not (isinstance(_v, str) and re.search(r"[<>]", SUI.render(_v))), "window probe b.set text with < or >: %r" % _v
IX_JAVA = IXA.java("b") + "\n" + SUI.java_set(*INFO_SET)
IX_BINDS = [("#" + IX + "Open" + str(n), "open:" + str(n)) for n in ORDER] + [("#" + IX + "Close", "close")]
IX_BIND = ["ev.addEventBinding(@BT@.Activating, %s, @EVD@.of(\"a\", %s));" % (SUI.java_lit(sel), SUI.java_lit(act))
           for sel, act in IX_BINDS]
print("index: %d appends, %d b.set lines, %d / %d px high (%d free), two columns %s | %s" % (
    len(IXA), len(IXA.sets) + 1, IX_USED, IX_H - 2 * IX_PADV, IX_FREE, ORDER[:PER_COL], ORDER[PER_COL:]))

# ================= 0.4: the MINIMAP probes (HUD probes started by /skyprobe map <step>; research/Minimap-Research.md section 9) =================
import math
MAP_KEY = "SkyyUiProbeMap"          # CustomUIHud key = the HudManager map key = the CustomHud packet's hudId
SKYYHUD_KEY = "skyyhud_main"        # SkyyHud/build_skyyhud_0.3.13.py HudMain: super(pr, "skyyhud_main") - this mod never sends that key
MAP_Z = 5                           # zOrder of the probe HUD (SkyyHud: 0) - UNVERIFIED which way the client stacks them
assert MAP_KEY != SKYYHUD_KEY and re.fullmatch(r"[A-Za-z]+", MAP_KEY), "the probe HUD has its OWN key (letters only)"
MP = PREFIX + "Map"
MID = {"root": MP + "Root", "box": MP + "Box", "pic": MP + "Pic", "cap": MP + "Cap", "capbox": MP + "CapBox", "clip": MP + "Clip",
       "back": MP + "Back", "grid": MP + "Grid", "ring": MP + "Ring", "me": MP + "Me", "tile": MP + "T"}
for _v in MID.values():
    SUI.check_id(_v, PREFIX)
TICK_MS = 250                       # the map tick: at most 4 pans a second
TILE_PX = 32                        # display px per 32-block chunk tile (1 px per block)
GRID_N, GRID_HALF = 9, 4            # the 9 x 9 window of tiles around the player's chunk
SPAN = GRID_N + 2 * GRID_HALF       # 17 tile positions per side in the grid Group: the window re-bases when it would leave them
CLIP_D, RING_D, ARROW_S = 160, 168, 24
BOX_TOP, BOX_RIGHT = 20, 20         # top-right corner (Skyy 2026-10-03: round, top-right, ~160 px)
P2_BOX_W = 260                      # the caption under the map needs the room (the map itself sits at the right)
RING_L, RING_T = P2_BOX_W - RING_D, 0
CLIP_L, CLIP_T = RING_L + (RING_D - CLIP_D) // 2, RING_T + (RING_D - CLIP_D) // 2
ME_L, ME_T = CLIP_L + (CLIP_D - ARROW_S) // 2, CLIP_T + (CLIP_D - ARROW_S) // 2
CAP_LINE_H = 22
CAP_T, CAP_H = RING_D + 4, CAP_LINE_H + 6
P2_BOX_H = CAP_T + CAP_H
P1_PIC = 128
P1_BOX_W = P1_PIC + 40              # the kit's hud panel pads 20 / 10 (Hud/TimeLeft)
P1_BOX_H = 10 + P1_PIC + 4 + CAP_LINE_H + 10
TAP_MS = 60000                      # P4 / each P5 segment
P5_SEGMENTS = 3
QMAX = 20000                        # packets the tap keeps per player between two ticks; more = counted as dropped (never blocks)
P3_TTL_MS = 600000                  # P3 stays armed this long (or until off)
READY_DELAY_MS = 1500               # SkyyHud attaches 1.5 s after PlayerReadyEvent - so does P3's re-show
ENC_PER_TICK, ENC_FIRST = 40, 120   # new tile PNGs encoded per tick at most (the first P2 build may take 120)
PART = 2621440                      # CommonAssetModule.sendAsset: ArrayUtil.split(blob, 2621440)
ASSET_DIR = "UI/SkyyUiProbe/"       # an AssetImage AssetPath is the full common asset name (Cartographer / FastMiniMap / DapperMap)
MASK_DIR, MASK_PREFIX = "UI/Custom/", "SkyyUiProbeMask-"   # a MaskTexturePath resolves under UI/Custom/ (Cartographer's mask)
assert GRID_HALF * TILE_PX - TILE_PX // 2 >= CLIP_D // 2, "the 9 x 9 window covers the round map wherever the player stands"
assert SPAN * TILE_PX == 544 and TILE_PX % 16 == 0
# tokens no kit / proven-table entry covers: what the map probes are FOR (they stay behind /skyprobe map, op only, off by default)
MAP_TRIAL = {"element AssetImage": "P1 / P2 / P3: a runtime picture (vanilla Memory.ui uses AssetImage with a runtime path)",
             "AssetPath": "P1 / P2 / P3: the picture's common asset name",
             "MaskTexturePath": "P2: the round mask - kit key text-mask (a TextGradient label mask, seen 2026-09-30); a runtime PNG on a "
                                "Group is UNVERIFIED"}
MAP_STEPS = ["p1a", "p1b", "p2", "p2sharp", "p3", "p3resend", "p4", "p5", "off", "status"]
MAP_USAGE = "Use: /skyprobe map " + " | ".join(MAP_STEPS)
MAP_LINES = [   # the ONE chat line each step prints at once (status: the line comes from the server tick)
    "P1a: a small box top-right shows ONE picture the server made (no asset rebuild). Picture, blank box or a hitch? SkyyHud widgets "
    "still there?",
    "P1b: the box shows a NEW picture + ONE asset rebuild. Picture there? Any hitch or flicker when it came in?",
    "P2: a round minimap top-right (north up, white arrow = you). Walk and sprint: smooth? blurry? a clean round edge? Sources are "
    "under it.",
    "P2 sharp: the same minimap, tiles enlarged on the server. Sharper than p2? Just as smooth?",
    "P3 armed: now change world (/hub, /island) or reconnect - the box comes back WITHOUT its picture being sent again. Is the picture "
    "there?",
    "P3 re-send armed: after your next world change or reconnect the picture is sent again first. Is it there?",
    "P4: counting the map packets the server sends you for 60 s - walk onto new ground. The result comes in chat.",
    "P5: counting the map stream here and in the next 2 worlds you enter (60 s each) - go to an island, then Zone 1. Results come in "
    "chat.",
    "Map probes off: probe box gone, counting stopped, P3 disarmed. Your SkyyHud widgets should look as before.",
    ""]
MAP_HELP = [
    "Map probes (op only; each is OFF until you start it and prints what to look at): " + MAP_USAGE[5:],
    "p1a / p1b - one server-made picture in a HUD box, without / with one asset rebuild",
    "p2 / p2sharp - the round 160 px minimap (real map tiles, else the shared cache, else a test pattern) / tiles enlarged on the server",
    "p3 / p3resend - after your next world change or reconnect: does the picture still show without / with sending it again?",
    "p4 - 60 s count of the map packets you get (run it with BetterMap on, then off) / p5 - the same per world for 3 worlds",
    "off - everything off, the probe box removed / status - what runs, pictures sent, counts so far"]
assert len(MAP_LINES) == len(MAP_STEPS) and MAP_LINES[-1] == "" and all(MAP_LINES[:-1])
MAP_CAPS = {"p1a": "P1a - no rebuild", "p1b": "P1b - one rebuild", "p3": "P3 - armed", "p3re": "P3 - re-sent",
            "p3no": "P3 - not re-sent"}
P2_CAP_SAMPLES = ["P2 - map 81 cache 81 test 81", "P2 sharp - map 81 cache 81 test 81"]   # the widest the tick writes (MapProbe.capText)


def rgba_int(name, alpha=None):
    """A kit colour (skyyui.COLOR) as the MapImage palette int 0xRRGGBBAA (signed 32 bit), optionally with another alpha."""
    c = SUI.norm_color(SUI.COLOR[name])
    m = re.fullmatch(r"#([0-9a-f]{6})(?:\(([0-9.]+)\))?", c)
    assert m, "kit colour %s = %r" % (name, c)
    a = alpha if alpha is not None else (int(round(float(m.group(2)) * 255)) if m.group(2) else 255)
    v = (int(m.group(1), 16) << 8) | a
    return v - (1 << 32) if v >= (1 << 31) else v


# every picture this mod makes: built from kit colours, then sent AS a MapImage through the same encoder as a real map tile
PAL_MASK = [0, rgba_int("white")]                                                        # transparent / the opaque disc
PAL_RING = [0, rgba_int("darkBlock", 170), rgba_int("title"), rgba_int("gold")]          # clear / dark edge / light ring / north tick
PAL_ARROW = [0, rgba_int("darkBlock", 230), rgba_int("white")]                           # clear / outline / the arrow
PAL_TEST = [[rgba_int("progressGreen"), rgba_int("separator"), rgba_int("title")],
            [rgba_int("progressBlue"), rgba_int("separator"), rgba_int("title")]]       # by chunk parity: base / border / diagonal
PIC_SETS = [("info", "accent", "progressBlue", "value"), ("progressGreen", "success", "value", "progressFill"),
            ("progressFill", "warning", "error", "value")]                              # p1a / p1b / p3: four quadrants each
PAL_PIC = [[rgba_int(a), rgba_int(b), rgba_int(c), rgba_int(d), rgba_int("separator"), rgba_int("white"), rgba_int("gold")]
           for a, b, c, d in PIC_SETS]
assert len(set(tuple(p) for p in PAL_PIC)) == 3, "each P1 / P3 picture has its own colours (a NEW asset each)"
RING_IN = CLIP_D // 2 - 1           # the ring: dark 79-80.5 px, light 80.5-82.5, dark 82.5-84 (in half pixels below)
RING_BANDS = [(2 * RING_IN) ** 2, (2 * RING_IN + 3) ** 2, (2 * RING_IN + 7) ** 2, RING_D ** 2]
assert RING_BANDS[-1] == (2 * (RING_IN + 5)) ** 2, "the ring's outer edge is the picture's edge"
NORTH_TICK = 11                     # the gold north tick: rows 0..10 at the ring's top
# the centre arrow: 8 headings (0 N, 1 NE, 2 E, 3 SE, 4 S, 5 SW, 6 W, 7 NW) as integer polygons on the doubled 48 x 48 grid of a 24 px
# picture (tip, right foot, notch, left foot); NE = N turned 45 degrees (rounded here, at build time), the rest = exact 90 degree turns
_ARROW_N = [(24, 4), (38, 42), (24, 32), (10, 42)]


def _rot45(p):
    dx, dy = p[0] - 24, p[1] - 24
    c = math.sqrt(0.5)
    return int(round(24 + dx * c - dy * c)), int(round(24 + dx * c + dy * c))


def _rot90(p):
    return 48 - p[1], p[0]          # clockwise on screen (y down): up -> right


ARROW_V = []
for _k in range(8):
    _pts = [_ARROW_N, [_rot45(p) for p in _ARROW_N]][_k % 2]
    for _i in range(_k // 2):
        _pts = [_rot90(p) for p in _pts]
    ARROW_V.append(_pts)
assert ARROW_V[2][0] == (44, 24) and ARROW_V[4][0] == (24, 44) and ARROW_V[6][0] == (4, 24), "E / S / W tips"
assert ARROW_V[1][0][0] > 24 > ARROW_V[1][0][1], "NE points up-right"
ARROW_FLAT = [c for pts in ARROW_V for p in pts for c in p]
assert len(ARROW_FLAT) == 64 and all(0 <= c <= 48 for c in ARROW_FLAT)

# ---- the HUD documents (kit builders; J() = the runtime value, its sample is what the checks see)
SAMPLE_PIC = ASSET_DIR + "p1a-0123456789abcdef.png"
SAMPLE_T = ASSET_DIR + "t-0123456789abcdef.png"
SAMPLE_MASK = MASK_PREFIX + "0123456789abcdef.png"
SAMPLE_RING = ASSET_DIR + "ring-0123456789abcdef.png"
SAMPLE_ME = ASSET_DIR + "arrow0-0123456789abcdef.png"
CAP_FS = None
for _fs in (16, 15, 14):            # the biggest kit-default label size every caption fits
    if all(SUI.text_width(t, _fs) + FIT_MARGIN <= P1_PIC for t in MAP_CAPS.values()) and \
            all(SUI.text_width(t, _fs) + FIT_MARGIN <= P2_BOX_W - 12 for t in P2_CAP_SAMPLES):
        CAP_FS = _fs
        break
assert CAP_FS is not None, "the map captions fit no label size 14-16: %s" % [(t, SUI.text_width(t, 14)) for t in P2_CAP_SAMPLES]
TILE_MK = 'AssetImage #%s%s { Anchor: (Left: %s, Top: %s, Width: %d, Height: %d); AssetPath: "%s"; }' % (
    MID["tile"], SUI.J("i", "40"), SUI.J("h.tl[i]", "256"), SUI.J("h.tt[i]", "256"), TILE_PX, TILE_PX, SUI.J("h.tp[i]", SAMPLE_T))


def map_p1_appends():
    """P1 / P3: the hud panel top-right, the picture (128 x 128 AssetImage), the caption (b.set: it has a hyphen)."""
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Full: 0); }" % MID["root"]))
    ap.append((MID["root"], SUI.panel(MID["box"], "hud", w=P1_BOX_W, h=P1_BOX_H, anchor={"top": BOX_TOP, "right": BOX_RIGHT})))
    ap.append((MID["box"], 'AssetImage #%s { Anchor: (Width: %d, Height: %d); AssetPath: "%s"; }' % (
        MID["pic"], P1_PIC, P1_PIC, SUI.J("pic", SAMPLE_PIC))))
    ap.append((MID["box"], SUI.spacer(h=4)))
    ap.append((MID["box"], SUI.label(MID["cap"], "", "default", h=CAP_LINE_H, w=P1_PIC, size=CAP_FS, align="Center")))
    ap.sets.append((MID["cap"], "Text", SUI.J("cap", MAP_CAPS["p1a"])))
    return ap


def map_p2_appends():
    """P2: a plain box top-right; the round clip (masked) with a dark backdrop and the grid Group (17 x 17 positions, panned by its
    Anchor) holding the 81 tile AssetImages (one Java loop); the ring and the arrow on top; the caption panel under it."""
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Full: 0); }" % MID["root"]))
    ap.append((MID["root"], SUI.group(MID["box"], layout=None, w=P2_BOX_W, h=P2_BOX_H, anchor={"top": BOX_TOP, "right": BOX_RIGHT})))
    ap.append((MID["box"], SUI.group(MID["clip"], layout=None, w=CLIP_D, h=CLIP_D, anchor={"left": CLIP_L, "top": CLIP_T},
                                     extra='MaskTexturePath: "%s";' % SUI.J("h.mask", SAMPLE_MASK))))
    ap.append((MID["clip"], SUI.group(MID["back"], layout=None, anchor={"full": 0}, bg="hud")))
    ap.append((MID["clip"], SUI.group(MID["grid"], layout=None, w=SPAN * TILE_PX, h=SPAN * TILE_PX,
                                     anchor={"left": SUI.J("h.gl", "-176"), "top": SUI.J("h.gt", "-176")})))
    ap.append((MID["grid"], TILE_MK))
    ap.append((MID["box"], 'AssetImage #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); AssetPath: "%s"; }' % (
        MID["ring"], RING_L, RING_T, RING_D, RING_D, SUI.J("h.ring", SAMPLE_RING))))
    ap.append((MID["box"], 'AssetImage #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); AssetPath: "%s"; }' % (
        MID["me"], ME_L, ME_T, ARROW_S, ARROW_S, SUI.J("h.me", SAMPLE_ME))))
    ap.append((MID["box"], SUI.panel(MID["capbox"], "hud", w=P2_BOX_W, h=CAP_H, anchor={"left": 0, "top": CAP_T},
                                     pad={"horizontal": 6, "vertical": 3})))
    ap.append((MID["capbox"], SUI.label(MID["cap"], "", "default", h=CAP_LINE_H, w=P2_BOX_W - 12, size=CAP_FS, align="Center")))
    ap.sets.append((MID["cap"], "Text", SUI.J("h.cap", P2_CAP_SAMPLES[1])))
    return ap


def map_p2_expanded():
    """P2 with the 81 tiles written out (the ids every runtime document creates): the duplicate-id check."""
    ap = SUI.Appends()
    for parent, mk in MAP_P2:
        if mk is TILE_MK:
            for i in range(GRID_N * GRID_N):
                ap.append((parent, 'AssetImage #%s%d { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); AssetPath: "%s"; }' % (
                    MID["tile"], i, (i % 9 + 4) * TILE_PX, (i // 9 + 4) * TILE_PX, TILE_PX, TILE_PX, SAMPLE_T)))
        else:
            ap.append((parent, mk))
    ap.sets = list(MAP_P2.sets)
    return ap


def check_hud(ap, what):
    """The page checks for a HUD document: the root (Anchor Full 0 - a HUD, not a page) by check_markup, the rest by check_page
    (rules, parents, no duplicate id, every b.set target); every element / property token proven or one of the map trial tokens."""
    items = list(ap)
    assert items[0][0] is None and all(p is not None for p, _m in items[1:]), "%s: one root first" % what
    SUI.check_markup(items[0][1], prefix=PREFIX, root=False)
    rest = SUI.Appends(items[1:])
    rest.sets = list(ap.sets)
    SUI.check_page(rest, PREFIX, known_parents=[MID["root"]])
    toks = SUI.proven_tokens(ap)
    bad = sorted(t for t, g in toks.items() if g is not None and t not in MAP_TRIAL)
    assert not bad, "%s: tokens that are neither proven nor map trial tokens: %s" % (what, bad)
    for _p, mk in items:
        assert "_" not in "".join(re.findall(r"#([A-Za-z0-9_]+)", SUI.render(mk))), "%s: underscore id" % what
    return toks


MAP_P1, MAP_P2 = map_p1_appends(), map_p2_appends()
MAP_TOKENS = {}
for _what, _ap in (("map P1 / P3 box", MAP_P1), ("map P2 minimap", MAP_P2), ("map P2, 81 tiles written out", map_p2_expanded())):
    MAP_TOKENS[_what] = check_hud(_ap, _what)
assert set(t for t in MAP_TOKENS["map P2 minimap"] if MAP_TOKENS["map P2 minimap"][t] is not None) == set(MAP_TRIAL), \
    "P2 uses exactly the 3 trial tokens: %s" % MAP_TOKENS["map P2 minimap"]
assert set(t for t in MAP_TOKENS["map P1 / P3 box"] if MAP_TOKENS["map P1 / P3 box"][t] is not None) == {"element AssetImage",
                                                                                                   "AssetPath"}
for _t in list(MAP_CAPS.values()) + P2_CAP_SAMPLES:
    SUI.check_text(_t.replace("-", " "), "map caption")      # captions go in by b.set anyway (the hyphen is proven inline too)
MAP_TILE_IDX = [i for i, (_p, mk) in enumerate(MAP_P2) if mk is TILE_MK]
assert len(MAP_TILE_IDX) == 1


def map_java(ap, loop_at=None):
    """The kit's Java for a HUD document: appendInline per append (page_root=False: the HUD root), the append at loop_at inside
    `for (int i = 0; i < 81; i++)`, then the b.set lines."""
    out = []
    for k, (parent, mk) in enumerate(ap):
        st = SUI.java_append(parent, mk, b="b", page_root=False)
        out += ["for (int i = 0; i < 81; i++) {", "  " + st, "}"] if k == loop_at else [st]
    out += [SUI.java_set(i, p, v, b="b") for i, p, v in ap.sets]
    return "\n".join("  " + l for l in out)


MAP_P1_JAVA, MAP_P2_JAVA = map_java(MAP_P1), map_java(MAP_P2, MAP_TILE_IDX[0])
print("map probes: HUD key %s (zOrder %d; SkyyHud's %s untouched), P1 box %dx%d, P2 box %dx%d (clip %d at %d,%d, grid %d px), "
      "captions at %d px, trial tokens %s" % (MAP_KEY, MAP_Z, SKYYHUD_KEY, P1_BOX_W, P1_BOX_H, P2_BOX_W, P2_BOX_H, CLIP_D, CLIP_L,
                                              CLIP_T, SPAN * TILE_PX, CAP_FS, sorted(MAP_TRIAL)))
MAP_DUMP = {"key": MAP_KEY, "skyyhud_key": SKYYHUD_KEY, "z": MAP_Z, "ids": MID, "tick_ms": TICK_MS, "tile": TILE_PX, "grid": GRID_N,
            "half": GRID_HALF, "span": SPAN, "clip": CLIP_D, "ring": RING_D, "arrow": ARROW_S, "box": [BOX_TOP, BOX_RIGHT],
            "p2_box": [P2_BOX_W, P2_BOX_H], "clip_at": [CLIP_L, CLIP_T], "ring_at": [RING_L, RING_T], "me_at": [ME_L, ME_T],
            "cap_at": [CAP_T, CAP_H], "p1_pic": P1_PIC, "p1_box": [P1_BOX_W, P1_BOX_H], "tap_ms": TAP_MS, "segments": P5_SEGMENTS,
            "qmax": QMAX, "p3_ttl_ms": P3_TTL_MS, "ready_ms": READY_DELAY_MS, "enc_tick": ENC_PER_TICK, "enc_first": ENC_FIRST,
            "part": PART, "asset_dir": ASSET_DIR, "mask_dir": MASK_DIR, "mask_prefix": MASK_PREFIX, "trial": sorted(MAP_TRIAL),
            "steps": MAP_STEPS, "lines": MAP_LINES, "help": MAP_HELP, "usage": MAP_USAGE, "caps": MAP_CAPS,
            "p2_cap_samples": P2_CAP_SAMPLES, "cap_fs": CAP_FS, "fit_margin": FIT_MARGIN,
            "pal_mask": PAL_MASK, "pal_ring": PAL_RING, "pal_arrow": PAL_ARROW, "pal_test": PAL_TEST, "pal_pic": PAL_PIC,
            "ring_bands": RING_BANDS, "north_tick": NORTH_TICK, "arrow_v": ARROW_FLAT,
            "p1": {"appends": [[p, SUI.render(m)] for p, m in MAP_P1], "sets": [[i, pr, SUI.render(v)] for i, pr, v in MAP_P1.sets]},
            "p2": {"appends": [[p, SUI.render(m)] for p, m in MAP_P2], "sets": [[i, pr, SUI.render(v)] for i, pr, v in MAP_P2.sets],
                   "tile_at": MAP_TILE_IDX[0]}}

if DUMP:
    out = {"kit": KIT_ID, "order": ORDER, "names": dict((str(p.n), p.name) for p in PROBES),
           "keys": dict((str(p.n), p.key) for p in PROBES), "whats": dict((str(n), WHAT[n]) for n in ORDER),
           "open_first": NEW + FIRST, "new": NEW, "first_txt": FIRST_TXT, "per_col": PER_COL,
           "what_w": WHAT_W, "what_fs": WHAT_FS, "name_w": NAME_W, "name_fs": NAME_FS, "fit_margin": FIT_MARGIN,
           "info_w": IX_IN_W, "info_fs": INFO_FS, "last_txts": dict((str(n), last_text(n)) for n in ORDER),
           "nowin_txts": dict((str(n), nowin_text(n)) for n in WIN_N),
           "foot": ["#" + NAV_BACK, "#" + NAV_CLOSE],
           "win": {"views": WIN_N, "arrows": "#" + WP_ARROWS, "grid": "#" + WP_GRID, "probe_items": PROBE_ITEMS, "slots": BOX_SLOTS,
                   "arrow_ids_vault": ARROW_IDS_VAULT, "arrow_ids_vanilla": ARROW_IDS_VANILLA, "arrow_names": ARROW_NAMES,
                   "arrow_desc": ARROW_DESC, "late_ms": LATE_CLOSE_MS, "grace_ms": NET_GRACE_MS,
                   "sync_delay_ms": SYNC_DELAY_MS, "saw_ms": SAW_MS, "sync_rate_ms": SYNC_RATE_MS, "texts": dict(
                       (str(k), v) for k, v in WIN_TEXT.items()), "note": WIN_NOTE, "page_w": WIN_PAGE_W},
           "index": {"appends": [[p, SUI.render(m)] for p, m in IXA], "sets": [[i, pr, v] for i, pr, v in IXA.sets],
                     "info": ["#" + IX + "Info", "Text"], "info_set": list(INFO_SET), "binds": [list(x) for x in IX_BINDS],
                     "w": IX_W, "h": IX_H}}
    for n, (ap, sets, _java, how, h, extra) in list(VIEWS.items()) + list(WVIEWS.items()):
        out[str(n)] = {"appends": [[p, SUI.render(m)] for p, m in ap],
                       "sets": [[i, pr, v] for i, pr, v in sets], "extra": extra, "how": how, "h": h}
    out["map"] = MAP_DUMP           # 0.4: the map probe constants, palettes, arrow polygons and the two HUD documents (samples)
    with open(DUMP, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("dumped the expected page commands to", DUMP)
    if DUMP_ONLY:
        raise SystemExit(0)

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.uiprobe"
T = {
    "PKG": PKG, "VERSION": VERSION,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CA": "com.hypixel.hytale.component.ComponentAccessor",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "ES": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "IGS": "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "VAL": "com.hypixel.hytale.server.core.ui.Value",
    # 0.3: the window probes
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "ICCE": "com.hypixel.hytale.server.core.inventory.container.ItemContainer$ItemContainerChangeEvent",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "MT": "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction",
    "STX": "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
    "ISX": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "MVT": "com.hypixel.hytale.server.core.inventory.transaction.MoveType",
    "ACT": "com.hypixel.hytale.server.core.inventory.transaction.ActionType",
    "WIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "CW": "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow",
    "VWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow",
    "CT": "com.hypixel.hytale.component.ComponentType",
    "HOT": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "STO": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage",
    "BAK": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack",
    "ARM": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "UTI": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "TOO": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Tool",
    "WM": "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager",
    "EREG": "com.hypixel.hytale.event.EventRegistration",
    "ITEM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "PAD": "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPW": "com.hypixel.hytale.server.core.io.adapter.PlayerPacketWatcher",
    "PF": "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT": "com.hypixel.hytale.protocol.Packet",
    "MIS": "com.hypixel.hytale.protocol.packets.inventory.MoveItemStack",
    "SMIS": "com.hypixel.hytale.protocol.packets.inventory.SmartMoveItemStack",
    "DIS": "com.hypixel.hytale.protocol.packets.inventory.DropItemStack",
    "IAC": "com.hypixel.hytale.protocol.packets.inventory.InventoryAction",
    "CLW": "com.hypixel.hytale.protocol.packets.window.CloseWindow",
    "SWA": "com.hypixel.hytale.protocol.packets.window.SendWindowAction",
    "COW": "com.hypixel.hytale.protocol.packets.window.ClientOpenWindow",
    "CPE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent",
    "NAVB": NAV_BACK, "NAVC": NAV_CLOSE, "ARROWS": WP_ARROWS, "GRID": WP_GRID,
    # 0.4: the map probes (engine classes)
    "HUD": "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud",
    "HM": "com.hypixel.hytale.server.core.entity.entities.player.hud.HudManager",
    "CHP": "com.hypixel.hytale.protocol.packets.interface_.CustomHud",
    "CUC": "com.hypixel.hytale.protocol.packets.interface_.CustomUICommand",
    "CMA": "com.hypixel.hytale.server.core.asset.common.CommonAsset",
    "AINI": "com.hypixel.hytale.protocol.packets.setup.AssetInitialize",
    "APRT": "com.hypixel.hytale.protocol.packets.setup.AssetPart",
    "AFIN": "com.hypixel.hytale.protocol.packets.setup.AssetFinalize",
    "ARB": "com.hypixel.hytale.protocol.packets.setup.RequestCommonAssetsRebuild",
    "TCP": "com.hypixel.hytale.protocol.ToClientPacket",
    "PKH": "com.hypixel.hytale.server.core.io.PacketHandler",
    "UWM": "com.hypixel.hytale.protocol.packets.worldmap.UpdateWorldMap",
    "CWM": "com.hypixel.hytale.protocol.packets.worldmap.ClearWorldMap",
    "MCH": "com.hypixel.hytale.protocol.packets.worldmap.MapChunk",
    "MIM": "com.hypixel.hytale.protocol.packets.worldmap.MapImage",
    "WMM": "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager",
    "TRC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "HRT": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "ANC": "com.hypixel.hytale.server.core.ui.Anchor",
    "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    # 0.4: the map probe constants (Q... so no 0.3.1 token is shadowed: ARM / GRID / ARROWS / CA are taken)
    "QKEY": MAP_KEY, "QZ": str(MAP_Z), "QTILE": str(TILE_PX), "QCLIP": str(CLIP_D), "QRING": str(RING_D), "QSPAN": str(SPAN),
    "QTICK": str(TICK_MS), "QTAPMS": str(TAP_MS), "QSEGS": str(P5_SEGMENTS), "QMAX": str(QMAX), "QPTTL": str(P3_TTL_MS),
    "QRDY": str(READY_DELAY_MS), "QENCT": str(ENC_PER_TICK), "QENCF": str(ENC_FIRST), "QPART": str(PART), "QADIR": ASSET_DIR,
    "QMDIR": MASK_DIR, "QMPRE": MASK_PREFIX, "QMLEN": str(len(MASK_DIR)), "QMT": MID["tile"], "QMGRID": MID["grid"],
    "QMME": MID["me"], "QMCAP": MID["cap"],
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["MSG"], "raw"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["PAGE"], "build"),
             (T["PGM"], "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss"),
             (PB, "getCommandRegistry"), (PB, "getLogger"), (PB, "shutdown"), (T["VAL"], "ref"),
             # 0.3: the window probes (every engine member the new classes call - API drift fails the build here)
             (T["PGM"], "openCustomPageWithWindows"), (T["PAGE"], "onDismiss"), (T["PAGE"], "sendUpdate"), (T["BT"], "SlotClicking"),
             (T["PLA"], "getWindowManager"), (T["WM"], "getWindow"), (T["WM"], "closeWindow"), (T["WIN"], "getId"),
             (T["CW"], "onClose0"), (T["VWIN"], "validate"), (T["WIN"], "invalidate"), (T["INVC"], "markDirty"),
             (T["HOT"], "getComponentType"), (T["STO"], "getComponentType"), (T["BAK"], "getComponentType"),
             (T["ARM"], "getComponentType"), (T["UTI"], "getComponentType"), (T["TOO"], "getComponentType"),
             (T["SIC"], "cantRemoveFromSlot"), (T["SIC"], "cantAddToSlot"), (T["SIC"], "cantDropFromSlot"),
             (T["SIC"], "internal_getSlot"), (T["IC"], "internal_moveItemStackFromSlot"), (T["IC"], "moveItemStackFromSlot"),
             (T["IC"], "getItemStack"), (T["IC"], "getCapacity"), (T["IC"], "setItemStackForSlot"), (T["IC"], "registerChangeEvent"),
             (T["ICCE"], "transaction"), (T["INVC"], "getCombined"), (T["INVC"], "EVERYTHING"), (T["INVC"], "STORAGE_HOTBAR_BACKPACK"),
             (T["MVT"], "MOVE_FROM_SELF"), (T["ACT"], "REMOVE"), (T["ISX"], "FAILED_ADD"), (T["EREG"], "unregister"),
             (T["IS"], "isEmpty"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IGS"], "setName"), (T["IGS"], "setDescription"),
             (T["IGS"], "setActivatable"), (T["ITEM"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (T["PAD"], "registerInbound"), (T["PAD"], "deregisterInbound"), (T["PPW"], "accept"), (T["PR"], "getUuid"),
             (T["PR"], "getReference"), (T["REF"], "isValid"), (T["REF"], "getStore"), (T["ST"], "getExternalData"),
             (T["ST"], "getComponent"), (T["ES"], "getWorld"), (T["WLD"], "execute"), (T["WLD"], "scheduleAfter"),
             (T["MIS"], "fromSectionId"), (T["MIS"], "fromSlotId"), (T["MIS"], "quantity"), (T["MIS"], "toSectionId"),
             (T["MIS"], "toSlotId"), (T["SMIS"], "moveType"), (T["DIS"], "inventorySectionId"), (T["DIS"], "slotId"),
             (T["IAC"], "inventoryActionType"), (T["CLW"], "id"), (T["SWA"], "action"), (T["COW"], "type"), (T["CPE"], "type"),
             (T["CPE"], "data")):
    B.probe(pool, c, m)
# 0.4: every engine member the map probe classes use (API drift fails the build here)
WMS = "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapSettings"
for c, m in ((T["HUD"], "show"), (T["HUD"], "update"), (T["HUD"], "getKey"), (T["HUD"], "getPlayerRef"), (T["HUD"], "onRemove"),
             (T["HUD"], "build"), (T["HM"], "addCustomHud"), (T["HM"], "removeCustomHud"), (T["HM"], "getCustomHud"),
             (T["PLA"], "getHudManager"), (T["CHP"], "hudId"), (T["CHP"], "zOrder"), (T["CHP"], "clear"), (T["CHP"], "commands"),
             (T["CHP"], "computeSize"), (T["CMA"], "hash"), (T["CMA"], "toPacket"), (T["CMA"], "getName"), (T["CMA"], "getHash"),
             (T["CMA"], "getBlob0"), (T["AINI"], "computeSize"), (T["APRT"], "computeSize"), (T["AFIN"], "computeSize"),
             (T["ARB"], "computeSize"), (T["PKH"], "write"), (T["PKH"], "writeNoCache"), (T["PR"], "getPacketHandler"),
             (T["UWM"], "chunks"), (T["UWM"], "addedMarkers"), (T["UWM"], "removedMarkers"), (T["UWM"], "computeSize"),
             (T["MCH"], "chunkX"), (T["MCH"], "chunkZ"), (T["MCH"], "image"), (T["MIM"], "width"), (T["MIM"], "height"),
             (T["MIM"], "palette"), (T["MIM"], "bitsPerIndex"), (T["MIM"], "packedIndices"), (T["WLD"], "getWorldMapManager"),
             (T["WLD"], "getName"), (T["WMM"], "getImageIfInMemory"), (T["WMM"], "isWorldMapEnabled"), (T["WMM"], "getGenerator"),
             (T["WMM"], "getWorldMapSettings"), (WMS, "getImageScale"), (T["TRC"], "getPosition"), (T["TRC"], "getRotation"),
             (T["TRC"], "getComponentType"), (T["HRT"], "getRotation"), (T["HRT"], "getComponentType"),
             ("com.hypixel.hytale.math.vector.Rotation3f", "yaw"), ("org.joml.Vector3d", "x"), ("org.joml.Vector3d", "z"),
             (T["ANC"], "setLeft"), (T["ANC"], "setTop"), (T["ANC"], "setWidth"), (T["ANC"], "setHeight"), (T["VAL"], "of"),
             (T["UCB"], "setObject"), (T["UCB"], "getCommands"), (T["PAD"], "registerOutbound"), (T["PAD"], "deregisterOutbound"),
             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (PB, "start"),
             (PB, "getEventRegistry"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"), (T["PR"], "getUuid"),
             (T["PR"], "isValid")):
    B.probe(pool, c, m)

# ================= 0.4: ENGINE FACTS the map probes rely on (HytaleServer.jar bytecode, in order) - a game update that changes one
# stops the build here (the SkyySacks 0.7.12 engine-facts pattern)
import jpype as _jp
_JIP, _JPS, _JBOS = _jp.JClass("javassist.bytecode.InstructionPrinter"), _jp.JClass("java.io.PrintStream"), \
    _jp.JClass("java.io.ByteArrayOutputStream")


def engine_code(cls, meth, sig=None):
    out = []
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) == meth and (sig is None or sig in str(mm.getSignature())):
            bos = _JBOS()
            _JIP(_JPS(bos)).print_(mm)
            out.append(str(bos.toString()))
    return "\n".join(out)


def in_order(txt, needles):
    p = 0
    for nd in needles:
        q = txt.find(nd, p)
        if q < 0:
            return nd
        p = q + len(nd)
    return None


IMB = "com.hypixel.hytale.server.core.universe.world.worldmap.provider.chunk.ImageBuilder"
CAM = "com.hypixel.hytale.server.core.asset.common.CommonAssetModule"
ENGINE_FACTS = [
    ("HudManager.addCustomHud replaces only an entry with the SAME key (get(key), onRemove, CustomHud(key, 0, clear, null), put, "
     "show) - a player has many keyed custom HUDs", T["HM"], "addCustomHud", None,
     ["CustomUIHud.getKey", "Map.get", "CustomUIHud.onRemove", "CustomHud.<init>", "writeNoCache", "Map.put", "CustomUIHud.show"]),
    ("HudManager.removeCustomHud clears that one key", T["HM"], "removeCustomHud", None,
     ["Map.remove", "CustomUIHud.onRemove", "CustomHud.<init>", "writeNoCache"]),
    ("HudManager.resetHud calls onRemove on every registered HUD, then clears the map", T["HM"], "resetHud", None,
     ["Map.entrySet", "CustomUIHud.onRemove", "CustomHud.<init>", "writeNoCache", "Map.clear"]),
    ("CustomUIHud.update sends CustomHud(key, zOrder, clear, commands) to its own player", T["HUD"], "update", None,
     ["CustomUIHud.key", "CustomUIHud.zOrder", "getCommands", "CustomHud.<init>", "getPacketHandler", "writeNoCache"]),
    ("CustomUIHud.show = build + update(true)", T["HUD"], "show", None, ["CustomUIHud.build", "iconst_1", "CustomUIHud.update"]),
    ("a world change (Player.resetManagers): WorldMapTracker.clear (ClearWorldMap), ResetUserInterfaceState, resetHud",
     T["PLA"], "resetManagers", None, ["WorldMapTracker.clear", "HudManager.resetUserInterface", "HudManager.resetHud"]),
    ("ImageBuilder.encodeToPalette: palette + BitFieldArr indices -> MapImage(width, height, palette, bits, bytes)", IMB,
     "encodeToPalette", None, ["calculateBitsRequired", "BitFieldArr.<init>", "BitFieldArr.set", "BitFieldArr.get", "MapImage.<init>"]),
    ("ImageBuilder.packImageData: pixel index = z * imageWidth + x", IMB, "packImageData", None,
     ["rawPixels", "iload_2", "imageWidth", "imul", "iload_1", "iadd", "Color.pack"]),
    ("ImageBuilder$Color.pack = r << 24 | g << 16 | b << 8 | a", IMB + "$Color", "pack", None,
     ["Color.r", "bipush 24", "ishl", "Color.g", "bipush 16", "ishl", "Color.b", "bipush 8", "ishl", "Color.a", "ior"]),
    ("CommonAsset(name, bytes): hash = HashUtil.sha256(bytes)", T["CMA"], "hash", None, ["HashUtil.sha256"]),
    ("CommonAssetModule.sendAsset: AssetInitialize, AssetPart(s) of 2621440 bytes, AssetFinalize, + RequestCommonAssetsRebuild",
     CAM, "lambda$sendAsset$0", None, ["2621440", "AssetInitialize.<init>", "AssetPart.<init>", "AssetFinalize.<init>",
                                       "RequestCommonAssetsRebuild.<init>"]),
    ("PacketHandler.writePacket runs the outbound adapters before the channel write (the tap sees what the server writes)",
     T["PKH"], "writePacket", None, ["PacketAdapters.__handleOutbound", "ChannelConnection.write"]),
    ("an outbound PlayerPacketWatcher gets the GamePacketHandler's PlayerRef and never stops the write", T["PAD"],
     "lambda$registerOutbound$2", None, ["GamePacketHandler", "getPlayerRef", "PlayerPacketWatcher.accept", "iconst_0"]),
    ("WorldMapManager.tick (its own ticking thread) runs WorldMapTracker.tick - where the vanilla map stream is written", T["WMM"],
     "tick", None, ["WorldMapTracker.tick"]),
    ("WorldMapManager.getImageIfInMemory only reads the images map (never generates)", T["WMM"], "getImageIfInMemory", "(J)",
     ["Long2ObjectConcurrentHashMap.get", "ImageEntry.image"]),
    ("Transform.getDirection: x = -sin(yaw), z = -cos(yaw): yaw 0 faces -Z (north), +yaw turns toward -X (west)",
     "com.hypixel.hytale.math.vector.Transform", "getDirection", "(FF)", ["TrigMathUtil.sin", "fneg", "TrigMathUtil.cos", "fneg"]),
]
_bad = []
for (_what, _cls, _meth, _sig, _needles) in ENGINE_FACTS:
    _miss = in_order(engine_code(_cls, _meth, _sig), _needles)
    if _miss is not None:
        _bad.append("%s (%s.%s: no %r in order)" % (_what, _cls.rsplit(".", 1)[1], _meth, _miss))
if _bad:
    raise SystemExit("0.4 engine check FAILED - the map probes would not work as built:\n  " + "\n  ".join(_bad))
print("engine facts: %d verified (HUD keys, world-change reset, MapImage format, asset packets, outbound tap, map thread, cache "
      "read, yaw)" % len(ENGINE_FACTS))

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def MR(cls, src):
    """A method whose text holds kit output: added exactly as written (no @TOKEN@ replacement - the tokens are filled in first)."""
    try:
        cls.addMethod(CtNewMethod.make(src, cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, src[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jl(s):
    return SUI.java_lit(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


# every class first (javassist resolves a type by name once it exists in the pool), then the members in dependency order
log = mk("ProbeLog")
views = mk("ProbeViews")
ses = mk("ProbeSession")
box = mk("ProbeBox", T["SIC"])
win = mk("ProbeWindow", T["CW"])
chg = mk("ProbeChange")
ctk = mk("ProbeCountTask")
ltk = mk("ProbeCloseTask")
stk = mk("ProbeSyncTask")
net = mk("ProbeNet")
page = mk("ProbePage", T["PAGE"])
pw = mk("ProbeWin")

# ---- ProbeLog: the server log lines (0.3: + the last 64 lines in memory - the harness reads them; nothing is written anywhere)
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.LinkedList TAIL = new java.util.LinkedList();")
M(log, 'public static String kit() { return %s; }' % jl(KIT_ID))
M(log, r"""
public static synchronized void remember(String s) {
  TAIL.add(s);
  while (TAIL.size() > 64) TAIL.removeFirst();
}""")
M(log, "public static synchronized String[] tail() { return (String[]) TAIL.toArray(new String[0]); }")
M(log, r"""
public static void info(String msg) {
  try { remember(msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { remember("WARNING " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyUiProbe] " + msg); } catch (Throwable t) { }
}""")

# ---- ProbeViews: every view's statements (one static method per probe page) + the page list
MAXN = max(BY_N)
NAMES = [""] * (MAXN + 1)
KEYS = [""] * (MAXN + 1)
WHATS = [""] * (MAXN + 1)
for p in PROBES:
    NAMES[p.n], KEYS[p.n], WHATS[p.n] = p.name, p.key, WHAT[p.n]
M(views, "public static int count() { return %d; }" % len(PROBES))
M(views, "public static int[] order() { return new int[] { %s }; }" % ", ".join(str(n) for n in ORDER))
M(views, "public static String[] names() { return new String[] { %s }; }" % ", ".join(jl(x) for x in NAMES))
M(views, "public static String[] keys() { return new String[] { %s }; }" % ", ".join(jl(x) for x in KEYS))
M(views, "public static String[] whats() { return new String[] { %s }; }" % ", ".join(jl(x) for x in WHATS))
M(views, r"""
public static boolean has(int n) {
  String[] a = names();
  return n > 0 && n < a.length && a[n].length() > 0;
}""")
M(views, "public static boolean isWin(int n) { return %s; }" % " || ".join("n == %d" % n for n in WIN_N))
M(views, "public static String nameOf(int n) { return has(n) ? names()[n] : \"?\"; }")
M(views, "public static String keyOf(int n) { return has(n) ? keys()[n] : \"?\"; }")
M(views, "public static String whatOf(int n) { return has(n) ? whats()[n] : \"\"; }")
# the page after n in the list order (-1 after the last one or for a missing page)
M(views, r"""
public static int nextOf(int n) {
  int[] o = order();
  for (int i = 0; i + 1 < o.length; i++) { if (o[i] == n) return o[i + 1]; }
  return -1;
}""")
# a page number (1-24) or a stable name (base1, checkbox, number-field, ..., win, secgrid); -1 = none. Locale.ROOT: under a Turkish /
# Azeri default locale toLowerCase() turns "TILE" into a dotless-i "tile" that matches nothing.
M(views, r"""
public static int find(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.startsWith("#")) t = t.substring(1);
  if (t.length() == 0) return -1;
  boolean digits = t.length() <= 3;
  for (int i = 0; i < t.length() && digits; i++) { char c = t.charAt(i); if (c < '0' || c > '9') digits = false; }
  if (digits) {
    int n = Integer.parseInt(t);
    return has(n) ? n : -1;
  }
  String[] a = names();
  for (int i = 1; i < a.length; i++) { if (a[i].length() > 0 && a[i].equals(t)) return i; }
  return -1;
}""")
# P1's arrow items: SkyyVault's own when the server's item asset map knows all three (SkyyVault loaded), else vanilla stand-ins.
# Item.getAssetMap().getAsset(id) is null for an unknown id (ItemStack.getItem() then falls back to Item.UNKNOWN by itself).
M(views, r"""
public static String[] arrowIds() {
  String[] v = %s;
  boolean ok = true;
  try {
    for (int i = 0; i < v.length; i++) { if (@ITEM@.getAssetMap().getAsset(v[i]) == null) ok = false; }
  } catch (Throwable t) { ok = false; }
  if (ok) return v;
  return %s;
}""" % (jarr(ARROW_IDS_VAULT), jarr(ARROW_IDS_VANILLA)))
M(views, "public static String[] arrowNames() { return %s; }" % jarr(ARROW_NAMES))
for n in sorted(VIEWS):
    MR(views, "public static void p%d(%s b) {\n%s\n}" % (n, T["UCB"], VIEWS[n][2]))
M(views, "public static boolean render(@UCB@ b, int n) {\n%s\n  return false;\n}" % "\n".join(
    "  if (n == %d) { p%d(b); return true; }" % (n, n) for n in sorted(VIEWS)))
for n in WIN_N:
    MR(views, "public static void p%d(%s b) {\n%s\n}" % (n, T["UCB"], jv(WVIEWS[n][2])))
M(views, "public static boolean renderWin(@UCB@ b, int n) {\n%s\n  return false;\n}" % "\n".join(
    "  if (n == %d) { p%d(b); return true; }" % (n, n) for n in WIN_N))
MR(views, "public static void index(%s b, %s ev, String info) {\n%s\n%s\n}" % (T["UCB"], T["UEB"], IX_JAVA, jv("\n".join(IX_BIND))))

# ---- ProbeSession: one open (or recently closed) probe window of one admin
for f in ("public @PR@ pr;", "public java.util.UUID owner;", "public String who;", "public int probe;", "public @PKG@.ProbeBox box;",
          "public @PKG@.ProbeWindow win;", "public int winId;", "public @WLD@ world;", "public @ST@ store;", "public @EREG@ reg;",
          "public volatile boolean closed;", "public boolean countQueued;", "public boolean lateQueued;", "public java.util.HashMap last;",
          "public String lastTx;", "public String closingBy;", "public String closedBy;", "public long openedAt;",
          "public long dismissedAt;", "public long closedAt;", "public int moves;", "public boolean syncQueued;", "public int syncs;",
          # review fix 1: sawAt = the packet watcher's stamp (netty thread) of the last client packet for this window; syncFor = the
          # stamp the last queued re-send covered; lastSyncAt = the fallback's rate limit (no watcher) - the last two world thread only
          "public volatile long sawAt;", "public long syncFor;", "public long lastSyncAt;"):
    F(ses, f)
C(ses, "public ProbeSession() { this.winId = -1; this.lastTx = \"\"; this.closedBy = \"\"; }")

# ---- ProbeBox: the scratch container behind a window probe (9 slots: 3 locked probe items + 6 free). Every refusal is by ITEM ID
# wherever the item sits (slot reads are raw internal_getSlot: the engine calls these checks inside the container's write lock).
F(box, "public boolean armed;")
C(box, "public ProbeBox(short cap) { super(cap); this.armed = false; }")
M(box, "public static String[] probeIds() { return %s; }" % jarr(PROBE_ITEMS))
M(box, r"""
public static boolean isProbeId(String id) {
  if (id == null) return false;
  String[] d = probeIds();
  for (int i = 0; i < d.length; i++) { if (d[i].equals(id)) return true; }
  return false;
}""")
M(box, r"""
public static boolean isProbe(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  return isProbeId(s.getItemId());
}""")
M(box, r"""
public boolean probeAt(short slot) {
  if (slot < 0 || slot >= getCapacity()) return false;
  try { return isProbe(internal_getSlot(slot)); } catch (Throwable t) { return false; }
}""")
M(box, r"""
protected boolean cantRemoveFromSlot(short slot) {
  if (this.armed && probeAt(slot)) return true;
  return super.cantRemoveFromSlot(slot);
}""")
M(box, r"""
protected boolean cantDropFromSlot(short slot) {
  if (this.armed && probeAt(slot)) return true;
  return super.cantDropFromSlot(slot);
}""")
# also refuses a stack with a probe item's id from outside (no copy can enter, so a probe item can never merge or be mistaken) and
# anything onto a probe item: the engine's swap (MoveItemStack onto an occupied slot) asks only the TARGET's cantAddToSlot, never
# its cantRemoveFromSlot (ItemContainer.lambda$internal_moveItemStackFromSlot$5, offsets 196-290)
M(box, r"""
protected boolean cantAddToSlot(short slot, @IS@ add, @IS@ existing) {
  if (this.armed && (isProbe(add) || isProbe(existing) || probeAt(slot))) return true;
  return super.cantAddToSlot(slot, add, existing);
}""")
# SkyyVault VView (live since 0.1.2): the whole-slot move primitive (shift-click, Take All) returns NULL for a slot that refuses
# removal and the engine then NPEs - answer with the engine's own failed MoveTransaction instead
M(box, r"""
public @MT@ refused(short slot, @IC@ to, boolean filter) {
  @IS@ cur = getItemStack(slot);
  @STX@ rm = new @STX@(false, @ACT@.REMOVE, slot, cur, cur, (@IS@) null, false, false, filter);
  return new @MT@(false, rm, @MVT@.MOVE_FROM_SELF, to, @ISX@.FAILED_ADD);
}""")
M(box, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, to, allOrNothing, filter);
}""")
M(box, r"""
protected @MT@ internal_moveItemStackFromSlot(short slot, int qty, @IC@ to, boolean allOrNothing, boolean filter) {
  if (filter && slot >= 0 && slot < getCapacity() && cantRemoveFromSlot(slot)) return refused(slot, to, filter);
  return super.internal_moveItemStackFromSlot(slot, qty, to, allOrNothing, filter);
}""")
# a new box: the probe items written in BEFORE the box is armed, then read back (count) - only ever called on the world thread
M(box, r"""
public static @PKG@.ProbeBox make() {
  @PKG@.ProbeBox b = new @PKG@.ProbeBox((short) %d);
  String[] d = probeIds();
  for (int i = 0; i < d.length; i++) b.setItemStackForSlot((short) i, new @IS@(d[i], 1));
  b.armed = true;
  return b;
}""" % BOX_SLOTS)

# ---- ProbeWindow / ProbeChange / ProbeCountTask / ProbeCloseTask / ProbeNet: fields + constructors (bodies after ProbeWin)
win.addInterface(pool.get(T["VWIN"]))
F(win, "public @PKG@.ProbeSession sess;")
C(win, "public ProbeWindow(@IC@ c, @PKG@.ProbeSession s) { super(c); this.sess = s; }")
# Window.invalidate() is PROTECTED: only the window itself may call it (SkyyVault 0.1.5 VWindow.resend - the engine then sends one
# UpdateWindow on its next window tick)
M(win, "public void resend() { invalidate(); }")
chg.addInterface(pool.get("java.util.function.Consumer"))
F(chg, "public @PKG@.ProbeSession sess;")
C(chg, "public ProbeChange(@PKG@.ProbeSession s) { this.sess = s; }")
for k in (ctk, ltk, stk):
    k.addInterface(pool.get("java.lang.Runnable"))
    F(k, "public @PKG@.ProbeSession sess;")
C(ctk, "public ProbeCountTask(@PKG@.ProbeSession s) { this.sess = s; }")
C(ltk, "public ProbeCloseTask(@PKG@.ProbeSession s) { this.sess = s; }")
C(stk, "public ProbeSyncTask(@PKG@.ProbeSession s) { this.sess = s; }")
net.addInterface(pool.get(T["PPW"]))
C(net, "public ProbeNet() { }")

# ---- ProbePage: the one inline page (view 0 = index, n = probe page n), switched by rebuild() after a click; window views (23 / 24)
# carry their ProbeSession (set by ProbeWin.open before openCustomPageWithWindows)
F(page, "public int view;")
F(page, "public String info;")
F(page, "public @PKG@.ProbeSession sess;")
M(page, r"""
public static String lastText(int n) {
  if (!@PKG@.ProbeViews.has(n)) return %s;
  int nx = @PKG@.ProbeViews.nextOf(n);
  return "Last opened: probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + "). Did it look right? "
    + (nx > 0 ? "Next: probe " + nx + " (" + @PKG@.ProbeViews.nameOf(nx) + ")." : "That was the last one.");
}""" % jl(FIRST_TXT))
M(page, r"""
public static String noWinText(int n) {
  return "Probe " + n + " needs its window - open it with its Open button or /skyprobe " + @PKG@.ProbeViews.nameOf(n) + ".";
}""")
C(page, r"""
public ProbePage(@PR@ pr, int view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view;
  this.info = lastText(view);
}""")
# one string value out of the page event JSON (SkyyBank 0.1.3 BankPage.jsonStr, verbatim)
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
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# SlotClicking payload: {"a":"arrow","SlotIndex":2} (the value may be quoted) - SkyyMenu 0.3.4 MenuUtil.jsonInt, verbatim
M(page, r"""
public static int jsonInt(String data, String key) {
  if (data == null || key == null) return -1;
  int p = data.indexOf("\"" + key + "\"");
  if (p < 0) return -1;
  int c = data.indexOf(':', p);
  if (c < 0) return -1;
  int i = c + 1;
  while (i < data.length() && (data.charAt(i) == ' ' || data.charAt(i) == '"')) i++;
  int j = i;
  while (j < data.length() && (Character.isDigit(data.charAt(j)) || data.charAt(j) == '-')) j++;
  if (j == i) return -1;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""")
# one chat line to the admin (ProbeCmds.tell is made after this class, so the page has its own copy)
M(page, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
# 0.3.1: P2's one InventorySectionId update, sent BY THE PAGE ITSELF. CustomUIPage.sendUpdate is PROTECTED: the JVM lets only a
# CustomUIPage subclass call it, on itself - 0.3 called pg.sendUpdate(ub) from ProbeWin, javassist compiled it and the game threw
# IllegalAccessError, so probe 24 never opened. ProbeWin.open calls this right after openCustomPageWithWindows returned; a throw here
# reaches ProbeWin.open's catch (the open counts as failed and the window is closed again, as in 0.3).
M(page, r"""
public void sendSection(int windowId) {
  @UCB@ ub = new @UCB@();
  ub.set("#@GRID@.InventorySectionId", windowId);
  this.sendUpdate(ub);
}""")

# ---- ProbeWin: the window probes (all inventory work on the world thread; the packet watcher only logs)
F(pw, "public static java.util.concurrent.ConcurrentHashMap BOXES = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> box
F(pw, "public static java.util.concurrent.ConcurrentHashMap SESS = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> newest
F(pw, "public static volatile @PF@ NET;")      # written under ensureNet / stopNet (synchronized), read by touched() on world threads
M(pw, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(pw, r"""
public static String cut(String s, int n) {
  if (s == null) return "";
  return s.length() <= n ? s : s.substring(0, n) + "...";
}""")
# ---- counting: item id -> long[1] quantity, over one or more containers
M(pw, r"""
public static void addCounts(java.util.HashMap m, @IC@ c) {
  if (c == null) return;
  int n = c.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = c.getItemStack((short) i);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    long[] v = (long[]) m.get(id);
    if (v == null) { v = new long[1]; m.put(id, v); }
    v[0] += (long) s.getQuantity();
  }
}""")
M(pw, r"""
public static java.util.HashMap counts(@IC@ a, @IC@ b) {
  java.util.HashMap m = new java.util.HashMap();
  addCounts(m, a);
  addCounts(m, b);
  return m;
}""")
M(pw, r"""
public static long val(java.util.HashMap m, String k) {
  if (m == null) return 0L;
  long[] v = (long[]) m.get(k);
  return v == null ? 0L : v[0];
}""")
M(pw, r"""
public static long total(java.util.HashMap m) {
  long t = 0L;
  if (m == null) return 0L;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) t += ((long[]) it.next())[0];
  return t;
}""")
# "" = the same; else "id a -> b, ..." (sorted, so the line is stable)
M(pw, r"""
public static String diff(java.util.HashMap a, java.util.HashMap b) {
  java.util.TreeSet keys = new java.util.TreeSet();
  if (a != null) keys.addAll(a.keySet());
  if (b != null) keys.addAll(b.keySet());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = keys.iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    long x = val(a, k);
    long y = val(b, k);
    if (x != y) {
      if (sb.length() > 0) sb.append(", ");
      sb.append(k).append(' ').append(x).append(" -> ").append(y);
    }
  }
  return sb.toString();
}""")
# how many of the 3 probe items are in the box (each exactly once)
M(pw, r"""
public static int probesIn(@PKG@.ProbeBox box) {
  if (box == null) return 0;
  String[] d = @PKG@.ProbeBox.probeIds();
  java.util.HashMap m = new java.util.HashMap();
  addCounts(m, box);
  int k = 0;
  for (int i = 0; i < d.length; i++) { if (val(m, d[i]) == 1L) k++; }
  return k;
}""")
# the admin's OWN items in the box (everything but the probe items)
M(pw, r"""
public static int ownIn(@PKG@.ProbeBox box) {
  if (box == null) return 0;
  int n = box.getCapacity();
  int k = 0;
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    k += s.getQuantity();
  }
  return k;
}""")
M(pw, r"""
public static String ownList(@PKG@.ProbeBox box) {
  StringBuilder sb = new StringBuilder();
  if (box == null) return "";
  int n = box.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(s.getItemId()).append(" x").append(s.getQuantity());
  }
  return sb.toString();
}""")
M(pw, r"""
public static @IC@ playerAll(@CA@ a, @REF@ ref) {
  try { return @INVC@.getCombined(a, ref, @INVC@.EVERYTHING); } catch (Throwable t) { return null; }
}""")
M(pw, r"""
public static @IC@ playerReturn(@CA@ a, @REF@ ref) {
  try { return @INVC@.getCombined(a, ref, @INVC@.STORAGE_HOTBAR_BACKPACK); } catch (Throwable t) { return null; }
}""")
M(pw, r"""
public static @PKG@.ProbeBox boxFor(java.util.UUID u) {
  @PKG@.ProbeBox b = (@PKG@.ProbeBox) BOXES.get(u);
  if (b != null) return b;
  b = @PKG@.ProbeBox.make();
  BOXES.put(u, b);
  return b;
}""")
# the return on close (vanilla StructuralCraftingWindow.onClose0 pattern, storage first): every own stack moves with the engine's
# own whole-slot move (what does not fit stays in its slot), counted before and after (box + the player's whole inventory, per id).
# Returns { log line, chat line or null }. Pure container work: the harness drives it with stand-in containers.
M(pw, r"""
public static String[] returnTo(@PKG@.ProbeBox box, @IC@ inv, @IC@ all) {
  String[] out = new String[2];
  int own = ownIn(box);
  if (box == null || own == 0) { out[0] = "nothing of the player's was in the probe box"; return out; }
  if (inv == null || all == null) {
    out[0] = "the player's inventory could not be read - " + own + " item(s) stay in the probe box (" + ownList(box) + ")";
    out[1] = own + " of your items stayed in the probe window (your inventory could not be read) - open /skyprobe win to take them.";
    return out;
  }
  java.util.HashMap before = counts(box, all);
  int n = box.getCapacity();
  for (int i = 0; i < n; i++) {
    @IS@ s = box.getItemStack((short) i);
    if (s == null || s.isEmpty() || @PKG@.ProbeBox.isProbe(s)) continue;
    try { box.moveItemStackFromSlot((short) i, inv); } catch (Throwable t) { @PKG@.ProbeLog.warn("returning probe box slot " + i + " failed: " + t); }
  }
  java.util.HashMap after = counts(box, all);
  int left = ownIn(box);
  String d = diff(before, after);
  out[0] = "returned " + (own - left) + " item(s) from the probe box to the inventory"
    + (left > 0 ? ", " + left + " stayed in the box (inventory full: " + ownList(box) + ")" : "")
    + "; counted " + total(before) + " items before and " + total(after) + " after"
    + (d.length() == 0 ? " - nothing created or lost" : " - COUNT CHANGED: " + d);
  if (d.length() > 0) out[1] = "The item count changed while your probe items were returned (" + d + ") - tell Claude.";
  else if (left > 0) out[1] = left + " of your items stayed in the probe window (inventory full) - make room, then open /skyprobe win to take them.";
  else out[1] = "Your " + own + " item(s) from the probe window are back in your inventory (counted before and after: nothing lost).";
  return out;
}""")
# ---- the client packets of a probe window (log only; PlayerPacketWatcher runs on the network thread)
M(pw, r"""
public static String sec(int s, int win) {
  if (win >= 0 && s == win) return "the probe window (" + s + ")";
  if (s == -1) return "hotbar";
  if (s == -2) return "storage";
  if (s == -3) return "armor";
  if (s == -5) return "utility";
  if (s == -8) return "tools";
  if (s == -9) return "backpack";
  if (s >= 0) return "window " + s;
  return "section " + s;
}""")
M(pw, r"""
public static String describe(Object p, int win) {
  if (p == null) return null;
  if (p instanceof @MIS@) {
    @MIS@ m = (@MIS@) p;
    return "MoveItemStack x" + m.quantity + " from " + sec(m.fromSectionId, win) + " slot " + m.fromSlotId + " to " + sec(m.toSectionId, win) + " slot " + m.toSlotId;
  }
  if (p instanceof @SMIS@) {
    @SMIS@ m = (@SMIS@) p;
    return "SmartMoveItemStack (shift-click) x" + m.quantity + " from " + sec(m.fromSectionId, win) + " slot " + m.fromSlotId + " (" + m.moveType + ")";
  }
  if (p instanceof @DIS@) {
    @DIS@ m = (@DIS@) p;
    return "DropItemStack x" + m.quantity + " from " + sec(m.inventorySectionId, win) + " slot " + m.slotId;
  }
  if (p instanceof @IAC@) {
    @IAC@ m = (@IAC@) p;
    return "InventoryAction " + m.inventoryActionType + " on " + sec(m.inventorySectionId, win);
  }
  if (p instanceof @CLW@) {
    @CLW@ m = (@CLW@) p;
    return "CloseWindow " + (win >= 0 && m.id == win ? "for the probe window (" + m.id + ")" : "for window " + m.id);
  }
  if (p instanceof @SWA@) {
    @SWA@ m = (@SWA@) p;
    return "SendWindowAction on " + sec(m.id, win) + ": " + (m.action == null ? "?" : m.action.getClass().getSimpleName());
  }
  if (p instanceof @COW@) {
    @COW@ m = (@COW@) p;
    return "ClientOpenWindow " + m.type;
  }
  if (p instanceof @CPE@) {
    @CPE@ m = (@CPE@) p;
    return "CustomPageEvent " + m.type + (m.data == null ? "" : " " + cut(m.data, 120));
  }
  return null;
}""")
# review fix 1: the client packets whose result the client may have guessed for the probe window, so the server re-sends the truth
# after them: a MoveItemStack with either end on the window, every shift-click (SmartMoveItemStack has no destination - the engine may
# put the stack into the window), a DropItemStack / InventoryAction on the window, a SendWindowAction for it. Never CloseWindow,
# ClientOpenWindow or page events.
M(pw, r"""
public static boolean wantsResend(Object p, int win) {
  if (p == null || win < 0) return false;
  if (p instanceof @MIS@) {
    @MIS@ m = (@MIS@) p;
    return m.fromSectionId == win || m.toSectionId == win;
  }
  if (p instanceof @SMIS@) return true;
  if (p instanceof @DIS@) return ((@DIS@) p).inventorySectionId == win;
  if (p instanceof @IAC@) return ((@IAC@) p).inventorySectionId == win;
  if (p instanceof @SWA@) return ((@SWA@) p).id == win;
  return false;
}""")
# the watcher (netty thread, before the engine's handler queues its world task): stamp sawAt for a packet the window needs a re-send
# after, log the packet; a session closed longer than the grace leaves SESS here (review fix 4: no closed session kept per admin)
M(pw, r"""
public static void packet(@PR@ pr, Object p) {
  if (pr == null || p == null || SESS.isEmpty()) return;
  java.util.UUID u = pr.getUuid();
  @PKG@.ProbeSession s = (@PKG@.ProbeSession) SESS.get(u);
  if (s == null) return;
  long now = System.currentTimeMillis();
  boolean shut = s.closed;
  if (shut && now - s.closedAt > %dL) { SESS.remove(u, s); return; }
  if (!shut && wantsResend(p, s.winId)) s.sawAt = now;
  String d = describe(p, s.winId);
  if (d == null) return;
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the client sent " + d + (shut ? " (after the window closed)" : ""));
}""" % NET_GRACE_MS)
M(pw, r"""
public static synchronized void ensureNet() {
  if (NET != null) return;
  try {
    NET = @PAD@.registerInbound((@PPW@) new @PKG@.ProbeNet());
    @PKG@.ProbeLog.info("watching the client's inventory / window / page packets while a probe window is open (log only)");
  } catch (Throwable t) { NET = null; @PKG@.ProbeLog.warn("could not watch the client's packets (the probes still work, the log just has less): " + t); }
}""")
M(pw, r"""
public static synchronized void stopNet() {
  if (NET == null) return;
  try { @PAD@.deregisterInbound(NET); } catch (Throwable t) { }
  NET = null;
}""")
# ---- the truth after every client packet for the probe window (ProbeWindow.validate, world thread): a REFUSED move (a locked probe
# item) changes nothing, fires no change event and the engine re-sends nothing, so the client could keep its own guess (an item shown
# moved / a ghost in the inventory). One task re-sends the window (resend -> UpdateWindow) and the player's six inventory sections
# (markDirty -> PlayerSendInventorySystem) - SkyyVault 0.1.5 resync - once per watcher stamp (review fix 1, wantSync below).
M(pw, r"""
public static @CT@ invType(int i) {
  if (i == 0) return @HOT@.getComponentType();
  if (i == 1) return @STO@.getComponentType();
  if (i == 2) return @BAK@.getComponentType();
  if (i == 3) return @ARM@.getComponentType();
  if (i == 4) return @UTI@.getComponentType();
  if (i == 5) return @TOO@.getComponentType();
  return null;
}""")
M(pw, r"""
public static void markInv(@ST@ st, @REF@ ref) {
  for (int i = 0; i < 6; i++) {
    try {
      @INVC@ c = (@INVC@) st.getComponent(ref, invType(i));
      if (c != null) c.markDirty();
    } catch (Throwable t) { }
  }
}""")
# review fix 1: validate() runs for every inventory packet that names the window AND on every movement tick (Player.moveTo ->
# WindowManager.validateWindows; knockback, teleports), so a re-send needs a NEW watcher stamp: one re-send per stamp (the two validate
# calls of one MoveItemStack, or a movement validate that runs before the packet's own handler, share it - the re-send is delayed, so it
# still lands after that handler); while one is queued a newer stamp is left for the next validate (the queued one covers every packet
# handled before it runs); a stamp older than SAW_MS is dropped. watched = false (no packet watcher): at most one per SYNC_RATE_MS.
M(pw, r"""
public static boolean wantSync(@PKG@.ProbeSession s, long now, boolean watched) {
  if (s == null || s.closed || s.syncQueued) return false;
  if (!watched) {
    if (s.lastSyncAt > 0L && now - s.lastSyncAt < %dL) return false;
    s.lastSyncAt = now;
    return true;
  }
  long seen = s.sawAt;
  if (seen == 0L || seen == s.syncFor) return false;
  s.syncFor = seen;
  return now - seen <= %dL;
}""" % (SYNC_RATE_MS, SAW_MS))
M(pw, r"""
public static void touched(@PKG@.ProbeSession s) {
  if (s == null || s.world == null) return;
  if (!wantSync(s, System.currentTimeMillis(), NET != null)) return;
  s.syncQueued = true;
  try { s.world.scheduleAfter(new @PKG@.ProbeSyncTask(s), %dL, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { s.syncQueued = false; }
}""" % SYNC_DELAY_MS)
M(pw, r"""
public static void syncNow(@PKG@.ProbeSession s) {
  if (s == null) return;
  s.syncQueued = false;
  if (s.closed) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) return;
    s.win.resend();
    markInv(s.store, ref);
    s.syncs++;
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": re-sending the window failed: " + t); }
}""")
# ---- the move handler: every successful change of the box (MoveItemStack / shift-click / drop / Take All ... handled by the engine)
# queues ONE count on the world thread (after the whole packet handler); countLine compares it with the last count
M(pw, r"""
public static void noteChange(@PKG@.ProbeSession s, Object ev) {
  if (s == null || s.closed) return;
  try { s.lastTx = ((@ICCE@) ev).transaction().getClass().getSimpleName(); } catch (Throwable t) { }
  if (s.countQueued || s.world == null) return;
  s.countQueued = true;
  try { s.world.execute(new @PKG@.ProbeCountTask(s)); } catch (Throwable t) { s.countQueued = false; }
}""")
# { log line, chat line, "1" when it is a WARNING } for a count `now` after a move; s.last becomes `now`
M(pw, r"""
public static String[] countLine(@PKG@.ProbeSession s, java.util.HashMap now) {
  String[] out = new String[3];
  String d = diff(s.last, now);
  int pi = probesIn(s.box);
  s.moves++;
  out[0] = "probe " + s.probe + " " + s.who + ": move " + s.moves + " seen" + (s.lastTx == null || s.lastTx.length() == 0 ? "" : " (" + s.lastTx + ")")
    + ": counted " + total(s.last) + " items before and " + total(now) + " after (probe box + inventory)"
    + (d.length() == 0 ? " - nothing created or lost" : " - COUNT CHANGED: " + d) + "; probe items in the box: " + pi + " of 3";
  if (pi != 3) out[1] = "A locked probe item left the probe window - tell Claude (that is a bug).";
  else if (d.length() > 0) out[1] = "Move seen, but the count changed (" + d + ") - did you drop or pick something up, or did a bag sweep or refill a stack? Tell Claude.";
  else out[1] = "Move seen - " + total(now) + " items counted before and after: nothing created or lost.";
  out[2] = (pi != 3 || d.length() > 0) ? "1" : "0";
  s.last = now;
  return out;
}""")
M(pw, r"""
public static void countNow(@PKG@.ProbeSession s) {
  if (s == null) return;
  s.countQueued = false;
  if (s.closed) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) return;
    String[] r = countLine(s, counts(s.box, playerAll(s.store, ref)));
    if ("1".equals(r[2])) @PKG@.ProbeLog.warn(r[0]); else @PKG@.ProbeLog.info(r[0]);
    say(s.pr, r[1]);
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": counting after a move failed: " + t); }
}""")
# review fix 4: a CLOSED session lets go of everything heavy - SESS keeps the newest session per admin, and a kept World / Store would
# keep an unloaded instance world alive. What stays: owner, who, probe, winId, closed / closedAt / closedBy (the 5 s packet grace and the
# late-close log read them) and the box (kept per admin in BOXES anyway). Only ever called once closed is set.
M(pw, r"""
public static void release(@PKG@.ProbeSession s) {
  if (s == null || !s.closed) return;
  s.reg = null;
  s.win = null;
  s.world = null;
  s.store = null;
  s.pr = null;
  s.last = null;
}""")
# the window closed (ProbeWindow.onClose0 - every path: CloseWindow from the client, the server's close, the engine's closeAllWindows on a
# world change / disconnect): stop counting, then return the admin's own items unless the NEXT window probe already shows the same box.
# closedAt is written BEFORE the volatile closed flag (the netty thread's grace check reads closed, then closedAt).
M(pw, r"""
public static void windowClosed(@PKG@.ProbeSession s, @REF@ ref, @CA@ a) {
  if (s == null || s.closed) return;
  s.closedAt = System.currentTimeMillis();
  s.closed = true;
  s.closedBy = s.closingBy != null ? "the server (" + s.closingBy + ")" : "the client or the engine";
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": window " + s.winId + " closed by " + s.closedBy
    + (s.dismissedAt > 0L ? ", " + (s.closedAt - s.dismissedAt) + " ms after the page closed" : " (the page was still open)")
    + "; " + s.moves + " counted move(s), " + s.syncs + " window re-send(s) after client packets");
  @PKG@.ProbeSession cur = (@PKG@.ProbeSession) SESS.get(s.owner);
  if (cur != null && cur != s && !cur.closed && cur.box == s.box) {
    @PKG@.ProbeLog.info("probe " + s.probe + ": the probe box stays open in probe " + cur.probe + " - its items are returned when that window closes");
    release(s);
    return;
  }
  String[] r = returnTo(s.box, playerReturn(a, ref), playerAll(a, ref));
  if (r[0].indexOf("COUNT CHANGED") >= 0) @PKG@.ProbeLog.warn("probe " + s.probe + " " + s.who + ": " + r[0]);
  else @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": " + r[0]);
  if (r[1] != null) say(s.pr, r[1]);
  release(s);
}""")
# end a session whose window is not registered any more (or could not be closed): the admin's items stay in the box (kept per admin)
M(pw, r"""
public static void endQuiet(@PKG@.ProbeSession s, String why) {
  if (s == null || s.closed) return;
  s.closedAt = System.currentTimeMillis();
  s.closed = true;
  s.closedBy = why;
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  int own = ownIn(s.box);
  @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": session ended (" + why + ")" + (own > 0 ? "; " + own + " own item(s) stay in the probe box: " + ownList(s.box) : ""));
  release(s);
}""")
# the server closes ITS OWN window only (WindowManager.closeWindow throws for a gone id and would close another window under a reused id)
M(pw, r"""
public static void closeNow(@PKG@.ProbeSession s, @REF@ ref, @ST@ st, String why) {
  if (s == null || s.closed) return;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) {
      @WM@ wm = p.getWindowManager();
      if (wm != null && s.winId >= 0 && wm.getWindow(s.winId) == s.win) {
        s.closingBy = why;
        wm.closeWindow(ref, s.winId, st);
      }
    }
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": closing the probe window failed (" + why + "): " + t); }
  if (!s.closed) endQuiet(s, "window not open any more (" + why + ")");
}""")
# the page was closed or replaced (onDismiss): the engine never closes windows here - check again in 1.5 s on the world thread
M(pw, r"""
public static void dismissed(@PKG@.ProbeSession s) {
  if (s == null || s.closed) return;
  if (s.dismissedAt == 0L) s.dismissedAt = System.currentTimeMillis();
  if (s.lateQueued || s.world == null) return;
  s.lateQueued = true;
  try { s.world.scheduleAfter(new @PKG@.ProbeCloseTask(s), %dL, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { s.lateQueued = false; @PKG@.ProbeLog.warn("probe " + s.probe + ": could not schedule the window check: " + t); }
}""" % LATE_CLOSE_MS)
M(pw, r"""
public static void lateClose(@PKG@.ProbeSession s) {
  if (s == null) return;
  if (s.closed) {
    @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": 1.5 s after the page closed the window was already closed (by " + s.closedBy + ")");
    return;
  }
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != s.store) {
      @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the player left this world - the engine closes the window");
      return;
    }
    @PKG@.ProbeLog.info("probe " + s.probe + " " + s.who + ": the window was still open 1.5 s after the page closed (Esc or another page) - the client did NOT close it with the page; the server closes it now");
    closeNow(s, ref, s.store, "page closed 1.5 s ago");
  } catch (Throwable t) { @PKG@.ProbeLog.warn("probe " + s.probe + ": the window check failed: " + t); }
}""")
# P1's arrow grid: one press = one chat line (+ a log line)
M(pw, r"""
public static void arrow(@PR@ pr, int idx) {
  String[] nm = @PKG@.ProbeViews.arrowNames();
  String[] id = @PKG@.ProbeViews.arrowIds();
  if (idx < 0 || idx >= nm.length) { say(pr, "A click on the arrow grid without a slot (SlotIndex " + idx + ") - tell Claude."); return; }
  @PKG@.ProbeLog.info("probe 23 " + (pr == null ? "?" : pr.getUsername()) + ": arrow " + (idx + 1) + " (" + nm[idx] + ", " + id[idx] + ") pressed");
  say(pr, "Arrow " + (idx + 1) + " (" + nm[idx] + ") pressed - the server got it on the first click. Did anything stick to your cursor?");
}""")
# open window probe n: a NEW ProbePage + a ProbeWindow over the admin's probe box, through openCustomPageWithWindows (world thread:
# the command or a page click). Order: a new session first, the page + window, then (P2) the one InventorySectionId update, the
# counting baseline, and only then the previous probe window closes (new page first - the SkyyVault askBuy order).
# 0.3.1: the InventorySectionId update goes through the page's own public sendSection (sendUpdate is protected - see WHY 0.3.1).
M(pw, r"""
public static boolean open(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, int n) {
  String who = pr == null ? "?" : pr.getUsername();
  if (!@PKG@.ProbeViews.isWin(n)) return false;
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { say(pr, "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") could not be opened (no player component)."); return false; }
  java.util.UUID u = pr.getUuid();
  @PKG@.ProbeSession old = (@PKG@.ProbeSession) SESS.get(u);
  @PKG@.ProbeSession s = new @PKG@.ProbeSession();
  s.pr = pr;
  s.owner = u;
  s.who = who;
  s.probe = n;
  s.world = w;
  s.store = st;
  s.openedAt = System.currentTimeMillis();
  boolean ok = false;
  try {
    s.box = boxFor(u);
    s.win = new @PKG@.ProbeWindow(s.box, s);
    @PKG@.ProbePage pg = new @PKG@.ProbePage(pr, n);
    pg.sess = s;
    ensureNet();
    SESS.put(u, s);
    @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + who + ": openCustomPageWithWindows with a ContainerWindow over the " + s.box.getCapacity() + "-slot probe box");
    ok = p.getPageManager().openCustomPageWithWindows(ref, st, pg, new @WIN@[] { s.win });
    if (ok) {
      s.winId = s.win.getId();
      if (n == 24) {
        pg.sendSection(s.winId);
        @PKG@.ProbeLog.info("probe 24 " + who + ": sent #@GRID@.InventorySectionId = " + s.winId + " (one page update, after the window opened)");
      }
      s.reg = s.box.registerChangeEvent(new @PKG@.ProbeChange(s));
      s.last = counts(s.box, playerAll(st, ref));
      @PKG@.ProbeLog.info("sent probe " + n + ": window id " + s.winId + ", probe items in the box " + probesIn(s.box) + " of 3, own items in the box "
        + ownIn(s.box) + ", counted " + total(s.last) + " items (probe box + inventory)");
    }
  } catch (Throwable t) {
    ok = false;
    @PKG@.ProbeLog.warn("could not open probe " + n + ": " + t);
  }
  if (!ok) {
    if (s.win != null && s.win.getId() >= 0) { s.winId = s.win.getId(); closeNow(s, ref, st, "open failed"); }
    endQuiet(s, "open failed");
    say(pr, "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") could not be opened - see the server log.");
    return false;
  }
  if (old != null && !old.closed && old != s) closeNow(old, ref, st, "replaced by probe " + n);
  return true;
}""")
M(pw, r"""
public static void shutdown() {
  stopNet();
  try {
    java.util.Iterator it = BOXES.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      @PKG@.ProbeBox b = (@PKG@.ProbeBox) e.getValue();
      int own = ownIn(b);
      if (own > 0) @PKG@.ProbeLog.warn("server stop: the probe box of " + e.getKey() + " still holds " + own + " of the admin's own item(s): " + ownList(b) + " - give them back by hand");
    }
  } catch (Throwable t) { }
}""")

# ---- bodies that call ProbeWin
# release after windowClosed: a no-op when windowClosed already let go (or the session is still open), the cleanup when it threw
M(win, r"""
public void onClose0(@REF@ ref, @CA@ a) {
  try { super.onClose0(ref, a); } catch (Throwable t) { }
  try { @PKG@.ProbeWin.windowClosed(this.sess, ref, a); } catch (Throwable t) { @PKG@.ProbeLog.warn("probe window close handling failed: " + t); }
  try { @PKG@.ProbeWin.release(this.sess); } catch (Throwable t) { }
}""")
M(win, r"""
public boolean validate(@REF@ ref, @CA@ a) {
  try { @PKG@.ProbeWin.touched(this.sess); } catch (Throwable t) { }
  return true;
}""")
M(stk, r"""
public void run() {
  try { @PKG@.ProbeWin.syncNow(this.sess); } catch (Throwable t) { }
}""")
M(chg, r"""
public void accept(Object ev) {
  try { @PKG@.ProbeWin.noteChange(this.sess, ev); } catch (Throwable t) { }
}""")
M(ctk, r"""
public void run() {
  try { @PKG@.ProbeWin.countNow(this.sess); } catch (Throwable t) { }
}""")
M(ltk, r"""
public void run() {
  try { @PKG@.ProbeWin.lateClose(this.sess); } catch (Throwable t) { }
}""")
M(net, r"""
public void accept(@PR@ pr, @PKT@ p) {
  try { @PKG@.ProbeWin.packet(pr, p); } catch (Throwable t) { }
}""")

# ---- ProbePage: build / clicks / dismiss
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (@PKG@.ProbeViews.isWin(this.view)) {
    if (this.sess != null && !this.sess.closed && @PKG@.ProbeViews.renderWin(b, this.view)) {
      ev.addEventBinding(@BT@.Activating, "#@NAVB@", @EVD@.of("a", "back"));
      ev.addEventBinding(@BT@.Activating, "#@NAVC@", @EVD@.of("a", "close"));
      if (this.view == 23) ev.addEventBinding(@BT@.SlotClicking, "#@ARROWS@", @EVD@.of("a", "arrow"), false);
      return;
    }
    this.info = noWinText(this.view);
    this.view = 0;
  } else if (this.view > 0 && @PKG@.ProbeViews.render(b, this.view)) {
    ev.addEventBinding(@BT@.Activating, "#@NAVB@", @EVD@.of("a", "back"));
    ev.addEventBinding(@BT@.Activating, "#@NAVC@", @EVD@.of("a", "close"));
    return;
  }
  @PKG@.ProbeViews.index(b, ev, this.info);
}""")
# clicks run on the player's world thread. open:<n> = the index Open buttons (23 / 24: ProbeWin.open - a new page with its window);
# back = the probe footer (a window view: the list first, then the window closes); close = both Close buttons; arrow = P1's grid.
# A probe whose build() throws inside rebuild() (the engine sends nothing then, the client keeps the index): the page goes back to
# the index view and the admin gets one chat line - never a rebuild() from the catch (review 2026-09-29).
# back only sets the Info line when it leaves a probe page: a stale or double back (view already 0) keeps "Last opened ..." or the
# failure line instead of resetting it to lastText(0) (0.2 review); it still re-sends the index.
# close on a window view (review fix 3): the session is detached first (so the onDismiss that close() triggers schedules no 1.5 s
# check), the page closes, then the server closes the window AT ONCE - even when close() threw.
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  int tried = -1;
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) {
      @PKG@.ProbeSession cs = this.sess;
      this.sess = null;
      if (cs != null && !cs.closed && cs.dismissedAt == 0L) cs.dismissedAt = System.currentTimeMillis();
      try { close(); } catch (Throwable t) { @PKG@.ProbeLog.warn("closing the probe page failed: " + t); }
      if (cs != null) @PKG@.ProbeWin.closeNow(cs, ref, st, "Close button");
      return;
    }
    if (a.equals("back")) {
      @PKG@.ProbeSession s = this.sess;
      this.sess = null;
      if (this.view > 0) {
        this.info = lastText(this.view);
        this.view = 0;
      }
      rebuild();
      if (s != null) @PKG@.ProbeWin.closeNow(s, ref, st, "Back to the list");
      return;
    }
    if (a.equals("arrow")) {
      if (this.view == 23 && this.sess != null) @PKG@.ProbeWin.arrow(this.playerRef, jsonInt(data, "SlotIndex"));
      return;
    }
    if (a.startsWith("open:")) {
      int n = -1;
      try { n = Integer.parseInt(a.substring(5)); } catch (Throwable t) { n = -1; }
      if (!@PKG@.ProbeViews.has(n)) return;
      if (@PKG@.ProbeViews.isWin(n)) {
        @WLD@ w = null;
        try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
        @PKG@.ProbeWin.open(ref, st, this.playerRef, w, n);
        return;
      }
      @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + this.playerRef.getUsername());
      tried = n;
      this.view = n;
      this.info = lastText(n);
      rebuild();
      @PKG@.ProbeLog.info("sent probe " + n);
    }
  } catch (Throwable ex) {
    @PKG@.ProbeLog.warn("probe page click failed" + (tried > 0 ? " (probe " + tried + ")" : "") + ": " + ex);
    if (tried > 0) {
      this.view = 0;
      this.info = "Probe " + tried + " could not be built - see the server log.";
      say(this.playerRef, "Probe " + tried + " (" + @PKG@.ProbeViews.nameOf(tried) + ") could not be built - see the server log.");
    }
  }
}""")
M(page, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try { if (this.sess != null) @PKG@.ProbeWin.dismissed(this.sess); } catch (Throwable t) { }
}""")

# ================= 0.4: the MAP PROBES (classes first, then the members in dependency order) =================
mpng = mk("MapPng")        # MapImage <-> indices, PNG writer (Deflater + CRC32), the generated pictures (as MapImages)
mgeo = mk("MapGeo")        # the pan / ring-buffer / heading math (pure)
masset = mk("MapAsset", T["CMA"])   # one runtime PNG as a CommonAsset
mreq = mk("MapReq")        # a request from a command / event (world thread) to the tick
mp3 = mk("MapP3")          # an armed P3 (survives a world change / reconnect on purpose)
msess = mk("MapSess")      # one player's map probes
mhud = mk("MapHud", T["HUD"])       # the probe HUD (its own key)
mui = mk("MapUi")          # the two HUD documents (kit Java)
mprobe = mk("MapProbe")    # everything else (the tick)
mtick = mk("MapTick")
mread = mk("MapRead")
matt = mk("MapAttach")
mdet = mk("MapDetach")
mrdy = mk("MapReady")
mquit = mk("MapQuit")
mtap = mk("MapTap")


def jint(v):
    return str(int(v))


def jints(vs):
    return "new int[] { %s }" % ", ".join(jint(v) for v in vs)


# ---- MapPng: indices <-> packed bits (the engine's BitFieldArr layout), the PNG writer, the generated pictures
F(mpng, "public static final int[] AV = %s;" % jints(ARROW_FLAT))     # the 8 arrow polygons (doubled grid), 8 ints each
M(mpng, r"""
public static void put32(java.io.ByteArrayOutputStream o, int v) {
  o.write((v >>> 24) & 255);
  o.write((v >>> 16) & 255);
  o.write((v >>> 8) & 255);
  o.write(v & 255);
}""")
M(mpng, r"""
public static byte[] ascii(String s) {
  byte[] b = new byte[s.length()];
  for (int i = 0; i < b.length; i++) b[i] = (byte) s.charAt(i);
  return b;
}""")
M(mpng, r"""
public static void chunk(java.io.ByteArrayOutputStream o, String type, byte[] data) {
  byte[] t = ascii(type);
  put32(o, data.length);
  o.write(t, 0, t.length);
  o.write(data, 0, data.length);
  java.util.zip.CRC32 c = new java.util.zip.CRC32();
  c.update(t, 0, t.length);
  c.update(data, 0, data.length);
  put32(o, (int) c.getValue());
}""")
M(mpng, r"""
public static byte[] zlib(byte[] raw) {
  java.util.zip.Deflater d = new java.util.zip.Deflater(9);
  byte[] out = null;
  try {
    d.setInput(raw, 0, raw.length);
    d.finish();
    java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream(raw.length / 4 + 64);
    byte[] buf = new byte[8192];
    int guard = 0;
    while (!d.finished() && guard < 100000) {
      int n = d.deflate(buf, 0, buf.length);
      if (n > 0) o.write(buf, 0, n);
      guard = guard + 1;
    }
    if (d.finished()) out = o.toByteArray();
  } catch (Throwable t) { out = null; }
  try { d.end(); } catch (Throwable t) { }
  return out;
}""")
M(mpng, r"""
public static byte[] png(int w, int h, int depth, int ctype, byte[] plte, byte[] trns, byte[] raw) {
  byte[] z = zlib(raw);
  if (z == null) return null;
  java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream(z.length + 160);
  o.write(137); o.write(80); o.write(78); o.write(71); o.write(13); o.write(10); o.write(26); o.write(10);
  byte[] ih = new byte[13];
  ih[0] = (byte) (w >>> 24); ih[1] = (byte) (w >>> 16); ih[2] = (byte) (w >>> 8); ih[3] = (byte) w;
  ih[4] = (byte) (h >>> 24); ih[5] = (byte) (h >>> 16); ih[6] = (byte) (h >>> 8); ih[7] = (byte) h;
  ih[8] = (byte) depth;
  ih[9] = (byte) ctype;
  chunk(o, "IHDR", ih);
  if (plte != null) chunk(o, "PLTE", plte);
  if (trns != null) chunk(o, "tRNS", trns);
  chunk(o, "IDAT", z);
  chunk(o, "IEND", new byte[0]);
  return o.toByteArray();
}""")
# BitFieldArr (the engine's MapImage packing): value i in bits [i * bits, i * bits + bits), bit p = byte p / 8 bit p % 8, LSB first
M(mpng, r"""
public static int[] unpack(byte[] packed, int bits, int count) {
  int[] out = new int[count];
  if (bits <= 0 || packed == null) return out;
  for (int i = 0; i < count; i++) {
    long bit = (long) i * (long) bits;
    int v = 0;
    int got = 0;
    while (got < bits) {
      long p = bit + (long) got;
      int bi = (int) (p >> 3);
      int off = (int) (p & 7L);
      int take = 8 - off;
      if (take > bits - got) take = bits - got;
      int b = bi < packed.length ? (packed[bi] & 255) : 0;
      v = v | (((b >>> off) & ((1 << take) - 1)) << got);
      got = got + take;
    }
    out[i] = v;
  }
  return out;
}""")
M(mpng, r"""
public static byte[] pack(int[] idx, int bits) {
  int n = idx.length;
  byte[] out = new byte[(int) (((long) n * (long) bits + 7L) / 8L)];
  for (int i = 0; i < n; i++) {
    int v = idx[i];
    long bit = (long) i * (long) bits;
    int done = 0;
    while (done < bits) {
      long p = bit + (long) done;
      int bi = (int) (p >> 3);
      int off = (int) (p & 7L);
      int take = 8 - off;
      if (take > bits - done) take = bits - done;
      int m = (1 << take) - 1;
      out[bi] = (byte) ((out[bi] & ~(m << off)) | (((v >>> done) & m) << off));
      done = done + take;
    }
  }
  return out;
}""")
# the engine's ImageBuilder.calculateBitsRequired: 4 for <= 16 colours, 8 <= 256, 12 <= 4096, else 16
M(mpng, r"""
public static int bitsFor(int colours) {
  if (colours <= 16) return 4;
  if (colours <= 256) return 8;
  if (colours <= 4096) return 12;
  return 16;
}""")
M(mpng, r"""
public static @MIM@ image(int w, int h, int[] pal, int[] idx) {
  int bits = bitsFor(pal.length);
  return new @MIM@(w, h, pal, (byte) bits, pack(idx, bits));
}""")
# <= 256 colours: an indexed PNG (bit depth 1 / 2 / 4 / 8 by palette size, samples packed from the MSB as PNG wants), PLTE from the
# palette's RGB, tRNS up to the last entry whose alpha is not 255; scale = nearest neighbour
M(mpng, r"""
public static byte[] indexed(int w, int h, int[] pal, int[] idx, int scale) {
  int n = pal.length;
  int depth = n <= 2 ? 1 : (n <= 4 ? 2 : (n <= 16 ? 4 : 8));
  int W = w * scale;
  int H = h * scale;
  int rb = (W * depth + 7) / 8;
  byte[] raw = new byte[H * (rb + 1)];
  for (int y = 0; y < H; y++) {
    int base = y * (rb + 1);
    int sy = y / scale;
    for (int x = 0; x < W; x++) {
      int v = idx[sy * w + x / scale];
      int bit = x * depth;
      int bi = base + 1 + (bit >> 3);
      int sh = 8 - depth - (bit & 7);
      raw[bi] = (byte) (raw[bi] | (v << sh));
    }
  }
  byte[] plte = new byte[n * 3];
  int last = -1;
  for (int k = 0; k < n; k++) {
    int c = pal[k];
    plte[k * 3] = (byte) (c >>> 24);
    plte[k * 3 + 1] = (byte) (c >>> 16);
    plte[k * 3 + 2] = (byte) (c >>> 8);
    if ((c & 255) != 255) last = k;
  }
  byte[] trns = null;
  if (last >= 0) {
    trns = new byte[last + 1];
    for (int k = 0; k <= last; k++) trns[k] = (byte) (pal[k] & 255);
  }
  return png(W, H, depth, 3, plte, trns, raw);
}""")
M(mpng, r"""
public static byte[] truecolor(int w, int h, int[] pal, int[] idx, int scale) {
  int W = w * scale;
  int H = h * scale;
  int row = 1 + W * 4;
  byte[] raw = new byte[H * row];
  for (int y = 0; y < H; y++) {
    int base = y * row;
    int sy = y / scale;
    for (int x = 0; x < W; x++) {
      int c = pal[idx[sy * w + x / scale]];
      int p = base + 1 + x * 4;
      raw[p] = (byte) (c >>> 24);
      raw[p + 1] = (byte) (c >>> 16);
      raw[p + 2] = (byte) (c >>> 8);
      raw[p + 3] = (byte) c;
    }
  }
  return png(W, H, 8, 6, null, null, raw);
}""")
# a MapImage (a real map tile or one this mod made) -> PNG bytes; null = not a picture this encoder takes (sizes 1-512, 1-16 bits,
# enough packed bytes, every index inside the palette, the scaled picture <= 1024 px)
M(mpng, r"""
public static byte[] fromMapImage(@MIM@ m, int scale) {
  if (m == null || scale < 1 || scale > 8) return null;
  int w = m.width;
  int h = m.height;
  int[] pal = m.palette;
  byte[] packed = m.packedIndices;
  int bits = m.bitsPerIndex & 255;
  if (w < 1 || h < 1 || w > 512 || h > 512 || w * scale > 1024 || h * scale > 1024) return null;
  if (pal == null || pal.length < 1 || bits < 1 || bits > 16 || packed == null) return null;
  long need = ((long) w * (long) h * (long) bits + 7L) / 8L;
  if ((long) packed.length < need) return null;
  int[] idx = unpack(packed, bits, w * h);
  for (int i = 0; i < idx.length; i++) {
    if (idx[i] >= pal.length) return null;
  }
  if (pal.length <= 256) return indexed(w, h, pal, idx, scale);
  return truecolor(w, h, pal, idx, scale);
}""")
M(mpng, r"""
public static int sharpScale(@MIM@ m, int tile) {
  if (m == null || m.width < 1) return 1;
  int s = tile / m.width;
  return s < 1 ? 1 : (s > 8 ? 8 : s);
}""")
# the generated pictures - integer geometry only (the harness redraws them in Python and compares every pixel)
M(mpng, r"""
public static @MIM@ mask(int d) {
  int[] idx = new int[d * d];
  long r2 = (long) d * (long) d;
  for (int y = 0; y < d; y++) {
    for (int x = 0; x < d; x++) {
      long dx = (long) (2 * x + 1 - d);
      long dy = (long) (2 * y + 1 - d);
      idx[y * d + x] = (dx * dx + dy * dy <= r2) ? 1 : 0;
    }
  }
  return image(d, d, %s, idx);
}""" % jints(PAL_MASK))
M(mpng, r"""
public static @MIM@ ring(int d) {
  int[] idx = new int[d * d];
  for (int y = 0; y < d; y++) {
    for (int x = 0; x < d; x++) {
      int dx = 2 * x + 1 - d;
      int dy = 2 * y + 1 - d;
      int r2 = dx * dx + dy * dy;
      int v = 0;
      if (r2 >= %d && r2 < %d) v = 1;
      else if (r2 >= %d && r2 < %d) v = 2;
      else if (r2 >= %d && r2 < %d) v = 1;
      int ax = dx < 0 ? -dx : dx;
      if (y < %d && ax <= 2 * (%d - y)) v = 3;
      idx[y * d + x] = v;
    }
  }
  return image(d, d, %s, idx);
}""" % (RING_BANDS[0], RING_BANDS[1], RING_BANDS[1], RING_BANDS[2], RING_BANDS[2], RING_BANDS[3], NORTH_TICK, NORTH_TICK,
        jints(PAL_RING)))
M(mpng, r"""
public static boolean inTri(int ax, int ay, int bx, int by, int cx, int cy, int px, int py) {
  long d1 = (long) (bx - ax) * (long) (py - ay) - (long) (by - ay) * (long) (px - ax);
  long d2 = (long) (cx - bx) * (long) (py - by) - (long) (cy - by) * (long) (px - bx);
  long d3 = (long) (ax - cx) * (long) (py - cy) - (long) (ay - cy) * (long) (px - cx);
  boolean neg = d1 < 0L || d2 < 0L || d3 < 0L;
  boolean pos = d1 > 0L || d2 > 0L || d3 > 0L;
  return !(neg && pos);
}""")
M(mpng, r"""
public static boolean inArrow(int b, int px, int py) {
  int o = b * 8;
  int[] v = AV;
  return inTri(v[o], v[o + 1], v[o + 2], v[o + 3], v[o + 4], v[o + 5], px, py)
    || inTri(v[o], v[o + 1], v[o + 4], v[o + 5], v[o + 6], v[o + 7], px, py);
}""")
M(mpng, r"""
public static @MIM@ arrow(int b) {
  int s = %d;
  int[] idx = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      if (inArrow(b, 2 * x + 1, 2 * y + 1)) idx[y * s + x] = 2;
    }
  }
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      if (idx[y * s + x] != 0) continue;
      boolean edge = (x > 0 && idx[y * s + x - 1] == 2) || (x + 1 < s && idx[y * s + x + 1] == 2)
        || (y > 0 && idx[(y - 1) * s + x] == 2) || (y + 1 < s && idx[(y + 1) * s + x] == 2);
      if (edge) idx[y * s + x] = 1;
    }
  }
  return image(s, s, %s, idx);
}""" % (ARROW_S, jints(PAL_ARROW)))
M(mpng, r"""
public static @MIM@ picture(int variant) {
  int s = %d;
  int[] idx = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      int v = (x >= s / 2 ? 1 : 0) + (y >= s / 2 ? 2 : 0);
      int dx = 2 * x + 1 - s;
      int dy = 2 * y + 1 - s;
      int r2 = dx * dx + dy * dy;
      if (r2 >= 88 * 88 && r2 <= 100 * 100) v = 5;
      if ((x == y || x == y + 1) && r2 < 88 * 88) v = 5;
      int ax = dx < 0 ? -dx : dx;
      if (y >= 8 && y < 30 && ax <= 2 * (y - 8)) v = 6;
      if (x < 3 || y < 3 || x >= s - 3 || y >= s - 3) v = 4;
      idx[y * s + x] = v;
    }
  }
  int[] pal = variant == 0 ? %s : (variant == 1 ? %s : %s);
  return image(s, s, pal, idx);
}""" % (P1_PIC, jints(PAL_PIC[0]), jints(PAL_PIC[1]), jints(PAL_PIC[2])))
M(mpng, r"""
public static @MIM@ testTile(int parity) {
  int s = 16;
  int[] idx = new int[s * s];
  for (int y = 0; y < s; y++) {
    for (int x = 0; x < s; x++) {
      int v = 0;
      if (x == y) v = 2;
      if (x == 0 || y == 0 || x == s - 1 || y == s - 1) v = 1;
      idx[y * s + x] = v;
    }
  }
  return image(s, s, parity == 0 ? %s : %s, idx);
}""" % (jints(PAL_TEST[0]), jints(PAL_TEST[1])))

# ---- MapGeo: chunk / slot / pan / heading math (pure; the harness walks it across chunk borders)
M(mgeo, "public static int chunkOf(double v) { return (int) Math.floor(v / 32.0); }")
M(mgeo, "public static int slot(int cx, int cz) { return Math.floorMod(cx, 9) + 9 * Math.floorMod(cz, 9); }")
M(mgeo, "public static long key(int cx, int cz) { return (((long) cx) << 32) | (((long) cz) & 4294967295L); }")
M(mgeo, "public static int keyX(long k) { return (int) (k >> 32); }")
M(mgeo, "public static int keyZ(long k) { return (int) k; }")
# the 9 x 9 window (centre cc +- 4) must lie inside the grid Group's 17 positions starting at chunk b
M(mgeo, "public static boolean inGroup(int cc, int b) { return cc - 4 >= b && cc + 4 <= b + 16; }")
M(mgeo, "public static int base(int cc) { return cc - 8; }")
M(mgeo, "public static int tilePos(int c, int b) { return (c - b) * %d; }" % TILE_PX)
# the grid Group's Left / Top inside the round clip so that block coordinate p sits at the clip centre
M(mgeo, "public static int groupPos(double p, int b) { return (int) Math.round(%d.0 - (p - (double) b * 32.0) * %d.0 / 32.0); }"
  % (CLIP_D // 2, TILE_PX))
# the arrow picture for a Hytale yaw (radians; 0 faces -Z = north, +yaw turns toward -X = west - Transform.getDirection): the
# compass bearing is -yaw; 8 buckets of 45 degrees centred on N, NE, E, SE, S, SW, W, NW
M(mgeo, r"""
public static int bucket(float yaw) {
  if (Float.isNaN(yaw) || Float.isInfinite(yaw)) return 0;
  double deg = -((double) yaw) * 180.0 / Math.PI;
  double b = deg % 360.0;
  if (b < 0.0) b = b + 360.0;
  int k = (int) Math.floor((b + 22.5) / 45.0);
  return k % 8;
}""")

# ---- MapAsset: one runtime PNG (the CommonAsset base keeps only a WeakReference to its blob: the bytes stay here)
F(masset, "public byte[] bytes;")
F(masset, "public long madeNs;")
F(masset, "public int w;")
F(masset, "public int h;")
C(masset, "public MapAsset(String name, String hash, byte[] b) { super(name, hash, b); this.bytes = b; }")
M(masset, "protected java.util.concurrent.CompletableFuture getBlob0() { return java.util.concurrent.CompletableFuture.completedFuture(this.bytes); }")

# ---- MapReq / MapP3: plain data
for f in ("public String kind;", "public @PR@ pr;", "public java.util.UUID uuid;", "public String who;", "public @WLD@ world;",
          "public @ST@ store;", "public double px;", "public double pz;", "public float yaw;", "public boolean posOk;",
          "public String info;", "public String wname;", "public long at;"):
    F(mreq, f)
C(mreq, "public MapReq() { this.wname = \"?\"; this.info = \"world ?\"; }")
for f in ("public java.util.UUID uuid;", "public String who;", "public boolean resend;", "public long armedAt;", "public long dueAt;",
          "public boolean sawQuit;", "public int shows;", "public @PR@ pr;", "public @WLD@ world;", "public @ST@ store;"):
    F(mp3, f)
C(mp3, "public MapP3() { }")

# ---- MapSess: one player's map probes. Tick-thread state unless marked: the position snapshot is written by the world-thread read
# (volatile), the queue / counters by the tap (lock-free)
for f in ("public @PR@ pr;", "public java.util.UUID uuid;", "public String who;", "public @WLD@ world;", "public @ST@ store;",
          "public int mode;", "public @PKG@.MapHud hud;", "public long hudAt;", "public long started;",
          "public volatile double px;", "public volatile double pz;", "public volatile float yaw;", "public volatile long posAt;",
          "public volatile int posState;", "public volatile boolean readPending;", "public long posUsed;", "public volatile long posSeq;",
          "public long posUsedSeq;",
          "public boolean capture;", "public boolean sharp;", "public boolean more;", "public boolean tilesDirty;", "public java.util.HashMap tiles;",
          "public int ccx;", "public int ccz;", "public int bx;", "public int bz;", "public int gl;", "public int gt;", "public int arrow;",
          "public long[] slotKey;", "public Object[] slotImg;", "public String[] slotPath;", "public int[] slotSrc;",
          "public String[] arrows;", "public int srcMap;", "public int srcCache;", "public int srcTest;", "public String capText;",
          "public int pans;", "public int swaps;", "public int jumps;", "public int rebases;", "public int encodes;",
          "public long encNs;", "public long encBytes;", "public int badImages;",
          "public int assets;", "public int assetPackets;", "public long assetBytes;", "public int cachedHits;", "public int rebuilds;",
          "public int updates;", "public long updateBytes;",
          "public volatile boolean wants;",
          "public final java.util.concurrent.ConcurrentLinkedQueue q = new java.util.concurrent.ConcurrentLinkedQueue();",
          "public final java.util.concurrent.atomic.AtomicInteger qn = new java.util.concurrent.atomic.AtomicInteger();",
          "public final java.util.concurrent.atomic.AtomicLong seen = new java.util.concurrent.atomic.AtomicLong();",
          "public final java.util.concurrent.atomic.AtomicLong dropped = new java.util.concurrent.atomic.AtomicLong();",
          "public volatile int tapMode;", "public long tapStart;", "public long tapEnd;", "public String tapInfo;", "public int seg;",
          "public boolean p5done;", "public String nextInfo;", "public boolean infoOpen;", "public long drop0;",
          "public long upd;", "public long chunks;", "public long nulls;", "public long imgs;", "public long mAdd;", "public long mRem;",
          "public long bytes;", "public long clears;", "public int tickMax;", "public int minW;", "public int maxW;", "public int minPal;",
          "public int maxPal;", "public int bitsMask;"):
    F(msess, f)
C(msess, r"""
public MapSess() {
  this.slotKey = new long[81];
  this.slotImg = new Object[81];
  this.slotPath = new String[81];
  this.slotSrc = new int[81];
  for (int i = 0; i < 81; i++) this.slotKey[i] = Long.MIN_VALUE;
  this.tiles = new java.util.HashMap();
  this.arrow = -1;
  this.capText = "";
  this.tapInfo = "world ?";
}""")

# ---- MapHud: the probe's own keyed custom HUD. build() replays the document from its fields (world thread, inside
# HudManager.addCustomHud -> show); push() = one update from the tick (CustomUIHud.update on this - public); onRemove() (the engine:
# removeCustomHud, resetHud at a world change, or a newer HUD with the same key) only flags it - the tick ends the session
for f in ("public @PKG@.MapSess sess;", "public int mode;", "public volatile boolean attached;", "public volatile boolean gone;",
          "public volatile boolean ended;", "public String pic;", "public String cap;", "public String mask;", "public String ring;",
          "public String me;", "public int gl;", "public int gt;", "public int[] tl;", "public int[] tt;", "public String[] tp;"):
    F(mhud, f)
C(mhud, r"""
public MapHud(@PR@ pr, @PKG@.MapSess s, int mode) {
  super(pr, "@QKEY@", @QZ@);
  this.sess = s;
  this.mode = mode;
  this.tl = new int[81];
  this.tt = new int[81];
  this.tp = new String[81];
  this.pic = "";
  this.cap = "";
  this.mask = "";
  this.ring = "";
  this.me = "";
}""")
M(mhud, r"""
public synchronized boolean push(@UCB@ b) {
  if (!this.attached || this.gone || this.ended) return false;
  update(false, b);
  return true;
}""")
# ---- MapUi: the two HUD documents (the kit's Java, page_root=False: the HUD root is Anchor Full 0)
MR(mui, jv("public static void p1(@UCB@ b, String pic, String cap) {\n") + MAP_P1_JAVA + "\n}")
MR(mui, jv("public static void p2(@UCB@ b, @PKG@.MapHud h) {\n") + MAP_P2_JAVA + "\n}")
M(mhud, r"""
protected void build(@UCB@ b) {
  if (this.mode == 3 || this.mode == 4) @PKG@.MapUi.p2(b, this);
  else @PKG@.MapUi.p1(b, this.pic, this.cap);
}""")

# ---- the small tasks / listeners: fields + constructors (their bodies call MapProbe, below)
mtick.addInterface(pool.get("java.lang.Runnable"))
C(mtick, "public MapTick() { }")
mread.addInterface(pool.get("java.lang.Runnable"))
F(mread, "public java.util.ArrayList list;")
C(mread, "public MapRead(java.util.ArrayList l) { this.list = l; }")
matt.addInterface(pool.get("java.lang.Runnable"))
F(matt, "public @PKG@.MapSess sess;")
F(matt, "public @PKG@.MapHud hud;")
F(matt, "public @ST@ store;")
C(matt, "public MapAttach(@PKG@.MapSess s, @PKG@.MapHud h, @ST@ st) { this.sess = s; this.hud = h; this.store = st; }")
mdet.addInterface(pool.get("java.lang.Runnable"))
F(mdet, "public @PR@ pr;")
F(mdet, "public @ST@ store;")
F(mdet, "public @PKG@.MapHud hud;")
C(mdet, "public MapDetach(@PR@ pr, @ST@ st, @PKG@.MapHud h) { this.pr = pr; this.store = st; this.hud = h; }")
mrdy.addInterface(pool.get("java.util.function.Consumer"))
C(mrdy, "public MapReady() { }")
mquit.addInterface(pool.get("java.util.function.Consumer"))
C(mquit, "public MapQuit() { }")
mtap.addInterface(pool.get(T["PPW"]))
C(mtap, "public MapTap() { }")

# ---- MapProbe: the state
for f in ("public static volatile java.util.concurrent.ScheduledExecutorService EXEC;",
          "public static final Object LOCK = new Object();",
          "public static final java.util.concurrent.ConcurrentHashMap SESS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentLinkedQueue REQ = new java.util.concurrent.ConcurrentLinkedQueue();",
          "public static final java.util.concurrent.ConcurrentHashMap P3ARM = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap DELIVERED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LASTWORLD = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.HashMap ASSETS = new java.util.HashMap();",
          "public static final java.util.IdentityHashMap ENC = new java.util.IdentityHashMap();",
          "public static @PKG@.MapAsset[] GEN = new @PKG@.MapAsset[13];",
          "public static @PKG@.MapAsset[] TESTA = new @PKG@.MapAsset[4];",
          "public static volatile java.util.concurrent.ScheduledFuture TICKER;",
          "public static volatile int TAPS;",
          "public static volatile @PF@ TAPF;",
          "public static final java.util.concurrent.atomic.AtomicLong TAPERR = new java.util.concurrent.atomic.AtomicLong();",
          "public static long TICKS;",
          "public static final String[] STEPS = %s;" % jarr(MAP_STEPS),
          "public static final String[] LINES = %s;" % jarr(MAP_LINES),
          "public static final String[] HELP = %s;" % jarr(MAP_HELP)):
    F(mprobe, f)
M(mprobe, r"""
public static void say(@PR@ pr, String s) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(mprobe, r"""
public static String secs(long ms) {
  long m = ms < 0L ? 0L : ms;
  return (m / 1000L) + "." + ((m % 1000L) / 100L);
}""")
M(mprobe, r"""
public static String ms(long ns) {
  long n = ns < 0L ? 0L : ns;
  return (n / 1000000L) + "." + ((n / 100000L) % 10L);
}""")
M(mprobe, r"""
public static String modeName(int m) {
  if (m == 1) return "P1a";
  if (m == 2) return "P1b";
  if (m == 3) return "P2";
  if (m == 4) return "P2 sharp";
  if (m == 5) return "P3";
  return "none";
}""")
M(mprobe, r"""
public static java.util.HashSet delivered(java.util.UUID u) {
  java.util.HashSet d = (java.util.HashSet) DELIVERED.get(u);
  if (d == null) { d = new java.util.HashSet(); DELIVERED.put(u, d); }
  return d;
}""")
# one PNG -> its asset: the name carries the content hash (sha256, the engine's CommonAsset.hash), so the same picture is ONE asset for
# every player and a changed picture is a new name (no client cache can show an old one)
M(mprobe, r"""
public static @PKG@.MapAsset asset(String kind, byte[] png) {
  if (png == null) return null;
  String hash = @CMA@.hash(png);
  String name = (kind.equals("mask") ? "@QMDIR@@QMPRE@" : "@QADIR@" + kind + "-") + hash.substring(0, 16) + ".png";
  @PKG@.MapAsset a = (@PKG@.MapAsset) ASSETS.get(name);
  if (a != null) return a;
  if (ASSETS.size() > 4096) ASSETS.clear();
  a = new @PKG@.MapAsset(name, hash, png);
  ASSETS.put(name, a);
  return a;
}""")
M(mprobe, "public static String maskRel(@PKG@.MapAsset a) { return a.getName().substring(@QMLEN@); }")
# one picture to ONE player: AssetInitialize + AssetPart(s) + AssetFinalize in one write (CommonAssetModule.sendAsset's sequence,
# to this player instead of a broadcast); force = also when this connection already got it (P3 re-send); returns the protocol bytes
# written, 0 = not sent (already delivered)
M(mprobe, r"""
public static int send(@PKG@.MapSess s, @PKG@.MapAsset a, boolean force) {
  if (s == null || a == null || s.pr == null) return 0;
  java.util.HashSet d = delivered(s.uuid);
  if (!force && d.contains(a.getName())) { s.cachedHits = s.cachedHits + 1; return 0; }
  byte[] b = a.bytes;
  int parts = (b.length + @QPART@ - 1) / @QPART@;
  if (parts < 1) parts = 1;
  @TCP@[] ps = new @TCP@[parts + 2];
  @AINI@ ai = new @AINI@((com.hypixel.hytale.protocol.Asset) a.toPacket(), b.length);
  ps[0] = ai;
  int bytes = ai.computeSize();
  for (int i = 0; i < parts; i++) {
    int off = i * @QPART@;
    int len = Math.min(@QPART@, b.length - off);
    if (len < 0) len = 0;
    byte[] part = new byte[len];
    System.arraycopy(b, off, part, 0, len);
    @APRT@ ap = new @APRT@(part);
    ps[1 + i] = ap;
    bytes = bytes + ap.computeSize();
  }
  @AFIN@ af = new @AFIN@();
  ps[parts + 1] = af;
  bytes = bytes + af.computeSize();
  s.pr.getPacketHandler().write(ps);
  d.add(a.getName());
  s.assets = s.assets + 1;
  s.assetPackets = s.assetPackets + parts + 2;
  s.assetBytes = s.assetBytes + (long) bytes;
  return bytes;
}""")
M(mprobe, r"""
public static int rebuild(@PKG@.MapSess s) {
  @ARB@ r = new @ARB@();
  s.pr.getPacketHandler().writeNoCache(r);
  s.rebuilds = s.rebuilds + 1;
  return r.computeSize();
}""")
M(mprobe, r"""
public static @ANC@ anchor(int l, int t, int w, int h) {
  @ANC@ a = new @ANC@();
  a.setLeft(@VAL@.of(Integer.valueOf(l)));
  a.setTop(@VAL@.of(Integer.valueOf(t)));
  a.setWidth(@VAL@.of(Integer.valueOf(w)));
  a.setHeight(@VAL@.of(Integer.valueOf(h)));
  return a;
}""")
# the pictures this mod makes, once per server (0 mask, 1 ring, 2-9 arrows N..NW, 10 P1a, 11 P1b, 12 P3)
M(mprobe, r"""
public static @PKG@.MapAsset gen(int which) {
  @PKG@.MapAsset a = GEN[which];
  if (a != null) return a;
  long t0 = System.nanoTime();
  @MIM@ m = null;
  String kind = "";
  if (which == 0) { m = @PKG@.MapPng.mask(@QCLIP@); kind = "mask"; }
  else if (which == 1) { m = @PKG@.MapPng.ring(@QRING@); kind = "ring"; }
  else if (which < 10) { m = @PKG@.MapPng.arrow(which - 2); kind = "arrow" + (which - 2); }
  else { m = @PKG@.MapPng.picture(which - 10); kind = which == 10 ? "p1a" : (which == 11 ? "p1b" : "p3"); }
  a = asset(kind, @PKG@.MapPng.fromMapImage(m, 1));
  if (a != null) { a.madeNs = System.nanoTime() - t0; a.w = m.width; a.h = m.height; }
  GEN[which] = a;
  return a;
}""")
M(mprobe, r"""
public static @PKG@.MapAsset testAsset(int parity, boolean sharp) {
  int k = parity + (sharp ? 2 : 0);
  @PKG@.MapAsset a = TESTA[k];
  if (a != null) return a;
  a = asset(sharp ? "xs" : "x", @PKG@.MapPng.fromMapImage(@PKG@.MapPng.testTile(parity), sharp ? @QTILE@ / 16 : 1));
  TESTA[k] = a;
  return a;
}""")
M(mprobe, r"""
public static String testPath(@PKG@.MapSess s, int parity) {
  @PKG@.MapAsset a = testAsset(parity, s.sharp);
  send(s, a, false);
  return a.getName();
}""")
# a map tile's picture path: one PNG per MapImage object and mode (ENC, identity - shared by every player), sent to this player once.
# null = out of this tick's encode budget (s.more: the next tick tries again) or a picture the encoder refuses (remembered as "")
M(mprobe, r"""
public static String tilePath(@PKG@.MapSess s, @MIM@ m, int[] budget) {
  int k = s.sharp ? 1 : 0;
  String[] e = (String[]) ENC.get(m);
  if (e != null && e[k] != null) {
    if (e[k].length() == 0) return null;
    @PKG@.MapAsset a0 = (@PKG@.MapAsset) ASSETS.get(e[k]);
    if (a0 != null) { send(s, a0, false); return a0.getName(); }
  }
  if (budget[0] <= 0) { s.more = true; return null; }
  budget[0] = budget[0] - 1;
  long t0 = System.nanoTime();
  byte[] png = @PKG@.MapPng.fromMapImage(m, s.sharp ? @PKG@.MapPng.sharpScale(m, @QTILE@) : 1);
  s.encNs = s.encNs + (System.nanoTime() - t0);
  s.encodes = s.encodes + 1;
  if (e == null) {
    if (ENC.size() > 8192) ENC.clear();
    e = new String[2];
    ENC.put(m, e);
  }
  if (png == null) { e[k] = ""; s.badImages = s.badImages + 1; return null; }
  s.encBytes = s.encBytes + (long) png.length;
  @PKG@.MapAsset a = asset(s.sharp ? "ts" : "t", png);
  e[k] = a.getName();
  send(s, a, false);
  return a.getName();
}""")
# the picture for window chunk (cx, cz) in slot sl: the tap's map piece for this player (1), else the engine's shared tile cache (2:
# getImageIfInMemory - a ConcurrentHashMap read, never a generation), else the test pattern (0); an unchanged image keeps its path
M(mprobe, r"""
public static String pick(@PKG@.MapSess s, int cx, int cz, int sl, int[] budget) {
  long k = @PKG@.MapGeo.key(cx, cz);
  @MIM@ m = null;
  int src = 0;
  Object o = s.tiles.get(Long.valueOf(k));
  if (o != null) { m = (@MIM@) o; src = 1; }
  else {
    try {
      @WMM@ w = s.world == null ? null : s.world.getWorldMapManager();
      if (w != null) m = w.getImageIfInMemory(cx, cz);
    } catch (Throwable t) { m = null; }
    if (m != null) src = 2;
  }
  if (m != null && s.slotImg[sl] == m && s.slotKey[sl] == k && s.slotPath[sl] != null) { s.slotSrc[sl] = src; return s.slotPath[sl]; }
  String p = m == null ? null : tilePath(s, m, budget);
  if (p == null) {
    p = testPath(s, Math.floorMod(cx + cz, 2));
    m = null;
    src = 0;
  }
  s.slotImg[sl] = m;
  s.slotSrc[sl] = src;
  return p;
}""")
# the 81 window chunks around (ccx, ccz) -> their ring-buffer slots: a slot whose chunk changed (it just entered the window) gets its
# Anchor + AssetPath, a slot whose picture changed gets its AssetPath; reanchor = after a re-base every slot's Anchor. b == null =
# the first build (the document carries them). Returns the slots that changed.
M(mprobe, r"""
public static int assign(@PKG@.MapSess s, @UCB@ b, boolean reanchor, int[] budget) {
  int changed = 0;
  int sm = 0;
  int sc = 0;
  int st = 0;
  for (int dz = -4; dz <= 4; dz++) {
    for (int dx = -4; dx <= 4; dx++) {
      int cx = s.ccx + dx;
      int cz = s.ccz + dz;
      int sl = @PKG@.MapGeo.slot(cx, cz);
      long k = @PKG@.MapGeo.key(cx, cz);
      boolean moved = s.slotKey[sl] != k;
      String p = pick(s, cx, cz, sl, budget);
      if (b != null && (moved || reanchor)) b.setObject("#@QMT@" + sl + ".Anchor", anchor(@PKG@.MapGeo.tilePos(cx, s.bx), @PKG@.MapGeo.tilePos(cz, s.bz), @QTILE@, @QTILE@));
      if (moved || !p.equals(s.slotPath[sl])) {
        if (b != null) b.set("#@QMT@" + sl + ".AssetPath", p);
        changed = changed + 1;
      }
      s.slotKey[sl] = k;
      s.slotPath[sl] = p;
      int src = s.slotSrc[sl];
      if (src == 1) sm = sm + 1; else if (src == 2) sc = sc + 1; else st = st + 1;
    }
  }
  s.srcMap = sm;
  s.srcCache = sc;
  s.srcTest = st;
  return changed;
}""")
M(mprobe, r"""
public static String capText(@PKG@.MapSess s) {
  return (s.sharp ? "P2 sharp - map " : "P2 - map ") + s.srcMap + " cache " + s.srcCache + " test " + s.srcTest;
}""")
# the window follows the player: a step into the next chunk changes the 9 slots of the entering column / row (ring buffer: the slot of
# the chunk that left), a diagonal step 17, a jump of 2+ chunks more; leaving the grid Group's 17 positions re-bases it (every Anchor);
# then ONE Anchor for the grid Group, the arrow picture when the heading bucket changed, the caption when the sources changed
M(mprobe, r"""
public static void move(@PKG@.MapSess s, @UCB@ b, double px, double pz, float yaw, int[] budget) {
  int cx = @PKG@.MapGeo.chunkOf(px);
  int cz = @PKG@.MapGeo.chunkOf(pz);
  if (cx != s.ccx || cz != s.ccz) {
    if (Math.abs(cx - s.ccx) > 1 || Math.abs(cz - s.ccz) > 1) s.jumps = s.jumps + 1; else s.swaps = s.swaps + 1;
    s.ccx = cx;
    s.ccz = cz;
  }
  boolean reb = false;
  if (!@PKG@.MapGeo.inGroup(cx, s.bx) || !@PKG@.MapGeo.inGroup(cz, s.bz)) {
    s.bx = @PKG@.MapGeo.base(cx);
    s.bz = @PKG@.MapGeo.base(cz);
    reb = true;
    s.rebases = s.rebases + 1;
  }
  assign(s, b, reb, budget);
  int gl = @PKG@.MapGeo.groupPos(px, s.bx);
  int gt = @PKG@.MapGeo.groupPos(pz, s.bz);
  if (gl != s.gl || gt != s.gt || reb) {
    b.setObject("#@QMGRID@.Anchor", anchor(gl, gt, @QSPAN@ * @QTILE@, @QSPAN@ * @QTILE@));
    s.gl = gl;
    s.gt = gt;
  }
  int ab = @PKG@.MapGeo.bucket(yaw);
  if (ab != s.arrow && s.arrows != null) {
    b.set("#@QMME@.AssetPath", s.arrows[ab]);
    s.arrow = ab;
  }
  String cap = capText(s);
  if (!cap.equals(s.capText)) {
    b.set("#@QMCAP@.Text", cap);
    s.capText = cap;
  }
}""")
M(mprobe, r"""
public static int docBytes(@PKG@.MapHud h) {
  try {
    @UCB@ b = new @UCB@();
    if (h.mode == 3 || h.mode == 4) @PKG@.MapUi.p2(b, h); else @PKG@.MapUi.p1(b, h.pic, h.cap);
    return new @CHP@("@QKEY@", @QZ@, true, b.getCommands()).computeSize();
  } catch (Throwable t) { return -1; }
}""")
# a new HUD for the session (the pictures it names were written before this, on this thread): the old one is ended (the new one has
# the same key, so addCustomHud clears the old document on the client first), the attach goes to the world thread (HudManager)
M(mprobe, r"""
public static boolean attach(@PKG@.MapSess s, @PKG@.MapHud h, @WLD@ w, @ST@ st, long now) {
  @PKG@.MapHud old = s.hud;
  if (old != null && old != h) old.ended = true;
  s.hud = h;
  s.mode = h.mode;
  s.hudAt = now;
  try { w.execute(new @PKG@.MapAttach(s, h, st)); return true; }
  catch (Throwable t) { h.gone = true; @PKG@.ProbeLog.warn("map probe " + s.who + ": could not reach the world thread to show the HUD: " + t); return false; }
}""")
# world thread: register the HUD with the player's HudManager (its own key; SkyyHud's key is never touched) - only if the player is
# still in the world the session started in
M(mprobe, r"""
public static void attachNow(@PKG@.MapSess s, @PKG@.MapHud h, @ST@ st) {
  if (s == null || h == null || h.ended) return;
  try {
    @REF@ ref = s.pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != st) { h.gone = true; return; }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { h.gone = true; return; }
    p.getHudManager().addCustomHud(s.pr, h);
    h.attached = true;
  } catch (Throwable t) { h.gone = true; @PKG@.ProbeLog.warn("map probe " + s.who + ": showing the HUD failed: " + t); }
}""")
# world thread: remove OUR hud object only (never another key, never a newer probe HUD); a player who left that world needs nothing
# (the engine's resetHud already removed every registered HUD there)
M(mprobe, r"""
public static void detachNow(@PR@ pr, @ST@ st, @PKG@.MapHud h) {
  try {
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid() || ref.getStore() != st) return;
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    @HM@ hm = p.getHudManager();
    if (hm.getCustomHud("@QKEY@") == h) hm.removeCustomHud(pr, "@QKEY@");
  } catch (Throwable t) { @PKG@.ProbeLog.warn("map probe: removing the HUD failed: " + t); }
}""")
# world thread, one task per world per tick: the positions / headings of that world's P2 players (cheap component reads, no map work)
M(mprobe, r"""
public static void readNow(java.util.ArrayList list) {
  long now = System.currentTimeMillis();
  for (int i = 0; i < list.size(); i++) {
    @PKG@.MapSess s = (@PKG@.MapSess) list.get(i);
    try {
      @REF@ ref = s.pr.getReference();
      if (ref == null || !ref.isValid()) s.posState = 2;
      else if (ref.getStore() != s.store) s.posState = 1;
      else {
        @ST@ st = ref.getStore();
        @TRC@ tc = (@TRC@) st.getComponent(ref, @TRC@.getComponentType());
        if (tc != null) {
          org.joml.Vector3d v = tc.getPosition();
          float yaw = tc.getRotation().yaw();
          @HRT@ hr = (@HRT@) st.getComponent(ref, @HRT@.getComponentType());
          if (hr != null) yaw = hr.getRotation().yaw();
          s.px = v.x;
          s.pz = v.z;
          s.yaw = yaw;
          s.posAt = now;
          s.posSeq = s.posSeq + 1L;
        }
      }
    } catch (Throwable t) { }
    s.readPending = false;
  }
}""")
M(mprobe, "public static void noteGone(@PKG@.MapHud h) { if (h != null) h.gone = true; }")
M(mprobe, r"""
public static void recountTaps() {
  int n = 0;
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) { if (((@PKG@.MapSess) it.next()).wants) n = n + 1; }
  TAPS = n;
}""")
# a finished session lets go of its world / store / pictures / queued packets (the 0.3 review lesson: no unloaded world kept alive)
M(mprobe, r"""
public static void release(@PKG@.MapSess s) {
  s.world = null;
  s.store = null;
  s.hud = null;
  s.capture = false;
  s.wants = false;
  s.tiles.clear();
  s.q.clear();
  s.qn.set(0);
  for (int i = 0; i < 81; i++) s.slotImg[i] = null;
}""")
M(mprobe, r"""
public static void resetStats(@PKG@.MapSess s, long now) {
  s.upd = 0L; s.chunks = 0L; s.nulls = 0L; s.imgs = 0L; s.mAdd = 0L; s.mRem = 0L; s.bytes = 0L; s.clears = 0L;
  s.tickMax = 0; s.minW = 0; s.maxW = 0; s.minPal = 0; s.maxPal = 0; s.bitsMask = 0;
  s.drop0 = s.dropped.get();
  s.tapStart = now;
  s.tapEnd = now + @QTAPMS@L;
}""")
M(mprobe, r"""
public static void noteImage(@PKG@.MapSess s, @MIM@ m) {
  int w = m.width;
  int p = m.palette == null ? 0 : m.palette.length;
  int b = m.bitsPerIndex & 255;
  if (s.minW == 0 || w < s.minW) s.minW = w;
  if (w > s.maxW) s.maxW = w;
  if (s.minPal == 0 || p < s.minPal) s.minPal = p;
  if (p > s.maxPal) s.maxPal = p;
  if (b < 31) s.bitsMask = s.bitsMask | (1 << b);
}""")
M(mprobe, r"""
public static String bitsText(int mask) {
  StringBuilder sb = new StringBuilder();
  for (int b = 0; b < 31; b++) {
    if ((mask & (1 << b)) != 0) { if (sb.length() > 0) sb.append('/'); sb.append(b); }
  }
  return sb.length() == 0 ? "-" : sb.toString();
}""")
M(mprobe, r"""
public static String tapLine(@PKG@.MapSess s, String why, long now) {
  StringBuilder sb = new StringBuilder();
  if (s.tapMode == 5) sb.append("P5 world ").append(s.seg).append(" of @QSEGS@ (").append(s.tapInfo).append(")");
  else sb.append("P4 (").append(s.tapInfo).append(")");
  sb.append(" ").append(secs(now - s.tapStart)).append(" s: ");
  sb.append(s.upd).append(" UpdateWorldMap (max ").append(s.tickMax).append(" in one 0.25 s), ");
  sb.append(s.chunks).append(" chunks (").append(s.nulls).append(" null = unloads), ");
  sb.append(s.mAdd).append(" markers added / ").append(s.mRem).append(" removed, ");
  sb.append(s.clears).append(" ClearWorldMap, ").append(s.bytes).append(" bytes");
  if (s.imgs > 0L) {
    sb.append("; pictures ").append(s.minW);
    if (s.maxW != s.minW) sb.append("-").append(s.maxW);
    sb.append(" px, ").append(s.minPal).append("-").append(s.maxPal).append(" colours, ").append(bitsText(s.bitsMask)).append(" bit");
  }
  long dr = s.dropped.get() - s.drop0;
  if (dr > 0L) sb.append("; ").append(dr).append(" packet(s) not kept (queue full)");
  if (s.upd == 0L) sb.append(" - NO map stream: the map is off here, or all ground around you was already sent (walk onto new ground)");
  if (why != null) sb.append(" - ").append(why);
  return sb.toString();
}""")
# P5: the engine's ClearWorldMap (every world change) closes the world's count and opens the next (named by the ready event)
M(mprobe, r"""
public static void segment(@PKG@.MapSess s, long now) {
  String line = tapLine(s, "the world changed (ClearWorldMap)", now);
  @PKG@.ProbeLog.info(line);
  say(s.pr, line);
  if (s.seg >= @QSEGS@) { s.tapEnd = now; s.p5done = true; return; }
  s.seg = s.seg + 1;
  resetStats(s, now);
  if (s.nextInfo != null) { s.tapInfo = s.nextInfo; s.infoOpen = false; }
  else { s.tapInfo = "the next world"; s.infoOpen = true; }
  s.nextInfo = null;
}""")
M(mprobe, r"""
public static void prune(@PKG@.MapSess s) {
  java.util.Iterator it = s.tiles.keySet().iterator();
  while (it.hasNext()) {
    long k = ((Long) it.next()).longValue();
    int dx = @PKG@.MapGeo.keyX(k) - s.ccx;
    int dz = @PKG@.MapGeo.keyZ(k) - s.ccz;
    if (dx > 16 || dx < -16 || dz > 16 || dz < -16) it.remove();
  }
}""")
# tick thread: what the tap queued for this player since the last tick - the P4 / P5 counts and P2's captured map pieces
M(mprobe, r"""
public static void drain(@PKG@.MapSess s, long now) {
  int n = 0;
  while (true) {
    Object o = s.q.poll();
    if (o == null) break;
    s.qn.decrementAndGet();
    if (o instanceof @UWM@) {
      n = n + 1;
      @UWM@ u = (@UWM@) o;
      s.upd = s.upd + 1L;
      try { s.bytes = s.bytes + (long) u.computeSize(); } catch (Throwable t) { }
      @MCH@[] cs = u.chunks;
      if (cs != null) {
        for (int i = 0; i < cs.length; i++) {
          @MCH@ c = cs[i];
          if (c == null) continue;
          s.chunks = s.chunks + 1L;
          Long key = Long.valueOf(@PKG@.MapGeo.key(c.chunkX, c.chunkZ));
          if (c.image == null) {
            s.nulls = s.nulls + 1L;
            if (s.capture) { s.tiles.remove(key); s.tilesDirty = true; }
          } else {
            s.imgs = s.imgs + 1L;
            noteImage(s, c.image);
            if (s.capture) { s.tiles.put(key, c.image); s.tilesDirty = true; }
          }
        }
      }
      if (u.addedMarkers != null) s.mAdd = s.mAdd + (long) u.addedMarkers.length;
      if (u.removedMarkers != null) s.mRem = s.mRem + (long) u.removedMarkers.length;
    } else if (o instanceof @CWM@) {
      s.clears = s.clears + 1L;
      if (s.capture) { s.tiles.clear(); s.tilesDirty = true; }
      if (s.tapMode == 5 && !s.p5done) {
        if (n > s.tickMax) s.tickMax = n;
        n = 0;
        segment(s, now);
      }
    }
  }
  if (n > s.tickMax) s.tickMax = n;
  if (s.capture && s.tiles.size() > 4096) prune(s);
}""")
M(mprobe, r"""
public static void finishTap(@PKG@.MapSess s, String why, boolean chat, long now) {
  if (s.tapMode == 0) return;
  drain(s, now);
  if (!s.p5done) {
    String line = tapLine(s, why, now);
    @PKG@.ProbeLog.info(line);
    if (chat) say(s.pr, line);
  }
  s.tapMode = 0;
  s.p5done = false;
  s.wants = s.capture;
  recountTaps();
}""")
M(mprobe, r"""
public static void endHud(@PKG@.MapSess s, String why, boolean detach, long now) {
  @PKG@.MapHud h = s.hud;
  if (h == null) return;
  h.ended = true;
  int mode = s.mode;
  s.hud = null;
  s.mode = 0;
  boolean p2 = s.capture;
  s.capture = false;
  s.tiles.clear();
  s.wants = s.tapMode != 0;
  if (detach && s.world != null && s.pr != null) {
    try { s.world.execute(new @PKG@.MapDetach(s.pr, s.store, h)); }
    catch (Throwable t) { @PKG@.ProbeLog.warn("map probe " + s.who + ": could not reach the world thread to remove the HUD: " + t); }
  }
  @PKG@.ProbeLog.info(modeName(mode) + " " + s.who + ": HUD ended (" + why + ") after " + secs(now - s.hudAt) + " s - this session sent " + s.assets + " picture(s) ("
    + s.assetBytes + " bytes in " + s.assetPackets + " packets, " + s.cachedHits + " not sent again), " + s.rebuilds + " rebuild(s), " + s.updates + " HUD update(s) ("
    + s.updateBytes + " bytes)" + (p2 ? ", " + s.pans + " pans, " + s.swaps + " edge swaps, " + s.jumps + " jumps, " + s.rebases + " re-bases, " + s.encodes
    + " tile PNGs encoded in " + ms(s.encNs) + " ms (" + s.encBytes + " bytes)" + (s.badImages > 0 ? ", " + s.badImages + " map pieces refused" : "") : ""));
  recountTaps();
}""")
M(mprobe, r"""
public static void endAll(@PKG@.MapSess s, String why, boolean detach, boolean chat, long now) {
  endHud(s, why, detach, now);
  finishTap(s, why, chat, now);
  SESS.remove(s.uuid, s);
  release(s);
  recountTaps();
}""")
# the session of the request's player (made if needed); a session from another world ends first (the engine reset its HUD there) -
# except P5's counting, which follows the player (its test)
M(mprobe, r"""
public static @PKG@.MapSess session(@PKG@.MapReq r, long now) {
  @PKG@.MapSess s = (@PKG@.MapSess) SESS.get(r.uuid);
  if (s != null && s.store != null && r.store != null && s.store != r.store) {
    if (s.tapMode == 5) endHud(s, "world change", false, now);
    else { endAll(s, "world change", false, true, now); s = null; }
  }
  if (s == null) {
    s = new @PKG@.MapSess();
    s.uuid = r.uuid;
    s.started = now;
    SESS.put(r.uuid, s);
  }
  s.pr = r.pr;
  s.who = r.who;
  s.world = r.world;
  s.store = r.store;
  s.posState = 0;
  if (r.posOk) { s.px = r.px; s.pz = r.pz; s.yaw = r.yaw; s.posAt = now; s.posSeq = s.posSeq + 1L; }
  return s;
}""")
# P1 / P3: ONE picture (made once per server) to this player unless this connection has it, the rebuild when asked, then the box
M(mprobe, r"""
public static void startP1(@PKG@.MapReq r, @PKG@.MapSess s, int which, boolean reb, int mode, String cap, long now) {
  if (s.capture) { s.capture = false; s.tiles.clear(); s.wants = s.tapMode != 0; recountTaps(); }
  long t0 = System.nanoTime();
  @PKG@.MapAsset a = gen(which);
  if (a == null) { say(s.pr, "The probe picture could not be made - see the server log."); @PKG@.ProbeLog.warn("map probe " + s.who + ": picture " + which + " could not be made"); return; }
  int sent = send(s, a, false);
  int rb = reb ? rebuild(s) : 0;
  long t1 = System.nanoTime();
  @PKG@.MapHud h = new @PKG@.MapHud(s.pr, s, mode);
  h.pic = a.getName();
  h.cap = cap;
  int doc = docBytes(h);
  boolean ok = attach(s, h, r.world, r.store, now);
  @PKG@.ProbeLog.info(modeName(mode) + " " + s.who + ": picture " + a.getName() + " (" + a.w + " x " + a.h + ", " + a.bytes.length + " bytes PNG, made in "
    + ms(a.madeNs) + " ms) " + (sent > 0 ? "sent in 3 packets (AssetInitialize + AssetPart + AssetFinalize, " + sent + " bytes)" : "NOT sent again (this connection has it)")
    + (reb ? " + ONE RequestCommonAssetsRebuild (" + rb + " bytes)" : ", no rebuild") + " in " + ms(t1 - t0) + " ms; HUD box " + doc + " bytes (CustomHud key @QKEY@, zOrder @QZ@)"
    + (ok ? " - to the world thread" : " - NOT shown"));
}""")
# P2: the static pictures (mask + ONE rebuild the first time this connection gets it, ring, 8 arrows), the 81 tiles, the minimap HUD
M(mprobe, r"""
public static void startP2(@PKG@.MapReq r, @PKG@.MapSess s, boolean sharp, long now) {
  long t0 = System.nanoTime();
  int a0 = s.assets;
  int k0 = s.assetPackets;
  long b0 = s.assetBytes;
  int e0 = s.encodes;
  long n0 = s.encNs;
  long eb0 = s.encBytes;
  int c0 = s.cachedHits;
  boolean was = s.capture;
  s.sharp = sharp;
  s.capture = true;
  s.wants = true;
  recountTaps();
  if (!was) s.tiles.clear();
  for (int i = 0; i < 81; i++) { s.slotKey[i] = Long.MIN_VALUE; s.slotImg[i] = null; s.slotPath[i] = null; s.slotSrc[i] = 0; }
  s.ccx = @PKG@.MapGeo.chunkOf(s.px);
  s.ccz = @PKG@.MapGeo.chunkOf(s.pz);
  s.bx = @PKG@.MapGeo.base(s.ccx);
  s.bz = @PKG@.MapGeo.base(s.ccz);
  s.pans = 0; s.swaps = 0; s.jumps = 0; s.rebases = 0;
  @PKG@.MapAsset mask = gen(0);
  @PKG@.MapAsset ring = gen(1);
  boolean firstMask = !delivered(s.uuid).contains(mask.getName());
  send(s, mask, false);
  send(s, ring, false);
  s.arrows = new String[8];
  for (int i = 0; i < 8; i++) {
    @PKG@.MapAsset ar = gen(2 + i);
    send(s, ar, false);
    s.arrows[i] = ar.getName();
  }
  int[] budget = new int[] { @QENCF@ };
  s.more = false;
  assign(s, null, true, budget);
  int rb = firstMask ? rebuild(s) : 0;
  s.gl = @PKG@.MapGeo.groupPos(s.px, s.bx);
  s.gt = @PKG@.MapGeo.groupPos(s.pz, s.bz);
  s.arrow = @PKG@.MapGeo.bucket(s.yaw);
  s.posUsed = s.posAt;
  s.posUsedSeq = s.posSeq;
  @PKG@.MapHud h = new @PKG@.MapHud(s.pr, s, sharp ? 4 : 3);
  h.mask = maskRel(mask);
  h.ring = ring.getName();
  h.me = s.arrows[s.arrow];
  h.gl = s.gl;
  h.gt = s.gt;
  for (int sl = 0; sl < 81; sl++) {
    h.tl[sl] = @PKG@.MapGeo.tilePos(@PKG@.MapGeo.keyX(s.slotKey[sl]), s.bx);
    h.tt[sl] = @PKG@.MapGeo.tilePos(@PKG@.MapGeo.keyZ(s.slotKey[sl]), s.bz);
    h.tp[sl] = s.slotPath[sl];
  }
  h.cap = capText(s);
  s.capText = h.cap;
  int doc = docBytes(h);
  boolean ok = attach(s, h, r.world, r.store, now);
  long t1 = System.nanoTime();
  @PKG@.ProbeLog.info(modeName(h.mode) + " " + s.who + ": chunk " + s.ccx + " " + s.ccz + ", 81 tiles (" + s.srcMap + " from the map stream, " + s.srcCache + " from the shared map cache, "
    + s.srcTest + " test pattern); " + (s.encodes - e0) + " tile PNGs encoded in " + ms(s.encNs - n0) + " ms (" + (s.encBytes - eb0) + " bytes); " + (s.assets - a0)
    + " pictures sent in " + (s.assetPackets - k0) + " packets (" + (s.assetBytes - b0) + " bytes), " + (s.cachedHits - c0) + " not sent again"
    + (firstMask ? ", ONE RequestCommonAssetsRebuild (" + rb + " bytes: the first mask of this connection)" : ", no rebuild")
    + "; HUD " + doc + " bytes; " + ms(t1 - t0) + " ms on the tick thread" + (ok ? " - to the world thread" : " - NOT shown"));
}""")
M(mprobe, r"""
public static void armP3(@PKG@.MapReq r, @PKG@.MapSess s, boolean resend, long now) {
  @PKG@.MapP3 p = new @PKG@.MapP3();
  p.uuid = r.uuid;
  p.who = r.who;
  p.resend = resend;
  p.armedAt = now;
  p.pr = r.pr;
  P3ARM.put(r.uuid, p);
  startP1(r, s, 12, false, 5, %s, now);
  @PKG@.ProbeLog.info("P3 " + s.who + ": armed (re-send " + (resend ? "on" : "off") + ") - the box comes back after the next world change or reconnect");
}""" % jl(MAP_CAPS["p3"]))
M(mprobe, r"""
public static void showP3(@PKG@.MapP3 p, long now) {
  if (p.pr == null || p.world == null || p.store == null) return;
  @PKG@.MapReq r = new @PKG@.MapReq();
  r.kind = "p3show";
  r.pr = p.pr;
  r.uuid = p.uuid;
  r.who = p.who;
  r.world = p.world;
  r.store = p.store;
  r.at = now;
  p.world = null;
  p.store = null;
  @PKG@.MapSess s = session(r, now);
  @PKG@.MapAsset a = gen(12);
  boolean had = delivered(s.uuid).contains(a.getName());
  int sent = p.resend ? send(s, a, true) : 0;
  @PKG@.MapHud h = new @PKG@.MapHud(s.pr, s, 5);
  h.pic = a.getName();
  h.cap = p.resend ? %s : %s;
  boolean ok = attach(s, h, r.world, r.store, now);
  p.shows = p.shows + 1;
  String what = p.sawQuit ? "reconnect" : "world change";
  say(s.pr, "P3: after your " + what + " the picture was " + (p.resend ? "SENT AGAIN first" : "NOT sent again") + " - do you see it in the box top-right? Tell Claude, then /skyprobe map off.");
  @PKG@.ProbeLog.info("P3 " + s.who + ": shown again after a " + what + " (" + secs(now - p.armedAt) + " s after arming, show " + p.shows + "), picture " + a.getName()
    + (p.resend ? " sent again (" + sent + " bytes)" : " NOT sent again") + "; the server's list for this connection " + (had ? "had" : "did not have") + " it" + (ok ? "" : " - NOT shown"));
  p.sawQuit = false;
}""" % (jl(MAP_CAPS["p3re"]), jl(MAP_CAPS["p3no"])))
M(mprobe, r"""
public static void startCount(@PKG@.MapReq r, @PKG@.MapSess s, int mode, long now) {
  if (s.tapMode != 0) finishTap(s, "restarted", true, now);
  drain(s, now);
  s.tapMode = mode;
  s.seg = 1;
  s.p5done = false;
  s.nextInfo = null;
  s.infoOpen = false;
  resetStats(s, now);
  s.tapInfo = r.info == null ? "world ?" : r.info;
  s.wants = true;
  recountTaps();
  @PKG@.ProbeLog.info((mode == 5 ? "P5 " : "P4 ") + s.who + ": counting the map stream for 60 s (" + s.tapInfo + ")");
}""")
M(mprobe, r"""
public static String statusText(@PKG@.MapSess s, @PKG@.MapP3 p, java.util.UUID u, long now) {
  StringBuilder sb = new StringBuilder("Map probes: ");
  if (s == null || (s.hud == null && s.tapMode == 0)) sb.append("no HUD probe, no counting");
  else {
    sb.append("HUD ").append(s.hud == null ? "none" : modeName(s.mode) + (s.hud.attached ? "" : " (being shown)"));
    if (s.capture) sb.append(" - map ").append(s.srcMap).append(" cache ").append(s.srcCache).append(" test ").append(s.srcTest).append(", ").append(s.swaps).append(" edge swaps, ").append(s.rebases).append(" re-bases, ").append(s.pans).append(" pans");
    sb.append("; pictures sent ").append(s.assets).append(" (").append(s.assetBytes).append(" bytes), ").append(s.rebuilds).append(" rebuild(s), ").append(s.updates).append(" HUD updates");
    if (s.tapMode != 0) sb.append("; ").append(s.tapMode == 5 ? "P5 world " + s.seg : "P4").append(" ").append(secs(s.tapEnd - now)).append(" s left: ").append(s.upd).append(" UpdateWorldMap, ").append(s.chunks).append(" chunks");
  }
  sb.append("; P3 ").append(p == null ? "off" : "armed (re-send " + (p.resend ? "on" : "off") + ")");
  java.util.HashSet d = (java.util.HashSet) DELIVERED.get(u);
  sb.append("; this connection got ").append(d == null ? 0 : d.size()).append(" picture(s)");
  long te = TAPERR.get();
  if (te > 0L) sb.append("; tap errors ").append(te);
  return sb.toString();
}""")
# one request (tick thread)
M(mprobe, r"""
public static void handle(@PKG@.MapReq r, long now) {
  String k = r.kind;
  if (k == null || r.uuid == null) return;
  @PKG@.MapSess s = (@PKG@.MapSess) SESS.get(r.uuid);
  if (k.equals("quit")) {
    if (s != null) endAll(s, "disconnect", false, false, now);
    DELIVERED.remove(r.uuid);
    LASTWORLD.remove(r.uuid);
    @PKG@.MapP3 p = (@PKG@.MapP3) P3ARM.get(r.uuid);
    if (p != null) { p.sawQuit = true; p.dueAt = 0L; p.world = null; p.store = null; }
    return;
  }
  if (k.equals("ready")) {
    Object last = LASTWORLD.put(r.uuid, r.wname);
    if (last != null && !last.equals(r.wname)) DELIVERED.remove(r.uuid);
    if (s != null && s.store != null && r.store != null && s.store != r.store) {
      if (s.tapMode == 5) {
        endHud(s, "world change", false, now);
        if (s.infoOpen) { s.tapInfo = r.info; s.infoOpen = false; } else s.nextInfo = r.info;
        s.world = r.world;
        s.store = r.store;
        s.pr = r.pr;
        s.posState = 0;
      } else endAll(s, "world change", false, true, now);
    }
    @PKG@.MapP3 p = (@PKG@.MapP3) P3ARM.get(r.uuid);
    if (p != null) {
      if (now - p.armedAt > @QPTTL@L) { P3ARM.remove(r.uuid); @PKG@.ProbeLog.info("P3 " + p.who + ": disarmed after 10 minutes"); }
      else { p.dueAt = now + @QRDY@L; p.pr = r.pr; p.world = r.world; p.store = r.store; }
    }
    return;
  }
  if (k.equals("off")) {
    if (s != null) endAll(s, "off", true, true, now);
    if (P3ARM.remove(r.uuid) != null) @PKG@.ProbeLog.info("P3 " + r.who + ": disarmed (off)");
    @PKG@.ProbeLog.info("map probes off for " + r.who);
    return;
  }
  if (k.equals("status")) { say(r.pr, statusText(s, (@PKG@.MapP3) P3ARM.get(r.uuid), r.uuid, now)); return; }
  if (r.wname != null) LASTWORLD.put(r.uuid, r.wname);   // the world the pictures go to (a later ready event in another world clears the list)
  s = session(r, now);
  if (k.equals("p1a")) startP1(r, s, 10, false, 1, %s, now);
  else if (k.equals("p1b")) startP1(r, s, 11, true, 2, %s, now);
  else if (k.equals("p2")) startP2(r, s, false, now);
  else if (k.equals("p2sharp")) startP2(r, s, true, now);
  else if (k.equals("p3")) armP3(r, s, false, now);
  else if (k.equals("p3resend")) armP3(r, s, true, now);
  else if (k.equals("p4")) startCount(r, s, 4, now);
  else if (k.equals("p5")) startCount(r, s, 5, now);
}""" % (jl(MAP_CAPS["p1a"]), jl(MAP_CAPS["p1b"])))
M(mprobe, r"""
public static void pan(@PKG@.MapSess s, @PKG@.MapHud h, long now) {
  @UCB@ b = new @UCB@();
  int[] budget = new int[] { @QENCT@ };
  s.more = false;
  s.tilesDirty = false;
  long seq = s.posSeq;
  move(s, b, s.px, s.pz, s.yaw, budget);
  s.posUsed = s.posAt;
  s.posUsedSeq = seq;
  @CUC@[] cmds = b.getCommands();
  if (cmds.length == 0) return;
  if (h.push(b)) {
    s.updates = s.updates + 1;
    s.pans = s.pans + 1;
    try { s.updateBytes = s.updateBytes + (long) new @CHP@("@QKEY@", @QZ@, false, cmds).computeSize(); } catch (Throwable t) { }
  }
}""")
# one session per tick: the 60 s timer, a HUD the engine removed / a player who left the world, P2's pan from the last read + the next
# read (grouped per world by tick0), and a session with nothing left leaves SESS
M(mprobe, r"""
public static void step(@PKG@.MapSess s, long now, java.util.HashMap reads) {
  if (s.tapMode != 0 && now >= s.tapEnd) finishTap(s, null, true, now);
  @PKG@.MapHud h = s.hud;
  if (h != null) {
    if (h.gone) endHud(s, h.attached ? "the engine removed it: a world change or another HUD with the same key" : "the player was not in that world any more when it was to be shown", false, now);
    else if (s.posState == 1) { endAll(s, "world change", false, true, now); return; }
    else if (s.posState == 2) { endAll(s, "the player left", false, false, now); return; }
    else if ((s.mode == 3 || s.mode == 4) && h.attached && !s.readPending) {
      if (s.posSeq != s.posUsedSeq || s.more || s.tilesDirty) pan(s, h, now);
      s.readPending = true;
      java.util.ArrayList l = (java.util.ArrayList) reads.get(s.world);
      if (l == null) { l = new java.util.ArrayList(); reads.put(s.world, l); }
      l.add(s);
    }
  }
  if (s.hud == null && s.tapMode == 0) { SESS.remove(s.uuid, s); release(s); recountTaps(); }
}""")
M(mprobe, r"""
public static void tick0() {
  long now = System.currentTimeMillis();
  TICKS = TICKS + 1L;
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MapSess s = (@PKG@.MapSess) it.next();
    try { drain(s, now); } catch (Throwable t) { @PKG@.ProbeLog.warn("map probes: counting failed for " + s.who + ": " + t); }
  }
  while (true) {
    Object o = REQ.poll();
    if (o == null) break;
    try { handle((@PKG@.MapReq) o, now); } catch (Throwable t) { @PKG@.ProbeLog.warn("map probes: a request failed: " + t); }
  }
  it = P3ARM.values().iterator();
  while (it.hasNext()) {
    @PKG@.MapP3 p = (@PKG@.MapP3) it.next();
    if (p.dueAt != 0L && now >= p.dueAt) {
      p.dueAt = 0L;
      try { showP3(p, now); } catch (Throwable t) { @PKG@.ProbeLog.warn("map probes: P3 could not be shown again: " + t); }
    }
  }
  java.util.HashMap reads = new java.util.HashMap();
  it = SESS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MapSess s = (@PKG@.MapSess) it.next();
    try { step(s, now, reads); } catch (Throwable t) { @PKG@.ProbeLog.warn("map probes: the tick failed for " + s.who + ": " + t); }
  }
  java.util.Iterator rt = reads.entrySet().iterator();
  while (rt.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) rt.next();
    @WLD@ w = (@WLD@) e.getKey();
    java.util.ArrayList l = (java.util.ArrayList) e.getValue();
    try { w.execute(new @PKG@.MapRead(l)); }
    catch (Throwable t) { for (int i = 0; i < l.size(); i++) ((@PKG@.MapSess) l.get(i)).readPending = false; }
  }
}""")
M(mprobe, r"""
public static boolean idle() {
  if (!REQ.isEmpty() || !SESS.isEmpty()) return false;
  java.util.Iterator it = P3ARM.values().iterator();
  while (it.hasNext()) { if (((@PKG@.MapP3) it.next()).dueAt != 0L) return false; }
  return true;
}""")
# the tick runs only while something is on: started by a request, cancelled when nothing is left (off by default). Both under the
# class monitor (not LOCK), so a request and the tick's own stop never miss each other
M(mprobe, r"""
public static synchronized boolean stopIfIdle() {
  if (!idle()) return false;
  try { if (TICKER != null) TICKER.cancel(false); } catch (Throwable t) { }
  TICKER = null;
  return true;
}""")
M(mprobe, r"""
public static void tick() {
  synchronized (LOCK) { tick0(); }
  stopIfIdle();
}""")
M(mprobe, r"""
public static synchronized void ensureTick() {
  if (TICKER != null) return;
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e == null) { @PKG@.ProbeLog.warn("map probes: no scheduler - the probes cannot run"); return; }
  try { TICKER = e.scheduleAtFixedRate(new @PKG@.MapTick(), 0L, @QTICK@L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("map probes: could not start the 0.25 s tick: " + t); }
}""")
M(mprobe, r"""
public static void submit(@PKG@.MapReq r) {
  REQ.add(r);
  ensureTick();
}""")
# THE TAP (any thread that writes a packet - the WorldMapManager's thread for the vanilla stream, BetterMap's threads for its own):
# references and counts only - one volatile read when nothing asked for packets, never a lock, never a throw, never reads the packet
M(mprobe, r"""
public static void tap(@PR@ pr, Object p) {
  if (TAPS == 0 || pr == null || p == null) return;
  if (!(p instanceof @UWM@) && !(p instanceof @CWM@)) return;
  @PKG@.MapSess s = (@PKG@.MapSess) SESS.get(pr.getUuid());
  if (s == null || !s.wants) return;
  s.seen.incrementAndGet();
  if (s.qn.incrementAndGet() > @QMAX@) { s.qn.decrementAndGet(); s.dropped.incrementAndGet(); return; }
  s.q.add(p);
}""")
M(mprobe, r"""
public static boolean interested(java.util.UUID u) {
  return u != null && (SESS.containsKey(u) || P3ARM.containsKey(u) || DELIVERED.containsKey(u) || LASTWORLD.containsKey(u));
}""")
# world thread (commands, the ready event): the player's position + heading (HeadRotation when there is one) - cheap reads only
M(mprobe, r"""
public static void readPos(@PKG@.MapReq r, @ST@ st, @REF@ ref) {
  try {
    if (st == null || ref == null) return;
    @TRC@ tc = (@TRC@) st.getComponent(ref, @TRC@.getComponentType());
    if (tc == null) return;
    org.joml.Vector3d v = tc.getPosition();
    float yaw = tc.getRotation().yaw();
    try {
      @HRT@ hr = (@HRT@) st.getComponent(ref, @HRT@.getComponentType());
      if (hr != null) yaw = hr.getRotation().yaw();
    } catch (Throwable t) { }
    r.px = v.x;
    r.pz = v.z;
    r.yaw = yaw;
    r.posOk = true;
  } catch (Throwable t) { }
}""")
M(mprobe, r"""
public static String worldInfo(@WLD@ w) {
  if (w == null) return "world ?";
  String n = "?";
  String on = "?";
  String gen = "?";
  String sc = "?";
  try { n = w.getName(); } catch (Throwable t) { }
  try {
    @WMM@ m = w.getWorldMapManager();
    if (m == null) on = "no map manager";
    else {
      on = m.isWorldMapEnabled() ? "on" : "OFF";
      Object g = m.getGenerator();
      gen = g == null ? "no generator" : g.getClass().getSimpleName();
      sc = String.valueOf(m.getWorldMapSettings().getImageScale());
    }
  } catch (Throwable t) { }
  return "world '" + n + "', map " + on + ", " + gen + ", image scale " + sc;
}""")
M(mprobe, r"""
public static @PKG@.MapReq req(String kind, @PR@ pr, @WLD@ w, @ST@ st, @REF@ ref) {
  @PKG@.MapReq r = new @PKG@.MapReq();
  r.kind = kind;
  r.pr = pr;
  r.uuid = pr.getUuid();
  r.who = pr.getUsername();
  r.world = w;
  r.store = st;
  r.at = System.currentTimeMillis();
  try { r.wname = w == null ? "?" : w.getName(); } catch (Throwable t) { r.wname = "?"; }
  readPos(r, st, ref);
  r.info = worldInfo(w);
  return r;
}""")
M(mprobe, r"""
public static int stepIndex(String t) {
  for (int i = 0; i < STEPS.length; i++) { if (STEPS[i].equals(t)) return i; }
  return -1;
}""")
M(mprobe, r"""
public static void help(@PR@ pr) {
  for (int i = 0; i < HELP.length; i++) say(pr, HELP[i]);
}""")
# /skyprobe map <step> (world thread): read the player's position / world, print the step's ONE line, queue the request
M(mprobe, r"""
public static void command(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ world, String step) {
  String t = step == null ? "" : step.trim().toLowerCase(java.util.Locale.ROOT);
  int i = stepIndex(t);
  if (i < 0) { say(pr, "No map probe '" + t + "'. %s"); return; }
  @PKG@.MapReq q = req(t, pr, world, store, ref);
  if (LINES[i].length() > 0) say(pr, LINES[i]);
  submit(q);
}""" % SUI.java_escape(MAP_USAGE))
# PlayerReadyEvent (every world change and every join; world thread): only for a player with a map probe, P3 or pictures sent
M(mprobe, r"""
public static void ready(Object ev) {
  @PRE@ e = (@PRE@) ev;
  @REF@ r = e.getPlayerRef();
  if (r == null) return;
  @ST@ st = r.getStore();
  if (st == null) return;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  if (pr == null || !interested(pr.getUuid())) return;
  @WLD@ w = null;
  try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
  submit(req("ready", pr, w, st, r));
}""")
M(mprobe, r"""
public static void quit(Object ev) {
  @PR@ pr = ((@PDE@) ev).getPlayerRef();
  if (pr == null || !interested(pr.getUuid())) return;
  @PKG@.MapReq r = new @PKG@.MapReq();
  r.kind = "quit";
  r.pr = pr;
  r.uuid = pr.getUuid();
  r.who = pr.getUsername();
  r.at = System.currentTimeMillis();
  submit(r);
}""")
# the outbound tap: registered in the plugin's start(), removed in shutdown() (a second start removes the first one first)
M(mprobe, r"""
public static void tapOff0() {
  @PF@ f = TAPF;
  TAPF = null;
  if (f != null) { try { @PAD@.deregisterOutbound(f); } catch (Throwable t) { } }
}""")
M(mprobe, "public static synchronized void tapOff() { tapOff0(); }")
M(mprobe, r"""
public static synchronized void tapOn() {
  tapOff0();
  try {
    TAPF = @PAD@.registerOutbound((@PPW@) new @PKG@.MapTap());
    @PKG@.ProbeLog.info("map probes: outbound map-packet tap registered (it keeps nothing until an op starts p2, p4 or p5)");
  } catch (Throwable t) { TAPF = null; @PKG@.ProbeLog.warn("map probes: the outbound tap could not be registered (p2 uses the shared map cache only, p4 / p5 count nothing): " + t); }
}""")
M(mprobe, r"""
public static void shutdown0() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = SESS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MapSess s = (@PKG@.MapSess) it.next();
    try { endAll(s, "server stop", true, false, now); } catch (Throwable t) { }
  }
  SESS.clear();
  REQ.clear();
  P3ARM.clear();
  DELIVERED.clear();
  LASTWORLD.clear();
  ASSETS.clear();
  ENC.clear();
  TAPS = 0;
}""")
M(mprobe, r"""
public static void shutdown() {
  tapOff();
  try { if (TICKER != null) TICKER.cancel(false); } catch (Throwable t) { }
  TICKER = null;
  synchronized (LOCK) { shutdown0(); }
  @PKG@.ProbeLog.info("map probes stopped: tap removed, tick cancelled, every probe HUD removed");
}""")

# ---- bodies that call MapProbe
M(mhud, r"""
protected void onRemove() {
  this.gone = true;
  try { @PKG@.MapProbe.noteGone(this); } catch (Throwable t) { }
}""")
M(mtick, "public void run() { try { @PKG@.MapProbe.tick(); } catch (Throwable t) { @PKG@.ProbeLog.warn(\"map probes: tick failed: \" + t); } }")
M(mread, "public void run() { try { @PKG@.MapProbe.readNow(this.list); } catch (Throwable t) { } }")
M(matt, "public void run() { @PKG@.MapProbe.attachNow(this.sess, this.hud, this.store); }")
M(mdet, "public void run() { @PKG@.MapProbe.detachNow(this.pr, this.store, this.hud); }")
M(mrdy, "public void accept(Object ev) { try { @PKG@.MapProbe.ready(ev); } catch (Throwable t) { } }")
M(mquit, "public void accept(Object ev) { try { @PKG@.MapProbe.quit(ev); } catch (Throwable t) { } }")
M(mtap, "public void accept(@PR@ pr, @PKT@ p) { try { @PKG@.MapProbe.tap(pr, p); } catch (Throwable t) { @PKG@.MapProbe.TAPERR.incrementAndGet(); } }")
MAP_CLASSES = [mpng, mgeo, masset, mreq, mp3, msess, mhud, mui, mprobe, mtick, mread, matt, mdet, mrdy, mquit, mtap]

# ---- ProbeCmds: what the two command classes do
cmds = mk("ProbeCmds")
M(cmds, r"""
public static void tell(@PR@ pr, String s) {
  try { pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(cmds, r"""
public static void open(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ world, int n) {
  if (n > 0 && @PKG@.ProbeViews.isWin(n)) { @PKG@.ProbeWin.open(ref, store, pr, world, n); return; }
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { tell(pr, "The page could not be opened (no player component)."); return; }
  String who = pr.getUsername();
  if (n > 0) @PKG@.ProbeLog.info("opening probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ") for " + who);
  else @PKG@.ProbeLog.info("opening the index for " + who);
  try {
    p.getPageManager().openCustomPage(ref, store, new @PKG@.ProbePage(pr, n));
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn("could not open " + (n > 0 ? "probe " + n : "the index") + ": " + t);
    tell(pr, (n > 0 ? "Probe " + n + " (" + @PKG@.ProbeViews.nameOf(n) + ")" : "The list page") + " could not be opened - see the server log.");
    return;
  }
  if (n > 0) @PKG@.ProbeLog.info("sent probe " + n); else @PKG@.ProbeLog.info("sent the index");
}""")
M(cmds, r"""
public static void list(@PR@ pr) {
  int[] o = @PKG@.ProbeViews.order();
  tell(pr, "" + o.length + " probe pages (kit " + @PKG@.ProbeLog.kit() + "). Open them in this order: /skyprobe <n>, or /skyprobe for the list page.");
  for (int i = 0; i < o.length; i++) {
    int n = o[i];
    String k = @PKG@.ProbeViews.keyOf(n);
    String nm = @PKG@.ProbeViews.nameOf(n);
    tell(pr, "" + n + "  " + nm + (k.equals(nm) ? "" : "  (key " + k + ")") + "  -  " + @PKG@.ProbeViews.whatOf(n));
  }
  tell(pr, %s);
}""" % jl("0.4: the minimap HUD probes are chat commands - /skyprobe map lists them (p1a p1b p2 p2sharp p3 p3resend p4 p5 off status)"))
M(cmds, r"""
public static void arg(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ world, String a) {
  String t = a == null ? "" : a.trim();
  if (t.equalsIgnoreCase("list")) { list(pr); return; }
  if (t.equalsIgnoreCase("map")) { @PKG@.MapProbe.help(pr); return; }
  int n = @PKG@.ProbeViews.find(t);
  if (n < 0) {
    tell(pr, "No probe page '" + t + "'. Use a number 1-" + @PKG@.ProbeViews.count() + ", a name like base1, win or secgrid, or list.");
    return;
  }
  open(ref, store, pr, world, n);
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- 0.4: usage variant /skyprobe map <step> (2 words; admin: requirePermission + no permission groups, like its parent). A usage
# variant, not a sub-command: /skyprobe <page> keeps its one-word variant, and getPermissionGroupsRecursive never reaches variants
cmdM = mk("SkyProbeMapCmd", T["APC"])
F(cmdM, "public @RA@ whatArg;")
F(cmdM, "public @RA@ stepArg;")
C(cmdM, r"""
public SkyProbeMapCmd() {
  super("(admin) /skyprobe map <step> starts ONE minimap probe for you: p1a, p1b, p2, p2sharp, p3, p3resend, p4, p5, off, status");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("map", "the word map", @ATY@.STRING);
  this.stepArg = withRequiredArg("step", "p1a, p1b, p2, p2sharp, p3, p3resend, p4, p5, off or status", @ATY@.STRING);
}""")
M(cmdM, EXEC + r""" {
  String a = null;
  String st = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); st = String.valueOf(ctx.get(this.stepArg)); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe map failed: " + t); @PKG@.ProbeCmds.tell(pr, "Usage: /skyprobe map <step> - /skyprobe map lists the steps"); return; }
  if (!"map".equalsIgnoreCase(a.trim())) { @PKG@.ProbeCmds.tell(pr, "Two words after /skyprobe are the map probes: /skyprobe map <step> - /skyprobe map lists the steps"); return; }
  @PKG@.MapProbe.command(ref, store, pr, world, st);
}""")
# ---- usage variant /skyprobe <n | name | list>   (admin: requirePermission + no permission groups, like its parent)
cmdA = mk("SkyProbeArgCmd", T["APC"])
F(cmdA, "public @RA@ pageArg;")
C(cmdA, r"""
public SkyProbeArgCmd() {
  super("(admin) /skyprobe <n or name> opens that probe page (win and secgrid: the vault window probes); /skyprobe list prints every page in chat");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  this.pageArg = withRequiredArg("page", "probe page number, its name (base1, checkbox, ..., win, secgrid) or list", @ATY@.STRING);
}""")
M(cmdA, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.pageArg)); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe failed: " + t); @PKG@.ProbeCmds.tell(pr, "Usage: /skyprobe, /skyprobe <n or name>, /skyprobe list"); return; }
  @PKG@.ProbeCmds.arg(ref, store, pr, world, a);
}""")
# ---- /skyprobe (alias /uiprobe): the index page
cmd = mk("SkyProbeCmd", T["APC"])
C(cmd, r"""
public SkyProbeCmd() {
  super("skyprobe", "(admin) Probe pages: /skyprobe opens the list page, /skyprobe <n or name> opens one page, /skyprobe list prints them; /skyprobe map: the minimap probes");
  requirePermission("skyyuiprobe.admin");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "uiprobe" });
  addUsageVariant(new @PKG@.SkyProbeArgCmd());
  addUsageVariant(new @PKG@.SkyProbeMapCmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.ProbeCmds.open(ref, store, pr, world, 0);
}""")

# ---- plugin
pl = mk("SkyyUiProbePlugin", T["JP"])
C(pl, "public SkyyUiProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ProbeLog.LOG = getLogger();
  @PKG@.MapProbe.EXEC = @HSV@.SCHEDULED_EXECUTOR;
  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.MapReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MapQuit());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - /skyprobe (admin): " + @PKG@.ProbeViews.count() + " probe pages (kit " + @PKG@.ProbeLog.kit() + "); /skyprobe map: " + (@PKG@.MapProbe.STEPS.length - 2) + " minimap probes, each off until an op starts it");
}""")
# 0.4: the outbound map-packet tap is registered in start() (every plugin is set up by then) and removed in shutdown() - the SkyySacks
# 0.7.12 pattern; it keeps nothing until an op starts p2 / p4 / p5
M(pl, r"""
protected void start() {
  super.start();
  @PKG@.MapProbe.tapOn();
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.ProbeWin.shutdown(); } catch (Throwable t) { }
  try { @PKG@.MapProbe.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

CLASSES = [log, views, ses, box, win, chg, ctk, ltk, stk, net, page, pw, cmds, cmdA, cmd, pl] + MAP_CLASSES + [cmdM]
OLD_CLASSES = 16                    # the 0.3.1 classes (same names; the harness compares them byte for byte)


# ================= 0.3.1: ACCESS AUDIT - what the JVM would refuse at RUN time with IllegalAccessError =================
# javassist compiles a call to a protected / package-private member from any class (0.3: ProbeWin -> the page's protected sendUpdate),
# and -Xverify:all does not catch it either: the JVM checks member access when the instruction first runs (JVMS 5.4.4). So every class
# / member reference in the final class bytes is resolved here with the JVM's rules: a class must be public (or in our package); a
# member public, protected only from a subclass of its declaring class (the receiver rule - an instance member only on this / a
# reference of that subclass - is the verifier's, which the harness's -Xverify:all load covers), package-private only in its own
# package, private only in its own class. The harness checks the same references again with the JVM's own MethodHandles.Lookup.
import jpype
JMod, JConstPool = J["Modifier"], jpype.JClass("javassist.bytecode.ConstPool")
JClassFile, JDataIn, JByteIn = (jpype.JClass("javassist.bytecode.ClassFile"), jpype.JClass("java.io.DataInputStream"),
                                jpype.JClass("java.io.ByteArrayInputStream"))
AUDIT_OPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
             0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
             0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def class_file(data):
    """a javassist ClassFile read from class bytes (Python bytes or a Java byte[])"""
    return JClassFile(JDataIn(JByteIn(data)))


def audit_pkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def audit_elem(name):
    """the class a constant-pool class name stands for ([Lx.Y; -> x.Y), None for a primitive array"""
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items):
    """items: [(the referencing CtClass, the javassist ClassFile of its final bytes)] -> (refused, used non-public engine members,
    references checked). refused: one line per reference the JVM would refuse."""
    refused, used, seen = [], set(), 0
    for D, cf in items:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in AUDIT_OPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, AUDIT_OPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != JConstPool.CONST_Class:
                    continue                                  # a string / number constant
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)),
                                                                        str(cp.getFieldrefType(idx)))
                elif tag == JConstPool.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)),
                                                                                  str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)),
                                                                         str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = audit_elem(cname)
                    if en is not None and audit_pkg(en) != audit_pkg(dn) and not JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    C = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = C.getField(name, desc)
                    elif name == "<init>":
                        x = C.getConstructor(desc)
                    else:
                        x = C.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if JMod.isPublic(md) or (audit_pkg(dcn) == audit_pkg(dn) and not JMod.isPrivate(md)):
                        continue
                    if JMod.isPrivate(md):
                        ok = dcn == dn
                    elif JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False                            # package-private, another package
                    use = "%s %s.%s%s" % (JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


# self-test first: the 0.3 call (a class that is no page calling the page's protected sendUpdate) must be named - javassist compiles it
_st = mk("AccessAuditSelfTest")
M(_st, "public static void bad(@PAGE@ p, @UCB@ b) { p.sendUpdate(b); }")
_st_refused, _st_used, _st_n = access_audit([(_st, class_file(_st.toBytecode()))])
_st.detach()
assert len(_st_refused) == 1 and "CustomUIPage.sendUpdate" in _st_refused[0] and "IllegalAccessError" in _st_refused[0], \
    "access audit self-test: the 0.3 sendUpdate call from a non-page class must be refused: %s" % _st_refused

for c in CLASSES:
    c.writeFile(OUT)
print("classes written:", len(CLASSES))
_items = []
for c in CLASSES:
    with open(os.path.join(OUT, *str(c.getName()).split(".")) + ".class", "rb") as _f:
        _items.append((c, class_file(_f.read())))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_items)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError) - call protected engine "
                     "members only from their subclass, on this:\n  %s" % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
assert AUDIT_N > 1000 and any("CustomUIPage.sendUpdate" in u and "(from ProbePage)" in u for u in AUDIT_USED), \
    "access audit: %d references, sendUpdate only from ProbePage: %s" % (AUDIT_N, AUDIT_USED)
_by = {}
for _u in AUDIT_USED:
    _m, _from = _u[:-1].split(" (from ")
    _by.setdefault(_from, []).append(_m)
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; the non-public engine members, each used "
      "from its own subclass: %s" % (AUDIT_N, len(_items), " | ".join("%s: %s" % (k, ", ".join(v)) for k, v in sorted(_by.items()))))

jar = os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)
man = B.manifest("SkyyUiProbe", VERSION, "SkyWynn dev / test tool: /skyprobe (admin only) opens the vanilla-look kit's probe pages and the vault window probes (win, secgrid) one by one, and /skyprobe map runs the minimap HUD probes (server-made pictures in a HUD, a round test minimap, the map packet count) - each off until an op starts it, so Skyy can see which UI tricks work before a build uses them. No data, no config, zero dependencies.", PKG + ".SkyyUiProbePlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyUiProbe jar must not ship .ui files (inline pages only): %s" % _bad)
