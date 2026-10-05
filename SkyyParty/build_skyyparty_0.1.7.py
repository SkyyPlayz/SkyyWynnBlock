"""SkyyParty 0.1.7 - build script (javassist via jpype).
Run:   python build_skyyparty_0.1.7.py            -> SkyyParty/SkyyParty-0.1.7.jar
       (--deploy exists like every Skyy build script, but only deploy with Skyy's OK; tools/deploy_set.py is the normal path)
Check: python test_skyyparty_0.1.7.py             (bare JVM, -Xverify:all: page states of 0.1.6 and 0.1.7 side by side, the TPA buttons
                                                   with a stand-in SkyyEssentials bridge, every click answered, class byte-compare)
Derived by COPY + EDIT from build_skyyparty_0.1.6.py (the live pin; SkyyParty has used copy + edit since 0.1.3, no patch script).
Same package, class names, commands, bridge keys, file name and file keys. Everything 0.1.6 did is unchanged unless listed here.

0.1.7 (2026-10-05, Skyy 2026-10-03 with a Party page screenshot: "here in the party and a tpa button and a tpa accept to make it quick and
      easy"; docs/answered/social.md REQUEST 2026-10-03 evening). Needs SkyyEssentials 0.1.8 (its tpa bridge); without it the page is 0.1.6's
      plus one short note.
  - TPA button (#SkyyPTpa<i>, small Secondary row action, "TPA") on every OTHER member's row while that member is online and SkyyEssentials'
    bridge is there - for the leader after Promote / Kick, for members alone in the row's action column (#SkyyPAC<i>, now built for every
    row with an action). Click (EventData a = "tpa:<member uuid>") -> skyy.bridge "ess:fn:tpa".apply(Object[] { me, member, FALSE }) =
    EXACTLY /tpa <member> (SkyyEssentials runs its own command body: part.tpa, self, offline, the target's tpa.requests switch + staff
    bypass, already pending, cooldown, the /tpa permission of the registered command). The line it answers (also in chat, like the
    command) is shown in #SkyyPInfo without its "[TPA] " tag.
  - Accept TPA button (#SkyyPTpAcc, Primary, in the footer button row after Leave / Disband) while a /tpa or /tpahere request TO the viewer
    is waiting ("ess:fn:tpaPending".apply(me) -> { fromUuid, fromName, here }, the newest request - the one /tpaccept takes); shown in
    every page state (also when not in a party: a request can come from anyone). The info line (when no click result is showing) names
    it: "<name> wants to teleport to you - press Accept TPA." / "<name> wants you to teleport to them - press Accept TPA.". Click
    (a = "tpaccept:<from uuid>") -> "ess:fn:tpaccept".apply(Object[] { me, from }) = EXACTLY /tpaccept <from>: if that request ran out
    or was taken meanwhile the answer says so ("No pending teleport request from that player.") - never another player's request.
  - The pending state is read when the page is built (open, and every click: each click rebuilds) - no periodic page update (HANDOFF UI
    rules); Refresh re-reads it too.
  - SkyyEssentials missing (no ess:fn:* functions): no TPA / Accept TPA button; in a party with other members the default info line ends
    "(TPA buttons need SkyyEssentials.)"; a click that arrives after SkyyEssentials went away answers "TPA needs SkyyEssentials, which is
    not on this server." A bridge call that throws answers "That didn't work - try /tpa <name> in chat." (logged).
  - EVERY CLICK IS ANSWERED (SkyyExploration 0.2.3's lesson: a click that sends nothing leaves the client on "Loading..."): an unknown
    payload now rebuilds the page (0.1.6 returned without an answer) and a failing handler still rebuilds with "Something went wrong -
    try again." (0.1.6 only logged).
  - Member row columns make room for the TPA button (the row keeps ROW_SLACK px): Promote 120 -> 104 (the 14 px
    uppercase label is 71 px + 2 x 16 padding), Health / Stamina / Mana 175 -> 165 (bars stay 160; "Stamina  1000 / 1000" at 16 px is 157 px), Where 300 ->
    281, TPA 64 ("TPA" at 14 px is ~29 px + padding). Leader's default hint: "You lead this party. Promote, Kick or TPA a member on their row."
    (with SkyyEssentials).
  Not changed: commands, permissions, bridge keys, config rows / files (kit KEEP=10), settings switches, the invite flow, stats.

0.1.6 (history; header of build_skyyparty_0.1.6.py):
SkyyParty 0.1.6 - build script (javassist via jpype).
Run:   python build_skyyparty_0.1.6.py            -> SkyyParty/SkyyParty-0.1.6.jar
       (--deploy exists like every Skyy build script, but only deploy with Skyy's OK; tools/deploy_set.py is the normal path)
Derived by COPY + EDIT from build_skyyparty_0.1.5.py (the live pin; SkyyParty has used copy + edit since 0.1.3, no patch script).
Same package, class names, commands, bridge keys, file name and file keys. Everything 0.1.5 did is unchanged unless listed here.

0.1.6 (2026-09-29, the vanilla UI pass B1 - the LIST-page pilot; Skyy 2026-09-28 "look and feel vanilla", HANDOFF section 2 rule 0,
      research/Vanilla-UI-Style-Guide.md section 7, research/Skyy-UI-Inventory.md 5.16). LOOK ONLY - only PartyPage's markup changes:
  - The build imports the shared kit tools/skyyui.py as SUI and calls SUI.verify() first (every colour, font, texture and sound the page
    writes is proven against Assets.zip at every build); SUI.kit_id() goes into the ready log line.
  - party_page() (below) builds the page from kit calls and emits its Java with the kit emitters; every state (not in a party, invite
    pending, member, member with no stats yet, leader) is run through SUI.check_page and a height budget that fills the body exactly (no FlexWeight filler).
  - Window: the PLAIN vanilla frame (@Container: ContainerHeaderNoRunes title bar, ContainerPatch body, padding 17; the guide's frame for
    list pages), 1400 x 840. The 0.1.5 root #SkyyParty is now the body, #SkyyPTitle the frame title (same b.set text, shown in the 15 px
    Secondary uppercase title style). No dark-blue root, no accent stripe.
  - #SkyyPInfo: one centred bold line (wraps to 2): a click result in the vanilla info blue (the result lines of PartyStore carry no
    +/- marks - they are the same strings the chat commands print), the default hint in the vanilla label grey.
  - Invite pending: the kit's one-row confirm view (confirm_view compact, ids kept: #SkyyPPending / #SkyyPPendTxt / #SkyyPAccept /
    #SkyyPDecline): the warning-yellow question, Accept = Primary (save sound), Decline = Secondary (cancel sound).
  - Members: a section-label column head (#SkyyPHead) over a vanilla scrolling list on the well (#SkyyPList, new: TopScrolling + the
    vanilla scrollbar, the SkyyGear 0.1 pattern). One static list row per member (#SkyyPRow<i>, the WorldEventListRow panel
    colour, 56 high + 3): the viewer's own row carries the 4 px vanilla status bar (the 0.1.5 lighter "you" row); name (row name
    18 px) + role (row sub 15 px; the leader's role in the row name colour #d6e4ee); Health / Stamina / Mana as a 16 px value line
    + a flat bar (the 0.1.5 statCol structure from kit calls: the track #<id>B in the vanilla progress track colour, its fill in the
    stat's own data colour, UI_DATA_COLORS, appended only when it is wider than 0 px); Online (vanilla success green) / Offline
    (vanilla disabled grey) + where; the leader's Promote (small Secondary) + Kick (small Destructive) as row actions. The 0.1.5
    compact rows (more than 5 members squeezed into 460 px) are gone: every row keeps its height and a party bigger than the list
    scrolls (vanilla never paginates or squeezes). Ids SkyyPRole<i> / SkyyPOn<i> therefore exist for every row; for those parties the
    leader's name loses 0.1.5's "* " mark (the role line says it) and an offline member's "Offline" moves from the where line to the
    Online / Offline line.
  - Not in a party: the help text sits in the same list well (#SkyyPEmpty, heading + two lines, centred in the well), so the window
    keeps one geometry.
  - Invite row: vanilla text field (InputBox, #SkyyPInvBox / #SkyyPInvName), Invite = Primary (the row's main action), hint = caption.
  - Footer: the two chat hint lines as captions, the content separator, then Leave party / Disband party (Destructive) left and Refresh
    (Secondary) + Close (Secondary + cancel sound) right.
  Kept exactly: every 0.1.5 element id (asserted below), all 10 event bindings and their EventData ("a" + "@InviteName"), every text
  the page shows and the way it gets there (b.set exactly where 0.1.5 used it; inline only the column heads and button texts, as in
  0.1.5), handleDataEvent, closePage,
  jsonStr / parseUuid / nums / worldPart / stats / where, commands, aliases, permissions, config keys, the config kit rows, bridge
  keys, settings switches, the staff bypass and the party.invites refusal. PartyPage.style() and statCol() are gone (the kit replaces
  them); PartyPage.fillPx() (the 0.1.5 bar maths, 160 px) is new.
  Uses only what deployed Skyy pages already use inline (LayoutMode Top / Left, fixed widths, Anchor margins, Wrap, TopScrolling +
  the vanilla scrollbar of SkyyGear 0.1, the plain title bar of SkyySkills 0.4.6 Overall, the button / input textures and inline
  Sounds of SkyyRanks 0.1.1): no FlexWeight, WrapMaxLines, LetterSpacing, LayoutMode Center / Right, and no UNVERIFIED (trial) element.
  Review fixes (2026-09-29, review rv1b of 0.1.6; same version - 0.1.6 was never deployed; only PartyPage changes):
    - DEPLOY GATE (review medium): keep tools/deploy_set.py SET at ("SkyyParty", "0.1.5") until Skyy has opened probe pages base1 /
      base2 / base3 without a disconnect and "base" is in skyyui.PROBED; the build prints a DEPLOY GATE line while it is not. No
      Server Setup fallback switch to the 0.1.5 look (SkyyGear ui.frames style): a new config row is outside this look-only round.
    - Member row widths: Health / Stamina / Mana columns 185 -> 175 (bars stay 160), Where 280 -> 300; the row keeps ROW_SLACK (10) px
      beyond the 12 px scrollbar reserve (13 px now; asserted), so Kick cannot clip with a scrolling list of 9+ members.
    - Stat bars: the 0.1.5 statCol structure (track #<id>B, a fill Group only when > 0 px) instead of kit bar() + choose(), which drew
      an empty bar as a full-width track-coloured fill child.
    - #SkyyPFootB, #SkyyPEmptyA, #SkyyPInvLbl: back to 0.1.5's empty inline Text + b.set (FootB holds < > /, proven inline on buttons
      only).
    - The leader's role line: row name colour #d6e4ee instead of the gallery-only gold.
    - Not in a party: the heading and the two help lines are centred in the well (computed top padding + HorizontalAlignment Center).
    Kept as they are (review agreed / look-only): click results stay the info blue (PartyStore's result lines carry no +/- marks and
    are the chat texts too); the fixed 1400 x 840 window with its fixed list well (a runtime window size would jump on every Refresh).
  CHECKED (2026-09-29 after the review fixes, kit skyyui 1.3 988889603a0f; SkyyParty/test_skyyparty_0.1.6.py, bare JVM with
  HytaleServer.jar): 29 / 29 classes of 0.1.6 and of 0.1.5 load and initialize under -Xverify:all; 13 page states built by the real
  PartyPage.build of 0.1.5 and 0.1.6 side by side (alone, invites OFF, a click result, invite pending, invite ran out, leader / member
  of 2, leader of 5 with missing / zero / over-max / negative stats and islands, 16-letter names, leader of 7, member of 10, leader
  with a click message, an invite while in a party) gave identical event bindings (type, id, EventData, lock, order), identical texts
  (the compact-row changes above aside), identical inline texts, no 0.1.5 id missing; the 0.1.6 markup as sent passes
  SUI.check_markup / check_page with only kit / data colours, the body children fill 768 px in every state, every row keeps >= 13 px,
  every bar fill is 1-160 px; fillPx = the 0.1.5 bar maths on 5011 cases. 25 of 29 classes are byte-identical; PartyPage (build
  changed, fillPx new, style / statCol gone; closePage differs only by an ldc / ldc_w constant-pool index), SkyyPartyPlugin (setup:
  the ready log line) and the config kit's CfgRows / CfgFn (the version string only) differ.
  UNVERIFIED (needs the game): the whole look - the kit's "base" look has not been seen in game yet (probe pages base1 / base2 /
  base3: plain frame, button textures / inline Sounds / Disabled state / ShrinkTextToFit, the well, the text field, the scrollbar);
  the scrollbar's real width and the text widths of long names / places (labels have no truncation until WrapMaxLines is probed).
  Open this page only after Skyy has opened those probe pages, or together with them on a test server.

0.1.5 (2026-09-28, round 8; Skyy's 2026-09-25 answer "block", Decisions change note 2026-09-25 #7a, OPEN-QUESTIONS "Answer first" 1;
      research/Settings-Spec.md 1.3 exception + 3.11 + section 6 = the REFUSING version):
  PLAYER SETTING party.invites (NEW, General tab, default ON = 0.1.4 behaviour): registered in setup() like party.members / party.chat
    (settings:def:party.invites + settings:fn:register, category general). OFF = nobody can invite that player: PartyStore.invite (the
    ONE path of /party invite AND the page's Invite box) asks PartyStore.inviteGate(sender, target) right after the "can't invite
    yourself" check and BEFORE anything is stored. Refused: no INVITES entry, no line to the target, no bystander "X invited Y" line;
    the sender is told "<name> isn't accepting party invites right now." (the OFF can also be a server-wide default, so no reason is given)
    No SkyyMenu (no settings:fn:get) = no answer = ON = 0.1.4 behaviour. An invite that was already pending when the player turned
    the switch off stays acceptable / declinable (it is the target's own choice to click Accept) and runs out as before.
    The /party page's status line tells a player who is not in a party and has the switch OFF that nobody can invite them (text only,
    the existing #SkyyPInfo label; no new element, no style change).
  STAFF BYPASS (NEW Server Setup row, tools/skyycfg.py kit 1.1; the SAME convention as SkyyEssentials 0.1.5 /tpa + /msg):
    privacy.staffBypass bool, default true, live, category "Privacy", label "Staff get through blocked switches", field
    PartyStore.STAFF_BYPASS, file key privacy.staffBypass in the same config.properties. ON = a sender holding the node skyyparty.bypass
    gets through a target's OFF switch; OFF = staff are refused like everyone else. The ONE staff test (PartyStore.isStaff) is
    PermissionsModule.get().hasPermission(sender, "skyyparty.bypass") alone, inside try (false on any error, e.g. no PermissionsModule):
    ops pass through hytale:Admin's "*", rank groups through the node, and a personal deny "-skyyparty.bypass" (SkyyRanks offers it)
    keeps even an op out - HytaleServer.jar PermissionsModule.hasPermission checks the user's own nodes (deny first) before any group.
    It runs only when the target's switch is OFF. setup() registers the node with the static PermissionsModule.registerPermission(String)
    (ungrouped: no group gets it; it shows in /perm list and SkyyRanks' node search; probed below).
    Notices (identical words on the three blocked paths - party invite, /tpa, /msg): the sender's reply ends "(sent anyway - staff bypass:
    <name> has party invites off)"; the target's invite line tags the sender "<name> (staff) invited you ...".
    The row was called staffBypass earlier in 0.1.5 (never shipped, so no migration): the loader still reads an old staffBypass line
    when the file has no privacy.staffBypass line, and /partyadmin set takes both names. Old 0.1.4 files have neither line: the loader
    and the kit use the default (true); a change in game appends the line. /partyadmin shows it; /partyadmin set privacy.staffBypass
    <true|false|default>.
  LOCKED 2026-09-25 (Skyy, OPEN-QUESTIONS "Server Setup pages"): the party.members switch never hides "X kicked Y from the party." or
    "X invited Y to the party." (both stay plain broadcastTo, as the 0.1.4 review left them). Everything else of party.members /
    party.chat is unchanged.
  Config kit: picks up kit 1.1 (tools/skyycfg.py KIT_VERSION; the build stops if the emitted kit is not 1.1). KEEP=10 old file versions
    (LOCKED 2026-09-25, OPEN-QUESTIONS "In-game server setup" 3; 0.1.4 passed 20). No other kit change: same NODE, rows maxSize /
    inviteSeconds unchanged, same file. The first-run file text gained the privacy.staffBypass comment + line; new category "Privacy".
  Not changed: the /party page look (still the pre-vanilla dark-blue style; the vanilla-style pass is RESUME step 5, one shared helper
    first), commands, bridge keys, the stats ticker, party.members / party.chat gates.

0.1.4 (2026-09-25, in-game server setup round: research/Server-Setup-Spec.md 4.5 + 7, research/Settings-Spec.md 3.11 minus party.invites):
  ADMIN CONFIG (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md; SkyyMenu 0.3 Server Setup shows it as "Party", /modconfig party):
    maxSize        int  5   2-10    live  field PartyStore.MAX (already volatile). Lowering it never removes anyone: a party above the
                                          new limit keeps its members and cannot invite / be joined (the 0.1.3 checks, read at click time;
                                          an invite from such a party now says "the party limit is now N" instead of "full (5/3)").
    inviteSeconds  int  60  15-600  live  unit s, field PartyStore.INVITE_MS*1000 (the field stores ms). Invites already sent keep
                                          their own expiry; new invites, the page hint and the chat lines use the new value.
    No restart or danger rows (spec 4.5). Same file Skyy_SkyyParty/config.properties, same keys maxSize / inviteSeconds (row key =
    file key). RELOAD = none: on a hand edit the kit sets the two fields itself and clamps to the same 2-10 / 15-600 the loader uses.
    The mod's own loader (PartyStore.loadConfig) still runs first in setup(); CfgPub.start(...) publishes config:def:SkyyParty +
    config:fn:SkyyParty as the LAST statement of setup(); CfgPub.shutdown() in shutdown(). The first-run file text is one constant
    (PartyStore.DEFAULT_TEXT = the kit's DEFAULTS); only its comment lines changed (they now say how to change it in game).
  /partyadmin (NEW, admin only: every constructor calls requirePermission("skyyparty.admin") AND setPermissionGroups(new String[0]),
    so no permission group ever gets the node; ops pass through hytale:Admin's "*"):
    /partyadmin                      the current values and how to change them
    /partyadmin reload               re-reads config.properties through the kit's reload op (logged via=command, hand edits logged
                                     via=file) - the spec 4.5 command, so the file works without SkyyMenu too
    /partyadmin set <key> <value>    (extra) CfgFn.cmdSet: validated, logged, versioned like a menu change; value "default" resets
  PLAYER SETTINGS (SkyyMenu 0.2+ /settings, General tab; no SkyyMenu = no answer = on = 0.1.3 behaviour). Registered in setup():
    party.members  "Party join, leave and leader"  gates exactly what its spec help line names (Settings-Spec 2.2 Party #8-11), for
                   the OTHER members: X joined, X left, X disconnected and left, "X is now the party leader" (never hidden from the
                   new leader, who always sees it), "Y is now the party leader (promoted by X)".
    party.chat     "Party chat"                    gates /pc lines from other members (your own line always shows).
    Always shown (Settings-Spec 2.3): every reply to your own action, "The party has been disbanded" / "X disbanded the party",
    "You were kicked", "X made you the party leader", every invite line (sent, received, declined, ran out, cancelled on quit).
    Also always shown (review 2026-09-25): the 0.1.3 bystander lines "X kicked Y from the party." and "X invited Y to the party."
    The spec's help line (exact, owned by Settings-Spec and SkyyMenu's own SET list) does not mention them, so a player who turns
    the switch off must not lose them silently. [SKYY?] If Skyy wants them under party.members: pass "party.members" in the two
    broadcastTo calls in PartyStore.invite / PartyStore.kick (broadcastKey) AND have the spec owner widen the help line.
    NOT built: party.invites (it REFUSES the invite, Settings-Spec section 6 first [SKYY?] is unanswered).
    Only the sendMessage call is gated (PartyStore.broadcastKey); membership, the bridge keys and the stats ticker are untouched.
  Review fixes (2026-09-25, same version - 0.1.4 was never deployed): kick / invite bystander lines ungated (above); the manifest
    Description says "invites that run out (60 s by default)" instead of a fixed 60 s, since inviteSeconds is now admin-set.

0.1.3 (2026-09-24, for Skyy's first 2-player party + guild test; the friend joins as an ordinary hytale:Adventurer player):
  Commands (every command and subcommand calls setPermissionGroups(new String[] { "hytale:Adventurer" }); required args only):
    /party (alias /p)            opens the party PAGE (0.1.2 printed a help line); falls back to the help line in chat
    /party invite <player>       unchanged syntax; the invitee now gets the exact command: "Type /party accept to join (or
                                 /party decline). The invite runs out in 60 s." Expired invites are pruned every 5 s and both
                                 sides are told. A full party (maxSize) refuses the invite and the accept.
    /party accept | leave | list unchanged (list now shows n/max and [leader])
    /party decline               NEW - refuse the pending invite (the inviter is told)
    /party kick <player>         NEW - leader only
    /party promote <player>      NEW - leader only, hands the lead over
    /party disband               NEW - leader only
    /pc <message>                unchanged (GREEDY_STRING)
  /party page (inline, 1240 x 840, root anchor Width/Height only, no underscores in ids, TextButton + EventData, no periodic
    updates - it has a Refresh button): title with n / max, a status line, a pending-invite box with Accept / Decline (when you
    are not in a party and have an open invite), one big row per member (name, "(you)", Party leader / Member, Health, Stamina
    and Mana as "cur / max" text + a bar, from the party:stats bridge value, Online / Offline + where they are: Hub / Your island
    / <name>'s island (their own or anyone else's) / world name, "(with you)" when in your world), leader-only Promote + Kick buttons on the
    other members' rows (not built at all for members), an Invite row (TextField + Invite button, the SkyySacks 0.7.3/0.7.4
    craft search pattern verified in game 2026-09-24: Validating (Enter, no lock) or Activating on the button, EventData
    "a"="invite" + "@InviteName" = "#SkyyPInvName.Value"; the name is matched exactly (ignoring case) first, then by prefix),
    Leave party (members) / Disband (leader only) / Refresh / Close. Every click re-checks everything (leader, membership) at
    click time through the same PartyStore functions the commands use.
  Party store: a party is one Party object (volatile ArrayList, leader at index 0, then join order) that is REPLACED, never
    mutated, under the PartyStore lock, so readers on any thread (bridge Function, pages, ticking system) always see one
    consistent snapshot. Leader leaving or disconnecting still promotes the next member (join order); a party that drops to one
    player is disbanded (0.1.2 rule). Still in memory only, per PLAYER (not per profile - tools/PROFILES-CONTRACT.md rule 6).
  Config: <world>/mods/Skyy_SkyyParty/config.properties (written on first start, tmp + atomic rename): maxSize=5 (2-10),
    inviteSeconds=60 (15-600). Read once at server start (MAX / INVITE_MS are volatile: set in setup(), read on every thread).
  Review fixes (2026-09-24, same version - 0.1.3 was never deployed): the page reads party:stats with split(",", -1) and needs only
    the 6 numbers, so an empty world name no longer hides a member's Health / Stamina / Mana; a member standing on their own island
    shows "<name>'s island" (was the literal "Their island"); "(with you)" needs a non-empty world name; config written atomically.
  FIXED BRIDGE CONTRACT (System.getProperties().get("skyy.bridge") ConcurrentHashMap, per PLAYER):
    "party:fn:members"  java.util.function.Function, apply(java.util.UUID viewer) -> String[] of member UUID strings, leader
                        first, then join order; an empty String[0] when not in a party (also for a null / bad argument).
    "party:leader:<uuid>" leader UUID string, for every member; removed when the player is not in a party.
    "party:name:<uuid>" the player's username; published for every online player about once a second (ticking system) and at
                        every party action; kept after they leave (offline members' names stay readable).
    "party:stats:<uuid>" "hp,maxHp,stamina,maxStamina,mana,maxMana,worldName" (ints, Math.round), refreshed about every 1 s
                        (wall clock) on THAT member's own world thread by PartyStats (an EntityTickingSystem on Player
                        entities, one registerSystem for the class; EntityTickingSystem.isParallel() returns false in
                        HytaleServer.jar, so ticks run on the world thread), only while they are in a party. Commas in the
                        world name are replaced by spaces. Removed on leave / kick / disband / disconnect (the store removes
                        it after updating membership and the ticker re-checks membership after every put, so a tick racing
                        a leave can never leave a stale value behind).
    All party:* keys are removed in shutdown().
  Engine facts used (HytaleServer.jar, tools/dev reflect.py / bcfull.py, 2026-09-24):
    PlayerRef.isValid() = entity ref != null || holder != null, so a player in a cross-world transfer still counts as online.
    Universe.getPlayerByUsername(String, NameMatching) with NameMatching EXACT_IGNORE_CASE / STARTS_WITH_IGNORE_CASE.
    Store.getExternalData() -> EntityStore.getWorld().getName() inside the ticking system.
    PageManager.setPage(ref, store, Page.None) closes the page (SkyyMenu 0.1.2 close path, verified in game).
  Threads: commands and page clicks run on the clicking player's world thread and only touch PartyStore (synchronized static
    methods, no calls out while locked), the bridge map and PlayerRef.sendMessage (the 0.1.2 cross-player broadcast path).
    The 5 s invite pruner runs on HytaleServer.SCHEDULED_EXECUTOR and only touches INVITES + chat. Nothing reads another
    player's components: other members' stats come from the bridge value their own world thread wrote.

0.1.2: ordinary players can use the party commands. Every command (/party alias /p, /party invite|accept|leave|list, /pc)
  calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as SkyyEssentials 0.1).
  Engine (HytaleServer.jar bytecode, 2026-09-23): AbstractCommand.setOwner() gives every command without requirePermission() an
  auto node "<plugin base permission>.command.party" (subcommands: that id + ".invite" etc., version included), which default
  "hytale:Adventurer" players never held, so only "*" admins could run them. putRecursivePermissionGroups() walks subcommands,
  CommandManager.createVirtualPermissionGroups() collects it, PermissionsModule.start() -> refreshVirtualGroups() runs after
  every plugin setup(). Subcommand hasPermission(): own node, then (only when it has no groups of its own) the parent node.
  Positional arguments already work and are unchanged: "/party invite <player>" = subcommand dispatch on the first token
  (checkForExecutingSubcommands -> convertToSubCommand) then 1 token == 1 required arg; "/party" alone runs PartyCmd.execute
  (not an AbstractCommandCollection, 0 tokens == 0 required); "/pc <message with spaces>" = GREEDY_STRING, which sets
  allowsExtraArguments and passes the raw tail (extractGreedyRawTail) as one value.
Fixes vs 0.1 (code review 2026-09-22): synchronized party store (no lost members on concurrent accept),
accept refuses when already in a party, leader leaving promotes the next member instead of disbanding,
players are removed from their party on disconnect, expired invites are pruned, direct Universe.getPlayer
lookup, no exception text leaked to chat.
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI       # 0.1.6: the shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md)
SUI.verify()               # proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()      # "skyyui <version> <blob12>" - in the ready log line

VERSION = "0.1.7"
EXPECTED_KIT = "1.1"      # 0.1.5 picks up config kit 1.1 on purpose (tools/CONFIG-CONTRACT.md "Kit versions")
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.party"
T = {
    "PKG": PKG,
    "JP":  "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":  "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST":  "com.hypixel.hytale.component.Store",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":  "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":  "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "PGE": "com.hypixel.hytale.protocol.packets.interface_.Page",
    "NMT": "com.hypixel.hytale.server.core.NameMatching",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":  "com.hypixel.hytale.component.CommandBuffer",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "CRP": "com.hypixel.hytale.component.ComponentRegistryProxy",
    "ES":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "PBS": "com.hypixel.hytale.server.core.plugin.PluginBase",
    "PM":  "com.hypixel.hytale.server.core.permissions.PermissionsModule",   # 0.1.5: staff bypass (skyyparty.bypass node test)
    # every party command is player-facing: grant its (auto-generated) permission node to the default player group
    "ADV": 'setPermissionGroups(new String[] { "hytale:Adventurer" });',
}
TOK = re.compile(r"@([A-Z]+)@")


def sub(src):
    out = TOK.sub(lambda m: T[m.group(1)] if m.group(1) in T else m.group(0), src)
    left = TOK.findall(out)
    if left:
        raise SystemExit("unknown @TOKEN@ in Java source: %s" % left)
    return out


def M(cls, src):
    cls.addMethod(CtNewMethod.make(sub(src), cls))


def C(cls, src):
    cls.addConstructor(CtNewConstructor.make(sub(src), cls))


def F(cls, src):
    cls.addField(CtField.make(sub(src), cls))


for c, m in ((T["UNI"], "getPlayer"), (T["UNI"], "getPlayerByUsername"), (T["UNI"], "getDefaultWorld"), (T["PDE"], "getPlayerRef"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["PBS"], "shutdown"), (T["PBS"], "getEntityStoreRegistry"), (T["PBS"], "getDataDirectory"),
             (T["APC"], "setPermissionGroups"), (T["ATY"], "PLAYER_REF"), (T["ATY"], "GREEDY_STRING"), (T["PR"], "isValid"),
             (T["PR"], "getUsername"), (T["NMT"], "EXACT_IGNORE_CASE"), (T["NMT"], "STARTS_WITH_IGNORE_CASE"),
             (T["PAGE"], "rebuild"), (T["PGM"], "openCustomPage"), (T["PGM"], "setPage"), (T["PGE"], "None"), (T["PLA"], "getPageManager"),
             (T["PLA"], "isWaitingForClientReady"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"),
             (T["EVD"], "of"), (T["EVD"], "append"), (T["BT"], "Activating"), (T["BT"], "Validating"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["DST"], "getHealth"),
             (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["ETS"], "tick"), (T["ACH"], "getReferenceTo"), (T["CB"], "getComponent"),
             (T["CRP"], "registerSystem"), (T["ST"], "getExternalData"), (T["ES"], "getWorld"), (T["WLD"], "getName"),
             # 0.1.4: /partyadmin (admin node, cleared groups, STRING args) + the config kit's scheduler / permission check
             (T["APC"], "requirePermission"), (T["APC"], "addSubCommand"), (T["APC"], "withRequiredArg"), (T["ATY"], "STRING"),
             (T["CTX"], "get"), ("com.hypixel.hytale.server.core.permissions.PermissionsModule", "hasPermission"),
             # 0.1.5: staff bypass = hasPermission(sender, skyyparty.bypass) alone; the node is registered (static, ungrouped) in setup()
             (T["PM"], "get"), (T["PM"], "registerPermission")):
    B.probe(pool, c, m)
# 0.1.5: the exact overloads the staff bypass compiles against (javassist picks them by argument count / types)
_pmc = pool.get(T["PM"])
assert any(str(x.getSignature()) == "(Ljava/lang/String;)V" and J["Modifier"].isStatic(x.getModifiers())
           for x in _pmc.getDeclaredMethods("registerPermission")), "PermissionsModule.registerPermission(String) static void is missing"
assert any(str(x.getSignature()) == "(Ljava/util/UUID;Ljava/lang/String;)Z" and not J["Modifier"].isStatic(x.getModifiers())
           for x in _pmc.getDeclaredMethods("hasPermission")), "PermissionsModule.hasPermission(UUID, String) boolean is missing"

pty  = pool.makeClass(PKG + ".Party")
ps   = pool.makeClass(PKG + ".PartyStore")
fn   = pool.makeClass(PKG + ".PartyFn")
sts  = pool.makeClass(PKG + ".PartyStats", pool.get(T["ETS"]))
page = pool.makeClass(PKG + ".PartyPage", pool.get(T["PAGE"]))
inv  = pool.makeClass(PKG + ".InviteCmd", pool.get(T["APC"]))
acc  = pool.makeClass(PKG + ".AcceptCmd", pool.get(T["APC"]))
dec  = pool.makeClass(PKG + ".DeclineCmd", pool.get(T["APC"]))
lev  = pool.makeClass(PKG + ".LeaveCmd", pool.get(T["APC"]))
lst  = pool.makeClass(PKG + ".ListCmd", pool.get(T["APC"]))
kck  = pool.makeClass(PKG + ".KickCmd", pool.get(T["APC"]))
pro  = pool.makeClass(PKG + ".PromoteCmd", pool.get(T["APC"]))
dis  = pool.makeClass(PKG + ".DisbandCmd", pool.get(T["APC"]))
pc   = pool.makeClass(PKG + ".PartyChatCmd", pool.get(T["APC"]))
root = pool.makeClass(PKG + ".PartyCmd", pool.get(T["APC"]))
adm  = pool.makeClass(PKG + ".PartyAdmin")                               # 0.1.4: /partyadmin logic (config kit calls)
admr = pool.makeClass(PKG + ".PartyAdminReloadCmd", pool.get(T["APC"]))  # 0.1.4: /partyadmin reload
adms = pool.makeClass(PKG + ".PartyAdminSetCmd", pool.get(T["APC"]))     # 0.1.4: /partyadmin set <key> <value>
admc = pool.makeClass(PKG + ".PartyAdminCmd", pool.get(T["APC"]))        # 0.1.4: /partyadmin
quit_ = pool.makeClass(PKG + ".PartyQuit")
prune = pool.makeClass(PKG + ".PartyPrune")
pl   = pool.makeClass(PKG + ".SkyyPartyPlugin", pool.get(T["JP"]))

# ================= Party: one party = one immutable-by-convention member list (leader first), swapped under the store lock =================
F(pty, "public volatile java.util.ArrayList list;")
C(pty, "public Party(java.util.ArrayList l) { this.list = l; }")

# ================= PartyStore (in-memory, per player; THE data feed for the HUD party widget + future map) =================
F(ps, "public static @LOG@ LOG;")
F(ps, "public static final java.util.concurrent.ConcurrentHashMap PARTY_OF = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> Party
F(ps, "public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();")   # invitee uuid -> Object[]{inviter uuid, Long expiryMs, String inviterName}
F(ps, "public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();")     # uuid -> long[]{last stats publish ms}
F(ps, "public static volatile int MAX = 5;")          # loadConfig in setup(), then the config kit (live), read from every thread
F(ps, "public static volatile long INVITE_MS = 60000L;")   # milliseconds; the kit row is inviteSeconds (unit s, *1000)
# 0.1.5: holders of skyyparty.bypass (ops through "*") get through a target's party.invites OFF switch; loadConfig in setup(), then the
# kit row privacy.staffBypass
F(ps, "public static volatile boolean STAFF_BYPASS = true;")
F(ps, 'public static final String BYPASS_PERM = "skyyparty.bypass";')
# 0.1.4: the first-run config.properties text = the config kit's DEFAULTS (one constant, so the two can never differ). Only the comment
# lines differ from 0.1.3's text; the loader still writes it with the system line separator, like 0.1.3. 0.1.5 added privacy.staffBypass.
CONFIG_TEXT = "\n".join([
    "# SkyyParty settings. Change them in game (SkyWynn Menu - Server Setup - Party, or /modconfig party) or edit this file and type /partyadmin reload.",
    "# maxSize = most players in one party (2-10). Lowering it never removes anyone - a bigger party just cannot invite.",
    "maxSize=5",
    "# inviteSeconds = how long a party invite stays open (15-600)",
    "inviteSeconds=60",
    "# privacy.staffBypass = players with skyyparty.bypass (ops included) can still invite players who turned party invites off in /settings (true or false)",
    "privacy.staffBypass=true",
    "",
])
assert all(ord(ch) < 128 for ch in CONFIG_TEXT) and "@" not in CONFIG_TEXT and '"' not in CONFIG_TEXT
F(ps, "public static final String DEFAULT_TEXT = %s;" % json.dumps(CONFIG_TEXT))
M(ps, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyParty] " + msg); } catch (Throwable t) { }
}""")
# the SkyyCoins / SkyyProfiles bridge helper, verbatim (same monitor, so no mod can create a second map)
M(ps, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# 0.1.4: player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.2-1.3). No SkyyMenu = no answer = today's behaviour (on).
# settings:fn:get never throws, never calls out and holds only SkyyMenu's own monitor, so it is safe from any thread (1.2 guarantees).
M(ps, r"""
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
}""")
M(ps, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyParty", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
# 0.1.5: staff = hasPermission(u, skyyparty.bypass) ALONE (the same test as SkyyEssentials' skyyessentials.bypass). The engine checks the
# user's own nodes first (a personal "-skyyparty.bypass" denies, even for an op), then each group: hytale:Admin's "*" lets every op
# through, a rank group passes through the node. PermissionsModule is safe from any thread (the config kit calls it from any thread
# too); fail closed: false on any error (no PermissionsModule, a provider that throws).
M(ps, r"""
public static boolean isStaff(java.util.UUID u) {
  if (u == null) return false;
  try {
    @PM@ pm = @PM@.get();
    if (pm == null) return false;
    return pm.hasPermission(u, BYPASS_PERM);
  } catch (Throwable t) { return false; }
}""")
# 0.1.5: setup() registers the node (static registerPermission(String) = an entry with NO groups, so no group is granted it; refreshVirtual
# Groups only copies registered groups). It then shows in /perm list and SkyyRanks' node search. Never throws; true = registered.
M(ps, r"""
public static boolean regPerm() {
  try {
    @PM@.registerPermission(BYPASS_PERM);
    return true;
  } catch (Throwable t) {
    warn("could not register the permission node " + BYPASS_PERM + " (the staff bypass still works): " + t);
    return false;
  }
}""")
# 0.1.5: the party.invites gate (Settings-Spec 1.3 exception + 3.11, refusing version). 0 = send the invite, 1 = REFUSE (the target has
# party invites OFF), 2 = send anyway (the target has them OFF, the sender is staff and privacy.staffBypass is on). The cheap, lock-free settings
# read comes first; the permission lookup runs only for a refused invite.
M(ps, r"""
public static int inviteGate(java.util.UUID sender, java.util.UUID target) {
  if (notifyOn(target, "party.invites")) return 0;
  if (STAFF_BYPASS && isStaff(sender)) return 2;
  return 1;
}""")
M(ps, r"""
public static java.util.ArrayList listOf(java.util.UUID u) {
  if (u == null) return null;
  Object o = PARTY_OF.get(u);
  if (o == null) return null;
  java.util.ArrayList l = ((@PKG@.Party) o).list;
  if (l == null || l.isEmpty() || !l.contains(u)) return null;
  return l;
}""")
M(ps, r"""
public static java.util.UUID leaderOf(java.util.UUID u) {
  java.util.ArrayList l = listOf(u);
  return l == null ? null : (java.util.UUID) l.get(0);
}""")
M(ps, r"""
public static @PR@ online(java.util.UUID u) {
  if (u == null) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(u);
    return (p != null && p.isValid()) ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(ps, r"""
public static void pubName(@PR@ p) {
  try {
    if (p == null) return;
    String n = p.getUsername();
    if (n == null || n.length() == 0) return;
    java.util.Map b = bridge();
    String k = "party:name:" + p.getUuid().toString();
    if (!n.equals(b.get(k))) b.put(k, n);
  } catch (Throwable t) { }
}""")
M(ps, r"""
public static String nameOf(java.util.UUID u) {
  if (u == null) return "someone";
  @PR@ p = online(u);
  if (p != null && p.getUsername() != null) return p.getUsername();
  try {
    Object n = bridge().get("party:name:" + u.toString());
    if (n != null) return n.toString();
  } catch (Throwable t) { }
  return "someone";
}""")
M(ps, r"""
public static String cut(String s, int max) {
  if (s == null) return "";
  if (s.length() <= max) return s;
  return s.substring(0, max) + "...";
}""")
M(ps, r"""
public static void publishParty(java.util.ArrayList l) {
  if (l == null || l.isEmpty()) return;
  java.util.Map b = bridge();
  String lead = l.get(0).toString();
  for (int i = 0; i < l.size(); i++) b.put("party:leader:" + l.get(i).toString(), lead);
}""")
M(ps, r"""
public static void unpublish(java.util.UUID u) {
  if (u == null) return;
  java.util.Map b = bridge();
  b.remove("party:leader:" + u.toString());
  b.remove("party:stats:" + u.toString());
}""")
# ---- the only methods that change parties (synchronized, never call out except the bridge map) ----
# 0 = joined, 1 = member already in a party, 2 = party full
M(ps, r"""
public static synchronized int join(java.util.UUID inviter, java.util.UUID member) {
  if (listOf(member) != null) return 1;
  java.util.ArrayList cur = listOf(inviter);
  @PKG@.Party pt;
  java.util.ArrayList nl;
  if (cur == null) {
    nl = new java.util.ArrayList();
    nl.add(inviter);
    pt = new @PKG@.Party(nl);
  } else {
    pt = (@PKG@.Party) PARTY_OF.get(inviter);
    nl = new java.util.ArrayList(cur);
  }
  if (nl.size() >= MAX) return 2;
  nl.add(member);
  pt.list = nl;
  PARTY_OF.put(inviter, pt);
  PARTY_OF.put(member, pt);
  publishParty(nl);
  return 0;
}""")
# null = was not in a party; else { ArrayList before, ArrayList after (the others, new leader first), Boolean disbanded }
M(ps, r"""
public static synchronized Object[] removeMember(java.util.UUID m) {
  java.util.ArrayList before = listOf(m);
  if (before == null) {
    PARTY_OF.remove(m);
    unpublish(m);
    return null;
  }
  @PKG@.Party pt = (@PKG@.Party) PARTY_OF.get(m);
  java.util.ArrayList after = new java.util.ArrayList(before);
  after.remove(m);
  PARTY_OF.remove(m);
  unpublish(m);
  if (after.size() <= 1) {
    for (int i = 0; i < after.size(); i++) {
      java.util.UUID o = (java.util.UUID) after.get(i);
      PARTY_OF.remove(o);
      unpublish(o);
    }
    pt.list = new java.util.ArrayList();
    return new Object[] { before, after, Boolean.TRUE };
  }
  pt.list = after;
  publishParty(after);
  return new Object[] { before, after, Boolean.FALSE };
}""")
M(ps, r"""
public static synchronized Object[] kickM(java.util.UUID leader, java.util.UUID target) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return new Object[] { "none" };
  if (!leader.equals(l.get(0))) return new Object[] { "notleader" };
  if (leader.equals(target)) return new Object[] { "self" };
  if (!l.contains(target)) return new Object[] { "notmember" };
  Object[] r = removeMember(target);
  if (r == null) return new Object[] { "notmember" };
  return new Object[] { "ok", r[0], r[1], r[2] };
}""")
M(ps, r"""
public static synchronized String promoteM(java.util.UUID leader, java.util.UUID target) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return "none";
  if (!leader.equals(l.get(0))) return "notleader";
  if (leader.equals(target)) return "self";
  if (!l.contains(target)) return "notmember";
  java.util.ArrayList nl = new java.util.ArrayList();
  nl.add(target);
  for (int i = 0; i < l.size(); i++) if (!target.equals(l.get(i))) nl.add(l.get(i));
  ((@PKG@.Party) PARTY_OF.get(leader)).list = nl;
  publishParty(nl);
  return "ok";
}""")
M(ps, r"""
public static synchronized Object[] disbandM(java.util.UUID leader) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return new Object[] { "none", null };
  if (!leader.equals(l.get(0))) return new Object[] { "notleader", null };
  @PKG@.Party pt = (@PKG@.Party) PARTY_OF.get(leader);
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID o = (java.util.UUID) l.get(i);
    PARTY_OF.remove(o);
    unpublish(o);
  }
  pt.list = new java.util.ArrayList();
  return new Object[] { "ok", l };
}""")
# ---- chat helpers ----
M(ps, r"""
public static void send(@PR@ p, String msg) {
  try { if (p != null) p.sendMessage(@MSG@.raw(msg)); } catch (Throwable t) { }
}""")
M(ps, r"""
public static void tell(java.util.UUID u, String msg) {
  send(online(u), msg);
}""")
# 0.1.4: key = the player Settings switch that may hide this line (null = always shown); always = the one member who sees it
# regardless (the new leader for "is now the party leader", the sender for their own /pc line). Only the send is skipped.
M(ps, r"""
public static void broadcastKey(java.util.List l, String msg, java.util.UUID skip1, java.util.UUID skip2, String key, java.util.UUID always) {
  if (l == null) return;
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID u = (java.util.UUID) l.get(i);
    if (u.equals(skip1) || u.equals(skip2)) continue;
    @PR@ p = online(u);
    if (p == null) continue;
    if (key != null && !u.equals(always) && !notifyOn(u, key)) continue;
    send(p, msg);
  }
}""")
M(ps, r"""
public static void broadcastTo(java.util.List l, String msg, java.util.UUID skip1, java.util.UUID skip2) {
  broadcastKey(l, msg, skip1, skip2, (String) null, (java.util.UUID) null);
}""")
M(ps, r"""
public static int inviteSecs() {
  return (int) (INVITE_MS / 1000L);
}""")
M(ps, r"""
public static String helpText() {
  return "Party: /party (opens the party page) - /party invite <player> - /party accept - /party decline - /party leave - /party list - /party kick <player> - /party promote <player> - /party disband - /pc <message>";
}""")
# a typed player name from the page TextField: letters, digits and underscores only (Hytale usernames), max 32
M(ps, r"""
public static String cleanName(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 32; i++) {
    char c = s.charAt(i);
    if (Character.isLetterOrDigit(c) || c == '_') sb.append(c);
  }
  return sb.toString();
}""")
M(ps, r"""
public static @PR@ findOnline(String name) {
  if (name == null || name.length() == 0) return null;
  @PR@ p = null;
  try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.EXACT_IGNORE_CASE); } catch (Throwable t) { p = null; }
  if (p == null) {
    try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.STARTS_WITH_IGNORE_CASE); } catch (Throwable t) { p = null; }
  }
  return (p != null && p.isValid()) ? p : null;
}""")
# ---- actions (commands AND page buttons): each returns the line for the acting player; others get [Party] chat lines ----
M(ps, r"""
public static String invite(@PR@ me, @PR@ target) {
  if (target == null || !target.isValid()) return "That player is not online.";
  java.util.UUID mu = me.getUuid();
  java.util.UUID tu = target.getUuid();
  if (tu.equals(mu)) return "You can't invite yourself.";
  pubName(me);
  pubName(target);
  String tn = target.getUsername();
  // 0.1.5: party.invites OFF refuses the invite before anything is stored or sent (no INVITES entry, no line to the target or party)
  int gate = inviteGate(mu, tu);
  if (gate == 1) return tn + " isn't accepting party invites right now.";
  if (listOf(tu) != null) return tn + " is already in a party.";
  java.util.ArrayList mine = listOf(mu);
  int n = mine == null ? 1 : mine.size();
  // 0.1.4: maxSize is live, so an admin may lower it below a running party: it keeps its members and cannot invite (spec 4.5)
  if (n > MAX) return "Your party has " + n + " players and the party limit is now " + MAX + " - nobody can join until it is smaller.";
  if (n >= MAX) return "Your party is full (" + n + "/" + MAX + ").";
  long now = System.currentTimeMillis();
  Object[] old = (Object[]) INVITES.get(tu);
  if (old != null && mu.equals(old[0]) && ((Long) old[1]).longValue() > now) {
    long left = (((Long) old[1]).longValue() - now + 999L) / 1000L;
    return "You already invited " + tn + " - that invite runs out in " + left + " s.";
  }
  INVITES.put(tu, new Object[] { mu, Long.valueOf(now + INVITE_MS), me.getUsername() });
  int s = inviteSecs();
  // 0.1.5 staff bypass notices - the same words as SkyyEssentials /tpa and /msg: the target sees "<name> (staff)", the sender
  // "(sent anyway - staff bypass: <name> has party invites off)"
  String from = me.getUsername() + (gate == 2 ? " (staff)" : "");
  send(target, "[Party] " + from + " invited you to their party! Type /party accept to join (or /party decline). The invite runs out in " + s + " s.");
  // LOCKED 2026-09-25 (Skyy): "X invited Y to the party." is always shown - party.members never hides it
  if (mine != null) broadcastTo(mine, "[Party] " + me.getUsername() + " invited " + tn + " to the party.", mu, null);
  return "Invited " + tn + " to your party. They have " + s + " s to type /party accept." + (gate == 2 ? (" (sent anyway - staff bypass: " + tn + " has party invites off)") : "");
}""")
M(ps, r"""
public static String accept(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  pubName(me);
  if (listOf(mu) != null) return "You're already in a party. Leave it first with /party leave.";
  Object[] inv = (Object[]) INVITES.remove(mu);
  if (inv == null || ((Long) inv[1]).longValue() < System.currentTimeMillis()) return "You have no party invite right now (invites run out after " + inviteSecs() + " s).";
  java.util.UUID inviter = (java.util.UUID) inv[0];
  if (online(inviter) == null) return "The player who invited you is no longer online.";
  int r = join(inviter, mu);
  if (r == 1) return "You're already in a party.";
  if (r == 2) return "That party is full (" + MAX + " players).";
  java.util.ArrayList l = listOf(mu);
  if (l == null) return "Could not join the party.";
  broadcastKey(l, "[Party] " + me.getUsername() + " joined the party! (" + l.size() + "/" + MAX + ")", mu, null, "party.members", null);
  return "You joined " + nameOf((java.util.UUID) l.get(0)) + "'s party! Open /party to see it. Party chat: /pc <message>";
}""")
M(ps, r"""
public static String decline(@PR@ me) {
  Object[] inv = (Object[]) INVITES.remove(me.getUuid());
  if (inv == null || ((Long) inv[1]).longValue() < System.currentTimeMillis()) return "You have no party invite right now.";
  tell((java.util.UUID) inv[0], "[Party] " + me.getUsername() + " declined your party invite.");
  return "Declined the party invite from " + String.valueOf(inv[2]) + ".";
}""")
# r = removeMember() result; stayMsg / goneMsg go to the remaining members (never to the one who left)
M(ps, r"""
public static void announceLeave(Object[] r, java.util.UUID mu, String stayMsg, String goneMsg) {
  java.util.ArrayList before = (java.util.ArrayList) r[0];
  java.util.ArrayList after = (java.util.ArrayList) r[1];
  boolean gone = ((Boolean) r[2]).booleanValue();
  if (gone) { broadcastTo(after, goneMsg, mu, null); return; }
  broadcastKey(after, stayMsg, mu, null, "party.members", null);
  java.util.UUID oldLead = (java.util.UUID) before.get(0);
  java.util.UUID newLead = (java.util.UUID) after.get(0);
  if (!newLead.equals(oldLead)) broadcastKey(after, "[Party] " + nameOf(newLead) + " is now the party leader.", null, null, "party.members", newLead);
}""")
M(ps, r"""
public static String leave(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  Object[] r = removeMember(mu);
  if (r == null) return "You're not in a party.";
  String n = me.getUsername();
  announceLeave(r, mu, "[Party] " + n + " left the party.", "[Party] " + n + " left. The party has been disbanded.");
  return "You left the party.";
}""")
M(ps, r"""
public static String kick(@PR@ me, java.util.UUID target) {
  if (target == null) return "That player is not in your party.";
  java.util.UUID mu = me.getUuid();
  String tn = nameOf(target);
  Object[] r = kickM(mu, target);
  String code = (String) r[0];
  if ("none".equals(code)) return "You're not in a party.";
  if ("notleader".equals(code)) return "Only the party leader can kick members.";
  if ("self".equals(code)) return "You can't kick yourself - use /party leave or /party disband.";
  if (!"ok".equals(code)) return tn + " is not in your party.";
  java.util.ArrayList after = (java.util.ArrayList) r[2];
  boolean gone = ((Boolean) r[3]).booleanValue();
  tell(target, "[Party] You were kicked from the party by " + me.getUsername() + ".");
  if (gone) return "Kicked " + tn + ". Nobody else is left, so the party is disbanded.";
  // LOCKED 2026-09-25 (Skyy): "X kicked Y from the party." is always shown - party.members never hides it
  broadcastTo(after, "[Party] " + me.getUsername() + " kicked " + tn + " from the party.", mu, null);
  return "Kicked " + tn + " from the party.";
}""")
M(ps, r"""
public static String promote(@PR@ me, java.util.UUID target) {
  if (target == null) return "That player is not in your party.";
  java.util.UUID mu = me.getUuid();
  String tn = nameOf(target);
  String code = promoteM(mu, target);
  if ("none".equals(code)) return "You're not in a party.";
  if ("notleader".equals(code)) return "Only the party leader can promote members.";
  if ("self".equals(code)) return "You are already the party leader.";
  if (!"ok".equals(code)) return tn + " is not in your party.";
  tell(target, "[Party] " + me.getUsername() + " made you the party leader.");
  broadcastKey(listOf(target), "[Party] " + tn + " is now the party leader (promoted by " + me.getUsername() + ").", mu, target, "party.members", null);
  return tn + " is now the party leader.";
}""")
M(ps, r"""
public static String disband(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  Object[] r = disbandM(mu);
  String code = (String) r[0];
  if ("none".equals(code)) return "You're not in a party.";
  if (!"ok".equals(code)) return "Only the party leader can disband the party. Use /party leave to leave it.";
  broadcastTo((java.util.List) r[1], "[Party] " + me.getUsername() + " disbanded the party.", mu, null);
  return "You disbanded the party.";
}""")
M(ps, r"""
public static String listText(@PR@ me) {
  java.util.ArrayList l = listOf(me.getUuid());
  if (l == null) return "You're not in a party. /party invite <player> to start one, or /party to open the party page.";
  StringBuilder sb = new StringBuilder("Party (" + l.size() + "/" + MAX + "): ");
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID u = (java.util.UUID) l.get(i);
    if (i > 0) sb.append(", ");
    sb.append(nameOf(u));
    if (online(u) == null) sb.append(" (offline)");
    if (i == 0) sb.append(" [leader]");
  }
  return sb.toString();
}""")
M(ps, r"""
public static void pruneInvites() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = INVITES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (v == null || ((Long) v[1]).longValue() >= now) continue;
    if (!INVITES.remove(e.getKey(), v)) continue;
    java.util.UUID invitee = (java.util.UUID) e.getKey();
    tell((java.util.UUID) v[0], "[Party] Your party invite to " + nameOf(invitee) + " ran out.");
    tell(invitee, "[Party] The party invite from " + String.valueOf(v[2]) + " ran out.");
  }
}""")
M(ps, r"""
public static void onQuit(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String name = pr.getUsername();
  CLOCK.remove(u);
  Object[] mine = (Object[]) INVITES.remove(u);
  if (mine != null) tell((java.util.UUID) mine[0], "[Party] " + name + " left the game - your party invite was cancelled.");
  java.util.Iterator it = INVITES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (v == null || !u.equals(v[0])) continue;
    if (INVITES.remove(e.getKey(), v)) tell((java.util.UUID) e.getKey(), "[Party] " + name + " left the game - their party invite was cancelled.");
  }
  Object[] r = removeMember(u);
  if (r != null) announceLeave(r, u, "[Party] " + name + " disconnected and left the party.", "[Party] " + name + " disconnected. The party has been disbanded.");
}""")
M(ps, r"""
public static int intProp(java.util.Properties p, String key, int def, int lo, int hi) {
  int v = def;
  try { v = Integer.parseInt(p.getProperty(key, String.valueOf(def)).trim()); } catch (Throwable t) { warn("config.properties: bad " + key + " - using " + def); v = def; }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
# 0.1.5: the same words the config kit accepts for a bool row (true/false, on/off, yes/no, 1/0); anything else = the default + a warning
M(ps, r"""
public static boolean boolProp(java.util.Properties p, String key, boolean def) {
  String v = p.getProperty(key);
  if (v == null) return def;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return false;
  warn("config.properties: bad " + key + " - using " + def);
  return def;
}""")
M(ps, r"""
public static void loadConfig(java.nio.file.Path dir) {
  try {
    java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path f = dir.resolve("config.properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      String txt = DEFAULT_TEXT.replace("\n", System.lineSeparator());
      // tmp + atomic rename (SkyyProfiles / SkyySacks pattern): a crash mid-write never leaves a half-written config behind
      java.nio.file.Path tmp = dir.resolve("config.properties.tmp");
      java.nio.file.Files.write(tmp, txt.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    MAX = intProp(p, "maxSize", 5, 2, 10);
    INVITE_MS = (long) intProp(p, "inviteSeconds", 60, 15, 600) * 1000L;
    // 0.1.5: privacy.staffBypass; an old staffBypass line (the row's earlier, never shipped name) is read only when the new one is absent
    if (p.getProperty("privacy.staffBypass") != null) STAFF_BYPASS = boolProp(p, "privacy.staffBypass", true);
    else STAFF_BYPASS = boolProp(p, "staffBypass", true);
  } catch (Throwable t) {
    warn("could not read config.properties - using maxSize=" + MAX + " inviteSeconds=" + (INVITE_MS / 1000L) + " privacy.staffBypass=" + STAFF_BYPASS + ": " + t);
  }
}""")

# ================= 0.1.4: the admin config kit (research/Server-Setup-Spec.md 4.5; tools/CONFIG-CONTRACT.md) =================
# Row key = file key (the spec 4.5 names), so the file keys never change. Every row is live: every reader of MAX / INVITE_MS /
# STAFF_BYPASS reads the volatile field at click / tick time. No RELOAD routine: on a hand edit (found by /partyadmin reload, the menu's
# Reload file or the kit's next write) the kit writes the fields itself and clamps to the same bounds as PartyStore.loadConfig (intProp
# 2-10 / 15-600; boolProp takes the kit's bool words).
CATS = [("party", "Party"), ("privacy", "Privacy")]
ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding)
    ("maxSize", "Most players in one party", "party", "int", "5", "2", "10", "step=1", "", "live",
     "Lowering it never removes anyone: a bigger party keeps its members and just cannot invite.",
     "field:PartyStore.MAX@config.properties:maxSize"),
    ("inviteSeconds", "Invite time", "party", "int", "60", "15", "600", "step=15", "s", "live",
     "How long a party invite stays open. Invites already sent keep their own time.",
     "field:PartyStore.INVITE_MS*1000@config.properties:inviteSeconds"),
    # 0.1.5: staff bypass for the party.invites switch (Skyy 2026-09-25: block the sender, staff bypass default on). Same key, category,
    # label and help pattern as SkyyEssentials 0.1.5's privacy.staffBypass
    ("privacy.staffBypass", "Staff get through blocked switches", "privacy", "bool", "true", "", "", "", "", "live",
     "Players with skyyparty.bypass (ops included) reach players who switched party invites off.",
     "field:PartyStore.STAFF_BYPASS@config.properties:privacy.staffBypass"),
]
KIT = CFG.emit(pool, PKG, MOD="SkyyParty", TITLE="Party", VERSION=VERSION, NODE="skyyparty.admin", CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyParty/config.properties"], NOTE="Parties live in memory only. Every setting applies at once.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT})
assert KIT.info.get("kit", "1.0") == EXPECTED_KIT, "the emitted config kit is %s, SkyyParty %s pins %s - pick a kit change up on purpose" % (
    KIT.info.get("kit", "1.0"), VERSION, EXPECTED_KIT)
print("config kit %s: %d rows, files %s, KEEP 10" % (KIT.info.get("kit", "1.0"), KIT.info["rows"], ", ".join(KIT.info["files"])))

# ================= PartyFn: bridge "party:fn:members" =================
fn.addInterface(pool.get("java.util.function.Function"))
C(fn, "public PartyFn() { }")
M(fn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o != null) u = java.util.UUID.fromString(o.toString());
    java.util.ArrayList l = @PKG@.PartyStore.listOf(u);
    if (l == null) return new String[0];
    String[] out = new String[l.size()];
    for (int i = 0; i < out.length; i++) out[i] = l.get(i).toString();
    return out;
  } catch (Throwable t) { return new String[0]; }
}""")

# ================= PartyStats: party:stats:<uuid> on the member's OWN world thread (EntityTickingSystem on Player) =================
# AccEffects (SkyyAccessories 0.2+) pattern: store.getComponent for Player / PlayerRef, cb.getComponent for EntityStatMap.
# Throttled by wall clock (1 s per player), so the dt unit does not matter.
F(sts, "public static boolean FAILED_ONCE = false;")
C(sts, "public PartyStats() { super(); }")
M(sts, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(sts, r"""
public static int val(@ESM@ m, int idx, boolean max) {
  if (m == null || idx < 0) return 0;
  @ESV@ v = m.get(idx);
  if (v == null) return 0;
  return max ? Math.round(v.getMax()) : Math.round(v.get());
}""")
M(sts, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    long now = System.currentTimeMillis();
    long[] c = (long[]) @PKG@.PartyStore.CLOCK.get(u);
    if (c == null) { c = new long[] { 0L }; @PKG@.PartyStore.CLOCK.put(u, c); }
    if (now - c[0] < 1000L) return;
    c[0] = now;
    @PKG@.PartyStore.pubName(pr);
    if (@PKG@.PartyStore.listOf(u) == null) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    int hi = @DST@.getHealth();
    int si = @DST@.getStamina();
    int mi = @DST@.getMana();
    String w = "";
    try {
      Object ex = store.getExternalData();
      if (ex instanceof @ES@) {
        @WLD@ wd = ((@ES@) ex).getWorld();
        if (wd != null && wd.getName() != null) w = wd.getName().replace(',', ' ');
      }
    } catch (Throwable t) { w = ""; }
    String s = "" + val(m, hi, false) + "," + val(m, hi, true) + "," + val(m, si, false) + "," + val(m, si, true) + "," + val(m, mi, false) + "," + val(m, mi, true) + "," + w;
    java.util.Map b = @PKG@.PartyStore.bridge();
    String key = "party:stats:" + u.toString();
    b.put(key, s);
    // a leave / kick / disband / disconnect may have run on another thread since the check above: never leave a stale value
    if (@PKG@.PartyStore.listOf(u) == null) b.remove(key);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.PartyStore.warn("party stats tick failed (logged once): " + t); }
  }
}""")

# ================= PartyPage: /party (inline; no periodic updates - Refresh button) =================
F(page, "public String info;")
C(page, r"""
public PartyPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.info = "";
}""")
# SkyySacks 0.7.3 jsonStr, verbatim: one string value out of the page event JSON ("@InviteName": "..."), escapes handled
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
M(page, r"""
public static java.util.UUID parseUuid(String s) {
  try { return java.util.UUID.fromString(s.trim()); } catch (Throwable t) { return null; }
}""")
# "hp,maxHp,stamina,maxStamina,mana,maxMana,worldName" -> the 6 numbers (null when missing / malformed)
M(page, r"""
public static int[] nums(String s) {
  if (s == null) return null;
  String[] p = s.split(",", -1);
  if (p.length < 6) return null;
  int[] out = new int[6];
  try {
    for (int i = 0; i < 6; i++) out[i] = Integer.parseInt(p[i].trim());
  } catch (Throwable t) { return null; }
  return out;
}""")
M(page, r"""
public static String worldPart(String s) {
  if (s == null) return null;
  int c = 0;
  for (int i = 0; i < s.length(); i++) {
    if (s.charAt(i) == ',') {
      c++;
      if (c == 6) return s.substring(i + 1);
    }
  }
  return null;
}""")
M(page, r"""
public static String stats(java.util.UUID u) {
  try {
    Object o = @PKG@.PartyStore.bridge().get("party:stats:" + u.toString());
    return o == null ? null : o.toString();
  } catch (Throwable t) { return null; }
}""")
# friendly place name: SkyyIslands worlds are skyy-island-<uuid> or skyy-island-<uuid>-pN (tools/PROFILES-CONTRACT.md)
M(page, r"""
public static String where(String w, java.util.UUID member, java.util.UUID viewer) {
  if (w == null || w.length() == 0) return "somewhere";
  if (w.startsWith("skyy-island-")) {
    String k = w.substring(12);
    String owner = k.length() >= 36 ? k.substring(0, 36) : k;
    if (owner.equals(viewer.toString())) return "Your island";
    if (owner.equals(member.toString())) return @PKG@.PartyStore.cut(@PKG@.PartyStore.nameOf(member), 14) + "'s island";
    try {
      Object n = @PKG@.PartyStore.bridge().get("party:name:" + owner);
      if (n != null) return @PKG@.PartyStore.cut(n.toString(), 14) + "'s island";
    } catch (Throwable t) { }
    return "An island";
  }
  try {
    @WLD@ d = @UNI@.get().getDefaultWorld();
    if (d != null && w.equals(d.getName())) return "Hub";
  } catch (Throwable t) { }
  return @PKG@.PartyStore.cut(w, 20);
}""")
# 0.1.7: SkyyEssentials' tpa bridge (SkyyEssentials 0.1.8: ess:fn:tpa / ess:fn:tpaccept / ess:fn:tpaPending, java.util.function.Function,
# plain java types). Only through the bridge map - no dependency. The calls run on the clicking player's world thread (the page's
# handleDataEvent), the thread a typed /tpa runs on; SkyyEssentials' functions are thread-safe either way.
M(page, r"""
public static boolean essOn() {
  try {
    java.util.Map b = @PKG@.PartyStore.bridge();
    return b.get("ess:fn:tpa") instanceof java.util.function.Function && b.get("ess:fn:tpaccept") instanceof java.util.function.Function
        && b.get("ess:fn:tpaPending") instanceof java.util.function.Function;
  } catch (Throwable t) { return false; }
}""")
# the newest request TO me: { String fromUuid, String fromName, Boolean here } or null
M(page, r"""
public static Object[] tpaPending(java.util.UUID me) {
  try {
    Object f = @PKG@.PartyStore.bridge().get("ess:fn:tpaPending");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(me);
    if (r instanceof Object[] && ((Object[]) r).length >= 3 && parseUuid(String.valueOf(((Object[]) r)[0])) != null) return (Object[]) r;
  } catch (Throwable t) { @PKG@.PartyStore.warn("ess:fn:tpaPending failed: " + t); }
  return null;
}""")
# SkyyEssentials' answer as the page line: its "[TPA] " chat tag dropped
M(page, r"""
public static String tpaLine(Object r) {
  if (r == null) return "That didn't work - try /tpa <name> in chat.";
  String s = r.toString();
  if (s.startsWith("[TPA] ")) s = s.substring(6);
  return s.length() == 0 ? "That didn't work - try /tpa <name> in chat." : s;
}""")
M(page, r"""
public static String tpaCall(java.util.UUID me, java.util.UUID target) {
  Object f = null;
  try { f = @PKG@.PartyStore.bridge().get("ess:fn:tpa"); } catch (Throwable t) { }
  if (!(f instanceof java.util.function.Function)) return "TPA needs SkyyEssentials, which is not on this server.";
  try { return tpaLine(((java.util.function.Function) f).apply(new Object[] { me, target, Boolean.FALSE })); }
  catch (Throwable t) { @PKG@.PartyStore.warn("ess:fn:tpa failed: " + t); return "That didn't work - try /tpa <name> in chat."; }
}""")
M(page, r"""
public static String tpaAccept(java.util.UUID me, java.util.UUID from) {
  Object f = null;
  try { f = @PKG@.PartyStore.bridge().get("ess:fn:tpaccept"); } catch (Throwable t) { }
  if (!(f instanceof java.util.function.Function)) return "TPA needs SkyyEssentials, which is not on this server.";
  if (from == null) return "That request is gone - press Refresh.";
  try { return tpaLine(((java.util.function.Function) f).apply(new Object[] { me, from })); }
  catch (Throwable t) { @PKG@.PartyStore.warn("ess:fn:tpaccept failed: " + t); return "That didn't work - try /tpaccept in chat."; }
}""")
# 0.1.6: the filled width of one stat bar (the 0.1.5 statCol maths: cur clamped to 0..max, 0 when max <= 0) - the bar itself is the kit's
# bar() in party_page() below (PARTY_BAR_W wide)
PARTY_BAR_W, PARTY_BAR_H = 160, 8
M(page, r"""
public static int fillPx(int cur, int max) {
  if (max <= 0) return 0;
  int c = cur < 0 ? 0 : (cur > max ? max : cur);
  return (int) (((long) """ + str(PARTY_BAR_W) + r""" * (long) c) / (long) max);
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.PartyStore.warn("could not close the party page: " + t); }
}""")
# ================= 0.1.6: PartyPage's look from the vanilla UI kit (tools/skyyui.py; research/Vanilla-UI-Style-Guide.md) =================
# party_page() builds every piece of the page with kit calls (every value proven by SUI.verify() above), runs each page state through
# SUI.check_page and an exact height budget, and returns the Java of each piece (the kit's emitters). A piece = what one Java branch of
# build() appends. build() below keeps 0.1.5's logic, texts and its 10 event bindings verbatim; only the markup comes from here.
# SUI.J("expr") = a local of build() (its prelude declares every one: in, lead, l, max, inf, fromClick, pend, pendText, invHint, gapR,
# and per row i, self, isLead, nm, stT, stF, on, wh).
TPA_W = 64                            # 0.1.7: the TPA row action ("TPA" at 14 px bold uppercase ~29 px + 2 x 16 px padding)
PARTY_W, PARTY_H = 1400, 840          # plain window (a list page); inner 1366 x 768 (38 px title bar + 2 x 17 px padding)
PARTY_PREFIX = "SkyyP"                # every element id starts with it (the 0.1.5 ids already did)
ROW_SLACK = 10                        # review fix: px a member row keeps free beyond the 12 px scrollbar reserve (Kick never clips)
# data colours: the fills of the Health / Stamina / Mana bars (content, not chrome - research/Skyy-UI-Inventory.md section 3); the bar
# track is the kit's vanilla progress track
UI_DATA_COLORS = {"health": "#d04848", "stamina": "#e0b040", "mana": "#4a8ae0"}
# every element id 0.1.5's page built (row ids with <i> = 0) - all kept; party_page() asserts that some page state still creates each one
PARTY_IDS_015 = ['SkyyParty', 'SkyyPTitle', 'SkyyPInfo', 'SkyyPPending', 'SkyyPPendTxt', 'SkyyPAccept', 'SkyyPDecline', 'SkyyPHead',
                 'SkyyPRow0', 'SkyyPNC0', 'SkyyPName0', 'SkyyPRole0', 'SkyyPHp0C', 'SkyyPHp0T', 'SkyyPHp0B', 'SkyyPSt0C', 'SkyyPSt0T',
                 'SkyyPSt0B', 'SkyyPMp0C', 'SkyyPMp0T', 'SkyyPMp0B', 'SkyyPWC0', 'SkyyPOn0', 'SkyyPWh0', 'SkyyPAC0', 'SkyyPPro0',
                 'SkyyPKick0', 'SkyyPEmpty', 'SkyyPEmptyA', 'SkyyPEmptyB', 'SkyyPEmptyC', 'SkyyPInvRow', 'SkyyPInvLbl', 'SkyyPInvBox',
                 'SkyyPInvName', 'SkyyPInvGo', 'SkyyPInvHint', 'SkyyPActs', 'SkyyPLeave', 'SkyyPDisband', 'SkyyPRefresh', 'SkyyPClose',
                 'SkyyPFootA', 'SkyyPFootB']


def party_page():
    """(shell, pieces, java, states, gapR): PartyPage's markup from the kit. pieces = {name: Appends}, java = {name: Java statements},
    states = {state: [piece names in build() order]}; gapR = the Java expression of the Refresh button's left margin."""
    J, C = SUI.J, SUI.COLOR
    sh = SUI.page_shell("SkyyPF", PARTY_W, PARTY_H, kind="plain", body_id="SkyyParty", title_id="SkyyPTitle",
                        title=J('in ? ("Party   " + l.size() + " / " + max + " players") : "Party"', "Party   2 / 5 players"))
    body, W = sh.body, sh.inner_w
    pc = {}

    def piece(name):
        pc[name] = SUI.Appends()
        return pc[name]

    # ---- frame: the root, the plain title bar (b.set of #SkyyPTitle: 0.1.5's text), the body #SkyyParty
    shell = piece("shell")
    shell.extend(sh.appends)
    shell.sets.extend(sh.sets)
    # ---- #SkyyPInfo: a click result (PartyStore's own chat lines - no +/- marks) in the vanilla info blue, the default hint in the
    # vanilla label grey; centred, bold, wraps to two lines
    info_h, info_gap = 44, 6
    info = piece("info")
    info.append((body, SUI.label("SkyyPInfo", "", "default", h=info_h, bold=True, align="Center", wrap=True, anchor={"bottom": info_gap},
                                 col=J('fromClick ? "%s" : "%s"' % (C["info"], C["text"]), C["info"]))))
    info.sets.append(("SkyyPInfo", "Text", J("inf", "You lead this party")))
    # ---- the fixed parts under the content area: invite row, the two captions, separator, footer buttons
    inv_top, foot_top, cap_h = 12, 8, 25
    sep_h = 1 + 2 * SUI.SEP_MARGIN
    fixed = [info_h + info_gap, inv_top + SUI.BTN_H, foot_top + 2 * cap_h, sep_h, SUI.BTN_H]
    area = sh.inner_h - sum(fixed)                 # the member list (head + well) or the help well (+ the pending invite)
    # ---- pending invite: the kit's one-row confirm view (the 0.1.5 ids); the question is b.set (it holds the name and the seconds)
    pend = piece("pend")
    cv = SUI.confirm_view(body, "SkyyPPend", W, yes_text="Accept", no_text="Decline", compact=True, top=0,
                          ids={"box": "SkyyPPending", "question": "SkyyPPendTxt", "yes": "SkyyPAccept", "no": "SkyyPDecline"})
    pend.extend(cv)
    pend.sets.append(("SkyyPPendTxt", "Text", J("pendText", "Steve invited you to their party  (42 s left)")))
    # ---- members: section-label column heads over a scrolling list on the vanilla well
    head_h = 30
    list_h = area - head_h
    row_h, row_gap, row_pad, mark_w = SUI.ROW_H_READABLE, SUI.ROW_GAP, 8, 4 + 8
    # review fix (2026-09-29): stat 185 -> 175 (the 160 px bars + a 15 px gap; "Health  1000 / 1000" at 16 px is ~150 px) and
    # Where 280 -> 300 ("<14-char name>...'s island (with you)" at 15 px), leaving ROW_SLACK px beyond the 12 px scrollbar reserve
    # 0.1.7: room for the TPA row action - Promote 120 -> 104, stats 175 -> 165, Where 300 -> 281
    name_w, stat_w, where_w = 260, 165, 281
    pro_w, kick_w, act_btn_h = 104, SUI.ROW_ACTION_W, SUI.ROW_H      # row actions: the vanilla 42 px WorldEventListRow action height
    tpa_w = TPA_W
    # the kit's small-button rule: the 14 px bold UPPERCASE label + 2 x 16 px padding fits without shrinking
    for _t, _w in (("Promote", pro_w), ("Kick", kick_w), ("TPA", tpa_w)):
        assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= _w, "row action %s does not fit %d px" % (_t, _w)
    assert SUI.text_width("Accept TPA", 17, True, upper=True) + 2 * SUI.BTN_PAD <= SUI.BTN_MIN_W
    assert SUI.text_width("Stamina  1000 / 1000", 16) <= stat_w and PARTY_BAR_W <= stat_w
    act_w = 4 + pro_w + 4 + kick_w + 4 + tpa_w
    row_inner = W - 2 * SUI.WELL_LIST_PAD - (SUI.SCROLL_SIZE + SUI.SCROLL_SPACING) - 2 * row_pad
    slack = SUI.fit([mark_w, name_w, 3 * stat_w, where_w, act_w], row_inner, "member row columns")
    assert slack >= ROW_SLACK, "member row columns leave %d px, want >= %d (scrollbar width not yet seen in game)" % (slack, ROW_SLACK)
    lst = piece("list")
    lst.append((body, SUI.group("SkyyPHead", "Left", h=head_h, pad={"left": SUI.WELL_LIST_PAD + row_pad + mark_w})))
    for text, w in (("Member", name_w), ("Health", stat_w), ("Stamina", stat_w), ("Mana", stat_w), ("Where", where_w)):
        lst.append(("SkyyPHead", SUI.label(None, text, "section", w=w, h=head_h)))
    lst.append((body, SUI.scroll_list("SkyyPList", h=list_h, well=True)))
    # one static row per member (the WorldEventListRow panel, 56 + 3); the viewer's own row carries the 4 px vanilla status bar
    row = piece("row")
    i = J("i")
    rid = "SkyyPRow" + i
    row.append(("SkyyPList", SUI.panel(rid, "row", h=row_h, layout="Left", pad={"left": row_pad, "right": row_pad},
                                       anchor={"bottom": row_gap})))
    bar_on = SUI.group(None, None, w=4, h=row_h, anchor={"right": 8}, extra="Background: " + C["selected"])
    bar_off = SUI.group(None, None, w=4, h=row_h, anchor={"right": 8})
    row.append((rid, SUI.choose(J("self"), bar_on, bar_off)))
    name_h, sub_h = 26, 20
    SUI.fit([name_h, sub_h], row_h, "name column")
    row.append((rid, SUI.group("SkyyPNC" + i, "Top", w=name_w, h=row_h, pad={"top": (row_h - name_h - sub_h) // 2})))
    row.append(("SkyyPNC" + i, SUI.label("SkyyPName" + i, "", "rowName", h=name_h)))
    # review fix: the leader's role in the row's own name colour (vanilla WorldEventListRow #Label #d6e4ee), not the gallery-only gold
    row.append(("SkyyPNC" + i, SUI.label("SkyyPRole" + i, "", "rowSub", h=sub_h,
                                         col=J('isLead ? "%s" : "%s"' % (C["rowName"], C["rowSub"]), C["rowName"]))))
    row.sets.append(("SkyyPName" + i, "Text", J("nm", "Steve  (you)")))
    row.sets.append(("SkyyPRole" + i, "Text", J('isLead ? "* Party leader" : "Member"', "Member")))
    stat_h = 26
    col_h = stat_h + 4 + PARTY_BAR_H
    SUI.fit([col_h], row_h, "stat column")
    for k, (sid, key) in enumerate((("SkyyPHp", "health"), ("SkyyPSt", "stamina"), ("SkyyPMp", "mana"))):
        cid = sid + i
        row.append((rid, SUI.group(cid + "C", "Top", w=stat_w, h=row_h, pad={"top": (row_h - col_h) // 2})))
        row.append((cid + "C", SUI.label(cid + "T", "", "propValue", h=stat_h, wrap=False)))
        # review fix: the 0.1.5 statCol structure (the deployed pattern, as Collections / Guilds / Skills): the track #<id>B (the vanilla
        # progress track colour, LayoutMode Left) always, its fill Group (the stat's data colour, no id) appended by build() ONLY when
        # stF[k] > 0 (pieces fill0 / fill1 / fill2) - never a 0 px wide Group and no redundant full-width track-coloured fill.
        # Composed from kit calls because SUI.bar() always emits its fill child (KIT-GAP: a stat_bar that can omit it).
        row.append((cid + "C", SUI.group(cid + "B", "Left", w=PARTY_BAR_W, h=PARTY_BAR_H, anchor={"top": 4},
                                         extra="Background: " + SUI.color("progressTrack"))))
        piece("fill%d" % k).append((cid + "B", SUI.group(None, None, w=J("stF[%d]" % k, "80"), h=PARTY_BAR_H,
                                                          extra="Background: " + SUI.color(UI_DATA_COLORS[key]))))
        row.sets.append((cid + "T", "Text", J("stT[%d]" % k, "Health  18 / 20")))
    row.append((rid, SUI.group("SkyyPWC" + i, "Top", w=where_w, h=row_h, pad={"top": (row_h - name_h - sub_h) // 2})))
    row.append(("SkyyPWC" + i, SUI.label("SkyyPOn" + i, "", "bold", h=name_h,
                                         col=J('on ? "%s" : "%s"' % (C["success"], C["disabled"]), C["success"]))))
    row.append(("SkyyPWC" + i, SUI.label("SkyyPWh" + i, "", "rowSub", h=sub_h)))
    row.sets.append(("SkyyPOn" + i, "Text", J('on ? "Online" : "Offline"', "Online")))
    row.sets.append(("SkyyPWh" + i, "Text", J("wh", "Hub")))
    # the row's action column (vanilla #ActionA: small buttons, left 4) - 0.1.7: built for every row that has an action: the leader's
    # Promote + Kick on the OTHER members' rows, and the TPA button (everyone, on another ONLINE member's row, with SkyyEssentials)
    piece("actcol").append((rid, SUI.group("SkyyPAC" + i, "Left", w=act_w, h=row_h, pad={"top": (row_h - act_btn_h) // 2})))
    acts = piece("rowacts")
    acts.append(("SkyyPAC" + i, SUI.row_action("SkyyPPro" + i, "Promote", "secondary", w=pro_w, h=act_btn_h)))
    acts.append(("SkyyPAC" + i, SUI.row_action("SkyyPKick" + i, "Kick", "destructive", w=kick_w, h=act_btn_h)))
    piece("tpabtn").append(("SkyyPAC" + i, SUI.row_action("SkyyPTpa" + i, "TPA", "secondary", w=tpa_w, h=act_btn_h)))
    # ---- not in a party: the help text in the same well (below the pending invite when there is one)
    # review fix: the empty state is centred in the well (vertically by a computed top padding - no LayoutMode Middle / FlexWeight -
    # and each line HorizontalAlignment Center), the way vanilla empty-state lines sit (TriggerVolumeInspectorPage), instead of three
    # short lines in the top-left corner of a 1366 x 543 well
    help_gap, help_hs = 8, [34, 28, 28]
    help_pend = area - cv.h - help_gap
    SUI.fit(help_hs, help_pend, "help well")
    top_free, top_pend = (area - sum(help_hs)) // 2, (help_pend - sum(help_hs)) // 2
    emp = piece("empty")
    emp.append((body, SUI.panel("SkyyPEmpty", "well", h=J("pend ? %d : %d" % (help_pend, area), str(area)),
                                pad={"horizontal": 18, "top": J("pend ? %d : %d" % (top_pend, top_free), str(top_free))},
                                anchor={"top": J("pend ? %d : 0" % help_gap, "0")})))
    # review fix: #SkyyPEmptyA keeps the 0.1.5 path (empty inline Text + b.set), like every other label text of the deployed pages
    emp.append(("SkyyPEmpty", SUI.label("SkyyPEmptyA", "", "heading", h=help_hs[0], wrap=False, align="Center")))
    emp.sets.append(("SkyyPEmptyA", "Text", "Play together - start a party"))
    emp.text("SkyyPEmpty", "SkyyPEmptyB", "1. Type your friend's name in the box below and press Enter or Invite.", "default",
             h=help_hs[1], align="Center")
    emp.text("SkyyPEmpty", "SkyyPEmptyC", "2. They type /party accept in chat, or open /party and click Accept.", "default",
             h=help_hs[2], align="Center")
    # ---- invite row: label, the vanilla text field (Enter or the button), Invite (Primary: the row's action), the hint caption
    lbl_w, field_w, field_gap, go_w, go_gap = 190, 380, 12, SUI.BTN_MIN_W, 16
    hint_w = W - (lbl_w + field_w + field_gap + go_w + go_gap)
    SUI.fit([lbl_w, field_w, field_gap, go_w, go_gap, hint_w], W, "invite row")
    invp = piece("invite")
    invp.append((body, SUI.group("SkyyPInvRow", "Left", h=SUI.BTN_H, anchor={"top": inv_top})))
    invp.append(("SkyyPInvRow", SUI.label("SkyyPInvLbl", "", "bold", w=lbl_w, h=SUI.BTN_H)))     # review fix: b.set, as 0.1.5
    invp.sets.append(("SkyyPInvLbl", "Text", "Invite a player"))
    invp.append(("SkyyPInvRow", SUI.text_field("SkyyPInvBox", "SkyyPInvName", w=field_w, placeholder="Player name - press Enter",
                                               max_length=32, anchor={"top": (SUI.BTN_H - SUI.FIELD_H) // 2, "right": field_gap})))
    invp.append(("SkyyPInvRow", SUI.button("SkyyPInvGo", "Invite", "primary", w=go_w, anchor={"right": go_gap})))
    invp.append(("SkyyPInvRow", SUI.label("SkyyPInvHint", "", "caption", w=hint_w, h=SUI.BTN_H)))
    invp.sets.append(("SkyyPInvHint", "Text", J("invHint", "they must be online - the invite lasts 60 s")))
    # ---- footer: 0.1.5's two chat hint lines (captions), the content separator, the button row
    foot = piece("foot")
    foot.text(body, "SkyyPFootA", "Party chat: /pc <message>   -   Health, Stamina and Mana update when you press Refresh", "caption",
              h=cap_h, align="Center", anchor={"top": foot_top})
    # review fix: #SkyyPFootB keeps the 0.1.5 path (empty inline Text + b.set): < > / in inline text are proven on buttons only
    foot.append((body, SUI.label("SkyyPFootB", "", "caption", h=cap_h, align="Center")))
    foot.sets.append(("SkyyPFootB", "Text", "/party invite <player>  accept  decline  leave  list  kick <player>  promote <player>  disband"))
    foot.append((body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    foot.append((body, SUI.group("SkyyPActs", "Left", h=SUI.BTN_H)))
    leave_w, dis_w, btn_gap = 200, 200, 6
    piece("leave").append(("SkyyPActs", SUI.button("SkyyPLeave", "Leave party", "destructive", w=leave_w, anchor={"right": btn_gap})))
    piece("disband").append(("SkyyPActs", SUI.button("SkyyPDisband", "Disband party", "destructive", w=dis_w, anchor={"right": btn_gap})))
    # 0.1.7: Accept TPA (Primary: the page's one pending action) while a teleport request to the viewer is waiting
    acc_w = SUI.BTN_MIN_W
    piece("tpacc").append(("SkyyPActs", SUI.button("SkyyPTpAcc", "Accept TPA", "primary", w=acc_w, anchor={"right": btn_gap})))
    right0 = W - 2 * SUI.BTN_MIN_W - btn_gap            # Refresh's left margin with no Leave / Disband / Accept TPA in front of it
    SUI.fit([leave_w + btn_gap, dis_w + btn_gap, acc_w + btn_gap, SUI.BTN_MIN_W, btn_gap, SUI.BTN_MIN_W], W, "footer buttons")
    gap_r = "%d - (in ? %d : 0) - (lead ? %d : 0) - (tpaP ? %d : 0)" % (right0, leave_w + btn_gap, dis_w + btn_gap, acc_w + btn_gap)
    close = piece("close")
    close.append(("SkyyPActs", SUI.button("SkyyPRefresh", "Refresh", "secondary", w=SUI.BTN_MIN_W, anchor={"left": J("gapR", str(right0))})))
    close.append(("SkyyPActs", SUI.button("SkyyPClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel", anchor={"left": btn_gap})))
    # ---- every page state: check_page (ids, prefix, parents, duplicates, markup rules, b.set targets) + a body filled exactly
    fills = ["fill0", "fill1", "fill2"]            # build() appends each only when that bar has something to show
    states = {"not in a party": (["shell", "info", "empty", "invite", "foot", "close"], [area]),
              "invite pending": (["shell", "info", "pend", "empty", "invite", "foot", "close"], [cv.h, help_gap + help_pend]),
              "member": (["shell", "info", "list", "row"] + fills + ["invite", "foot", "leave", "close"], [head_h, list_h]),
              "member, no stats yet": (["shell", "info", "list", "row", "invite", "foot", "leave", "close"], [head_h, list_h]),
              "leader": (["shell", "info", "list", "row"] + fills + ["actcol", "rowacts", "invite", "foot", "leave", "disband", "close"],
                         [head_h, list_h]),
              # 0.1.7: the TPA states
              "member, TPA": (["shell", "info", "list", "row"] + fills + ["actcol", "tpabtn", "invite", "foot", "leave", "close"],
                              [head_h, list_h]),
              "leader, TPA + Accept TPA": (["shell", "info", "list", "row"] + fills + ["actcol", "rowacts", "tpabtn", "invite", "foot",
                                           "leave", "disband", "tpacc", "close"], [head_h, list_h]),
              "not in a party, Accept TPA": (["shell", "info", "empty", "invite", "foot", "tpacc", "close"], [area])}
    made = set()
    for name in states:
        names, var = states[name]
        ap = SUI.Appends()
        for nm in names:
            ap.extend(pc[nm])
        SUI.check_page(ap, PARTY_PREFIX)
        left = sh.fit(fixed + var, "party page body (%s)" % name)
        assert left == 0, "the party page body (%s) must be filled exactly (no FlexWeight filler): %d px left" % (name, left)
        for _p, mk in ap:
            for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,)):
                made |= set(re.findall(r"#([A-Za-z0-9]+)\s*\{", SUI.render(v)))
    missing = [x for x in PARTY_IDS_015 + ["SkyyPTpa0", "SkyyPTpAcc"] if x not in made]
    assert not missing, "0.1.6 dropped 0.1.5 element ids: %s" % missing
    java = dict((nm, "\n".join("  " + ln for ln in pc[nm].java("b").split("\n"))) for nm in pc)
    return sh, pc, java, dict((k, states[k][0]) for k in states), gap_r


PARTY_SH, PARTY_PIECES, PARTY_JAVA, PARTY_STATES, PARTY_GAPR = party_page()
print("party page (%s): %d states checked, %d pieces, %d appends" % (KIT_ID, len(PARTY_STATES), len(PARTY_PIECES),
                                                                      sum(len(p) for p in PARTY_PIECES.values())))
# review fix (deploy gate, 2026-09-29): the whole page is the kit's "base" look, not yet seen in game; a parse error disconnects the
# client the moment /party or the Menu tile opens it. Keep tools/deploy_set.py SET at ("SkyyParty", "0.1.5") until Skyy has opened
# probe pages base1 / base2 / base3 without a disconnect and "base" is in skyyui.PROBED.
if "base" not in SUI.PROBED:
    print("DEPLOY GATE: SkyyParty %s uses the unseen kit base look - keep the SET pin at 0.1.5 until probe pages base1-3 pass in game"
          % VERSION)
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID me = this.playerRef.getUuid();
  @PKG@.PartyStore.pubName(this.playerRef);
  java.util.ArrayList l = @PKG@.PartyStore.listOf(me);
  boolean in = l != null;
  boolean lead = in && me.equals(l.get(0));
  int max = @PKG@.PartyStore.MAX;
  String inf = this.info;
  boolean fromClick = inf != null && inf.length() > 0;
  // 0.1.7: SkyyEssentials' tpa bridge (TPA / Accept TPA buttons); the waiting request is read now - at open and at every click (rebuild)
  boolean ess = essOn();
  Object[] tp = null;
  if (ess) tp = tpaPending(me);
  boolean tpaP = tp != null;
  String tpaFrom = "";
  if (tpaP) tpaFrom = String.valueOf(tp[0]);
  if (!fromClick) {
    // 0.1.5: a player with party invites OFF learns why nobody can invite them (text only, the existing label)
    if (!in) inf = @PKG@.PartyStore.notifyOn(me, "party.invites") ? "You're not in a party yet." : "You're not in a party yet. Your party invites are OFF in /settings - other players can't invite you.";
    else if (lead) inf = ess ? "You lead this party. Promote, Kick or TPA a member on their row." : "You lead this party. Promote or Kick a member on their row.";
    else inf = "Party leader: " + @PKG@.PartyStore.nameOf((java.util.UUID) l.get(0)) + ". Party chat: /pc <message>";
    if (!ess && in && l.size() > 1) inf = inf + "  (TPA buttons need SkyyEssentials.)";
    if (tpaP) inf = @PKG@.PartyStore.cut(String.valueOf(tp[1]), 18) + (Boolean.TRUE.equals(tp[2]) ? " wants you to teleport to them" : " wants to teleport to you") + " - press Accept TPA.";
  }
  // pending invite (only when not in a party)
  Object[] inv = (Object[]) @PKG@.PartyStore.INVITES.get(me);
  long left = 0L;
  if (inv != null) left = (((Long) inv[1]).longValue() - System.currentTimeMillis() + 999L) / 1000L;
  boolean pend = !in && inv != null && left > 0L;
  String pendText = pend ? (String.valueOf(inv[2]) + " invited you to their party  (" + left + " s left)") : "";
  String invHint = "   they must be online - the invite lasts " + @PKG@.PartyStore.inviteSecs() + " s";
  int gapR = """ + PARTY_GAPR + r""";

  // ---- frame (the plain vanilla window; the 0.1.5 root #SkyyParty is its body) + the info line
""" + PARTY_JAVA["shell"] + "\n" + PARTY_JAVA["info"] + r"""

  // ---- pending invite (only when not in a party)
  if (pend) {
""" + PARTY_JAVA["pend"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyPAccept", @EVD@.of("a", "accept"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPDecline", @EVD@.of("a", "decline"));
  }

  // ---- members
  if (in) {
    int n = l.size();
""" + PARTY_JAVA["list"] + r"""
    String myWorld = worldPart(stats(me));
    for (int i = 0; i < n; i++) {
      java.util.UUID u = (java.util.UUID) l.get(i);
      boolean self = u.equals(me);
      boolean isLead = i == 0;
      String nm = @PKG@.PartyStore.cut(@PKG@.PartyStore.nameOf(u), 18) + (self ? "  (you)" : "");
      // health / stamina / mana from the member's own world thread (party:stats)
      String s = stats(u);
      int[] v = nums(s);
      String[] stT = new String[3];
      int[] stF = new int[3];
      if (v == null) {
        stT[0] = "Health  ...";
        stT[1] = "Stamina  ...";
        stT[2] = "Mana  ...";
      } else {
        stT[0] = "Health  " + v[0] + " / " + v[1];
        stT[1] = "Stamina  " + v[2] + " / " + v[3];
        stT[2] = v[5] > 0 ? ("Mana  " + v[4] + " / " + v[5]) : "Mana  none";
        stF[0] = fillPx(v[0], v[1]);
        stF[1] = fillPx(v[2], v[3]);
        stF[2] = fillPx(v[4], v[5]);
      }
      // online + where
      boolean on = @PKG@.PartyStore.online(u) != null;
      String w = worldPart(s);
      String wh = on ? where(w, u, me) : "";
      if (on && !self && w != null && w.length() > 0 && w.equals(myWorld)) wh = wh + " (with you)";
""" + PARTY_JAVA["row"] + r"""
      // each bar's fill only when there is something to show (the 0.1.5 statCol rule: never a 0 px wide Group)
      if (stF[0] > 0) {
""" + PARTY_JAVA["fill0"] + r"""
      }
      if (stF[1] > 0) {
""" + PARTY_JAVA["fill1"] + r"""
      }
      if (stF[2] > 0) {
""" + PARTY_JAVA["fill2"] + r"""
      }
      // the action column: leader-only Promote / Kick on the OTHER members' rows; 0.1.7 TPA on another ONLINE member's row (SkyyEssentials)
      boolean tpaBtn = ess && !self && on;
      if ((lead && !self) || tpaBtn) {
""" + PARTY_JAVA["actcol"] + r"""
      }
      if (lead && !self) {
""" + PARTY_JAVA["rowacts"] + r"""
        ev.addEventBinding(@BT@.Activating, "#SkyyPPro" + i, @EVD@.of("a", "promote:" + u.toString()));
        ev.addEventBinding(@BT@.Activating, "#SkyyPKick" + i, @EVD@.of("a", "kick:" + u.toString()));
      }
      if (tpaBtn) {
""" + PARTY_JAVA["tpabtn"] + r"""
        ev.addEventBinding(@BT@.Activating, "#SkyyPTpa" + i, @EVD@.of("a", "tpa:" + u.toString()));
      }
    }
  } else {
""" + PARTY_JAVA["empty"] + r"""
  }

  // ---- invite row: SkyySacks 0.7.3 search TextField pattern (Enter = Validating without lock, or the button)
""" + PARTY_JAVA["invite"] + r"""
  ev.addEventBinding(@BT@.Validating, "#SkyyPInvName", @EVD@.of("a", "invite").append("@InviteName", "#SkyyPInvName.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyPInvGo", @EVD@.of("a", "invite").append("@InviteName", "#SkyyPInvName.Value"));

  // ---- footer: the chat hint captions, the separator, the actions (Leave / Disband left, Refresh + Close right)
""" + PARTY_JAVA["foot"] + r"""
  if (in) {
""" + PARTY_JAVA["leave"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyPLeave", @EVD@.of("a", "leave"));
  }
  if (lead) {
""" + PARTY_JAVA["disband"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyPDisband", @EVD@.of("a", "disband"));
  }
  if (tpaP) {
""" + PARTY_JAVA["tpacc"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyPTpAcc", @EVD@.of("a", "tpaccept:" + tpaFrom));
  }
""" + PARTY_JAVA["close"] + r"""
  ev.addEventBinding(@BT@.Activating, "#SkyyPRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyPClose", @EVD@.of("a", "close"));
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    @PR@ me = this.playerRef;
    // only the invite bindings carry "@InviteName" (the typed text) - handled before any action match, so a typed word can
    // never be mistaken for a button payload
    if (data.indexOf("\"@InviteName\"") >= 0) {
      String nm = @PKG@.PartyStore.cleanName(jsonStr(data, "@InviteName"));
      if (nm.length() == 0) this.info = "Type a player's name in the box first, then press Enter or Invite.";
      else {
        @PR@ t = @PKG@.PartyStore.findOnline(nm);
        this.info = t == null ? ("Nobody called " + nm + " is online right now.") : @PKG@.PartyStore.invite(me, t);
      }
      rebuild();
      return;
    }
    String a = jsonStr(data, "a");
    if (a.equals("close")) { closePage(ref, st); return; }
    if (a.equals("accept")) this.info = @PKG@.PartyStore.accept(me);
    else if (a.equals("decline")) this.info = @PKG@.PartyStore.decline(me);
    else if (a.equals("leave")) this.info = @PKG@.PartyStore.leave(me);
    else if (a.equals("disband")) this.info = @PKG@.PartyStore.disband(me);
    else if (a.equals("refresh")) this.info = "";
    else if (a.startsWith("kick:")) this.info = @PKG@.PartyStore.kick(me, parseUuid(a.substring(5)));
    else if (a.startsWith("promote:")) this.info = @PKG@.PartyStore.promote(me, parseUuid(a.substring(8)));
    // 0.1.7: the TPA buttons - SkyyEssentials runs its own /tpa and /tpaccept bodies (the bridge); its answer is the page line
    else if (a.startsWith("tpa:")) this.info = tpaCall(me.getUuid(), parseUuid(a.substring(4)));
    else if (a.startsWith("tpaccept:")) this.info = tpaAccept(me.getUuid(), parseUuid(a.substring(9)));
    // 0.1.7: every click is answered (a click that sends nothing leaves the client on "Loading...") - an unknown payload rebuilds too
    else this.info = "";
    rebuild();
  } catch (Throwable t) {
    @PKG@.PartyStore.warn("party page event failed: " + t);
    // 0.1.7: still answer the click
    try { this.info = "Something went wrong - try again."; rebuild(); } catch (Throwable t2) { }
  }
}""")

# ================= commands (every one: Adventurer group; required args only) =================
F(inv, "public @RA@ targetArg;")
C(inv, r"""
public InviteCmd() {
  super("invite", "Invite a player to your party");
  @ADV@
  this.targetArg = withRequiredArg("player", "Player to invite", @ATY@.PLAYER_REF);
}""")
M(inv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party invite <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.invite(pr, (@PR@) t)));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("invite failed: " + t2); pr.sendMessage(@MSG@.raw("Invite failed.")); }
}""")

C(acc, 'public AcceptCmd() { super("accept", "Accept a party invite"); @ADV@ }')
M(acc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.accept(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("accept failed: " + t2); pr.sendMessage(@MSG@.raw("Accept failed.")); }
}""")

C(dec, 'public DeclineCmd() { super("decline", "Decline a party invite"); @ADV@ }')
M(dec, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.decline(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("decline failed: " + t2); }
}""")

C(lev, 'public LeaveCmd() { super("leave", "Leave your party"); @ADV@ }')
M(lev, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.leave(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("leave failed: " + t2); }
}""")

C(lst, 'public ListCmd() { super("list", "List party members"); @ADV@ }')
M(lst, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.listText(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("list failed: " + t2); }
}""")

F(kck, "public @RA@ targetArg;")
C(kck, r"""
public KickCmd() {
  super("kick", "Kick a member from your party (leader only)");
  @ADV@
  this.targetArg = withRequiredArg("player", "Party member to kick", @ATY@.PLAYER_REF);
}""")
M(kck, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party kick <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.kick(pr, ((@PR@) t).getUuid())));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("kick failed: " + t2); pr.sendMessage(@MSG@.raw("Kick failed.")); }
}""")

F(pro, "public @RA@ targetArg;")
C(pro, r"""
public PromoteCmd() {
  super("promote", "Make a member the party leader (leader only)");
  @ADV@
  this.targetArg = withRequiredArg("player", "Party member to promote", @ATY@.PLAYER_REF);
}""")
M(pro, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party promote <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.promote(pr, ((@PR@) t).getUuid())));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("promote failed: " + t2); pr.sendMessage(@MSG@.raw("Promote failed.")); }
}""")

C(dis, 'public DisbandCmd() { super("disband", "Disband your party (leader only)"); @ADV@ }')
M(dis, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.disband(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("disband failed: " + t2); }
}""")

# /pc - unchanged behaviour (GREEDY_STRING; everyone in the party incl. the sender sees "[Party] name: msg")
F(pc, "public @RA@ msgArg;")
C(pc, r"""
public PartyChatCmd() {
  super("pc", "Party chat");
  @ADV@
  this.msgArg = withRequiredArg("message", "Message to your party", @ATY@.GREEDY_STRING);
}""")
M(pc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  Object m = ctx.get(this.msgArg);
  if (m == null) return;
  java.util.ArrayList l = @PKG@.PartyStore.listOf(pr.getUuid());
  if (l == null) { pr.sendMessage(@MSG@.raw("You're not in a party.")); return; }
  @PKG@.PartyStore.broadcastKey(l, "[Party] " + pr.getUsername() + ": " + m.toString(), null, null, "party.chat", pr.getUuid());
}""")

C(root, r"""
public PartyCmd() {
  super("party", "Party: open the party page, or /party invite|accept|decline|leave|list|kick|promote|disband");
  @ADV@
  addAliases(new String[] { "p" });
  addSubCommand(new @PKG@.InviteCmd());
  addSubCommand(new @PKG@.AcceptCmd());
  addSubCommand(new @PKG@.DeclineCmd());
  addSubCommand(new @PKG@.LeaveCmd());
  addSubCommand(new @PKG@.ListCmd());
  addSubCommand(new @PKG@.KickCmd());
  addSubCommand(new @PKG@.PromoteCmd());
  addSubCommand(new @PKG@.DisbandCmd());
}""")
M(root, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.helpText())); return; }
    @PKG@.PartyStore.pubName(pr);
    p.getPageManager().openCustomPage(ref, store, new @PKG@.PartyPage(pr));
  } catch (Throwable t) {
    @PKG@.PartyStore.warn("/party page failed: " + t);
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.helpText()));
  }
}""")

# ================= 0.1.4: /partyadmin (admin only) - every write goes through the config kit, so it is validated, logged and versioned =================
# PartyAdmin runs on the admin's world thread and only calls the kit (CfgFn: its own monitors, file I/O on the scheduler, never throws).
C(adm, "public PartyAdmin() { }")
M(adm, r"""
public static String rowKey(String typed) {
  if (typed == null) return "";
  String k = typed.trim();
  if (k.equalsIgnoreCase("maxSize")) return "maxSize";
  if (k.equalsIgnoreCase("inviteSeconds")) return "inviteSeconds";
  // 0.1.5: the row is privacy.staffBypass; the short (earlier) name staffBypass still works
  if (k.equalsIgnoreCase("privacy.staffBypass") || k.equalsIgnoreCase("staffBypass")) return "privacy.staffBypass";
  return k;
}""")
M(adm, r"""
public static String cur(String key, String fallback) {
  String v = null;
  try { v = @PKG@.CfgFn.cmdGet(key); } catch (Throwable t) { v = null; }
  return v == null ? fallback : v;
}""")
M(adm, r"""
public static String status() {
  return "[SkyyParty] maxSize=" + cur("maxSize", String.valueOf(@PKG@.PartyStore.MAX)) + " (most players in one party, 2-10), inviteSeconds="
    + cur("inviteSeconds", String.valueOf(@PKG@.PartyStore.inviteSecs())) + " (how long an invite stays open, 15-600), privacy.staffBypass="
    + cur("privacy.staffBypass", String.valueOf(@PKG@.PartyStore.STAFF_BYPASS)) + " (players with skyyparty.bypass, ops included, can invite players who turned party invites off)."
    + " Change: /partyadmin set <maxSize|inviteSeconds|privacy.staffBypass> <value|default>, or in game with /modconfig party."
    + " After editing Skyy_SkyyParty/config.properties by hand: /partyadmin reload.";
}""")
# the kit's reload op (spec 1.3): reads the file, logs + applies every value changed by hand (via=file), keeps pending in-game changes
M(adm, r"""
public static String reload(@PR@ pr) {
  String k = null;
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) k = String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { @PKG@.PartyStore.warn("/partyadmin reload failed: " + t); }
  if (k == null) k = "The config kit did not answer - see the server log.";
  return "[SkyyParty] " + k + " Now: maxSize=" + @PKG@.PartyStore.MAX + ", inviteSeconds=" + @PKG@.PartyStore.inviteSecs() + ", privacy.staffBypass=" + @PKG@.PartyStore.STAFF_BYPASS + ".";
}""")
M(adm, r"""
public static String set(@PR@ pr, String key, String value) {
  String v = value == null ? "" : value.trim();
  String low = v.toLowerCase();
  if (low.equals("default") || low.equals("reset")) v = null;
  return "[SkyyParty] " + @PKG@.CfgFn.cmdSet(rowKey(key), v, pr.getUuid(), pr.getUsername());
}""")

C(admr, r"""
public PartyAdminReloadCmd() {
  super("reload", "(admin) Read Skyy_SkyyParty/config.properties again after editing it by hand");
  requirePermission("skyyparty.admin");
  setPermissionGroups(new String[0]);
}""")
M(admr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyAdmin.reload(pr))); }
  catch (Throwable t) { @PKG@.PartyStore.warn("/partyadmin reload failed: " + t); pr.sendMessage(@MSG@.raw("[SkyyParty] Reload failed - see the server log.")); }
}""")

F(adms, "public @RA@ keyArg;")
F(adms, "public @RA@ valueArg;")
C(adms, r"""
public PartyAdminSetCmd() {
  super("set", "(admin) Change a party setting: /partyadmin set <maxSize|inviteSeconds|privacy.staffBypass> <value|default>");
  requirePermission("skyyparty.admin");
  setPermissionGroups(new String[0]);
  this.keyArg = withRequiredArg("setting", "maxSize, inviteSeconds or privacy.staffBypass", @ATY@.STRING);
  this.valueArg = withRequiredArg("value", "the new value, or default", @ATY@.STRING);
}""")
M(adms, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object k = ctx.get(this.keyArg);
    Object v = ctx.get(this.valueArg);
    if (k == null || v == null) { pr.sendMessage(@MSG@.raw("Usage: /partyadmin set <maxSize|inviteSeconds|privacy.staffBypass> <value|default>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyAdmin.set(pr, k.toString(), v.toString())));
  } catch (Throwable t) { @PKG@.PartyStore.warn("/partyadmin set failed: " + t); pr.sendMessage(@MSG@.raw("[SkyyParty] Could not change it - see the server log.")); }
}""")

C(admc, r"""
public PartyAdminCmd() {
  super("partyadmin", "(admin) SkyyParty settings: /partyadmin, /partyadmin reload, /partyadmin set <key> <value>");
  requirePermission("skyyparty.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.PartyAdminReloadCmd());
  addSubCommand(new @PKG@.PartyAdminSetCmd());
}""")
M(admc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyAdmin.status())); }
  catch (Throwable t) { @PKG@.PartyStore.warn("/partyadmin failed: " + t); }
}""")

# ================= disconnect cleanup + invite pruning =================
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public PartyQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    @PKG@.PartyStore.onQuit(pr);
  } catch (Throwable t) { @PKG@.PartyStore.warn("disconnect cleanup failed: " + t); }
}""")

prune.addInterface(pool.get("java.lang.Runnable"))
C(prune, "public PartyPrune() { }")
M(prune, r"""
public void run() {
  try { @PKG@.PartyStore.pruneInvites(); } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture pruner;")
C(pl, "public SkyyPartyPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.PartyStore.LOG = getLogger();
  @PKG@.PartyStore.loadConfig(getDataDirectory().resolveSibling("Skyy_SkyyParty"));
  // 0.1.5: the staff bypass node, registered ungrouped (listed in /perm list and SkyyRanks' node search; no group is granted it)
  @PKG@.PartyStore.regPerm();
  @PKG@.PartyStore.bridge().put("party:fn:members", new @PKG@.PartyFn());
  getCommandRegistry().registerCommand(new @PKG@.PartyCmd());
  getCommandRegistry().registerCommand(new @PKG@.PartyChatCmd());
  getCommandRegistry().registerCommand(new @PKG@.PartyAdminCmd());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.PartyQuit());
  getEntityStoreRegistry().registerSystem(new @PKG@.PartyStats());
  this.pruner = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.PartyPrune(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  // player Settings switches (research/Settings-Spec.md 2.2, General tab). 0.1.5: party.invites REFUSES the sender when OFF (Skyy
  // 2026-09-25 "block"); holders of skyyparty.bypass (ops included) get through while the Server Setup row privacy.staffBypass is on
  @PKG@.PartyStore.regSetting("party.invites", "Party invites", "general", true, "OFF: other players can't invite you - they are told so");
  @PKG@.PartyStore.regSetting("party.members", "Party join, leave and leader", "general", true, "Steve joined, left, disconnected or is now the party leader");
  @PKG@.PartyStore.regSetting("party.chat", "Party chat", "general", true, "[Party] lines from other members - your own lines always show");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyParty] """ + VERSION + r""" ready - /party page, invite|accept|decline|leave|list|kick|promote|disband, /pc, /partyadmin (admin); maxSize=" + @PKG@.PartyStore.MAX + " inviteSeconds=" + @PKG@.PartyStore.inviteSecs() + " privacy.staffBypass=" + @PKG@.PartyStore.STAFF_BYPASS + " (node skyyparty.bypass); bridge party:fn:members, party:leader, party:name, party:stats; settings party.invites (refuses), party.members, party.chat; TPA / Accept TPA buttons through SkyyEssentials' ess:fn:tpa, ess:fn:tpaccept, ess:fn:tpaPending (when installed); page look """ + KIT_ID + r"""");
  // LAST: the admin config kit reads config.properties after loadConfig and publishes config:def:SkyyParty + config:fn:SkyyParty
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.PartyStore.warn("config kit flush at shutdown failed: " + t); }
  try { if (this.pruner != null) this.pruner.cancel(false); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.PartyStore.bridge();
    java.util.Iterator it = b.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (k instanceof String && ((String) k).startsWith("party:")) it.remove();
    }
  } catch (Throwable t) { }
  super.shutdown();
}""")

KIT.write(OUT)      # deferred kit checks, then the 7 generated Cfg* classes
for c in (pty, ps, fn, sts, page, inv, acc, dec, lev, lst, kck, pro, dis, pc, root, adm, admr, adms, admc, quit_, prune, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)
m = B.manifest("SkyyParty", VERSION, "SkyWynn parties: /party page (members with health, stamina, mana and where they are; invite box; leader kick / promote / disband; TPA and Accept TPA buttons with SkyyEssentials), invites that run out (60 s by default), party chat /pc, leader handoff. Party size and invite time are set in game (SkyWynn Menu Server Setup, /partyadmin); players can turn party invites off in /settings (the inviter is told; staff with skyyparty.bypass, ops included, still get through unless the server turns that off) and hide party member news and party chat. Publishes party members + stats for the SkyyHud party widget. Zero dependencies.", PKG + ".SkyyPartyPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyParty.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyParty" % VERSION, disable_prefix="Skyy:")
