# Answered - Profiles, party, guilds, ranks

Covers: profiles, party, guilds, ranks + permissions (SkyyProfiles, SkyyParty, SkyyGuilds, SkyyRanks).

**How to read:** one decision per line, word for word from OPEN-QUESTIONS.md (moved 2026-10-05; still-open questions stay in OPEN-QUESTIONS.md), in that file's order:
the 'Q&A with Skyy 2026-10-02' block (rounds R1-R9, then dated lines up to 2026-10-04) BEATS every older block below it; inside a
block the LOWER line is newer and wins. Each line starts with its status: LOCKED / ANSWERED / DECIDED = Skyy
decided; LIVE / VERIFIED / TESTED = shipped + seen. An OPEN / QUESTION / ASKED line here was answered by a later line - unless OPEN-QUESTIONS.md still lists it.
New answers go in the 'New answers' block at the end and leave OPEN-QUESTIONS.md (`python tools/qa_append.py social <file> --close "<words from the question>"`, or `--no-question`). Index of all topics: [README.md](README.md).

## Q&A with Skyy 2026-10-02 (all open questions, round by round - newest answers win)
- R9 LOCKED (Skyy): KEEP ALL the small live defaults not otherwise marked in this file - tree felling XP (felled logs full XP + collections, leaves normal XP, placed logs never), party combat XP 50% within 48 blocks, menu hover tooltips on, staff bypass on, two crossbows share one big-arrow meter, AH 48h never cheaper than 24h (xFloorPrev on), old SkyyRolls rolls not clamped (clampToLevel off), SkyyRanks placeholders (Admin = kick + Server Setup + staff bypass, no ban; Developer = Admin's; Owner = rank editor; only real ops grant op-level nodes; no grants below Member), the vanilla UI look defaults (readable text, footer Close, vanilla colours / tabs / frames, Mythic #CC66CC, current text-box look), no sickle / gear swing-speed for now, a deleted profile's AH claims stay in its archive (admin can regrant), rank perks later, the picked non-metal gear levels (ranges in SkyyGear 0.2).  *(also in: project, skills, ui, economy, gear, classes)*
- REQUEST 2026-10-03 evening (Skyy, Party page screenshot): "here in the party and a tpa button and a tpa accept to make it quick and easy" -> SkyyParty page: a TPA button on each member row (a /tpa request to that member) + an ACCEPT TPA button while a request to you is waiting; SkyyEssentials already has /tpa, /tpahere, /tpaccept (it needs a bridge for SkyyParty to call). [SkyyParty 0.1.7 + SkyyEssentials 0.1.8, a full round (teleports / commands) after the weekly reset - usage 90%]

## Round 8 defaults (live 2026-09-28)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- Staff bypass for the blocking switches is ON by default (ops + players with skyyparty.bypass / skyyessentials.bypass). [on]

## Round 9 + SkyyGear defaults (live 2026-09-29)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- LOCKED 2026-10-01 (Skyy): the guild member list shows each member's overall bank contribution = deposits minus withdrawals (can be negative, e.g. +100,000 - 25,000 = 75,000; +2,000 - 5,000 = -3,000). Sort: first by guild rank (Leader/owner top, then Admins, then Members), then by contribution, highest first - so the biggest donors and the biggest takers are visible in each rank. [SkyyGuilds 0.1.5, with the % refunds]
- LOCKED 2026-10-01 (Skyy): guild disband pays the bank back fairly, BY PERCENTAGE ("use %") - each member still in the guild gets the share of the whole bank equal to their share of everything the current members put in (their deposits minus withdrawals, from the bank log), so interest and rewards are shared the same way. Members with nothing put in get nothing; if nobody put anything in, the bank is split evenly. Same when the last member leaves. Was: everything to the Leader. [SkyyGuilds 0.1.5 - queued]
- LIVE 2026-10-01 (SkyyGuilds 0.1.5): % disband refunds + Contribution column as decided above.
- LOCKED 2026-10-01 (Skyy): a member who LEAVES (or is kicked) gets part of their contribution back - "some of it but not all. like 30%-40% of what they donated" -> 35% of their positive net contribution (deposits - withdrawals), editable in Server Setup; the rest stays in the bank. [LIVE 2026-10-01, SkyyGuilds 0.1.6 - the rest of a leaver's contribution becomes the guild's, so rejoining starts at 0]
- LOCKED 2026-10-01 (Skyy): profiles can be deleted - confirm question, then a 6-hour undo window (Restore button, frees the slot at once); never the active or the last profile; after 6 h the files go to an admin-only archive (not wiped). Restore works even over the limit. [SkyyProfiles 0.1.5] LIVE 2026-10-01. Review change: a restore may not push you past max(limit, how many profiles you had before that delete) - otherwise delete, create, restore made unlimited profiles. A lowered limit still lets every deleted profile come back.
- LOCKED 2026-10-01 (Skyy): yes, block it - "a player can always leave an island and make their own. so only the owner of an island can delete it." While the OWNER's profile is deleted (undo window) the island is closed to co-op members (anyone on it is sent away); a restore opens it again; once the profile is archived the members are released so they can make their own island. A member deleting their own profile never affects the island. [LIVE 2026-10-01, SkyyIslands 0.5.5]  *(also in: world)*
- DECIDED 2026-10-01 (Skyy): starter coins, class kit and island starter chest stay ONCE PER PROFILE (no change).
- DECIDED 2026-10-01 (Skyy): the profile undo window stays in HOURS ("considering the amount of play time that could be lost"; Wynncraft uses a few days - Server Setup allows up to 168 h = 7 days). [default 6 h]
- Profile cap default = number of classes you can pick (5 now, grows with Assassin/Shaman); more profiles later through ranks (Skyy 2026-09-30). [SkyyProfiles 0.1.4]
- SkyyRanks placeholders: Admin = kick + /modconfig + party/essentials staff bypass (no ban/unban); Developer = Admin's; Owner = rank editor. Only a real op may grant `*`, `skyyranks.*`, `hytale.*` or `hytale.permissionsmodule.*` (covers /op, /perm) - Owner included. [as listed]
- SkyyRanks: a rank below the default rank (Member) can't have grants or be staff, and the default rank can't be staff. [on]

## In-game server setup (`research/Server-Setup-Spec.md` section 9)
8. LOCKED 2026-09-25 (Skyy): ranks are in their own mod, SkyyRanks. 0.1 is live. [yes, already the default]
9. LOCKED 2026-09-25 (Skyy): seeded ranks are Member, Admin, and Developer. Admin and Developer are close to the owner and do not get full op. Was: Developer got the rank editor. The rank editing UI is for ops and players with the Owner rank. Was: ops only. Admin and Developer cannot edit rank permissions or create or modify ranks. skyymenu.modconfig does not open it. Ranks stay fully editable in that UI. Was: only Member. [Member, Admin, Developer; 0.1 still seeds only Member; 0.1 still opens /rankadmin for anyone with skyyranks.admin; 0.1 still refuses grants, delete, and ladder moves on the default rank]
10. LOCKED 2026-09-25 (Skyy): chat order is `[Rank] [Title] Name`. [yes, already the default]
15. Rank perks later (extra vault pages, bigger parties)? [later]
16. CONFIRMED intentionally open 2026-09-25 (Skyy): how a player raises the profile cap above 6 is left open. Likely linked to ranks, and undecided. Not a resolved mechanic. [parked; no way above 6 yet]
17. SkyyRanks before the other mods' settings pages? [done]

## Server Setup pages (round 4, live)
- LOCKED 2026-09-25 (Skyy): the party members switch does not hide "X kicked Y" and "X invited Y". Those lines are always shown. [no, already the default]
- LOCKED 2026-09-25 (Skyy): SkyyGuilds `onlineMessages` treats off, no, and 0 as OFF, the same as every other on/off setting. That stays. [yes, already the default]
- Profiles: the default cap is now 6 (your 2026-09-24 decision); lowering it never deletes a profile.

## New answers (2026-10-05 on - newest last, beats everything above)
- BUG 2026-10-08 (Skyy, screenshot: new Assassin profile 'Lime' right after the Monk 'Pineapple', Health bar about half): "damage from the monk carried over to a new assassin profile." -> a profile switch keeps the player's current Health; a NEW profile must start at full Health, and a switch should restore that profile's own saved Health (or full) - not carry the other profile's damage. Fix in the queued SkyyProfiles lean round (with the big-SWITCH confirm). Also seen: Assassin kit Daggers Crude x1, 10,000 starter coins, island created (TEST 46 Assassin start PASSED).
- LOCKED 2026-10-08 (Skyy, popup batch 5): profile cap -> "profile cap should match the number of classes. ( upgrade: ranks and earn in game later)" -> cap = class count (8 with Spellblade) instead of 6; ranks + in-game unlocks later. Next SkyyProfiles round.
- IDEA LOCKED 2026-10-09 (Skyy, LATER content): GUILD GAMES - guild islands with a ruined castle to rebuild using guild gold (mounted crossbows etc.), then castle-raid war games (both castles copied onto a random island, steal the enemy standard). Skyy's words + first sketch: research/Guild-Games.md.
- IDEA LOCKED 2026-10-09 (Skyy, Guild Games): "I want guilds to be able to challenge each other and set rewards, so you can battle over loot and money" + "I wana 1v1 guild battles, and group battles where guilds team up, for server wide events." -> challenges with wagers (escrow), 1v1 guild battles + alliance battles for server-wide events (research/Guild-Games.md).
