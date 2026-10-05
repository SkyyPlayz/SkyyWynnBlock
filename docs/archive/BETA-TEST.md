# SkyWynn beta test - 2026-09-24 (Skyy + friend)
S = Skyy (host), F = friend (first join). Multiplayer first, then solo. Mark each line OK or write what happened.
Needs the 19-mod set deployed (`python tools/deploy_set.py` with the game closed).

## 0. Smoke test (S alone, right after the deploy)
- [ ] Server log: a "[Skyy...] ready" line for every Skyy mod incl. `[SkyyParty] 0.1.3`, `[SkyyGuilds] 0.1`, `[SkyyExploration] 0.1`; no errors.
- [ ] `/skyyhud`: the editor shows "Party (sample)" and "[SKY] Sample Guild". **If the game disconnects here, stop and report it (HUD layout).**
- [ ] `/party` opens the party page, `/guild` opens the Create guild page.

## A. Friend's first join
- [ ] F joins: 10,000 starter coins message, the SkyWynn Menu item in slot 9, the Create Profile page about 2 s later (no second class picker).
- [ ] F picks a class, Create profile. `/balance`, `/skills`, `/menu` work for F (no "no permission").

## B. Party
- [ ] S: `/party`, type F's name (first letters are enough), Enter -> "Invited ...". F gets the invite in chat (60 s).
- [ ] F: `/party` -> Accept (or `/party accept`). Both get "joined" messages.
- [ ] Party widget on BOTH HUDs: "Party (2)", S (L) and F with HP / ST. F takes damage -> S sees F's HP drop within ~1 s.
- [ ] `/pc hello` -> both see it.
- [ ] F goes `/island` -> on S's HUD F's line turns grey "... - Island".
- [ ] `/party promote F` (leader moves), `/party kick`, `/party leave`, `/party disband` all work; the widget hides for whoever is out.

## C. Guild
- [ ] S: `/guild` -> type a name -> Create (or `/guild create <name>`), then `/guild tag SKY`.
- [ ] S invites F (page or `/guild invite F`); F: `/guild accept`.
- [ ] Guild widget on BOTH HUDs: "[SKY] <name>", "Lv 1 (...)", "Online 2/2".
- [ ] `/gc hello` -> both see it.
- [ ] Promote F to Officer, demote, kick, re-invite.
- [ ] Bank: F `/guild bank deposit 100` (F -100 coins, bank +100); S `/guild bank withdraw 50`; a plain Member cannot withdraw.
- [ ] Guild XP: both gather for a minute -> guild XP rises (widget / page) within ~10 s.
- [ ] F `/guild leave`; S `/guild disband` (repeat within 10 s).

## D. Islands together
- [ ] F: `/island` -> new island, the starter chest HAS items (0.4.5 fix; if empty, report it).
- [ ] S: `/island visit F` -> can walk around; cannot break, place, open the chest or pick up items; doors work.
- [ ] F: `/island invite S` -> S can now build on F's island.
- [ ] Zone widget: F sees "Your Island", S sees "Island"; at the hub the zone name or "Hub".

## E. Other multiplayer
- [ ] `/pay F 100`, `/tpa F` + `/tpaccept`, `/msg F hi`.
- [ ] Hitting each other does no damage (PvP is off).
- [ ] F tries a weapon their class cannot use -> popup "You can't use this weapon".
- [ ] F makes a 2nd profile in `/profiles` (new island, fresh coins), then switches back (items return).
- [ ] Both use `/bazaar` (buy and sell).

## F. Solo checks
- [ ] Rolls: `/rolls give mithril bow` -> name "<Reforge> Mithril Shortbow" in rarity colour + stat lines on hover; the old rolled bows show their rolls after joining; hold the rerolled sack -> `/rolls clear`.
- [ ] HUD styles: widget Settings -> Color, Bold, Italic, Glow (+ glow colour), Preview, Reset style; `/skyyhud export` / import keeps styles.
- [ ] Exploration: open a world chest in a NEWLY generated area -> Exploration XP; walk into new chunks -> XP (none while flying); enter a new Hytale zone -> XP; `/explore` page; `/title` -> pick a title -> it shows before your name in chat.
- [ ] `/skills`: an Exploration row (+max Stamina on its Stats page); Tree buttons on Acrobatics and Exploration.
- [ ] `/tree acrobatics`: buy Second Wind (+Stamina) and Fleet Foot (speed); `/tree exploration`: Wanderer's Heart (+Health); "Coming later" slots.
- [ ] Campfire: craft the Campfire accessory at a Workbench (Campfire + 4 Copper Bars), equip it; `/craft` -> Campfire tab -> cook meat -> a graded dish + half Cooking XP.
- [ ] Cooking: eat the Grade 5 Meat Pie (12 min regen, +30% max health); cook Bread at a Cooking Bench -> Cooking XP.
- [ ] Alchemy Bench -> Alchemy XP. `/craft` Furnace tab -> Smithing XP per bar.
- [ ] Acrobatics falls: safe drop 0 XP; a fall that hurts (survived) pays XP; water pays 0.
- [ ] Collections: F-harvest a ripe crop and break stone -> counts go up.
- [ ] Pack mods: Cobalt / Thorium / Mithril / Adamantite crossbows at the Weapon Bench (Archer can fight with them); leaves sometimes drop saplings.
- [ ] Profiles: a switch during combat is refused; log out on profile 2 and back in -> still profile 2.

## Known issues (already on the fix list - no need to report)
- A felled tree pays Foraging XP and counts collections for only the 1 log you cut (fix specced: research/Tree-Fall-Spec.md).
- Bag recipes on collection tiers do nothing yet (bags are craftable at a Workbench; bag restructure pending your Cobblestone-vs-Iron answer).
- Chests generated before SkyyExploration was installed never give Exploration XP.
- An old island may need `/hub` then `/island` once to show green grass.
- A disconnect removes that player from their party (guilds persist).

## RESULTS 2026-09-24 evening (Skyy + WesleyPlayz)
Working: HUD 0.3.8 (widget colours / styles "work great", Party + Guild widgets), /party + page, /pc, /guild (leader-only invite/disband,
deposit + withdraw, /gc), friend's first join (10k coins, commands), /tpa + /tpaccept, /pay, /bazaar, Exploration titles, skill trees,
Saplings From Trees (leaves drop saplings), More Crossbow Tiers crossbows, island tree felling (the whole tree falls when the base is cut).
NOTE: WesleyPlayz was OPPED for part of the session (op add/remove in the log) - permission checks from those windows do not count.
Bugs:
- Menu: hover an item, press Esc -> its tooltip stays on screen.
- Party widget drawn misaligned until clicked/moved in the editor.
- '/r' is VANILLA's /redo shortcut (builder permission) - that was the 'msg needs op'; /msg, /tell, /w, /reply work without op.
- Sacks still do not hold ingots.
- Felled trees still pay XP / count collections for the cut log only (known; fix specced).
Requests: HANDOFF 2026-09-24 20:10 backlog.
