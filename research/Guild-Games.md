# Guild Games - castle raids (Skyy 2026-10-09, LATER: after the server is live)

Skyy: "This is later game content I have planned for once we actually have the server up and running. But i want Guild Games!  The first
one will be a castle raid. Here my idea, each guild gets a guild island, with a zone to build in that starts with a rundown broken cast.
Pretty similar to the one, the skeleton spawn in, in vanilla hightail. Guild members can then use guild gold to upgrade this area by special
weapons like huge mounted crossbows.   But basically you build your guild castle.    Then we have games. I'm picturing something like in
Percy Jackson, the son of Neptune, the camp Jupiter war games. Your castle and the enemy castle spawn at random locations on a random
island. Then you battle and try to steal the enemy standard."

## Pieces (first sketch - every number / rule still Skyy's to decide)
1. GUILD ISLAND: one per guild (SkyyGuilds + SkyyIslands instance pattern), a build zone that starts with a ruined castle like the
   vanilla skeleton castle / fort prefab (find the prefab id in Assets.zip; spawn a copy, never ship vanilla files).
2. CASTLE UPGRADES: bought with GUILD GOLD (SkyyGuilds treasury): siege defences (huge mounted crossbows / ballistae, walls, gates,
   towers), cosmetic banners; members build freely inside the zone with guild permissions.
3. WAR GAMES (Camp Jupiter style): two guilds; BOTH castles are copied (as saved prefabs / schematics of the build zone) onto a RANDOM
   arena island at random spots; capture-the-flag: steal the enemy STANDARD and bring it home; temporary instance, nothing lost from the
   real castles; respawn rules, time limit, team sizes, rewards (guild XP / gold / trophies), seasons + ladder later.
## Engine questions to probe later
- Copying a player-built area (prefab save / paste API) into an instance world; mounted crossbow as a usable block / entity; flag carrier
  state + drop on death; instance per match; PvP toggles per instance.
