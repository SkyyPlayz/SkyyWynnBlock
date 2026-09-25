"""0.1.4 (2026-09-25): HOTFIX - /trade offer grids get metadata-free item copies (a rolled item would disconnect the client:
  ClientItemMetadata); rolled items show their name + description in the slot tooltip. Notes in tools/essentials_0_1_4_patch.py.
SkyyEssentials 0.1.3 - build script (javassist via jpype). Derived from the LIVE 0.1.2 by copy + edit (this mod has no patch script).
Run:   python build_skyyessentials_0.1.3.py            -> SkyyEssentials/SkyyEssentials-0.1.3.jar
       (never --deploy from a workflow; tools/deploy_set.py installs the SET after Skyy says deploy)

0.1.3 = the admin config registry (research/Server-Setup-Spec.md 4.6, 5.4, section 3 parts; tools/CONFIG-CONTRACT.md) + the player
Settings switch tpa.updates (research/Settings-Spec.md 3.11 WITHOUT the refusing tpa.requests / msg.private: Skyy has not answered
refuse-vs-hide). Every 0.1.2 command, permission node, file, key and default is unchanged: nothing plays differently until an admin
changes a setting.
  CONFIG KIT (tools/skyycfg.py): config:def:SkyyEssentials / config:fn:SkyyEssentials / config:epoch:SkyyEssentials, published at the END
    of setup() after config.properties is loaded. Node skyyessentials.admin (SkyyMenu Server Setup shows the page as "Essentials").
    File: Skyy_SkyyEssentials/config.properties (the same file; every 0.1.2 key keeps its name). Rows (row key -> file key when they
    differ): parts part.tpa, part.msg, part.trade (-> tradeEnabled) (live, part, danger: switching OFF asks first); tpa
    tpa.expireSeconds (60 s, 10-600) and tpa.cooldownSeconds (10 s, 0-300) (live; EssStore.EXPIRE_MS / COOLDOWN_MS are now
    public static volatile long milliseconds bound with *1000, the unit rule); msg replyShortcut (restart); warps warps.editor (link
    warpadmin), spawn.set and spawn.reset (actions, danger); trade: every 0.1.2 /trade key (tradeSameWorld, tradeDistance,
    tradeExpirySeconds, tradeCooldownSeconds, tradeSlotsPerSide (new trades), tradeCountdownSeconds, tradeCoinsAllowed, tradeMaxCoins,
    tradeCancelOnDamage, tradeOpenMode (choice, custom: binding because the field is the 0.1.2 boolean PAGE_MODE),
    tradeAfterSwitchSeconds (adv, danger when lowered), tradeSaveDelayMillis (adv, ms)). Ranges = the 0.1.2 loader's clamps.
    Hand edits: TCfg.reloadKit is the kit's RELOAD (re-reads every live key, never replyShortcut: that one waits for a restart).
  PARTS (spec section 3): part.tpa OFF -> /tpa, /tpahere and /tpaccept answer "Teleport requests are turned off on this server."
    (/tpdeny and /tpacancel still work; pending requests expire as usual). part.msg OFF -> /msg (tell, w, whisper), /reply and /r <text>
    answer "Private messages are turned off on this server." (/r alone and /r <count> still run /redo for builders). part.trade = the
    0.1.2 tradeEnabled switch (requests and accepts refused, open trades finish, /trade claim works). Commands stay registered.
  /tradeadmin config is folded into the kit: the same "Trade settings" page, now drawn from the kit rows; ON/OFF, Set and Reload file go
    through CfgFn (validated, logged in config-changes.log, versioned in config-history/, written line by line - the 0.1.2 whole-file
    writer that dropped hand comments is gone). A part switched OFF asks Confirm / Cancel on the page. /tradeadmin reload = the kit's
    reload op. Holders of only skyyessentials.tradeadmin keep changing the TRADE keys there as in 0.1.2: the kit's permission check
    (PERM_FN EssPerm.has) also accepts skyyessentials.tradeadmin, but only inside those two trade-page / reload calls (a ThreadLocal),
    never from SkyyMenu (which needs skyyessentials.admin).
  /warpadmin (requirePermission skyyessentials.admin; also the kit's warps.editor link row): BIG inline page (1120 x 930) - every vanilla
    warp as a row "name - world - x y z - creator" with Go (teleport), Move here, Rename (to the name typed in the box) and Remove
    (Confirm / Cancel); Add warp here; the world spawn buttons; Settings (teleport + message settings page, the kit rows) and Refresh.
    Engine calls copied from vanilla (HytaleServer.jar bytecode, this session): WarpSetCommand = new Warp(new Transform(position,
    head rotation), name, world, username, Instant.now()) -> TeleportPlugin.addWarp(warp, true) (addWarp itself places / replaces the
    marker entity and calls saveWarps()); a replace first dispatches ReplaceWarpEvent and stops when a listener cancels it;
    WarpRemoveCommand = RemoveWarpEvent, then removeWarp(id) (removes the marker and saves). Names: the /warp sub-command names (go,
    list, remove, reload, set) are refused like WarpSetCommand does. Rename = addWarp(copy under the new id, false) then removeWarp(old)
    (a case-only rename replaces in place). Go = WarpCommand.tryGo's calls (Warp.toTeleport(), TeleportHistory, Teleport component),
    page closed first.
  WORLD SPAWN (spec 5.4, same calls as vanilla /spawn set and /spawn set default, bytecode this session): on the admin's world thread,
    WorldConfig.setSpawnProvider(new GlobalSpawnProvider(new Transform(position, head rotation))) + markChanged(); reset =
    setSpawnProvider(null) + markChanged() (vanilla's /spawn set default skips markChanged - added so the reset is saved too). Refused
    in instance worlds (SkyyIslands islands, portal worlds: they own their spawn). From the warps page (Confirm / Cancel) and from the
    kit's action rows (SkyyMenu Server Setup; the action schedules itself on the admin's world and answers in chat). Change log: a page
    click writes one line via=command; a Server Setup click is the kit's own "done" line (via=menu) only - no second line - and, when the
    scheduled change then does not happen, one follow-up line with status "failed" (see 0.1.3 REVIEW FIXES).
  PLAYER SETTINGS: tpa.updates ("Teleport request updates", general, default ON) registered in setup() (settings:def: + settings:fn:register,
    no SkyyMenu = always on). OFF hides only the lines about requests that were never accepted: "denied your teleport request",
    "expired", "went offline, ... cancelled" (EssStore.prune) and the /tpacancel notice to the target. The work (removal, cooldowns) runs
    either way; accepted-teleport lines always show (Settings-Spec 2.3).
  NOT BUILT: tpa.requests and msg.private (the refusing switches wait for Skyy's refuse-vs-hide answer, Settings-Spec section 6); warp
    locks (spec 5.4 "later"). Spec 4.6's placeholder names trade.timeoutSeconds / trade.allowCoins / trade.maxStacks are the real 0.1.2
    keys tradeExpirySeconds / tradeCoinsAllowed / tradeSlotsPerSide (file keys never change). 0.1.2 wrote "CONFIG key old -> new" lines
    into trades/trade.log; 0.1.3 logs every change in the kit's config-changes.log instead (with who, via and old/new values).
  CHECKED in a bare JVM: python SkyyEssentials/test_skyyessentials_0.1.3.py (committed next to this script, re-runnable; the first
    run's throwaway scratch harness was replaced by it in the review fixes; 224 checks, 0 fails on 2026-09-25): all 62 classes load
    under -Xverify:all with HytaleServer.jar; defaults = 0.1.2; a missing file gets exactly the default text; a 0.1.2 CRLF file with a
    hand comment keeps every byte and gets the 4 new keys appended (CRLF); the 0.1.2 clamps; the kit header (21 rows, flags) and the
    rows' start values; no rewrite and no clamp lines at start; console sets apply to the real fields with the unit scale
    (tpa.expireSeconds 90 -> EXPIRE_MS 90000, out of range refused), part OFF asks / ON does not, part.trade -> tradeEnabled,
    tradeOpenMode through the custom: binding, replyShortcut RESTART (field untouched, status restart), tradeAfterSwitchSeconds asks
    only when lowered; file lines rewritten in place (comments + CRLF kept, the row key part.trade never written), history copies,
    change-log lines; a hand edit + reload -> logged via=file, TCfg.reloadKit applied it (clamp logged, replyShortcut untouched);
    export -> import preview "nothing to change"; a UUID without nodes is denied; notifyOn / regSetting against fake settings:fn:get /
    register and the tpa.updates gates (bytecode: only denied / expired / went offline / /tpacancel lines); the request book uses the
    live EXPIRE_MS / COOLDOWN_MS; setup() order (TCfg.load -> registrations -> regSetting -> CfgPub.start last); permissions through the
    engine's AbstractCommand (hytale:Adventurer gets only player nodes, /fly /tradeadmin /warpadmin nodes in no group); spawn actions
    from the console asked / refused, a scheduled spawn change that cannot happen writes one "failed" line and no "done" line; the
    warps page (main, result, both confirm views, no permission) and both settings pages (plain, confirm, draft kept) rendered into a
    real UICommandBuilder: root anchor only Width/Height, height <= 1000, unique ids, no underscores, every append / set / event
    target exists, balanced markup; garbage ops never throw. NOT runnable in a bare JVM (no TeleportPlugin / worlds / permissions): the
    warp rows with real warps, Go / Move / Rename / Remove / Add, the world spawn change itself, EssPerm with real nodes, a trade-page
    click (needs a PlayerRef; it calls the same CfgFn.set as the console checks) - they are in the in-game steps.
  0.1.3 REVIEW FIXES (2026-09-25, before any deploy):
    - A Server Setup spawn.set / spawn.reset click wrote TWO config-changes.log lines (the kit's via=menu "done" line + the mod's own
      line hard-coded via=command). SpawnTask now passes no via: a change that works adds only a server log line with the details
      (world, x y z); the /warpadmin page passes via=command and keeps its one line.
    - The kit logs "done" as soon as the action answers ok; a scheduled change that then did not happen (the admin left, changed
      worlds, position unreadable, the world closing, an error) left that "done" line standing alone. SpawnTask now writes a follow-up
      line (key spawn.set / spawn.reset, old "(action)", new "not done - <why>", status "failed", via menu - the kit hands an action hook
      no via; SkyyMenu Server Setup is its only caller). kitSpawn also refuses an instance world BEFORE scheduling (a plain read of
      the world config), so the common refusal never produces a "done" line at all.
    - EssWarp.spawnSet refuses a world that is not alive ("try again in a moment"), the same answer kitSpawn gives, so the page's direct
      call never touches a closing world and never falls through to the page's catch-and-log.
  UNVERIFIED: that the vanilla warp marker entity follows addWarp / removeWarp for our edits exactly as for /warp set / remove (same calls);
    that WorldConfig.markChanged() alone saves the new spawn provider (and the reset) across a restart (spec 8.4.8); the confirm view's
    Wrap: true label (used by SkyyAuctions / SkyyClasses).

0.1.2 = /trade, built from research/Trade-Spec.md. Every 0.1.1 command, permission and the /r behaviour are unchanged (the 0.1.1 notes
follow below this block). New:
  /trade <player>          send a trade request (60 s, 10 s cooldown per requester, same world + within 9 blocks - all config)
  /trade accept [player]   accept the newest request (or that player's); opens the trade for BOTH players
  /trade deny [player]     refuse;   /trade cancel   take back your requests AND end your open trade (everything goes back)
  /trade                   reopen the trade page of your open trade (or the usage + your pending requests)
  /trade claim             collect what a trade still owes you (your inventory was full, or you were offline)
  Every one of them (root, subcommands, both usage variants) calls setPermissionGroups(new String[] { "hytale:Adventurer" }).
  /tradeadmin log [player] | return <player> | config | reload   - requirePermission("skyyessentials.tradeadmin") on the root, every
                           subcommand and the log variant. config = the in-game settings page (HANDOFF "In-game server setup": every
                           key of config.properties can be changed there; the page writes the same file at once).
THE TRADE PAGE (inline, BIG: 1100 x 800): title, a status line, two columns - "Your offer" and "<Name>'s offer" - each a read-only
  ItemGrid built from a snapshot (AreItemsDraggable false, NO InfoDisplay: None, so hovering shows the real item tooltip: the
  anti-scam feature of Trade-Spec section 1), READY / not ready, the coin offer; a coin box (TextField + Set, the SkyyGuilds / SkyySacks
  "@Key" "#Id.Value" pattern) only when SkyyCoins' coins:fn:get/add/take are all on the bridge and tradeCoinsAllowed=true; buttons
  Ready / Not ready, Open as chest (page mode) or Edit my offer (chest mode), Cancel trade, Close; help lines and a result line.
  Your OWN offer is a real container window: page mode (tradeOpenMode=page, default) opens the page TOGETHER with a ContainerWindow on
  your escrow container (PageManager.openCustomPageWithWindows, the SkyyVault 0.1 pattern); "Open as chest" opens the same container in
  the vanilla chest window (Page.Bench, the proven /invsee pattern) - the fallback in case the client does not draw window slots next to
  a custom page (UNVERIFIED, same open question as SkyyVault). Closing that chest brings the trade page back (without slots: its Edit my
  offer button opens the chest again). tradeOpenMode=chest: accepting opens the chest at once.
  Page rebuilds: after your own click, and when a REAL change happens on the other side (their offer, Ready, coins) - coalesced to at
  most one per second per page. NEVER on a timer: the countdown is counted in CHAT ("2...", "1..."), the page shows one static "trading
  in 3 seconds" line (a per-second page update would swallow the Cancel click - HANDOFF UI rule).
ESCROW (Trade-Spec section 10): each player's offer slots ARE a plugin-owned SimpleItemContainer (tradeSlotsPerSide, 16). Dragging an
  item in moves it out of the inventory into that container in the same engine move - it is never "your inventory, shown elsewhere".
  One lock per trade (synchronized TSession methods) orders every offer change, Ready click, countdown and settle. ANY change of either
  offer (items or coins) clears BOTH Ready marks and stops a running countdown. Both Ready -> both containers DENY_ALL (set inside the
  lock) + the agreed contents are recorded -> tradeCountdownSeconds (3) countdown -> settle: each container is emptied with ONE
  clear() (SimpleItemContainer.internal_clear: a single write under the container lock that ignores the global filter, so an item is
  either taken by the trade or by a racing client move, never both - NOT removeAllItemStacks(), which skips every slot whose filter denies
  output and so returns NOTHING from a DENY_ALL escrow) and compared with the agreed contents; any difference = the whole trade is
  cancelled and everything goes back to its owner (never a swap of goods nobody agreed to). Coins (only through the SkyyCoins bridge, only
  when present and tradeCoinsAllowed): both profiles must still be the ones the trade opened on, a PAYING marker is written, take A (marked
  paid + written), take B (same; A is refunded when B fails), then the COMPLETED record is written to disk (tmp + fsync + atomic rename)
  BEFORE anything is paid out, then coins are added and the items delivered. A refund or payout that cannot be paid right now (SkyyCoins
  error, or that player's profile changed) stays OWED in the record and is paid on the profile the trade was made on (/trade claim, next
  join). Cancel (button, /trade cancel, distance, world change, damage, profile busy/switch, disconnect, admin, server stop,
  trade:fn:cancel) = every item back to its own owner.
DELIVERY ("give to storage first, count before and after"): on the recipient's world thread, storage -> hotbar -> backpack, counting the
  item id before and after; only after - before counts as given. What does not fit stays OWED in the trade record (never dropped, never
  forced in): "/trade claim", every world join/switch (PlayerReadyEvent) and /tradeadmin return retry it. Deliveries wait while
  profile:busy:<uuid> is set and for tradeAfterSwitchSeconds (30) after a profile switch / crash recovery (the SkyyVault gate: a crash in
  SkyyProfiles' 30 s marker window would otherwise duplicate or lose them). A stack whose item no longer exists is kept byte for byte.
  After a trade ends, each dead escrow container is checked again 3 s and 15 s later; anything a late client move put there goes back to
  its owner (belt and braces - DENY_ALL already refuses such moves).
FILES (<world>/mods/Skyy_SkyyEssentials/, config.properties stays where 0.1.1 put it): trades/pending/<id>.json = one live or unsettled
  trade (EXTENDED JSON, the SkyyVault / SkyyProfiles lossless slot format: explicit id/qty/durability/quality/metadata + the engine's
  ItemStack.CODEC encoding), written AT ONCE when items move into or out of an offer, a trade settles or a delivery changes what is
  owed (tradeSaveDelayMillis, 1 s, only delays Ready / coin-offer changes, which carry no item risk), rev-ordered under a per-trade IO lock
  so an old snapshot never overwrites a newer file; read back after every write. At start every pending record still ACTIVE (server
  crash or kill during a trade) becomes CANCELLED reason server-restart and is returned at the owners' next join (coins a PAYING record
  shows as already taken are owed back too). A pending record whose id is already in trades/archive (an old copy put back, e.g. a
  restored backup) is NOT loaded and left untouched for a human. A record with nothing owed moves to trades/archive/<yyyy-MM>/<id>.json
  (never deleted). trades/trade.log (REQUEST, ACCEPT, DENY, EXPIRE, READY, UNREADY, COINS, COUNTDOWN-START, COUNTDOWN-CANCEL, COINS-TAKEN,
  COINS-REFUND, COIN-OWED, COMPLETE, CANCEL reason=..., DELIVER, RETURN-AT-JOIN, LATE-RETURN, ADMIN-RETURN, CONFIG, WRITE-FAIL,
  SKIP-ARCHIVED, ARCHIVE), trades/names.properties (for /tradeadmin with offline players).
CONFIG (config.properties, all editable in game on /tradeadmin config; a hand edit + /tradeadmin reload works too): replyShortcut (0.1.1,
  restart), tradeEnabled, tradeSameWorld, tradeDistance (0 = no distance limit), tradeExpirySeconds, tradeCooldownSeconds,
  tradeSlotsPerSide (new trades), tradeCountdownSeconds, tradeCoinsAllowed, tradeMaxCoins (0 = no cap), tradeCancelOnDamage,
  tradeOpenMode (page | chest), tradeAfterSwitchSeconds, tradeSaveDelayMillis. Missing keys are added to an existing file on start
  (the 0.1.1 value of replyShortcut is kept). A file that cannot be read is never overwritten; in-game changes are refused until it reads.
BRIDGE: trade:active:<uuid> = TRUE while that player is in an open trade; trade:fn:cancel = Function(UUID) -> Boolean.
PROFILES (tools/PROFILES-CONTRACT.md): accepting is refused while either player has profile:busy:<uuid> or is inside the
  tradeAfterSwitchSeconds window; an open trade is cancelled for BOTH when either player's profile:busy appears or profile:epoch changes
  (1 s ticker; the window's ValidatedWindow.validate also closes on busy). coins:fn:* act on the active profile. Each side's storage key
  (the contract's pkey(uuid)) is recorded when the trade opens; what a trade owes a player (their own items back after a cancel, or
  what they received) is only delivered while that SAME profile is active - on another profile it waits ("switch back, then /trade
  claim"), so a trade never moves items between one player's profiles. Coins follow the same rule: right before coins are taken the
  settle checks both players' storage key + epoch against the trade's (not only profile:busy), and a payout or refund to a player whose
  profile changed stays owed until that profile is active again. KNOWN LIMIT (the same one SkyyVault states): a SERVER CRASH (not a
  normal stop) within ~10 s after items moved can duplicate or lose them (engine saves inventories every 10 s;
  tools/PROFILES-CONTRACT.md section 5). A crash in the few milliseconds between a SkyyCoins take and the paid marker being on disk loses
  those coins; the COINS-TAKEN trade.log line (written right after the take) is the trace, and the start-up CANCEL line names such a
  trade. A normal stop cancels open trades and keeps everything in the files for the next join.
THREADS: page clicks, window close/validate, container change events and deliveries run on the player's world thread; the 1 s ticker,
  the countdown, every settle / cancel (also /tradeadmin return's), every trade-file and config.properties write (the settings page and
  /tradeadmin reload hand theirs over; the page is rebuilt on the admin's world thread when the write is done) run on ONE daemon thread
  (SkyyEssentials-trade), never on the shared scheduler. Only trade.log / names lines are appended on other threads (no fsync, own lock).
  Emptying an escrow from the trade thread is safe: ItemContainer writes hold the container's own write lock, and the only engine
  listener on a window's container (WindowManager.setWindow0 -> markWindowChanged) is an Int2ObjectConcurrentHashMap lookup +
  AtomicBoolean.set - the window packet itself is sent by updateWindows() on the world tick (bytecode, 2026-09-25). Locks: TSession ->
  TRecord -> IO lock, nothing calls out while holding one except the SkyyCoins functions (which never call back). Container locks are
  leaf locks (the engine fires change events after releasing them).

0.1.2 REVIEW FIXES (2026-09-25, before any deploy):
  - CRITICAL: the escrow was emptied with removeAllItemStacks() while DENY_ALL - SimpleItemContainer.cantRemoveFromSlot is true when
    the global filter denies output, so it returned an empty list: every cancel and every countdown would have lost all offered items
    (left in a dead, locked container; the late check could not take them either). Now clear() (filter-free, one write) everywhere.
  - /tradeadmin return runs its cancel + delivery on the trade thread (it cancelled inline on the admin's world thread) and reports back
    in chat; deliveries save the record through the trade thread (was an fsync on the recipient's world thread); settings-page changes
    and reloads write config.properties on the trade thread.
  - A coin refund that fails (A's coins taken, then B's take or the record write fails, then SkyyCoins refuses the refund) stays OWED
    (coinOwe) instead of being dropped with a log line only; PAYING marker (see ESCROW) so a crash mid-transfer owes taken coins back.
  - Coins are profile-bound like items (key + epoch check right before taking; payouts/refunds wait for the right profile).
  - Item moves into / out of an offer are saved at once (tradeSaveDelayMillis up to 30 s could have widened the crash item-loss window).
  - Coin trading turned off (or SkyyCoins gone) with a coin offer on the table: a "Clear my coins" button shows instead of the coin box,
    both columns keep showing any offered coins, and a countdown that still reaches zero with coins is cancelled (reason coins-off).
  - "1 second" (not "1 seconds") when tradeCountdownSeconds is 1; the ended page is a small panel; a player whose trade request is
    waiting on someone who leaves is told the request was dropped (a request FROM a leaving player is still dropped silently, spec 7).

0.1.1 CHANGES (beta test 2026-09-24, BETA-TEST.md results):
 (1) /r = reply. Players typed /r to answer a /msg and got "no permission": /r is vanilla's /redo alias (WorldEditor group).
     Investigation (HytaleServer.jar bytecode, 2026-09-24):
       - RedoCommand: name "redo", addAliases("r"), setPermissionGroups("hytale:WorldEditor"), usage variant RedoWithCountCommand
         (/redo <count>). BuilderToolsPlugin registers it in setup(); PluginManager runs every plugin's setup() before any start().
       - CommandManager.register: commandRegistration.put(name, cmd) and aliases.put(alias, name) - no conflict check, last wins.
       - CommandManager.resolveCommand(name): commandRegistration.get(name) FIRST, the alias map only when no command has that name.
         handleCommand lower-cases the typed name and calls resolveCommand. So a top-level command NAMED "r" always wins over
         vanilla's alias, whatever order the plugins load in; /redo itself (its name) is never touched.
       - The unregister lambda does commandRegistration.remove(name) + aliases.remove(each alias) unconditionally, so registering "r"
         as an ALIAS of /reply would delete vanilla's r->redo mapping when this mod unloads; a NAME "r" removes only our entry.
       - Precedent: nhulston Essentials 1.8.0 (a published mod) registers a top-level "r" (alias "reply") the same way, with
         setAllowsExtraArguments(true) + ctx.getInputString(); Skyy's 2026-07-04 "test all modspacks" session ran with it enabled.
       - CommandTreeBuilder sends every permitted command as name + getAliases() to the client, so WorldEditors would receive "r"
         twice (our name + redo's alias). To keep the client's command list clean, start() removes "r" from RedoCommand.getAliases()
         (the live Set; resolution does not use it) ONLY when our /r is the registered one; shutdown() puts it back.
     Result - /r is SAFE to take over, so 0.1.1 registers a top-level /r (all players, hytale:Adventurer):
       /r <message>        reply to your last message partner (same as /reply)
       /r  (alone)         players who may use /redo (WorldEditor/admin): forwarded to vanilla "/redo" via CommandManager.handleCommand
                           (vanilla checks the permission again); everyone else gets the usage line
       /r <1-4 digits>     players who may use /redo: forwarded to "/redo <count>"; everyone else: replies with that number
       Builders who want to reply with a bare number use /reply. /redo and /redo <count> are unchanged for everyone.
     Server owners can switch it off: <world>/mods/Skyy_SkyyEssentials/config.properties  replyShortcut=false  (restart) -> /r stays
     vanilla's /redo alias only. If another mod already registered a top-level /r, SkyyEssentials leaves it alone (logged).
 (2) TPA WARN fixed: "could not record the instance return point ... NullPointerException: Cannot invoke ArchetypeChunk..." (server
     log 2026-09-24_19-51-34, line stamped 2026/09/25 02:55:55 UTC, SkyLordPlayz TPA'd from their island into WesleyPlayz's island). Cause (bytecode): Store.addComponent outside
     a system tick consumes its CommandBuffer before returning; TeleportSystems$PlayerMoveSystem.onComponentAdded(Teleport) for a
     DIFFERENT world runs teleportToWorld -> commandBuffer.run(... PlayerRef.removeFromStore(); destWorld.addPlayer(...)). So after
     st.addComponent(ref, Teleport) the mover's Ref is already dead, and 0.1's markReturn (ensureAndGetComponent on that Ref) threw the
     NPE - the return point was never set; the TeleportHistory append after it failed silently too (so /tp back missed cross-world
     TPAs). Vanilla InstancesPlugin.teleportPlayerToInstance does setReturnPointOverride, then TeleportHistory.append, then
     addComponent(Teleport) LAST; onPlayerAddToWorld reads the override from the Holder that removeFromStore carries to the new world.
     0.1.1 uses the same order; if addComponent throws, the override is cleared again (no stale return point).
 (3) Review fixes (same 0.1.1, before any deploy):
     - config.properties is written tmp + fsync + atomic rename (ATOMIC_MOVE + REPLACE_EXISTING, 5 x 20 ms retries - the SkyyGuilds /
       SkyyProfiles pattern). An unreadable file is NOT overwritten (that would throw away the owner's setting); the warning names the
       file and says to fix or delete it (a deleted file comes back with the default on the next start).
     - The "r" alias of /redo is only edited while the engine refuses logins (HytaleServer: InitialPacketHandler disconnects while
       !isBooted() and while isShuttingDown()), because AbstractCommand.aliases is a plain HashSet that CommandTreeBuilder iterates on
       every login / PermissionsModule tree resend. Vanilla /plugin load|unload|reload can load or unload this mod with players online;
       then the Set is left alone (logged): cosmetic only, typed /r resolves the same either way.
     - The /r setup block in setup() has its own try/catch: a failure there costs only /r (log "/r off (error)"), never /tpa /msg /fly.
     - /r <digits> from a player who may /redo: when that player has an online message partner, a chat line says it ran /redo and
       that /reply <number> sends the number (no line without a partner - then it cannot have been a reply).

Skyy's rule: "use vanilla everywhere possible, and only add what we need to". HyperEssentials is gone (world crash on death),
so this mod fills ONLY the gaps vanilla leaves. Vanilla check (2026-09-23, HytaleServer.jar, all 763 AbstractCommand
subclasses: constructor name + addAliases strings, plus a String-constant scan of every com/hypixel class):
  tpa, tpahere, tpaccept, tpdeny, tpacancel, msg, tell, w, whisper, reply, fly  -> NOT in vanilla (built here)
  r      -> vanilla alias of /redo; 0.1.1 takes it over as described above (smart /r: reply, or /redo for players allowed to redo).
  (/tp, /tp back, /spawn, /warp, /whereami stay vanilla; our teleports append to vanilla TeleportHistory so /tp back works.)

Commands (all players, vanilla "hytale:Adventurer" permission group like /ping /who /whereami /emote). How that gate works
(bytecode, 2026-09-23 review): CommandRegistry.registerCommand -> AbstractCommand.setOwner() generates the command's permission
node (plugin base permission + ".command.<name>"; a usage variant inherits its parent's node) unless requireNoPermission() was
called, so AbstractCommand.hasPermission() does NOT short-circuit. setPermissionGroups() feeds CommandManager.createVirtualPermissionGroups
-> PermissionsModule virtual groups, which grant that node to "hytale:Adventurer" = HytalePermissionsProvider.DEFAULT_GROUP_LIST
(every player who has no explicit group). So everyone can use them, and a player moved out of that group chain loses them.
  /tpa <player>        ask to teleport to a player          /tpahere <player>   ask a player to teleport to you
  /tpaccept [player]   accept (newest, or from that player) /tpdeny [player]    refuse
  /tpacancel           cancel all your outgoing requests
  /msg <player> <text> (aliases tell, w, whisper)          /reply <text>       answer your last message partner
  /r <text>            same as /reply (0.1.1; see above)
Admin: /fly (permission skyyessentials.fly) - toggles MovementSettings.fly = FlyMode.Allowed (engine API verified;
  pattern from HyperEssentials FlyCommand.applyFly, which used the old canFly boolean). Off = vanilla resetFly(gameMode).
  Vanilla re-derives movement settings on world change / gamemode change / model change / mount, so a 2s tick re-asserts it.

Rules: requests expire after 60s, 10s cooldown per requester, max 1 pending per requester->target pair.
Cross-world teleport = the vanilla TeleportToPlayerCommand pattern: read the destination player's TransformComponent +
HeadRotation ON THEIR world thread, then add Teleport.createForPlayer(destWorld, transform) to the mover ON THE MOVER'S
world thread (world.execute). Each step re-validates both players and re-dispatches if a player changed worlds.
Teleporting INTO an instance world (a SkyyIslands island, a portal world): like InstancesPlugin.teleportPlayerToInstance, the mover's
pre-teleport world + transform is stored as InstanceEntityConfig.setReturnPointOverride(WorldReturnPoint) (built exactly like the
engine's private makeWorldReturnPoint), so vanilla /instance exit (alias leave) and world-drain send a TPA visitor back to where they
were instead of to the island's own spawnInstance return point (the owner's position when the island was first created). Only set
when the destination is an instance AND a different world: onPlayerAddToWorld consumes the override only on instance entry.
The override and the TeleportHistory entry are written BEFORE the Teleport component (0.1.1 fix above).
State is in memory only; a tick prunes everything that is not keyed by an online UUID (every 10s). The only file is
Skyy_SkyyEssentials/config.properties (replyShortcut), written with the default on first start.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG

VERSION = "0.1.4"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
TC  = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
HR  = "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation"
TP  = "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport"
TPH = "com.hypixel.hytale.builtin.teleport.components.TeleportHistory"
TRF = "com.hypixel.hytale.math.vector.Transform"
R3F = "com.hypixel.hytale.math.vector.Rotation3f"
V3D = "org.joml.Vector3d"
MM  = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MS  = "com.hypixel.hytale.protocol.MovementSettings"
FM  = "com.hypixel.hytale.protocol.FlyMode"
GM  = "com.hypixel.hytale.protocol.GameMode"
PLY = "com.hypixel.hytale.server.core.entity.entities.Player"
IEC = "com.hypixel.hytale.builtin.instances.config.InstanceEntityConfig"
IWC = "com.hypixel.hytale.builtin.instances.config.InstanceWorldConfig"
WRP = "com.hypixel.hytale.builtin.instances.config.WorldReturnPoint"
WCF = "com.hypixel.hytale.server.core.universe.world.WorldConfig"
CMG = "com.hypixel.hytale.server.core.command.system.CommandManager"
CSN = "com.hypixel.hytale.server.core.command.system.CommandSender"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

# every engine member this mod touches (checked against HytaleServer.jar with scratchpad/reflect.py + bc.py)
for c, m in ((PR, "getUuid"), (PR, "getUsername"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"),
             (PR, "sendMessage"), (PR, "getPacketHandler"), (PR, "hasPermission"),
             (UNI, "get"), (UNI, "getPlayer"), (UNI, "getWorld"),
             (REF, "getStore"), (ST, "getComponent"), (ST, "addComponent"), (ST, "ensureAndGetComponent"), (ST, "getExternalData"),
             (EST, "getWorld"), (WLD, "execute"), (WLD, "isAlive"),
             (TC, "getComponentType"), (TC, "getPosition"), (HR, "getComponentType"), (HR, "getRotation"),
             (TP, "getComponentType"), (TP, "createForPlayer"), (TPH, "getComponentType"), (TPH, "append"),
             (R3F, "x"), (R3F, "y"), (R3F, "z"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (MM, "getComponentType"), (MM, "getSettings"), (MM, "getDefaultSettings"), (MM, "update"), (MM, "resetFly"),
             (MS, "fly"), (FM, "Allowed"), (FM, "Disabled"), (FM, "Forced"), (GM, "Creative"), (GM, "Adventure"),
             (PLY, "getComponentType"), (PLY, "getGameMode"),
             (AC, "addAliases"), (AC, "requirePermission"), (AC, "addUsageVariant"), (AC, "setPermissionGroups"), (AC, "withRequiredArg"),
             (ATY, "PLAYER_REF"), (ATY, "GREEDY_STRING"), (CTX, "get"), (MSG, "raw"), (MSG, "color"),
             (HSV, "SCHEDULED_EXECUTOR"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             (TC, "getTransform"), (WLD, "getWorldConfig"), (WCF, "getUuid"),
             (IEC, "getComponentType"), (IEC, "setReturnPointOverride"),
             (IWC, "get"), (IWC, "shouldRespawnWhenTargeted"), (IWC, "getInstanceKey"), (IWC, "getInstanceName"),
             (WRP, "getReturnPoint"), (WRP, "getWorld"),
             # 0.1.1: /r takeover + TPA order fix
             (CMG, "get"), (CMG, "resolveCommand"), (CMG, "getCommandRegistration"), (CMG, "handleCommand"),
             (AC, "hasPermission"), (AC, "getAliases"), (AC, "setAllowsExtraArguments"), (AC, "getName"),
             (CTX, "getInputString"), (CTX, "sender"), (PB, "start"), (PB, "getDataDirectory"), (REF, "isValid"),
             # 0.1.1 review: alias Set edits only while logins are refused
             (HSV, "get"), (HSV, "isBooted"), (HSV, "isShuttingDown")):
    B.probe(pool, c, m)

PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
rq   = pool.makeClass(PKG + ".TpReq")
es   = pool.makeClass(ES)
hop  = pool.makeClass(PKG + ".HopDispatch")
mv   = pool.makeClass(PKG + ".MoveTask")
rd   = pool.makeClass(PKG + ".ReadDestTask")
fly  = pool.makeClass(PKG + ".FlyTask")
tick = pool.makeClass(PKG + ".EssTick")
tpa  = pool.makeClass(PKG + ".TpaCmd", pool.get(APC))
tph  = pool.makeClass(PKG + ".TpaHereCmd", pool.get(APC))
tacn = pool.makeClass(PKG + ".TpAcceptNamedCmd", pool.get(APC))
tac  = pool.makeClass(PKG + ".TpAcceptCmd", pool.get(APC))
tdnn = pool.makeClass(PKG + ".TpDenyNamedCmd", pool.get(APC))
tdn  = pool.makeClass(PKG + ".TpDenyCmd", pool.get(APC))
tcan = pool.makeClass(PKG + ".TpaCancelCmd", pool.get(APC))
msg  = pool.makeClass(PKG + ".MsgCmd", pool.get(APC))
rep  = pool.makeClass(PKG + ".ReplyCmd", pool.get(APC))
rcm  = pool.makeClass(PKG + ".RCmd", pool.get(APC))
flc  = pool.makeClass(PKG + ".FlyCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyEssentialsPlugin", pool.get(JP))

# vanilla: /ping /who /whereami /emote /help. NOT dead code: setOwner() auto-generates the permission node at registration and
# this grants it to the default player group via the virtual permission groups (see the docstring).
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'

# ================= TpReq (one pending teleport request) =================
for f in ("public java.util.UUID from;", "public java.util.UUID to;", "public boolean here;",
          "public String fromName;", "public String toName;", "public long created;", "public long expires;"):
    rq.addField(CtField.make(f, rq))
rq.addConstructor(CtNewConstructor.make("""
public TpReq(java.util.UUID from, java.util.UUID to, boolean here, String fromName, String toName, long created, long expires) {
  this.from = from; this.to = to; this.here = here; this.fromName = fromName; this.toName = toName;
  this.created = created; this.expires = expires;
}""", rq))

# ================= EssStore (in-memory state + shared helpers) =================
es.addField(CtField.make(f"public static {LOG} LOG;", es))
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap REQ = new java.util.concurrent.ConcurrentHashMap();", es))        # "from>to" -> TpReq
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST_SENT = new java.util.concurrent.ConcurrentHashMap();", es))  # requester uuid -> Long millis
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST_PM = new java.util.concurrent.ConcurrentHashMap();", es))    # uuid -> partner uuid
es.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FLY = new java.util.concurrent.ConcurrentHashMap();", es))        # uuid -> Boolean (flight on)
# 0.1.3: config rows (tpa.expireSeconds / tpa.cooldownSeconds, bound field:...*1000 - milliseconds behind a seconds row) and the
# part switches part.tpa / part.msg; same defaults as the 0.1.2 constants
es.addField(CtField.make("public static volatile long EXPIRE_MS = 60000L;", es))
es.addField(CtField.make("public static volatile long COOLDOWN_MS = 10000L;", es))
es.addField(CtField.make("public static volatile boolean PART_TPA = true;", es))
es.addField(CtField.make("public static volatile boolean PART_MSG = true;", es))
es.addField(CtField.make('public static final String INFO = "#FFD37A";', es))
es.addField(CtField.make('public static final String OK = "#9CFF9C";', es))
es.addField(CtField.make('public static final String ERR = "#FF8A8A";', es))
es.addField(CtField.make('public static final String PM = "#E9A6FF";', es))
es.addField(CtField.make('public static final String FLY_PERM = "skyyessentials.fly";', es))
# 0.1.1 /r takeover state: config switch, our registered /r, and the vanilla /redo command whose "r" alias we hid (restored at shutdown)
es.addField(CtField.make("public static volatile boolean R_SHORTCUT = true;", es))
es.addField(CtField.make("public static java.nio.file.Path CFG;", es))
es.addField(CtField.make(f"public static {AC} R_CMD;", es))
es.addField(CtField.make(f"public static {AC} REDO;", es))
es.addField(CtField.make("public static boolean R_TAKEN = false;", es))
es.addMethod(CtNewMethod.make("""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyEssentials] " + m); } catch (Throwable t) { }
}""", es))
es.addMethod(CtNewMethod.make(f"""
public static {PR} online(java.util.UUID u) {{
  if (u == null) return null;
  {PR} p = {UNI}.get().getPlayer(u);
  return (p != null && p.isValid()) ? p : null;
}}""", es))
# the world a player is in right now (vanilla: ref.getStore().getExternalData() -> EntityStore.getWorld())
es.addMethod(CtNewMethod.make(f"""
public static {WLD} worldOf({PR} p) {{
  if (p == null) return null;
  try {{
    {REF} r = p.getReference();
    if (r != null) {{
      Object ext = r.getStore().getExternalData();
      if (ext instanceof {EST}) return (({EST}) ext).getWorld();
    }}
    java.util.UUID wu = p.getWorldUuid();
    if (wu != null) return {UNI}.get().getWorld(wu);
  }} catch (Throwable t) {{ }}
  return null;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void say({PR} p, String text, String color) {{
  if (p == null) return;
  try {{ p.sendMessage({MSG}.raw(text).color(color)); }} catch (Throwable t) {{ }}
}}""", es))
es.addMethod(CtNewMethod.make("""
public static void sayTo(java.util.UUID u, String text, String color) { say(online(u), text, color); }""", es))
# ---- 0.1.3 player Settings registry (research/Settings-Spec.md 1.3; SkyyMenu 0.2+). A CREATING bridge() (the SkillStore pattern: the
# map is made under System.class when no mod made it yet); a synchronized block holds exactly one call (javassist rule)
es.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", es))
es.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    return bridge0();
  }
}""", es))
# No SkyyMenu = no answer = today's behaviour (on). Never throws, never blocks (SkyyMenu's settings:fn:get is lock-free after the first
# read and never calls back), so it is safe inside the synchronized prune() (Settings-Spec guarantee 2)
es.addMethod(CtNewMethod.make("""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""", es))
es.addMethod(CtNewMethod.make("""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyEssentials", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""", es))
es.addMethod(CtNewMethod.make("""
public static String key(java.util.UUID a, java.util.UUID b) { return a.toString() + ">" + b.toString(); }""", es))
es.addMethod(CtNewMethod.make("""
public static String secs(long ms) { if (ms < 0L) ms = 0L; return ((ms + 999L) / 1000L) + "s"; }""", es))
# ---- 0.1.1 config (Skyy_SkyyEssentials/config.properties, read once in setup; restart to change)
# file replace: tmp + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyGuilds 0.1.1 / SkyyProfiles 0.1)
es.addMethod(CtNewMethod.make("""
public static void replaceFile(java.nio.file.Path tmp, java.nio.file.Path f) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      try {
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
      } catch (java.nio.file.AtomicMoveNotSupportedException a) {
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      }
      return;
    } catch (java.nio.file.NoSuchFileException e) {
      throw e;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""", es))
# 0.1.2: saveDefaultConfig / loadConfig moved to TCfg (config.properties now also carries the /trade keys; see TCfg below)
# ---- 0.1.1 /r helpers
# the text after the command name: CommandContext.getInputString() is the whole line without the slash ("r hello there"), the same
# string vanilla BanCommand/EventTitleCommand cut with CommandUtil.stripCommandName (and nhulston Essentials' /r with split("\\s+", 2))
es.addMethod(CtNewMethod.make("""
public static String argText(String raw) {
  if (raw == null) return "";
  String s = raw.trim();
  if (s.startsWith("/")) s = s.substring(1);
  int sp = s.indexOf(' ');
  if (sp < 0) return "";
  return s.substring(sp + 1).trim();
}""", es))
es.addMethod(CtNewMethod.make("""
public static boolean isCount(String s) {
  if (s == null || s.length() == 0 || s.length() > 4) return false;
  for (int i = 0; i < s.length(); i++) if (!Character.isDigit(s.charAt(i))) return false;
  return true;
}""", es))
# may this sender run vanilla /redo? (same check the command tree uses; handleCommand re-checks it anyway)
es.addMethod(CtNewMethod.make(f"""
public static boolean mayRedo({CSN} s) {{
  try {{
    if (s == null) return false;
    {AC} c = {CMG}.get().resolveCommand("redo");
    return c != null && c.hasPermission(s);
  }} catch (Throwable t) {{ return false; }}
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void forwardRedo({CSN} s, String line) {{
  try {{ {CMG}.get().handleCommand(s, line); }} catch (Throwable t) {{ warn("could not forward /r to /" + line + ": " + t); }}
}}""", es))
# AbstractCommand.aliases is a plain HashSet (private final, getAliases() returns it live) that CommandTreeBuilder.buildTreeEntry
# iterates on every login (GamePacketHandler) and PermissionsModule tree resend, on those threads. Editing it is race-free only while
# the engine refuses logins: InitialPacketHandler disconnects while !isBooted() (boot sets booted AFTER PluginManager.start(), so a
# normal start() is inside that window) and while isShuttingDown() (set in shutdownServer before PluginManager.shutdown()). Vanilla
# /plugin load|unload|reload can run start()/shutdown() with players online - then the Set is left alone (cosmetic: typed /r resolves
# the same either way, only the client's command list differs).
es.addMethod(CtNewMethod.make(f"""
public static boolean aliasEditSafe() {{
  try {{
    {HSV} s = {HSV}.get();
    return s != null && (!s.isBooted() || s.isShuttingDown());
  }} catch (Throwable t) {{ return false; }}
}}""", es))
# start(): hide "r" from RedoCommand's alias Set (client command list only; resolution already prefers our NAME "r") - but only when
# the registered top-level "r" is really ours (another mod set up after us would have replaced it: last registration wins)
es.addMethod(CtNewMethod.make(f"""
public static void claimR() {{
  try {{
    if (R_CMD == null) return;
    {CMG} cm = {CMG}.get();
    Object cur = cm.getCommandRegistration().get("r");
    if (cur != (Object) R_CMD) {{
      R_CMD = null;
      warn("another mod replaced /r after SkyyEssentials registered it - leaving it alone (players can use /reply).");
      return;
    }}
    {AC} redo = cm.resolveCommand("redo");
    if (redo == null || redo.getAliases() == null) return;
    if (!aliasEditSafe()) {{
      if (redo.getAliases().contains("r"))
        warn("loaded while the server is running (/plugin load or reload): /redo keeps its r alias in the client command list until the next restart, so builders may see r twice. /r works the same.");
      return;
    }}
    if (redo.getAliases().remove("r")) {{ REDO = redo; R_TAKEN = true; }}
  }} catch (Throwable t) {{ warn("could not tidy the /redo alias list: " + t); }}
}}""", es))
es.addMethod(CtNewMethod.make("""
public static void releaseR() {
  try {
    if (R_TAKEN && REDO != null && REDO.getAliases() != null && !REDO.getAliases().contains("r")) {
      if (aliasEditSafe()) REDO.getAliases().add("r");
      else warn("unloaded while the server is running: /redo's r alias stays out of the client command list until the next restart (typing /r still runs /redo for builders).");
    }
  } catch (Throwable t) { }
  R_TAKEN = false;
  REDO = null;
}""", es))
# ---- request book (all synchronized on EssStore.class)
es.addMethod(CtNewMethod.make(f"""
public static synchronized String tryAdd(java.util.UUID from, java.util.UUID to, boolean here, String fromName, String toName) {{
  long now = System.currentTimeMillis();
  {PKG}.TpReq old = ({PKG}.TpReq) REQ.get(key(from, to));
  if (old != null && old.expires > now)
    return "You already have a pending request to " + toName + " (" + secs(old.expires - now) + " left). /tpacancel to cancel it.";
  Long last = (Long) LAST_SENT.get(from);
  if (last != null && now - last.longValue() < COOLDOWN_MS)
    return "Please wait " + secs(COOLDOWN_MS - (now - last.longValue())) + " before sending another teleport request.";
  REQ.put(key(from, to), new {PKG}.TpReq(from, to, here, fromName, toName, now, now + EXPIRE_MS));
  LAST_SENT.put(from, Long.valueOf(now));
  return null;
}}""", es))
# newest live request addressed to `to` (optionally only from `from`); removed atomically so it can be accepted once
es.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.TpReq take(java.util.UUID to, java.util.UUID from) {{
  long now = System.currentTimeMillis();
  {PKG}.TpReq best = null;
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null || !r.to.equals(to) || r.expires <= now) continue;
    if (from != null && !r.from.equals(from)) continue;
    if (best == null || r.created > best.created) best = r;
  }}
  if (best != null) REQ.remove(key(best.from, best.to));
  return best;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static synchronized int pendingFor(java.util.UUID to) {{
  long now = System.currentTimeMillis();
  int n = 0;
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r != null && r.to.equals(to) && r.expires > now) n++;
  }}
  return n;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.List cancelFrom(java.util.UUID from) {{
  java.util.ArrayList out = new java.util.ArrayList();
  long now = System.currentTimeMillis();
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null || !r.from.equals(from)) continue;
    it.remove();
    if (r.expires > now) out.add(r);
  }}
  return out;
}}""", es))

# ================= HopDispatch (scheduler -> the right world thread, used for retries) =================
hop.addInterface(pool.get("java.lang.Runnable"))
hop.addField(CtField.make(f"public {PKG}.ReadDestTask rd;", hop))
hop.addField(CtField.make(f"public {PKG}.MoveTask mv;", hop))
hop.addConstructor(CtNewConstructor.make(f"""
public HopDispatch({PKG}.ReadDestTask rd, {PKG}.MoveTask mv) {{ this.rd = rd; this.mv = mv; }}""", hop))

# ================= MoveTask (runs on the MOVING player's world thread) =================
mv.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID moverU;", "public java.util.UUID destU;", "public String moverName;", "public String destName;",
          f"public {WLD} destWorld;", f"public {TRF} dest;", f"public {WLD} expected;", "public int attempts;"):
    mv.addField(CtField.make(f, mv))
mv.addConstructor(CtNewConstructor.make(f"""
public MoveTask(java.util.UUID moverU, java.util.UUID destU, String moverName, String destName, {WLD} destWorld, {TRF} dest) {{
  this.moverU = moverU; this.destU = destU; this.moverName = moverName; this.destName = destName;
  this.destWorld = destWorld; this.dest = dest; this.attempts = 0;
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void fail(String why) {{
  {ES}.sayTo(this.moverU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
  {ES}.sayTo(this.destU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void retryLater(String why) {{
  this.attempts++;
  if (this.attempts > 8) {{ fail(why); return; }}
  {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.HopDispatch(null, this), 500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void hop() {{
  {PR} m = {ES}.online(this.moverU);
  if (m == null) {{ fail(this.moverName + " went offline."); return; }}
  {WLD} w = {ES}.worldOf(m);
  if (w == null || !w.isAlive()) {{ retryLater(this.moverName + " is changing worlds, try again."); return; }}
  this.expected = w;
  w.execute(this);
}}""", mv))
# InstancesPlugin.teleportPlayerToInstance bookkeeping (bytecode-copied): when entering an instance world from another world,
# store the mover's current world + transform as the return-point override. makeWorldReturnPoint(from, t, false) is private, so
# it is rebuilt here: instanceName/instanceKey only when the FROM world is an instance with RespawnWhenTargeted and a key.
# 0.1.1: run() calls it BEFORE addComponent(Teleport). 0.1 called it after, which threw "Cannot invoke ArchetypeChunk... because
# archetypeChunk is null": Store.addComponent (outside a system tick) consumes its CommandBuffer before returning, and
# PlayerMoveSystem.teleportToWorld's buffered job does PlayerRef.removeFromStore() + destWorld.addPlayer(), so the Ref is dead by then.
# Vanilla InstancesPlugin.teleportPlayerToInstance: setReturnPointOverride -> TeleportHistory.append -> addComponent(Teleport) last;
# onPlayerAddToWorld reads the override from the Holder that removeFromStore carries into the new world.
# Returns true when an override was written (run() clears it again if the Teleport cannot be added).
mv.addMethod(CtNewMethod.make(f"""
public boolean markReturn({ST} st, {REF} ref, {WLD} here, {TC} mtc) {{
  try {{
    if (here == null || this.destWorld == null || here == this.destWorld) return false;
    if (mtc == null || mtc.getTransform() == null) return false;
    if ({IWC}.get(this.destWorld.getWorldConfig()) == null) return false;
    {WCF} hc = here.getWorldConfig();
    if (hc == null || hc.getUuid() == null) return false;
    {IWC} hic = {IWC}.get(hc);
    String iname = null;
    String ikey = null;
    if (hic != null && hic.shouldRespawnWhenTargeted() && hic.getInstanceKey() != null) {{
      iname = hic.getInstanceName();
      ikey = hic.getInstanceKey();
    }}
    {WRP} wrp = new {WRP}(hc.getUuid(), new {TRF}(mtc.getTransform()), false, iname, ikey);
    {IEC} iec = ({IEC}) st.ensureAndGetComponent(ref, {IEC}.getComponentType());
    if (iec != null) {{ iec.setReturnPointOverride(wrp); return true; }}
  }} catch (Throwable t) {{
    {ES}.warn("could not record the instance return point for " + this.moverName + ": " + t);
  }}
  return false;
}}""", mv))
mv.addMethod(CtNewMethod.make(f"""
public void clearReturn({ST} st, {REF} ref) {{
  try {{
    if (ref == null || !ref.isValid()) return;
    {IEC} iec = ({IEC}) st.getComponent(ref, {IEC}.getComponentType());
    if (iec != null) iec.setReturnPointOverride(({WRP}) null);
  }} catch (Throwable t) {{ }}
}}""", mv))
# 0.1.1: all bookkeeping on the mover's entity (return point, TeleportHistory) happens BEFORE addComponent(Teleport) - a cross-world
# Teleport removes the entity from this store inside addComponent (see markReturn), so nothing may touch ref after it
mv.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} m = {ES}.online(this.moverU);
    {PR} d = {ES}.online(this.destU);
    if (m == null) {{ fail(this.moverName + " went offline."); return; }}
    if (d == null) {{ fail(this.destName + " went offline."); return; }}
    {REF} ref = m.getReference();
    {WLD} here = {ES}.worldOf(m);
    if (ref == null || here == null || here != this.expected) {{ retryLater(this.moverName + " is changing worlds, try again."); return; }}
    if (this.destWorld == null || !this.destWorld.isAlive()) {{ fail("the destination world is closed."); return; }}
    {ST} st = ref.getStore();
    if (st.getComponent(ref, {TP}.getComponentType()) != null) {{ retryLater(this.moverName + " is already teleporting."); return; }}
    {TC} mtc = ({TC}) st.getComponent(ref, {TC}.getComponentType());
    {HR} mhr = ({HR}) st.getComponent(ref, {HR}.getComponentType());
    boolean marked = markReturn(st, ref, here, mtc);
    try {{
      if (mtc != null && mtc.getPosition() != null) {{
        {V3D} p = mtc.getPosition();
        {R3F} r = mhr != null ? mhr.getRotation() : null;
        {TPH} h = ({TPH}) st.ensureAndGetComponent(ref, {TPH}.getComponentType());
        if (h != null) h.append(here, new {V3D}(p.x, p.y, p.z), r != null ? new {R3F}(r.x, r.y, r.z) : new {R3F}(), "TPA to " + this.destName);
      }}
    }} catch (Throwable t2) {{ }}
    Throwable bad = null;
    try {{
      st.addComponent(ref, {TP}.getComponentType(), {TP}.createForPlayer(this.destWorld, this.dest));
    }} catch (Throwable t3) {{ bad = t3; }}
    if (bad != null) {{
      if (marked) clearReturn(st, ref);
      {ES}.warn("teleport failed: " + bad);
      fail("something went wrong.");
      return;
    }}
    {ES}.say(m, "[TPA] Teleporting to " + this.destName + ".", {ES}.OK);
  }} catch (Throwable t) {{
    {ES}.warn("teleport failed: " + t);
    fail("something went wrong.");
  }}
}}""", mv))

# ================= ReadDestTask (runs on the DESTINATION player's world thread) =================
rd.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID moverU;", "public java.util.UUID destU;", "public String moverName;", "public String destName;",
          f"public {WLD} expected;", "public int attempts;"):
    rd.addField(CtField.make(f, rd))
rd.addConstructor(CtNewConstructor.make("""
public ReadDestTask(java.util.UUID moverU, java.util.UUID destU, String moverName, String destName) {
  this.moverU = moverU; this.destU = destU; this.moverName = moverName; this.destName = destName; this.attempts = 0;
}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void fail(String why) {{
  {ES}.sayTo(this.moverU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
  {ES}.sayTo(this.destU, "[TPA] Teleport cancelled: " + why, {ES}.ERR);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void retryLater(String why) {{
  this.attempts++;
  if (this.attempts > 8) {{ fail(why); return; }}
  {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.HopDispatch(this, null), 500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void hop() {{
  {PR} d = {ES}.online(this.destU);
  if (d == null) {{ fail(this.destName + " went offline."); return; }}
  {WLD} w = {ES}.worldOf(d);
  if (w == null || !w.isAlive()) {{ retryLater(this.destName + " is changing worlds, try again."); return; }}
  this.expected = w;
  w.execute(this);
}}""", rd))
rd.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} m = {ES}.online(this.moverU);
    {PR} d = {ES}.online(this.destU);
    if (m == null) {{ fail(this.moverName + " went offline."); return; }}
    if (d == null) {{ fail(this.destName + " went offline."); return; }}
    {REF} ref = d.getReference();
    {WLD} here = {ES}.worldOf(d);
    if (ref == null || here == null || here != this.expected) {{ retryLater(this.destName + " is changing worlds, try again."); return; }}
    {ST} st = ref.getStore();
    {TC} tc = ({TC}) st.getComponent(ref, {TC}.getComponentType());
    if (tc == null || tc.getPosition() == null) {{ fail("could not read the position of " + this.destName + "."); return; }}
    {HR} hr = ({HR}) st.getComponent(ref, {HR}.getComponentType());
    {V3D} p = tc.getPosition();
    {R3F} r = hr != null ? hr.getRotation() : null;
    {TRF} tr = new {TRF}(new {V3D}(p.x, p.y, p.z), r != null ? new {R3F}(r.x, r.y, r.z) : new {R3F}());
    new {PKG}.MoveTask(this.moverU, this.destU, this.moverName, this.destName, here, tr).hop();
  }} catch (Throwable t) {{
    {ES}.warn("reading teleport destination failed: " + t);
    fail("something went wrong.");
  }}
}}""", rd))

hop.addMethod(CtNewMethod.make("""
public void run() {
  try {
    if (this.rd != null) this.rd.hop();
    if (this.mv != null) this.mv.hop();
  } catch (Throwable t) { }
}""", hop))

# ================= FlyTask (runs on the player's world thread; mode 1 = on, 0 = off, 2 = re-assert) =================
fly.addInterface(pool.get("java.lang.Runnable"))
for f in ("public java.util.UUID u;", "public int mode;", f"public {WLD} expected;", "public int attempts;"):
    fly.addField(CtField.make(f, fly))
fly.addConstructor(CtNewConstructor.make(f"""
public FlyTask(java.util.UUID u, int mode, {WLD} expected) {{ this.u = u; this.mode = mode; this.expected = expected; this.attempts = 0; }}""", fly))
fly.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {ES}.online(this.u);
    if (pr == null) return;
    {REF} ref = pr.getReference();
    {WLD} here = {ES}.worldOf(pr);
    if (ref == null || here == null || here != this.expected) {{
      if (this.mode != 2 && this.attempts < 3 && here != null) {{ this.attempts++; this.expected = here; here.execute(this); }}
      return;
    }}
    {ST} st = ref.getStore();
    {MM} mm = ({MM}) st.getComponent(ref, {MM}.getComponentType());
    if (mm == null) {{
      if (this.mode != 2) {ES}.say(pr, "[Fly] Could not change your flight right now, try again.", {ES}.ERR);
      return;
    }}
    if (this.mode == 0) {{
      {PLY} p = ({PLY}) st.getComponent(ref, {PLY}.getComponentType());
      {GM} gm = p != null ? p.getGameMode() : {GM}.Adventure;
      if (gm == null) gm = {GM}.Adventure;
      mm.resetFly(gm);
      mm.update(pr.getPacketHandler());
      {ES}.say(pr, "[Fly] Flight disabled." + (gm == {GM}.Creative ? " (Creative mode still lets you fly.)" : ""), {ES}.INFO);
      return;
    }}
    if (this.mode == 2 && !{ES}.FLY.containsKey(this.u)) return;
    {MS} s = mm.getSettings();
    {MS} d = mm.getDefaultSettings();
    boolean changed = false;
    if (s != null && s.fly != {FM}.Allowed && s.fly != {FM}.Forced) {{ s.fly = {FM}.Allowed; changed = true; }}
    if (d != null && d.fly != {FM}.Allowed && d.fly != {FM}.Forced) {{ d.fly = {FM}.Allowed; }}
    if (changed || this.mode == 1) mm.update(pr.getPacketHandler());
    if (this.mode == 1) {ES}.say(pr, "[Fly] Flight enabled - take off the same way as in creative. /fly again to turn it off.", {ES}.OK);
  }} catch (Throwable t) {{ {ES}.warn("fly task failed: " + t); }}
}}""", fly))

# ================= EssStore: prune + request actions (need the task classes above) =================
es.addMethod(CtNewMethod.make(f"""
public static synchronized void prune() {{
  long now = System.currentTimeMillis();
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null) {{ it.remove(); continue; }}
    {PR} f = online(r.from);
    {PR} t = online(r.to);
    if (f == null || t == null) {{
      it.remove();
      if (f != null && notifyOn(r.from, "tpa.updates")) say(f, "[TPA] " + r.toName + " went offline, your teleport request was cancelled.", INFO);
      if (t != null && notifyOn(r.to, "tpa.updates")) say(t, "[TPA] " + r.fromName + " went offline, their teleport request was cancelled.", INFO);
    }} else if (r.expires <= now) {{
      it.remove();
      if (notifyOn(r.from, "tpa.updates")) say(f, "[TPA] Your teleport request to " + r.toName + " expired.", INFO);
      if (notifyOn(r.to, "tpa.updates")) say(t, "[TPA] The teleport request from " + r.fromName + " expired.", INFO);
    }}
  }}
  it = LAST_SENT.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Long v = (Long) e.getValue();
    if (v == null || now - v.longValue() >= COOLDOWN_MS || online((java.util.UUID) e.getKey()) == null) it.remove();
  }}
  it = LAST_PM.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online((java.util.UUID) e.getKey()) == null || online((java.util.UUID) e.getValue()) == null) it.remove();
  }}
  it = FLY.keySet().iterator();
  while (it.hasNext()) {{
    java.util.UUID u = (java.util.UUID) it.next();
    {PR} p = online(u);
    if (p == null) {{ it.remove(); continue; }}
    boolean allowed = true;
    try {{ allowed = p.hasPermission(FLY_PERM); }} catch (Throwable t2) {{ }}
    if (!allowed) {{
      it.remove();
      {WLD} w = worldOf(p);
      if (w != null && w.isAlive()) w.execute(new {PKG}.FlyTask(u, 0, w));
    }}
  }}
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void request({PR} pr, Object t, boolean here) {{
  String cmd = here ? "/tpahere" : "/tpa";
  if (!PART_TPA) {{ say(pr, "[TPA] Teleport requests are turned off on this server.", ERR); return; }}
  if (!(t instanceof {PR})) {{ say(pr, "[TPA] Usage: " + cmd + " <player>", ERR); return; }}
  {PR} target = ({PR}) t;
  if (target.getUuid().equals(pr.getUuid())) {{ say(pr, "[TPA] You can't send a teleport request to yourself.", ERR); return; }}
  if (online(target.getUuid()) == null) {{ say(pr, "[TPA] " + target.getUsername() + " is not online.", ERR); return; }}
  String me = pr.getUsername();
  String them = target.getUsername();
  String err = tryAdd(pr.getUuid(), target.getUuid(), here, me, them);
  if (err != null) {{ say(pr, "[TPA] " + err, ERR); return; }}
  String ex = secs(EXPIRE_MS);
  if (here) {{
    say(pr, "[TPA] Asked " + them + " to teleport to you. They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + me + " wants you to teleport to them. /tpaccept " + me + " to go, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }} else {{
    say(pr, "[TPA] Request sent to " + them + ". They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + me + " wants to teleport to you. /tpaccept " + me + " to allow, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }}
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void accept({PR} pr, java.util.UUID from) {{
  if (!PART_TPA) {{ say(pr, "[TPA] Teleport requests are turned off on this server.", ERR); return; }}
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null) {{
    say(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
    return;
  }}
  {PR} req = online(r.from);
  if (req == null) {{ say(pr, "[TPA] " + r.fromName + " is no longer online.", ERR); return; }}
  java.util.UUID moverU = r.here ? r.to : r.from;
  java.util.UUID destU = r.here ? r.from : r.to;
  String moverName = r.here ? pr.getUsername() : req.getUsername();
  String destName = r.here ? req.getUsername() : pr.getUsername();
  if (r.here) {{
    say(pr, "[TPA] Accepted. Teleporting you to " + destName + "...", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted and is teleporting to you.", OK);
  }} else {{
    say(pr, "[TPA] Accepted. " + moverName + " is teleporting to you.", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted your request. Teleporting...", OK);
  }}
  int left = pendingFor(pr.getUuid());
  if (left > 0) say(pr, "[TPA] You still have " + left + " pending request(s). /tpaccept <player> or /tpdeny <player>.", INFO);
  new {PKG}.ReadDestTask(moverU, destU, moverName, destName).hop();
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void deny({PR} pr, java.util.UUID from) {{
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null) {{
    say(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
    return;
  }}
  say(pr, "[TPA] Denied the teleport request from " + r.fromName + ".", INFO);
  if (notifyOn(r.from, "tpa.updates")) sayTo(r.from, "[TPA] " + pr.getUsername() + " denied your teleport request.", ERR);
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void pm({PR} pr, {PR} target, String text) {{
  if (!PART_MSG) {{ say(pr, "Private messages are turned off on this server.", ERR); return; }}
  if (text == null) text = "";
  text = text.trim();
  if (text.length() == 0) {{ say(pr, "Usage: /msg <player> <message>", ERR); return; }}
  if (target == null || online(target.getUuid()) == null) {{ say(pr, "That player is not online.", ERR); return; }}
  if (target.getUuid().equals(pr.getUuid())) {{ say(pr, "You can't message yourself.", ERR); return; }}
  say(pr, "[you -> " + target.getUsername() + "] " + text, PM);
  say(target, "[" + pr.getUsername() + " -> you] " + text, PM);
  LAST_PM.put(pr.getUuid(), target.getUuid());
  LAST_PM.put(target.getUuid(), pr.getUuid());
}}""", es))
# /reply and /r share this (0.1.1; 0.1 had it inline in ReplyCmd)
es.addMethod(CtNewMethod.make(f"""
public static void reply({PR} pr, String text) {{
  if (!PART_MSG) {{ say(pr, "Private messages are turned off on this server.", ERR); return; }}
  java.util.UUID partner = (java.util.UUID) LAST_PM.get(pr.getUuid());
  if (partner == null) {{ say(pr, "Nobody to reply to yet. Use /msg <player> <message>.", ERR); return; }}
  {PR} target = online(partner);
  if (target == null) {{ LAST_PM.remove(pr.getUuid()); say(pr, "The player you were talking to is no longer online.", ERR); return; }}
  pm(pr, target, text);
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void rUsage({PR} pr) {{
  java.util.UUID partner = (java.util.UUID) LAST_PM.get(pr.getUuid());
  {PR} t = online(partner);
  say(pr, "Usage: /r <message>" + (t != null ? " - replies to " + t.getUsername() : " - replies to your last private message") + ". /msg <player> <message> starts a chat.", ERR);
}}""", es))
# /r <digits> went to /redo for a player who may redo: say so ONLY when they have an online message partner (the one case where they
# may have meant a reply); without a partner /r <n> could not have been a reply, so builders redoing get no extra line
es.addMethod(CtNewMethod.make(f"""
public static void redoNote({PR} pr, String n) {{
  java.util.UUID partner = (java.util.UUID) LAST_PM.get(pr.getUuid());
  {PR} t = online(partner);
  if (t == null) return;
  say(pr, "/r " + n + " ran /redo " + n + " (you can use builder tools), so nothing was sent to " + t.getUsername() + ". To reply with a number: /reply " + n, INFO);
}}""", es))

# ================= EssTick (scheduler, every 2s: fly re-assert; every 10s: prune) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public int n;", tick))
tick.addConstructor(CtNewConstructor.make("public EssTick() { this.n = 0; }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    this.n++;
    java.util.Iterator it = {ES}.FLY.keySet().iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      {PR} p = {ES}.online(u);
      if (p == null) continue;
      {WLD} w = {ES}.worldOf(p);
      if (w != null && w.isAlive()) w.execute(new {PKG}.FlyTask(u, 2, w));
    }}
    if (this.n % 5 == 0) {ES}.prune();
  }} catch (Throwable t) {{ {ES}.warn("tick failed: " + t); }}
}}""", tick))

# ================= commands =================
# Permission guard for these classes: they are all listed in OLD_CMDS, and the compiled permission check after writeFile (end of this
# script) stops the build BEFORE the jar is assembled when one of them lacks setPermissionGroups(hytale:Adventurer) or its
# requirePermission node - a dropped {ADV} fails this script, not only tools/ci/lint.py.
def player_cmd(cls, ctor_src, body):
    cls.addConstructor(CtNewConstructor.make(ctor_src, cls))
    cls.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
{body}
  }} catch (Throwable t) {{
    {ES}.warn("{cls.getSimpleName()} failed: " + t);
    {ES}.say(pr, "Something went wrong with that command.", {ES}.ERR);
  }}
}}""", cls))

# /tpa <player>
tpa.addField(CtField.make(f"public {RA} targetArg;", tpa))
player_cmd(tpa, f"""
public TpaCmd() {{
  super("tpa", "Ask a player if you may teleport to them");
  this.targetArg = withRequiredArg("player", "Player to teleport to", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"    {ES}.request(pr, ctx.get(this.targetArg), false);")
# /tpahere <player>
tph.addField(CtField.make(f"public {RA} targetArg;", tph))
player_cmd(tph, f"""
public TpaHereCmd() {{
  super("tpahere", "Ask a player to teleport to you");
  this.targetArg = withRequiredArg("player", "Player to bring to you", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"    {ES}.request(pr, ctx.get(this.targetArg), true);")
# /tpaccept <player> (usage variant, description-only constructor like vanilla WhereAmIOtherCommand)
tacn.addField(CtField.make(f"public {RA} fromArg;", tacn))
player_cmd(tacn, f"""
public TpAcceptNamedCmd() {{
  super("Accept the teleport request from this player");
  this.fromArg = withRequiredArg("player", "Player whose request to accept", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.fromArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "[TPA] Usage: /tpaccept [player]", {ES}.ERR); return; }}
    {ES}.accept(pr, (({PR}) t).getUuid());""")
player_cmd(tac, f"""
public TpAcceptCmd() {{
  super("tpaccept", "Accept a teleport request (newest, or /tpaccept <player>)");
  {ADV}
  addUsageVariant(new {PKG}.TpAcceptNamedCmd());
}}""", f"    {ES}.accept(pr, null);")
# /tpdeny [player]
tdnn.addField(CtField.make(f"public {RA} fromArg;", tdnn))
player_cmd(tdnn, f"""
public TpDenyNamedCmd() {{
  super("Deny the teleport request from this player");
  this.fromArg = withRequiredArg("player", "Player whose request to deny", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.fromArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "[TPA] Usage: /tpdeny [player]", {ES}.ERR); return; }}
    {ES}.deny(pr, (({PR}) t).getUuid());""")
player_cmd(tdn, f"""
public TpDenyCmd() {{
  super("tpdeny", "Deny a teleport request (newest, or /tpdeny <player>)");
  {ADV}
  addUsageVariant(new {PKG}.TpDenyNamedCmd());
}}""", f"    {ES}.deny(pr, null);")
# /tpacancel
player_cmd(tcan, f"""
public TpaCancelCmd() {{
  super("tpacancel", "Cancel your outgoing teleport requests");
  {ADV}
}}""", f"""    java.util.List l = {ES}.cancelFrom(pr.getUuid());
    if (l.isEmpty()) {{ {ES}.say(pr, "[TPA] You have no outgoing teleport requests.", {ES}.INFO); return; }}
    for (int i = 0; i < l.size(); i++) {{
      {PKG}.TpReq r = ({PKG}.TpReq) l.get(i);
      if ({ES}.notifyOn(r.to, "tpa.updates")) {ES}.sayTo(r.to, "[TPA] " + pr.getUsername() + " cancelled their teleport request.", {ES}.INFO);
    }}
    {ES}.say(pr, "[TPA] Cancelled " + l.size() + " teleport request(s).", {ES}.INFO);""")
# /msg <player> <message>  (aliases tell, w, whisper - none used by vanilla)
msg.addField(CtField.make(f"public {RA} targetArg;", msg))
msg.addField(CtField.make(f"public {RA} textArg;", msg))
player_cmd(msg, f"""
public MsgCmd() {{
  super("msg", "Send a private message to a player");
  this.targetArg = withRequiredArg("player", "Who to message", {ATY}.PLAYER_REF);
  this.textArg = withRequiredArg("message", "Your message", {ATY}.GREEDY_STRING);
  addAliases(new String[] {{ "tell", "w", "whisper" }});
  {ADV}
}}""", f"""    Object t = ctx.get(this.targetArg);
    Object m = ctx.get(this.textArg);
    if (!(t instanceof {PR})) {{ {ES}.say(pr, "Usage: /msg <player> <message>", {ES}.ERR); return; }}
    {ES}.pm(pr, ({PR}) t, m == null ? "" : m.toString());""")
# /reply <message>
rep.addField(CtField.make(f"public {RA} textArg;", rep))
player_cmd(rep, f"""
public ReplyCmd() {{
  super("reply", "Reply to the last player you messaged or who messaged you");
  this.textArg = withRequiredArg("message", "Your message", {ATY}.GREEDY_STRING);
  {ADV}
}}""", f"""    Object m = ctx.get(this.textArg);
    {ES}.reply(pr, m == null ? "" : m.toString());""")
# /r [message]  (0.1.1) - a top-level NAME "r" beats vanilla's r->redo alias in CommandManager.resolveCommand (docstring). No required
# argument + setAllowsExtraArguments(true) (the nhulston Essentials pattern) so a bare /r still reaches execute and can be handed to
# /redo for players who may use it; the message is read from the raw input line.
player_cmd(rcm, f"""
public RCmd() {{
  super("r", "Reply to your last private message: /r <message> (players who can /redo: /r alone or /r <count> still redoes)");
  setAllowsExtraArguments(true);
  {ADV}
}}""", f"""    String text = {ES}.argText(ctx.getInputString());
    {CSN} snd = ctx.sender();
    if (text.length() == 0) {{
      if ({ES}.mayRedo(snd)) {{ {ES}.forwardRedo(snd, "redo"); return; }}
      {ES}.rUsage(pr);
      return;
    }}
    if ({ES}.isCount(text) && {ES}.mayRedo(snd)) {{
      {ES}.forwardRedo(snd, "redo " + text);
      {ES}.redoNote(pr, text);
      return;
    }}
    {ES}.reply(pr, text);""")
# /fly (admin)
player_cmd(flc, f"""
public FlyCmd() {{
  super("fly", "Toggle flight (admin)");
  requirePermission("skyyessentials.fly");
}}""", f"""    java.util.UUID u = pr.getUuid();
    if ({ES}.FLY.remove(u) != null) {{
      new {PKG}.FlyTask(u, 0, world).run();
    }} else {{
      {ES}.FLY.put(u, Boolean.TRUE);
      new {PKG}.FlyTask(u, 1, world).run();
    }}""")

# =====================================================================================================================================
# 0.1.2 /trade (research/Trade-Spec.md). Written in the SkyyVault 0.1 token style (@PR@, @PKG@, ...) so the Java needs no doubled braces.
# Order matters (javassist compiles each method against what already exists): classes + fields + constructors first, then methods
# callee-before-caller: TCfg, TCodec, TRecord, TSession, TStore layer 1 (leaf helpers), TradePage part 1 (build), TCfgPage, TStore
# layers 2-5 (files, requests, sessions, settle, deliveries, commands, tick), then the bodies that call TStore (TradePage clicks, TChange,
# TWindow, TTask, TCountdown, TJob, listeners, tick), the commands and the plugin.
# =====================================================================================================================================
import re

T = {
    "PKG": PKG, "VERSION": VERSION, "ES": ES,
    "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "CTX": CTX, "MSG": MSG, "HSV": HSV, "ATY": ATY, "RA": RA,
    "LOG": LOG, "TC": TC, "VEC": V3D, "PLA": PLY, "APC": APC, "CMG": CMG, "JPI": JPI,
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC":  "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "FT":   "com.hypixel.hytale.server.core.inventory.container.filter.FilterType",
    "IST":  "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "CLT":  "com.hypixel.hytale.server.core.inventory.transaction.ClearTransaction",
    "INV":  "com.hypixel.hytale.server.core.inventory.Inventory",
    "CW":   "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow",
    "VWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow",
    "WIN":  "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "CA":   "com.hypixel.hytale.component.ComponentAccessor",
    "EREG": "com.hypixel.hytale.event.EventRegistration",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGE":  "com.hypixel.hytale.protocol.packets.interface_.Page",
    "IGS":  "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "ESM":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST":  "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "PRE":  "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":  "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "ADV":  'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    "ADMIN": 'requirePermission("skyyessentials.tradeadmin");',
    # 0.1.3 warps editor + world spawn
    "EADM": 'requirePermission("skyyessentials.admin");',
    "TPP":  "com.hypixel.hytale.builtin.teleport.TeleportPlugin",
    "WARP": "com.hypixel.hytale.builtin.teleport.Warp",
    "RPWE": "com.hypixel.hytale.builtin.teleport.commands.event.ReplaceWarpEvent",
    "RMWE": "com.hypixel.hytale.builtin.teleport.commands.event.RemoveWarpEvent",
    "MWE":  "com.hypixel.hytale.builtin.teleport.commands.event.ModifyWarpEvent",
    "IED":  "com.hypixel.hytale.event.IEventDispatcher",
    "IBE":  "com.hypixel.hytale.event.IBaseEvent",
    "GSP":  "com.hypixel.hytale.server.core.universe.world.spawn.GlobalSpawnProvider",
    "ISP":  "com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider",
    "WCF":  WCF, "IWC": IWC, "EST": EST, "HR": HR, "TRF": TRF, "R3F": R3F, "TPC": TP, "TPH": TPH,
}
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
WM = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"

# every engine member the trade code touches (API drift fails the build here, not in game)
for c, m in ((PGM, "openCustomPageWithWindows"), (PGM, "setPageWithWindows"), (PGM, "openCustomPage"), (PGM, "getCustomPage"),
             (PGM, "setPage"), (WM, "getWindow"), (WM, "closeWindow"), (T["WIN"], "getId"), (T["CW"], "onClose0"),
             (T["VWIN"], "validate"), (T["PGE"], "Bench"), (T["PGE"], "None"), (T["FT"], "DENY_ALL"), (T["FT"], "ALLOW_ALL"),
             (T["EREG"], "unregister"), (T["SIC"], "getItemStack"), (T["SIC"], "getCapacity"), (T["SIC"], "setGlobalFilter"),
             (T["IC"], "clear"), (T["CLT"], "getItems"), (T["IC"], "addItemStack"), (T["IC"], "registerChangeEvent"),
             (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "getDurability"), (T["IS"], "getMaxDurability"),
             (T["IS"], "getQualityIndex"), (T["IS"], "getMetadata"), (T["IS"], "getOverrideDroppedItemAnimation"),
             (T["IS"], "setOverrideDroppedItemAnimation"), (T["IS"], "isEmpty"), (T["IS"], "withQuantity"),
             (T["CODEC"], "encode"), (T["CODEC"], "decode"), (T["IST"], "getRemainder"),
             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"),
             (T["PLA"], "getInventory"), (T["PLA"], "getPageManager"), (T["PLA"], "getWindowManager"), (T["PLA"], "markNeedsSave"),
             (T["IGS"], "setActivatable"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["EVD"], "append"), (T["BT"], "Activating"), (T["BT"], "Validating"), (T["PAGE"], "rebuild"), (T["PAGE"], "sendUpdate"),
             (T["PAGE"], "handleDataEvent"), (T["PAGE"], "onDismiss"), (T["PAGE"], "close"), (T["LIFE"], "CanDismiss"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "get"), (T["DST"], "getHealth"),
             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"),
             (PB, "getEventRegistry"), (UNI, "getPlayers"), (PR, "getWorldUuid"), (PR, "getComponentType"),
             ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"), ("org.bson.json.JsonWriterSettings", "builder"),
             ("org.bson.json.JsonMode", "EXTENDED")):
    B.probe(pool, c, m)
# 0.1.3: every engine member the warps editor / world spawn code touches (the vanilla WarpSetCommand / WarpRemoveCommand / WarpCommand.tryGo
# / SpawnSetCommand / SpawnSetDefaultCommand calls, read with tools/dev/bcfull.py this session)
for c, m in ((T["TPP"], "get"), (T["TPP"], "getWarps"), (T["TPP"], "isWarpsLoaded"), (T["TPP"], "addWarp"), (T["TPP"], "removeWarp"),
             (T["WARP"], "getId"), (T["WARP"], "getWorld"), (T["WARP"], "getTransform"), (T["WARP"], "getCreator"),
             (T["WARP"], "getCreationDate"), (T["WARP"], "toTeleport"),
             (T["MWE"], "isCancelled"), (T["MWE"], "getCancelReason"), (T["IED"], "hasListener"), (T["IED"], "dispatch"),
             (HSV, "getEventBus"), ("com.hypixel.hytale.event.EventBus", "dispatchFor"),
             (WCF, "setSpawnProvider"), (WCF, "getSpawnProvider"), (WCF, "markChanged"), (WLD, "getName"), (UNI, "getWorld"),
             (TRF, "getPosition"), (TRF, "getRotation"), (T["PGE"], "None"), (PGM, "openCustomPage")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z][A-Z0-9]{1,6})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
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
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


tcfg  = pool.makeClass(PKG + ".TCfg")
tcod  = pool.makeClass(PKG + ".TCodec")
trec  = pool.makeClass(PKG + ".TRecord")
tses  = pool.makeClass(PKG + ".TSession")
tchg  = pool.makeClass(PKG + ".TChange")
twin  = pool.makeClass(PKG + ".TWindow", pool.get(T["CW"]))
tthr  = pool.makeClass(PKG + ".TThreads")
tjob  = pool.makeClass(PKG + ".TJob")
ttask = pool.makeClass(PKG + ".TTask")
tcd   = pool.makeClass(PKG + ".TCountdown")
tpage = pool.makeClass(PKG + ".TradePage", pool.get(T["PAGE"]))
tcpg  = pool.makeClass(PKG + ".TCfgPage", pool.get(T["PAGE"]))
tst   = pool.makeClass(PKG + ".TStore")
tfn   = pool.makeClass(PKG + ".TCancelFn")
trl   = pool.makeClass(PKG + ".TReadyL")
tql   = pool.makeClass(PKG + ".TQuitL")
ttk   = pool.makeClass(PKG + ".TTick")
TRADE_ALL = [tcfg, tcod, trec, tses, tchg, twin, tthr, tjob, ttask, tcd, tpage, tcpg, tst, tfn, trl, tql, ttk]
tchg.addInterface(pool.get("java.util.function.Consumer"))
trl.addInterface(pool.get("java.util.function.Consumer"))
tql.addInterface(pool.get("java.util.function.Consumer"))
tfn.addInterface(pool.get("java.util.function.Function"))
twin.addInterface(pool.get(T["VWIN"]))
tthr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
for c in (tjob, ttask, tcd, ttk):
    c.addInterface(pool.get("java.lang.Runnable"))

# ================= TCfg: config.properties (replyShortcut, the 0.1.3 teleport/message keys, the /trade keys), logger, bridge, atomic files, trade.log =================
# (key, label, type, java field, lo, hi, default, note, file comment). 0.1.3: the field may live in EssStore ("@ES@.NAME"); type "secms" =
# whole seconds in the file, milliseconds in the field (x 1000). The in-game editor is the config kit now (KIT_ROWS below): these rows are
# the mod's own LOADER (start + the kit's RELOAD after a hand edit) and the default file text. Labels / notes are kept for log lines only.
ROWS = [
    ("tradeEnabled", "Trading on", "bool", "ENABLED", 0, 1, "true", "Open trades finish normally.",
     "tradeEnabled: false turns /trade off (\"trading is turned off\"); open trades finish normally. /tpa /msg are not affected."),
    ("tradeSameWorld", "Both players in the same world", "bool", "SAME_WORLD", 0, 1, "true", "",
     "tradeSameWorld: true = both players must be in the same world to send, accept or keep a trade (false = any world)."),
    ("tradeDistance", "Max distance (blocks, 0 = none)", "int", "DIST", 0, 1000, "9", "Checked on send, accept and every second.",
     "tradeDistance: max blocks between the two players (on send, on accept and every second while trading; only inside one world). 0 = no limit."),
    ("tradeExpirySeconds", "Request expires after (s)", "int", "EXPIRE_S", 10, 600, "60", "",
     "tradeExpirySeconds: a trade request is dead after this many seconds (10-600)."),
    ("tradeCooldownSeconds", "Request cooldown (s)", "int", "COOLDOWN_S", 0, 300, "10", "",
     "tradeCooldownSeconds: seconds between two trade requests from the same player (0-300)."),
    ("tradeSlotsPerSide", "Offer slots per player", "int", "SLOTS", 4, 36, "16", "Applies to trades opened from now on.",
     "tradeSlotsPerSide: offer slots per player (4-36, default 16 = a 4 x 4 grid). Applies to trades opened after the change."),
    ("tradeCountdownSeconds", "Countdown after both Ready (s)", "int", "COUNTDOWN_S", 1, 30, "3", "",
     "tradeCountdownSeconds: seconds between both players being ready and the swap; offers are locked, Cancel still works (1-30)."),
    ("tradeCoinsAllowed", "Coins in trades (needs SkyyCoins)", "bool", "COINS", 0, 1, "true", "",
     "tradeCoinsAllowed: true = a coin box on the trade page when SkyyCoins is installed. false = items only."),
    ("tradeMaxCoins", "Max coins per trade (0 = no cap)", "long", "MAX_COINS", 0, 1000000000000000, "0", "",
     "tradeMaxCoins: the most coins one player can put in one trade. 0 = no cap."),
    ("tradeCancelOnDamage", "Cancel when a trader is hurt", "bool", "DAMAGE", 0, 1, "true", "",
     "tradeCancelOnDamage: true = a trade is cancelled (everything goes back) when either player loses health."),
    ("tradeOpenMode", "Offer slots open as", "mode", "PAGE_MODE", 0, 1, "page", "",
     "tradeOpenMode: page = the trade page with your offer slots beside it (Open as chest on the page is the fallback); chest = your offer opens as a chest at once."),
    ("tradeAfterSwitchSeconds", "Wait after a profile switch (s)", "int", "AFTER_S", 0, 120, "30", "",
     "tradeAfterSwitchSeconds: no new trade and no trade delivery this many seconds after a profile switch or crash recovery (SkyyProfiles keeps its switch marker 30 s)."),
    ("tradeSaveDelayMillis", "Save delay, Ready/coins (ms)", "int", "SAVE_MS", 100, 30000, "1000", "Item moves are always saved at once.",
     "tradeSaveDelayMillis: how soon a trade file is written after a Ready or coin-offer change. Items moved into or out of an offer, a settle, cancel, delivery or stop are always written at once."),
    ("replyShortcut", "/r replies to messages (restart)", "bool", "REPLY_FILE", 0, 1, "true", "Takes effect after a server restart.",
     "replyShortcut: true = /r replies to private messages (players allowed to /redo: /r alone or /r <count> still runs /redo). false = /r stays vanilla's /redo alias. Restart the server after a change."),
    # 0.1.3 (fields in EssStore)
    ("part.tpa", "Teleport requests on", "bool", "@ES@.PART_TPA", 0, 1, "true", "",
     "part.tpa: false turns /tpa, /tpahere and /tpaccept off (\"turned off on this server\"); /tpdeny and /tpacancel still work."),
    ("part.msg", "Private messages on", "bool", "@ES@.PART_MSG", 0, 1, "true", "",
     "part.msg: false turns /msg (tell, w, whisper), /reply and /r <text> off; /r alone and /r <count> still run /redo for builders."),
    ("tpa.expireSeconds", "Teleport request expires after (s)", "secms", "@ES@.EXPIRE_MS", 10, 600, "60", "",
     "tpa.expireSeconds: a /tpa or /tpahere request is dropped after this many seconds (10-600)."),
    ("tpa.cooldownSeconds", "Teleport request cooldown (s)", "secms", "@ES@.COOLDOWN_MS", 0, 300, "10", "",
     "tpa.cooldownSeconds: seconds a player waits before sending the next teleport request (0-300)."),
]
IDX = dict((r[0], i) for i, r in enumerate(ROWS))
REPLY_IDX = IDX["replyShortcut"]
# the default file: replyShortcut first (the 0.1.1 key), then the 0.1.3 teleport / message block, then the /trade block (0.1.2 order)
FILE_ORDER = [REPLY_IDX, IDX["part.tpa"], IDX["part.msg"], IDX["tpa.expireSeconds"], IDX["tpa.cooldownSeconds"]] + list(range(0, 13))
FILE_BLOCKS = {1: "# ---- teleports and private messages (SkyyEssentials 0.1.3) ----", 5: "# ---- /trade (SkyyEssentials 0.1.2) ----"}
N_ROWS = len(ROWS)
DEFAULT_LINES = ["# SkyyEssentials config - change it in game: SkyWynn Menu -> Server Setup -> Essentials, /tradeadmin config (the trade keys)",
                 "# or /warpadmin -> Settings (teleports and messages). Every change is written to this file at once, line by line.",
                 "# Or edit it here and run /tradeadmin reload. replyShortcut needs a server restart; everything else applies at once."]
for _k, _i in enumerate(FILE_ORDER):
    if _k in FILE_BLOCKS:
        DEFAULT_LINES.append("#")
        DEFAULT_LINES.append(FILE_BLOCKS[_k])
    DEFAULT_LINES.append("# " + ROWS[_i][8])
    DEFAULT_LINES.append("%s=%s" % (ROWS[_i][0], ROWS[_i][6]))
DEFAULT_TEXT = "\n".join(DEFAULT_LINES) + "\n"
if sorted(FILE_ORDER) != list(range(N_ROWS)):
    raise SystemExit("FILE_ORDER must list every TCfg row once")
for r in ROWS:
    typ, fld, dflt = r[2], r[3], r[6]
    if "." in fld:
        continue            # declared in EssStore (0.1.3 keys)
    if typ in ("bool",):
        F(tcfg, "public static volatile boolean %s = %s;" % (fld, dflt))
    elif typ == "mode":
        F(tcfg, "public static volatile boolean %s = %s;" % (fld, "true" if dflt == "page" else "false"))
    elif typ == "int":
        F(tcfg, "public static volatile int %s = %s;" % (fld, dflt))
    else:
        F(tcfg, "public static volatile long %s = %sL;" % (fld, dflt))
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path TDIR;", "public static java.nio.file.Path PDIR;",
          "public static java.nio.file.Path ADIR;", "public static java.nio.file.Path LOGF;", "public static java.nio.file.Path NAMESF;",
          "public static volatile boolean BROKEN = false;",
          'public static final String ADMIN = "skyyessentials.tradeadmin";',
          'public static final String EADMIN = "skyyessentials.admin";',
          "public static final Object LOGLOCK = new Object();",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();"):
    F(tcfg, f)
F(tcfg, "public static final String[] KEYS = %s;" % jarr([r[0] for r in ROWS]))
F(tcfg, "public static final String[] LABELS = %s;" % jarr([r[1] for r in ROWS]))
F(tcfg, "public static final String[] TYPES = %s;" % jarr([r[2] for r in ROWS]))
F(tcfg, "public static final String[] COMMENTS = %s;" % jarr([r[8] for r in ROWS]))
F(tcfg, "public static final String[] DEFAULTS = %s;" % jarr([r[6] for r in ROWS]))
F(tcfg, "public static final long[] LO = new long[] { %s };" % ", ".join("%dL" % r[4] for r in ROWS))
F(tcfg, "public static final long[] HI = new long[] { %s };" % ", ".join("%dL" % r[5] for r in ROWS))
F(tcfg, "public static final int[] FILE_ORDER = new int[] { %s };" % ", ".join(str(i) for i in FILE_ORDER))
F(tcfg, "public static final int REPLY_IDX = %d;" % REPLY_IDX)
F(tcfg, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT).replace("\n", "\\n"))
# the JVM-wide bridge map (created under System.class like every Skyy mod; a synchronized block holds one call in javassist)
M(tcfg, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(tcfg, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    return bridge0();
  }
}""")
M(tcfg, r"""
public static void warn(String m) { @ES@.warn(m); }""")
M(tcfg, r"""
public static void info(String m) {
  try { if (@ES@.LOG != null) @ES@.LOG.at(java.util.logging.Level.INFO).log("[SkyyEssentials] " + m); } catch (Throwable t) { }
}""")
M(tcfg, r"""
public static void warnOnce(String key, String msg) {
  long now = System.currentTimeMillis();
  Object last = WARNED.get(key);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  WARNED.put(key, Long.valueOf(now));
  warn(msg);
}""")
# tmp file + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyVault VCfg.atomicWrite / SkyyProfiles)
M(tcfg, r"""
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
M(tcfg, r"""
public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")
M(tcfg, r"""
public static void appendLine(java.nio.file.Path f, String line) {
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(f, (line + "\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { warnOnce("log", "could not append to " + f + ": " + t); }
}""")
# its own lock (not the TCfg class monitor): a config.properties write on the trade thread holds that monitor through an fsync, and
# world threads append trade.log lines
M(tcfg, r"""
public static void log(String line) {
  if (LOGF == null) return;
  String s = java.time.Instant.now().toString() + " " + line;
  synchronized (LOGLOCK) {
    appendLine(LOGF, s);
  }
}""")
# typed amounts: 2500, 2,500, 2k, 1.5m, 3b; -1 = not a number
M(tcfg, r"""
public static long parseAmount(String raw) {
  if (raw == null) return -1L;
  String s = raw.trim().toLowerCase().replace(",", "").replace("_", "").replace(" ", "");
  if (s.length() == 0 || s.length() > 20) return -1L;
  long mul = 1L;
  char last = s.charAt(s.length() - 1);
  if (last == 'k') mul = 1000L;
  else if (last == 'm') mul = 1000000L;
  else if (last == 'b') mul = 1000000000L;
  if (mul > 1L) s = s.substring(0, s.length() - 1);
  if (s.length() == 0) return -1L;
  int dot = s.indexOf('.');
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '.' && i == dot) continue;
    if (c < '0' || c > '9') return -1L;
  }
  try {
    if (dot >= 0) {
      if (mul == 1L) return -1L;
      double d = Double.parseDouble(s) * (double) mul;
      if (d < 0.0 || d > 9.0E17) return -1L;
      return (long) Math.floor(d + 0.0000001);
    }
    if (s.length() > 18) return -1L;
    long v = Long.parseLong(s);
    if (v > 900000000000000000L / mul) return -1L;
    return v * mul;
  } catch (Throwable t) { return -1L; }
}""")
# the generated get / put (one if per row; no String switch in javassist). 0.1.3: "secms" = seconds in the file, milliseconds in the field
get_lines, put_lines = [], []
for i, r in enumerate(ROWS):
    typ, fld = r[2], r[3]
    if typ == "bool":
        get_lines.append('  if (i == %d) return %s ? "true" : "false";' % (i, fld))
        put_lines.append('    if (i == %d) { %s = "true".equals(v); return true; }' % (i, fld))
    elif typ == "mode":
        get_lines.append('  if (i == %d) return %s ? "page" : "chest";' % (i, fld))
        put_lines.append('    if (i == %d) { %s = !"chest".equals(v); return true; }' % (i, fld))
    elif typ == "int":
        get_lines.append('  if (i == %d) return String.valueOf(%s);' % (i, fld))
        put_lines.append('    if (i == %d) { %s = (int) Long.parseLong(v); return true; }' % (i, fld))
    elif typ == "secms":
        get_lines.append('  if (i == %d) return String.valueOf(%s / 1000L);' % (i, fld))
        put_lines.append('    if (i == %d) { %s = Long.parseLong(v) * 1000L; return true; }' % (i, fld))
    else:
        get_lines.append('  if (i == %d) return String.valueOf(%s);' % (i, fld))
        put_lines.append('    if (i == %d) { %s = Long.parseLong(v); return true; }' % (i, fld))
M(tcfg, "public static String get(int i) {\n%s\n  return \"\";\n}" % "\n".join(get_lines))
M(tcfg, "public static boolean put(int i, String v) {\n  try {\n%s\n  } catch (Throwable t) { }\n  return false;\n}" % "\n".join(put_lines))
# canonical text or null: bool / mode words (the loader's reading of a file value; typed values are validated by the config kit)
M(tcfg, r"""
public static String canon(int i, String raw) {
  if (raw == null) return null;
  String v = raw.trim().toLowerCase();
  String t = TYPES[i];
  if (t.equals("bool")) {
    if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return "true";
    if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return "false";
    return null;
  }
  if (t.equals("mode")) {
    if (v.equals("page") || v.equals("chest")) return v;
    return null;
  }
  long n = parseAmount(v);
  if (n < 0L || n < LO[i] || n > HI[i]) return null;
  return String.valueOf(n);
}""")
# read from the file: bad text -> null (value kept, warned); numbers out of range are CLAMPED (and warned), like every Skyy load()
M(tcfg, r"""
public static String canonFile(int i, String raw) {
  String t = TYPES[i];
  if (t.equals("bool") || t.equals("mode")) return canon(i, raw);
  long n = parseAmount(raw == null ? "" : raw.trim());
  if (n < 0L) return null;
  if (n < LO[i]) { warn("config.properties: " + KEYS[i] + "=" + raw + " is below " + LO[i] + " - using " + LO[i]); n = LO[i]; }
  if (n > HI[i]) { warn("config.properties: " + KEYS[i] + "=" + raw + " is above " + HI[i] + " - using " + HI[i]); n = HI[i]; }
  return String.valueOf(n);
}""")
M(tcfg, r"""
public static String rule(int i) {
  String t = TYPES[i];
  if (t.equals("bool")) return "use true or false";
  if (t.equals("mode")) return "use page or chest";
  return "use a whole number from " + LO[i] + " to " + HI[i];
}""")
M(tcfg, r"""
public static String summary0() {
  return "trade " + (ENABLED ? "on" : "OFF") + ", " + (SAME_WORLD ? "same world" : "any world") + ", " + (DIST > 0 ? "within " + DIST + " blocks" : "no distance limit")
    + ", " + SLOTS + " slots, countdown " + COUNTDOWN_S + " s, coins " + (COINS ? "allowed" : "off") + ", openMode " + (PAGE_MODE ? "page" : "chest")
    + "; tpa " + (@ES@.PART_TPA ? "on" : "OFF") + " (expire " + (@ES@.EXPIRE_MS / 1000L) + " s, cooldown " + (@ES@.COOLDOWN_MS / 1000L) + " s), msg " + (@ES@.PART_MSG ? "on" : "OFF");
}""")
M(tcfg, r"""
public static java.util.Properties readProps() throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(@ES@.CFG, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""")
# a missing file gets the default text (the kit's DEFAULTS are the same text); null = written, else the reason
M(tcfg, r"""
public static synchronized String saveDefault() {
  try {
    atomicWrite(@ES@.CFG, DEFAULT_TEXT.getBytes("ISO-8859-1"));
    return null;
  } catch (Throwable t) {
    warn("could not write " + @ES@.CFG + ": " + t);
    return String.valueOf(t);
  }
}""")
# 0.1.3: keys a readable file does not have yet (a 0.1.1 / 0.1.2 file) are APPENDED at the end with their comment and default - every
# existing byte stays as it is (0.1.2 rewrote the whole file and lost hand-written comments). Runs at start only, before the config kit
# reads the file (so the kit never races it). Line ending = the file's own.
M(tcfg, r"""
public static synchronized String appendMissing(boolean[] miss) {
  try {
    byte[] cur = java.nio.file.Files.readAllBytes(@ES@.CFG);
    String txt = new String(cur, "ISO-8859-1");
    String nl = "\n";
    if (txt.indexOf("\r\n") >= 0) nl = "\r\n";
    StringBuilder sb = new StringBuilder();
    if (txt.length() > 0 && !txt.endsWith("\n")) sb.append(nl);
    sb.append("#").append(nl).append("# ---- added by SkyyEssentials @VERSION@ (keys this file did not have yet, with their defaults) ----").append(nl);
    for (int k = 0; k < FILE_ORDER.length; k++) {
      int i = FILE_ORDER[k];
      if (!miss[i]) continue;
      sb.append("# ").append(COMMENTS[i]).append(nl);
      sb.append(KEYS[i]).append("=").append(get(i)).append(nl);
    }
    byte[] add = sb.toString().getBytes("ISO-8859-1");
    byte[] out = new byte[cur.length + add.length];
    System.arraycopy(cur, 0, out, 0, cur.length);
    System.arraycopy(add, 0, out, cur.length, add.length);
    atomicWrite(@ES@.CFG, out);
    return null;
  } catch (Throwable t) {
    warn("could not add the missing keys to " + @ES@.CFG + " (the defaults are used; the file is unchanged): " + t);
    return String.valueOf(t);
  }
}""")
# start (setup): missing file -> written with the defaults; unreadable -> BROKEN (never overwritten; the kit refuses in-game changes to it
# until it reads); readable -> every key parsed (clamped like 0.1.2) and the missing keys appended
M(tcfg, r"""
public static synchronized String load() {
  try {
    if (@ES@.CFG == null) return "no config path";
    java.nio.file.Files.createDirectories(@ES@.CFG.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(@ES@.CFG, new java.nio.file.LinkOption[0])) {
      BROKEN = false;
      String e = saveDefault();
      return summary0() + (e == null ? " (new config.properties written)" : " (config.properties could not be written)");
    }
    java.util.Properties p = readProps();
    boolean[] miss = new boolean[KEYS.length];
    int n = 0;
    for (int i = 0; i < KEYS.length; i++) {
      String raw = p.getProperty(KEYS[i]);
      if (raw == null) { miss[i] = true; n++; continue; }
      String c = canonFile(i, raw);
      if (c == null) { warn("config.properties: " + KEYS[i] + "=" + raw + " is not valid (" + rule(i) + ") - keeping " + get(i)); continue; }
      put(i, c);
    }
    BROKEN = false;
    if (n > 0) {
      String e = appendMissing(miss);
      if (e == null) info("config.properties: added " + n + " missing key(s) at the end with their defaults - every existing line kept");
    }
    return summary0();
  } catch (Throwable t) {
    BROKEN = true;
    warn("could not read " + @ES@.CFG + " - keeping the current values and NOT overwriting the file; in-game changes are refused until it reads. Fix it, or delete it to get fresh defaults: " + t);
    return summary0() + " (config.properties unreadable)";
  }
}""")
# the config kit's RELOAD (tools/CONFIG-CONTRACT.md): after a hand edit is found (at the kit's next write of the file, "Reload file",
# /tradeadmin reload or SkyyMenu's Reload), the kit writes the file and then calls this, outside every kit lock, on the scheduler thread.
# Re-reads every LIVE key (a key removed by hand goes back to its default, as the kit shows it); never replyShortcut - a restart key the
# kit tracks itself (spec: a reload routine must not apply restart keys it happens to re-read). No world access.
M(tcfg, r"""
public static void reloadKit() {
  try {
    if (@ES@.CFG == null) return;
    java.util.Properties p = readProps();
    for (int i = 0; i < KEYS.length; i++) {
      if (i == REPLY_IDX) continue;
      String raw = p.getProperty(KEYS[i]);
      String c = null;
      if (raw == null) c = DEFAULTS[i]; else c = canonFile(i, raw);
      if (c == null) { warn("config.properties: " + KEYS[i] + "=" + raw + " is not valid (" + rule(i) + ") - keeping " + get(i)); continue; }
      put(i, c);
    }
    BROKEN = false;
  } catch (Throwable t) { warn("could not re-read " + @ES@.CFG + " after a hand edit (values kept): " + t); }
}""")
# the kit's custom: row tradeOpenMode (a choice row over the 0.1.2 boolean PAGE_MODE; the kit validated the value already). customSet
# hands the file line back to the kit (written through, versioned, logged); customRead makes it restorable from History.
M(tcfg, r"""
public static String customGet(String key) {
  if ("tradeOpenMode".equals(key)) return PAGE_MODE ? "page" : "chest";
  return null;
}""")
M(tcfg, r"""
public static Object[] customSet(String key, String value) {
  if (!"tradeOpenMode".equals(key)) return new Object[] { "unknown", null, "Unknown setting: " + key + "." };
  String v = "page";
  if ("chest".equals(value)) v = "chest";
  PAGE_MODE = v.equals("page");
  return new Object[] { "ok", v, null, new String[] { "tradeOpenMode", v } };
}""")
M(tcfg, r"""
public static String customRead(String key, java.util.Map m) {
  if (!"tradeOpenMode".equals(key) || m == null) return null;
  Object o = m.get("tradeOpenMode");
  if (o == null) return null;
  String s = String.valueOf(o).trim().toLowerCase();
  if (s.equals("page") || s.equals("chest")) return s;
  return null;
}""")

# ================= 0.1.3 EssPerm: the config kit's permission check (PERM_FN) =================
# The kit re-checks NODE (skyyessentials.admin) on every change. The /tradeadmin config page and /tradeadmin reload (requirePermission
# skyyessentials.tradeadmin, 0.1.2) set TRADE around their own kit calls, so a holder of only skyyessentials.tradeadmin keeps changing
# the trade keys there exactly as in 0.1.2 - but not from SkyyMenu Server Setup (TRADE is never set on that path). A ThreadLocal: the
# flag belongs to the one call on this thread, never to another player's click. Same engine call the kit makes by default; false on error.
eperm = pool.makeClass(PKG + ".EssPerm")
PMOD = "com.hypixel.hytale.server.core.permissions.PermissionsModule"
B.probe(pool, PMOD, "get")
B.probe(pool, PMOD, "hasPermission")
F(eperm, "public static final ThreadLocal TRADE = new ThreadLocal();")
M(eperm, r"""
public static boolean has(java.util.UUID who, String node) {
  if (who == null || node == null) return false;
  try {
    if (%s.get().hasPermission(who, node)) return true;
    if (Boolean.TRUE.equals(TRADE.get())) return %s.get().hasPermission(who, "skyyessentials.tradeadmin");
  } catch (Throwable t) { }
  return false;
}""" % (PMOD, PMOD))
M(eperm, r"""public static void tradeOn() { TRADE.set(Boolean.TRUE); }""")
M(eperm, r"""public static void tradeOff() { TRADE.remove(); }""")

# ================= 0.1.3 the admin config kit (research/Server-Setup-Spec.md 4.6 + 5.4 + section 3; tools/CONFIG-CONTRACT.md) =================
# Same file, same keys as 0.1.2 (a row key may differ from its file key: part.trade -> tradeEnabled). Ranges = the TCfg loader's clamps
# (so the kit's start-up clamp check never reports a value the loader accepted). RELOAD = TCfg.reloadKit (hand edits).
EWARP = pool.makeClass(PKG + ".EssWarp")
KIT_CATS = [("parts", "Parts"), ("tpa", "Teleports"), ("msg", "Messages"), ("warps", "Warps"), ("trade", "Trade")]
CF = "@config.properties:"
KIT_ROWS = [
    ("part.tpa", "Teleport requests", "parts", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: /tpa, /tpahere and /tpaccept say they are turned off. /tpdeny and /tpacancel still work.",
     "field:EssStore.PART_TPA" + CF + "part.tpa"),
    ("part.msg", "Private messages", "parts", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: /msg, /reply and /r replies say they are turned off. /r alone still redoes for builders.",
     "field:EssStore.PART_MSG" + CF + "part.msg"),
    ("part.trade", "Trading", "parts", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: new trade requests and accepts are refused. Open trades finish; /trade claim still works.",
     "field:TCfg.ENABLED" + CF + "tradeEnabled"),
    ("tpa.expireSeconds", "Teleport request expires after", "tpa", "int", "60", "10", "600", "step=5", "s", "live",
     "A /tpa or /tpahere request is dropped after this long (requests sent from now on).",
     "field:EssStore.EXPIRE_MS*1000" + CF + "tpa.expireSeconds"),
    ("tpa.cooldownSeconds", "Cooldown between teleport requests", "tpa", "int", "10", "0", "300", "step=5", "s", "live",
     "How long a player waits before sending the next teleport request.",
     "field:EssStore.COOLDOWN_MS*1000" + CF + "tpa.cooldownSeconds"),
    ("replyShortcut", "/r replies to private messages", "msg", "bool", "true", "", "", "", "", "restart",
     "On: /r replies (builders: /r alone or /r with a number still redoes). Off: /r is only /redo.",
     "field:TCfg.REPLY_FILE" + CF + "replyShortcut"),
    ("warps.editor", "Warps editor", "warps", "link", "", "", "", "warpadmin", "", "",
     "Add, move, rename, remove and visit the /warp warps. It also sets the world spawn.", ""),
    ("spawn.set", "Set the world spawn here", "warps", "action", "", "", "", "Set the world spawn here", "", "danger",
     "Moves the spawn of the world you stand in to your spot. New and respawning players arrive there.",
     "action:EssWarp.kitSpawnSet"),
    ("spawn.reset", "Reset the world spawn to the original", "warps", "action", "", "", "", "Reset the world spawn", "", "danger",
     "The world you stand in goes back to its original spawn point (like /spawn set default).",
     "action:EssWarp.kitSpawnReset"),
    ("tradeSameWorld", "Traders must be in the same world", "trade", "bool", "true", "", "", "", "", "live",
     "Off: players in different worlds may send, accept and keep a trade.", "field:TCfg.SAME_WORLD" + CF + "tradeSameWorld"),
    ("tradeDistance", "Max distance between traders", "trade", "int", "9", "0", "1000", "", "blocks", "live",
     "0 = no limit. Checked on send, on accept and every second (inside one world).", "field:TCfg.DIST" + CF + "tradeDistance"),
    ("tradeExpirySeconds", "Trade request expires after", "trade", "int", "60", "10", "600", "step=5", "s", "live",
     "A /trade request is dead after this long.", "field:TCfg.EXPIRE_S" + CF + "tradeExpirySeconds"),
    ("tradeCooldownSeconds", "Cooldown between trade requests", "trade", "int", "10", "0", "300", "step=5", "s", "live",
     "Seconds between two trade requests from the same player.", "field:TCfg.COOLDOWN_S" + CF + "tradeCooldownSeconds"),
    ("tradeSlotsPerSide", "Offer slots per player", "trade", "int", "16", "4", "36", "", "", "new",
     "16 = a 4 x 4 grid. Trades opened after the change use it.", "field:TCfg.SLOTS" + CF + "tradeSlotsPerSide"),
    ("tradeCountdownSeconds", "Countdown after both are Ready", "trade", "int", "3", "1", "30", "", "s", "live",
     "Offers are locked during it; Cancel trade still works.", "field:TCfg.COUNTDOWN_S" + CF + "tradeCountdownSeconds"),
    ("tradeCoinsAllowed", "Coins in trades", "trade", "bool", "true", "", "", "", "", "live",
     "A coin box on the trade page when SkyyCoins is installed. Off: items only.", "field:TCfg.COINS" + CF + "tradeCoinsAllowed"),
    ("tradeMaxCoins", "Max coins per trade", "trade", "int", "0", "0", "1000000000000000", "", "coins", "live",
     "The most coins one player can put in one trade. 0 = no cap.", "field:TCfg.MAX_COINS" + CF + "tradeMaxCoins"),
    ("tradeCancelOnDamage", "Cancel when a trader is hurt", "trade", "bool", "true", "", "", "", "", "live",
     "A trade is cancelled (everything goes back) when either player loses health.", "field:TCfg.DAMAGE" + CF + "tradeCancelOnDamage"),
    ("tradeOpenMode", "Offer slots open as", "trade", "choice", "page", "", "", "page|Trade page,chest|Chest window", "", "live",
     "Trade page = your slots beside the page (Open as chest is the fallback). Chest = a chest at once.",
     "custom:TCfg@config.properties:tradeOpenMode"),
    ("tradeAfterSwitchSeconds", "Wait after a profile switch", "trade", "int", "30", "0", "120", "step=5", "s", "live,adv,danger",
     "No trade or delivery this long after a switch. Under 30 s risks duplicates (SkyyProfiles marker).",
     "field:TCfg.AFTER_S" + CF + "tradeAfterSwitchSeconds;confirm=down"),
    ("tradeSaveDelayMillis", "Save delay for Ready and coins", "trade", "int", "1000", "100", "30000", "", "ms", "live,adv",
     "How soon a trade file is written after a Ready or coin change. Item moves are saved at once.",
     "field:TCfg.SAVE_MS" + CF + "tradeSaveDelayMillis"),
]
# the two in-game pages that edit these rows without SkyyMenu (TCfgPage): /tradeadmin config (0.1.2's keys, node tradeadmin) and
# /warpadmin -> Settings (the 0.1.3 teleport / message keys, node admin)
TRADE_PAGE_KEYS = ["part.trade", "tradeSameWorld", "tradeDistance", "tradeExpirySeconds", "tradeCooldownSeconds", "tradeSlotsPerSide",
                   "tradeCountdownSeconds", "tradeCoinsAllowed", "tradeMaxCoins", "tradeCancelOnDamage", "tradeOpenMode",
                   "tradeAfterSwitchSeconds", "tradeSaveDelayMillis", "replyShortcut"]
ESS_PAGE_KEYS = ["part.tpa", "part.msg", "tpa.expireSeconds", "tpa.cooldownSeconds", "replyShortcut"]
_kit_keys = [r[0] for r in KIT_ROWS]
for _k in TRADE_PAGE_KEYS + ESS_PAGE_KEYS:
    if _k not in _kit_keys:
        raise SystemExit("page key %s is not a kit row" % _k)
# every TCfg loader key is bound by exactly one kit row (the file and the game always agree)
_bound = set()
for r in KIT_ROWS:
    if "@config.properties:" in r[11]:
        _bound.add(r[11].split("@config.properties:")[1].split(";")[0])
if _bound != set(x[0] for x in ROWS):
    raise SystemExit("kit rows and TCfg loader keys differ: %s" % sorted(_bound ^ set(x[0] for x in ROWS)))
kit = CFG.emit(pool, PKG, MOD="SkyyEssentials", TITLE="Essentials", VERSION=VERSION, NODE="skyyessentials.admin", CATS=KIT_CATS,
               ROWS=KIT_ROWS, FILES=["Skyy_SkyyEssentials/config.properties"],
               NOTE="Warps + world spawn: Warps editor (/warpadmin). Trade keys also on /tradeadmin config.",
               RELOAD="TCfg.reloadKit", KEEP=20, DEFAULTS={"config.properties": DEFAULT_TEXT}, PERM_FN="EssPerm.has")

# ================= TCodec: the SkyyVault 0.1 / SkyyProfiles 0.1 lossless slot format =================
M(tcod, r"""
public static int intOf(org.bson.BsonDocument d, String k, int def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(tcod, r"""
public static long lngOf(org.bson.BsonDocument d, String k, long def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return def;
}""")
M(tcod, r"""
public static double dblOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return 0.0;
}""")
M(tcod, r"""
public static String strOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return null;
}""")
M(tcod, r"""
public static boolean boolOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isBoolean()) return v.asBoolean().getValue(); } catch (Throwable t) { }
  return false;
}""")
M(tcod, r"""
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
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("enc-" + s.getItemId(), "ItemStack.CODEC could not encode " + s.getItemId() + " (explicit fields kept): " + t); }
  return d;
}""")
# engine codec first (exact engine persistence), explicit fields as the fallback; null = cannot be rebuilt (the doc is kept as it is)
M(tcod, r"""
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
M(tcod, r"""
public static String toJson(org.bson.BsonDocument d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")
# stacks -> slot docs (slot = index in the array); empty slots skipped
M(tcod, r"""
public static java.util.ArrayList docList(@IS@[] a) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (a == null) return l;
  for (int i = 0; i < a.length; i++) {
    if (a[i] == null || a[i].isEmpty()) continue;
    l.add(slotDoc(i, a[i]));
  }
  return l;
}""")
M(tcod, r"""
public static org.bson.BsonArray docArray(java.util.List l) {
  org.bson.BsonArray a = new org.bson.BsonArray();
  if (l == null) return a;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof org.bson.BsonDocument) a.add((org.bson.BsonDocument) ((org.bson.BsonDocument) o).clone());
  }
  return a;
}""")
M(tcod, r"""
public static java.util.ArrayList listOf(org.bson.BsonArray a) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (a == null) return l;
  for (int i = 0; i < a.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) a.get(i);
    if (v != null && v.isDocument()) l.add(v.asDocument());
  }
  return l;
}""")
M(tcod, r"""
public static int qtyOf(java.util.List l) {
  int n = 0;
  if (l == null) return 0;
  for (int i = 0; i < l.size(); i++) {
    Object o = l.get(i);
    if (o instanceof org.bson.BsonDocument) n = n + intOf((org.bson.BsonDocument) o, "qty", 0);
  }
  return n;
}""")

# ================= TRecord: the persistent half of a trade (trades/pending/<id>.json), and after it settles, what is still owed =================
# state ACTIVE = a live trade (items = the escrow right now); SETTLING = decided (result COMPLETED | CANCELLED), owe lists = what each
# player still gets. All mutators are synchronized instance methods and bump rev; writes are rev-ordered under ioLock (TStore.writeLocked).
for f in ("public String id;", "public java.util.UUID ua;", "public java.util.UUID ub;", "public String na;", "public String nb;",
          "public long startedAt;", "public long endedAt;", "public String state;", "public String result;", "public String reason;",
          "public @IS@[] liveA;", "public @IS@[] liveB;", "public org.bson.BsonArray itemsA;", "public org.bson.BsonArray itemsB;",
          "public long coinsA;", "public long coinsB;", "public boolean readyA;", "public boolean readyB;",
          "public java.util.ArrayList oweA;", "public java.util.ArrayList oweB;", "public long coinOweA;", "public long coinOweB;",
          "public volatile long rev;", "public volatile long writtenRev;", "public Object ioLock;", "public volatile long lastFail;",
          "public String keyA;", "public String keyB;", "public boolean paying;", "public boolean paidA;", "public boolean paidB;"):
    F(trec, f)
C(trec, r"""
public TRecord(String id, java.util.UUID ua, String na, java.util.UUID ub, String nb, int cap, long now) {
  this.id = id; this.ua = ua; this.na = na == null ? "" : na; this.ub = ub; this.nb = nb == null ? "" : nb;
  this.startedAt = now; this.endedAt = 0L; this.state = "ACTIVE"; this.result = ""; this.reason = "";
  this.liveA = null; this.liveB = null;
  if (cap > 0) { this.liveA = new @IS@[cap]; this.liveB = new @IS@[cap]; }
  this.itemsA = new org.bson.BsonArray(); this.itemsB = new org.bson.BsonArray();
  this.coinsA = 0L; this.coinsB = 0L; this.readyA = false; this.readyB = false;
  this.oweA = new java.util.ArrayList(); this.oweB = new java.util.ArrayList(); this.coinOweA = 0L; this.coinOweB = 0L;
  this.rev = 1L; this.writtenRev = 0L; this.ioLock = new Object(); this.lastFail = 0L;
  this.keyA = ""; this.keyB = "";
  this.paying = false; this.paidA = false; this.paidB = false;
}""")
M(trec, r"""
public java.util.UUID uOf(int side) { return side == 0 ? this.ua : this.ub; }""")
M(trec, r"""
public String nameOf(int side) { return side == 0 ? this.na : this.nb; }""")
# "" = any profile (records written before 0.1.2 kept keys, or no SkyyProfiles)
M(trec, r"""
public String keyOf(int side) {
  String k = side == 0 ? this.keyA : this.keyB;
  return k == null ? "" : k;
}""")
# the escrow view -> the record (every change event); true when anything changed
M(trec, r"""
public synchronized boolean copyIn(int side, @IS@[] now) {
  @IS@[] a = side == 0 ? this.liveA : this.liveB;
  if (a == null || !"ACTIVE".equals(this.state)) return false;
  boolean ch = false;
  for (int i = 0; i < a.length && i < now.length; i++) {
    if (a[i] != now[i]) { a[i] = now[i]; ch = true; }
  }
  if (ch) this.rev = this.rev + 1L;
  return ch;
}""")
M(trec, r"""
public synchronized void setOffer(int side, long coins, boolean ready) {
  if (!"ACTIVE".equals(this.state)) return;
  if (side == 0) { this.coinsA = coins; this.readyA = ready; } else { this.coinsB = coins; this.readyB = ready; }
  this.rev = this.rev + 1L;
}""")
M(trec, r"""
public static org.bson.BsonArray arr(java.util.List l) { return @PKG@.TCodec.docArray(l); }""")
M(trec, r"""
public org.bson.BsonDocument toDoc() {
  org.bson.BsonDocument d = new org.bson.BsonDocument();
  d.put("format", new org.bson.BsonInt32(1));
  d.put("mod", new org.bson.BsonString("SkyyEssentials"));
  d.put("version", new org.bson.BsonString("@VERSION@"));
  d.put("sessionId", new org.bson.BsonString(this.id));
  d.put("uuidA", new org.bson.BsonString(this.ua.toString()));
  d.put("nameA", new org.bson.BsonString(this.na));
  d.put("uuidB", new org.bson.BsonString(this.ub.toString()));
  d.put("nameB", new org.bson.BsonString(this.nb));
  d.put("keyA", new org.bson.BsonString(this.keyA == null ? "" : this.keyA));
  d.put("keyB", new org.bson.BsonString(this.keyB == null ? "" : this.keyB));
  d.put("startedAt", new org.bson.BsonInt64(this.startedAt));
  d.put("endedAt", new org.bson.BsonInt64(this.endedAt));
  d.put("state", new org.bson.BsonString(this.state));
  d.put("result", new org.bson.BsonString(this.result));
  d.put("reason", new org.bson.BsonString(this.reason));
  d.put("rev", new org.bson.BsonInt64(this.rev));
  d.put("savedAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  org.bson.BsonArray ia = this.itemsA;
  org.bson.BsonArray ib = this.itemsB;
  if ("ACTIVE".equals(this.state) && this.liveA != null) ia = arr(@PKG@.TCodec.docList(this.liveA));
  if ("ACTIVE".equals(this.state) && this.liveB != null) ib = arr(@PKG@.TCodec.docList(this.liveB));
  d.put("itemsA", ia);
  d.put("itemsB", ib);
  d.put("coinsA", new org.bson.BsonInt64(this.coinsA));
  d.put("coinsB", new org.bson.BsonInt64(this.coinsB));
  d.put("readyA", new org.bson.BsonBoolean(this.readyA));
  d.put("readyB", new org.bson.BsonBoolean(this.readyB));
  d.put("oweA", arr(this.oweA));
  d.put("oweB", arr(this.oweB));
  d.put("coinOweA", new org.bson.BsonInt64(this.coinOweA));
  d.put("coinOweB", new org.bson.BsonInt64(this.coinOweB));
  d.put("paying", new org.bson.BsonBoolean(this.paying));
  d.put("paidA", new org.bson.BsonBoolean(this.paidA));
  d.put("paidB", new org.bson.BsonBoolean(this.paidB));
  d.put("count", new org.bson.BsonInt32(ia.size() + ib.size() + this.oweA.size() + this.oweB.size()));
  return d;
}""")
M(trec, r"""
public synchronized Object[] snap() {
  return new Object[] { toDoc(), Long.valueOf(this.rev) };
}""")
# decide the trade: owe lists (slot docs) + coins still to pay; items = the agreed / returned stacks for the archive
M(trec, r"""
public synchronized Object[] settle(String result, String reason, java.util.ArrayList oA, java.util.ArrayList oB, long cA, long cB, org.bson.BsonArray iA, org.bson.BsonArray iB) {
  this.state = "SETTLING";
  this.result = result == null ? "" : result;
  this.reason = reason == null ? "" : reason;
  this.endedAt = System.currentTimeMillis();
  this.oweA = oA == null ? new java.util.ArrayList() : oA;
  this.oweB = oB == null ? new java.util.ArrayList() : oB;
  this.coinOweA = cA; this.coinOweB = cB;
  if (iA != null) this.itemsA = iA;
  if (iB != null) this.itemsB = iB;
  this.liveA = null; this.liveB = null;
  this.rev = this.rev + 1L;
  return snap();
}""")
# coin transfer write-ahead marker (still ACTIVE: a crash now = the start-up cancel returns the items and owes back every coin take
# marked paid). ia / ib = the drained escrow (what the file must return), ca / cb = the agreed coins.
M(trec, r"""
public synchronized Object[] markPaying(@IS@[] ia, @IS@[] ib, long ca, long cb) {
  this.liveA = ia; this.liveB = ib;
  this.coinsA = ca; this.coinsB = cb;
  this.paying = true; this.paidA = false; this.paidB = false;
  this.rev = this.rev + 1L;
  return snap();
}""")
M(trec, r"""
public synchronized Object[] markPaid(int side) {
  if (side == 0) this.paidA = true; else this.paidB = true;
  this.rev = this.rev + 1L;
  return snap();
}""")
M(trec, r"""
public synchronized java.util.ArrayList oweCopy(int side) {
  return new java.util.ArrayList(side == 0 ? this.oweA : this.oweB);
}""")
M(trec, r"""
public synchronized void replaceOwe(int side, java.util.ArrayList keep) {
  if (side == 0) this.oweA = keep; else this.oweB = keep;
  this.rev = this.rev + 1L;
}""")
M(trec, r"""
public synchronized long coinOwe(int side) { return side == 0 ? this.coinOweA : this.coinOweB; }""")
M(trec, r"""
public synchronized void clearCoinOwe(int side) {
  if (side == 0) this.coinOweA = 0L; else this.coinOweB = 0L;
  this.rev = this.rev + 1L;
}""")
M(trec, r"""
public synchronized boolean owes(java.util.UUID u) {
  if (!"SETTLING".equals(this.state) || u == null) return false;
  if (u.equals(this.ua) && (!this.oweA.isEmpty() || this.coinOweA > 0L)) return true;
  if (u.equals(this.ub) && (!this.oweB.isEmpty() || this.coinOweB > 0L)) return true;
  return false;
}""")
M(trec, r"""
public synchronized int oweStacks(java.util.UUID u) {
  int n = 0;
  if (u == null || !"SETTLING".equals(this.state)) return 0;
  if (u.equals(this.ua)) n = n + this.oweA.size();
  if (u.equals(this.ub)) n = n + this.oweB.size();
  return n;
}""")
M(trec, r"""
public synchronized boolean done() {
  return "SETTLING".equals(this.state) && this.oweA.isEmpty() && this.oweB.isEmpty() && this.coinOweA <= 0L && this.coinOweB <= 0L;
}""")
M(trec, r"""
public static @PKG@.TRecord fromDoc(org.bson.BsonDocument d) {
  String id = @PKG@.TCodec.strOf(d, "sessionId");
  String a = @PKG@.TCodec.strOf(d, "uuidA");
  String b = @PKG@.TCodec.strOf(d, "uuidB");
  if (id == null || a == null || b == null) return null;
  java.util.UUID ua = null;
  java.util.UUID ub = null;
  try { ua = java.util.UUID.fromString(a); ub = java.util.UUID.fromString(b); } catch (Throwable t) { return null; }
  @PKG@.TRecord r = new @PKG@.TRecord(id, ua, @PKG@.TCodec.strOf(d, "nameA"), ub, @PKG@.TCodec.strOf(d, "nameB"), 0, @PKG@.TCodec.lngOf(d, "startedAt", 0L));
  r.endedAt = @PKG@.TCodec.lngOf(d, "endedAt", 0L);
  String ka = @PKG@.TCodec.strOf(d, "keyA");
  String kb = @PKG@.TCodec.strOf(d, "keyB");
  r.keyA = ka == null ? "" : ka;
  r.keyB = kb == null ? "" : kb;
  String st = @PKG@.TCodec.strOf(d, "state");
  r.state = "SETTLING".equals(st) ? "SETTLING" : "ACTIVE";
  String res = @PKG@.TCodec.strOf(d, "result");
  r.result = res == null ? "" : res;
  String rs = @PKG@.TCodec.strOf(d, "reason");
  r.reason = rs == null ? "" : rs;
  r.itemsA = d.getArray("itemsA", new org.bson.BsonArray());
  r.itemsB = d.getArray("itemsB", new org.bson.BsonArray());
  r.coinsA = @PKG@.TCodec.lngOf(d, "coinsA", 0L);
  r.coinsB = @PKG@.TCodec.lngOf(d, "coinsB", 0L);
  r.readyA = @PKG@.TCodec.boolOf(d, "readyA");
  r.readyB = @PKG@.TCodec.boolOf(d, "readyB");
  r.oweA = @PKG@.TCodec.listOf(d.getArray("oweA", new org.bson.BsonArray()));
  r.oweB = @PKG@.TCodec.listOf(d.getArray("oweB", new org.bson.BsonArray()));
  r.coinOweA = @PKG@.TCodec.lngOf(d, "coinOweA", 0L);
  r.coinOweB = @PKG@.TCodec.lngOf(d, "coinOweB", 0L);
  r.paying = @PKG@.TCodec.boolOf(d, "paying");
  r.paidA = @PKG@.TCodec.boolOf(d, "paidA");
  r.paidB = @PKG@.TCodec.boolOf(d, "paidB");
  r.rev = @PKG@.TCodec.lngOf(d, "rev", 1L);
  r.writtenRev = r.rev;
  return r;
}""")

# ================= TSession: one live trade (side 0 = the player who sent the request, side 1 = the one who accepted) =================
# state 0 = editing, 1 = countdown (both containers DENY_ALL), 2 = settling / over. Every state change is a synchronized method (the
# ONE lock per trade); container filters are set inside it (setGlobalFilter is a plain field write, no container lock).
for f in ("public @PKG@.TRecord rec;", "public java.util.UUID[] u;", "public String[] name;", "public @SIC@[] box;", "public @EREG@[] reg;",
          "public long[] coins;", "public boolean[] ready;", "public volatile int state;", "public int token;", "public String[] agreed;",
          "public long[] agreedCoins;", "public @PKG@.TWindow[] win;", "public @PKG@.TradePage[] page;", "public java.util.concurrent.CopyOnWriteArrayList wins;",
          "public Object[] epoch;", "public double[] px;", "public double[] py;", "public double[] pz;", "public double[] sx;",
          "public double[] sy;", "public double[] sz;", "public boolean[] hasPos;", "public boolean[] hasStart;", "public boolean[] hpSeen;",
          "public boolean[] hurt;", "public float[] hp;", "public java.util.UUID[] wu;", "public java.util.UUID[] sw;", "public long[] posAt;",
          "public long[] lastBuilt;", "public boolean[] refreshPending;", "public int[] offline;", "public volatile boolean closed;"):
    F(tses, f)
C(tses, r"""
public TSession() {
  this.u = new java.util.UUID[2]; this.name = new String[2]; this.box = new @SIC@[2]; this.reg = new @EREG@[2];
  this.coins = new long[2]; this.ready = new boolean[2]; this.state = 0; this.token = 0; this.agreed = new String[2]; this.agreedCoins = new long[2];
  this.win = new @PKG@.TWindow[2]; this.page = new @PKG@.TradePage[2]; this.wins = new java.util.concurrent.CopyOnWriteArrayList(); this.epoch = new Object[2];
  this.px = new double[2]; this.py = new double[2]; this.pz = new double[2]; this.sx = new double[2]; this.sy = new double[2]; this.sz = new double[2];
  this.hasPos = new boolean[2]; this.hasStart = new boolean[2]; this.hpSeen = new boolean[2]; this.hurt = new boolean[2]; this.hp = new float[2];
  this.wu = new java.util.UUID[2]; this.sw = new java.util.UUID[2]; this.posAt = new long[2];
  this.lastBuilt = new long[2]; this.refreshPending = new boolean[2]; this.offline = new int[2]; this.closed = false;
  this.agreed[0] = ""; this.agreed[1] = "";
}""")
M(tses, r"""
public void lockBoxes() {
  try { this.box[0].setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
  try { this.box[1].setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
}""")
M(tses, r"""
public void unlockBoxes() {
  try { this.box[0].setGlobalFilter(@FT@.ALLOW_ALL); } catch (Throwable t) { }
  try { this.box[1].setGlobalFilter(@FT@.ALLOW_ALL); } catch (Throwable t) { }
}""")
M(tses, r"""
public boolean live() { return !this.closed && this.state < 2; }""")
M(tses, r"""
public int side(java.util.UUID x) {
  if (x == null) return -1;
  if (x.equals(this.u[0])) return 0;
  if (x.equals(this.u[1])) return 1;
  return -1;
}""")
# Ready click. -1 over; 0 now not ready; 1 ready (the other is not); 3 countdown stopped (clicked during it); 10 + token = both ready,
# countdown started with that token (containers locked HERE, inside the lock)
M(tses, r"""
public synchronized int toggleReady(int side) {
  if (this.state >= 2) return -1;
  if (this.state == 1) { this.state = 0; this.token = this.token + 1; this.ready[side] = false; unlockBoxes(); return 3; }
  this.ready[side] = !this.ready[side];
  if (!this.ready[side]) return 0;
  if (!this.ready[1 - side]) return 1;
  this.state = 1;
  this.token = this.token + 1;
  lockBoxes();
  return 10 + this.token;
}""")
# a container change event: -1 ignored (settling / over); 2 countdown stopped; 1 Ready marks cleared; 0 nothing to clear
M(tses, r"""
public synchronized int onChange(int side) {
  if (this.state >= 2) return -1;
  if (this.state == 1) { this.state = 0; this.token = this.token + 1; this.ready[0] = false; this.ready[1] = false; unlockBoxes(); return 2; }
  if (this.ready[0] || this.ready[1]) { this.ready[0] = false; this.ready[1] = false; return 1; }
  return 0;
}""")
# coin offer: -1 over; -2 locked (countdown); 0 unchanged; 1 changed; 2 changed and Ready marks cleared
M(tses, r"""
public synchronized int setCoins(int side, long n) {
  if (this.state >= 2) return -1;
  if (this.state == 1) return -2;
  if (this.coins[side] == n) return 0;
  this.coins[side] = n;
  boolean had = this.ready[0] || this.ready[1];
  this.ready[0] = false; this.ready[1] = false;
  return had ? 2 : 1;
}""")
M(tses, r"""
public synchronized boolean setAgreed(int tok, String a, String b) {
  if (this.state != 1 || tok != this.token) return false;
  this.agreed[0] = a; this.agreed[1] = b;
  this.agreedCoins[0] = this.coins[0]; this.agreedCoins[1] = this.coins[1];
  return true;
}""")
M(tses, r"""
public synchronized boolean stopCountdown(int tok) {
  if (this.state != 1 || tok != this.token) return false;
  this.state = 0; this.token = this.token + 1; this.ready[0] = false; this.ready[1] = false;
  unlockBoxes();
  return true;
}""")
M(tses, r"""
public synchronized boolean countdownValid(int tok) { return this.state == 1 && tok == this.token; }""")
# the ONLY way into state 2: tok >= 0 = the countdown's own execute (must still be that countdown), tok < 0 = a cancel from any state.
# Containers are locked here, inside the lock, before anyone empties them.
M(tses, r"""
public synchronized boolean beginSettle(int tok) {
  if (this.state >= 2) return false;
  if (tok >= 0 && (this.state != 1 || tok != this.token)) return false;
  this.state = 2;
  this.token = this.token + 1;
  lockBoxes();
  return true;
}""")
# your trade page / offer window closed: 2 countdown stopped (both unready), 1 your Ready cleared, 0 nothing
M(tses, r"""
public synchronized int stopForClose(int side) {
  if (this.state >= 2) return 0;
  if (this.state == 1) { this.state = 0; this.token = this.token + 1; this.ready[0] = false; this.ready[1] = false; unlockBoxes(); return 2; }
  if (this.ready[side]) { this.ready[side] = false; return 1; }
  return 0;
}""")
M(tses, r"""
public synchronized boolean markRefresh(int side) {
  if (this.refreshPending[side]) return false;
  this.refreshPending[side] = true;
  return true;
}""")
M(tses, r"""
public synchronized void clearRefresh(int side) { this.refreshPending[side] = false; }""")

# ================= small classes: constructors now, bodies (which call TStore) later =================
F(tchg, "public @PKG@.TSession sess;")
F(tchg, "public int side;")
C(tchg, "public TChange(@PKG@.TSession s, int side) { this.sess = s; this.side = side; }")
for f in ("public @PKG@.TSession sess;", "public int side;", "public int mode;", "public volatile boolean dead;", "public Object page;"):
    F(twin, f)
C(twin, r"""
public TWindow(@IC@ c, @PKG@.TSession s, int side, int mode) { super(c); this.sess = s; this.side = side; this.mode = mode; this.dead = false; this.page = null; }""")
C(tthr, "public TThreads() { }")
M(tthr, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyEssentials-trade");
  t.setDaemon(true);
  return t;
}""")
# TJob kinds (run on the trade thread): 1 write a record, 2 names file, 3 archive a record, 4 cancel a trade, 5 late sweep of dead escrow,
# 6 mark deliveries due for players already online when the plugin starts (/plugin load or reload: no PlayerReadyEvent for them),
# 7 /tradeadmin return (u1 = target, u2 = admin), (8 and 9 = the 0.1.2 settings writes, gone in 0.1.3: the config kit writes the file),
# 10 write a record NOW (item moves, deliveries)
for f in ("public int kind;", "public @PKG@.TRecord rec;", "public @PKG@.TSession sess;", "public String reason;", "public int by;", "public String byName;",
          "public java.util.UUID u1;", "public java.util.UUID u2;", "public Object obj;", "public int idx;", "public String val;"):
    F(tjob, f)
C(tjob, r"""
public TJob(int kind, @PKG@.TRecord rec, @PKG@.TSession sess, String reason, int by, String byName) {
  this.kind = kind; this.rec = rec; this.sess = sess; this.reason = reason; this.by = by; this.byName = byName;
}""")
# TTask kinds (run on a PLAYER's world thread, hop first): 1 open the trade UI, 2 end-of-trade UI close + message, 3 position/health read,
# 4 deliver what trades owe, 5 page refresh, 6 close a dismissed page's window, 7 bring the trade page back after the chest closed,
# 8 settings-page refresh (obj = the page, msg = result, side = row or -1, val = the typed text to keep on a refusal; 0.1.3: only the
# delayed refresh after Reload file)
for f in ("public int kind;", "public @PKG@.TSession sess;", "public int side;", "public java.util.UUID uuid;", "public String msg;",
          "public @PKG@.TWindow win;", "public @WLD@ expected;", "public int tries;", "public int mode;", "public Object obj;", "public String val;"):
    F(ttask, f)
C(ttask, r"""
public TTask(int kind, @PKG@.TSession s, int side, java.util.UUID u, String msg) {
  this.kind = kind; this.sess = s; this.side = side; this.uuid = u; this.msg = msg; this.win = null; this.expected = null; this.tries = 0; this.mode = 1;
}""")
for f in ("public @PKG@.TSession sess;", "public int token;", "public int left;", "public int total;"):
    F(tcd, f)
C(tcd, "public TCountdown(@PKG@.TSession s, int token, int left) { this.sess = s; this.token = token; this.left = left; this.total = left; }")
C(tfn, "public TCancelFn() { }")
C(trl, "public TReadyL() { }")
C(tql, "public TQuitL() { }")
F(ttk, "public int n;")
C(ttk, "public TTick() { this.n = 0; }")

# ================= TStore layer 1: state maps + leaf helpers (no TradePage / TTask bodies needed) =================
for f in ("public static final java.util.concurrent.ConcurrentHashMap SESSIONS = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> TSession
          "public static final java.util.concurrent.ConcurrentHashMap RECORDS = new java.util.concurrent.ConcurrentHashMap();",    # id -> TRecord (settling)
          "public static final java.util.concurrent.ConcurrentHashMap TREQ = new java.util.concurrent.ConcurrentHashMap();",       # "from>to" -> TpReq
          "public static final java.util.concurrent.ConcurrentHashMap TLAST = new java.util.concurrent.ConcurrentHashMap();",      # requester -> Long
          "public static final java.util.concurrent.ConcurrentHashMap EPOCHS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SWITCHED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BUSYSEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap DUE = new java.util.concurrent.ConcurrentHashMap();",        # uuid -> Long
          "public static final java.util.concurrent.ConcurrentHashMap DELIVERING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",    # rec id -> TRUE
          "public static final java.util.concurrent.ConcurrentHashMap NOWQ = new java.util.concurrent.ConcurrentHashMap();",       # rec id -> TRUE (a write-now job queued)
          "public static final java.util.concurrent.ConcurrentHashMap ARCHIVING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicInteger SEQ = new java.util.concurrent.atomic.AtomicInteger(0);",
          "public static volatile boolean NAMES_DIRTY = false;",
          "public static volatile boolean STOPPING = true;",
          "public static volatile java.util.concurrent.ScheduledExecutorService SAVER = null;",
          "public static volatile java.util.concurrent.ScheduledFuture TICK = null;",
          'public static final String P = "[Trade] ";'):
    F(tst, f)
M(tst, r"""
public static @PKG@.TSession current(java.util.UUID u) {
  if (u == null) return null;
  Object o = SESSIONS.get(u);
  if (o == null) return null;
  @PKG@.TSession s = (@PKG@.TSession) o;
  if (!s.live()) return null;
  return s;
}""")
# "+" good (green), "-" problem (red), "=" info (yellow); always "[Trade] " in front
M(tst, r"""
public static void tellPr(@PR@ p, String res) {
  if (p == null || res == null || res.length() == 0) return;
  String col = @ES@.INFO;
  String txt = res;
  char c = res.charAt(0);
  if (c == '+') { col = @ES@.OK; txt = res.substring(1); }
  else if (c == '-') { col = @ES@.ERR; txt = res.substring(1); }
  else if (c == '=') { txt = res.substring(1); }
  @ES@.say(p, P + txt, col);
}""")
M(tst, r"""
public static void tell(java.util.UUID u, String res) { tellPr(@ES@.online(u), res); }""")
M(tst, r"""
public static void sayBoth(@PKG@.TSession s, String res) {
  tell(s.u[0], res);
  tell(s.u[1], res);
}""")
M(tst, r"""
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
M(tst, r"""
public static void log(String line) { @PKG@.TCfg.log(line); }""")
M(tst, r"""
public static String who(java.util.UUID u, String name) { return (name == null ? "?" : name) + "(" + u + ")"; }""")
M(tst, r"""
public static String ids(@PKG@.TSession s) {
  return "id=" + s.rec.id + " a=" + who(s.u[0], s.name[0]) + " b=" + who(s.u[1], s.name[1]);
}""")
# ---- coins: ONLY through the SkyyCoins bridge functions, and only when all three are there
M(tst, r"""
public static Object coinFn(String k) { return @PKG@.TCfg.bridge().get("coins:fn:" + k); }""")
M(tst, r"""
public static boolean coinsPresent() {
  return coinFn("get") instanceof java.util.function.Function && coinFn("add") instanceof java.util.function.Function && coinFn("take") instanceof java.util.function.Function;
}""")
M(tst, r"""
public static boolean coinsOn() { return @PKG@.TCfg.COINS && coinsPresent(); }""")
M(tst, r"""
public static String coinsNote() {
  if (!@PKG@.TCfg.COINS) return "Coin trading is turned off on this server - items only.";
  return "Coin trading needs SkyyCoins - items only.";
}""")
M(tst, r"""
public static Long coinsGet(java.util.UUID u) {
  try {
    Object f = coinFn("get");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Long) return (Long) r;
    if (r instanceof Number) return Long.valueOf(((Number) r).longValue());
  } catch (Throwable t) { }
  return null;
}""")
# 1 taken, 0 not enough (nothing taken), -1 coins unavailable
M(tst, r"""
public static int coinsTake(java.util.UUID u, long n) {
  if (n <= 0L) return 1;
  try {
    Object f = coinFn("take");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    if (Boolean.TRUE.equals(r)) return 1;
    if (r instanceof Boolean) return 0;
  } catch (Throwable t) { @PKG@.TCfg.warn("coins:fn:take failed for " + u + ": " + t); }
  return -1;
}""")
M(tst, r"""
public static boolean coinsAdd(java.util.UUID u, long n) {
  if (n <= 0L) return true;
  try {
    Object f = coinFn("add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    return r instanceof Long;
  } catch (Throwable t) { @PKG@.TCfg.warn("coins:fn:add failed for " + u + ": " + t); }
  return false;
}""")
# ---- item snapshots
M(tst, r"""
public static @IS@[] snapshot(@IC@ c) {
  if (c == null) return new @IS@[0];
  int cap = c.getCapacity();
  @IS@[] a = new @IS@[cap];
  for (int i = 0; i < cap; i++) {
    @IS@ x = c.getItemStack((short) i);
    if (x != null && !x.isEmpty()) a[i] = x;
  }
  return a;
}""")
# empty an escrow: ONE write under the container lock that IGNORES the global filter (ItemContainer.clear -> SimpleItemContainer
# .internal_clear copies every slot out and nulls it). Never removeAllItemStacks(): its loop skips every slot where cantRemoveFromSlot
# is true, and SimpleItemContainer.cantRemoveFromSlot is true whenever the global filter denies output - the escrow is DENY_ALL from both
# Ready until it is emptied, so it would return nothing and leave the items in a dead container (bytecode, 2026-09-25). Client moves
# still honour DENY_ALL (InventoryUtils.moveItem -> moveItemStackFromSlotToSlot(..., filter = true)). null = could not be emptied.
M(tst, r"""
public static @IS@[] drain(@SIC@ c) {
  if (c == null) return new @IS@[0];
  @CLT@ tx = c.clear();
  if (tx == null) return null;
  @IS@[] all = tx.getItems();
  if (all == null) return new @IS@[0];
  int n = 0;
  for (int i = 0; i < all.length; i++) if (all[i] != null && !all[i].isEmpty()) n++;
  @IS@[] a = new @IS@[n];
  int k = 0;
  for (int i = 0; i < all.length; i++) {
    if (all[i] != null && !all[i].isEmpty()) { a[k] = all[i]; k++; }
  }
  return a;
}""")
M(tst, r"""
public static String secWord(int n) { return n == 1 ? n + " second" : n + " seconds"; }""")
# order-independent fingerprint of an offer: id, count, durability, quality and metadata of every stack
M(tst, r"""
public static String sig(@IS@[] a) {
  java.util.ArrayList parts = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    @IS@ s = a[i];
    if (s == null || s.isEmpty()) continue;
    String m = "";
    try { org.bson.BsonDocument md = s.getMetadata(); if (md != null) m = md.toJson(); } catch (Throwable t) { m = "?"; }
    parts.add(s.getItemId() + "|" + s.getQuantity() + "|" + s.getDurability() + "|" + s.getQualityIndex() + "|" + m);
  }
  java.util.Collections.sort(parts);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < parts.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) parts.get(i)); }
  return sb.toString();
}""")
M(tst, r"""
public static int stacks(@IS@[] a) {
  int n = 0;
  for (int i = 0; i < a.length; i++) if (a[i] != null && !a[i].isEmpty()) n++;
  return n;
}""")
M(tst, r"""
public static int items(@IS@[] a) {
  int n = 0;
  for (int i = 0; i < a.length; i++) if (a[i] != null && !a[i].isEmpty()) n = n + a[i].getQuantity();
  return n;
}""")
# ---- page grid: cols, slot size, width, height for n slots (fits a 516 x 300 box)
M(tst, r"""
public static int[] gridGeom(int n) {
  int cols = n <= 16 ? 4 : (n <= 25 ? 5 : 6);
  int rows = (n + cols - 1) / cols;
  if (rows < 1) rows = 1;
  int sz = 72;
  if (rows * sz > 296) sz = 296 / rows;
  if (cols * sz > 500) sz = 500 / cols;
  if (sz < 36) sz = 36;
  return new int[] { cols, sz, cols * sz, rows * sz };
}""")
# read-only grid slots from a SNAPSHOT (never the live container). 0.1.4: a grid slot must NEVER carry item metadata (the client
# disconnects: ClientItemMetadata) - the slot gets a metadata-free copy, and a stack that had metadata shows its display name +
# description (plain text, e.g. SkyyRolls rolls) through the slot's own tooltip
M(tst, r"""
public static String rawOf(@MSG@ m) {
  if (m == null) return null;
  try { String r = m.getRawText(); return (r == null || r.trim().length() == 0) ? null : r; } catch (Throwable t) { return null; }
}""")
M(tst, r"""
public static @IGS@ gridSlot(@IS@ s) {
  if (s == null || s.isEmpty()) return new @IGS@();
  @IGS@ g = new @IGS@(new @IS@(s.getItemId(), s.getQuantity()));
  try {
    if (s.getMetadata() != null) {
      String n = rawOf(s.getDisplayName());
      String d = rawOf(s.getDisplayDescription());
      if (n != null) g.setName(n);
      if (d != null) g.setDescription(d);
    }
  } catch (Throwable t) { }
  return g;
}""")
M(tst, r"""
public static java.util.ArrayList gridSlots(@IS@[] a) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    @IGS@ g = gridSlot(a[i]);
    g.setActivatable(false);
    l.add(g);
  }
  return l;
}""")
# ---- profile gate (SkyyVault 0.1 VSessions.noteEpoch / noteBusy / settleLeft; first epoch seen = baseline, contract section 4)
M(tst, r"""
public static boolean noteEpoch(java.util.UUID u) {
  Object cur = @PKG@.TCfg.bridge().get("profile:epoch:" + u);
  if (cur == null) return false;
  Object prev = EPOCHS.put(u, cur);
  if (prev != null && !prev.equals(cur)) { SWITCHED.put(u, Long.valueOf(System.currentTimeMillis())); return true; }
  return false;
}""")
M(tst, r"""
public static boolean noteBusy(java.util.UUID u) {
  if (@PKG@.TCfg.bridge().get("profile:busy:" + u) != null) { BUSYSEEN.put(u, Boolean.TRUE); return true; }
  if (BUSYSEEN.remove(u) != null) SWITCHED.put(u, Long.valueOf(System.currentTimeMillis()));
  return false;
}""")
# tools/PROFILES-CONTRACT.md helper: storage key of the player's ACTIVE profile (uuid.toString() without SkyyProfiles)
M(tst, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = @PKG@.TCfg.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(tst, r"""
public static boolean busy(java.util.UUID u) { return u != null && @PKG@.TCfg.bridge().get("profile:busy:" + u) != null; }""")
M(tst, r"""
public static long settleLeft(java.util.UUID u) {
  Object at = SWITCHED.get(u);
  if (!(at instanceof Long)) return 0L;
  long left = (long) @PKG@.TCfg.AFTER_S * 1000L - (System.currentTimeMillis() - ((Long) at).longValue());
  if (left <= 0L) return 0L;
  return (left + 999L) / 1000L;
}""")
# null = may trade now; else the reason (whose = null -> "your", else that player's name)
M(tst, r"""
public static String gate(java.util.UUID u, String whose) {
  if (noteBusy(u)) return whose == null ? "-Your profile is still loading - try again in a moment." : "-" + whose + "'s profile is still loading - try again in a moment.";
  noteEpoch(u);
  long left = settleLeft(u);
  if (left > 0L) return whose == null ? "-Your profile just changed - you can trade again in " + left + " s." : "-" + whose + "'s profile just changed - they can trade again in " + left + " s.";
  return null;
}""")
# ---- names (lower-case name -> uuid) for /tradeadmin with offline players
M(tst, r"""
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
    p.store(bo, "SkyyEssentials /trade: lower-case player name = uuid (for /tradeadmin with offline players)");
    @PKG@.TCfg.atomicWrite(@PKG@.TCfg.NAMESF, bo.toByteArray());
  } catch (Throwable t) { NAMES_DIRTY = true; @PKG@.TCfg.warnOnce("names", "could not write trades/names.properties: " + t); }
}""")
M(tst, r"""
public static void loadNames() {
  try {
    if (@PKG@.TCfg.NAMESF == null || !java.nio.file.Files.exists(@PKG@.TCfg.NAMESF, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(@PKG@.TCfg.NAMESF, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); NAMES.put(k, p.getProperty(k)); }
  } catch (Throwable t) { @PKG@.TCfg.warn("trades/names.properties could not be read: " + t); }
}""")
M(tst, r"""
public static java.util.UUID resolve(String whoText) {
  if (whoText == null) return null;
  String w = whoText.trim();
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
# ---- inventory: give ONE stack, storage first, then hotbar, then backpack; only (count after - count before) of that id counts
M(tst, r"""
public static int countId(@IC@[] cs, String id) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    @IC@ k = cs[c];
    if (k == null) continue;
    int cap = k.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = k.getItemStack((short) i);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n = n + it.getQuantity();
    }
  }
  return n;
}""")
M(tst, r"""
public static int give(@PLA@ p, @IS@ s) {
  if (p == null || s == null || s.isEmpty()) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  @IC@[] order = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  String id = s.getItemId();
  int want = s.getQuantity();
  int before = countId(order, id);
  @IS@ rest = s;
  for (int c = 0; c < order.length && rest != null; c++) {
    if (order[c] == null) continue;
    @IST@ tx = order[c].addItemStack(rest);
    if (tx == null) continue;
    @IS@ rem = tx.getRemainder();
    rest = (rem == null || rem.isEmpty()) ? null : rem;
  }
  int added = countId(order, id) - before;
  if (added < 0) added = 0;
  if (added > want) added = want;
  return added;
}""")
# same world + distance, on the CALLER's world thread (both TransformComponents are read there only when both are in that world)
M(tst, r"""
public static String rangeCheck(@PR@ me, @REF@ ref, @ST@ st, @PR@ other) {
  @WLD@ wm = @ES@.worldOf(me);
  @WLD@ wo = @ES@.worldOf(other);
  String on = other.getUsername();
  if (wm == null || wo == null) return "-Could not find where " + on + " is - try again in a moment.";
  if (wm != wo) {
    if (@PKG@.TCfg.SAME_WORLD) return "-You and " + on + " must be in the same world to trade.";
    return null;
  }
  int d = @PKG@.TCfg.DIST;
  if (d <= 0) return null;
  try {
    @REF@ oref = other.getReference();
    if (oref == null || !oref.isValid()) return "-Could not find where " + on + " is - try again in a moment.";
    @TC@ a = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    @TC@ b = (@TC@) oref.getStore().getComponent(oref, @TC@.getComponentType());
    if (a == null || b == null || a.getPosition() == null || b.getPosition() == null) return null;
    @VEC@ pa = a.getPosition();
    @VEC@ pb = b.getPosition();
    double dx = pa.x - pb.x;
    double dy = pa.y - pb.y;
    double dz = pa.z - pb.z;
    double dd = dx * dx + dy * dy + dz * dz;
    if (dd > (double) d * (double) d) return "-You must be within " + d + " blocks of " + on + " to trade (you are " + ((int) Math.sqrt(dd)) + " blocks apart).";
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("range", "trade distance check failed (allowed): " + t); }
  return null;
}""")

# ================= TradePage part 1: the trade page (inline, 1100 x 800; rebuilt after a click or a real change, never on a timer) =================
# mode 1 = opened together with this player's offer window (page mode); 3 = no window (chest mode's control page / after the chest closed)
for f in ("public @PKG@.TSession sess;", "public int side;", "public int mode;", "public String info;", "public String keepCoin;",
          "public @PKG@.TWindow win;", "public volatile boolean dismissed;", "public volatile boolean replacing;", "public boolean cleared;"):
    F(tpage, f)
C(tpage, r"""
public TradePage(@PR@ pr, @PKG@.TSession s, int side, int mode) {
  super(pr, @LIFE@.CanDismiss);
  this.sess = s; this.side = side; this.mode = mode; this.info = ""; this.keepCoin = null; this.win = null;
  this.dismissed = false; this.replacing = false; this.cleared = false;
}""")
M(tpage, r"""
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 / SkyyGuilds 0.1 / SkyyVault jsonStr, verified in game with a TextField)
M(tpage, r"""
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
M(tpage, r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#ffd37a";
}""")
M(tpage, r"""
public static String textOf(String res) {
  if (res == null || res.length() == 0) return "";
  char c = res.charAt(0);
  if (c == '+' || c == '-' || c == '=') return res.substring(1);
  return res;
}""")
M(tpage, r"""
public void refresh() { rebuild(); }""")
M(tpage, r"""
public @PR@ pr() { return this.playerRef; }""")
# one offer column: title, READY / not ready, the read-only grid (snapshot), the coin line
M(tpage, r"""
public static void column(@UCB@ b, String k, String title, boolean ready, @IS@[] items, long coins, boolean coinsShown) {
  String id = "#SkyyTr" + k;
  b.appendInline("#SkyyTrCols", "Group " + id + "Col { Anchor: (Width: 516, Height: 394); LayoutMode: Top; }");
  b.appendInline(id + "Col", "Label " + id + "H { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 23, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set(id + "H.Text", title);
  b.appendInline(id + "Col", "Label " + id + "S { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + (ready ? "#8fe39a" : "#9aa8bd") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set(id + "S.Text", ready ? "READY" : "not ready");
  int[] g = @PKG@.TStore.gridGeom(items.length);
  int gx = (516 - g[2]) / 2;
  if (gx < 0) gx = 0;
  int gy = (300 - g[3]) / 2;
  if (gy < 0) gy = 0;
  b.appendInline(id + "Col", "Group " + id + "Box { Anchor: (Height: 300); }");
  b.appendInline(id + "Box", "ItemGrid " + id + "Grid { Anchor: (Left: " + gx + ", Top: " + gy + ", Width: " + g[2] + ", Height: " + g[3] + "); SlotsPerRow: " + g[0] + "; AreItemsDraggable: false; Style: (SlotSize: " + g[1] + ", SlotIconSize: " + (g[1] - 14) + ", SlotSpacing: 0); }");
  b.set(id + "Grid.Slots", @PKG@.TStore.gridSlots(items));
  b.appendInline(id + "Col", "Label " + id + "C { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: #ffd37a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set(id + "C.Text", coinsShown ? (coins > 0L ? "Coins: " + @PKG@.TStore.grp(coins) : "Coins: none") : "");
}""")
M(tpage, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  this.cleared = false;
  @PKG@.TSession s = this.sess;
  int me = this.side;
  int ot = 1 - me;
  if (s != null) s.lastBuilt[me] = System.currentTimeMillis();
  boolean live = s != null && s.live();
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 20);
  String ys = style("#6a4a12", "#8a641a", "#3e2a08", "#fff2d6", 20);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 20);
  String rs = style("#6a2020", "#8f2f2f", "#3a1010", "#ffe6e6", 20);
  String ds = style("#262f3d", "#303b4c", "#1a212c", "#7f8ea6", 20);
  String st = "Put what you want to give in your offer slots, then click Ready.";
  String sc = "#cfe3ff";
  if (!live) { st = "This trade has ended."; sc = "#ff9d6b"; }
  else if (s.state == 1) { st = "Both ready - trading in " + @PKG@.TStore.secWord(@PKG@.TCfg.COUNTDOWN_S) + " (see chat). Not ready or Cancel trade stops it."; sc = "#ffd37a"; }
  else if (s.ready[me] && !s.ready[ot]) { st = "You are ready - waiting for " + s.name[ot] + "."; sc = "#9cff9c"; }
  else if (!s.ready[me] && s.ready[ot]) { st = s.name[ot] + " is ready - check their offer (hover the items), then click Ready."; sc = "#ffd37a"; }
  // the ended view is a small panel (28 padding + 3 + 48 + 34 + 20 + 60 + 60 = 253 of 280), not the full 800-high trade page
  int ph = live ? 800 : 280;
  b.appendInline((String) null, "Group #SkyyTrade { Anchor: (Width: 1100, Height: " + ph + "); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyTrade", "Group { Anchor: (Height: 3); Background: #6fd3a0; }");
  b.appendInline("#SkyyTrade", "Label #SkyyTrTitle { Anchor: (Height: 48); Text: \"\"; Style: (FontSize: 32, RenderBold: true, TextColor: #d8ffe8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTrTitle.Text", s == null ? "Trade" : "Trade with " + s.name[ot]);
  b.appendInline("#SkyyTrade", "Label #SkyyTrStatus { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + sc + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTrStatus.Text", st);
  if (!live) {
    b.appendInline("#SkyyTrade", "Label { Anchor: (Height: 20); Text: \"\"; }");
    b.appendInline("#SkyyTrade", "Label #SkyyTrEnded { Anchor: (Height: 60); Text: \"\"; Style: (FontSize: 20, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyTrEnded.Text", "Anything still owed to you from a trade: /trade claim");
    b.appendInline("#SkyyTrade", "Group #SkyyTrEndRow { Anchor: (Height: 60); LayoutMode: Left; }");
    b.appendInline("#SkyyTrEndRow", "Label { Anchor: (Width: 451, Height: 56); Text: \"\"; }");
    b.appendInline("#SkyyTrEndRow", "TextButton #SkyyTrClose { Anchor: (Width: 150, Height: 56); Text: \"Close\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrClose", @EVD@.of("a", "close"));
    return;
  }
  boolean coinsOk = @PKG@.TStore.coinsOn();
  boolean locked = s.state == 1;
  // coins already on the table stay visible to both players even when coin trading was turned off (or SkyyCoins left) mid-trade
  boolean coinsShown = coinsOk || s.coins[me] > 0L || s.coins[ot] > 0L;
  b.appendInline("#SkyyTrade", "Label { Anchor: (Height: 6); Text: \"\"; }");
  b.appendInline("#SkyyTrade", "Group #SkyyTrCols { Anchor: (Height: 400); LayoutMode: Left; }");
  column(b, "Mine", "Your offer", s.ready[me], @PKG@.TStore.snapshot(s.box[me]), s.coins[me], coinsShown);
  b.appendInline("#SkyyTrCols", "Group #SkyyTrDiv { Anchor: (Width: 20, Height: 394); }");
  b.appendInline("#SkyyTrDiv", "Group { Anchor: (Left: 9, Top: 0, Width: 2, Height: 394); Background: #2a3f5a; }");
  column(b, "Theirs", s.name[ot] + "'s offer", s.ready[ot], @PKG@.TStore.snapshot(s.box[ot]), s.coins[ot], coinsShown);
  b.appendInline("#SkyyTrade", "Label { Anchor: (Height: 6); Text: \"\"; }");
  b.appendInline("#SkyyTrade", "Group #SkyyTrCoinRow { Anchor: (Height: 52); LayoutMode: Left; }");
  if (coinsOk) {
    b.appendInline("#SkyyTrCoinRow", "Label #SkyyTrCoinLbl { Anchor: (Width: 170, Height: 46); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffd37a, HorizontalAlignment: End, VerticalAlignment: Center); }");
    b.set("#SkyyTrCoinLbl.Text", "Your coins:");
    b.appendInline("#SkyyTrCoinRow", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
    b.appendInline("#SkyyTrCoinRow", "Group #SkyyTrCoinBox { Anchor: (Width: 230, Height: 46); Background: #16263a; }");
    b.appendInline("#SkyyTrCoinBox", "TextField #SkyyTrCoin { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 16; PlaceholderText: \"0\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 19); Style: (TextColor: #ffffff, FontSize: 19); }");
    String kv = this.keepCoin != null ? this.keepCoin : (s.coins[me] > 0L ? String.valueOf(s.coins[me]) : "");
    if (kv.length() > 0) b.set("#SkyyTrCoin.Value", kv);
    b.appendInline("#SkyyTrCoinRow", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
    b.appendInline("#SkyyTrCoinRow", "TextButton #SkyyTrCoinSet { Anchor: (Width: 170, Height: 46); Text: \"Set coins\"; " + (locked ? ds : ys) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrCoinSet", @EVD@.of("a", "coins").append("@TrCoin", "#SkyyTrCoin.Value"));
    ev.addEventBinding(@BT@.Validating, "#SkyyTrCoin", @EVD@.of("a", "coins").append("@TrCoin", "#SkyyTrCoin.Value"), false);
    b.appendInline("#SkyyTrCoinRow", "Label { Anchor: (Width: 16, Height: 46); Text: \"\"; }");
    b.appendInline("#SkyyTrCoinRow", "Label #SkyyTrPurse { Anchor: (Width: 430, Height: 46); Text: \"\"; Style: (FontSize: 18, TextColor: #cfe3ff, VerticalAlignment: Center); }");
    Long bal = @PKG@.TStore.coinsGet(s.u[me]);
    String cap = @PKG@.TCfg.MAX_COINS > 0L ? " (max " + @PKG@.TStore.grp(@PKG@.TCfg.MAX_COINS) + " per trade)" : "";
    b.set("#SkyyTrPurse.Text", (bal == null ? "Your purse cannot be read right now" : "You have " + @PKG@.TStore.grp(bal.longValue()) + " coins") + cap);
  } else if (s.coins[me] > 0L) {
    // coin trading went away with a coin offer of yours on the table: Ready is refused until it is 0, so the way to clear it stays here
    b.appendInline("#SkyyTrCoinRow", "Label #SkyyTrNoCoin { Anchor: (Width: 780, Height: 46); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: #ff9d6b, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyTrNoCoin.Text", "Coin trading is off right now - clear your " + @PKG@.TStore.grp(s.coins[me]) + " coin offer to go on (or Cancel trade).");
    b.appendInline("#SkyyTrCoinRow", "Label { Anchor: (Width: 22, Height: 46); Text: \"\"; }");
    b.appendInline("#SkyyTrCoinRow", "TextButton #SkyyTrCoinClear { Anchor: (Width: 250, Height: 46); Text: \"Clear my coins\"; " + (locked ? ds : ys) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrCoinClear", @EVD@.of("a", "coinclear"));
  } else {
    b.appendInline("#SkyyTrCoinRow", "Label #SkyyTrNoCoin { Anchor: (Width: 1052, Height: 46); Text: \"\"; Style: (FontSize: 18, TextColor: #9aa8bd, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyTrNoCoin.Text", @PKG@.TStore.coinsNote());
  }
  b.appendInline("#SkyyTrade", "Label { Anchor: (Height: 8); Text: \"\"; }");
  b.appendInline("#SkyyTrade", "Group #SkyyTrBtns { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyTrBtns", "Label { Anchor: (Width: 70, Height: 56); Text: \"\"; }");
  boolean amReady = s.ready[me] || locked;
  b.appendInline("#SkyyTrBtns", "TextButton #SkyyTrReady { Anchor: (Width: 240, Height: 56); Text: \"" + (amReady ? "Not ready" : "Ready") + "\"; " + (amReady ? ys : gs) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrReady", @EVD@.of("a", "ready"));
  b.appendInline("#SkyyTrBtns", "Label { Anchor: (Width: 14, Height: 56); Text: \"\"; }");
  b.appendInline("#SkyyTrBtns", "TextButton #SkyyTrChest { Anchor: (Width: 250, Height: 56); Text: \"" + (this.win != null ? "Open as chest" : "Edit my offer") + "\"; " + (locked ? ds : bs) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrChest", @EVD@.of("a", "chest"));
  b.appendInline("#SkyyTrBtns", "Label { Anchor: (Width: 14, Height: 56); Text: \"\"; }");
  b.appendInline("#SkyyTrBtns", "TextButton #SkyyTrCancel { Anchor: (Width: 230, Height: 56); Text: \"Cancel trade\"; " + rs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrCancel", @EVD@.of("a", "cancel"));
  b.appendInline("#SkyyTrBtns", "Label { Anchor: (Width: 14, Height: 56); Text: \"\"; }");
  b.appendInline("#SkyyTrBtns", "TextButton #SkyyTrClose { Anchor: (Width: 150, Height: 56); Text: \"Close\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrClose", @EVD@.of("a", "close"));
  b.appendInline("#SkyyTrade", "Label { Anchor: (Height: 6); Text: \"\"; }");
  String[] help = null;
  if (this.win != null) {
    help = new String[] { "Drag items from your inventory into your offer slots - they leave your inventory at once and come back if the trade is cancelled.",
                          "Offer slots not showing next to this page? Click Open as chest (closing the chest brings this page back).",
                          "Any change to either offer clears both Ready marks. Hover their items to check them before you click Ready." };
  } else {
    help = new String[] { "Click Edit my offer to open your offer slots as a chest - closing the chest brings this page back.",
                          "Any change to either offer clears both Ready marks. Hover their items to check them before you click Ready.",
                          "Cancel trade (or /trade cancel) ends the trade and gives everything back. /trade opens this page again." };
  }
  for (int i = 0; i < help.length; i++) {
    b.appendInline("#SkyyTrade", "Label #SkyyTrHelp" + i + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 16, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyTrHelp" + i + ".Text", help[i]);
  }
  b.appendInline("#SkyyTrade", "Label #SkyyTrInfo { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTrInfo.Text", textOf(this.info));
}""")
# SkyyMenu 0.1.3 stuck-tooltip mitigation: ONE update that empties both grids (the hovered slot too) while the page is still open, sent
# right before the server closes the page. Only called on the page's own world thread while it is the open page.
M(tpage, r"""
public void clearGrids() {
  if (this.cleared || this.sess == null) return;
  this.cleared = true;
  try {
    java.util.ArrayList e1 = new java.util.ArrayList();
    java.util.ArrayList e2 = new java.util.ArrayList();
    int n = this.sess.box[0] == null ? 16 : this.sess.box[0].getCapacity();
    for (int i = 0; i < n; i++) { e1.add(new @IGS@()); e2.add(new @IGS@()); }
    @UCB@ b = new @UCB@();
    b.set("#SkyyTrMineGrid.Slots", e1);
    b.set("#SkyyTrTheirsGrid.Slots", e2);
    sendUpdate(b);
  } catch (Throwable t) { }
}""")

# ================= TCfgPage (0.1.3: drawn from the config kit's rows) =================
# which 0 = /tradeadmin config "Trade settings" (0.1.2's keys; node skyyessentials.tradeadmin), which 1 = /warpadmin -> Settings "Teleport and
# message settings" (the 0.1.3 keys; node skyyessentials.admin). Every value is read from the kit (CfgFn.cmdGet) and every change goes
# through CfgFn.set (validated, logged, versioned, written line by line on the scheduler - no file I/O on the admin's world thread).
# A danger row (a part switched OFF, tradeAfterSwitchSeconds lowered) asks Confirm / Cancel first. guard() first in build() and clicks.
F(tcpg, "public String info;")
F(tcpg, "public String[] keep;")
F(tcpg, "public String[] keys;")
F(tcpg, "public int which;")
F(tcpg, "public String pendKey;")
F(tcpg, "public String pendVal;")
F(tcpg, "public String pendQ;")
F(tcpg, "public static final String[] TRADE_KEYS = %s;" % jarr(TRADE_PAGE_KEYS))
F(tcpg, "public static final String[] ESS_KEYS = %s;" % jarr(ESS_PAGE_KEYS))
C(tcpg, r"""
public TCfgPage(@PR@ pr, int which) {
  super(pr, @LIFE@.CanDismiss);
  this.which = which;
  this.keys = which == 1 ? ESS_KEYS : TRADE_KEYS;
  this.info = ""; this.keep = new String[this.keys.length];
  this.pendKey = null; this.pendVal = null; this.pendQ = null;
}""")
# CustomUIPage.rebuild() is protected: TStore rebuilds this page (one delayed refresh after Reload file) through this
M(tcpg, r"""
public void refresh() { rebuild(); }""")
M(tcpg, r"""
public String node() { return this.which == 1 ? @PKG@.TCfg.EADMIN : @PKG@.TCfg.ADMIN; }""")
M(tcpg, r"""
public boolean guard() {
  try { return this.playerRef.hasPermission(node()); } catch (Throwable t) { return false; }
}""")
M(tcpg, r"""
public String fileKey(int i) {
  String k = @PKG@.CfgRows.BFK[i];
  if (k == null || k.length() == 0) k = @PKG@.CfgRows.BCK[i];
  return k == null ? "" : k;
}""")
M(tcpg, r"""
public String shown(int i, String v) {
  if (v == null) return "?";
  String t = @PKG@.CfgRows.TYPES[i];
  if (t.equals("choice")) {
    String[] cv = @PKG@.CfgRows.chVals(i);
    String[] cl = @PKG@.CfgRows.chLabels(i);
    for (int k = 0; k < cv.length && k < cl.length; k++) if (cv[k].equals(v)) return cl[k];
    return v;
  }
  String s = @PKG@.CfgRows.disp(i, v);
  if (@PKG@.CfgRows.KEYS[i].equals("replyShortcut") && ("true".equals(v) != @ES@.R_SHORTCUT)) s = s + " (restart)";
  return s;
}""")
M(tcpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  String gs = @PKG@.TradePage.style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 17);
  String bs = @PKG@.TradePage.style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 17);
  String ds = @PKG@.TradePage.style("#262f3d", "#303b4c", "#1a212c", "#9aa8bd", 17);
  String rs = @PKG@.TradePage.style("#6a2020", "#8f2f2f", "#3a1010", "#ffe6e6", 17);
  boolean ok = guard();
  String state = "ok";
  String smsg = "";
  try {
    Object so = new @PKG@.CfgFn().apply(new Object[] { "status" });
    if (so instanceof String[] && ((String[]) so).length >= 2) { state = ((String[]) so)[0]; smsg = ((String[]) so)[1]; }
  } catch (Throwable t) { }
  boolean broken = "unreadable".equals(state) || "unsaved".equals(state);
  int n = this.keys.length;
  int ph = 28 + 3 + 46 + 28 + 30 + n * 42 + 8 + 52 + 24 + 24 + 32 + (broken ? 28 : 0) + 6;
  b.appendInline((String) null, "Group #SkyyTcfg { Anchor: (Width: 1060, Height: " + ph + "); Background: #0b1524(0.97); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyTcfg", "Group { Anchor: (Height: 3); Background: #6fd3a0; }");
  b.appendInline("#SkyyTcfg", "Label #SkyyTcTitle { Anchor: (Height: 46); Text: \"\"; Style: (FontSize: 30, RenderBold: true, TextColor: #d8ffe8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTcTitle.Text", this.which == 1 ? "Teleport and message settings" : "Trade settings");
  b.appendInline("#SkyyTcfg", "Label #SkyyTcSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTcSub.Text", "SkyyEssentials @VERSION@ - every change is saved to config.properties at once (the file and this page always match).");
  if (broken) {
    b.appendInline("#SkyyTcfg", "Label #SkyyTcBroken { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ff9d6b, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyTcBroken.Text", smsg);
  }
  b.appendInline("#SkyyTcfg", "Group #SkyyTcHead { Anchor: (Height: 30); LayoutMode: Left; }");
  b.appendInline("#SkyyTcHead", "Label { Anchor: (Width: 380, Height: 30); Text: \"Setting\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyTcHead", "Label { Anchor: (Width: 150, Height: 30); Text: \"Now\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyTcHead", "Label { Anchor: (Width: 300, Height: 30); Text: \"Change\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyTcHead", "Label { Anchor: (Width: 170, Height: 30); Text: \"Key in the file\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  for (int r = 0; r < n; r++) {
    String row = "#SkyyTcRow" + r;
    int i = @PKG@.CfgRows.index(this.keys[r]);
    b.appendInline("#SkyyTcfg", "Group " + row + " { Anchor: (Height: 42); LayoutMode: Left; }");
    b.appendInline(row, "Label #SkyyTcLbl" + r + " { Anchor: (Width: 380, Height: 40); Text: \"\"; Style: (FontSize: 18, TextColor: #e6f2ff, VerticalAlignment: Center); }");
    if (i < 0) { b.set("#SkyyTcLbl" + r + ".Text", this.keys[r] + " (unknown)"); continue; }
    String t = @PKG@.CfgRows.TYPES[i];
    String v = @PKG@.CfgFn.cmdGet(this.keys[r]);
    b.set("#SkyyTcLbl" + r + ".Text", @PKG@.CfgRows.LABELS[i]);
    b.appendInline(row, "Label #SkyyTcVal" + r + " { Anchor: (Width: 150, Height: 40); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: #ffd37a, VerticalAlignment: Center); }");
    b.set("#SkyyTcVal" + r + ".Text", shown(i, v));
    if (t.equals("bool")) {
      boolean on = "true".equals(v);
      b.appendInline(row, "TextButton #SkyyTcOn" + r + " { Anchor: (Width: 110, Height: 36); Text: \"ON\"; " + (on ? gs : ds) + " }");
      b.appendInline(row, "Label { Anchor: (Width: 10, Height: 36); Text: \"\"; }");
      b.appendInline(row, "TextButton #SkyyTcOff" + r + " { Anchor: (Width: 110, Height: 36); Text: \"OFF\"; " + (on ? ds : gs) + " }");
      b.appendInline(row, "Label { Anchor: (Width: 70, Height: 36); Text: \"\"; }");
      ev.addEventBinding(@BT@.Activating, "#SkyyTcOn" + r, @EVD@.of("a", "b1:" + r));
      ev.addEventBinding(@BT@.Activating, "#SkyyTcOff" + r, @EVD@.of("a", "b0:" + r));
    } else if (t.equals("choice")) {
      String[] cv = @PKG@.CfgRows.chVals(i);
      String[] cl = @PKG@.CfgRows.chLabels(i);
      int used = 0;
      for (int k = 0; k < cv.length && k < cl.length && k < 2; k++) {
        boolean sel = cv[k].equals(v);
        b.appendInline(row, "TextButton #SkyyTcCh" + k + "x" + r + " { Anchor: (Width: 140, Height: 36); Text: \"\"; " + (sel ? gs : ds) + " }");
        b.set("#SkyyTcCh" + k + "x" + r + ".Text", cl[k]);
        ev.addEventBinding(@BT@.Activating, "#SkyyTcCh" + k + "x" + r, @EVD@.of("a", "c" + k + ":" + r));
        b.appendInline(row, "Label { Anchor: (Width: 10, Height: 36); Text: \"\"; }");
        used = used + 150;
      }
      if (used < 300) b.appendInline(row, "Label { Anchor: (Width: " + (300 - used) + ", Height: 36); Text: \"\"; }");
    } else {
      b.appendInline(row, "Group #SkyyTcBox" + r + " { Anchor: (Width: 170, Height: 36); Background: #16263a; }");
      b.appendInline("#SkyyTcBox" + r, "TextField #SkyyTcV" + r + " { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 18; PlaceholderText: \"new value\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
      if (this.keep[r] != null && this.keep[r].length() > 0) b.set("#SkyyTcV" + r + ".Value", this.keep[r]);
      b.appendInline(row, "Label { Anchor: (Width: 10, Height: 36); Text: \"\"; }");
      b.appendInline(row, "TextButton #SkyyTcSet" + r + " { Anchor: (Width: 110, Height: 36); Text: \"Set\"; " + bs + " }");
      b.appendInline(row, "Label { Anchor: (Width: 10, Height: 36); Text: \"\"; }");
      ev.addEventBinding(@BT@.Activating, "#SkyyTcSet" + r, @EVD@.of("a", "set:" + r).append("@TcV" + r, "#SkyyTcV" + r + ".Value"));
      ev.addEventBinding(@BT@.Validating, "#SkyyTcV" + r, @EVD@.of("a", "set:" + r).append("@TcV" + r, "#SkyyTcV" + r + ".Value"), false);
    }
    b.appendInline(row, "Label #SkyyTcKey" + r + " { Anchor: (Width: 170, Height: 40); Text: \"\"; Style: (FontSize: 13, TextColor: #7f8ea6, VerticalAlignment: Center); }");
    b.set("#SkyyTcKey" + r + ".Text", fileKey(i));
  }
  b.appendInline("#SkyyTcfg", "Label { Anchor: (Height: 8); Text: \"\"; }");
  b.appendInline("#SkyyTcfg", "Group #SkyyTcBtns { Anchor: (Height: 52); LayoutMode: Left; }");
  if (this.pendQ != null) {
    b.appendInline("#SkyyTcBtns", "Label { Anchor: (Width: 316, Height: 48); Text: \"\"; }");
    b.appendInline("#SkyyTcBtns", "TextButton #SkyyTcYes { Anchor: (Width: 220, Height: 48); Text: \"Confirm\"; " + rs + " }");
    b.appendInline("#SkyyTcBtns", "Label { Anchor: (Width: 20, Height: 48); Text: \"\"; }");
    b.appendInline("#SkyyTcBtns", "TextButton #SkyyTcNo { Anchor: (Width: 150, Height: 48); Text: \"Cancel\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTcYes", @EVD@.of("a", "confirm"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTcNo", @EVD@.of("a", "cancel"));
  } else {
    int lead = this.which == 1 ? 136 : 316;
    b.appendInline("#SkyyTcBtns", "Label { Anchor: (Width: " + lead + ", Height: 48); Text: \"\"; }");
    if (this.which == 1) {
      b.appendInline("#SkyyTcBtns", "TextButton #SkyyTcWarps { Anchor: (Width: 220, Height: 48); Text: \"Back to warps\"; " + bs + " }");
      b.appendInline("#SkyyTcBtns", "Label { Anchor: (Width: 20, Height: 48); Text: \"\"; }");
      ev.addEventBinding(@BT@.Activating, "#SkyyTcWarps", @EVD@.of("a", "warps"));
    }
    b.appendInline("#SkyyTcBtns", "TextButton #SkyyTcReload { Anchor: (Width: 220, Height: 48); Text: \"Reload file\"; " + bs + " }");
    b.appendInline("#SkyyTcBtns", "Label { Anchor: (Width: 20, Height: 48); Text: \"\"; }");
    b.appendInline("#SkyyTcBtns", "TextButton #SkyyTcClose { Anchor: (Width: 150, Height: 48); Text: \"Close\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTcReload", @EVD@.of("a", "reload"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTcClose", @EVD@.of("a", "close"));
  }
  b.appendInline("#SkyyTcfg", "Label #SkyyTcHelp0 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTcHelp0.Text", this.which == 1 ? "Numbers: type a value, then press Enter or Set. Applies at once (/r: after a restart). Also in SkyWynn Menu -> Server Setup."
                                             : "Numbers: type a value, then press Enter or Set. Applies at once (offer slots: new trades only; /r: after a restart).");
  b.appendInline("#SkyyTcfg", "Label #SkyyTcHelp1 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTcHelp1.Text", "File: <world>/mods/Skyy_SkyyEssentials/config.properties - after a hand edit click Reload file (or /tradeadmin reload).");
  String inf = this.info;
  if (!ok) inf = "-You do not have permission to change these settings (" + node() + ").";
  b.appendInline("#SkyyTcfg", "Label #SkyyTcInfo { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + @PKG@.TradePage.colorOf(inf) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyTcInfo.Text", @PKG@.TradePage.textOf(inf));
}""")
# one change through the config kit (the trade page lets skyyessentials.tradeadmin through EssPerm, only for this call). typedRow >= 0 =
# a typed value: kept in its box when refused, cleared when it was saved
M(tcpg, r"""
public void apply(String key, String val, String confirm, int typedRow) {
  Object[] r = null;
  boolean trade = this.which == 0;
  try {
    if (trade) @PKG@.EssPerm.tradeOn();
    r = @PKG@.CfgFn.set(key, val, this.playerRef.getUuid(), this.playerRef.getUsername(), confirm, "command");
  } catch (Throwable t) {
    r = null;
  } finally {
    if (trade) @PKG@.EssPerm.tradeOff();
  }
  String st = "error";
  String msg = "Could not change it - see the server log.";
  if (r != null && r.length >= 3) {
    st = String.valueOf(r[0]);
    if (r[2] != null) msg = String.valueOf(r[2]);
  }
  if (st.equals("confirm")) { this.pendKey = key; this.pendVal = val; this.pendQ = msg; this.info = "=" + msg; return; }
  boolean good = st.equals("ok") || st.equals("restart");
  if (good) {
    this.info = (msg.indexOf(" is already ") >= 0 ? "=" : "+") + msg;
    if (typedRow >= 0 && typedRow < this.keep.length) this.keep[typedRow] = null;
  } else {
    this.info = "-" + msg;
    if (typedRow >= 0 && typedRow < this.keep.length) this.keep[typedRow] = val;
  }
}""")
# (TCfgPage.handleDataEvent and reload are compiled with the other bodies that call TStore / WarpPage, near the end)

# ================= TStore layer 2: files (rev-ordered writes, read back; archive; boot load) =================
M(tst, r"""
public static java.nio.file.Path fileOf(String id) { return @PKG@.TCfg.PDIR.resolve(id + ".json"); }""")
M(tst, r"""
public static boolean write0(@PKG@.TRecord rec, org.bson.BsonDocument doc, long r) {
  if (r <= rec.writtenRev) return true;
  java.nio.file.Path f = fileOf(rec.id);
  try {
    int want = @PKG@.TCodec.intOf(doc, "count", -1);
    @PKG@.TCfg.atomicWrite(f, @PKG@.TCodec.toJson(doc).getBytes("UTF-8"));
    org.bson.BsonDocument back = org.bson.BsonDocument.parse(@PKG@.TCfg.readText(f));
    if (@PKG@.TCodec.intOf(back, "count", -2) != want) { @PKG@.TCfg.warn("trade file " + f + " did not read back correctly (kept in memory, retrying)"); rec.lastFail = System.currentTimeMillis(); return false; }
    rec.writtenRev = r;
    return true;
  } catch (Throwable t) {
    rec.lastFail = System.currentTimeMillis();
    @PKG@.TCfg.warnOnce("write-" + rec.id, "could not write trade file " + f + " (kept in memory, retrying): " + t);
    return false;
  }
}""")
M(tst, r"""
public static boolean writeLocked(@PKG@.TRecord rec, org.bson.BsonDocument doc, long r) {
  synchronized (rec.ioLock) {
    return write0(rec, doc, r);
  }
}""")
M(tst, r"""
public static boolean writeSnap(@PKG@.TRecord rec, Object[] sn) {
  boolean ok = writeLocked(rec, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) log("WRITE-FAIL id=" + rec.id + " rev " + sn[1] + " (kept in memory, retrying)");
  return ok;
}""")
M(tst, r"""
public static boolean writeRec(@PKG@.TRecord rec) { return writeSnap(rec, rec.snap()); }""")
M(tst, r"""
public static void saveJob(@PKG@.TRecord rec) {
  PENDING.remove(rec.id);
  if (rec.rev == rec.writtenRev) return;
  writeRec(rec);
}""")
M(tst, r"""
public static void saveSoon(@PKG@.TRecord rec, long delay) {
  if (rec == null) return;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveJob(rec); return; }
  if (PENDING.putIfAbsent(rec.id, Boolean.TRUE) != null) return;
  try { ex.schedule(new @PKG@.TJob(1, rec, (@PKG@.TSession) null, (String) null, -1, (String) null), delay < 0L ? 0L : delay, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { PENDING.remove(rec.id); saveJob(rec); }
}""")
# write NOW on the trade thread (item moves into / out of an escrow, deliveries): its own queue marker, so a delayed Ready / coin save
# that is already pending (tradeSaveDelayMillis, up to 30 s) can never hold an item change back. At most one queued per record; the
# marker is cleared BEFORE the snapshot, so a change made during the write queues the next one.
M(tst, r"""
public static void saveNowJob(@PKG@.TRecord rec) {
  NOWQ.remove(rec.id);
  if (rec.rev != rec.writtenRev) writeRec(rec);
}""")
M(tst, r"""
public static void saveNow(@PKG@.TRecord rec) {
  if (rec == null) return;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveJob(rec); return; }
  if (NOWQ.putIfAbsent(rec.id, Boolean.TRUE) != null) return;
  try { ex.execute(new @PKG@.TJob(10, rec, (@PKG@.TSession) null, (String) null, -1, (String) null)); }
  catch (Throwable t) { NOWQ.remove(rec.id); saveJob(rec); }
}""")
M(tst, r"""
public static void noteName(java.util.UUID u, String name) {
  if (u == null || name == null || name.length() == 0) return;
  String k = name.toLowerCase();
  if (u.toString().equals(NAMES.get(k))) return;
  NAMES.put(k, u.toString());
  NAMES_DIRTY = true;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) return;
  try { ex.execute(new @PKG@.TJob(2, (@PKG@.TRecord) null, (@PKG@.TSession) null, (String) null, -1, (String) null)); } catch (Throwable t) { }
}""")
# nothing owed any more: the record goes to archive/<yyyy-MM>/<id>.json (never overwriting), then the pending file is removed
M(tst, r"""
public static void archive(@PKG@.TRecord rec) {
  try {
    if (!rec.done()) return;
    Object[] sn = rec.snap();
    org.bson.BsonDocument d = (org.bson.BsonDocument) sn[0];
    String month = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM").format(java.time.LocalDate.now());
    java.nio.file.Path dir = @PKG@.TCfg.ADIR.resolve(month);
    java.nio.file.Path f = dir.resolve(rec.id + ".json");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) f = dir.resolve(rec.id + "-" + System.currentTimeMillis() + ".json");
    @PKG@.TCfg.atomicWrite(f, @PKG@.TCodec.toJson(d).getBytes("UTF-8"));
    org.bson.BsonDocument back = org.bson.BsonDocument.parse(@PKG@.TCfg.readText(f));
    if (@PKG@.TCodec.intOf(back, "count", -2) != @PKG@.TCodec.intOf(d, "count", -1)) { @PKG@.TCfg.warn("archive " + f + " did not read back - pending file kept"); return; }
    java.nio.file.Files.deleteIfExists(fileOf(rec.id));
    RECORDS.remove(rec.id, rec);
    log("ARCHIVE id=" + rec.id + " " + rec.result + (rec.reason.length() > 0 ? " reason=" + rec.reason : ""));
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("arch-" + rec.id, "could not archive trade " + rec.id + " (kept in pending, retrying): " + t); }
}""")
# ids already in trades/archive/<yyyy-MM>/ (file <id>.json, or <id>-<13-digit millis>.json when that name was taken)
M(tst, r"""
public static java.util.HashSet archivedIds() {
  java.util.HashSet ids = new java.util.HashSet();
  try {
    java.nio.file.Path ad = @PKG@.TCfg.ADIR;
    if (ad == null || !java.nio.file.Files.isDirectory(ad, new java.nio.file.LinkOption[0])) return ids;
    java.nio.file.DirectoryStream months = java.nio.file.Files.newDirectoryStream(ad);
    try {
      java.util.Iterator it = months.iterator();
      while (it.hasNext()) {
        java.nio.file.Path m = (java.nio.file.Path) it.next();
        if (!java.nio.file.Files.isDirectory(m, new java.nio.file.LinkOption[0])) continue;
        java.nio.file.DirectoryStream fs = java.nio.file.Files.newDirectoryStream(m, "*.json");
        try {
          java.util.Iterator j = fs.iterator();
          while (j.hasNext()) {
            String nm = ((java.nio.file.Path) j.next()).getFileName().toString();
            nm = nm.substring(0, nm.length() - 5);
            ids.add(nm);
            int dash = nm.lastIndexOf('-');
            if (dash > 0 && nm.length() - dash - 1 >= 12) {
              boolean digits = true;
              for (int k = dash + 1; k < nm.length(); k++) if (!Character.isDigit(nm.charAt(k))) digits = false;
              if (digits) ids.add(nm.substring(0, dash));
            }
          }
        } finally { fs.close(); }
      }
    } finally { months.close(); }
  } catch (Throwable t) { @PKG@.TCfg.warn("could not scan trades/archive (the already-archived check is skipped): " + t); }
  return ids;
}""")
# at start: every pending record is loaded; a record still ACTIVE (the server died during that trade) becomes CANCELLED reason
# server-restart: each player gets their own escrow back at their next join, plus every coin take a PAYING record shows as done.
# A file that cannot be read is left untouched. A record that could still hand something out but whose id is already archived (an old
# copy put back - e.g. only the pending folder restored from a backup) is NOT loaded and left untouched for a human: an archived record
# owed nothing any more, so loading the copy would hand the same items out twice.
M(tst, r"""
public static int loadAll() {
  int n = 0;
  try {
    java.nio.file.Files.createDirectories(@PKG@.TCfg.PDIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.HashSet arch = archivedIds();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(@PKG@.TCfg.PDIR, "*.json");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it.next();
        try {
          org.bson.BsonDocument d = org.bson.BsonDocument.parse(@PKG@.TCfg.readText(f));
          @PKG@.TRecord r = @PKG@.TRecord.fromDoc(d);
          if (r == null) { @PKG@.TCfg.warn("trade file " + f + " is not a trade record - left untouched"); continue; }
          if (!r.done() && arch.contains(r.id)) {
            @PKG@.TCfg.warn("trade file " + f + " (trade " + r.id + ") is already in trades/archive - it looks like an old copy put back. NOT loaded (nothing is handed out twice) and left untouched: check it by hand.");
            log("SKIP-ARCHIVED id=" + r.id + " file=" + f.getFileName() + " (already archived; not loaded, left untouched)");
            continue;
          }
          if ("ACTIVE".equals(r.state)) {
            long oa = 0L;
            long ob = 0L;
            if (r.paying) { if (r.paidA) oa = r.coinsA; if (r.paidB) ob = r.coinsB; }
            Object[] sn = r.settle("CANCELLED", "server-restart", @PKG@.TCodec.listOf(r.itemsA), @PKG@.TCodec.listOf(r.itemsB), oa, ob, (org.bson.BsonArray) null, (org.bson.BsonArray) null);
            writeSnap(r, sn);
            String extra = "";
            if (r.paying) {
              extra = " - it was cut off DURING THE COIN TRANSFER: coins owed back a=" + oa + " b=" + ob + " (a COINS-TAKEN line for this id whose side is not owed back here must be returned by hand)";
              @PKG@.TCfg.warn("trade " + r.id + " was cut off during its coin transfer by a server crash - see trades/trade.log (id=" + r.id + ")");
            }
            log("CANCEL id=" + r.id + " a=" + who(r.ua, r.na) + " b=" + who(r.ub, r.nb) + " reason=server-restart (open when the server stopped; returned at the next join)" + extra);
          }
          RECORDS.put(r.id, r);
          n++;
        } catch (Throwable t) { @PKG@.TCfg.warn("trade file " + f + " cannot be read - left untouched (tell Skyy): " + t); }
      }
    } finally { ds.close(); }
  } catch (Throwable t) { @PKG@.TCfg.warn("could not scan " + @PKG@.TCfg.PDIR + ": " + t); }
  return n;
}""")

# ================= TStore layer 3: the trade request book (TpReq objects, its own map - never mixed with /tpa) =================
M(tst, r"""
public static synchronized String tryAddReq(java.util.UUID from, java.util.UUID to, String fromName, String toName) {
  long now = System.currentTimeMillis();
  @PKG@.TpReq old = (@PKG@.TpReq) TREQ.get(@ES@.key(from, to));
  if (old != null && old.expires > now) return "-You already sent " + toName + " a trade request (" + @ES@.secs(old.expires - now) + " left). /trade cancel takes it back.";
  Long last = (Long) TLAST.get(from);
  long cd = (long) @PKG@.TCfg.COOLDOWN_S * 1000L;
  if (last != null && now - last.longValue() < cd) return "-Please wait " + @ES@.secs(cd - (now - last.longValue())) + " before sending another trade request.";
  TREQ.put(@ES@.key(from, to), new @PKG@.TpReq(from, to, false, fromName, toName, now, now + (long) @PKG@.TCfg.EXPIRE_S * 1000L));
  TLAST.put(from, Long.valueOf(now));
  return null;
}""")
M(tst, r"""
public static synchronized @PKG@.TpReq takeReq(java.util.UUID to, java.util.UUID from) {
  long now = System.currentTimeMillis();
  @PKG@.TpReq best = null;
  java.util.Iterator it = TREQ.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpReq r = (@PKG@.TpReq) it.next();
    if (r == null || !r.to.equals(to) || r.expires <= now) continue;
    if (from != null && !r.from.equals(from)) continue;
    if (best == null || r.created > best.created) best = r;
  }
  if (best != null) TREQ.remove(@ES@.key(best.from, best.to));
  return best;
}""")
M(tst, r"""
public static synchronized int pendingReqFor(java.util.UUID to) {
  long now = System.currentTimeMillis();
  int n = 0;
  java.util.Iterator it = TREQ.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpReq r = (@PKG@.TpReq) it.next();
    if (r != null && r.to.equals(to) && r.expires > now) n++;
  }
  return n;
}""")
M(tst, r"""
public static synchronized java.util.List cancelReqFrom(java.util.UUID from) {
  java.util.ArrayList out = new java.util.ArrayList();
  long now = System.currentTimeMillis();
  java.util.Iterator it = TREQ.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpReq r = (@PKG@.TpReq) it.next();
    if (r == null || !r.from.equals(from)) continue;
    it.remove();
    if (r.expires > now) out.add(r);
  }
  return out;
}""")
# a player left: their own requests are dropped silently (Trade-Spec section 7); requests waiting on them are dropped too (they could
# not accept from offline, and the same-world / distance rule would be checked again anyway) - returned so the senders are told
M(tst, r"""
public static synchronized java.util.List dropReqOf(java.util.UUID u) {
  java.util.ArrayList waiting = new java.util.ArrayList();
  long now = System.currentTimeMillis();
  java.util.Iterator it = TREQ.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpReq r = (@PKG@.TpReq) it.next();
    if (r == null) { it.remove(); continue; }
    if (r.from.equals(u)) { it.remove(); continue; }
    if (r.to.equals(u)) { it.remove(); if (r.expires > now) waiting.add(r); }
  }
  TLAST.remove(u);
  return waiting;
}""")
M(tst, r"""
public static synchronized void pruneReq() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = TREQ.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpReq r = (@PKG@.TpReq) it.next();
    if (r == null) { it.remove(); continue; }
    if (@ES@.online(r.from) == null) { it.remove(); continue; }
    if (@ES@.online(r.to) == null) { it.remove(); if (r.expires > now) tell(r.from, "=" + r.toName + " left the game - your trade request to them was dropped."); continue; }
    if (r.expires <= now) {
      it.remove();
      tell(r.from, "=Your trade request to " + r.toName + " expired.");
      tell(r.to, "=The trade request from " + r.fromName + " expired.");
      log("EXPIRE from=" + who(r.from, r.fromName) + " to=" + who(r.to, r.toName));
    }
  }
  long cd = (long) @PKG@.TCfg.COOLDOWN_S * 1000L;
  it = TLAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Long v = (Long) e.getValue();
    if (v == null || now - v.longValue() >= cd) it.remove();
  }
}""")

# ================= TStore layer 4: world-thread hops, sessions, UI =================
M(tst, r"""
public static void taskDone(@PKG@.TTask t) {
  if (t.kind == 4 && t.uuid != null) DELIVERING.remove(t.uuid);
  if (t.kind == 5 && t.sess != null && t.side >= 0) t.sess.clearRefresh(t.side);
}""")
M(tst, r"""
public static void retry0(@PKG@.TTask t) {
  t.tries = t.tries + 1;
  if (t.tries > 6) { taskDone(t); return; }
  t.expected = null;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(t, 500L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable e) { taskDone(t); }
}""")
M(tst, r"""
public static void hop(@PKG@.TTask t) {
  @PR@ p = @ES@.online(t.uuid);
  if (p == null) { taskDone(t); return; }
  @WLD@ w = @ES@.worldOf(p);
  if (w == null || !w.isAlive()) { retry0(t); return; }
  t.expected = w;
  try { w.execute(t); } catch (Throwable e) { retry0(t); }
}""")

M(tst, r"""
public static boolean registered(@PLA@ p, @PKG@.TWindow w) {
  try {
    if (p == null || w == null) return false;
    int id = w.getId();
    if (id <= 0) return false;
    return p.getWindowManager().getWindow(id) == w;
  } catch (Throwable t) { return false; }
}""")
# at most ONE page rebuild per second per page for changes made by the OTHER side (UI rule: react to real events, never faster than 1/s)
M(tst, r"""
public static void requestRefresh(@PKG@.TSession s, int side) {
  if (s == null || side < 0 || !s.live()) return;
  if (s.page[side] == null) return;
  if (!s.markRefresh(side)) return;
  long delay = s.lastBuilt[side] + 1000L - System.currentTimeMillis();
  if (delay < 80L) delay = 80L;
  @PKG@.TTask t = new @PKG@.TTask(5, s, side, s.u[side], (String) null);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(t, delay, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable e) { s.clearRefresh(side); }
}""")
M(tst, r"""
public static String newId() {
  String t = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").format(java.time.LocalDateTime.now());
  int n = SEQ.incrementAndGet() & 0xfff;
  int r = (int) (Math.random() * 65535.0);
  return t + "-" + Integer.toHexString(0x1000 | n).substring(1) + Integer.toHexString(0x10000 | r).substring(1);
}""")
# both players become busy together or not at all (two accepts in the same instant on two world threads)
M(tst, r"""
public static synchronized boolean claim(@PKG@.TSession s) {
  if (current(s.u[0]) != null || current(s.u[1]) != null) return false;
  SESSIONS.put(s.u[0], s);
  SESSIONS.put(s.u[1], s);
  return true;
}""")
M(tst, r"""
public static synchronized void putBack(@PKG@.TpReq r) {
  if (r != null && r.expires > System.currentTimeMillis() && !TREQ.containsKey(@ES@.key(r.from, r.to))) TREQ.put(@ES@.key(r.from, r.to), r);
}""")
M(tst, r"""
public static @PKG@.TSession newSession(@PR@ a, @PR@ b) {
  @PKG@.TSession s = new @PKG@.TSession();
  s.u[0] = a.getUuid(); s.u[1] = b.getUuid();
  s.name[0] = a.getUsername(); s.name[1] = b.getUsername();
  int cap = @PKG@.TCfg.SLOTS;
  for (int i = 0; i < 2; i++) {
    s.box[i] = new @SIC@((short) cap);
    s.box[i].setGlobalFilter(@FT@.ALLOW_ALL);
    s.epoch[i] = @PKG@.TCfg.bridge().get("profile:epoch:" + s.u[i]);
  }
  s.rec = new @PKG@.TRecord(newId(), s.u[0], s.name[0], s.u[1], s.name[1], cap, System.currentTimeMillis());
  s.rec.keyA = pkey(s.u[0]);
  s.rec.keyB = pkey(s.u[1]);
  if (!claim(s)) return null;
  s.reg[0] = s.box[0].registerChangeEvent(new @PKG@.TChange(s, 0));
  s.reg[1] = s.box[1].registerChangeEvent(new @PKG@.TChange(s, 1));
  java.util.Map br = @PKG@.TCfg.bridge();
  br.put("trade:active:" + s.u[0], Boolean.TRUE);
  br.put("trade:active:" + s.u[1], Boolean.TRUE);
  noteName(s.u[0], s.name[0]);
  noteName(s.u[1], s.name[1]);
  saveSoon(s.rec, 0L);
  return s;
}""")
# open this player's side of the trade. mode 1 = page + offer window, 2 = offer as a vanilla chest (Page.Bench), 3 = page only.
# The page / window on screen before is simply replaced (never closed first). Every window is only a VIEW of the same escrow container,
# so an old one that lingers can do no harm; it is marked dead and closed by validate() / the client.
M(tst, r"""
public static String openUI(@PR@ pr, @REF@ ref, @ST@ st, @PKG@.TSession s, int side, int mode) {
  if (s == null || !s.live()) return "-This trade has ended.";
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  if (busy(s.u[side])) return "-Your profile is still loading - type /trade again in a moment.";
  Object cp = null;
  try { cp = p.getPageManager().getCustomPage(); } catch (Throwable t) { cp = null; }
  if (cp instanceof @PKG@.TradePage) ((@PKG@.TradePage) cp).replacing = true;
  if (s.win[side] != null) s.win[side].dead = true;
  s.win[side] = null;
  @PKG@.TWindow w = null;
  if (mode == 1 || mode == 2) {
    w = new @PKG@.TWindow(s.box[side], s, side, mode);
    s.wins.add(w);
  }
  boolean ok = false;
  try {
    if (mode == 2) {
      ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Bench, true, new @WIN@[] { w });
    } else {
      @PKG@.TradePage tp = new @PKG@.TradePage(pr, s, side, mode);
      tp.win = w;
      if (w != null) w.page = tp;
      s.page[side] = tp;
      if (mode == 1) ok = p.getPageManager().openCustomPageWithWindows(ref, st, tp, new @WIN@[] { w });
      else { p.getPageManager().openCustomPage(ref, st, tp); ok = true; }
    }
  } catch (Throwable t) { @PKG@.TCfg.warn("trade window open failed for " + pr.getUsername() + ": " + t); ok = false; }
  if (!ok) {
    if (w != null) w.dead = true;
    if (cp instanceof @PKG@.TradePage) ((@PKG@.TradePage) cp).replacing = false;
    return "-The trade window could not open - type /trade to try again.";
  }
  if (w != null) s.win[side] = w;
  return null;
}""")
# ---- deliveries of what trades owe (items + coins): only on the owner's world thread, only when the profile gate is open
M(tst, r"""
public static boolean hasOwed(java.util.UUID u) {
  java.util.Iterator it = RECORDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.TRecord r = (@PKG@.TRecord) it.next();
    if (r.owes(u)) return true;
  }
  return false;
}""")
M(tst, r"""
public static int owedStacks(java.util.UUID u) {
  int n = 0;
  java.util.Iterator it = RECORDS.values().iterator();
  while (it.hasNext()) n = n + ((@PKG@.TRecord) it.next()).oweStacks(u);
  return n;
}""")
M(tst, r"""
public static void due(java.util.UUID u, long at) { if (u != null && !STOPPING) DUE.put(u, Long.valueOf(at)); }""")
M(tst, r"""
public static void deliverNow2(java.util.UUID u, boolean loud) {
  if (u == null || STOPPING) return;
  if (@ES@.online(u) == null) return;
  if (!hasOwed(u)) return;
  long now = System.currentTimeMillis();
  if (busy(u)) { due(u, now + 2000L); return; }
  noteEpoch(u);
  long left = settleLeft(u);
  if (left > 0L) { due(u, now + left * 1000L); return; }
  if (DELIVERING.putIfAbsent(u, Boolean.TRUE) != null) { due(u, now + 1500L); return; }
  DUE.remove(u);
  @PKG@.TTask t = new @PKG@.TTask(4, (@PKG@.TSession) null, -1, u, (String) null);
  t.mode = loud ? 1 : 0;
  hop(t);
}""")
M(tst, r"""
public static void deliverNow(java.util.UUID u) { deliverNow2(u, false); }""")
# ---- ending a trade (after its record is decided): maps + bridge cleared, both players' windows + page closed with the result line,
# and each dead escrow container checked again 3 s and 15 s later
M(tst, r"""
public static void endSession(@PKG@.TSession s, String m0, String m1) {
  s.closed = true;
  for (int i = 0; i < 2; i++) { try { if (s.reg[i] != null) s.reg[i].unregister(); } catch (Throwable t) { } }
  SESSIONS.remove(s.u[0], s);
  SESSIONS.remove(s.u[1], s);
  java.util.Map br = @PKG@.TCfg.bridge();
  if (current(s.u[0]) == null) br.remove("trade:active:" + s.u[0]);
  if (current(s.u[1]) == null) br.remove("trade:active:" + s.u[1]);
  for (int i = 0; i < 2; i++) {
    if (@ES@.online(s.u[i]) == null) continue;
    hop(new @PKG@.TTask(2, s, i, s.u[i], i == 0 ? m0 : m1));
  }
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (ex != null && !STOPPING) {
    try {
      ex.schedule(new @PKG@.TJob(5, (@PKG@.TRecord) null, s, (String) null, -1, (String) null), 3000L, java.util.concurrent.TimeUnit.MILLISECONDS);
      ex.schedule(new @PKG@.TJob(5, (@PKG@.TRecord) null, s, (String) null, -1, (String) null), 15000L, java.util.concurrent.TimeUnit.MILLISECONDS);
    } catch (Throwable t) { }
  }
}""")
M(tst, r"""
public static String[] cancelMsg(@PKG@.TSession s, String reason, int by, String byName) {
  String w = (byName == null || byName.length() == 0) ? "Someone" : byName;
  String tail = " Everything you put in comes back to you.";
  String a = "The trade was cancelled.";
  if (reason.equals("player")) a = w + " cancelled the trade.";
  else if (reason.equals("disconnect")) a = w + " left the game - trade cancelled.";
  else if (reason.equals("distance")) a = w + " moved too far away (more than " + @PKG@.TCfg.DIST + " blocks) - trade cancelled.";
  else if (reason.equals("world")) a = w + " left this world - trade cancelled.";
  else if (reason.equals("damage")) a = w + " took damage - trade cancelled.";
  else if (reason.equals("profile")) a = w + "'s profile changed - trade cancelled.";
  else if (reason.equals("offer-changed")) a = "An offer changed at the last moment - trade cancelled to keep both of you safe.";
  else if (reason.equals("coins")) a = w + " does not have the coins they offered any more - trade cancelled.";
  else if (reason.equals("coins-off")) a = "Coin trading is not available right now (turned off, or SkyyCoins is missing) - trade cancelled.";
  else if (reason.equals("write-failed")) a = "The trade could not be saved - cancelled to keep both of you safe (please tell an admin).";
  else if (reason.equals("admin")) a = "An admin cancelled this trade.";
  String m0 = "-" + a + tail;
  String m1 = m0;
  if (reason.equals("player") && by == 0) m0 = "=You cancelled the trade." + tail;
  if (reason.equals("player") && by == 1) m1 = "=You cancelled the trade." + tail;
  if (reason.equals("server-stop")) { m0 = "=The server is stopping - trade cancelled. Your offer comes back when you join again."; m1 = m0; }
  return new String[] { m0, m1 };
}""")
# CANCELLED: each player's own escrow goes back to that player (never swapped); the record is written before anything is delivered.
# owA / owB = coins taken from that player whose refund could not be paid now: they stay OWED (coinOwe) and are paid by the delivery
# (/trade claim, next join) on the profile the trade was made on - never dropped with only a log line
M(tst, r"""
public static void finishCancel(@PKG@.TSession s, @IS@[] ia, @IS@[] ib, String reason, String[] m, long owA, long owB) {
  java.util.ArrayList la = @PKG@.TCodec.docList(ia);
  java.util.ArrayList lb = @PKG@.TCodec.docList(ib);
  Object[] sn = s.rec.settle("CANCELLED", reason, la, lb, owA, owB, @PKG@.TCodec.docArray(la), @PKG@.TCodec.docArray(lb));
  writeSnap(s.rec, sn);
  RECORDS.put(s.rec.id, s.rec);
  log("CANCEL " + ids(s) + " reason=" + reason + " back to a=" + items(ia) + " items, back to b=" + items(ib) + " items" + (owA > 0L || owB > 0L ? ", coins owed back a=" + owA + " b=" + owB : ""));
  String m0 = m[0];
  String m1 = m[1];
  if (owA > 0L) m0 = m0 + " Your " + grp(owA) + " coins could not be given back yet - /trade claim (or your next join) pays them.";
  if (owB > 0L) m1 = m1 + " Your " + grp(owB) + " coins could not be given back yet - /trade claim (or your next join) pays them.";
  endSession(s, m0, m1);
  deliverNow(s.u[0]);
  deliverNow(s.u[1]);
}""")
M(tst, r"""
public static boolean cancelNow(@PKG@.TSession s, String reason, int by, String byName) {
  if (s == null || !s.beginSettle(-1)) return false;
  @IS@[] ia = null;
  @IS@[] ib = null;
  try { ia = drain(s.box[0]); } catch (Throwable t) { @PKG@.TCfg.warn("trade escrow of " + s.name[0] + " could not be emptied (the late check retries): " + t); }
  try { ib = drain(s.box[1]); } catch (Throwable t) { @PKG@.TCfg.warn("trade escrow of " + s.name[1] + " could not be emptied (the late check retries): " + t); }
  if (ia == null) ia = new @IS@[0];
  if (ib == null) ib = new @IS@[0];
  finishCancel(s, ia, ib, reason, cancelMsg(s, reason, by, byName), 0L, 0L);
  return true;
}""")
M(tst, r"""
public static void cancelAsync(@PKG@.TSession s, String reason, int by, String byName) {
  if (s == null) return;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { cancelNow(s, reason, by, byName); return; }
  try { ex.execute(new @PKG@.TJob(4, (@PKG@.TRecord) null, s, reason, by, byName)); } catch (Throwable t) { cancelNow(s, reason, by, byName); }
}""")
# anything a late client move put into a dead escrow container goes back to its owner (DENY_ALL should already refuse such moves)
M(tst, r"""
public static void lateSweep(@PKG@.TSession s) {
  if (s == null) return;
  for (int i = 0; i < 2; i++) {
    try {
      if (s.box[i] == null || stacks(snapshot(s.box[i])) == 0) continue;
      @IS@[] a = drain(s.box[i]);
      if (a == null || a.length == 0) continue;
      @PKG@.TRecord lr = new @PKG@.TRecord(s.rec.id + "-late" + i + "-" + (System.currentTimeMillis() % 1000000L), s.u[0], s.name[0], s.u[1], s.name[1], 0, System.currentTimeMillis());
      lr.keyA = s.rec.keyA;
      lr.keyB = s.rec.keyB;
      java.util.ArrayList l = @PKG@.TCodec.docList(a);
      java.util.ArrayList none = new java.util.ArrayList();
      Object[] sn = null;
      if (i == 0) sn = lr.settle("CANCELLED", "late-return", l, none, 0L, 0L, @PKG@.TCodec.docArray(l), new org.bson.BsonArray());
      else sn = lr.settle("CANCELLED", "late-return", none, l, 0L, 0L, new org.bson.BsonArray(), @PKG@.TCodec.docArray(l));
      writeSnap(lr, sn);
      RECORDS.put(lr.id, lr);
      log("LATE-RETURN id=" + lr.id + " to=" + who(s.u[i], s.name[i]) + " items=" + items(a));
      deliverNow(s.u[i]);
    } catch (Throwable t) { @PKG@.TCfg.warn("late escrow check failed for trade " + s.rec.id + ": " + t); }
  }
}""")
M(tst, r"""
public static String gotText(int n, long coins) {
  String t = "";
  if (coins > 0L) t = t + " You get " + grp(coins) + " coins.";
  if (n > 0) t = t + " " + n + " item(s) are going into your inventory.";
  return t;
}""")
# is this side still on the profile the trade was opened on? (storage key recorded at open + the epoch baseline) - checked right before
# coins move: profile:busy alone misses a switch that finished between the last 1 s tick and this settle (coins:fn:* act on the ACTIVE
# profile's purse)
M(tst, r"""
public static boolean keyOk(@PKG@.TSession s, int side) {
  java.util.UUID u = s.u[side];
  String k = s.rec.keyOf(side);
  if (k.length() > 0 && !k.equals(pkey(u))) return false;
  Object ep = @PKG@.TCfg.bridge().get("profile:epoch:" + u);
  Object was = s.epoch[side];
  if (ep != null && was != null && !ep.equals(was)) return false;
  return true;
}""")
# give taken coins back; what cannot be paid now (SkyyCoins refused, or that player is on another profile) is returned as still owed
M(tst, r"""
public static long refund(@PKG@.TSession s, int side, long n) {
  if (n <= 0L) return 0L;
  java.util.UUID u = s.u[side];
  if (keyOk(s, side) && coinsAdd(u, n)) { log("COINS-REFUND id=" + s.rec.id + " " + n + " coins back to " + who(u, s.name[side])); return 0L; }
  log("COIN-OWED id=" + s.rec.id + " " + n + " coins back to " + who(u, s.name[side]) + " (refund not possible now - paid on their next join or /trade claim, on the profile the trade was made on)");
  @PKG@.TCfg.warn("trade " + s.rec.id + ": " + n + " coins for " + u + " are owed back (refund not possible now; /trade claim or their next join pays them)");
  return n;
}""")
# a coin take that worked: logged at once (appended, no fsync - survives a process kill), then the paid marker is written
M(tst, r"""
public static boolean takeFor(@PKG@.TSession s, int side, long n) {
  if (n <= 0L) return true;
  java.util.UUID u = s.u[side];
  if (coinsTake(u, n) != 1) return false;
  log("COINS-TAKEN id=" + s.rec.id + " " + n + " coins from " + who(u, s.name[side]));
  writeSnap(s.rec, s.rec.markPaid(side));
  return true;
}""")
# the countdown reached zero (trade thread). Containers have been DENY_ALL since both clicked Ready. Emptied with ONE clear() each (drain),
# compared with what was agreed; both profiles checked; coins: PAYING marker on disk, take A, take B (each marked paid on disk; A refunded
# if B fails); the COMPLETED record is ON DISK before anything is paid out.
M(tst, r"""
public static void execute(@PKG@.TSession s, int tok) {
  if (!s.beginSettle(tok)) return;
  @IS@[] ia = null;
  @IS@[] ib = null;
  try { ia = drain(s.box[0]); } catch (Throwable t) { @PKG@.TCfg.warn("trade escrow of " + s.name[0] + " could not be emptied (the late check retries): " + t); }
  try { ib = drain(s.box[1]); } catch (Throwable t) { @PKG@.TCfg.warn("trade escrow of " + s.name[1] + " could not be emptied (the late check retries): " + t); }
  boolean bad = ia == null || ib == null;
  if (ia == null) ia = new @IS@[0];
  if (ib == null) ib = new @IS@[0];
  java.util.UUID ua = s.u[0];
  java.util.UUID ub = s.u[1];
  String why = null;
  int by = -1;
  if (bad) why = "offer-changed";
  else if (!sig(ia).equals(s.agreed[0]) || !sig(ib).equals(s.agreed[1])) why = "offer-changed";
  if (why == null && @ES@.online(ua) == null) { why = "disconnect"; by = 0; }
  if (why == null && @ES@.online(ub) == null) { why = "disconnect"; by = 1; }
  if (why == null && busy(ua)) { why = "profile"; by = 0; }
  if (why == null && busy(ub)) { why = "profile"; by = 1; }
  if (why == null && !keyOk(s, 0)) { why = "profile"; by = 0; }
  if (why == null && !keyOk(s, 1)) { why = "profile"; by = 1; }
  long ca = s.agreedCoins[0];
  long cb = s.agreedCoins[1];
  boolean coinTrade = ca > 0L || cb > 0L;
  if (why == null && coinTrade && !coinsOn()) why = "coins-off";
  if (why == null && coinTrade && !writeSnap(s.rec, s.rec.markPaying(ia, ib, ca, cb))) why = "write-failed";
  boolean tookA = false;
  boolean tookB = false;
  if (why == null && ca > 0L) { if (takeFor(s, 0, ca)) tookA = true; else { why = "coins"; by = 0; } }
  if (why == null && cb > 0L) { if (takeFor(s, 1, cb)) tookB = true; else { why = "coins"; by = 1; } }
  if (why != null) {
    long owA = tookA ? refund(s, 0, ca) : 0L;
    long owB = tookB ? refund(s, 1, cb) : 0L;
    finishCancel(s, ia, ib, why, cancelMsg(s, why, by, by >= 0 ? s.name[by] : (String) null), owA, owB);
    return;
  }
  java.util.ArrayList toA = @PKG@.TCodec.docList(ib);
  java.util.ArrayList toB = @PKG@.TCodec.docList(ia);
  Object[] sn = s.rec.settle("COMPLETED", "", toA, toB, cb, ca, @PKG@.TCodec.docArray(toB), @PKG@.TCodec.docArray(toA));
  if (!writeSnap(s.rec, sn)) {
    long owA = tookA ? refund(s, 0, ca) : 0L;
    long owB = tookB ? refund(s, 1, cb) : 0L;
    java.util.ArrayList ra = @PKG@.TCodec.docList(ia);
    java.util.ArrayList rb = @PKG@.TCodec.docList(ib);
    Object[] sn2 = s.rec.settle("CANCELLED", "write-failed", ra, rb, owA, owB, @PKG@.TCodec.docArray(ra), @PKG@.TCodec.docArray(rb));
    writeSnap(s.rec, sn2);
    RECORDS.put(s.rec.id, s.rec);
    log("CANCEL " + ids(s) + " reason=write-failed" + (owA > 0L || owB > 0L ? " coins owed back a=" + owA + " b=" + owB : ""));
    String[] m = cancelMsg(s, "write-failed", -1, (String) null);
    String m0 = m[0];
    String m1 = m[1];
    if (owA > 0L) m0 = m0 + " Your " + grp(owA) + " coins could not be given back yet - /trade claim (or your next join) pays them.";
    if (owB > 0L) m1 = m1 + " Your " + grp(owB) + " coins could not be given back yet - /trade claim (or your next join) pays them.";
    endSession(s, m0, m1);
    deliverNow(ua);
    deliverNow(ub);
    return;
  }
  RECORDS.put(s.rec.id, s.rec);
  log("COMPLETE " + ids(s) + " a gave " + items(ia) + " items in " + stacks(ia) + " stacks + " + ca + " coins, b gave " + items(ib) + " items in " + stacks(ib) + " stacks + " + cb + " coins");
  // payouts: only to the profile the trade was made on; otherwise they stay owed (deliverTask pays coinOwe only on the matching key)
  if (cb > 0L) { if (keyOk(s, 0) && coinsAdd(ua, cb)) s.rec.clearCoinOwe(0); else log("COIN-OWED id=" + s.rec.id + " " + cb + " coins to " + who(ua, s.name[0]) + " (paid on their next join or /trade claim, on the profile the trade was made on)"); }
  if (ca > 0L) { if (keyOk(s, 1) && coinsAdd(ub, ca)) s.rec.clearCoinOwe(1); else log("COIN-OWED id=" + s.rec.id + " " + ca + " coins to " + who(ub, s.name[1]) + " (paid on their next join or /trade claim, on the profile the trade was made on)"); }
  saveNow(s.rec);
  endSession(s, "+Trade with " + s.name[1] + " complete!" + gotText(items(ib), cb), "+Trade with " + s.name[0] + " complete!" + gotText(items(ia), ca));
  deliverNow(ua);
  deliverNow(ub);
}""")
M(tst, r"""
public static void countdownStep(@PKG@.TCountdown c) {
  @PKG@.TSession s = c.sess;
  if (s == null || !s.countdownValid(c.token)) return;
  if (c.left <= 0) { execute(s, c.token); return; }
  if (c.left < c.total) sayBoth(s, "=" + c.left + "...");
  c.left = c.left - 1;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (ex == null || STOPPING) return;
  try { ex.schedule(c, 1000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { s.stopCountdown(c.token); }
}""")
# both Ready: the containers are already locked (inside toggleReady); record what was agreed, then count down on the trade thread
M(tst, r"""
public static String startCountdown(@PKG@.TSession s, int tok, int by) {
  String sa = sig(snapshot(s.box[0]));
  String sb = sig(snapshot(s.box[1]));
  if (!s.setAgreed(tok, sa, sb)) return "=The offers just changed - click Ready again.";
  if (sa.length() == 0 && sb.length() == 0 && s.agreedCoins[0] <= 0L && s.agreedCoins[1] <= 0L) {
    s.stopCountdown(tok);
    sayBoth(s, "-Both offers are empty - there is nothing to trade.");
    return "-Both offers are empty - put something in first.";
  }
  int n = @PKG@.TCfg.COUNTDOWN_S;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (ex == null || STOPPING) { s.stopCountdown(tok); return "-The server is stopping."; }
  log("COUNTDOWN-START " + ids(s) + " " + n + "s");
  sayBoth(s, "+Both ready! Trading in " + secWord(n) + " - Not ready or Cancel trade stops it.");
  try { ex.schedule(new @PKG@.TCountdown(s, tok, n), 0L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { s.stopCountdown(tok); return "-Could not start the countdown - click Ready again."; }
  return "+Both ready - trading in " + secWord(n) + ".";
}""")
M(tst, r"""
public static void syncOffers(@PKG@.TSession s) {
  s.rec.setOffer(0, s.coins[0], s.ready[0]);
  s.rec.setOffer(1, s.coins[1], s.ready[1]);
  saveSoon(s.rec, (long) @PKG@.TCfg.SAVE_MS);
}""")
# a container change event (the engine fires it AFTER releasing the container lock): any change of an offer clears BOTH Ready marks.
# The item left (or came back into) the player's inventory in that same engine move, so the record is written AT ONCE (saveNow), not
# after tradeSaveDelayMillis: a crash in between would otherwise lose an item the engine had already saved out of the inventory.
M(tst, r"""
public static void onBoxChange(@PKG@.TSession s, int side) {
  if (s == null) return;
  int r = s.onChange(side);
  if (r < 0) return;
  boolean ch = false;
  try { ch = s.rec.copyIn(side, snapshot(s.box[side])); } catch (Throwable t) { @PKG@.TCfg.warnOnce("copy", "trade escrow snapshot failed: " + t); }
  if (r >= 1) { s.rec.setOffer(0, s.coins[0], s.ready[0]); s.rec.setOffer(1, s.coins[1], s.ready[1]); }
  if (ch) saveNow(s.rec);
  else if (r >= 1) saveSoon(s.rec, (long) @PKG@.TCfg.SAVE_MS);
  if (r == 2) {
    sayBoth(s, "=" + s.name[side] + " changed their offer - countdown stopped. Both of you must click Ready again.");
    log("COUNTDOWN-CANCEL " + ids(s) + " offer changed by " + s.name[side]);
  } else if (r == 1) {
    tell(s.u[1 - side], "=" + s.name[side] + " changed their offer - both Ready marks were cleared.");
    log("UNREADY " + ids(s) + " offer changed by " + s.name[side]);
  }
  requestRefresh(s, 0);
  requestRefresh(s, 1);
}""")
# ---- page clicks (the page's world thread)
M(tst, r"""
public static String clickReady(@PKG@.TradePage page) {
  @PKG@.TSession s = page.sess;
  int me = page.side;
  if (s == null || !s.live()) return "-This trade has ended.";
  java.util.UUID u = s.u[me];
  if (busy(u)) return "-Your profile is still loading - try again in a moment.";
  if (!s.ready[me] && s.state == 0 && s.coins[me] > 0L) {
    if (!coinsOn()) return "-Coin trading is off right now - click Clear my coins (or Cancel trade).";
    Long bal = coinsGet(u);
    if (bal == null) return "-Your purse cannot be read right now - try again, or set your coin offer to 0.";
    if (bal.longValue() < s.coins[me]) return "-You only have " + grp(bal.longValue()) + " coins - lower your coin offer first.";
  } else if (!s.ready[me] && s.state == 0 && s.coins[1 - me] > 0L && !coinsOn()) {
    return "-Coin trading is off right now - " + s.name[1 - me] + " has to clear their coin offer first (or Cancel trade).";
  }
  int r = s.toggleReady(me);
  if (r < 0) return "-This trade has ended.";
  syncOffers(s);
  String mine = s.name[me];
  String res = null;
  if (r == 0) { log("UNREADY " + ids(s) + " by " + mine); tell(s.u[1 - me], "=" + mine + " is not ready any more."); res = "=You are not ready any more."; }
  else if (r == 1) { log("READY " + ids(s) + " by " + mine); tell(s.u[1 - me], "=" + mine + " is ready - check their offer, then click Ready."); res = "+You are ready - waiting for " + s.name[1 - me] + "."; }
  else if (r == 3) { log("COUNTDOWN-CANCEL " + ids(s) + " by " + mine); sayBoth(s, "=" + mine + " is not ready any more - countdown stopped."); res = "=Countdown stopped."; }
  else { log("READY " + ids(s) + " by " + mine); res = startCountdown(s, r - 10, me); }
  requestRefresh(s, 1 - me);
  return res;
}""")
M(tst, r"""
public static String clickCoins(@PKG@.TradePage page, String text) {
  @PKG@.TSession s = page.sess;
  int me = page.side;
  if (s == null || !s.live()) return "-This trade has ended.";
  long n = @PKG@.TCfg.parseAmount(text);
  if (n < 0L) return "-Type a number of coins (for example 2500, 2k or 1.5m).";
  // clearing (0) always works, so an offer made before coin trading went away can be taken back
  if (n > 0L && !coinsOn()) return "-" + coinsNote();
  if (@PKG@.TCfg.MAX_COINS > 0L && n > @PKG@.TCfg.MAX_COINS) return "-The most coins one trade can carry here is " + grp(@PKG@.TCfg.MAX_COINS) + ".";
  if (n > 0L) {
    Long bal = coinsGet(s.u[me]);
    if (bal == null) return "-Your purse cannot be read right now - try again.";
    if (n > bal.longValue()) return "-You only have " + grp(bal.longValue()) + " coins.";
  }
  int r = s.setCoins(me, n);
  if (r == -1) return "-This trade has ended.";
  if (r == -2) return "-Offers are locked during the countdown - click Not ready first.";
  if (r == 0) return "=Your coin offer is already " + grp(n) + ".";
  syncOffers(s);
  log("COINS " + ids(s) + " " + s.name[me] + " offers " + n);
  String cleared = r == 2 ? " Both Ready marks were cleared." : "";
  tell(s.u[1 - me], "=" + s.name[me] + (n > 0L ? " now offers " + grp(n) + " coins." : " took their coins out of the offer.") + cleared);
  requestRefresh(s, 1 - me);
  return (n > 0L ? "+You offer " + grp(n) + " coins." : "+Your coin offer is cleared.") + cleared;
}""")
M(tst, r"""
public static void clickCancel(@PKG@.TradePage page) {
  @PKG@.TSession s = page.sess;
  if (s == null || !s.live()) return;
  cancelAsync(s, "player", page.side, s.name[page.side]);
}""")
M(tst, r"""
public static String clickChest(@PKG@.TradePage page, @REF@ ref, @ST@ st) {
  @PKG@.TSession s = page.sess;
  if (s == null || !s.live()) return "-This trade has ended.";
  if (s.state == 1) return "-Offers are locked during the countdown - click Not ready first.";
  page.replacing = true;
  String r = openUI(page.pr(), ref, st, s, page.side, 2);
  if (r != null) page.replacing = false;
  return r;
}""")
# our page left the screen (Esc, Close, replaced): its window is closed 1.5 s later if still registered; a real close (not a replacement
# by our own code) stops the countdown / clears your Ready and says how to come back
M(tst, r"""
public static void pageDismissed(@PKG@.TradePage page) {
  if (page == null || page.dismissed) return;
  page.dismissed = true;
  @PKG@.TSession s = page.sess;
  if (s == null) return;
  int me = page.side;
  if (s.page[me] == page) s.page[me] = null;
  if (page.win != null) {
    @PKG@.TTask t = new @PKG@.TTask(6, s, me, s.u[me], (String) null);
    t.win = page.win;
    try { @HSV@.SCHEDULED_EXECUTOR.schedule(t, 1500L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable e) { }
  }
  if (!s.live() || page.replacing) return;
  int r = s.stopForClose(me);
  if (r == 2) { sayBoth(s, "=" + s.name[me] + " closed the trade page - countdown stopped."); log("COUNTDOWN-CANCEL " + ids(s) + " page closed by " + s.name[me]); }
  if (r > 0) { syncOffers(s); requestRefresh(s, 1 - me); }
  tell(s.u[me], "=Trade page closed - the trade stays open. /trade opens it again, /trade cancel ends it.");
}""")
M(tst, r"""
public static void windowClosed(@PKG@.TWindow w) {
  if (w == null || w.dead) return;
  w.dead = true;
  @PKG@.TSession s = w.sess;
  if (s == null || !s.live()) return;
  int side = w.side;
  if (s.win[side] == w) s.win[side] = null;
  int r = s.stopForClose(side);
  if (r == 2) { sayBoth(s, "=" + s.name[side] + " closed their offer - countdown stopped."); log("COUNTDOWN-CANCEL " + ids(s) + " offer window closed by " + s.name[side]); }
  if (r > 0) { syncOffers(s); requestRefresh(s, 1 - side); }
  if (w.mode == 2) {
    @PKG@.TTask t = new @PKG@.TTask(7, s, side, s.u[side], (String) null);
    try { @HSV@.SCHEDULED_EXECUTOR.schedule(t, 400L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable e) { }
  }
}""")
# ValidatedWindow.validate (the engine calls it on player movement): false closes the window
M(tst, r"""
public static boolean windowValid(@PKG@.TWindow w, @REF@ ref, @CA@ a) {
  if (w == null || w.dead) return false;
  @PKG@.TSession s = w.sess;
  if (s == null || !s.live()) return false;
  if (busy(s.u[w.side])) return false;
  return true;
}""")
# ---- the world-thread task bodies (TTask kinds)
M(tst, r"""
public static void openTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  String e = openUI(pr, ref, st, t.sess, t.side, t.mode);
  if (e != null) tellPr(pr, e);
}""")
M(tst, r"""
public static void closeUiTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TSession s = t.sess;
  Object cp = null;
  try { cp = p.getPageManager().getCustomPage(); } catch (Throwable e) { cp = null; }
  boolean ours = cp instanceof @PKG@.TradePage && ((@PKG@.TradePage) cp).sess == s;
  if (ours) ((@PKG@.TradePage) cp).clearGrids();
  java.util.Iterator it = s.wins.iterator();
  while (it.hasNext()) {
    @PKG@.TWindow w = (@PKG@.TWindow) it.next();
    if (w.side != t.side) continue;
    w.dead = true;
    if (registered(p, w)) { try { p.getWindowManager().closeWindow(ref, w.getId(), st); } catch (Throwable e) { } }
  }
  if (ours) { try { p.getPageManager().setPage(ref, st, @PGE@.None); } catch (Throwable e) { } }
  if (t.msg != null) tellPr(pr, t.msg);
}""")
M(tst, r"""
public static void posTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TSession s = t.sess;
  int i = t.side;
  if (s == null || !s.live() || i < 0) return;
  @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  if (tc != null && tc.getPosition() != null) {
    @VEC@ v = tc.getPosition();
    s.px[i] = v.x; s.py[i] = v.y; s.pz[i] = v.z;
    s.wu[i] = pr.getWorldUuid();
    if (!s.hasStart[i]) { s.sx[i] = v.x; s.sy[i] = v.y; s.sz[i] = v.z; s.sw[i] = s.wu[i]; s.hasStart[i] = true; }
    s.posAt[i] = System.currentTimeMillis();
    s.hasPos[i] = true;
  }
  try {
    @ESM@ m = (@ESM@) st.getComponent(ref, @ESM@.getComponentType());
    if (m != null) {
      @ESV@ hv = m.get(@DST@.getHealth());
      if (hv != null) {
        float h = hv.get();
        if (s.hpSeen[i] && h < s.hp[i] - 0.05f) s.hurt[i] = true;
        s.hp[i] = h;
        s.hpSeen[i] = true;
      }
    }
  } catch (Throwable e) { }
}""")
M(tst, r"""
public static void deliverTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  java.util.UUID u = t.uuid;
  try {
    if (busy(u)) { due(u, System.currentTimeMillis() + 2000L); return; }
    int given = 0;
    int left = 0;
    int orphan = 0;
    int waiting = 0;
    long coinsGot = 0L;
    boolean restart = false;
    String key = pkey(u);
    java.util.ArrayList recs = new java.util.ArrayList(RECORDS.values());
    for (int k = 0; k < recs.size(); k++) {
      @PKG@.TRecord r = (@PKG@.TRecord) recs.get(k);
      if (!r.owes(u)) continue;
      for (int side = 0; side < 2; side++) {
        if (!u.equals(r.uOf(side))) continue;
        String want0 = r.keyOf(side);
        if (want0.length() > 0 && !want0.equals(key)) { waiting = waiting + r.oweCopy(side).size() + (r.coinOwe(side) > 0L ? 1 : 0); continue; }
        java.util.ArrayList docs = r.oweCopy(side);
        boolean changed = false;
        int g0 = 0;
        int l0 = 0;
        if (!docs.isEmpty()) {
          java.util.ArrayList keep = new java.util.ArrayList();
          for (int j = 0; j < docs.size(); j++) {
            org.bson.BsonDocument d = (org.bson.BsonDocument) docs.get(j);
            @IS@ s = @PKG@.TCodec.stackOf(d);
            if (s == null) { keep.add(d); orphan++; continue; }
            int want = s.getQuantity();
            int added = give(p, s);
            if (added > 0) { changed = true; g0 = g0 + added; }
            if (added < want) {
              if (added > 0) keep.add(@PKG@.TCodec.slotDoc(j, s.withQuantity(want - added)));
              else keep.add(d);
              l0 = l0 + (want - added);
            }
          }
          if (changed) r.replaceOwe(side, keep);
        }
        long co = r.coinOwe(side);
        long c0 = 0L;
        if (co > 0L && coinsAdd(u, co)) { r.clearCoinOwe(side); c0 = co; changed = true; }
        left = left + l0;
        if (changed) {
          given = given + g0;
          coinsGot = coinsGot + c0;
          boolean rs = "server-restart".equals(r.reason);
          if (rs) restart = true;
          log((rs ? "RETURN-AT-JOIN" : "DELIVER") + " id=" + r.id + " to=" + who(u, pr.getUsername()) + " items=" + g0 + " coins=" + c0 + " still-owed=" + l0);
          saveNow(r);
        }
      }
    }
    if (given > 0) { try { p.markNeedsSave(); } catch (Throwable e) { } }
    if (given > 0 || coinsGot > 0L) {
      String what = given > 0 ? given + " item(s) added to your inventory" : "";
      if (coinsGot > 0L) what = what + (given > 0 ? " and " : "") + grp(coinsGot) + " coins added to your purse";
      tellPr(pr, "+" + (restart ? "Returned from a trade that was open when the server stopped: " : "From your trade: ") + what + ".");
    }
    if (left > 0) tellPr(pr, "-" + left + " item(s) from a trade did not fit - make room in your inventory, then type /trade claim.");
    if (orphan > 0) tellPr(pr, "-" + orphan + " stack(s) from a trade are items this server does not have right now - kept safe, please tell an admin.");
    if (waiting > 0 && (t.mode == 1 || given > 0)) tellPr(pr, "=" + waiting + " thing(s) from a trade belong to the profile you traded on - switch back to that profile, then /trade claim.");
  } catch (Throwable e) {
    @PKG@.TCfg.warn("trade delivery failed for " + u + " (kept owed, retried on /trade claim or the next join): " + e);
  } finally {
    DELIVERING.remove(u);
  }
}""")
M(tst, r"""
public static void refreshTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TSession s = t.sess;
  s.clearRefresh(t.side);
  if (!s.live()) return;
  Object cp = p.getPageManager().getCustomPage();
  if (cp != null && cp == s.page[t.side] && cp instanceof @PKG@.TradePage) ((@PKG@.TradePage) cp).refresh();
}""")
M(tst, r"""
public static void closeWinTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TWindow w = t.win;
  if (w == null || !registered(p, w)) return;
  @PKG@.TSession s = w.sess;
  Object cp = null;
  try { cp = p.getPageManager().getCustomPage(); } catch (Throwable e) { cp = null; }
  boolean keep = !w.dead && s != null && s.live() && s.win[w.side] == w && w.page != null && cp == w.page;
  if (keep) return;
  w.dead = true;
  if (s != null && s.win[w.side] == w) s.win[w.side] = null;
  try { p.getWindowManager().closeWindow(ref, w.getId(), st); } catch (Throwable e) { }
}""")
M(tst, r"""
public static void reopenTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  @PKG@.TSession s = t.sess;
  if (s == null || !s.live() || s.win[t.side] != null) return;
  if (p.getPageManager().getCustomPage() != null) return;
  String e = openUI(pr, ref, st, s, t.side, 3);
  if (e != null) tellPr(pr, e);
}""")
# 0.1.3: the ONE delayed refresh after "Reload file" (TStore.laterRefresh): rebuild the settings page if it is still the open page, so it
# shows the values the kit's reload routine just applied; otherwise nothing (the result was already on the page)
M(tst, r"""
public static void cfgResultTask(@PKG@.TTask t, @PR@ pr, @REF@ ref, @ST@ st, @PLA@ p) {
  if (!(t.obj instanceof @PKG@.TCfgPage)) return;
  @PKG@.TCfgPage pg = (@PKG@.TCfgPage) t.obj;
  Object cp = null;
  try { cp = p.getPageManager().getCustomPage(); } catch (Throwable e) { cp = null; }
  if (cp == pg) pg.refresh();
}""")
M(tst, r"""
public static void taskRun(@PKG@.TTask t) {
  try {
    if (t.expected == null) { hop(t); return; }
    @PR@ pr = @ES@.online(t.uuid);
    if (pr == null) { taskDone(t); return; }
    @WLD@ here = @ES@.worldOf(pr);
    if (here != t.expected) { retry0(t); return; }
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) { retry0(t); return; }
    @ST@ st = ref.getStore();
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { retry0(t); return; }
    int k = t.kind;
    if (k == 1) openTask(t, pr, ref, st, p);
    else if (k == 2) closeUiTask(t, pr, ref, st, p);
    else if (k == 3) posTask(t, pr, ref, st, p);
    else if (k == 4) deliverTask(t, pr, ref, st, p);
    else if (k == 5) refreshTask(t, pr, ref, st, p);
    else if (k == 6) closeWinTask(t, pr, ref, st, p);
    else if (k == 7) reopenTask(t, pr, ref, st, p);
    else if (k == 8) cfgResultTask(t, pr, ref, st, p);
  } catch (Throwable e) {
    @PKG@.TCfg.warnOnce("task" + t.kind, "trade task " + t.kind + " failed: " + e);
    taskDone(t);
  }
}""")
# ---- commands (the player's world thread)
M(tst, r"""
public static void usage(@PR@ pr) {
  tellPr(pr, "=/trade <player> - ask a player near you to trade. /trade accept [player] - /trade deny [player] - /trade cancel - /trade claim");
  if (!@PKG@.TCfg.ENABLED) tellPr(pr, "-Trading is turned off on this server.");
  int n = pendingReqFor(pr.getUuid());
  if (n > 0) tellPr(pr, "=You have " + n + " pending trade request(s) - /trade accept opens the newest.");
  if (hasOwed(pr.getUuid())) tellPr(pr, "=A trade still owes you something - /trade claim.");
}""")
M(tst, r"""
public static void request(@PR@ pr, @REF@ ref, @ST@ st, Object t) {
  if (!@PKG@.TCfg.ENABLED) { tellPr(pr, "-Trading is turned off on this server."); return; }
  if (!(t instanceof @PR@)) { tellPr(pr, "-Usage: /trade <player>"); return; }
  @PR@ target = (@PR@) t;
  java.util.UUID me = pr.getUuid();
  java.util.UUID tu = target.getUuid();
  String them = target.getUsername();
  if (tu.equals(me)) { tellPr(pr, "-You can't trade with yourself."); return; }
  if (@ES@.online(tu) == null) { tellPr(pr, "-" + them + " is not online."); return; }
  if (current(me) != null) { tellPr(pr, "-Finish your open trade first (or /trade cancel)."); return; }
  if (current(tu) != null) { tellPr(pr, "-" + them + " is already trading with someone."); return; }
  String g = gate(me, (String) null);
  if (g == null) g = gate(tu, them);
  if (g == null) g = rangeCheck(pr, ref, st, target);
  if (g != null) { tellPr(pr, g); return; }
  String myName = pr.getUsername();
  String err = tryAddReq(me, tu, myName, them);
  if (err != null) { tellPr(pr, err); return; }
  noteName(me, myName);
  noteName(tu, them);
  log("REQUEST from=" + who(me, myName) + " to=" + who(tu, them));
  int ex = @PKG@.TCfg.EXPIRE_S;
  tellPr(pr, "=Trade request sent to " + them + ". They have " + ex + "s to accept. /trade cancel takes it back.");
  tellPr(target, "=" + myName + " wants to trade with you. /trade accept " + myName + " opens the trade, /trade deny " + myName + " refuses (" + ex + "s).");
}""")
M(tst, r"""
public static void accept(@PR@ pr, @REF@ ref, @ST@ st, java.util.UUID from) {
  if (!@PKG@.TCfg.ENABLED) { tellPr(pr, "-Trading is turned off on this server."); return; }
  java.util.UUID me = pr.getUuid();
  if (current(me) != null) { tellPr(pr, "-You are already trading - finish that trade first (or /trade cancel)."); return; }
  @PKG@.TpReq r = takeReq(me, from);
  if (r == null) { tellPr(pr, from == null ? "-You have no pending trade requests." : "-No pending trade request from that player."); return; }
  @PR@ a = @ES@.online(r.from);
  if (a == null) { tellPr(pr, "-" + r.fromName + " is no longer online."); return; }
  String an = a.getUsername();
  if (current(r.from) != null) { tellPr(pr, "-" + an + " is already trading with someone else."); return; }
  String g = gate(me, (String) null);
  if (g == null) g = gate(r.from, an);
  if (g == null) g = rangeCheck(pr, ref, st, a);
  if (g != null) { putBack(r); tellPr(pr, g); return; }
  @PKG@.TSession s = newSession(a, pr);
  if (s == null) { tellPr(pr, "-One of you just started another trade."); return; }
  log("ACCEPT " + ids(s));
  int mode = @PKG@.TCfg.PAGE_MODE ? 1 : 2;
  String e = openUI(pr, ref, st, s, 1, mode);
  if (e != null) tellPr(pr, e);
  @PKG@.TTask ot = new @PKG@.TTask(1, s, 0, s.u[0], (String) null);
  ot.mode = mode;
  hop(ot);
  tell(s.u[0], "+" + pr.getUsername() + " accepted - the trade is open.");
  tellPr(pr, "+Trade with " + an + " is open.");
  int left = pendingReqFor(me);
  if (left > 0) tellPr(pr, "=You still have " + left + " other pending trade request(s).");
}""")
M(tst, r"""
public static void deny(@PR@ pr, java.util.UUID from) {
  @PKG@.TpReq r = takeReq(pr.getUuid(), from);
  if (r == null) { tellPr(pr, from == null ? "-You have no pending trade requests." : "-No pending trade request from that player."); return; }
  tellPr(pr, "=Refused the trade request from " + r.fromName + ".");
  tell(r.from, "-" + pr.getUsername() + " refused your trade request.");
  log("DENY from=" + who(r.from, r.fromName) + " to=" + who(r.to, r.toName));
}""")
M(tst, r"""
public static void cancelCmd(@PR@ pr) {
  java.util.UUID me = pr.getUuid();
  java.util.List l = cancelReqFrom(me);
  for (int i = 0; i < l.size(); i++) {
    @PKG@.TpReq r = (@PKG@.TpReq) l.get(i);
    tell(r.to, "=" + pr.getUsername() + " took back their trade request.");
  }
  @PKG@.TSession s = current(me);
  if (l.isEmpty() && s == null) { tellPr(pr, "-You have no open trade and no trade request to cancel."); return; }
  if (!l.isEmpty()) tellPr(pr, "=Took back " + l.size() + " trade request(s).");
  if (s != null) cancelAsync(s, "player", s.side(me), pr.getUsername());
}""")
M(tst, r"""
public static void reopen(@PR@ pr, @REF@ ref, @ST@ st) {
  @PKG@.TSession s = current(pr.getUuid());
  if (s == null) { usage(pr); return; }
  String e = openUI(pr, ref, st, s, s.side(pr.getUuid()), @PKG@.TCfg.PAGE_MODE ? 1 : 3);
  if (e != null) tellPr(pr, e);
}""")
M(tst, r"""
public static void claim(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  if (!hasOwed(u)) { tellPr(pr, "=Nothing from a trade is waiting for you."); return; }
  if (busy(u)) { tellPr(pr, "-Your profile is still loading - try again in a moment."); return; }
  noteEpoch(u);
  long left = settleLeft(u);
  if (left > 0L) { tellPr(pr, "=Your profile just changed - your trade items come in " + left + " s."); due(u, System.currentTimeMillis() + left * 1000L); return; }
  tellPr(pr, "=Giving you what your trades owe you (" + owedStacks(u) + " stack(s))...");
  deliverNow2(u, true);
}""")
M(tst, r"""
public static void adminLog(@PR@ pr, String whoText) {
  try {
    java.nio.file.Path f = @PKG@.TCfg.LOGF;
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { tellPr(pr, "=No trades logged yet."); return; }
    java.io.RandomAccessFile raf = new java.io.RandomAccessFile(f.toFile(), "r");
    byte[] buf = null;
    long start = 0L;
    try {
      long len = raf.length();
      start = len > 65536L ? len - 65536L : 0L;
      buf = new byte[(int) (len - start)];
      raf.seek(start);
      raf.readFully(buf);
    } finally { raf.close(); }
    String[] lines = new String(buf, "UTF-8").split("\n");
    String needle = null;
    String uid = null;
    if (whoText != null && whoText.trim().length() > 0) {
      needle = whoText.trim().toLowerCase();
      java.util.UUID u = resolve(whoText);
      if (u != null) uid = u.toString();
    }
    java.util.ArrayList hits = new java.util.ArrayList();
    for (int i = (start > 0L ? 1 : 0); i < lines.length; i++) {
      String l = lines[i].trim();
      if (l.length() == 0) continue;
      if (needle != null && l.toLowerCase().indexOf(needle) < 0 && (uid == null || l.indexOf(uid) < 0)) continue;
      hits.add(l);
    }
    String forWho = needle != null ? " for " + whoText.trim() : "";
    if (hits.isEmpty()) { tellPr(pr, "=No trade log lines" + forWho + "."); return; }
    int from = hits.size() > 12 ? hits.size() - 12 : 0;
    tellPr(pr, "=Last " + (hits.size() - from) + " trade log line(s)" + forWho + " (all of them: trades/trade.log):");
    for (int i = from; i < hits.size(); i++) {
      String l = (String) hits.get(i);
      if (l.length() > 240) l = l.substring(0, 240) + " ...";
      @ES@.say(pr, l, "#cfe3ff");
    }
  } catch (Throwable t) { tellPr(pr, "-Could not read trades/trade.log: " + t); }
}""")
# /tradeadmin return, the work itself: on the TRADE thread like every other cancel (it empties both escrows and writes the record with
# an fsync - never on the admin's world thread); the admin is answered in chat (PlayerRef.sendMessage is safe from any thread)
M(tst, r"""
public static void adminReturnNow(java.util.UUID au, String an, java.util.UUID tu) {
  @PKG@.TSession s = current(tu);
  boolean cancelled = s != null && cancelNow(s, "admin", -1, an);
  int n = owedStacks(tu);
  boolean any = hasOwed(tu);
  log("ADMIN-RETURN by=" + an + " target=" + tu + (cancelled ? " (open trade cancelled)" : "") + " owed-stacks=" + n);
  String pre = cancelled ? "+Cancelled their open trade. " : "=";
  if (!any) { tell(au, pre + "Nothing is owed to that player now."); return; }
  String what = n > 0 ? n + " stack(s)" : "what trades owe them (coins)";
  @PR@ tp = @ES@.online(tu);
  if (tp != null) {
    deliverNow2(tu, true);
    tell(au, pre + "Returning " + what + " to " + tp.getUsername() + " now (what does not fit waits for their /trade claim).");
  } else {
    tell(au, pre + "That player is offline - " + what + " come back at their next join.");
  }
}""")
M(tst, r"""
public static void adminReturn(@PR@ pr, String whoText) {
  java.util.UUID tu = resolve(whoText);
  if (tu == null) { tellPr(pr, "-No player found for " + whoText + " - use an online name, a name seen before or a UUID."); return; }
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { adminReturnNow(pr.getUuid(), pr.getUsername(), tu); return; }
  @PKG@.TJob j = new @PKG@.TJob(7, (@PKG@.TRecord) null, (@PKG@.TSession) null, (String) null, -1, pr.getUsername());
  j.u1 = tu;
  j.u2 = pr.getUuid();
  try { ex.execute(j); } catch (Throwable t) { adminReturnNow(pr.getUuid(), pr.getUsername(), tu); }
}""")
# 0.1.3: settings changes go through the config kit (memory at once, the file ~500 ms later on the kit's scheduler), so the trade thread
# hand-off of 0.1.2 is gone. After "Reload file" the kit runs TCfg.reloadKit on its scheduler once the file is written: ONE delayed
# rebuild of the page (TTask 8 -> cfgResultTask, in reaction to the admin's click - never periodic) shows the re-read values.
M(tst, r"""
public static void laterRefresh(@PKG@.TCfgPage page, java.util.UUID au, String res) {
  try {
    @PKG@.TTask t = new @PKG@.TTask(8, (@PKG@.TSession) null, -1, au, res);
    t.obj = page;
    t.val = null;
    @HSV@.SCHEDULED_EXECUTOR.schedule(t, 1200L, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { }
}""")
# the kit's reload op (hand edits of config.properties: logged via=file, applied by TCfg.reloadKit); trade = the /tradeadmin path
# (skyyessentials.tradeadmin accepted for this one call, EssPerm). Returns a "+/-" line.
M(tst, r"""
public static String kitReload(java.util.UUID au, String who, boolean trade) {
  Object o = null;
  try {
    if (trade) @PKG@.EssPerm.tradeOn();
    o = new @PKG@.CfgFn().apply(new Object[] { "reload", au, who, "command" });
  } catch (Throwable t) {
    o = null;
  } finally {
    if (trade) @PKG@.EssPerm.tradeOff();
  }
  if (o instanceof Object[] && ((Object[]) o).length > 2) {
    Object[] r = (Object[]) o;
    String st = String.valueOf(r[0]);
    String m = r[2] == null ? "" : String.valueOf(r[2]);
    return (st.equals("ok") ? "+" : "-") + m;
  }
  return "-Could not re-read config.properties - see the server log.";
}""")
M(tst, r"""
public static void adminReload(@PR@ pr) {
  tellPr(pr, kitReload(pr.getUuid(), pr.getUsername(), true));
}""")
M(tst, r"""
public static void adminConfig(@PR@ pr, @REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) { tellPr(pr, "-You are not in a world right now."); return; }
  p.getPageManager().openCustomPage(ref, st, new @PKG@.TCfgPage(pr, 0));
}""")
M(tst, r"""
public static void adminHelp(@PR@ pr) {
  tellPr(pr, "=/tradeadmin log [player] - recent trade log lines (optionally only that player's)");
  tellPr(pr, "=/tradeadmin return <player> - cancel their open trade and give back everything a trade owes them");
  tellPr(pr, "=/tradeadmin config - the trade settings page (writes config.properties)");
  tellPr(pr, "=/tradeadmin reload - re-read config.properties after a hand edit");
}""")
# ---- bridge function, listeners
M(tst, r"""
public static Object cancelApi(Object o) {
  try {
    if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) o;
    @PKG@.TSession s = current(u);
    if (s == null) return Boolean.FALSE;
    cancelAsync(s, "api", s.side(u), (String) null);
    return Boolean.TRUE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
M(tst, r"""
public static void onReady(@PR@ pr) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  noteName(u, pr.getUsername());
  if (hasOwed(u)) due(u, System.currentTimeMillis() + 1500L);
}""")
M(tst, r"""
public static void onQuit(@PR@ pr) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  java.util.List waiting = dropReqOf(u);
  for (int i = 0; i < waiting.size(); i++) {
    @PKG@.TpReq r = (@PKG@.TpReq) waiting.get(i);
    tell(r.from, "=" + pr.getUsername() + " left the game - your trade request to them was dropped.");
  }
  DUE.remove(u);
  @PKG@.TSession s = current(u);
  if (s != null) cancelAsync(s, "disconnect", s.side(u), pr.getUsername());
}""")
# ---- the 1 s ticker (trade thread): profile gate bookkeeping, open trades (online, profile, damage, world, distance), requests,
# due deliveries, unsaved / finished records
M(tst, r"""
public static int mover(@PKG@.TSession s) {
  double a = (s.px[0] - s.sx[0]) * (s.px[0] - s.sx[0]) + (s.py[0] - s.sy[0]) * (s.py[0] - s.sy[0]) + (s.pz[0] - s.sz[0]) * (s.pz[0] - s.sz[0]);
  double b = (s.px[1] - s.sx[1]) * (s.px[1] - s.sx[1]) + (s.py[1] - s.sy[1]) * (s.py[1] - s.sy[1]) + (s.pz[1] - s.sz[1]) * (s.pz[1] - s.sz[1]);
  return a >= b ? 0 : 1;
}""")
M(tst, r"""
public static void tickSession(@PKG@.TSession s, long now) {
  if (!s.live()) {
    if (s.closed) { SESSIONS.remove(s.u[0], s); SESSIONS.remove(s.u[1], s); }
    return;
  }
  java.util.Map br = @PKG@.TCfg.bridge();
  for (int i = 0; i < 2; i++) {
    if (@ES@.online(s.u[i]) == null) {
      s.offline[i] = s.offline[i] + 1;
      if (s.offline[i] >= 3) { cancelNow(s, "disconnect", i, s.name[i]); return; }
      continue;
    }
    s.offline[i] = 0;
    if (br.get("profile:busy:" + s.u[i]) != null) { cancelNow(s, "profile", i, s.name[i]); return; }
    Object ep = br.get("profile:epoch:" + s.u[i]);
    if (ep != null) {
      if (s.epoch[i] == null) s.epoch[i] = ep;
      else if (!ep.equals(s.epoch[i])) { cancelNow(s, "profile", i, s.name[i]); return; }
    }
    if (!@PKG@.TCfg.DAMAGE) s.hurt[i] = false;
    else if (s.hurt[i]) { cancelNow(s, "damage", i, s.name[i]); return; }
  }
  if (s.hasPos[0] && s.hasPos[1] && now - s.posAt[0] < 3500L && now - s.posAt[1] < 3500L && s.wu[0] != null && s.wu[1] != null) {
    if (!s.wu[0].equals(s.wu[1])) {
      if (@PKG@.TCfg.SAME_WORLD) {
        int m = (s.sw[1] != null && !s.wu[1].equals(s.sw[1])) ? 1 : 0;
        cancelNow(s, "world", m, s.name[m]);
        return;
      }
    } else if (@PKG@.TCfg.DIST > 0) {
      double dx = s.px[0] - s.px[1];
      double dy = s.py[0] - s.py[1];
      double dz = s.pz[0] - s.pz[1];
      double lim = (double) @PKG@.TCfg.DIST;
      if (dx * dx + dy * dy + dz * dz > lim * lim) { int m = mover(s); cancelNow(s, "distance", m, s.name[m]); return; }
    }
  }
  for (int i = 0; i < 2; i++) {
    if (@ES@.online(s.u[i]) != null) hop(new @PKG@.TTask(3, s, i, s.u[i], (String) null));
  }
}""")
M(tst, r"""
public static void tick(int n) {
  long now = System.currentTimeMillis();
  @UNI@ un = null;
  try { un = @UNI@.get(); } catch (Throwable t) { un = null; }
  if (un != null) {
    try {
      java.util.Iterator it = un.getPlayers().iterator();
      while (it.hasNext()) {
        @PR@ p = (@PR@) it.next();
        if (p != null && p.isValid()) { noteBusy(p.getUuid()); noteEpoch(p.getUuid()); }
      }
    } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick-players", "trade tick (players) failed: " + t); }
  }
  try {
    long keep = (long) @PKG@.TCfg.AFTER_S * 1000L + 10000L;
    java.util.Iterator w = SWITCHED.entrySet().iterator();
    while (w.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) w.next();
      if (now - ((Long) e.getValue()).longValue() > keep) w.remove();
    }
  } catch (Throwable t) { }
  try {
    java.util.Iterator it = SESSIONS.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      @PKG@.TSession s = (@PKG@.TSession) e.getValue();
      if (s == null) continue;
      if (e.getKey().equals(s.u[1]) && SESSIONS.get(s.u[0]) == s) continue;
      try { tickSession(s, now); } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick-" + s.rec.id, "trade tick failed for " + s.rec.id + ": " + t); }
      if (s.live() && s.rec.rev != s.rec.writtenRev && now - s.rec.lastFail > 5000L && !PENDING.containsKey(s.rec.id)) saveSoon(s.rec, 0L);
    }
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick-sessions", "trade tick (sessions) failed: " + t); }
  if (n % 10 == 0) { try { pruneReq(); } catch (Throwable t) { } }
  try {
    java.util.Iterator it = DUE.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      Long at = (Long) e.getValue();
      if (at != null && at.longValue() > now) continue;
      java.util.UUID u = (java.util.UUID) e.getKey();
      it.remove();
      deliverNow(u);
    }
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick-due", "trade tick (deliveries) failed: " + t); }
  try {
    java.util.Iterator it = RECORDS.values().iterator();
    while (it.hasNext()) {
      @PKG@.TRecord r = (@PKG@.TRecord) it.next();
      if (r.rev != r.writtenRev) { if (now - r.lastFail > 5000L && !PENDING.containsKey(r.id)) saveSoon(r, 0L); }
      else if (r.done()) archive(r);
    }
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick-records", "trade tick (records) failed: " + t); }
  if (NAMES_DIRTY) saveNames();
}""")
M(tst, r"""
public static void dueOnline() {
  try {
    long now = System.currentTimeMillis();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid() && hasOwed(p.getUuid())) due(p.getUuid(), now);
    }
  } catch (Throwable t) { }
}""")
M(tst, r"""
public static void jobRun(@PKG@.TJob j) {
  try {
    if (j.kind == 1) saveJob(j.rec);
    else if (j.kind == 2) saveNames();
    else if (j.kind == 3) archive(j.rec);
    else if (j.kind == 4) cancelNow(j.sess, j.reason, j.by, j.byName);
    else if (j.kind == 5) lateSweep(j.sess);
    else if (j.kind == 6) dueOnline();
    else if (j.kind == 7) adminReturnNow(j.u2, j.byName, j.u1);
    else if (j.kind == 10) saveNowJob(j.rec);
  } catch (Throwable t) { @PKG@.TCfg.warn("trade job " + j.kind + " failed: " + t); }
}""")
M(tst, r"""
public static String start() {
  STOPPING = false;
  SAVER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.TThreads());
  loadNames();
  int n = loadAll();
  @PKG@.TCfg.bridge().put("trade:fn:cancel", new @PKG@.TCancelFn());
  TICK = SAVER.scheduleAtFixedRate(new @PKG@.TTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  SAVER.schedule(new @PKG@.TJob(6, (@PKG@.TRecord) null, (@PKG@.TSession) null, (String) null, -1, (String) null), 5L, java.util.concurrent.TimeUnit.SECONDS);
  return n + " unsettled trade record(s)";
}""")
M(tst, r"""
public static void flushAll() {
  java.util.Iterator it = RECORDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.TRecord r = (@PKG@.TRecord) it.next();
    try { if (r.rev != r.writtenRev && !writeRec(r)) log("SHUTDOWN-WRITE-FAIL id=" + r.id); } catch (Throwable t) { }
  }
  if (NAMES_DIRTY) saveNames();
}""")
# normal stop: the trade thread is stopped first (no countdown can fire any more), then every open trade is cancelled with its record
# written right here - each player gets their offer back at their next join (deliveries are skipped while stopping)
M(tst, r"""
public static void stop() {
  try { if (TICK != null) TICK.cancel(false); } catch (Throwable t) { }
  STOPPING = true;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (ex != null) {
    try { ex.shutdownNow(); ex.awaitTermination(3L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
  }
  java.util.ArrayList live = new java.util.ArrayList();
  java.util.Iterator it = SESSIONS.values().iterator();
  while (it.hasNext()) { Object o = it.next(); if (o != null && !live.contains(o)) live.add(o); }
  for (int i = 0; i < live.size(); i++) {
    try { cancelNow((@PKG@.TSession) live.get(i), "server-stop", -1, (String) null); } catch (Throwable t) { @PKG@.TCfg.warn("could not settle an open trade at shutdown: " + t); }
  }
  flushAll();
  try { @PKG@.TCfg.bridge().remove("trade:fn:cancel"); } catch (Throwable t) { }
}""")

# ================= bodies that call TStore =================
M(tpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    if (a.equals("cancel")) { @PKG@.TStore.clickCancel(this); return; }
    if (a.equals("chest")) {
      String r = @PKG@.TStore.clickChest(this, ref, store);
      if (r != null) { this.info = r; rebuild(); }
      return;
    }
    if (a.equals("ready")) { this.keepCoin = null; this.info = @PKG@.TStore.clickReady(this); rebuild(); return; }
    if (a.equals("coinclear")) { this.keepCoin = null; this.info = @PKG@.TStore.clickCoins(this, "0"); rebuild(); return; }
    if (a.equals("coins")) {
      String typed = jsonStr(data, "@TrCoin");
      String r = @PKG@.TStore.clickCoins(this, typed);
      this.info = r;
      this.keepCoin = r.startsWith("-") ? typed : null;
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.TCfg.warn("trade page click failed: " + t); }
}""")
M(tpage, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try { @PKG@.TStore.pageDismissed(this); } catch (Throwable t) { }
}""")
# =====================================================================================================================================
# 0.1.3 warps editor + world spawn (research/Server-Setup-Spec.md 5.4). Engine calls copied from vanilla (bytecode, tools/dev/bcfull.py):
#   WarpSetCommand.execute: TransformComponent + HeadRotation -> new Transform(new Vector3d(pos), new Rotation3f(rot)) ->
#     new Warp(transform, name, world, username, Instant.now()) -> TeleportPlugin.get().addWarp(warp, true). addWarp(w, true) = put (a
#     replaced warp's marker entity is removed first), createWarpEntity for a new one, then saveWarps(); addWarp(w, false) = putIfAbsent
#     (false when the id is taken). Before replacing an existing warp (no --force) it dispatches ReplaceWarpEvent(existing) and stops
#     when a listener cancels it. Reserved names = WarpCommand's sub-command names (go, list, remove, reload, set).
#   WarpRemoveCommand.executeSync: RemoveWarpEvent(existing) (same cancel rule) -> removeWarp(id) (removes the marker entity, saves).
#   WarpCommand.tryGo: Universe.getWorld(warp.getWorld()) + warp.toTeleport() (null when the world is not loaded) -> TeleportHistory
#     append -> addComponent(Teleport). Here the history comes first and the page is closed before the Teleport (0.1.1 order: a
#     cross-world Teleport removes the entity inside addComponent).
#   SpawnSetCommand: WorldConfig.setSpawnProvider(new GlobalSpawnProvider(new Transform(pos, rot))) + markChanged(); SpawnSetDefaultCommand:
#     setSpawnProvider(null) (no markChanged - we add it so the reset is saved too; getSpawnProvider() then answers the default provider).
# Warp edits and spawn changes made on the /warpadmin page are written to config-changes.log with the kit's line format, via=command,
# status "done" (the SkyyRanks pattern), so SkyyMenu's Changes view lists them without an Undo it cannot do. A spawn change from the
# kit's action rows (SkyyMenu Server Setup) is NOT logged again when it works: the kit already wrote its own "done" line for that click
# (CfgFn.opAction, via=menu) - the details (world, x y z) go to the server log instead. When the scheduled change does NOT happen (the
# admin left, changed worlds, the world closed, an instance world), a follow-up line with status "failed" says so, so the kit's "done"
# line never stands alone for a change that never happened (review fix 2026-09-25).
# =====================================================================================================================================
wpage = pool.makeClass(PKG + ".WarpPage", pool.get(T["PAGE"]))
spt = pool.makeClass(PKG + ".SpawnTask")
spt.addInterface(pool.get("java.lang.Runnable"))
for c, m in ((AC, "getSubCommands"), (CMG, "resolveCommand"), (T["IWC"], "get")):
    B.probe(pool, c, m)
M(EWARP, r"""
public static void auditVia(java.util.UUID who, String name, String via, String key, String old, String nw) {
  try { @PKG@.CfgLog.add(who, name, via, key, old, nw, "done"); @PKG@.CfgFile.bump(); @PKG@.CfgFile.logSoon(); } catch (Throwable t) { }
}""")
M(EWARP, r"""
public static void audit(java.util.UUID who, String name, String key, String old, String nw) { auditVia(who, name, "command", key, old, nw); }""")
# the follow-up line for a Server Setup spawn action whose scheduled change did not happen. via = "menu": the kit hands an action hook
# only (who, name), never the caller's via; the kit's own default via for an action is "menu" and SkyyMenu Server Setup is the only
# caller of these rows (a console caller never gets this far: kitSpawn refuses who = null). No epoch bump: nothing changed.
M(EWARP, r"""
public static void failed(java.util.UUID who, String name, String key, String why) {
  try { @PKG@.CfgLog.add(who, name, "menu", key, "(action)", "not done - " + why, "failed"); @PKG@.CfgFile.logSoon(); } catch (Throwable t) { }
}""")
M(EWARP, r"""
public static @TPP@ tp() {
  try {
    @TPP@ p = @TPP@.get();
    if (p != null && p.isWarpsLoaded()) return p;
  } catch (Throwable t) { }
  return null;
}""")
M(EWARP, r"""
public static @WARP@ find(String id) {
  @TPP@ p = tp();
  if (p == null || id == null) return null;
  try {
    Object o = p.getWarps().get(id.toLowerCase(java.util.Locale.ROOT));
    if (o instanceof @WARP@) return (@WARP@) o;
  } catch (Throwable t) { }
  return null;
}""")
# every warp id, sorted A-Z (ignoring case); the map is read on the admin's world thread like vanilla /warp list
M(EWARP, r"""
public static String[] ids() {
  @TPP@ p = tp();
  if (p == null) return new String[0];
  java.util.ArrayList l = new java.util.ArrayList();
  try {
    java.util.Iterator it = new java.util.ArrayList(p.getWarps().values()).iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @WARP@ && ((@WARP@) o).getId() != null) l.add(((@WARP@) o).getId());
    }
  } catch (Throwable t) { @PKG@.TCfg.warnOnce("warps", "could not list the warps: " + t); }
  String[] a = (String[]) l.toArray(new String[0]);
  java.util.Arrays.sort(a, String.CASE_INSENSITIVE_ORDER);
  return a;
}""")
M(EWARP, r"""
public static String coords(@TRF@ t) {
  if (t == null || t.getPosition() == null) return "?";
  @VEC@ p = t.getPosition();
  return (long) Math.floor(p.x) + " " + (long) Math.floor(p.y) + " " + (long) Math.floor(p.z);
}""")
# where the player stands (WarpSetCommand / SpawnSetCommand read the same two components); null = unreadable. World thread only.
M(EWARP, r"""
public static @TRF@ here(@ST@ st, @REF@ ref) {
  try {
    if (ref == null || !ref.isValid()) return null;
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
    if (tc == null || tc.getPosition() == null) return null;
    @VEC@ p = tc.getPosition();
    @R3F@ r = hr != null ? hr.getRotation() : null;
    return new @TRF@(new @VEC@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@());
  } catch (Throwable t) { return null; }
}""")
M(EWARP, r"""
public static boolean reserved(String lower) {
  if (lower.equals("go") || lower.equals("list") || lower.equals("remove") || lower.equals("reload") || lower.equals("set")) return true;
  try {
    Object w = @CMG@.get().resolveCommand("warp");
    if (w != null) {
      java.util.Map m = ((com.hypixel.hytale.server.core.command.system.AbstractCommand) w).getSubCommands();
      if (m != null && m.containsKey(lower)) return true;
    }
  } catch (Throwable t) { }
  return false;
}""")
M(EWARP, r"""
public static String nameErr(String raw) {
  if (raw == null || raw.trim().length() == 0) return "Type a warp name in the box first.";
  String s = raw.trim();
  if (s.length() > 32) return "A warp name can have at most 32 characters.";
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.';
    if (!ok) return "Use only letters, digits and _ - . in a warp name (no spaces).";
  }
  if (reserved(s.toLowerCase(java.util.Locale.ROOT))) return s + " is a /warp command word - pick another name.";
  return null;
}""")
# vanilla WarpSetCommand.cancel / WarpRemoveCommand.cancel: null = go on; else why a listener stopped it (its reason goes to chat)
M(EWARP, r"""
public static String cancelled(@WARP@ w, boolean remove, @PR@ pr) {
  try {
    @IED@ d = null;
    if (remove) d = @HSV@.get().getEventBus().dispatchFor(@RMWE@.class, (Object) null);
    else d = @HSV@.get().getEventBus().dispatchFor(@RPWE@.class, (Object) null);
    if (d == null || !d.hasListener()) return null;
    Object r = null;
    if (remove) r = d.dispatch(new @RMWE@(w));
    else r = d.dispatch(new @RPWE@(w));
    if (r instanceof @MWE@ && ((@MWE@) r).isCancelled()) {
      com.hypixel.hytale.server.core.Message m = ((@MWE@) r).getCancelReason();
      if (m != null && pr != null) pr.sendMessage(m);
      return "Another mod stopped that change" + (m != null ? " (its reason is in your chat)." : ".");
    }
  } catch (Throwable t) { @PKG@.TCfg.warn("warp event check failed: " + t); }
  return null;
}""")
M(EWARP, r"""
public static String wname(@WLD@ w) {
  try { if (w != null && w.getName() != null) return w.getName(); } catch (Throwable t) { }
  return "?";
}""")
# ---- the warp operations (the admin's world thread: page clicks). "+" done, "-" refused, "=" nothing to do
M(EWARP, r"""
public static String add(@PR@ pr, @ST@ st, @REF@ ref, String raw) {
  @TPP@ p = tp();
  if (p == null) return "-Warps are still loading - try again in a moment.";
  String err = nameErr(raw);
  if (err != null) return "-" + err;
  String name = raw.trim();
  if (find(name) != null) return "-A warp named " + name + " already exists - use Move here on its row to move it.";
  @WLD@ w = @ES@.worldOf(pr);
  if (w == null) return "-You are not in a world right now.";
  @TRF@ t = here(st, ref);
  if (t == null) return "-Could not read where you stand - try again.";
  @WARP@ wp = new @WARP@(t, name, w, pr.getUsername(), java.time.Instant.now());
  if (!p.addWarp(wp, false)) return "-A warp named " + name + " already exists.";
  audit(pr.getUuid(), pr.getUsername(), "warp[" + name + "]", "(none)", wname(w) + " " + coords(t));
  return "+Warp " + name + " added where you stand (" + wname(w) + " " + coords(t) + ").";
}""")
M(EWARP, r"""
public static String move(@PR@ pr, @ST@ st, @REF@ ref, String id) {
  @TPP@ p = tp();
  if (p == null) return "-Warps are still loading - try again in a moment.";
  @WARP@ old = find(id);
  if (old == null) return "-The warp " + id + " is gone - click Refresh.";
  @WLD@ w = @ES@.worldOf(pr);
  if (w == null) return "-You are not in a world right now.";
  @TRF@ t = here(st, ref);
  if (t == null) return "-Could not read where you stand - try again.";
  String c = cancelled(old, false, pr);
  if (c != null) return "-" + c;
  String creator = old.getCreator();
  if (creator == null) creator = pr.getUsername();
  java.time.Instant made = old.getCreationDate();
  if (made == null) made = java.time.Instant.now();
  String was = old.getWorld() + " " + coords(old.getTransform());
  p.addWarp(new @WARP@(t, old.getId(), w, creator, made), true);
  audit(pr.getUuid(), pr.getUsername(), "warp[" + old.getId() + "]", was, wname(w) + " " + coords(t));
  return "+Warp " + old.getId() + " moved to where you stand (" + wname(w) + " " + coords(t) + ").";
}""")
M(EWARP, r"""
public static String rename(@PR@ pr, String id, String raw) {
  @TPP@ p = tp();
  if (p == null) return "-Warps are still loading - try again in a moment.";
  @WARP@ old = find(id);
  if (old == null) return "-The warp " + id + " is gone - click Refresh.";
  String err = nameErr(raw);
  if (err != null) return "-" + err + " (Rename uses the name in the box.)";
  String nn = raw.trim();
  if (nn.equals(old.getId())) return "=The warp is already called " + nn + ".";
  boolean same = nn.toLowerCase(java.util.Locale.ROOT).equals(old.getId().toLowerCase(java.util.Locale.ROOT));
  if (!same && find(nn) != null) return "-A warp named " + nn + " already exists.";
  @WLD@ w = @UNI@.get().getWorld(old.getWorld());
  if (w == null) return "-The world of " + old.getId() + " (" + old.getWorld() + ") is not loaded - rename it when that world is loaded.";
  String c = cancelled(old, true, pr);
  if (c != null) return "-" + c;
  String creator = old.getCreator();
  if (creator == null) creator = pr.getUsername();
  java.time.Instant made = old.getCreationDate();
  if (made == null) made = java.time.Instant.now();
  @WARP@ nw = new @WARP@(new @TRF@(old.getTransform()), nn, w, creator, made);
  if (same) p.addWarp(nw, true);
  else {
    if (!p.addWarp(nw, false)) return "-A warp named " + nn + " already exists.";
    p.removeWarp(old.getId());
  }
  audit(pr.getUuid(), pr.getUsername(), "warp[" + old.getId() + "]", old.getId(), nn);
  return "+Warp " + old.getId() + " is now called " + nn + ".";
}""")
M(EWARP, r"""
public static String remove(@PR@ pr, String id) {
  @TPP@ p = tp();
  if (p == null) return "-Warps are still loading - try again in a moment.";
  @WARP@ old = find(id);
  if (old == null) return "-The warp " + id + " is gone already.";
  String c = cancelled(old, true, pr);
  if (c != null) return "-" + c;
  String was = old.getWorld() + " " + coords(old.getTransform());
  if (!p.removeWarp(old.getId())) return "-The warp " + id + " is gone already.";
  audit(pr.getUuid(), pr.getUsername(), "warp[" + old.getId() + "]", was, "(none)");
  return "+Warp " + old.getId() + " removed.";
}""")
# ---- world spawn (the world thread of w). Instance worlds (SkyyIslands islands, portal worlds) keep their own spawn: refused.
# instanceErr is a plain read of the world's config (InstanceWorldConfig.get = WorldConfig.getPluginConfig().get(class), bytecode), so
# kitSpawn may also ask it on the caller's thread before anything is scheduled
M(EWARP, r"""
public static String instanceErr(@WLD@ w) {
  try {
    @WCF@ c = w.getWorldConfig();
    if (c != null && @IWC@.get(c) != null) return wname(w) + " is an instance world (an island or a portal world) - it keeps its own spawn. Stand in a normal world.";
  } catch (Throwable t) { }
  return null;
}""")
# via = the change-log origin of a /warpadmin page click ("command"); null = a Server Setup action (SpawnTask): the kit logged that
# click already, so a change that works only gets a server log line with the details (review fix: no second, mislabelled line).
# A world that is closing is refused like kitSpawn refuses it (review fix: both call sites answer the same, nothing touches a dying world)
M(EWARP, r"""
public static String spawnSet(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, boolean reset, String via) {
  if (w == null || !w.isAlive()) return "-You are not in a world right now - try again in a moment.";
  @WCF@ c = w.getWorldConfig();
  if (c == null) return "-This world has no config to change.";
  String ie = instanceErr(w);
  if (ie != null) return "-" + ie;
  String key = "spawn.set";
  String nw = "(original spawn)";
  if (reset) {
    key = "spawn.reset";
    c.setSpawnProvider((@ISP@) null);
  } else {
    @TRF@ t = here(st, ref);
    if (t == null) return "-Could not read where you stand - try again.";
    c.setSpawnProvider(new @GSP@(t));
    nw = coords(t);
  }
  c.markChanged();
  if (via != null) auditVia(pr.getUuid(), pr.getUsername(), via, key, wname(w), nw);
  else @PKG@.TCfg.info("world spawn " + key + ": " + wname(w) + " -> " + nw + " by " + pr.getUsername() + " (SkyWynn Menu Server Setup; config-changes.log has the kit's line)");
  if (reset) return "+The spawn of world " + wname(w) + " is back to its original spawn point.";
  return "+The spawn of world " + wname(w) + " is now where you stand (" + nw + "). New and respawning players arrive here.";
}""")
# SkyyMenu Server Setup action rows (spawn.set / spawn.reset): scheduled on the admin's own world (contract guarantee 3), answer in chat.
# Every way the scheduled change can end without happening writes the "failed" follow-up line (EssWarp.failed).
for f in ("public java.util.UUID who;", "public String name;", "public boolean reset;", "public @WLD@ w;"):
    F(spt, f)
C(spt, "public SpawnTask(java.util.UUID who, String name, boolean reset, @WLD@ w) { this.who = who; this.name = name; this.reset = reset; this.w = w; }")
M(spt, r"""
public void fail(String why) { @PKG@.EssWarp.failed(this.who, this.name, this.reset ? "spawn.reset" : "spawn.set", why); }""")
M(spt, r"""
public void run() {
  try {
    @PR@ pr = @ES@.online(this.who);
    if (pr == null) { fail("the admin left before it ran"); return; }
    @WLD@ here = @ES@.worldOf(pr);
    if (here != this.w) { fail("the admin changed worlds first"); @ES@.say(pr, "[Spawn] You changed worlds - nothing was changed. Try again.", @ES@.ERR); return; }
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) { fail("could not read where the admin stood"); @ES@.say(pr, "[Spawn] Could not read where you stand - nothing was changed.", @ES@.ERR); return; }
    String r = @PKG@.EssWarp.spawnSet(pr, ref.getStore(), ref, here, this.reset, (String) null);
    if (!r.startsWith("+")) fail(@PKG@.TradePage.textOf(r));
    @ES@.say(pr, "[Spawn] " + @PKG@.TradePage.textOf(r), r.startsWith("+") ? @ES@.OK : @ES@.ERR);
  } catch (Throwable t) {
    fail("an error - see the server log");
    @ES@.warn("world spawn change failed: " + t);
  }
}""")
# the kit logs "done" as soon as this answers ok, so everything that can be refused here is refused BEFORE scheduling (instance world
# included); only what can change between now and the world's tick is left to SpawnTask (and its "failed" line)
M(EWARP, r"""
public static Object[] kitSpawn(java.util.UUID who, String name, boolean reset) {
  @PR@ pr = @ES@.online(who);
  if (pr == null) return new Object[] { "bad", null, "Only a player in game can do this: it changes the world they stand in." };
  @WLD@ w = @ES@.worldOf(pr);
  if (w == null || !w.isAlive()) return new Object[] { "bad", null, "You are not in a world right now - try again in a moment." };
  String ie = instanceErr(w);
  if (ie != null) return new Object[] { "bad", null, ie };
  try { w.execute(new @PKG@.SpawnTask(who, name, reset, w)); }
  catch (Throwable t) { return new Object[] { "error", null, "Could not reach your world - see the server log." }; }
  return new Object[] { "ok", "", "Working on it in world " + wname(w) + " - the result comes in your chat." };
}""")
M(EWARP, r"""public static Object[] kitSpawnSet(java.util.UUID who, String name) { return kitSpawn(who, name, false); }""")
M(EWARP, r"""public static Object[] kitSpawnReset(java.util.UUID who, String name) { return kitSpawn(who, name, true); }""")

# ---- WarpPage: /warpadmin (and the kit's warps.editor link row). BIG inline page, 1120 x 930 (28 + 3 + 46 + 28 + 30 + 9 x 50 + 6 + 44 +
# 50 + 50 + 24 + 24 + 32 + 52 = 867 used). Rebuilt only after the admin's own click (never on a timer). guard() first in build + clicks.
WP_ROWS = 9
for f in ("public String info;", "public int pg;", "public String[] ids;", "public String keepName;", "public String cKind;", "public String cId;"):
    F(wpage, f)
C(wpage, r"""
public WarpPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.info = ""; this.pg = 0; this.ids = new String[%d]; this.keepName = null; this.cKind = null; this.cId = null;
}""" % WP_ROWS)
M(wpage, r"""
public boolean guard() {
  try { return this.playerRef.hasPermission(@PKG@.TCfg.EADMIN); } catch (Throwable t) { return false; }
}""")
M(wpage, r"""
public static String lbl(String id, int w, int fs, String col) {
  return "Label " + id + " { Anchor: (Width: " + w + ", Height: 44); Text: \"\"; Style: (FontSize: " + fs + ", TextColor: " + col + ", VerticalAlignment: Center); }";
}""")
M(wpage, r"""
public static String btn(String id, int w, int h, String text, String style) {
  return "TextButton " + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"" + text + "\"; " + style + " }";
}""")
M(wpage, r"""
public static String gap(int w, int h) { return "Label { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; }"; }""")
M(wpage, r"""
public String question() {
  String wn = @PKG@.EssWarp.wname(@ES@.worldOf(this.playerRef));
  if ("rm".equals(this.cKind)) return "Remove the warp " + this.cId + "? Nobody can warp there any more (the vanilla /warp list loses it too).";
  if ("spset".equals(this.cKind)) return "Move the spawn of world " + wn + " to where you stand? New and respawning players arrive here.";
  if ("spreset".equals(this.cKind)) return "Put the spawn of world " + wn + " back to its original spawn point?";
  return "";
}""")
M(wpage, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  String bs = @PKG@.TradePage.style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 17);
  String gs = @PKG@.TradePage.style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 17);
  String rs = @PKG@.TradePage.style("#6a2020", "#8f2f2f", "#3a1010", "#ffe6e6", 17);
  String ys = @PKG@.TradePage.style("#6a4a12", "#8a641a", "#3e2a08", "#fff2d6", 17);
  if (!guard()) {
    b.appendInline((String) null, "Group #SkyyWp { Anchor: (Width: 900, Height: 250); Background: #0b1524(0.97); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
    b.appendInline("#SkyyWp", "Label #SkyyWpNo { Anchor: (Height: 120); Text: \"\"; Style: (FontSize: 22, RenderBold: true, TextColor: #ff9d6b, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyWpNo.Text", "You do not have permission to edit warps (skyyessentials.admin).");
    b.appendInline("#SkyyWp", "Group #SkyyWpFoot { Anchor: (Height: 56); LayoutMode: Left; }");
    b.appendInline("#SkyyWpFoot", gap(351, 52));
    b.appendInline("#SkyyWpFoot", btn("#SkyyWpClose", 150, 52, "Close", bs));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpClose", @EVD@.of("a", "close"));
    return;
  }
  if (this.cKind != null) {
    b.appendInline((String) null, "Group #SkyyWp { Anchor: (Width: 1000, Height: 330); Background: #0b1524(0.97); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
    b.appendInline("#SkyyWp", "Group { Anchor: (Height: 3); Background: #ff9d6b; }");
    b.appendInline("#SkyyWp", "Label { Anchor: (Height: 50); Text: \"Please confirm\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffd9c4, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.appendInline("#SkyyWp", "Label #SkyyWpQ { Anchor: (Height: 120); Text: \"\"; Style: (FontSize: 21, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
    b.set("#SkyyWpQ.Text", question());
    b.appendInline("#SkyyWp", "Group #SkyyWpCf { Anchor: (Height: 60); LayoutMode: Left; }");
    b.appendInline("#SkyyWpCf", gap(236, 56));
    b.appendInline("#SkyyWpCf", btn("#SkyyWpYes", 220, 56, "Confirm", rs));
    b.appendInline("#SkyyWpCf", gap(20, 56));
    b.appendInline("#SkyyWpCf", btn("#SkyyWpNoBtn", 220, 56, "Cancel", bs));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpYes", @EVD@.of("a", "yes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpNoBtn", @EVD@.of("a", "no"));
    return;
  }
  boolean loaded = @PKG@.EssWarp.tp() != null;
  String[] all = @PKG@.EssWarp.ids();
  int per = this.ids.length;
  int pages = (all.length + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pg >= pages) this.pg = pages - 1;
  if (this.pg < 0) this.pg = 0;
  String wn = @PKG@.EssWarp.wname(@ES@.worldOf(this.playerRef));
  b.appendInline((String) null, "Group #SkyyWp { Anchor: (Width: 1120, Height: 930); Background: #0b1524(0.97); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyWp", "Group { Anchor: (Height: 3); Background: #7fb2ff; }");
  b.appendInline("#SkyyWp", "Label { Anchor: (Height: 46); Text: \"Warps and world spawn\"; Style: (FontSize: 30, RenderBold: true, TextColor: #dbe9ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyWp", "Label #SkyyWpSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyWpSub.Text", (loaded ? all.length + (all.length == 1 ? " warp" : " warps") : "Warps are still loading") + " - you are in world " + wn + " - page " + (this.pg + 1) + " of " + pages);
  b.appendInline("#SkyyWp", "Group #SkyyWpHead { Anchor: (Height: 30); LayoutMode: Left; }");
  b.appendInline("#SkyyWpHead", "Label { Anchor: (Width: 180, Height: 30); Text: \"Warp\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyWpHead", "Label { Anchor: (Width: 170, Height: 30); Text: \"World\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyWpHead", "Label { Anchor: (Width: 180, Height: 30); Text: \"Position (x y z)\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.appendInline("#SkyyWpHead", "Label { Anchor: (Width: 140, Height: 30); Text: \"Made by\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  for (int r = 0; r < per; r++) {
    int k = this.pg * per + r;
    this.ids[r] = null;
    String row = "#SkyyWpRow" + r;
    b.appendInline("#SkyyWp", "Group " + row + " { Anchor: (Height: 50); LayoutMode: Left; }");
    if (k >= all.length) continue;
    @WARP@ w = @PKG@.EssWarp.find(all[k]);
    if (w == null) continue;
    this.ids[r] = w.getId();
    b.appendInline(row, lbl("#SkyyWpN" + r, 180, 18, "#ffffff"));
    b.set("#SkyyWpN" + r + ".Text", w.getId());
    b.appendInline(row, lbl("#SkyyWpW" + r, 170, 16, "#cfe3ff"));
    b.set("#SkyyWpW" + r + ".Text", w.getWorld() == null ? "?" : w.getWorld());
    b.appendInline(row, lbl("#SkyyWpP" + r, 180, 16, "#ffd37a"));
    b.set("#SkyyWpP" + r + ".Text", @PKG@.EssWarp.coords(w.getTransform()));
    b.appendInline(row, lbl("#SkyyWpC" + r, 140, 15, "#9aa8bd"));
    b.set("#SkyyWpC" + r + ".Text", w.getCreator() == null ? "?" : w.getCreator());
    b.appendInline(row, btn("#SkyyWpGo" + r, 70, 42, "Go", gs));
    b.appendInline(row, gap(6, 42));
    b.appendInline(row, btn("#SkyyWpMv" + r, 110, 42, "Move here", bs));
    b.appendInline(row, gap(6, 42));
    b.appendInline(row, btn("#SkyyWpRn" + r, 90, 42, "Rename", bs));
    b.appendInline(row, gap(6, 42));
    b.appendInline(row, btn("#SkyyWpRm" + r, 90, 42, "Remove", rs));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpGo" + r, @EVD@.of("a", "go:" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpMv" + r, @EVD@.of("a", "mv:" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpRn" + r, @EVD@.of("a", "rn:" + r).append("@WpName", "#SkyyWpName.Value"));
    ev.addEventBinding(@BT@.Activating, "#SkyyWpRm" + r, @EVD@.of("a", "rm:" + r));
  }
  if (loaded && all.length == 0) b.set("#SkyyWpSub.Text", "No warps yet - type a name below and click Add warp here. You are in world " + wn + ".");
  b.appendInline("#SkyyWp", gap(10, 6));
  b.appendInline("#SkyyWp", "Group #SkyyWpPages { Anchor: (Height: 44); LayoutMode: Left; }");
  b.appendInline("#SkyyWpPages", gap(316, 40));
  b.appendInline("#SkyyWpPages", btn("#SkyyWpPrev", 140, 40, "Prev", this.pg > 0 ? bs : @PKG@.TradePage.style("#262f3d", "#303b4c", "#1a212c", "#7f8ea6", 17)));
  b.appendInline("#SkyyWpPages", "Label #SkyyWpPg { Anchor: (Width: 160, Height: 40); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyWpPg.Text", "Page " + (this.pg + 1) + " of " + pages);
  b.appendInline("#SkyyWpPages", btn("#SkyyWpNext", 140, 40, "Next", this.pg + 1 < pages ? bs : @PKG@.TradePage.style("#262f3d", "#303b4c", "#1a212c", "#7f8ea6", 17)));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpNext", @EVD@.of("a", "next"));
  b.appendInline("#SkyyWp", "Group #SkyyWpAddRow { Anchor: (Height: 50); LayoutMode: Left; }");
  b.appendInline("#SkyyWpAddRow", "Label { Anchor: (Width: 150, Height: 44); Text: \"Warp name:\"; Style: (FontSize: 18, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyWpAddRow", "Group #SkyyWpNameBox { Anchor: (Width: 280, Height: 42); Background: #16263a; }");
  b.appendInline("#SkyyWpNameBox", "TextField #SkyyWpName { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 32; PlaceholderText: \"name (letters, digits)\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 17); }");
  if (this.keepName != null && this.keepName.length() > 0) b.set("#SkyyWpName.Value", this.keepName);
  b.appendInline("#SkyyWpAddRow", gap(12, 42));
  b.appendInline("#SkyyWpAddRow", btn("#SkyyWpAdd", 220, 42, "Add warp here", gs));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpAdd", @EVD@.of("a", "add").append("@WpName", "#SkyyWpName.Value"));
  b.appendInline("#SkyyWpAddRow", "Label #SkyyWpAddHint { Anchor: (Width: 400, Height: 44); Text: \"\"; Style: (FontSize: 15, TextColor: #9aa8bd, VerticalAlignment: Center); }");
  b.set("#SkyyWpAddHint.Text", "   Rename on a row also uses this name.");
  b.appendInline("#SkyyWp", "Group #SkyyWpSpawn { Anchor: (Height: 50); LayoutMode: Left; }");
  b.appendInline("#SkyyWpSpawn", "Label #SkyyWpSpLbl { Anchor: (Width: 330, Height: 44); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.set("#SkyyWpSpLbl.Text", "World spawn of " + wn + ":");
  b.appendInline("#SkyyWpSpawn", btn("#SkyyWpSpSet", 320, 42, "Set the world spawn here", ys));
  b.appendInline("#SkyyWpSpawn", gap(12, 42));
  b.appendInline("#SkyyWpSpawn", btn("#SkyyWpSpReset", 300, 42, "Reset to the original", bs));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpSpSet", @EVD@.of("a", "spset"));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpSpReset", @EVD@.of("a", "spreset"));
  b.appendInline("#SkyyWp", "Label #SkyyWpHelp0 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyWpHelp0.Text", "Go teleports you there. Move here puts the warp where you stand. Remove asks first. Players see the warps in SkyWynn Menu -> Teleport.");
  b.appendInline("#SkyyWp", "Label #SkyyWpHelp1 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyWpHelp1.Text", "The world spawn only changes the world you stand in (islands keep their own). Same as vanilla /spawn set.");
  b.appendInline("#SkyyWp", "Label #SkyyWpInfo { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + @PKG@.TradePage.colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyWpInfo.Text", @PKG@.TradePage.textOf(this.info));
  b.appendInline("#SkyyWp", "Group #SkyyWpFoot { Anchor: (Height: 52); LayoutMode: Left; }");
  b.appendInline("#SkyyWpFoot", gap(191, 48));
  b.appendInline("#SkyyWpFoot", btn("#SkyyWpSettings", 300, 48, "Teleport and message settings", bs));
  b.appendInline("#SkyyWpFoot", gap(20, 48));
  b.appendInline("#SkyyWpFoot", btn("#SkyyWpRefresh", 150, 48, "Refresh", bs));
  b.appendInline("#SkyyWpFoot", gap(20, 48));
  b.appendInline("#SkyyWpFoot", btn("#SkyyWpClose", 150, 48, "Close", bs));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpSettings", @EVD@.of("a", "settings"));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyWpClose", @EVD@.of("a", "close"));
}""")
# Go: WarpCommand.tryGo's calls; history first, the page closed before the Teleport (the ref is dead after a cross-world addComponent)
M(wpage, r"""
public String go(@REF@ ref, @ST@ st, String id) {
  @WARP@ w = @PKG@.EssWarp.find(id);
  if (w == null) return "-The warp " + id + " is gone - click Refresh.";
  @WLD@ target = @UNI@.get().getWorld(w.getWorld());
  @TPC@ t = w.toTeleport();
  if (target == null || t == null) return "-The world of warp " + id + " (" + w.getWorld() + ") is not loaded.";
  if (st.getComponent(ref, @TPC@.getComponentType()) != null) return "-You are already teleporting.";
  @WLD@ here = @ES@.worldOf(this.playerRef);
  try {
    @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
    if (here != null && mtc != null && mtc.getPosition() != null) {
      @VEC@ p = mtc.getPosition();
      @R3F@ r = mhr != null ? mhr.getRotation() : null;
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(here, new @VEC@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), "Warp '" + w.getId() + "'");
    }
  } catch (Throwable t2) { }
  close();
  try { st.addComponent(ref, @TPC@.getComponentType(), t); }
  catch (Throwable t3) {
    @ES@.warn("warp teleport failed: " + t3);
    @ES@.say(this.playerRef, "[Warps] Could not teleport you to " + w.getId() + " - the server log has the details.", @ES@.ERR);
    return null;
  }
  @ES@.say(this.playerRef, "[Warps] Teleporting to warp " + w.getId() + ".", @ES@.OK);
  return null;
}""")
M(wpage, r"""
public void openSettings(@REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  p.getPageManager().openCustomPage(ref, st, new @PKG@.TCfgPage(this.playerRef, 1));
}""")
M(wpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.TradePage.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    if (!guard()) { this.cKind = null; this.cId = null; this.info = "-You do not have permission to edit warps (skyyessentials.admin)."; rebuild(); return; }
    @PR@ pr = this.playerRef;
    String typed = @PKG@.TradePage.jsonStr(data, "@WpName");
    if (a.equals("no")) { this.cKind = null; this.cId = null; this.info = "=Nothing was changed."; rebuild(); return; }
    if (a.equals("yes")) {
      String k = this.cKind;
      String id = this.cId;
      this.cKind = null;
      this.cId = null;
      if ("rm".equals(k)) this.info = @PKG@.EssWarp.remove(pr, id);
      else if ("spset".equals(k)) this.info = @PKG@.EssWarp.spawnSet(pr, store, ref, @ES@.worldOf(pr), false, "command");
      else if ("spreset".equals(k)) this.info = @PKG@.EssWarp.spawnSet(pr, store, ref, @ES@.worldOf(pr), true, "command");
      rebuild();
      return;
    }
    if (a.equals("refresh")) { this.info = "=Refreshed."; rebuild(); return; }
    if (a.equals("prev")) { this.pg = this.pg - 1; rebuild(); return; }
    if (a.equals("next")) { this.pg = this.pg + 1; rebuild(); return; }
    if (a.equals("settings")) { openSettings(ref, store); return; }
    if (a.equals("add")) {
      String res = @PKG@.EssWarp.add(pr, store, ref, typed);
      this.info = res;
      this.keepName = res.startsWith("-") ? typed : null;
      rebuild();
      return;
    }
    if (a.equals("spset") || a.equals("spreset")) { this.cKind = a; this.cId = null; rebuild(); return; }
    int r = -1;
    try { r = Integer.parseInt(a.substring(a.indexOf(':') + 1)); } catch (Throwable t) { r = -1; }
    if (r < 0 || r >= this.ids.length || this.ids[r] == null) { this.info = "-That row changed - click Refresh."; rebuild(); return; }
    String id = this.ids[r];
    if (a.startsWith("go:")) { String e = go(ref, store, id); if (e != null) { this.info = e; rebuild(); } return; }
    if (a.startsWith("mv:")) { this.info = @PKG@.EssWarp.move(pr, store, ref, id); rebuild(); return; }
    if (a.startsWith("rn:")) {
      String res = @PKG@.EssWarp.rename(pr, id, typed);
      this.info = res;
      this.keepName = res.startsWith("-") ? typed : null;
      rebuild();
      return;
    }
    if (a.startsWith("rm:")) { this.cKind = "rm"; this.cId = id; rebuild(); return; }
  } catch (Throwable t) { @PKG@.TCfg.warn("warps page click failed: " + t); }
}""")
M(EWARP, r"""
public static void open(@PR@ pr, @REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) { @ES@.say(pr, "[Warps] You are not in a world right now.", @ES@.ERR); return; }
  p.getPageManager().openCustomPage(ref, st, new @PKG@.WarpPage(pr));
}""")

# /tradeadmin config and /warpadmin -> Settings clicks: guard first, then the kit (TCfgPage.apply); Reload file = the kit's reload op
M(tcpg, r"""
public void reload() {
  String res = @PKG@.TStore.kitReload(this.playerRef.getUuid(), this.playerRef.getUsername(), this.which == 0);
  this.info = res;
  if (res.startsWith("+")) @PKG@.TStore.laterRefresh(this, this.playerRef.getUuid(), res);
}""")
M(tcpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.TradePage.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    if (!guard()) { this.pendKey = null; this.pendVal = null; this.pendQ = null; this.info = "-You do not have permission to change these settings (" + node() + ")."; rebuild(); return; }
    if (a.equals("warps")) {
      @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
      if (p != null) p.getPageManager().openCustomPage(ref, store, new @PKG@.WarpPage(this.playerRef));
      return;
    }
    if (a.equals("cancel")) { this.pendKey = null; this.pendVal = null; this.pendQ = null; this.info = "=Nothing was changed."; rebuild(); return; }
    if (a.equals("confirm")) {
      String k = this.pendKey;
      String v = this.pendVal;
      this.pendKey = null; this.pendVal = null; this.pendQ = null;
      if (k != null) apply(k, v, "yes", -1);
      rebuild();
      return;
    }
    if (a.equals("reload")) { this.pendKey = null; this.pendVal = null; this.pendQ = null; reload(); rebuild(); return; }
    int r = -1;
    String val = null;
    boolean typed = false;
    try {
      if (a.startsWith("b1:") || a.startsWith("b0:")) {
        r = Integer.parseInt(a.substring(3));
        val = a.startsWith("b1:") ? "true" : "false";
      } else if (a.startsWith("c0:") || a.startsWith("c1:")) {
        r = Integer.parseInt(a.substring(3));
        int ci = a.charAt(1) - '0';
        int i = (r >= 0 && r < this.keys.length) ? @PKG@.CfgRows.index(this.keys[r]) : -1;
        if (i >= 0) { String[] cv = @PKG@.CfgRows.chVals(i); if (ci >= 0 && ci < cv.length) val = cv[ci]; }
      } else if (a.startsWith("set:")) {
        r = Integer.parseInt(a.substring(4));
        val = @PKG@.TradePage.jsonStr(data, "@TcV" + r);
        typed = true;
      }
    } catch (Throwable t) { r = -1; }
    if (r < 0 || r >= this.keys.length || val == null) return;
    this.pendKey = null; this.pendVal = null; this.pendQ = null;
    apply(this.keys[r], val, "", typed ? r : -1);
    rebuild();
  } catch (Throwable t) { @PKG@.TCfg.warn("settings page click failed: " + t); }
}""")
M(tchg, r"""
public void accept(Object ev) {
  try { @PKG@.TStore.onBoxChange(this.sess, this.side); } catch (Throwable t) { @PKG@.TCfg.warnOnce("chg", "trade offer change failed: " + t); }
}""")
M(twin, r"""
public void onClose0(@REF@ ref, @CA@ a) {
  try { super.onClose0(ref, a); } catch (Throwable t) { }
  try { @PKG@.TStore.windowClosed(this); } catch (Throwable t) { @PKG@.TCfg.warn("trade window close handling failed: " + t); }
}""")
M(twin, r"""
public boolean validate(@REF@ ref, @CA@ a) {
  try { return @PKG@.TStore.windowValid(this, ref, a); } catch (Throwable t) { return true; }
}""")
M(ttask, r"""
public void run() { @PKG@.TStore.taskRun(this); }""")
M(tcd, r"""
public void run() {
  try { @PKG@.TStore.countdownStep(this); } catch (Throwable t) { @PKG@.TCfg.warn("trade countdown failed: " + t); }
}""")
M(tjob, r"""
public void run() { @PKG@.TStore.jobRun(this); }""")
M(tfn, r"""
public Object apply(Object o) { return @PKG@.TStore.cancelApi(o); }""")
M(trl, r"""
public void accept(Object ev) {
  try {
    @REF@ r = ((@PRE@) ev).getPlayerRef();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PKG@.TStore.onReady((@PR@) st.getComponent(r, @PR@.getComponentType()));
  } catch (Throwable t) { }
}""")
M(tql, r"""
public void accept(Object ev) {
  try { @PKG@.TStore.onQuit(((@PDE@) ev).getPlayerRef()); } catch (Throwable t) { }
}""")
M(ttk, r"""
public void run() {
  try { this.n = this.n + 1; @PKG@.TStore.tick(this.n); } catch (Throwable t) { @PKG@.TCfg.warnOnce("tick", "trade tick failed: " + t); }
}""")

# ================= /trade and /tradeadmin commands =================
# Permission self-check (tools/ci/lint.py only sees literal super("name" text; these constructors are generated): every class made here
# is "adv" (setPermissionGroups hytale:Adventurer) or "admin" (requirePermission skyyessentials.tradeadmin); ADMIN_CMDS must match the
# admin set exactly, and after compiling, EVERY command class of the jar (0.1.1 ones included) is checked for its permission call.
TCMDS = []
TCMD_PERM = {}
ADMIN_CMDS = {"TALogNamedCmd", "TALogCmd", "TAReturnCmd", "TAConfigCmd", "TAReloadCmd", "TradeAdminCmd"}
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"


def tcmd(clsname, name, desc, perm, body, arg=None, variant=None, subs=()):
    """arg = (field, argName, argDesc, "PLAYER_REF" | "STRING"), read as Object a0."""
    if perm not in ("adv", "admin"):
        raise SystemExit("command %s: perm must be adv or admin" % clsname)
    if clsname in TCMD_PERM:
        raise SystemExit("command class %s defined twice" % clsname)
    c = pool.makeClass(PKG + "." + clsname, pool.get(APC))
    if arg:
        F(c, "public @RA@ %s;" % arg[0])
    lines = [('super("%s", "%s");' % (name, desc)) if name else ('super("%s");' % desc), "@ADV@" if perm == "adv" else "@ADMIN@"]
    if arg:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (arg[0], arg[1], arg[2], arg[3]))
    if variant:
        lines.append("addUsageVariant(new @PKG@.%s());" % variant)
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    ctor = "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines))
    want = T["ADV"] if perm == "adv" else T["ADMIN"]
    if want not in jv(ctor):
        raise SystemExit("command %s: generated constructor lacks %s" % (clsname, want))
    TCMD_PERM[clsname] = perm
    C(c, ctor)
    read = ("    Object a0 = ctx.get(this.%s);\n" % arg[0]) if arg else ""
    M(c, EXEC + " {\n  try {\n" + read + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.TCfg.warn(\"" + clsname + " failed: \" + t);\n"
      "    @PKG@.TStore.tellPr(pr, \"-Something went wrong with that command - the server log has the details.\");\n  }\n}")
    TCMDS.append(c)
    return c


TS = "@PKG@.TStore."
tcmd("TradeWithCmd", None, "Ask a player near you to trade: /trade <player>", "adv", TS + "request(pr, ref, store, a0);",
     arg=("targetArg", "player", "Player to trade with", "PLAYER_REF"))
tcmd("TradeAcceptNamedCmd", None, "Accept the trade request from this player", "adv",
     "if (!(a0 instanceof @PR@)) { " + TS + "tellPr(pr, \"-Usage: /trade accept [player]\"); return; } " + TS + "accept(pr, ref, store, ((@PR@) a0).getUuid());",
     arg=("fromArg", "player", "Player whose trade request to accept", "PLAYER_REF"))
tcmd("TradeAcceptCmd", "accept", "Accept a trade request (newest, or /trade accept <player>)", "adv", TS + "accept(pr, ref, store, (java.util.UUID) null);",
     variant="TradeAcceptNamedCmd")
tcmd("TradeDenyNamedCmd", None, "Refuse the trade request from this player", "adv",
     "if (!(a0 instanceof @PR@)) { " + TS + "tellPr(pr, \"-Usage: /trade deny [player]\"); return; } " + TS + "deny(pr, ((@PR@) a0).getUuid());",
     arg=("fromArg", "player", "Player whose trade request to refuse", "PLAYER_REF"))
tcmd("TradeDenyCmd", "deny", "Refuse a trade request (newest, or /trade deny <player>)", "adv", TS + "deny(pr, (java.util.UUID) null);",
     variant="TradeDenyNamedCmd")
tcmd("TradeCancelCmd", "cancel", "Take back your trade requests and end your open trade (everything goes back)", "adv", TS + "cancelCmd(pr);")
tcmd("TradeClaimCmd", "claim", "Collect what a trade still owes you", "adv", TS + "claim(pr);")
tcmd("TradeCmd", "trade", "Trade with a player: /trade <player>, accept, deny, cancel, claim (/trade alone reopens your trade)", "adv",
     TS + "reopen(pr, ref, store);", variant="TradeWithCmd",
     subs=("TradeAcceptCmd", "TradeDenyCmd", "TradeCancelCmd", "TradeClaimCmd"))
tcmd("TALogNamedCmd", None, "Admin: recent trade log lines of one player: /tradeadmin log <player>", "admin", TS + "adminLog(pr, String.valueOf(a0));",
     arg=("playerArg", "player", "Online name, known name or UUID", "STRING"))
tcmd("TALogCmd", "log", "Admin: recent trade log lines (/tradeadmin log <player> for one player)", "admin", TS + "adminLog(pr, (String) null);",
     variant="TALogNamedCmd")
tcmd("TAReturnCmd", "return", "Admin: cancel a player's open trade and give back everything trades owe them", "admin",
     TS + "adminReturn(pr, String.valueOf(a0));", arg=("playerArg", "player", "Online name, known name or UUID", "STRING"))
tcmd("TAConfigCmd", "config", "Admin: the trade settings page (writes config.properties)", "admin", TS + "adminConfig(pr, ref, store);")
tcmd("TAReloadCmd", "reload", "Admin: re-read config.properties", "admin",
     TS + "adminReload(pr);")
tcmd("TradeAdminCmd", "tradeadmin", "Trade admin: log [player] | return <player> | config | reload", "admin", TS + "adminHelp(pr);",
     subs=("TALogCmd", "TAReturnCmd", "TAConfigCmd", "TAReloadCmd"))
built_admin = set(k for k, v in TCMD_PERM.items() if v == "admin")
if built_admin != ADMIN_CMDS:
    raise SystemExit("ADMIN_CMDS mismatch - built as admin: %s, listed: %s" % (sorted(built_admin), sorted(ADMIN_CMDS)))
for c in TRADE_ALL:
    if str(c.getSuperclass().getName()) == APC:
        raise SystemExit("%s is a command but was not built by tcmd() (no permission self-check)" % c.getName())

# ================= 0.1.3 /warpadmin (admin root command: requirePermission, no permission groups, no sub-commands) =================
wac = pool.makeClass(PKG + ".WarpAdminCmd", pool.get(APC))
player_cmd(wac, f"""
public WarpAdminCmd() {{
  super("warpadmin", "Admin: the warps editor page (add, move, rename, remove and visit warps) and the world spawn");
  requirePermission("skyyessentials.admin");
}}""", f"    {PKG}.EssWarp.open(pr, ref, store);")

# ================= plugin (0.1.1 setup / start / shutdown + the trade parts; 0.1.3 settings switch, /warpadmin, config kit last) =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyEssentialsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @ES@.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyEssentials");
  @ES@.CFG = dir.resolve("config.properties");
  @PKG@.TCfg.DIR = dir;
  @PKG@.TCfg.TDIR = dir.resolve("trades");
  @PKG@.TCfg.PDIR = dir.resolve("trades").resolve("pending");
  @PKG@.TCfg.ADIR = dir.resolve("trades").resolve("archive");
  @PKG@.TCfg.LOGF = dir.resolve("trades").resolve("trade.log");
  @PKG@.TCfg.NAMESF = dir.resolve("trades").resolve("names.properties");
  String cfg = @PKG@.TCfg.load();
  @ES@.R_SHORTCUT = @PKG@.TCfg.REPLY_FILE;
  getCommandRegistry().registerCommand(new @PKG@.TpaCmd());
  getCommandRegistry().registerCommand(new @PKG@.TpaHereCmd());
  getCommandRegistry().registerCommand(new @PKG@.TpAcceptCmd());
  getCommandRegistry().registerCommand(new @PKG@.TpDenyCmd());
  getCommandRegistry().registerCommand(new @PKG@.TpaCancelCmd());
  getCommandRegistry().registerCommand(new @PKG@.MsgCmd());
  getCommandRegistry().registerCommand(new @PKG@.ReplyCmd());
  getCommandRegistry().registerCommand(new @PKG@.FlyCmd());
  String rNote = "/r off (replyShortcut=false)";
  // 0.1.1 review: own try/catch - PluginBase.setup0 fails the WHOLE plugin on any exception from setup(), so a problem in the optional
  // /r takeover must cost only /r, never the commands registered above
  if (@ES@.R_SHORTCUT) {
    try {
      Object other = null;
      try { other = @CMG@.get().getCommandRegistration().get("r"); } catch (Throwable t0) { }
      if (other != null) {
        rNote = "/r left to " + other.getClass().getName();
        @ES@.warn("another mod already registered a top-level /r (" + other.getClass().getName() + ") - SkyyEssentials leaves it alone; players can use /reply.");
      } else {
        @PKG@.RCmd rc = new @PKG@.RCmd();
        if (getCommandRegistry().registerCommand(rc) != null) { @ES@.R_CMD = rc; rNote = "/r (reply; /redo for players allowed to redo)"; }
        else rNote = "/r could not be registered";
      }
    } catch (Throwable t1) {
      @ES@.R_CMD = null;
      rNote = "/r off (error)";
      @ES@.warn("could not set up /r (players can use /reply): " + t1);
    }
  }
  // 0.1.2: /trade in its own try/catch too - a trade problem costs only /trade, never /tpa /msg /r /fly
  String tNote = "/trade /tradeadmin";
  try {
    String loaded = @PKG@.TStore.start();
    getCommandRegistry().registerCommand(new @PKG@.TradeCmd());
    getCommandRegistry().registerCommand(new @PKG@.TradeAdminCmd());
    getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.TReadyL());
    getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.TQuitL());
    tNote = "/trade /tradeadmin (" + loaded + "; " + cfg + ")";
  } catch (Throwable t2) {
    tNote = "/trade off (error)";
    @ES@.warn("could not set up /trade: " + t2);
  }
  // 0.1.3: /warpadmin in its own try/catch (a problem costs only the warps page)
  String wNote = "/warpadmin";
  try { getCommandRegistry().registerCommand(new @PKG@.WarpAdminCmd()); }
  catch (Throwable t3) { wNote = "/warpadmin off (error)"; @ES@.warn("could not set up /warpadmin: " + t3); }
  // 0.1.3 player Settings switch (research/Settings-Spec.md 2.2 / 3.11; tpa.requests and msg.private are NOT built - they wait for Skyy)
  @ES@.regSetting("tpa.updates", "Teleport request updates", "general", true, "Denied, expired and cancelled requests - accepted ones always show");
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.EssTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  // 0.1.3: the admin config kit LAST, after config.properties was loaded (TCfg.load above): config:def / config:fn / config:epoch
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyEssentials] @VERSION@ ready - /tpa /tpahere /tpaccept /tpdeny /tpacancel /msg (tell, w, whisper) /reply /fly; " + rNote + "; " + tNote + "; " + wNote + "; config in SkyWynn Menu -> Server Setup (node skyyessentials.admin)");
}""")
# every plugin's setup() (BuilderTools registers /redo there) has run before any start()
M(pl, r"""
protected void start() {
  @ES@.claimR();
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.TStore.stop(); } catch (Throwable t) { @ES@.warn("trade shutdown failed: " + t); }
  @ES@.releaseR();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

OLD_CMDS = [tpa, tph, tacn, tac, tdnn, tdn, tcan, msg, rep, rcm, flc, wac]
MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS + TRADE_ALL + TCMDS + [eperm, EWARP, wpage, spt, pl]
for c in MINE:
    c.writeFile(OUT)
kit.write(OUT)      # the config kit's deferred checks (hook methods exist with the right signature), then its 7 classes
print("classes written:", len(MINE) + 7)

# compiled permission check: every command class of the jar references its permission call and argument
perm_of = {"FlyCmd": (b"requirePermission", b"skyyessentials.fly"), "WarpAdminCmd": (b"requirePermission", b"skyyessentials.admin")}
for c in OLD_CMDS + TCMDS:
    short = str(c.getSimpleName())
    if short in perm_of:
        need = perm_of[short]
    elif TCMD_PERM.get(short) == "admin":
        need = (b"requirePermission", b"skyyessentials.tradeadmin")
    else:
        need = (b"setPermissionGroups", b"hytale:Adventurer")
    with open(os.path.join(OUT, *(PKG.split(".") + [short + ".class"])), "rb") as fh:
        raw = fh.read()
    if not all(x in raw for x in need):
        raise SystemExit("compiled command %s lacks %s" % (short, " + ".join(x.decode() for x in need)))
print("command permissions checked:", len(OLD_CMDS) + len(TCMDS), "command classes")

jar = os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)
m = B.manifest("SkyyEssentials", VERSION, "SkyWynn essentials, only what vanilla lacks: /tpa /tpahere /tpaccept /tpdeny /tpacancel (cross-world), /msg /reply /r private messages (/r alone still redoes for builders), /trade (safe player trading: items + coins, escrow, countdown), admin /fly /tradeadmin /warpadmin (warps editor + world spawn), every setting in game (SkyWynn Menu Server Setup). Zero dependencies.", PKG + ".SkyyEssentialsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
