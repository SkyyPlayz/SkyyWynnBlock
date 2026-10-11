# Guild Games - design spec (LATER content, design doc only)

Draft 2026-10-09 (cloud). Not a build plan: nothing here is scheduled until the server is live (Skyy: "later game content ... once we
actually have the server up and running"). Every number is a placeholder for Skyy to decide.

## Decisions this follows (never re-decided here)

| Source | What it fixes |
|---|---|
| research/Guild-Games.md lines 1-12 | Guild island + ruined castle, rebuilt with guild gold; castle-raid war games, steal the enemy standard |
| research/Guild-Games.md lines 25-27 | Challenges with wagers held in escrow; winner takes the pot; Mythic / UT / Sets wagerable is still open |
| research/Guild-Games.md lines 28-30 | Modes: 1v1 guild battle, alliance battle (server-wide events) |
| research/Guild-Games.md lines 31-35 | "The Institute": 12 guilds, 12 castles, one map, last guild wins, captured players work for the captor |
| docs/answered/social.md lines 49-51 | The three IDEA LOCKED lines above (2026-10-09) |
| docs/answered/economy.md line 89 | Market wall = Mythic + UT + Sets: never bought or sold on Bazaar / Auctions |
| docs/answered/social.md lines 21-24 | Guild bank: member contribution = deposits - withdrawals; leaver gets 35%; disband pays by percentage |
| PROJECT-RULES.md section 2 | Public repo: vanilla castle prefab is spawned from the game at runtime, never shipped |

## What exists today (read only)

| Thing | Where | Use for Guild Games |
|---|---|---|
| Guild bank (`g.bank`), `deposit()` takes from the purse first, then adds to the bank | SkyyGuilds/build_skyyguilds_0.1.6.py lines 2918-2925 | "Guild gold" = this bank. No separate currency exists |
| Guild bridge: `guild:<uuid>`, `guild:info:<uuid>`, `guild:fn:online` | SkyyGuilds/build_skyyguilds_0.1.6.py lines 1584-1585, 552, 4963 | Only 3 read keys. Wagers, rosters, treasury spend need NEW bridge functions |
| Coins bridge `coins:fn:get/add/take` (take must say TRUE) | research/Trade-Spec.md lines 347-349; SkyyGuilds line 2925 | Player-side coin stakes |
| Plugin-owned escrow, written to disk on every change, tmp + fsync + atomic rename, returned on disconnect / next join | research/Trade-Spec.md lines 250-258, 283, 322 (section 10), disconnect + crash rows 114-115 | Pattern to copy for wagers |
| One file per listing, id counter written before use, "never in two places" | research/Auction-House-Spec.md lines 38, 222, 235, 242 | Same pattern for pot records |
| Island worlds via `InstancesPlugin.spawnInstance`, per-island `WorldConfig.setPvpEnabled`, 5-arg `teleportPlayerToLoadingInstance` | research/Island-Settings-Spec.md lines 31, 151-156, 283 | Guild island + match arenas are instance worlds |
| Party (no friendly-fire or team logic found) | SkyyParty/build_skyyparty_0.1.7.py | Parties join a match together; no team-damage rules exist yet |
| Faucet / sink picture (guild bank "moves coins", not a sink) | research/cloud/Economy-Audit.md line 63 | Wager fee is a NEW sink; see section 3 |

No SkyyGuilds island, castle, challenge or team code exists. All of Guild Games is new.

## 1. The game modes

All matches are temporary instance worlds. Real castles are never touched (Skyy's sketch: "nothing lost from the real castles").

### 1.0 Shared groundwork: Guild Island and Castle

| Item | Proposal |
|---|---|
| Guild island | One per guild, created on guild creation or first unlock (SkyyIslands instance pattern). Build zone with a ruined castle |
| Build zone | Fixed box (e.g. 96 x 96 x 64). Only this box is copied into matches, so size is the limit on match cost |
| Upgrades | Bought from the guild bank by Leader / Admin (ranks per SkyyRanks): walls, gates, towers, mounted crossbows (ballistae), banners |
| Siege weapons | Only active in matches; on the island they are cosmetic (target dummy only) |
| Standard | One banner block / item per castle. Defines the win condition in raids |

### 1.1 Castle Raid (first mode; 1v1 guilds)

| Rule | Proposal |
|---|---|
| Teams | 2 guilds. Roster 5v5 to 20v20, set by the challenge (both sides must field equal numbers) |
| Arena | Random arena island; both castle copies pasted at random spots (min distance between them, e.g. 150 blocks) |
| Win | Steal the enemy standard and carry it to your own standard point. Or time limit: more captures, then most standard-holding time |
| Flag rules | Carrier cannot use mounts / traversals / ender-style teleports (no void protection per docs/answered/classes.md line 117 still applies); drops on death, returns after N seconds if untouched |
| Respawn | Timed respawn at own castle (e.g. 20 s), shortened while the castle's tower stands |
| Time limit | 30 min (editable) |
| Rewards | Guild XP, guild gold, trophy; plus the wager pot if any (section 2) |
| Gear | Players keep own gear; optional "equal kit" flag for fairness (open question) |

### 1.2 Alliance Battle (server-wide event)

| Rule | Proposal |
|---|---|
| Teams | 2 sides, each 2-4 allied guilds. Scheduled and announced, not challenged |
| Arena | Larger arena island, one castle per guild (4-8 castles). Same castle-copy method as 1.1 |
| Win | A side wins by holding every enemy standard at once, or by most standards at the time limit |
| Rewards | Event rewards split by contribution (kills, flag time, castle damage), not by headcount, so the biggest guild does not just win the pot |
| Wagers | Allowed per guild, but only within a side vs side pot; each guild's share is its own stake (see 2.6) |

### 1.3 The Institute (12-guild free-for-all, Red Rising style)

| Rule | Proposal |
|---|---|
| Teams | 12 guilds, 12 castles on ONE big map. Last guild with a standing castle wins |
| Match length | Long: hours to days, runs in phases (e.g. 3 phases, a rest period between each) |
| Captured players | A player "defeated" at 0 lives (or knocked out inside an enemy castle) is captured: switched to the captor guild's team for the rest of the match, marked (collar / name tint), cannot attack the guild that captured them |
| Capture limits | Captives fight and gather for the captor; cap captives at e.g. 50% of the captor's roster so snowballing is bounded; a captive can be freed if the holding castle falls |
| Elimination | Guild with no castle standing and no free members is out; members become captives of whoever took the last castle |
| Resources | Map nodes (ore, wood, food) the owner of the nearest castle taxes; tied to guild gold for upgrades during the match |
| Rewards | Winner: large guild gold + trophy + season points. Captives released at the end keep their own loot |
| Entry | Opt-in per guild with a minimum member count; 12 slots filled by queue; empty slots stay empty (or NPC garrison, open question) |

Exact capture rules are Skyy's. The proposal above is only a starting point.

## 2. Wagers and escrow

### 2.1 What can be staked

| Stake | Held where | Notes |
|---|---|---|
| Guild gold | Moved from `g.bank` into the pot record | Needs a new guild bank function: `bank:fn:hold` / `release`, never a plain `take` |
| Player coins | Moved from purse into the pot record via `coins:fn:take` | Take must return TRUE; same rule as SkyyGuilds line 2925 |
| Items | Removed from the inventory the instant they land in the pot (Trade-Spec line 256) | Mythic / UT / Sets: see Q1. Default is NOT wagerable (market wall spirit) |

### 2.2 Pot record

One file per challenge (the Auction House pattern): `id`, both sides, stakes, state, expiry. States are strictly:
`PROPOSED -> ACCEPTED (both staked) -> LIVE -> SETTLED` with `CANCELLED / REFUNDED` side exits. The id counter is
written before use. Every state change is written to disk (tmp + fsync + atomic rename) before it counts.

### 2.3 Money flow

```
Challenge: Guild A proposes stake S. Guild B accepts or counter-offers.
Both stakes are removed from banks / purses at ACCEPTED (not before) so a refused challenge costs nothing.
Pot = A.stake + B.stake. Match ends -> settle: pot minus fee -> winner. Draw -> both refunded.
```

Fee (new coin sink): 5% of the pot, editable in Server Setup. Example: stakes 1,000,000 each, pot 2,000,000, fee 100,000,
winner gets 1,900,000. Without a fee the wager is not a sink at all (Economy-Audit.md line 63 treats guild bank as neutral).

### 2.4 Disconnects and crashes

| Event | Rule |
|---|---|
| One player disconnects mid-match | Match goes on; they have a grace window (e.g. 3 min) to rejoin their team; a rejoin returns them to the arena |
| Whole side drops | After the grace window, that side forfeits |
| Both sides fall below the minimum roster | Match voided: REFUNDED, full stakes back, no fee |
| Server stop / crash | Pot record stays LIVE on disk. On next boot: if the arena instance is gone, every LIVE pot becomes REFUNDED in full. Never auto-pay a winner from a crash |
| Refund of a disconnected player's stake | Returned to their purse / inventory on next join (Trade-Spec line 322 pattern), item stakes delivered via `deliver()` |
| Admin | `/guildadmin pot list|refund|settle` for stuck pots, logged |

### 2.5 Anti-abuse

| Abuse | Defence |
|---|---|
| Win-trading (alts of one player, guilds feed each other coins) | Minimum guild age and member count; a pot cannot exceed a multiple of the smaller guild's bank; per-pair daily limit (the same two guilds, max N wagered matches a day); wager fee makes loops lose coins |
| Sandbagging / throwing a match | Same limits; log pairs and results for admin review; no wager payout if one side deals no damage and holds no flag |
| Leaving the guild to dodge a loss or steal stake | Stake is the GUILD's (bank) or an individual's (purse). Players who leave mid-match forfeit their share; a player's own coin stake follows the player, not the guild |
| Stake withdrawal after accept | Impossible: funds already moved into the pot record |
| Dupe via crash / disconnect | One place at a time rule; record written before and after each move; refund on boot (2.4) |
| Item swap after accept | Item stakes locked by identity (stack contents re-read at settle, Trade-Spec lines 270+) |
| Bank drain by one officer | Wagering guild gold needs Leader or Admin; amounts above a threshold need Leader approval or a member vote (Q3) |
| Challenge spam | Cooldown per guild; challenges expire in e.g. 10 min |
| Griefing the real castle | Not possible: matches use copies |

### 2.6 Alliance and Institute stakes

Alliance: each guild stakes separately into one pot per side; payout is split by each guild's stake share, then by contribution
inside the guild. The Institute: an entry fee from each of the 12 guilds forms the prize (e.g. 12 x 500,000 = 6,000,000, 5% fee
300,000). No other wagers during an Institute.

## 3. Matchmaking and scheduling

| Mode | How |
|---|---|
| 1v1 raid | Direct challenge (`/guild challenge <guild>`, menu button). Also an open board: "Open challenge" anyone can accept. Optional unranked friendly (no stake) |
| Ranking | Simple Elo-style ladder per season later; separate from wagers |
| Fairness | Roster must match size; optional level / member-count bands; handicap off by default |
| Alliance | Scheduled by admins (a weekly slot), announced in chat and the SkyyMenu. Guilds sign up, then are paired into sides by an admin or by balanced total roster |
| Institute | Season event, e.g. monthly or quarterly. Guilds register for a slot; a queue fills 12; starts when full or at a fixed time |
| Match start | Ready check, a countdown, everyone gets teleported to the arena; same 5-arg teleport call as islands |
| Arena pool | Several prebuilt arena islands, one picked at random, keeps spawn points valid |

## 4. Systems needed and which mod owns them

| System | Owner | Status |
|---|---|---|
| Guild island + castle zone + upgrades | SkyyGuilds (treasury) + SkyyIslands (instance, build zone, guards) | New; SkyyIslands already has the island pattern |
| Guild gold hold / release / spend | SkyyGuilds | New bridge functions on `g.bank` |
| Pot / escrow records | New mod `SkyyGames` (proposed) with SkyyGuilds and SkyyCoins bridges | New. Copy Trade-Spec section 10 |
| Match instance lifecycle, team assignment, flag, scoring | `SkyyGames` | New |
| Team damage rules (no friendly fire, captive switch) | `SkyyGames` writes it; SkyyClasses / SkyyMobs may need a bridge for the damage filter | New; UNVERIFIED how team can be set |
| Mounted crossbow / ballista | SkyyGear (item) + `SkyyGames` (behaviour) | New; see probes |
| Fee, caps, times, roster limits | `SkyyGames` via skyycfg (editable in game) | New |
| Menu page "Guild Games" | SkyyMenu | New |
| Trophies, season points | SkyyGuilds | New |
| Party joins a match together | SkyyParty bridge | Small |

Cross-mod calls go through `skyy.bridge` with plain java.lang types only (PROJECT-RULES.md section 4).

## 5. Engine probes needed (all UNVERIFIED, need the game files)

1. Save the build zone as a prefab / schematic at runtime, and paste two of them at chosen offsets into an arena instance.
2. Vanilla "skeleton castle" prefab id for the starting ruin (Assets.zip). Spawn a copy, never ship it.
3. Is there a block / entity usable as a mounted crossbow, and can a player fire it? Or is it a custom entity?
4. Flag carrier state: item with "drops on death", custom NPC, or a held block?
5. Per-instance PvP flag (`WorldConfig.setPvpEnabled` works per world per Island-Settings-Spec line 31) and per-team friendly fire.
6. Entity team / faction: can damage filtering use a team tag, or must it be a damage event hook?
7. Captured player's team switch mid-match, and whether a name tint / marker is possible.
8. How many instance worlds can run at once, and memory per arena (matters for an Institute map and for several 1v1s at once).
9. Can a large single world (Institute) be built at the needed size, and can 12 castle copies fit in one pass?
10. Respawn point per player inside an instance; keep-inventory vs drop rules in the arena.
11. Disconnect handling: can a rejoining player be sent straight back into a live instance?
12. Timer / scoreboard UI on a custom HUD (SkyyHud) for flag time and standings.

## 6. Rough phases (when Skyy says go)

| Phase | Scope |
|---|---|
| 0 | Probes in section 5 (local, no code ships) |
| 1 | Guild island + ruined castle + upgrades with guild gold (no matches yet) |
| 2 | Castle Raid 1v1, friendly (no wagers): castle copies, flag, respawns, rewards |
| 3 | Wagers + escrow + refunds + admin tools + fee |
| 4 | Alliance battles on a schedule |
| 5 | The Institute: 12-guild map, captures, long-match persistence |
| 6 | Seasons, ladder, trophies |

Each phase is a Full round (economy, saved data, several mods). Phases 3 and 5 are Ultracode candidates.

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Can Mythic / UT / Sets be wagered? | [No. Coins and guild gold only, plus tradable items. Keeps the market wall] |
| 2 | Wager fee (coin sink)? | [5% of the pot, editable in Server Setup] |
| 3 | Who can stake guild gold? | [Leader / Admin. Over 25% of the bank needs the Leader] |
| 4 | Team sizes for 1v1 raids? | [5v5 to 20v20, equal on both sides, set in the challenge] |
| 5 | Equal kit in matches, or players use their own gear? | [Own gear; "equal kit" is an optional flag per challenge] |
| 6 | Respawns in a raid? | [Unlimited, 20 s timer, until the time limit] |
| 7 | Institute: how long, and do captives have a lives limit? | [Hours in a day, 3 lives, then captured] |
| 8 | Institute: a free guild slot with fewer than 12 guilds? | [Queue waits; below 8 guilds the event is cancelled] |
| 9 | Captured players: can they be freed? | [Yes, if the holding castle falls; max 50% of the captor's roster] |
| 10 | Rewards for the winner: coins, guild XP, trophies, items? | [Guild gold + guild XP + trophy; no items at first] |
| 11 | Alliance battles: how often? | [One scheduled event a week, admin-run] |
| 12 | Which castle upgrades first? | [Walls, gate, towers, 2 ballistae. Banners cosmetic] |

## For the local session

- Every item in section 5 is UNVERIFIED (needs HytaleServer.jar / Assets.zip). Probes 1-4 gate Phase 1-2.
- Nothing in SkyyGuilds or SkyyParty handles teams, islands or challenges; confirm before planning (only the bridge keys and bank
  deposit/withdraw were read).
- Wager escrow should copy research/Trade-Spec.md section 10 exactly; check whether SkyyEssentials' escrow code can be reused.
- Do not queue any of this before the server is live (Skyy's own "later" line).
- Suggested log line for `docs/log/2026-10.md`: "cloud: research/cloud/Guild-Games-Spec.md drafted (modes, escrow, probes, phases)".
