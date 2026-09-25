# /trade: build spec (SkyyEssentials 0.1.2)

*Written 2026-09-24 by the trade research pass. Only this file changed - no build script, mod folder or game file was touched.*
*Builds on `SkyyVault/build_skyyvault_0.1.py` (container window + chest fallback, session lifecycle, atomic files, profile-switch gating),
`SkyyEssentials/build_skyyessentials_0.1.1.py` (the tpa request/accept/deny/cancel pattern this reuses almost unchanged), `SkyyCoins/build_skyycoins_0.1.5.py`
(the `coins:fn:get/add/take` bridge), `tools/PROFILES-CONTRACT.md`, and `HANDOFF.md` sections 1 and 3 (`/trade` is locked to live in SkyyEssentials;
"everything a server owner might change must be doable IN GAME" is the 2026-09-24 rule this spec designs against). Owner: Skyy (they/them).*

**Tags.** VERIFIED (research) = consistent across at least two sources found this session, or it is our own live code. UNVERIFIED (research) = one
source only, or sources disagreed - treat as a shape to imitate, not a number to hard-code. Everything in sections 1-3 is paraphrased in our own
words from public wiki/forum/plugin-page content, never copied. Everything from section 4 on is our own design, built on our own mods.

---

## 0. Verdict (plain words)

**One feature added to the existing SkyyEssentials mod, no new mod.** `/trade <player>` works like our `/tpa`: a request, 60 s to accept, a
distance + same-world check. Once accepted, a trade page opens for both players: your own offer is a real container window (drag items in
from your inventory, drag them back out) sitting next to an inline page that shows the other player's offer read-only, a coins box (only if
SkyyCoins is installed), a Ready button, and Cancel. The moment either side changes their offer, both Ready flags clear. Once both are ready, a
3 s countdown starts with editing locked; either player can still cancel; if nobody does, the trade executes automatically at zero.

**The safety idea, in one sentence:** an item you drag into your offer slot is already gone from your inventory and sitting in a small
plugin-owned escrow the instant you drop it - never a client-trusted "shared GUI" that still has to be reconciled with two live inventories
later. That is the same "give to storage first, count before and after" discipline `SkyySacks` and `SkyyVault` already use, and it is also why
almost every classic Minecraft trade-plugin dupe bug (section 3) does not apply to this design in the first place, rather than needing a
special-case fix.

**What can still go wrong, and how it's bounded:** a genuine JVM crash (not a normal stop) between two of our own atomic writes, in the same
few-hundred-millisecond window every Skyy storage mod already accepts (`PROFILES-CONTRACT.md` section 5). Everything else - closing a window,
disconnecting, moving out of range, a full inventory, the server being stopped normally, a profile switch mid-trade - returns every item to its
owner (never swaps it, never drops it, never deletes it), because escrow contents are written to disk on every change and read back at the next
join, exactly like `SkyyVault`'s vault file.

---

## 1. Research: Hypixel SkyBlock player-to-player `/trade`

Hypixel SkyBlock has two separate things both called "trading": the NPC/collection-unlock **Trades** menu inside the Recipe Book (fixed
item-for-item barters with the server, nothing to do with other players), and the **player-to-player `/trade` command**, which is the one this
spec is about. The two are easy to conflate in search results; this section is player-to-player only.

- **Starting a trade (VERIFIED):** `/trade <player>`, shift-right-clicking the other player, or an emerald/trade icon in a player's profile
  menu. The target gets a chat line with a clickable "accept" prompt.
- **Distance (VERIFIED, two sources agreed):** you must be within **9 blocks** of the other player to send or keep a trade request; sources
  did not say whether moving apart after a trade has started forces a cancel, only that starting one requires the 9-block range.
- **The trade window (VERIFIED shape, UNVERIFIED fine detail):** a two-sided panel, "You" on one side and the other player's name on the
  other, separated by a divider. Each side has its own item slots and a coins slot/box. Items and coins placed on your side are visible to
  the other player but only you can change your own side.
- **Coins in the trade (VERIFIED):** coins became tradeable directly through the trade window in a past SkyBlock update (sources cite update
  "0.7.6"; treat the version number as UNVERIFIED, the feature itself as VERIFIED). Coin trade limits are tiered by the player's SkyBlock
  level (UNVERIFIED exact numbers - one detailed source gave roughly 50,000,000 below level 50, 1,000,000,000 at level 50+, and
  10,000,000,000 at level 100+; item-side limits were separately described as around 16 stacks per trade). We have no "SkyBlock level"
  concept, so this is a shape (a tiered coin cap that rises with some progress measure) rather than numbers to copy - flagged as an open
  question in section 20.
- **Accept / confirm / countdown (VERIFIED shape, UNVERIFIED exact seconds):** each side has an accept control; sources disagree on its
  exact look (one calls it a green check, another a red "ACCEPT TRADE" glass pane, which reads like it changed between SkyBlock versions or
  is state-dependent rather than a real disagreement). Multiple sources agree that after both sides accept there is a short **countdown**
  before the trade actually completes, and that **closing the trade menu at any point up to and including during that countdown cancels the
  trade** - nothing is exchanged unless the countdown finishes with the menu still open on both sides. No source gave the exact countdown
  length; we picked 3 seconds for our own design (matches the number Skyy's task description already asks for).
- **Changing an offer after accepting (UNVERIFIED from search, but standard across every trade system we looked at, including our own
  plugin research in section 2):** the working assumption - and the one every plugin below implements explicitly - is that touching either
  side's offer after an accept clears both sides' accept state, so nobody can "accept" a deal and then swap the goods before it executes.
- **Trade limits (VERIFIED, unrelated to the per-trade coin cap):** the *server-wide* Trades menu (the NPC one, not player trading) caps
  daily buys per item at 640; this is a different system and not something we copy for player trades.
- **Anti-scam warnings (VERIFIED as a community norm, not a hard mechanic):** every guide agrees the trade window itself does not stop a
  scam - it only stops a dupe. The advice is entirely social/visual: double-check both sides before accepting, because several SkyBlock
  items render as near-identical icons (an "Enchanted X Block" family was named specifically), and third-party resource packs exist just to
  make those items look different again. There is no in-game "are you sure, this looks like item Y not X" prompt - it's on the player to
  read the window. We take one concrete lesson from this for our own UI: showing the other player's offer with **native tooltips** (not a
  stripped-down icon-and-count row) is the single highest-value anti-scam feature we can build, because it lets the same hover-to-verify
  habit SkyBlock players already have just work.

## 2. Research: Minecraft trade plugins (TradeSystem, TradePlus, SimpleTrade)

These are third-party Bukkit/Spigot plugins, not something we can or would depend on - Hytale has no Bukkit API - but their request/accept
flow and safety fixes are exactly the prior art Skyy's task asked to mine.

- **TradeSystem ("Custom layouts"):** `/trade <player>` or shift-right-click sends a request; the target has **30 seconds** to
  `/trade accept <player>` or click an in-chat "[ACCEPT TRADE]" button. Both players always sit on a fixed side (you are always "left"),
  and the two GUIs are kept in lockstep. Its own changelog (seen via search snippets of its SpigotMC update history) lists more than one
  **dedicated dupe-fix release** across its life, including one described as fixing a duplication caused by "moving items to your own
  inventory at the last moment" - i.e. yanking an item back out of your offer in the same instant the trade executes, so the server credited
  you with both the returned item and whatever you were about to receive. That is exactly the "item swapped after confirm" bug class in
  section 3.
- **TradePlus:** `/trade <player>`, `/tradeyes`, `/tradeno`. Its documented safety feature is precisely the "changing your offer voids the
  other player's acceptance" rule described in section 1 - stated as a deliberate anti-theft measure, not an incidental side effect. That
  independent confirmation (a different plugin, same fix, described as intentional) is why we treat "any change resets both ready flags" as
  a hard rule rather than a nice-to-have.
- **SimpleTrade (the `snugbrick/simpleTrade` project on GitHub, and the separate SpigotMC "SimpleTrade" listing):** `/trade to <player>
  <money>` (or `/trade <player>`) to start, then separate accept/refuse/cancel commands. The GitHub project advertises "duplication free"
  as a headline feature of its own design, which only confirms that dupe-freedom is treated as the plugin's main selling point in this
  space, not a detail - it did not publish how.
- **Common shape across all three, independent of any single one of them:** a request/accept handshake with an expiry, a two-offer GUI kept
  in sync between both clients, an explicit accept step per side, and (once a plugin has been through at least one dupe-fix release) a rule
  that touching your offer after accepting undoes your accept. None of the public pages we could reach described their cancel-on-move,
  cancel-on-damage or cancel-on-disconnect behaviour in enough detail to cite as VERIFIED; we treat "cancel and return everything if either
  player disconnects" as the only non-negotiable one (every plugin in this space has to do at least that much, or its own support forum
  would be full of complaints), and make move/damage cancellation a config choice in section 16 rather than a hard rule, since our escrow
  design (section 10) does not actually need it for safety - only for UX/anti-combat-scam parity.

## 3. Research: classic trade dupe bugs, and why each does not apply here

These are the six bug classes the task named, drawn from the plugin research above plus general Bukkit/Spigot trade-plugin history (an old,
now-declined "Trade" plugin issue from 2014 describing a ghost-item dupe, and a 2024 `UltiTrade` GitHub issue describing an item-loss bug on
cancel). For each one: what causes it in a typical GUI-based trade plugin, and why our escrow design (fully designed in section 10) either
can't produce it or is built to bound it to a logged, recoverable window.

| Classic bug | What causes it in a typical plugin | Why ours doesn't (or how it's bounded) |
|---|---|---|
| **Closing the inventory mid-trade** | Many Bukkit trade GUIs show items that are still, technically, sitting in the player's real inventory (a shared/mirrored view). Closing the window mid-trade can leave the plugin's idea of "what's offered" out of sync with the inventory the client just got back control of. | An item placed in an offer is **already removed from the real inventory** into a plugin-owned `SimpleItemContainer` the instant it's dropped in (same as `SkyyVault`'s vault slots) - it was never "your inventory, just displayed elsewhere." Closing any window just retires that view (`VSession`-style: one more sync, marked inert, `DENY_ALL`); nothing can flow out of a closed view, and the escrowed items are already safely off to the side, tracked by our own file (section 11). |
| **Both-confirm races** (A accepts, B swaps an item, then B accepts too - or both click accept in the same instant) | The two accept flags are checked and the trade executed without re-validating the offers at execution time, or without a single point of serialization between two players' clicks. | One lock per trade session (`synchronized` on the `TSession`, mirroring `AhStore`'s one-lock rule in `Auction-House-Spec.md` section 6.1) serializes every offer change, every ready toggle and the final execute. Any offer change clears **both** ready flags (section 9) - not just the side that changed - so there is no state where "A is still accepted" survives a legitimate edit by B. Execution re-reads the live escrow contents inside the lock, never whatever was on screen when Ready was first clicked. |
| **Disconnect mid-trade** | The plugin either drops the disconnecting player's offered items (they vanish with their in-memory session) or leaves the other player's offer stuck with no way to get it back. | `PlayerDisconnectEvent` ends the whole session for both sides (a trade is two-party - either side leaving ends it for both, not just their half). Both escrows are written to their persisted file (continuously kept current, section 11) and returned to their owner - the online side gets theirs back immediately; the disconnecting side's is delivered automatically the next time they join, read back from the same file. Nothing is ever discarded because a `Bukkit.getPlayer(uuid)`-style lookup came back null (the exact cause named in the `UltiTrade` item-loss issue in section 2) - our return path always has a durable record to fall back to, not just an in-memory map. |
| **Server stop / crash** | Pending trade state lives only in memory (a `HashMap` of active sessions); the process dying loses every escrowed item with it. | Every escrow write is tmp+fsync+atomic-rename to a real file the moment it changes (the `SkyyVault` `VCfg.atomicWrite` pattern), not just held in memory. At boot, and again at each player's join, any leftover escrow record for their UUID is read back and delivered to them, logged either way. A normal stop returns everything before the process exits (plugin `shutdown()` flushes every open session, same as `SkyyVault`); only a true crash between two writes can lose something, and that window is the same few-hundred-millisecond one every Skyy storage mod already accepts and logs. |
| **Full inventory** (at final delivery) | The plugin force-adds items and silently drops the remainder, or (the EssentialsX trade-sign bug found in research) puts back a *partial* amount while still reporting the *original* full amount was available, letting the same crate be "broken" for a full inventory more than once. | Delivery reuses the exact `deliver()` discipline from `Auction-House-Spec.md` section 6.3: count the item before and after `addItemStack`, treat `added = after - before` as the only truth, and whatever didn't fit **stays owed** in the trade's own claim record - never dropped on the ground, never force-added past what the room check allows, never double-counted. |
| **Item swapped after confirm** (this is TradeSystem's own dupe-fix case from section 2 - pulling an item back out at the exact moment of execution) | The execute step trusts the offer as it stood at "accept" time instead of re-reading it, or the client can still send a move packet after accept but before the server processes the execute. | The moment both sides are ready, both escrow windows are set `DENY_ALL` (locked, same mechanism `SkyyVault` uses on a busy/retiring view) for the whole 3 s countdown - there is no window where a move can land after "ready" and before execution. Execution also happens inside the same lock as the ready-check (the both-confirm-race fix above), so "what gets swapped" and "what was agreed" are read from the same locked snapshot. |

The one bug class from the 2014 "ghost item" report (desynced clients showing an item that was never actually removed from either
inventory) is really the same root cause as "closing the inventory mid-trade" above: a GUI whose displayed state can drift from server-held
truth. Because our offer slots *are* the server-held truth (a real container, not a mirrored display), there is nothing for a client to
desync from in the first place.

---

## 4. Scope (SkyyEssentials 0.1.2)

**In 0.1.2:** `/trade <player>`, `/trade accept [player]`, `/trade deny [player]`, `/trade cancel`, the trade page (own offer via container
window + "Open as chest" fallback, other side's offer read-only with native tooltips, coins box gated on SkyyCoins), Ready/Cancel, the 3 s
locked countdown, escrow persistence + return-at-join, `/tradeadmin log|return|config|reload`, config keys editable both in
`config.properties` and in game (section 16, the 2026-09-24 "everything editable in game" rule).

**Not in 0.1.2, designed for later:** bartering more than one item type for coins-plus-items in a single "quick trade" shortcut, trade
history browsing beyond the raw log, a "recently traded with" list, party-only trade shortcuts. None of these need a data-shape change to
add later - the record already carries everything (section 14).

**Mod facts (unchanged):** folder `SkyyEssentials/`, new script `SkyyEssentials/build_skyyessentials_0.1.2.py` (derived from the live 0.1.1
by copy + edit, this mod's own established pattern - no patch script exists for it, per its docstring), package `com.skyy.essentials`, data
still `<world>/mods/Skyy_SkyyEssentials/`. Zero new hard dependency: without SkyyCoins the page opens with no coins box and a line saying
coin trading needs SkyyCoins; without SkyyProfiles, `pkey(u)` is `u.toString()` everywhere per `tools/PROFILES-CONTRACT.md`.

---

## 5. Commands

Every command, subcommand and usage variant calls `setPermissionGroups(new String[] { "hytale:Adventurer" })` (player commands) or
`requirePermission("skyyessentials.tradeadmin")` (admin), per the project's COMMAND RULES. Optional arguments are never positional - each
"optional player" case is a base command (no arg) plus a separate usage variant class with one required `ATY.PLAYER_REF` arg, exactly the
`TpAcceptCmd` / `TpAcceptNamedCmd` split already in `build_skyyessentials_0.1.1.py`.

| Command | Behaviour |
|---|---|
| `/trade <player>` | Sends a request, same rules as `/tpa`: refused if a live request to that player already exists (with seconds left and how to cancel it), refused inside `COOLDOWN_MS` of your last request, distance + same-world checked at send time (section 6). If you already have an open trade session, refused ("finish or `/trade cancel` your current trade first"). |
| `/trade accept` | Accepts the newest live request addressed to you (mirrors `TpaCmd`'s `take(to, null)`). |
| `/trade accept <player>` (usage variant) | Accepts a request from that specific player only. |
| `/trade deny` / `/trade deny <player>` | Same shape as accept, refuses/removes instead. |
| `/trade cancel` | Cancels your own pending outgoing requests (mirrors `/tpacancel`) **and**, if you have an open trade session, ends it - your escrow returns to you, the other side's returns to them, both notified. Whichever applies; refuses only if neither a pending request nor an open session exists. |
| `/trade` (bare) | With no pending session: the usage line. With an open session: reopens/refreshes the trade page (like `/vault` reopening a live session) - useful if you closed the window by accident. |

Accepting re-checks distance and same-world at that moment (a request can outlive either player's position), then opens the trade page for
both.

## 6. Same-world + distance rule

- `tradeSameWorld` (default `true`): both players must be in the same world to send a request, accept one, or keep a session open.
- `tradeDistance` (default `9`, matching Hypixel's researched 9-block figure): the straight-line distance both at accept time and
  continuously while the page is open (checked on the same 1 s ticker every other Skyy escrow mod already runs, e.g. `SkyyVault`'s
  `VTick`). Exceeding it while a session is open cancels the trade and returns both escrows, with a chat line naming which player moved
  away. `tradeDistance=0` disables the live re-check (still enforced at send/accept) for servers that want trading across a whole hub.
- Both checks are skipped entirely when `tradeSameWorld=false` and `tradeDistance=0` together (a server that wants unrestricted trading);
  this is a config choice, not a removed safety feature - it never affects the escrow/dupe-safety guarantees in section 10, only whether a
  session is allowed to exist at all.

## 7. Request / accept / deny / cancel / expiry

Reuses `SkyyEssentials`' own `TpReq`/`EssStore` request-book pattern (`tools/PROFILES-CONTRACT.md` is silent on trade requests since they
carry no per-player storage, so nothing there applies) with its own table so a pending TPA and a pending trade request never collide:

- `tradeExpirySeconds` (default `60`, same as the tpa default already in this mod) - a request older than this is dead; `take()` never
  returns it, and a background sweep (the same 10 s prune the tpa system already runs) clears expired entries from the map so it never
  grows unbounded.
- `tradeCooldownSeconds` (default `10`, same as tpa) - per requester, not per requester-target pair, matching the existing tpa cooldown so
  the two systems feel identical to a player.
- One pending trade request per requester-target pair, same `key(from, to)` scheme as `TpReq`.
- Accepting removes the request atomically (same `take()` semantics: `REQ.remove` happens before anything else can act on it), so a
  double-click accept can never open two sessions from one request.
- A request is silently dropped (not auto-denied, no message) if the sender disconnects before it's answered - the target's next
  `/trade accept` with no matching request just gets the normal "no pending trade request" line.

## 8. The trade page - layout and the container-window question

Same open technical question `SkyyVault` already flagged and never resolved in game: **whether the client actually draws a
`ContainerWindow`'s slots next to a custom page opened with `openCustomPageWithWindows`.** This spec designs for both outcomes exactly the
way `SkyyVault` 0.1 does, because the trade page is a harder version of the same problem (two container windows instead of one, two
viewers instead of one):

- **Primary (page mode, `tradeOpenMode=page`):** one inline page per player, each opened together with **their own** container window
  (`PageManager.openCustomPageWithWindows`, `SkyyVault`'s `VWindow` pattern) holding their offer slots (`tradeSlotsPerSide`, default 16 - a
  4x4 grid, generous enough for a real trade without inviting "list your whole inventory" abuse). Dragging an item from your inventory into
  that window removes it from your inventory and adds it to the window's `SimpleItemContainer` in the same client action - that container
  *is* your half of the escrow (section 10), not a copy of it. The inline part of the page (below or beside the window, BIG readable
  layout per the UI rules) shows:
  - the other player's name and a **read-only** mirror of their offer: one `ItemGrid`/`ItemGridSlot` row per occupied slot, built from a
    **snapshot array**, not their live container, so nothing you click there can ever move a real item. Left at the engine's default
    tooltip behaviour (not `InfoDisplay: None`) specifically so hovering shows the real item name/description/rolls, per the section 1
    lesson that native tooltips are the actual anti-scam feature here; this is a smaller risk of the "stuck tooltip" bug `SkyyMenu` worked
    around, because this grid only ever rebuilds in reaction to a real change event (never on hover, never periodically - see below), so it
    doesn't have the rapid-rebuild conditions that bug needed. Flagged UNVERIFIED until tested in game (section 19).
  - a coins box **only when the SkyyCoins bridge functions are present** (`coins:fn:get`/`add`/`take` all resolve): a `TextField` (the
    `SkyySacks` search-box / `SkyyGuilds` bank amount-box pattern - `EventData "@Key" "#Id.Value"` + rebuild on Enter, never on keystroke)
    for your own coin offer, and a plain read-only line for the other side's. Without SkyyCoins the box is simply absent and a small note
    reads "coin trading needs SkyyCoins" - the rest of the page (items only) still works.
  - the Ready / Cancel buttons and a status line (section 9).
  - **Rebuild discipline (HANDOFF section 2's UI rule, followed exactly):** the page never updates on a timer. It rebuilds only when: the
    escrow container's change event fires (someone's offer changed), a Ready/Cancel click, the countdown ticking down (that one *is* a
    timer, but it's a page the countdown itself owns and only while it's actively running - not a background poll of idle state), or the
    trade completing/cancelling. Rapid successive offer changes (dragging several items in a row) are coalesced to at most one rebuild per
    second, same ceiling the rule requires - the last real change always wins, nothing is ever silently skipped, just batched.
- **Fallback (`tradeOpenMode=chest`, or automatically if page mode is confirmed broken in game):** your own offer opens as a plain vanilla
  chest window on the container (the proven `/invsee`/`SkyyVault` chest pattern - `Page.Bench` + the same `ContainerWindow`), and a
  separate, always-available inline page (`/trade` reopens it) shows the other side's read-only offer, the coins box and the Ready/Cancel
  controls without any window attached. This is strictly worse UX (you can't see both offers on one screen) but it is guaranteed to render,
  exactly why `SkyyVault` ships it as the safety net rather than the default.
- **Never** does this design close one window right before opening another (HANDOFF section 2 rule) - a page swap (e.g. re-showing after a
  reconnect) retires the old view first (`SkyyVault`'s `retire()`: `DENY_ALL`, one last sync, marked inert) and only then opens the new one,
  same order `SkyyVault`'s `open()` already follows.
- **No UI on the vanilla inventory screen** - item input is entirely through the container window / chest fallback, never a custom overlay
  on the player's own inventory panel, per the project-wide UI rule.

## 9. Ready -> both ready -> 3 s countdown -> execute

1. **Ready.** Either player clicks Ready on their half of the page. This only sets that player's flag; it does not lock anything yet.
2. **Any offer change clears both flags**, not just the changer's - registered as the escrow container's change-event handler, so it fires
   however the change happened (drag in, drag out, a coin box edit) and cannot be bypassed by editing through some other path. A change
   also cancels an in-progress countdown immediately if one was running (step 4).
3. **Both ready.** The moment both flags are true (checked inside the trade's one lock, so two ready-clicks landing in the same instant on
   two different world threads still serialize correctly), both escrow containers are set `DENY_ALL` - no further edits are possible from
   either side - and a `tradeCountdownSeconds` (default `3`) countdown starts, shown on both pages ("Trading in 3... 2... 1...").
4. **Cancel during the countdown.** Either player's Cancel button (or `/trade cancel`, or moving out of range if `tradeDistance` is
   enforced, or disconnecting) stops the countdown at once, un-`DENY_ALL`s both containers, clears both ready flags, and both pages return
   to the normal editing view. Nothing has moved yet, so there is nothing to undo besides the lock states.
5. **Execute, at zero, still inside the trade's lock:** the escrow contents are re-read one last time (never trusted from when Ready was
   first clicked - the both-confirm-race fix in section 3), the full swap runs (section 10), and both pages close to a result line
   ("Trade complete!" / whatever didn't fit, per section 10's delivery rule).

This is deliberately closer to Hypixel's own "closing the menu during the countdown cancels it" behaviour (section 1) than to a fourth
manual "Confirm" click: the countdown itself *is* the last chance to back out, and finishing it uninterrupted **is** the confirmation. Section
20 asks Skyy to confirm this reading against the alternative (a literal extra click after the countdown) since the task description's
phrasing could support either.

## 10. ESCROW: the core safety design

This is the section that makes section 3's bug table true, not just asserted.

- **One `TSession` per active trade**, holding both players' UUIDs, both escrow containers (`SimpleItemContainer`, `tradeSlotsPerSide`
  slots each), both coin-offer longs, both ready flags, the countdown task handle (if running), and a `sessionId`. A `ConcurrentHashMap<UUID,
  TSession>` maps **each participant's** UUID to the one session they're in (both keys point at the same session object) - the same
  "one editable view per owner" idea `SkyyVault`'s `SESSIONS` map uses, just two keys per session instead of one.
- **Placing an item removes it from the real inventory the instant it lands in the escrow container** - there is no intermediate state
  where an item is "shown as offered" while still counted as being in the player's inventory. This is the single design choice that makes
  most of section 3 a non-issue rather than something requiring a special-case fix.
- **One lock per session** (`synchronized` on the `TSession` object itself, not a global lock - unlike Auction House's single JVM-wide lock,
  a trade only ever touches its own two players, so per-session locking doesn't create the cross-listing races a per-listing lock would
  in an auction house; nothing inside one trade's lock ever waits on another trade). Every offer change, ready toggle, cancel and the final
  execute run inside it.
- **Count, don't trust (the `SkyySacks 0.6.4` / Auction House `R5` lesson, reused verbatim):** every move between a real inventory and an
  escrow container counts the item id in the source before and after the engine's own move/remove call and treats `after - before` /
  `before - after` as the only truth, never the quantity the click claimed to move. This catches a stack that partially failed to move
  (e.g. inventory momentarily full) without ever inventing or losing part of a stack.
- **Execution (the swap), inside the lock, once the countdown reaches zero:**
  1. Snapshot both escrow arrays as they stand right now (never as they stood when Ready was first clicked).
  2. Deliver player A's escrow contents into player B's inventory, and vice versa, using the exact `deliver()` routine from
     `Auction-House-Spec.md` section 6.3 (room check across storage+hotbar+backpack; count before/after; whatever doesn't fit is **not**
     dropped and **not** force-added - it becomes an owed claim on the recipient's own record, collectible the same way Auction House
     claims are, or automatically retried on their next join).
  3. Coins: take each side's offered coins from their own balance (already validated they had it when offered - re-validated here too,
     since a coin balance could have changed through some other mod in the meantime) and add it to the other side's balance, in the same
     take-then-add order as every other Skyy coin move (never add before the matching take has actually succeeded).
  4. Write the trade record as `COMPLETED` (section 11), log `COMPLETE`, delete the escrow file (nothing left owed on either side unless a
     delivery didn't fit, in which case the file survives holding only the leftover claim).
  5. `markNeedsSave()` (and, if the review pass verifies it the way `Auction-House-Spec.md` section 6.1's R8 did, a forced
     `player.saveConfig(...)` right after, to shrink the crash-loses-state window from the engine's normal 10 s tick down to about however
     long the queued write takes) for both players, since both inventories just changed.
- **Cancel (button, `/trade cancel`, distance/damage rule, or one side disconnecting), inside the lock:** each side's escrow is delivered
  back to **its own owner** (never swapped) with the same `deliver()` routine and the same "owed claim, never dropped" rule if it doesn't
  fit. The record is written `CANCELLED` with a reason, logged, and the file is deleted once both sides' returns are confirmed delivered (or
  kept, holding only the undelivered remainder, exactly like a completed trade with a full inventory on one side).
- **Disconnect** ends the whole session (section 3's table) the same way as an explicit cancel, except the disconnecting player's return
  can't be delivered right now - it stays in the persisted file and is delivered at their next `PlayerConnectEvent`/`PlayerReadyEvent` join,
  same mechanism section 11 describes for a server crash. The still-online player gets their return immediately.

## 11. Data model and files

`<world>/mods/Skyy_SkyyEssentials/trades/` (a new subfolder inside the existing data directory):

- `pending/<sessionId>.json` - one file per **live** trade (exists from the moment either side's offer becomes non-empty, or immediately
  once a session opens if we choose to always persist it, whichever proves simplest to keep provably crash-safe; either way it exists well
  before execution, never created only at the end). Extended-JSON, the same lossless slot codec `SkyyVault`'s `VCodec` already
  implements (engine `ItemStack.CODEC` first, explicit id/qty/durability/quality/metadata fields as the fallback - SkyyRolls reforges and
  graded dishes survive exactly): `sessionId, uuidA, nameA, uuidB, nameB, itemsA:[...], coinsA, itemsB:[...], coinsB, readyA, readyB,
  startedAt, rev`. Written tmp+fsync+atomic-rename (`SkyyVault`'s `VCfg.atomicWrite`, 5 x 20 ms retries on a Windows
  `FileSystemException`) on every offer/coin/ready change, throttled to `tradeSaveDelayMillis` (default `1000`, same default `SkyyVault`
  uses) the same way `VSessions.syncView` schedules `saveSoon` - except a Cancel, a disconnect, or reaching execute always forces an
  immediate synchronous write first, never waits out the throttle.
- `archive/<yyyy-MM>/<sessionId>.json` - a completed or cancelled record, same shape plus `result` (`COMPLETED`/`CANCELLED`/`DISCONNECTED`/
  `ADMIN_RETURNED`) and `endedAt`, moved here (atomic move, never overwriting) once nothing is left owed. Kept for `/tradeadmin log` and any
  future "trade history" page - never deleted outright, so a dispute always has a record.
- `names.properties` - lower-case name -> uuid, so `/tradeadmin return <player>` and `/tradeadmin log <player>` work for an offline player
  by name, same convenience file `SkyyVault`'s admin commands already keep.
- `trade.log` - one line per event: `REQUEST`, `ACCEPT`, `DENY`, `EXPIRE`, `READY`, `UNREADY` (offer changed after being ready), `COUNTDOWN-
  START`, `COUNTDOWN-CANCEL`, `COMPLETE`, `CANCEL` (with reason: `player`, `distance`, `damage`, `world-change`, `disconnect`, `admin`),
  `RETURN-AT-JOIN`, `ADMIN-RETURN`, `WRITE-FAIL`.
- `config.properties` - section 16.

**Return-at-join (the "server stop returns items at next join" requirement, verbatim):** at `PlayerConnectEvent` (or, failing that, that
player's first `PlayerReadyEvent` of the session - the same two-stage fallback `tools/PROFILES-CONTRACT.md` documents for SkyyProfiles'
own join repair), scan `pending/` for any record naming that UUID. If found: the trade could not have completed while they were offline (an
`ACTIVE` `pending/` record only exists for trades that never reached step 5 of section 10 - a `COMPLETED` one is already in `archive/`), so
their escrow is delivered to them right there via `deliver()`, the other side (if still online, or at their own next join otherwise) gets
theirs back too, the record moves to `archive/` as `CANCELLED` (`reason=server-restart`), and `RETURN-AT-JOIN` is logged. This is the exact
same shape as `SkyyVault`'s own orphan-stack handling, just triggered at join instead of at vault-open.

## 12. Profile-busy / profile-switch rules

A trade is a **two-party** session, so - unlike `SkyyVault`, where only one player's own profile state matters - either participant's
`profile:busy:<uuid>` appearing, or either participant's `profile:epoch:<uuid>` changing, ends the **whole session for both sides**, not
just that one player's half:

- Opening a trade page (accepting a request) is refused while either player has `profile:busy:<uuid>` set, same `gate()` check `SkyyVault`
  runs before `open()`.
- An open session is closed by the same 1 s ticker `SkyyVault` uses (checking `profile:busy` and each remembered `profile:epoch` for both
  UUIDs) plus the container window's own `ValidatedWindow.validate()` hook on movement, exactly mirroring `SkyyVault`'s two-path close.
  Closing means: cancel (section 10's cancel path - each side's escrow returns to its own current owner), never a swap.
- `tradeAfterSwitchSeconds` (default `30`, the same number and the same reasoning as `SkyyVault`'s `afterSwitchSeconds`: SkyyProfiles keeps
  its switch marker 30 s after every switch or crash-recovery) - a player who just switched or recovered cannot **start** a new trade
  request or accept one for this many seconds, so a fresh session never opens right into the crash-recovery window `PROFILES-CONTRACT.md`
  section 5 describes.
- **Known limit, stated exactly as plainly as `SkyyVault`'s own docstring states its equivalent one:** because our close-on-busy check runs
  from a 1 s ticker (or on the next player movement), not from inside SkyyProfiles' own switch task, a switch that lands in the same instant
  as a live escrow return can have that return arrive in whichever profile happens to be active at the moment `deliver()` actually runs -
  not necessarily the one that owned the item when it went into escrow. This is the same order of window `SkyyVault` already accepts
  (bounded to about one world tick to one second, never open-ended, always logged), not a new or larger risk this feature introduces.

## 13. Coins (SkyyCoins bridge, optional)

- Presence check: all three of `coins:fn:get`, `coins:fn:add`, `coins:fn:take` must resolve from `System.getProperties().get("skyy.bridge")`
  (the exact `CoinFn` objects `SkyyCoins 0.1.5` registers). If any is missing, the coins box is not built at all - not shown-and-disabled,
  simply absent, matching `SkyyVault`'s own "buying says coins are missing" fallback philosophy but taken one step further since a missing
  coins box costs nothing (item trading is unaffected either way).
- `coins:fn:get`/`add`/`take` act on the **active profile** (per `SkyyCoins`' own docstring) - so a coin offer is taken from, and paid into,
  whichever profile is active for that player right now, exactly like every other coin move in the pack. This is consistent with the item
  side: escrowed items are also just "whatever was in the active profile's inventory" the instant they were dragged in.
- `tradeCoinsAllowed` (default `true`) - a server can turn off the coins box outright even with SkyyCoins installed, for a server that wants
  `/trade` item-only (e.g. to keep a separate economy mod as the only coin-moving path).
- No per-trade coin cap is hard-coded (section 1's Hypixel numbers don't map cleanly onto our economy or our "SkyBlock level" gap) -
  `tradeMaxCoins` (default `0` = no cap) is a config key so a server can set one without a rebuild; whether to eventually tie it to
  something like SkyySkills' overall level total is an open question (section 20), not part of 0.1.2.

## 14. Metadata kept + logs

Every trade record (live in `pending/`, archived afterward) keeps: both UUIDs and the names they had at the time (so a since-renamed player
still reads correctly in old logs), the full item snapshots on both sides (lossless - rolls, quality, durability, metadata all survive via
the shared `VCodec`-style codec), both coin amounts, `startedAt`/`endedAt`, and the result with a reason where one applies (a cancel always
has a reason; a completion doesn't need one). `trade.log` (section 11) is the append-only audit trail an admin reads with `/tradeadmin log`;
the JSON records are the actual state and are what `/tradeadmin return` acts on.

## 15. Admin: `/tradeadmin`

All subcommands `requirePermission("skyyessentials.tradeadmin")`, a new permission node next to the existing `skyyessentials.fly`.

| Command | Behaviour |
|---|---|
| `/tradeadmin log [player]` | Prints recent `trade.log` lines, optionally filtered to trades involving that player (online name, a name seen before in `names.properties`, or a UUID - same resolution `SkyyVault`'s admin commands already use). |
| `/tradeadmin return <player>` | Finds any `pending/` record naming that player (or, if they're mid-trade right now, ends that session as a cancel) and force-delivers their side back to them right away if they're online, or leaves it correctly queued for their next join if not. Logged as `ADMIN-RETURN`. This is the "return stuck escrow" tool the task named - for the case an admin needs to intervene without waiting for a natural cancel/disconnect/reconnect to trigger it. |
| `/tradeadmin config` | Opens the in-game settings page, section 16. |
| `/tradeadmin reload` | Re-reads `config.properties` from disk into the live volatile fields (`SkyyVault`/`SkyyEssentials`'s existing reload pattern) - used when the file was hand-edited outside the in-game page. |

## 16. Config keys + in-game settability

Per the 2026-09-24 HANDOFF rule ("everything a server owner might change must be doable IN GAME... with the config file kept in sync"),
`/tradeadmin config` opens an inline settings page - `TextField`s for numeric/text values (the `SkyySacks` search-box / `SkyyGuilds` bank
amount-box pattern: `EventData "@Key" "#Id.Value"`, rebuild only on submit) and toggle `TextButton`s for booleans, a Save button that writes
`config.properties` atomically (same tmp+fsync+rename as everything else in this spec) **and** updates the live volatile fields in the same
click - never a restart-required setting, matching what this rule already asks of every other admin-facing config in the pack. This is a
step beyond what `SkyyVault` 0.1 itself currently offers (its own config is file-edit-plus-`/vaultadmin reload` only) - worth flagging back
to the vault mod as a future follow-up, but out of scope for this file per the task's "edit only your own mod" boundary.

| Key | Default | Meaning |
|---|---|---|
| `tradeEnabled` | `true` | Turns `/trade` off entirely (commands reply "trading is disabled on this server"); does not affect `/tpa` etc. |
| `tradeSameWorld` | `true` | Section 6. |
| `tradeDistance` | `9` | Section 6; `0` disables the live re-check. |
| `tradeExpirySeconds` | `60` | Section 7. |
| `tradeCooldownSeconds` | `10` | Section 7. |
| `tradeSlotsPerSide` | `16` | Escrow container size per player. |
| `tradeCountdownSeconds` | `3` | Section 9. |
| `tradeCoinsAllowed` | `true` | Section 13. |
| `tradeMaxCoins` | `0` (no cap) | Section 13. |
| `tradeCancelOnDamage` | `true` | Cancels an open session (return-to-owner, section 10) if either player takes damage - anti-combat-scam parity with the plugins in section 2, not a dupe-safety requirement. |
| `tradeOpenMode` | `page` | `page` / `chest`, section 8. |
| `tradeAfterSwitchSeconds` | `30` | Section 12. |
| `tradeSaveDelayMillis` | `1000` | Section 11. |

## 17. Bridge keys published

None required for 0.1.2 to function, but two small ones cost nothing and let other mods react (e.g. a future HUD "trading..." indicator, or
SkyyParty muting party chat during a trade):

- `trade:active:<uuid>` -> `Boolean.TRUE` while that player is in an open session (removed on completion/cancel), mirroring the
  `profile:busy` shape other mods already know how to check.
- `trade:fn:cancel` -> a `Function` taking a `UUID` and cancelling that player's open session if any, `Boolean` result - an escape hatch for
  an admin mod or a future `/tradeadmin` successor to call without needing a direct class dependency.

## 18. Code structure and rough size

Following `SkyyEssentials`' own established pattern (derive 0.1.2 from the live 0.1.1 by copy + edit, no patch script - same as its
docstring already explains for 0.1.1 from 0.1):

| Piece | Rough size |
|---|---|
| `TradeReq` (mirrors `TpReq`), request book additions to `EssStore` | ~80 lines |
| `TSession`, `TStore` (the one-lock-per-session logic, section 10) | ~350 lines |
| `TCodec` (reuse/port of `SkyyVault`'s `VCodec` lossless slot format) | ~120 lines (mostly copied in shape from our own `SkyyVault`, not rewritten from scratch - the two mods sharing a private helper class is fine, it's still each mod bundling its own copy per the "zero external dependencies" rule) |
| `TWindow` (a `ContainerWindow` subclass, mirrors `VWindow`) | ~40 lines |
| `TradePage` (the inline page, both offer views, coins box, Ready/Cancel, countdown) | ~450 lines |
| `TAdminConfigPage` (the in-game settings page, section 16) | ~150 lines |
| Commands (`/trade` + 4 subcommand/variant classes, `/tradeadmin` + 4 subcommands) | ~250 lines |
| Persistence (atomic file I/O, return-at-join hook, the 1 s ticker) | ~200 lines |
| **Total added to `SkyyEssentials`** | **~1,650 lines**, roughly 1.6x the size of the entire current 0.1.1 script (1,011 lines) |

## 19. Test plan

1. Two-account solo test (required by `HANDOFF.md`'s "verify with 2 accounts" multiplayer rule): request, accept, drag items both ways,
   Ready both sides, watch the countdown, let it finish - confirm both inventories end up correct and the `pending/` file is gone.
2. Cancel at every stage: before either is ready, after one is ready (the other never readies), during the countdown (each side cancels
   in turn) - confirm every item and coin returns to its own original owner, never swapped, never lost.
3. Disconnect one player mid-trade with unclaimed items in their escrow; confirm the other player's return is immediate and the
   disconnected player's return happens automatically on their next join, matching the `trade.log` lines exactly.
4. Kill the server process (not a graceful stop) with an open trade holding items; confirm both `pending/*.json` files are intact from the
   last throttled/forced write and both players are made whole at their next join.
5. Fill one player's inventory completely, then execute a trade that would deliver them an item; confirm it becomes an owed claim rather
   than being dropped or force-added, and that it's collectible afterward.
6. **The open technical question from section 8:** confirm in game whether `openCustomPageWithWindows` actually draws the container
   window's slots next to our inline page at all (the same unresolved question `SkyyVault` 0.1 shipped with) - if not, `tradeOpenMode`
   flips to `chest` by default and this spec's page-mode description becomes the aspirational path, same as `SkyyVault`'s own docstring
   already treats its equivalent question.
7. Distance/same-world: start a trade, have one player teleport away (or cross a world boundary) mid-session; confirm the cancel-and-return
   path fires exactly as it does for a disconnect.
8. Profile switch mid-trade (with SkyyProfiles installed): switch one participant's profile while a session is open; confirm the whole
   session cancels for both sides and nothing crosses from one profile's inventory into another's beyond the documented single-tick known
   limit (section 12).

## 20. Open questions for Skyy (the build uses the default in brackets)

1. Is the countdown itself the confirmation (finishing it uninterrupted executes the trade, as designed in section 9), or does Skyy want a
   literal extra "Confirm" click after the countdown reaches zero, closer to a fourth explicit step? **[default: countdown-is-confirmation,
   matching the researched Hypixel behaviour most directly]**
2. Should `tradeMaxCoins` eventually scale with something (total skill levels, collections, an eventual "SkyBlock-level"-alike number), the
   way Hypixel ties its own coin cap to SkyBlock level, or stay a single flat server-wide config number for now? **[default: flat number,
   `0` = uncapped, until a level-like metric exists to key it off]**
3. `tradeCancelOnDamage` default `true` - matches the "don't get combat-scammed mid-trade" spirit of the researched plugins, but on a PvE-
   leaning server this could be an annoyance (stray mob damage cancelling a trade). Keep it `true`, or default `false` and let a PvP-heavy
   server opt in? **[default: `true`]**
4. `tradeSlotsPerSide=16` (a 4x4 grid) - big enough for a normal trade without inviting "dump your whole inventory" abuse, but Hypixel's own
   window reads as noticeably bigger (multiple rows). Keep 16, or go bigger (e.g. 27, a double-chest-row shape)? **[default: 16]**
5. Should a completed trade generate any server-wide or party chat line (e.g. for a guild/party to see "so-and-so traded with so-and-so"),
   or stay entirely private between the two participants the way Hypixel's own trade is? **[default: fully private, log-only]**
