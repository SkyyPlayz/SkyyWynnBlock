# SkyyGuilds — plan
*Design lock 2026-09-23 night. See `SkyWynn-Master-Plan.md` Part 2B step 8 and 2E (P1, P7), and `SkyWynn-Decisions.md` rows 8.1–8.3, 10.25, 10.27.*

## Where they sit

Guilds are in the **core loop with parties**. They are not Phase 7 and not a "later phase" system.

Parties and guilds both show up in P1, next to skills, collections, and the coin bypass. `SkyyParty` is the party mod already in the roster. Guilds build on that, they do not replace it.

## Parties (already locked, still core)

- Invite / kick / leave, party chat, member data for the HUD and the map
- Map shows live party-member positions (row 10.25)
- Party HUD widget: name, HP, stamina, mana (row 10.27)

## Guilds (pulled forward)

What moved into the core loop is the guild itself (row 8.2):

- Membership
- Guild bank
- Guild XP
- Seasons

That is the core-loop scope. This plan does not add ranks, perks, or a guild island.

## What stays later

**Territory war** (row 8.3) stays a later, public-server endgame system. It is side content in P7, with raids and the other non-spine systems (`SkyyDungeons-Plan.md`). Slayers are core loop, not in that pile. Pulling guilds forward does not pull the war map forward.

The hub town is the shared social point (`SkyyIslands-Plan.md`). Guilds and parties gather there. The leveling path is still the zone island chain.

## Status 2026-09-24 (built, next deploy)
SkyyGuilds 0.1 = the core-loop scope: /guild create|tag|invite|accept|leave|kick|promote|demote|disband|info, /gc guild chat, guild bank
(coins from the member's active profile purse), guild XP from a share (default 10%) of every member's skill XP, seasons (admin starts the next
one; no rewards yet), a /guild page. Ranks: Leader, Officer, Member. Membership is per PLAYER (not per profile). HUD Guild widget in SkyyHud
0.3.8. SkyyParty 0.1.3 adds kick / disband / promote, a /party page and the Party HUD widget (name, HP, stamina, mana, world).
Not yet: party positions on the map (row 10.25), guild perks, territory war (later).
