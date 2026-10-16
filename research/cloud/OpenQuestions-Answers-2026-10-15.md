# SkyWynn open questions notes (Cobb)

From the 2026-10-15 review of OPEN-QUESTIONS.md (94 open).

## General design notes
- Admin test modes (Skyy, 2026-10-15): most features should have an admin test mode, not just rebirth (see L90). The pattern is to switch a feature off when it has bugs, get them fixed, and switch it back on once the server is actually running.

- Ore tiers (Skyy, 2026-10-15, first thoughts and NOT settled): there aren't enough ores for the number of tiers. Gear is enough for combat to scale with the zones, but mining has only a few ores next to the many tree, farming and foraging options. He plans to add silver and gold as more mining tiers, and may need more ores beyond that so mining feels natural. This is a planned rework, not a decision. It ties into the open "ores per zone" question.

- Party loot split (Skyy, 2026-10-15, design direction for all party loot): party loot should split fairly, not only by damage dealt. Mob loot currently goes by who did the most damage. Add a party split so support classes, like Priests who heal and deal little damage, still get a fair share. Scale each share by how much damage that class is able to deal, the way Realm of the Mad God does it. In Realm of the Mad God the Priest deals the least damage of any class, so its damage threshold for soulbound drops is set lower so it still gets them. Use the same idea here: each class's threshold for loot eligibility is scaled by what that class can deal, not by raw damage dealt.

## Closed
- L55 lost forever tool: handled in build (summon command, works across dimensions).

## Answered
- L32 (keep zones vanilla): answered by Skyy. "Vanilla" means normal vanilla generation used as-is, with the zones turned into floating islands instead of separate zones on one map. No conflict with the caves-and-mines lock. Caves come from natural vanilla generation only, with no custom mine areas carved in, so solo play feels normal to vanilla players. Future plan: on Skyy's server every island will be hand-built, which is a separate case from the modpack's vanilla generation.

- Wynn elements: in now, on the current build list (locked; Hytale 0.7 is out). Not Later. ROADMAP.md in the repo still lists them under Later and needs a docs PR.

- L62 (tab vs rebirth): answered by Skyy. Rebirth takes all your money, and that money goes toward paying off your Tab. The Tab is a fixed, reasonable amount, not one that keeps rising. Players pay it off in about five rebirths, and after that they own their island (the team decides what paying off the Tab unlocks).

- L95 (first rebirth pacing): answered by Skyy, replacing the earlier options (keep the curve, cheaper early levels, one-time bonus). Every rebirth gives bonuses and upgrades, so each one goes a little faster. Players must reach max level to rebirth, and max level rises 10 levels per rebirth, with the bonuses on top, so the pace stays roughly the same for every rebirth. Past about four rebirths, rebirths start getting faster and faster, even though max level still rises 10 per rebirth.

- L128 (character hub tabs): answered by Skyy, option C. Merge only the pairs players open back-to-back, and keep the other tabs separate.

- L114 (gear rewards from daily jobs): answered by Skyy, option C. Reward gear has a level that matches the zone you're in.

- L80 (dragon pet): answered by Skyy, option A. Our pet slot summons the dragon from Aures' mod.

- L116 (quest markers): confirmed by Skyy as designed. A floating "!" over quest givers plus placeable signs, with an on/off toggle.

- L117 (mine 64 stone): confirmed by Skyy as designed. Player-placed blocks still count, because breaking a placed block takes the same time as breaking a natural one, so the difference doesn't matter.

- L83 (guild names): confirmed by Skyy. Guild names should allow spaces and the usual marks people put in names, like slashes, commas and dots. Apply the same fix in Shards and Rebirth.

- L98 (shard island co-op): changed by Skyy. Guests can visit, and the owner plus the island's co-op members can collect and upgrade, not just the owner.

- L99 (picked-up shard): confirmed by Skyy as designed. A picked-up shard makes nothing until it's placed again, and while held it's just an item.

- L102 (shard world server limit): changed by Skyy. With 50 players online as a decent target, 25 shard worlds loaded at once is the starting number. He expects many more players later, so the number will go up.

- L103 (shard collect target): changed by Skyy, replacing "inventory now, Magic Bags later". Collected items go straight into Magic Bags when they fit there. If the bags are full, they go to the inventory.

- L104 (worker cap; Skyy called it L106 on the call, but the worker cap is L104 and L106 is rebirth ranks): answered by Skyy. 12 items a minute is the base rate for the magical workers (spirits) a totem spawns. They collect ready crops or resources in an area and send them to your collection. The cap starts at that base and goes up with the totem tier, together with the totem's collection area. Related: L108 (totem speed tiers and costs).

- L107 (Harvest Moon): confirmed by Skyy. One Enchanted Wheat equals 100 regular Wheat, and the ratio stays at 100. Harvest Moon is a rare chance at night, and an enchant raises that chance.

- L109 (MoreTotems licence): answered by Skyy. Drop the MoreTotems mod completely and build our own totem pack, since SkyWynn only uses one totem from it. That means no copyright notice is needed.

- L110 (Creative mode): changed by Skyy, replacing "collections only count in Adventure mode". Collections work in Creative mode too. Only admins use Creative, and not often, so an Adventure-only limit isn't needed.

- L88 (rebirth switch): changed by Skyy. Turn rebirth ON now instead of keeping it off until it's tested.

- L89 (Nexus buttons): confirmed by Skyy. Rebirth works from both the Nexus click and the side panel, and both stay.

- L90 (admin test rebirth): confirmed by Skyy. Admin test rebirth keeps working even while the rebirth feature is switched off. General pattern for admin test modes across most features: switch a feature off when it has bugs, get them fixed, then switch it back on once the server is actually running. Use the same pattern in the future.

- L26 (loot names): confirmed by Skyy. Lost Loot, Lost Treasure and Supply Drop are the display names for the three world loot types.

- L27 (tier IV loot look): changed by Skyy. Tier IV loot shows as Legendary bright blue, not a gold treasure pile, since the top tier on most things is Legendary, which is bright blue.

- L28 (supply drops): changed by Skyy, replacing "first claim takes all". Drops are first come, first served. If the claimer is in a party, the haul is split across the party. With no party, the claimer gets everything. Still one every 30 minutes.

- L29 (how a drop arrives): confirmed by Skyy. A firework flash, then the crate appears.

- L30 (drop distance): confirmed by Skyy. Supply drops land 32 to 64 blocks from the chosen player.

## Open for Skyy's team
- L86/L87 rebirth bank bonus: is the bank per-profile with the rebirth bonus applied globally across all profiles, or was it coded differently? (Skyy will ask the team.)
- L106 (shard rebirth ranks, each rank needs twice the last tier's amount): NEEDS CLARIFICATION from Skyy's builder. Skyy didn't know shards had rebirth ranks and wants to go over it with his builder before answering. No answer recorded yet.
- L108 (totem speed tiers and their costs): STILL OPEN. Skyy hasn't seen these numbers and needs them from his builder. No answer recorded yet.
- L94 (Echo nodes: +4% points per level, up to +40%): LEFT OPEN by Skyy. No answer recorded yet.
- L31 (message joszza about using their structure mods): Skyy will handle this with his builder. Flagged for builder follow-up, no answer recorded.
