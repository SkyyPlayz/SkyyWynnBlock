# Balance inventory: Mobs, bands, classes, abilities (combat)

Generated 2026-10-18 by P0 from the LIVE configs (UserData/Saves/NewBetaTest/mods/Skyy_Mod/file.properties). Rows: key | value | line in that file. Comments (units, meaning) are in the source file. A value here is what the server runs today (defaults unless Skyy edited it).


## SkyyMobs / config.properties

| key | value | L |
|---|---|---|
| part.levels | true | 4 |
| levels.neutral | true | 6 |
| levels.roles |  | 9 |
| levels.exclude | Test_*,Tamed_*,Temple_*,*_Merchant*,Risen_*,Goblin_Duke*,Trork_Chieftain,Dragon_*,Skeleton_Elite*,*_Mount*,*_Pet*,*_Boss*,*NPC*,*_Hub*,*Blacksmith*,*Trader* | 12 |
| levels.max | 100 | 14 |
| strength.difficulty | normal | 18 |
| strength.hp | 4 | 20 |
| strength.dmg | 2 | 21 |
| strength.hpCap | 6 | 23 |
| strength.dmgCap | 3.5 | 24 |
| strength.floor | 50 | 26 |
| strength.healOnLoad | false | 28 |
| strength.shape | curve | 31 |
| strength.dmgFloor | 0 | 33 |
| strength.hitCap | 35 | 36 |
| curve.hp.easy.1 | 1 | 38 |
| curve.hp.easy.20 | 1.76 | 39 |
| curve.hp.easy.25 | 2.43 | 40 |
| curve.hp.easy.30 | 3.65 | 41 |
| curve.hp.easy.35 | 5.41 | 42 |
| curve.hp.easy.40 | 8.19 | 43 |
| curve.hp.easy.45 | 11.85 | 44 |
| curve.hp.easy.49 | 14.79 | 45 |
| curve.hp.easy.55 | 16.01 | 46 |
| curve.hp.easy.60 | 17.02 | 47 |
| curve.hp.normal.1 | 1 | 49 |
| curve.hp.normal.20 | 2.14 | 50 |
| curve.hp.normal.25 | 3.03 | 51 |
| curve.hp.normal.30 | 4.62 | 52 |
| curve.hp.normal.35 | 6.97 | 53 |
| curve.hp.normal.40 | 10.69 | 54 |
| curve.hp.normal.45 | 15.63 | 55 |
| curve.hp.normal.49 | 19.66 | 56 |
| curve.hp.normal.55 | 21.48 | 57 |
| curve.hp.normal.60 | 23 | 58 |
| curve.hp.hard.1 | 1 | 60 |
| curve.hp.hard.20 | 2.52 | 61 |
| curve.hp.hard.25 | 3.62 | 62 |
| curve.hp.hard.30 | 5.6 | 63 |
| curve.hp.hard.35 | 8.53 | 64 |
| curve.hp.hard.40 | 13.18 | 65 |
| curve.hp.hard.45 | 19.41 | 66 |
| curve.hp.hard.49 | 24.52 | 67 |
| curve.hp.hard.55 | 26.95 | 68 |
| curve.hp.hard.60 | 28.98 | 69 |
| curve.hp.custom.1 | 1 | 71 |
| curve.hp.custom.20 | 2.52 | 72 |
| curve.hp.custom.25 | 3.62 | 73 |
| curve.hp.custom.30 | 5.6 | 74 |
| curve.hp.custom.35 | 8.53 | 75 |
| curve.hp.custom.40 | 13.18 | 76 |
| curve.hp.custom.45 | 19.41 | 77 |
| curve.hp.custom.49 | 24.52 | 78 |
| curve.hp.custom.55 | 26.95 | 79 |
| curve.hp.custom.60 | 28.98 | 80 |
| curve.dmg.easy.1 | 1 | 82 |
| curve.dmg.easy.20 | 1.38 | 83 |
| curve.dmg.easy.25 | 1.75 | 84 |
| curve.dmg.easy.30 | 2.22 | 85 |
| curve.dmg.easy.35 | 2.77 | 86 |
| curve.dmg.easy.40 | 3.44 | 87 |
| curve.dmg.easy.45 | 4.36 | 88 |
| curve.dmg.easy.49 | 5.19 | 89 |
| curve.dmg.easy.55 | 5.47 | 90 |
| curve.dmg.easy.60 | 5.7 | 91 |
| curve.dmg.normal.1 | 1 | 93 |
| curve.dmg.normal.20 | 1.57 | 94 |
| curve.dmg.normal.25 | 2.04 | 95 |
| curve.dmg.normal.30 | 2.62 | 96 |
| curve.dmg.normal.35 | 3.33 | 97 |
| curve.dmg.normal.40 | 4.2 | 98 |
| curve.dmg.normal.45 | 5.39 | 99 |
| curve.dmg.normal.49 | 6.45 | 100 |
| curve.dmg.normal.55 | 6.89 | 101 |
| curve.dmg.normal.60 | 7.24 | 102 |
| curve.dmg.hard.1 | 1 | 104 |
| curve.dmg.hard.20 | 1.76 | 105 |
| curve.dmg.hard.25 | 2.32 | 106 |
| curve.dmg.hard.30 | 3.03 | 107 |
| curve.dmg.hard.35 | 3.89 | 108 |
| curve.dmg.hard.40 | 4.95 | 109 |
| curve.dmg.hard.45 | 6.41 | 110 |
| curve.dmg.hard.49 | 7.72 | 111 |
| curve.dmg.hard.55 | 8.31 | 112 |
| curve.dmg.hard.60 | 8.78 | 113 |
| curve.dmg.custom.1 | 1 | 115 |
| curve.dmg.custom.20 | 1.76 | 116 |
| curve.dmg.custom.25 | 2.32 | 117 |
| curve.dmg.custom.30 | 3.03 | 118 |
| curve.dmg.custom.35 | 3.89 | 119 |
| curve.dmg.custom.40 | 4.95 | 120 |
| curve.dmg.custom.45 | 6.41 | 121 |
| curve.dmg.custom.49 | 7.72 | 122 |
| curve.dmg.custom.55 | 8.31 | 123 |
| curve.dmg.custom.60 | 8.78 | 124 |
| part.gap | true | 126 |
| gap.free | 5 | 128 |
| gap.dealtStep | 2.5 | 130 |
| gap.dealtMin | 40 | 132 |
| gap.takenStep | 1.5 | 134 |
| gap.takenMax | 1.5 | 136 |
| bands.passThrough | River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_* | 138 |
| bands.volcanicTop | true | 140 |
| bands.islands | 0 | 142 |
| bands.default | 0 | 144 |
| plate.mode | all | 146 |
| plate.format | [Lv {level}] {name} | 148 |
| plate.strip | _Wander,_Patrol,_Surge,_Static,_Sleep | 150 |
| plate.colorOn | false | 152 |
| plate.markup | tag | 154 |
| plate.colors.1 | #d6e4ee | 156 |
| plate.colors.20 | #ffcc00 | 157 |
| plate.colors.30 | #E8A93B | 158 |
| plate.colors.45 | #ff6b6b | 159 |
| plate.colors.61 | #CC66CC | 160 |

## SkyyMobs / bands.properties

| key | value | L |
|---|---|---|
| biome.Zone1_Spawn | 1,3 | 9 |
| biome.Zone1_Temple | 1,3 | 10 |
| biome.Zone1_Tier1.Plains_Smooth | 1,3 | 11 |
| biome.Zone1_Tier1.Plains_Birch | 3,5 | 12 |
| biome.Zone1_Tier1.Forest_Birch | 5,7 | 13 |
| biome.Zone1_Tier1.Forest_Flower | 5,7 | 14 |
| biome.Zone1_Tier1.Mountain_Tier1 | 5,7 | 15 |
| biome.Zone1_Tier1.Forest_Birch_Trork | 5,7 | 16 |
| biome.Zone1_Tier1.Forest_Flower_Trork | 5,7 | 17 |
| biome.Zone1_Tier1.Plains_Birch_Trork | 5,7 | 18 |
| biome.Zone1_Tier1.Plains_Smooth_Trork | 5,7 | 19 |
| biome.Zone1_Tier1 | 1,7 | 20 |
| biome.Zone1_Tier2.Plains_Gorge | 7,9 | 21 |
| biome.Zone1_Tier2.Plains_Tallgrass | 9,11 | 22 |
| biome.Zone1_Tier2.Forest_Aspen | 10,12 | 23 |
| biome.Zone1_Tier2.Forest_Gully | 10,12 | 24 |
| biome.Zone1_Tier2.Mountain_Tier2 | 10,12 | 25 |
| biome.Zone1_Tier2.Forest_Aspen_Trork | 10,12 | 26 |
| biome.Zone1_Tier2.Forest_Gully_Trork | 10,12 | 27 |
| biome.Zone1_Tier2.Plains_Tallgrass_Trork | 10,12 | 28 |
| biome.Zone1_Tier2 | 7,12 | 29 |
| biome.Zone1_Tier3.Plains_Gorge | 12,14 | 30 |
| biome.Zone1_Tier3.Forest_Swamp | 16,18 | 31 |
| biome.Zone1_Tier3.Mountain_Tier3 | 16,18 | 32 |
| biome.Zone1_Tier3.Forest_Autumn_Trork | 16,18 | 33 |
| biome.Zone1_Tier3.Forest_Moss_Trork | 16,18 | 34 |
| biome.Zone1_Tier3.Forest_Autumn | 18,20 | 35 |
| biome.Zone1_Tier3.Forest_Moss | 18,20 | 36 |
| biome.Zone1_Tier3.Forest_Azure | 18,20 | 37 |
| biome.Zone1_Tier3 | 12,20 | 38 |
| biome.Zone1_Shore | 1,3 | 39 |
| biome.Zone2_Tier1.Savannah_Forest | 20,22 | 41 |
| biome.Zone2_Tier1.Savannah_Plains | 20,22 | 42 |
| biome.Zone2_Tier1.Savannah_Boab | 20,22 | 43 |
| biome.Zone2_Tier1.Savannah_Rock | 20,22 | 44 |
| biome.Zone2_Tier1.Savannah_Mudflats | 20,22 | 45 |
| biome.Zone2_Tier1.Plateau_Savannah_Boab | 21,23 | 46 |
| biome.Zone2_Tier1.Plateau_Savannah_Forest | 21,23 | 47 |
| biome.Zone2_Tier1.Plateau_Savannah_Plains | 21,23 | 48 |
| biome.Zone2_Tier1.Plateau_Savannah_Rock | 21,23 | 49 |
| biome.Zone2_Tier1.Plateau_Scrub_Bushland | 21,23 | 50 |
| biome.Zone2_Tier1.Scrub_Bushland | 22,24 | 51 |
| biome.Zone2_Tier1 | 20,24 | 52 |
| biome.Zone2_Tier2.Desert_Oasis | 25,27 | 53 |
| biome.Zone2_Tier2.Desert_Rock | 25,27 | 54 |
| biome.Zone2_Tier2.Desert_Springs | 25,27 | 55 |
| biome.Zone2_Tier2.Desert_Red | 25,27 | 56 |
| biome.Zone2_Tier2 | 25,27 | 57 |
| biome.Zone2_Tier3.Desert_Barren | 27,29 | 58 |
| biome.Zone2_Tier3.Desert_Mushroom | 27,29 | 59 |
| biome.Zone2_Tier3.Plateau_Desert_Barren | 28,30 | 60 |
| biome.Zone2_Tier3.Plateau_Desert_Mushroom | 28,30 | 61 |
| biome.Zone2_Tier3.Desert_Oasis_Hidden | 28,30 | 62 |
| biome.Zone2_Tier3.Desert_Oasis_Hidden_Dunes | 28,30 | 63 |
| biome.Zone2_Tier3.Scrub_Tar_Pits | 28,30 | 64 |
| biome.Zone2_Tier3.Desert_Mushroom_Foot | 28,30 | 65 |
| biome.Zone2_Tier3 | 27,30 | 66 |
| biome.Zone2_Shore | 20,22 | 67 |
| biome.Zone3_Tier1.Forest_Redwood | 30,32 | 69 |
| biome.Zone3_Tier1.Plains_Shire | 30,32 | 70 |
| biome.Zone3_Tier1.Forest_Fir | 32,34 | 71 |
| biome.Zone3_Tier1.Forest_Tundra | 32,34 | 72 |
| biome.Zone3_Tier1.Plains_Hotsprings | 32,34 | 73 |
| biome.Zone3_Tier1.Mountain_Zone3_Tier1 | 32,34 | 74 |
| biome.Zone3_Tier1 | 30,34 | 75 |
| biome.Zone3_Tier2.Forest_Cedar | 36,38 | 76 |
| biome.Zone3_Tier2.Plains_Frozen | 37,39 | 77 |
| biome.Zone3_Tier2.Forest_Cedar_Mixed | 37,39 | 78 |
| biome.Zone3_Tier2.Plains_Tundra | 37,39 | 79 |
| biome.Zone3_Tier2.Mountain_Zone3_Tier2 | 37,39 | 80 |
| biome.Zone3_Tier2 | 36,39 | 81 |
| biome.Zone3_Tier3.Forest_Frozen | 41,43 | 82 |
| biome.Zone3_Tier3.Forest_Frozen_Light | 41,43 | 83 |
| biome.Zone3_Tier3.Plains_Frozen_Frost | 41,43 | 84 |
| biome.Zone3_Tier3.Mountain_Zone3_Tier3 | 43,45 | 85 |
| biome.Zone3_Tier3 | 41,45 | 86 |
| biome.Zone3_Shore_Tier1 | 30,32 | 87 |
| biome.Zone3_Shore_Tier2 | 36,38 | 88 |
| biome.Zone3_Shore_Tier3 | 41,43 | 89 |
| biome.Zone4_Tier4.Wastes_Grasslands | 45,47 | 91 |
| biome.Zone4_Tier4.Wastes_Geysers | 48,50 | 92 |
| biome.Zone4_Tier4.Forest_Ghost | 48,50 | 93 |
| biome.Zone4_Tier4.Desert_Dunes | 48,50 | 94 |
| biome.Zone4_Tier4.Forest_Swamp | 48,50 | 95 |
| biome.Zone4_Tier4 | 45,50 | 96 |
| biome.Zone4_Tier5.Desert_Ash | 53,55 | 97 |
| biome.Zone4_Tier5.Wastes_Ash | 53,55 | 98 |
| biome.Zone4_Tier5.Wastes_Lava | 55,57 | 99 |
| biome.Zone4_Tier5.Forest_Burned | 58,60 | 100 |
| biome.Zone4_Tier5.Forest_Roots | 58,60 | 101 |
| biome.Zone4_Tier5 | 53,60 | 102 |
| biome.Zone4_Shore_Tier4 | 45,47 | 103 |
| biome.Zone4_Shore_Tier5 | 53,55 | 104 |
| env.Env_Zone1_Plains | 1,3,0 | 108 |
| env.Env_Zone1_Shores | 1,3,0 | 109 |
| env.Env_Zone1_Kweebec | 1,3,0 | 110 |
| env.Env_Zone1_Forests | 5,9,0 | 111 |
| env.Env_Zone1_Mountains | 5,14,0 | 112 |
| env.Env_Zone1_Trork | 5,16,0 | 113 |
| env.Env_Zone1_Swamps | 14,20,0 | 114 |
| env.Env_Zone1_Autumn | 16,20,0 | 115 |
| env.Env_Zone1_Azure | 16,20,0 | 116 |
| env.Env_Zone1_Caves | 5,14,0 | 117 |
| env.Env_Zone1_Caves_Forests | 5,14,0 | 118 |
| env.Env_Zone1_Caves_Mountains | 5,14,0 | 119 |
| env.Env_Zone1_Caves_Plains | 5,14,0 | 120 |
| env.Env_Zone1_Caves_Rats | 5,14,0 | 121 |
| env.Env_Zone1_Caves_Spiders | 5,14,0 | 122 |
| env.Env_Zone1_Caves_Swamps | 5,14,0 | 123 |
| env.Env_Zone1_Caves_Volcanic_T1 | 5,9,0 | 124 |
| env.Env_Zone1_Caves_Volcanic_T2 | 9,14,0 | 125 |
| env.Env_Zone1_Caves_Volcanic_T3 | 14,18,0 | 126 |
| env.Env_Zone1_Caves_Goblins | 5,16,1 | 127 |
| env.Env_Zone1_Mineshafts | 5,16,1 | 128 |
| env.Env_Zone1_Encounters | 9,18,2 | 129 |
| env.Env_Zone1_Graveyard | 9,18,2 | 130 |
| env.Env_Zone1_Mage_Towers | 9,18,2 | 131 |
| env.Env_Zone1_Dungeons | 14,20,2 | 132 |
| env.Env_Zone2_Savanna | 20,22,0 | 133 |
| env.Env_Zone2_Shores | 20,22,0 | 134 |
| env.Env_Zone2_Scrub | 22,24,0 | 135 |
| env.Env_Zone2_Plateaus | 21,27,0 | 136 |
| env.Env_Zone2_Deserts | 25,29,0 | 137 |
| env.Env_Zone2_Oasis | 25,30,0 | 138 |
| env.Env_Zone2_Feran | 23,28,1 | 139 |
| env.Env_Zone2_Scarak | 23,28,1 | 140 |
| env.Env_Zone2_Caves | 21,27,0 | 141 |
| env.Env_Zone2_Caves_Deserts | 21,27,0 | 142 |
| env.Env_Zone2_Caves_Plateaus | 21,27,0 | 143 |
| env.Env_Zone2_Caves_Rats | 21,27,0 | 144 |
| env.Env_Zone2_Caves_Savanna | 21,27,0 | 145 |
| env.Env_Zone2_Caves_Scarak | 21,27,0 | 146 |
| env.Env_Zone2_Caves_Scrub | 21,27,0 | 147 |
| env.Env_Zone2_Caves_Volcanic_T1 | 21,23,0 | 148 |
| env.Env_Zone2_Caves_Volcanic_T2 | 25,27,0 | 149 |
| env.Env_Zone2_Caves_Volcanic_T3 | 28,30,0 | 150 |
| env.Env_Zone2_Mineshafts | 23,27,1 | 151 |
| env.Env_Zone2_Caves_Goblins | 23,27,1 | 152 |
| env.Env_Zone2_Encounters | 25,29,2 | 153 |
| env.Env_Zone2_Mage_Towers | 25,29,2 | 154 |
| env.Env_Zone2_Dungeons | 27,30,2 | 155 |
| env.Env_Zone3_Tundra | 30,35,0 | 156 |
| env.Env_Zone3_Shores | 30,33,0 | 157 |
| env.Env_Zone3_Forests | 30,38,0 | 158 |
| env.Env_Zone3_Mountains | 35,41,0 | 159 |
| env.Env_Zone3_Glacial | 38,45,0 | 160 |
| env.Env_Zone3_Caves | 32,41,0 | 161 |
| env.Env_Zone3_Caves_Forests | 32,41,0 | 162 |
| env.Env_Zone3_Caves_Glacial | 32,41,0 | 163 |
| env.Env_Zone3_Caves_Mountains | 32,41,0 | 164 |
| env.Env_Zone3_Caves_Spider | 32,41,0 | 165 |
| env.Env_Zone3_Caves_Tundra | 32,41,0 | 166 |
| env.Env_Zone3_Caves_Volcanic_T1 | 32,41,0 | 167 |
| env.Env_Zone3_Caves_Volcanic_T2 | 32,41,0 | 168 |
| env.Env_Zone3_Caves_Volcanic_T3 | 32,41,0 | 169 |
| env.Env_Zone3_Trork | 35,42,1 | 170 |
| env.Env_Zone3_Outlander | 39,45,2 | 171 |
| env.Env_Zone3_Outlander_Village | 39,45,2 | 172 |
| env.Env_Zone3_Encounters | 39,45,2 | 173 |
| env.Env_Zone4_Wastes | 45,50,0 | 174 |
| env.Env_Zone4_Shores | 45,47,0 | 175 |
| env.Env_Zone4_Crucible | 48,50,0 | 176 |
| env.Env_Zone4_Volcanoes | 48,57,0 | 177 |
| env.Env_Zone4_Forests | 48,60,0 | 178 |
| env.Env_Zone4_Jungles | 50,58,0 | 179 |
| env.Env_Zone4_Encounters | 53,60,2 | 180 |
| env.Env_Zone4_Encounters_Forest | 53,60,2 | 181 |
| env.Env_Zone4_Villages | 55,60,2 | 182 |
| env.Env_Zone4_Villages_Forests | 55,60,2 | 183 |
| env.Env_Zone4_Villages_Swamp | 55,60,2 | 184 |
| env.Env_Portal_Goblin_Surface | 5,8,0 | 185 |
| env.Env_Portal_Goblin_Cave | 7,10,0 | 186 |
| env.Env_Portal_Goblin_Cave_Deep | 9,11,0 | 187 |
| env.Env_Portal_Goblin_Cave_Void | 10,12,0 | 188 |
| zone.Zone1 | 1,7 | 191 |
| zone.Zone2 | 20,24 | 192 |
| zone.Zone3 | 30,34 | 193 |
| zone.Zone4 | 45,50 | 194 |

## SkyyClasses / config.properties

| key | value | L |
|---|---|---|
| switchCost | 5000 | 5 |
| cooldownMinutes | 60 | 7 |
| requireClass | false | 9 |
| unassignedBlocked | true | 11 |
| promptEveryLogin | true | 13 |
| openDelayMillis | 2000 | 15 |
| kits.enabled | true | 20 |
| kit.Archer | Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64 | 23 |
| kit.Warrior | Weapon_Sword_Crude:1,Weapon_Shield_Wood:1 | 25 |
| kit.Mage | Weapon_Staff_Wood:1 | 26 |
| kit.Berserker | Weapon_Battleaxe_Crude:1 | 27 |
| kit.Priest | Weapon_Wand_Wood:1 | 28 |
| kit.Assassin | Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1 | 30 |
| kit.Monk | Weapon_Staff_Bo_Wood:1 | 31 |
| kit.Spellblade | Weapon_Longsword_Crude:1 | 32 |
| priestHeal.enabled | true | 42 |
| priestHeal.sharePercent | 25 | 43 |
| priestHeal.selfPercent | 100 | 44 |
| priestHeal.radius | 16 | 45 |
| priestHeal.hpPerMana | 2 | 46 |
| priestHeal.quickPercent | 20 | 47 |
| priestHeal.maxPerHit | 10 | 48 |
| priestHeal.maxPerSecond | 10 | 49 |
| priestHeal.othersPercent | 50 | 52 |
| priestHeal.messages | true | 55 |
| priestHeal.feedbackMs | 10000 | 56 |
| arrows.enabled | true | 59 |
| arrows.item | Weapon_Arrow_Crude | 61 |
| arrows.amount | 64 | 62 |
| arrows.cooldownHours | 24 | 64 |
| part.abilities | true | 75 |
| abil.creativeFree | true | 76 |
| abil.castChat | true | 77 |
| abil.refuse | 1 | 78 |
| abil.cdMessage | true | 79 |
| abil.healCap | 60 | 80 |
| abil.unlock.a1 | 1 | 81 |
| abil.unlock.a2 | 10 | 82 |
| abil.unlock.a2alt | 20 | 83 |
| abil.unlock.a1alt | 30 | 84 |
| abil.hitFallback | 25 | 85 |
| abil.maxLive | 48 | 86 |
| abil.safeWords | Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub | 87 |
| ab.Meteor.walk.mana | 23 | 88 |
| ab.Meteor.walk.stamina | 2 | 89 |
| ab.Meteor.walk.cooldown | 14 | 90 |
| ab.Meteor.power | 3 | 91 |
| ab.Meteor.radius | 4 | 92 |
| ab.Meteor.delay | 1 | 93 |
| ab.Meteor.range | 25 | 94 |
| ab.SacredHeal.walk.mana | 18 | 95 |
| ab.SacredHeal.walk.stamina | 2 | 96 |
| ab.SacredHeal.walk.cooldown | 14 | 97 |
| ab.SacredHeal.heal | 25 | 98 |
| ab.SacredHeal.selfBonus | 20 | 99 |
| ab.SacredHeal.radius | 9 | 100 |
| ab.SacredHeal.hot | 40 | 101 |
| ab.SacredHeal.hotTime | 4 | 102 |
| abil.tick | 0.25 | 103 |
| abil.maxZones | 2 | 104 |
| ab.ManaBarrier.walk.mana | 16 | 105 |
| ab.ManaBarrier.walk.stamina | 1 | 106 |
| ab.ManaBarrier.walk.cooldown | 30 | 107 |
| ab.ManaBarrier.time | 12 | 108 |
| ab.ManaBarrier.radius | 4 | 109 |
| ab.ManaBarrier.range | 8 | 110 |
| ab.ManaBarrier.ratio | 2 | 111 |
| ab.ManaBarrier.keep | 4 | 112 |
| ab.ManaBarrier.maxAbsorb | 100 | 113 |
| ab.ShieldBubble.walk.mana | 20 | 114 |
| ab.ShieldBubble.walk.stamina | 2 | 115 |
| ab.ShieldBubble.walk.cooldown | 24 | 116 |
| ab.ShieldBubble.time | 12 | 117 |
| ab.ShieldBubble.radius | 6 | 118 |
| ab.ShieldBubble.range | 8 | 119 |
| ab.ShieldBubble.hp | 100 | 120 |
| ab.ShieldBubble.pulse | 8 | 121 |
| ab.Meteor.sprint.mana | 23 | 122 |
| ab.Meteor.sprint.stamina | 2 | 123 |
| ab.Meteor.sprint.cooldown | 14 | 124 |
| ab.Meteor.air.mana | 23 | 125 |
| ab.Meteor.air.stamina | 2 | 126 |
| ab.Meteor.air.cooldown | 16 | 127 |
| ab.Meteor.crouch.mana | 20 | 128 |
| ab.Meteor.crouch.stamina | 1 | 129 |
| ab.Meteor.crouch.cooldown | 14 | 130 |
| ab.ManaBarrier.sprint.mana | 16 | 131 |
| ab.ManaBarrier.sprint.stamina | 1 | 132 |
| ab.ManaBarrier.sprint.cooldown | 30 | 133 |
| ab.ManaBarrier.air.mana | 16 | 134 |
| ab.ManaBarrier.air.stamina | 1 | 135 |
| ab.ManaBarrier.air.cooldown | 30 | 136 |
| ab.ManaBarrier.crouch.mana | 14 | 137 |
| ab.ManaBarrier.crouch.stamina | 1 | 138 |
| ab.ManaBarrier.crouch.cooldown | 28 | 139 |
| ab.FrostNova.walk.mana | 19 | 140 |
| ab.FrostNova.walk.stamina | 1 | 141 |
| ab.FrostNova.walk.cooldown | 22 | 142 |
| ab.FrostNova.sprint.mana | 19 | 143 |
| ab.FrostNova.sprint.stamina | 1 | 144 |
| ab.FrostNova.sprint.cooldown | 22 | 145 |
| ab.FrostNova.air.mana | 19 | 146 |
| ab.FrostNova.air.stamina | 1 | 147 |
| ab.FrostNova.air.cooldown | 24 | 148 |
| ab.FrostNova.crouch.mana | 20 | 149 |
| ab.FrostNova.crouch.stamina | 1 | 150 |
| ab.FrostNova.crouch.cooldown | 24 | 151 |
| ab.Starfall.walk.mana | 28 | 152 |
| ab.Starfall.walk.stamina | 2 | 153 |
| ab.Starfall.walk.cooldown | 18 | 154 |
| ab.Starfall.sprint.mana | 28 | 155 |
| ab.Starfall.sprint.stamina | 2 | 156 |
| ab.Starfall.sprint.cooldown | 18 | 157 |
| ab.Starfall.air.mana | 28 | 158 |
| ab.Starfall.air.stamina | 2 | 159 |
| ab.Starfall.air.cooldown | 20 | 160 |
| ab.Starfall.crouch.mana | 31 | 161 |
| ab.Starfall.crouch.stamina | 2 | 162 |
| ab.Starfall.crouch.cooldown | 22 | 163 |
| ab.ArcaneBeam.walk.mana | 23 | 164 |
| ab.ArcaneBeam.walk.stamina | 2 | 165 |
| ab.ArcaneBeam.walk.cooldown | 18 | 166 |
| ab.ArcaneBeam.sprint.mana | 22 | 167 |
| ab.ArcaneBeam.sprint.stamina | 2 | 168 |
| ab.ArcaneBeam.sprint.cooldown | 18 | 169 |
| ab.ArcaneBeam.air.mana | 23 | 170 |
| ab.ArcaneBeam.air.stamina | 2 | 171 |
| ab.ArcaneBeam.air.cooldown | 20 | 172 |
| ab.ArcaneBeam.crouch.mana | 27 | 173 |
| ab.ArcaneBeam.crouch.stamina | 2 | 174 |
| ab.ArcaneBeam.crouch.cooldown | 22 | 175 |
| ab.SacredHeal.sprint.mana | 18 | 176 |
| ab.SacredHeal.sprint.stamina | 2 | 177 |
| ab.SacredHeal.sprint.cooldown | 14 | 178 |
| ab.SacredHeal.air.mana | 18 | 179 |
| ab.SacredHeal.air.stamina | 2 | 180 |
| ab.SacredHeal.air.cooldown | 14 | 181 |
| ab.SacredHeal.crouch.mana | 20 | 182 |
| ab.SacredHeal.crouch.stamina | 2 | 183 |
| ab.SacredHeal.crouch.cooldown | 16 | 184 |
| ab.ShieldBubble.sprint.mana | 20 | 185 |
| ab.ShieldBubble.sprint.stamina | 2 | 186 |
| ab.ShieldBubble.sprint.cooldown | 24 | 187 |
| ab.ShieldBubble.air.mana | 20 | 188 |
| ab.ShieldBubble.air.stamina | 2 | 189 |
| ab.ShieldBubble.air.cooldown | 24 | 190 |
| ab.ShieldBubble.crouch.mana | 20 | 191 |
| ab.ShieldBubble.crouch.stamina | 2 | 192 |
| ab.ShieldBubble.crouch.cooldown | 26 | 193 |
| ab.Sanctuary.walk.mana | 26 | 194 |
| ab.Sanctuary.walk.stamina | 2 | 195 |
| ab.Sanctuary.walk.cooldown | 28 | 196 |
| ab.Sanctuary.sprint.mana | 26 | 197 |
| ab.Sanctuary.sprint.stamina | 2 | 198 |
| ab.Sanctuary.sprint.cooldown | 28 | 199 |
| ab.Sanctuary.air.mana | 26 | 200 |
| ab.Sanctuary.air.stamina | 2 | 201 |
| ab.Sanctuary.air.cooldown | 28 | 202 |
| ab.Sanctuary.crouch.mana | 26 | 203 |
| ab.Sanctuary.crouch.stamina | 2 | 204 |
| ab.Sanctuary.crouch.cooldown | 30 | 205 |
| ab.MartyrsGrace.walk.mana | 22 | 206 |
| ab.MartyrsGrace.walk.stamina | 2 | 207 |
| ab.MartyrsGrace.walk.cooldown | 18 | 208 |
| ab.MartyrsGrace.sprint.mana | 22 | 209 |
| ab.MartyrsGrace.sprint.stamina | 2 | 210 |
| ab.MartyrsGrace.sprint.cooldown | 18 | 211 |
| ab.MartyrsGrace.air.mana | 22 | 212 |
| ab.MartyrsGrace.air.stamina | 2 | 213 |
| ab.MartyrsGrace.air.cooldown | 18 | 214 |
| ab.MartyrsGrace.crouch.mana | 25 | 215 |
| ab.MartyrsGrace.crouch.stamina | 2 | 216 |
| ab.MartyrsGrace.crouch.cooldown | 20 | 217 |
| ab.FlowingForm.walk.mana | 2 | 218 |
| ab.FlowingForm.walk.stamina | 1 | 219 |
| ab.FlowingForm.walk.cooldown | 40 | 220 |
| ab.PalmStrike.walk.mana | 3 | 221 |
| ab.PalmStrike.walk.stamina | 1 | 222 |
| ab.PalmStrike.walk.cooldown | 6 | 223 |
| ab.CycloneKick.walk.mana | 4 | 224 |
| ab.CycloneKick.walk.stamina | 2 | 225 |
| ab.CycloneKick.walk.cooldown | 8 | 226 |
| ab.HundredFists.walk.mana | 3 | 227 |
| ab.HundredFists.walk.stamina | 1 | 228 |
| ab.HundredFists.walk.cooldown | 40 | 229 |
| ab.StillWater.walk.mana | 7 | 230 |
| ab.StillWater.walk.stamina | 3 | 231 |
| ab.StillWater.walk.cooldown | 25 | 232 |
| ab.CloakFirstStrike.walk.mana | 6 | 233 |
| ab.CloakFirstStrike.walk.stamina | 2 | 234 |
| ab.CloakFirstStrike.walk.cooldown | 30 | 235 |
| ab.Toxin.walk.mana | 5 | 236 |
| ab.Toxin.walk.stamina | 2 | 237 |
| ab.Toxin.walk.cooldown | 16 | 238 |
| ab.GodKiller.walk.mana | 6 | 239 |
| ab.GodKiller.walk.stamina | 2 | 240 |
| ab.GodKiller.walk.cooldown | 45 | 241 |
| ab.VanishingAct.walk.mana | 7 | 242 |
| ab.VanishingAct.walk.stamina | 2 | 243 |
| ab.VanishingAct.walk.cooldown | 28 | 244 |
| abil.shapes | true | 245 |
| abil.shapes.sprint | true | 246 |
| abil.shapes.air | true | 247 |
| abil.crouchMin | 0.1 | 248 |
| abil.airMin | 0.15 | 249 |
| abil.landWait | 2 | 250 |
| abil.ahead | 6 | 251 |
| abil.channelMove | 1 | 252 |
| ab.Meteor.cometRadius | 3 | 253 |
| ab.Meteor.onMeRadius | 5 | 254 |
| ab.Meteor.onMePower | 2.5 | 255 |
| ab.Meteor.onMeDelay | 0.5 | 256 |
| ab.ManaBarrier.pocketRadius | 4 | 257 |
| ab.ManaBarrier.pocketTime | 10 | 258 |
| ab.ManaBarrier.pocketRatio | 2.5 | 259 |
| ab.ShieldBubble.aroundRadius | 5 | 260 |
| ab.ShieldBubble.aroundHp | 110 | 261 |
| ab.SacredHeal.blessRadius | 6 | 262 |
| ab.SacredHeal.blessTime | 2 | 263 |
| ab.SacredHeal.blessHeal | 20 | 264 |
| ab.SacredHeal.beaconRadius | 10 | 265 |
| ab.SacredHeal.kneelBonus | 20 | 266 |
| ab.SacredHeal.kneelHot | 200 | 267 |
| ab.SacredHeal.kneelTime | 1 | 268 |
| ab.FrostNova.radius | 5 | 269 |
| ab.FrostNova.power | 1 | 270 |
| ab.FrostNova.freeze | 2 | 271 |
| ab.FrostNova.breakAfter | 1 | 272 |
| ab.FrostNova.breakPower | 0.5 | 273 |
| ab.FrostNova.chill | 3 | 274 |
| ab.FrostNova.wakeLength | 8 | 275 |
| ab.FrostNova.wakeWidth | 2 | 276 |
| ab.FrostNova.wakeTime | 3 | 277 |
| ab.FrostNova.wakeFreeze | 1.5 | 278 |
| ab.FrostNova.dropRadius | 6 | 279 |
| ab.FrostNova.deepRadius | 4 | 280 |
| ab.FrostNova.deepFreeze | 3 | 281 |
| abil.freezeStun | true | 282 |
| ab.FrostNova.deepBreak | 2 | 283 |
| abil.bossWords | Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti | 284 |
| ab.Starfall.stars | 12 | 285 |
| ab.Starfall.time | 3 | 286 |
| ab.Starfall.radius | 6 | 287 |
| ab.Starfall.power | 0.3 | 288 |
| ab.Starfall.starRadius | 3 | 289 |
| ab.Starfall.range | 25 | 290 |
| ab.Starfall.belowRadius | 7 | 291 |
| ab.Starfall.belowTime | 2 | 292 |
| ab.Starfall.showerStars | 16 | 293 |
| ab.Starfall.showerTime | 4 | 294 |
| ab.ArcaneBeam.range | 20 | 295 |
| ab.ArcaneBeam.time | 3 | 296 |
| ab.ArcaneBeam.rate | 0.5 | 297 |
| ab.ArcaneBeam.ramp | 3 | 298 |
| ab.ArcaneBeam.width | 1 | 299 |
| ab.ArcaneBeam.sweepRange | 15 | 300 |
| ab.ArcaneBeam.sweepTime | 2 | 301 |
| ab.ArcaneBeam.sweepMult | 1.5 | 302 |
| ab.ArcaneBeam.sweepWidth | 2 | 303 |
| ab.ArcaneBeam.downRange | 12 | 304 |
| ab.ArcaneBeam.downTime | 2 | 305 |
| ab.ArcaneBeam.focusRange | 25 | 306 |
| ab.ArcaneBeam.focusTime | 4 | 307 |
| ab.ArcaneBeam.focusRamp | 3.5 | 308 |
| ab.GuardianSpirit.mana | 15 | 309 |
| ab.GuardianSpirit.stamina | 1 | 310 |
| ab.GuardianSpirit.health | 30 | 311 |
| ab.GuardianSpirit.cooldown | 12 | 312 |
| ab.GuardianSpirit.resetAfter | 30 | 313 |
| ab.GuardianSpirit.radius | 30 | 314 |
| ab.GuardianSpirit.everyone | false | 315 |
| ab.Sanctuary.radius | 8 | 316 |
| ab.Sanctuary.time | 12 | 317 |
| ab.Sanctuary.heal | 5 | 318 |
| ab.Sanctuary.cut | 10 | 319 |
| ab.Sanctuary.ahead | 5 | 320 |
| ab.Sanctuary.innerRadius | 5 | 321 |
| ab.Sanctuary.innerHeal | 7 | 322 |
| ab.Sanctuary.innerCut | 15 | 323 |
| ab.Sanctuary.innerTime | 10 | 324 |
| ab.MartyrsGrace.range | 30 | 325 |
| ab.MartyrsGrace.first | 75 | 326 |
| ab.MartyrsGrace.drop | 15 | 327 |
| ab.MartyrsGrace.targets | 5 | 328 |
| ab.MartyrsGrace.firstCap | 90 | 329 |
| ab.MartyrsGrace.vowFirst | 90 | 330 |
| ab.MartyrsGrace.vowDrop | 20 | 331 |
| ab.MartyrsGrace.vowTime | 1 | 332 |
| abil.runeKeys | true | 333 |
| abil.castCmd | true | 334 |
| abil.vanillaRunes | false | 335 |
| abil.runeHud | true | 336 |
| abil.runeCooldownFill | false | 337 |
| abil.runeFallback | true | 338 |
| abil.rollCast | true | 339 |
| abil.treeGate | true | 340 |
| abil.levels | true | 341 |
| abil.maxLevel | 25 | 342 |
| abil.usesCoef | 4.5 | 343 |
| abil.usesExp | 1.5 | 344 |
| abil.useEvery | 3 | 345 |
| abil.perLevel | 2 | 346 |
| abil.softLevel | 10 | 347 |
| abil.halfLevel | 20 | 348 |
| mods.on | true | 349 |
| mods.unlock | 2,4,6,8,10 | 350 |
| mods.steps | 10,30,60,100 | 351 |
| mods.power | 5 | 352 |
| mods.radius | 0.5 | 353 |
| mods.duration | 10 | 354 |
| mods.efficiency | 5 | 355 |
| mods.echoBase | 20 | 356 |
| mods.echoStep | 2.5 | 357 |
| abil.echoDelay | 1 | 358 |
| ab.GodKiller.eliteWords | Elite,Captain,Champion,Alpha,Brute | 359 |
| ab.FlowingForm.numbers | drainMana=0.65,drainStamina=0.25,time=30,radius=5,maxStacks=20,decay=5,movePerStack=2,attackPerStack=1.5,awedDefence=1,aweLinger=10,distract=1,sprintStacks=2,sprintFree=3,centredStacks=3,centredRadius=4,centredDrain=25,countAt=5 | 360 |
| ab.HundredFists.numbers | drainMana=0.7,drainStamina=0.3,every=10,power=1,gap=8,sprintEvery=8,tempestEvery=12,tempestPower=1.3 | 361 |
| ab.StillWater.numbers | time=10,counter=1,front=90,gap=0.4,sprintTime=6,landRadius=2,landPower=0.5,deepTime=12,deepPower=1.3,echoTime=3 | 362 |
| ab.PalmStrike.numbers | power=1.2,stun=0.75,push=4,reach=4,cdFloor=5,cdPerLevel=0.1,sprintStep=2,sprintPush=6,sprintStun=0.5,airStun=1,rootStun=1.25 | 363 |
| ab.CycloneKick.numbers | radius=3,power=0.8,push=5,sweepRadius=4,sweepPush=6,dropRadius=4,legStun=1,haste=20 | 364 |
| ab.CloakFirstStrike.numbers | time=8,window=10,strike=50,lose=24,dashTime=6,dashSpeed=20,stillTime=11,stillBonus=20,haste=20 | 365 |
| ab.Toxin.numbers | range=20,radius=4,time=5,poison=0.25,weaken=15,lobRange=28,lobRadius=3.5,poolRadius=5,poolTime=6,chainRange=6 | 366 |
| ab.GodKiller.numbers | window=12,mult=2,backMult=3,backAngle=80,rushWindow=8,rushSpeed=15,patientWindow=20,haste=25 | 367 |
| ab.VanishingAct.numbers | cloak=3,radius=4,time=3,lose=2,slow=25,dropRadius=5,ambushCloak=5 | 368 |
| ab.RallyingGuard.numbers | mana=5,stamina=2,cooldown=24,time=10,cut=20,cutCap=40,party=10,players=6,taunt=8,tauntTime=6,chargeTime=1.5,chargeRadius=4,chargeTaunt=6,landTaunt=10,holdTaunt=16,holdTime=6,holdCut=10,echoTime=3 | 369 |
| ab.ShieldShockwave.numbers | mana=4,stamina=2,cooldown=12,range=6,angle=45,power=1,stun=1.5,stunLevel=0.03,step=2,sprintRange=7,sprintPower=1.2,sprintStun=1.2,poundRadius=4,poundStun=1.5,poundUp=4,ringRadius=3,ringPower=0.8,echoStun=0.5,retriPct=20,retriGap=20 | 370 |
| ab.IronChain.numbers | mana=5,stamina=2,cooldown=14,range=15,power=0.6,stun=1,meetStun=0.8,hookPower=0.8,hookUp=6,anchorRange=20,anchorStun=1.5,anchorRoot=1,anchorPull=60,chainRange=4,barbed=25,barbedTime=5 | 371 |
| ab.Challenge.numbers | mana=5,stamina=2,cooldown=20,range=12,time=8,cut=30,reflect=20,step=2,sprintTime=6,landRadius=8,duelTime=10,duelCut=40,duelReflect=30,chainRange=4 | 372 |
| ab.GuardiansOath.numbers | mana=5,stamina=2,cooldown=22,range=15,time=8,share=40,cut=15,rushRange=8,rushSpeed=20,burdenTime=10,burdenShare=50,burdenCut=25,leash=30 | 373 |
| ab.Enrage.numbers | mana=3,stamina=3,cooldown=30,grow=10,hold=5,start=10,peak=20,selfMult=2,selfCap=60,players=8,party=16,chargeTime=2,chargeRadius=4,leapAdd=2,loneBonus=10,loneHold=8,hornDelay=3,hornStart=15,rallyShield=10,fade=3 | 374 |
| ab.Whirlwind.numbers | mana=3,stamina=2,cooldown=14,time=3,radius=3,every=0.5,power=0.5,heal=10,sprintTime=2.5,sprintRadius=2.5,dropPower=1,grindEvery=0.4,grindRadius=3.5,bleed=0.2,bleedTime=4 | 375 |
| ab.Earthsplitter.numbers | mana=3,stamina=3,cooldown=12,length=12,width=2,power=2,up=3,missingCap=50,sprintLength=16,sprintWidth=1.4,sprintPower=1.8,craterRadius=5,wind=1,fissureLength=8,fissurePower=2.4,fissureSlow=2,splitAngle=20,poundRadius=2.5,poundPower=1.5,pactCost=10,pactBonus=30 | 376 |
| ab.BloodFrenzy.numbers | mana=1,stamina=1,cooldown=10,hitMana=0.7,hitStam=0.6,drainMana=0.15,drainStam=0.1,max=25,decay=6,dmg=1.5,move=0.5,ally=50,players=8,party=16,chargeStacks=3,landStacks=2,bankWindow=20,bankShare=50,bankPlayers=6,bankParty=12,hasteAt=10,hasteSpeed=10,countAt=10 | 377 |
| ab.WarlordsBanner.numbers | mana=9,stamina=8,cooldown=40,time=30,radius=12,players=8,party=12,self=16,killAdd=1,miniAdd=3,bossAdd=5,cap=60,ahead=6,landAdd=2,rootedRadius=10,rootedTime=40,echoTime=4,bearerHeal=1,bearerTime=25 | 378 |
| ab.PinningShot.numbers | mana=4,stamina=1,cooldown=12,range=30,pierce=2,power=1.2,root=2,mark=15,markCap=25,markTime=6,width=0.8,sprintRange=24,sprintRoot=2.5,rainPower=0.6,rainRadius=3,steadyRange=40,steadyMark=20,steadyStill=0.5,farRange=45,trapRoot=2,trapLife=8 | 379 |
| ab.RapidFire.numbers | mana=6,stamina=2,cooldown=20,arrows=15,time=3,power=0.5,range=30,width=0.6,sprintArrows=12,spread=8,hoverTime=2.5,hoverFall=1,bracedTime=2,bracedBonus=10,bounce=6,focusEvery=0.4,focusBonus=25 | 380 |
| ab.ExplosiveArrow.numbers | mana=5,stamina=2,cooldown=14,window=15,mult=2,radius=4,quickMult=1.5,quickRadius=3,mortarRadius=5,mortarUp=4,setDelay=1,setMult=2.5,burnTime=3,burnPower=0.2 | 381 |
| ab.ArrowRain.numbers | mana=7,stamina=2,cooldown=20,range=25,radius=6,time=3,power=2,slow=30,rootAfter=2,root=1.5,mark=15,markTime=6,behind=4,overRadius=7,delay=0.5,volleyRadius=8,volleyTime=4,volleySlow=40,volleyWind=1 | 382 |
| ab.HuntersNet.numbers | mana=6,stamina=2,cooldown=18,range=20,radius=4,time=3,power=0.5,mark=10,markTime=8,stripLength=6,stripWidth=2,dropRadius=5,dropTime=3.5,trapArm=1,trapLife=20,trapRadius=3,pull=4 | 383 |
| ab.ArcaneBreach.numbers | mana=8,stamina=1,cooldown=5,range=6.5,speed=15,width=8,knock=2,power=1.4,breach=15,time=8,perStack=1,stackCap=10,perLevel=0.5,cap=30,step=2,sprintTime=7,airRadius=4,airPower=1,airUp=1.5,markRadius=3.5,markBreach=20,gain=3,chainRange=6,durMax=2 | 385 |
| ab.ElementalImbue.numbers | mana=7,stamina=1,cooldown=18,time=12,pct=30,crescent=8,crescentPower=0.8,crescentWidth=1.5,burstRadius=4,burstPower=0.8,deepTime=15,deepStatus=25,deepStill=0.5,chainRange=6,twinCut=2 | 386 |
| ab.Sunder.numbers | mana=9,stamina=2,cooldown=30,range=4,power=2,time=12,weaken=15,expose=20,gain=2,step=3,lungePower=1.8,airRadius=3,airPower=2.4,airStagger=0.5,wind=1,breakTime=15,breakDef=10,chainRange=6,chainPct=75,durMax=2,splitDef=10,splitCd=4 | 387 |
| ab.RiftCleave.numbers | mana=10,stamina=2,cooldown=20,range=5,angle=80,power=1.2,length=8,width=2,time=3,breach=15,slow=20,runLength=10,dropRadius=5,ringRadius=4,ringTime=4,ringBreach=18,gain=3,patch=1.5,patchTime=2 | 388 |
| ab.ShatteringArc.numbers | mana=9,stamina=2,cooldown=20,range=6,angle=100,power=1.2,perStack=0.1,breach=15,breachPerStack=1,breachCap=30,time=8,timePerStack=0.25,keep=5,step=3,airRadius=5,airPower=1,airUp=3,halfAngle=80 | 389 |
| ab.Momentum.numbers | max=20,decay=4,perHit=1,maxPerSwing=2,rhythm=1,flow=0.4,swing=0.15,rolling=7,unstoppable=14,pushRolling=5,pushUnstoppable=10,pushRange=8,heavyHit=15,heavyDrop=3,elemPerStack=1,statusUnstop=50,windKeep=5,windEvery=60,tempestEvery=5,tempestRadius=4,tempestPower=1,tempestDecay=3.5,vanguardCut=15,vanguardMax=18,pushRange3=12,keen=5 | 390 |
| ab.Elements.numbers | burnPct=10,burnTime=4,burnStacks=3,chillSlow=15,chillTime=3,freezeAt=3,freezeWindow=3,freezeTime=1.5,staggerEvery=3,staggerTime=0.4,staggerDef=10,staggerDefTime=4,shockPct=40,shockRange=3,shockVuln=5,shockTime=3,gustUp=3,gustKb=1,poisonPct=8,poisonTime=6,bossCc=50,breachMark=5,bothBonus=10 | 391 |
| abil.pushPerBlock | 2 | 392 |
| abil.critStand | 50 | 393 |
| abil.speedCap | 60 | 394 |
| rb.classCap0 | 100 | 395 |
| rb.modSlotEvery | 5 | 396 |
| rb.modSlotMax | 2 | 397 |

# Part 2 - defaults written in the build scripts (not in the live configs)

Extracted by a free OpenRouter model (nemotron) from the pinned build script named in each heading, then spot-checked (values yes; the line column is the model's estimate and OFTEN WRONG - treat it as a hint and grep the key in the named script). Rows overlapping Part 1 are the same defaults seen in code.

## SkyyClasses 0.1.39

| system | key | value | line (approx) |
|---|---|---|---|
| SkyyClasses | DEF_SWITCH_COST | 5000 | 292 |
| SkyyClasses | DEF_COOLDOWN_MIN | 60 | 293 |
| SkyyClasses | DEF_REQUIRE_CLASS | False | 294 |
| SkyyClasses | DEF_UNASSIGNED_BLOCKED | True | 295 |
| SkyyClasses | DEF_PROMPT_EVERY_LOGIN | True | 296 |
| SkyyClasses | DEF_KITS_ON | True | 303 |
| SkyyClasses | KIT_MAX_STACKS | 9 | 304 |
| SkyyClasses | ALLOW_SWITCH | False | 317 |
| SkyyClasses | CFG_KEEP | 10 | 318 |
| SkyyClasses | DEF_HEAL_ON | True | 320 |
| SkyyClasses | DEF_HEAL_SHARE_PCT | 25 | 321 |
| SkyyClasses | DEF_HEAL_SELF_PCT | 100 | 322 |
| SkyyClasses | DEF_HEAL_RADIUS | 16.0 | 323 |
| SkyyClasses | DEF_HEAL_MAX_HIT | 10.0 | 324 |
| SkyyClasses | DEF_HEAL_MAX_SEC | 10.0 | 325 |
| SkyyClasses | DEF_HEAL_MSG | True | 326 |
| SkyyClasses | HEAL_SHARE_MAX | 500 | 328 |
| SkyyClasses | HEAL_SELF_MAX | 100 | 328 |
| SkyyClasses | HEAL_RADIUS_MIN | 1.0 | 329 |
| SkyyClasses | HEAL_RADIUS_MAX | 64.0 | 329 |
| SkyyClasses | HEAL_CAP_MIN | 0.5 | 330 |
| SkyyClasses | HEAL_CAP_MAX | 1000.0 | 330 |
| SkyyClasses | HEAL_MSG_MS_MIN | 1000 | 331 |
| SkyyClasses | HEAL_MSG_MS_MAX | 60000 | 331 |
| SkyyClasses | DEF_HEAL_PER_MANA | 2.0 | 334 |
| SkyyClasses | DEF_HEAL_QUICK_PCT | 20 | 335 |
| SkyyClasses | HEAL_PER_MANA_MIN | 0.0 | 336 |
| SkyyClasses | HEAL_PER_MANA_MAX | 50.0 | 336 |
| SkyyClasses | HEAL_QUICK_MAX | 100 | 337 |
| SkyyClasses | DEF_HEAL_OTHERS_PCT | 50 | 341 |
| SkyyClasses | HEAL_OTHERS_MAX | 100 | 342 |
| SkyyClasses | DEF_SWITCH_COST | 5000 | 357 |
| SkyyClasses | DEF_COOLDOWN_MIN | 60 | 360 |
| SkyyClasses | DEF_REQUIRE_CLASS | False | 363 |
| SkyyClasses | DEF_UNASSIGNED_BLOCKED | True | 366 |
| SkyyClasses | DEF_PROMPT_EVERY_LOGIN | True | 369 |
| SkyyClasses | DEF_KITS_ON | True | 388 |
| SkyyClasses | DEF_HEAL_ON | True | 414 |
| SkyyClasses | DEF_HEAL_SHARE_PCT | 25 | 420 |
| SkyyClasses | DEF_HEAL_SELF_PCT | 100 | 423 |
| SkyyClasses | DEF_HEAL_RADIUS | 16.0 | 426 |
| SkyyClasses | DEF_HEAL_MAX_HIT | 10.0 | 435 |
| SkyyClasses | DEF_HEAL_MAX_SEC | 10.0 | 440 |
| SkyyClasses | DEF_HEAL_PER_MANA | 2.0 | 444 |
| SkyyClasses | DEF_HEAL_QUICK_PCT | 20 | 448 |
| SkyyClasses | DEF_HEAL_OTHERS_PCT | 50 | 453 |
| SkyyClasses | DEF_HEAL_MSG | True | 457 |
| SkyyClasses | PART | true | 504 |
| SkyyClasses | CREATIVE_FREE | true | 505 |
| SkyyClasses | CAST_CHAT | true | 506 |
| SkyyClasses | REFUSE | 1.0 | 507 |
| SkyyClasses | CD_MSG | true | 511 |
| SkyyClasses | HEAL_CAP | 60 | 513 |
| SkyyClasses | UNLOCK_A1 | 1 | 515 |
| SkyyClasses | UNLOCK_A2 | 10 | 517 |
| SkyyClasses | UNLOCK_A2X | 20 | 519 |
| SkyyClasses | UNLOCK_A1X | 30 | 521 |
| SkyyClasses | H_FALLBACK | 25.0 | 523 |
| SkyyClasses | MAX_LIVE | 48 | 526 |
| SkyyClasses | SAFE_WORDS | Merchant,Trader,Shopkeeper,Vendor,NPC,Pet,Mount,Tamed,Hub | 529 |
| SkyyClasses | M_MANA | 23.0 | 531 |
| SkyyClasses | M_STAM | 2.0 | 533 |
| SkyyClasses | M_CD | 14.0 | 535 |
| SkyyClasses | M_POWER | 3.0 | 537 |
| SkyyClasses | M_RADIUS | 4.0 | 539 |
| SkyyClasses | M_DELAY | 1.0 | 541 |
| SkyyClasses | M_RANGE | 25.0 | 543 |
| SkyyClasses | S_MANA | 18.0 | 545 |
| SkyyClasses | S_STAM | 2.0 | 547 |
| SkyyClasses | S_CD | 14.0 | 549 |
| SkyyClasses | S_HEAL | 25 | 551 |
| SkyyClasses | S_SELF | 20 | 553 |
| SkyyClasses | S_RADIUS | 9.0 | 555 |
| SkyyClasses | S_HOT | 40 | 557 |
| SkyyClasses | S_HOT_TIME | 4.0 | 559 |
| SkyyClasses | TICK | 0.25 | 562 |
| SkyyClasses | MAX_ZONES | 2 | 564 |
| SkyyClasses | B_MANA | 16.0 | 566 |
| SkyyClasses | B_STAM | 1.0 | 568 |
| SkyyClasses | B_CD | 30.0 | 570 |
| SkyyClasses | B_TIME | 12.0 | 572 |
| SkyyClasses | B_RADIUS | 4.0 | 574 |
| SkyyClasses | B_RANGE | 8.0 | 576 |
| SkyyClasses | B_RATIO | 2.0 | 578 |
| SkyyClasses | B_KEEP | 4.0 | 580 |
| SkyyClasses | B_MAX | 100 | 582 |
| SkyyClasses | U_MANA | 20.0 | 584 |
| SkyyClasses | U_STAM | 2.0 | 586 |
| SkyyClasses | U_CD | 24.0 | 588 |
| SkyyClasses | U_TIME | 12.0 | 590 |
| SkyyClasses | U_RADIUS | 6.0 | 592 |
| SkyyClasses | U_RANGE | 8.0 | 594 |
| SkyyClasses | U_HP | 100 | 596 |
| SkyyClasses | U_PULSE | 8 | 598 |
| SkyyClasses | SHAPES | true | 610 |
| SkyyClasses | SHAPES_SPRINT | true | 611 |
| SkyyClasses | SHAPES_AIR | true | 612 |
| SkyyClasses | CROUCH_MIN | 0.1 | 613 |
| SkyyClasses | LOS_ON | true | 614 |
| SkyyClasses | AIR_MIN | 0.15 | 615 |
| SkyyClasses | LAND_WAIT | 2.0 | 616 |
| SkyyClasses | AHEAD | 6.0 | 617 |
| SkyyClasses | CHAN_MOVE | 1.0 | 618 |
| SkyyClasses | M_COMET_R | 3.0 | 619 |
| SkyyClasses | M_ONME_R | 5.0 | 620 |
| SkyyClasses | M_ONME_P | 2.5 | 621 |
| SkyyClasses | M_RIFT_ON | true | 622 |
| SkyyClasses | M_RIFT_P | 90.0 | 623 |
| SkyyClasses | M_RIFT_TGT | true | 624 |
| SkyyClasses | M_RIFT_D | 0.5 | 625 |
| SkyyClasses | M_ONME_D | 0.5 | 626 |
| SkyyClasses | B_POCKET_R | 4.0 | 627 |
| SkyyClasses | B_POCKET_T | 10.0 | 628 |
| SkyyClasses | B_POCKET_RATIO | 2.5 | 629 |
| SkyyClasses | U_AROUND_R | 5.0 | 630 |
| SkyyClasses | U_AROUND_HP | 110 | 631 |
| SkyyClasses | S_BLESS_R | 6.0 | 632 |
| SkyyClasses | S_BLESS_T | 2.0 | 633 |
| SkyyClasses | S_BEACON_R | 10.0 | 635 |
| SkyyClasses | S_KNEEL | 20 | 636 |
| SkyyClasses | S_KNEEL_HOT | 200 | 637 |
| SkyyClasses | S_KNEEL_T | 1.0 | 638 |
| SkyyClasses | F_RADIUS | 5.0 | 641 |
| SkyyClasses | F_POWER | 1.0 | 642 |
| SkyyClasses | F_FREEZE | 2.0 | 643 |
| SkyyClasses | F_BREAK | 1.0 | 644 |
| SkyyClasses | F_BREAK_P | 0.5 | 645 |
| SkyyClasses | F_CHILL | 3.0 | 646 |
| SkyyClasses | F_WAKE_L | 8.0 | 647 |
| SkyyClasses | F_WAKE_T | 3.0 | 649 |
| SkyyClasses | F_WAKE_F | 1.5 | 650 |
| SkyyClasses | F_DROP_R | 6.0 | 651 |
| SkyyClasses | F_DEEP_R | 4.0 | 652 |
| SkyyClasses | F_DEEP_F | 3.0 | 653 |
| SkyyClasses | FREEZE_STUN | true | 654 |
| SkyyClasses | F_DEEP_B | 2.0 | 655 |
| SkyyClasses | BOSS_WORDS | Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti | 657 |
| SkyyClasses | T_STARS | 12 | 660 |
| SkyyClasses | T_TIME | 3.0 | 661 |
| SkyyClasses | T_RADIUS | 6.0 | 662 |
| SkyyClasses | T_POWER | 0.3 | 663 |
| SkyyClasses | T_STAR_R | 3.0 | 664 |
| SkyyClasses | T_RANGE | 25.0 | 665 |
| SkyyClasses | T_BELOW_R | 7.0 | 666 |
| SkyyClasses | T_BELOW_T | 2.0 | 667 |
| SkyyClasses | T_SHOWER_N | 16 | 668 |
| SkyyClasses | T_SHOWER_T | 4.0 | 669 |
| SkyyClasses | R_RANGE | 20.0 | 672 |
| SkyyClasses | R_TIME | 3.0 | 673 |
| SkyyClasses | R_RATE | 0.5 | 674 |
| SkyyClasses | R_RAMP | 3.0 | 675 |
| SkyyClasses | R_WIDTH | 1.0 | 676 |
| SkyyClasses | R_SWEEP_R | 15.0 | 677 |
| SkyyClasses | R_SWEEP_T | 2.0 | 678 |
| SkyyClasses | R_SWEEP_M | 1.5 | 679 |
| SkyyClasses | R_DOWN_R | 12.0 | 681 |
| SkyyClasses | R_DOWN_T | 2.0 | 682 |
| SkyyClasses | R_FOCUS_R | 25.0 | 683 |
| SkyyClasses | R_FOCUS_T | 4.0 | 684 |
| SkyyClasses | R_FOCUS_RAMP | 3.5 | 685 |
| SkyyClasses | GS_MANA | 15.0 | 688 |
| SkyyClasses | GS_STAM | 1.0 | 689 |
| SkyyClasses | GS_HP | 30 | 690 |
| SkyyClasses | GS_CD | 12.0 | 691 |
| SkyyClasses | GS_RESET | 30.0 | 692 |
| SkyyClasses | GS_RADIUS | 30.0 | 693 |
| SkyyClasses | GS_ALL | false | 694 |
| SkyyClasses | Y_RADIUS | 8.0 | 697 |
| SkyyClasses | Y_TIME | 12.0 | 698 |
| SkyyClasses | Y_HEAL | 5 | 699 |
| SkyyClasses | Y_CUT | 10 | 700 |
| SkyyClasses | Y_AHEAD | 5.0 | 701 |
| SkyyClasses | Y_IN_R | 5.0 | 702 |
| SkyyClasses | Y_IN_C | 15 | 704 |
| SkyyClasses | Y_IN_T | 10.0 | 705 |
| SkyyClasses | G_RANGE | 30.0 | 708 |
| SkyyClasses | G_FIRST | 75 | 709 |
| SkyyClasses | G_DROP | 15 | 710 |
| SkyyClasses | G_TARGETS | 5 | 711 |
| SkyyClasses | G_CAP | 90 | 712 |
| SkyyClasses | G_VOW_F | 90 | 713 |
| SkyyClasses | G_VOW_D | 20 | 714 |
| SkyyClasses | G_VOW_T | 1.0 | 715 |
| SkyyClasses | RUNE_KEYS | true | 718 |
| SkyyClasses | CAST_CMD | true | 719 |
| SkyyClasses | VAN_RUNES | false | 720 |
| SkyyClasses | RUNE_HUD | true | 721 |
| SkyyClasses | RUNE_FILL | false | 722 |
| SkyyClasses | RUNE_FB | true | 723 |
| SkyyClasses | ROLL_CAST | true | 724 |
| SkyyClasses | TREE_GATE | true | 725 |
| SkyyClasses | LEVELS | true | 728 |
| SkyyClasses | MAX_LVL | 25 | 729 |
| SkyyClasses | USES_COEF | 4.5 | 730 |
| SkyyClasses | USES_EXP | 1.5 | 731 |
| SkyyClasses | USE_EVERY | 3.0 | 732 |
| SkyyClasses | PER_LEVEL | 2.0 | 733 |
| SkyyClasses | SOFT_LVL | 10 | 734 |
| SkyyClasses | HALF_LVL | 20 | 735 |
| SkyyClasses | MODS_ON | true | 737 |
| SkyyClasses | MOD_UNLOCK | 2,4,6,8,10 | 738 |
| SkyyClasses | MOD_STEPS | 10,30,60,100 | 739 |
| SkyyClasses | MOD_POWER | 5.0 | 740 |
| SkyyClasses | MOD_RADIUS | 0.5 | 741 |
| SkyyClasses | MOD_DUR | 10.0 | 742 |
| SkyyClasses | MOD_EFF | 5.0 | 743 |
| SkyyClasses | ECHO_BASE | 20.0 | 744 |
| SkyyClasses | ECHO_STEP | 2.5 | 745 |
| SkyyClasses | ECHO_DELAY | 1.0 | 746 |
| SkyyClasses | PUSH_PER_BLOCK | 2.0 | 774 |
| SkyyClasses | CRIT_STAND | 50 | 775 |
| SkyyClasses | SPEED_CAP | 60 | 776 |
| SkyyClasses | RB_CAP0 | 100 | 779 |
| SkyyClasses | RB_SLOT_EVERY | 5 | 782 |
| SkyyClasses | RB_SLOT_MAX | 2 | 783 |
| SkyyClasses | FF_DM | 0.65 | 787 |
| SkyyClasses | FF_DS | 0.25 | 788 |
| SkyyClasses | FF_TIME | 30.0 | 789 |
| SkyyClasses | FF_RADIUS | 5.0 | 790 |
| SkyyClasses | FF_MAX | 20 | 791 |
| SkyyClasses | FF_DECAY | 5.0 | 792 |
| SkyyClasses | FF_MOVE | 2.0 | 793 |
| SkyyClasses | FF_ATK | 1.5 | 794 |
| SkyyClasses | FF_ADEF | 1.0 | 795 |
| SkyyClasses | FF_ALINGER | 10.0 | 796 |
| SkyyClasses | FF_DISTRACT | 1.0 | 797 |
| SkyyClasses | FF_SP_ST | 2 | 798 |
| SkyyClasses | FF_SP_FREE | 3.0 | 799 |
| SkyyClasses | FF_CR_ST | 3 | 800 |
| SkyyClasses | FF_CR_R | 4.0 | 801 |
| SkyyClasses | FF_CR_D | 25 | 802 |
| SkyyClasses | FF_COUNT | 5 | 803 |
| SkyyClasses | HF_DM | 0.7 | 805 |
| SkyyClasses | HF_DS | 0.3 | 806 |
| SkyyClasses | HF_EVERY | 10 | 807 |
| SkyyClasses | HF_POWER | 1.0 | 808 |
| SkyyClasses | HF_GAP | 8.0 | 809 |
| SkyyClasses | HF_SP_EVERY | 8 | 810 |
| SkyyClasses | HF_CR_EVERY | 12 | 811 |
| SkyyClasses | HF_CR_POWER | 1.3 | 812 |
| SkyyClasses | SW_TIME | 10.0 | 814 |
| SkyyClasses | SW_POWER | 1.0 | 815 |
| SkyyClasses | SW_FRONT | 90.0 | 816 |
| SkyyClasses | SW_GAP | 0.4 | 817 |
| SkyyClasses | SW_SP_TIME | 6.0 | 818 |
| SkyyClasses | SW_AIR_R | 2.0 | 819 |
| SkyyClasses | SW_AIR_P | 0.5 | 820 |
| SkyyClasses | SW_CR_TIME | 12.0 | 821 |
| SkyyClasses | SW_CR_P | 1.3 | 822 |
| SkyyClasses | SW_ECHO_T | 3.0 | 823 |
| SkyyClasses | PS_POWER | 1.2 | 825 |
| SkyyClasses | PS_STUN | 0.75 | 826 |
| SkyyClasses | PS_PUSH | 4.0 | 827 |
| SkyyClasses | PS_REACH | 4.0 | 828 |
| SkyyClasses | PS_CD_FLOOR | 5.0 | 829 |
| SkyyClasses | PS_CD_LVL | 0.1 | 830 |
| SkyyClasses | PS_SP_STEP | 2.0 | 831 |
| SkyyClasses | PS_SP_PUSH | 6.0 | 832 |
| SkyyClasses | PS_SP_STUN | 0.5 | 833 |
| SkyyClasses | PS_AI_STUN | 1.0 | 834 |
| SkyyClasses | PS_CR_STUN | 1.25 | 835 |
| SkyyClasses | CK_RADIUS | 3.0 | 837 |
| SkyyClasses | CK_POWER | 0.8 | 838 |
| SkyyClasses | CK_PUSH | 5.0 | 839 |
| SkyyClasses | CK_SP_R | 4.0 | 840 |
| SkyyClasses | CK_SP_PUSH | 6.0 | 841 |
| SkyyClasses | CK_AI_R | 4.0 | 842 |
| SkyyClasses | CK_CR_STUN | 1.0 | 843 |
| SkyyClasses | CK_HASTE | 20 | 844 |
| SkyyClasses | CL_TIME | 8.0 | 847 |
| SkyyClasses | CL_WINDOW | 10.0 | 848 |
| SkyyClasses | CL_STRIKE | 50 | 849 |
| SkyyClasses | CL_LOSE | 24.0 | 850 |
| SkyyClasses | CL_SP_TIME | 6.0 | 851 |
| SkyyClasses | CL_SP_SPEED | 20 | 852 |
| SkyyClasses | CL_CR_TIME | 11.0 | 853 |
| SkyyClasses | CL_CR_BONUS | 20 | 854 |
| SkyyClasses | CL_HASTE | 20 | 855 |
| SkyyClasses | TX_RANGE | 20.0 | 857 |
| SkyyClasses | TX_RADIUS | 4.0 | 858 |
| SkyyClasses | TX_TIME | 5.0 | 859 |
| SkyyClasses | TX_POISON | 0.25 | 860 |
| SkyyClasses | TX_WEAKEN | 15 | 861 |
| SkyyClasses | TX_SP_RANGE | 28.0 | 862 |
| SkyyClasses | TX_SP_R | 3.5 | 863 |
| SkyyClasses | TX_CR_R | 5.0 | 864 |
| SkyyClasses | TX_CR_T | 6.0 | 865 |
| SkyyClasses | TX_CHAIN_R | 6.0 | 866 |
| SkyyClasses | GK_WINDOW | 12.0 | 868 |
| SkyyClasses | GK_MULT | 2.0 | 869 |
| SkyyClasses | GK_BACK | 3.0 | 870 |
| SkyyClasses | GK_ANGLE | 80.0 | 871 |
| SkyyClasses | GK_ELITE | Elite,Captain,Champion,Alpha,Brute | 873 |
| SkyyClasses | GK_SP_WIN | 8.0 | 875 |
| SkyyClasses | GK_SP_SPEED | 15 | 876 |
| SkyyClasses | GK_CR_WIN | 20.0 | 877 |
| SkyyClasses | GK_HASTE | 25 | 878 |
| SkyyClasses | VA_CLOAK | 3.0 | 880 |
| SkyyClasses | VA_RADIUS | 4.0 | 881 |
| SkyyClasses | VA_TIME | 3.0 | 882 |
| SkyyClasses | VA_LOSE | 2.0 | 883 |
| SkyyClasses | VA_SLOW | 25 | 884 |
| SkyyClasses | VA_AI_R | 5.0 | 885 |
| SkyyClasses | VA_CR_CLOAK | 5.0 | 886 |
| SkyyClasses | RG_MANA | 5.0 | 889 |
| SkyyClasses | RG_STAM | 2.0 | 890 |
| SkyyClasses | RG_CD | 24.0 | 891 |
| SkyyClasses | RG_TIME | 10.0 | 892 |
| SkyyClasses | RG_CUT | 20.0 | 893 |
| SkyyClasses | RG_CUTCAP | 40.0 | 894 |
| SkyyClasses | RG_PARTY | 10.0 | 895 |
| SkyyClasses | RG_PLAYERS | 6.0 | 896 |
| SkyyClasses | RG_TAUNT | 8.0 | 897 |
| SkyyClasses | RG_TAUNTTIME | 6.0 | 898 |
| SkyyClasses | RG_CHARGETIME | 1.5 | 899 |
| SkyyClasses | RG_CHARGERADIUS | 4.0 | 900 |
| SkyyClasses | RG_CHARGETAUNT | 6.0 | 901 |
| SkyyClasses | RG_LANDTAUNT | 10.0 | 902 |
| SkyyClasses | RG_HOLDTAUNT | 16.0 | 903 |
| SkyyClasses | RG_HOLDTIME | 6.0 | 904 |
| SkyyClasses | RG_HOLDCUT | 10.0 | 905 |
| SkyyClasses | RG_ECHOTIME | 3.0 | 906 |
| SkyyClasses | SS_MANA | 4.0 | 908 |
| SkyyClasses | SS_STAM | 2.0 | 909 |
| SkyyClasses | SS_CD | 12.0 | 910 |
| SkyyClasses | SS_RANGE | 6.0 | 911 |
| SkyyClasses | SS_ANGLE | 45.0 | 912 |
| SkyyClasses | SS_POWER | 1.0 | 913 |
| SkyyClasses | SS_STUN | 1.5 | 914 |
| SkyyClasses | SS_STUNLEVEL | 0.03 | 915 |
| SkyyClasses | SS_STEP | 2.0 | 916 |
| SkyyClasses | SS_SPRINTRANGE | 7.0 | 917 |
| SkyyClasses | SS_SPRINTPOWER | 1.2 | 918 |
| SkyyClasses | SS_SPRINTSTUN | 1.2 | 919 |
| SkyyClasses | SS_POUNDRADIUS | 4.0 | 920 |
| SkyyClasses | SS_POUNDSTUN | 1.5 | 921 |
| SkyyClasses | SS_POUNDUP | 4.0 | 922 |
| SkyyClasses | SS_RINGRADIUS | 3.0 | 923 |
| SkyyClasses | SS_RINGPOWER | 0.8 | 924 |
| SkyyClasses | SS_ECHOSTUN | 0.5 | 925 |
| SkyyClasses | SS_RETRIPCT | 20.0 | 926 |
| SkyyClasses | SS_RETRIGAP | 20.0 | 927 |
| SkyyClasses | IC_MANA | 5.0 | 929 |
| SkyyClasses | IC_STAM | 2.0 | 930 |
| SkyyClasses | IC_CD | 14.0 | 931 |
| SkyyClasses | IC_RANGE | 15.0 | 932 |
| SkyyClasses | IC_POWER | 0.6 | 933 |
| SkyyClasses | IC_STUN | 1.0 | 934 |
| SkyyClasses | IC_MEETSTUN | 0.8 | 935 |
| SkyyClasses | IC_HOOKPOWER | 0.8 | 936 |
| SkyyClasses | IC_HOOKUP | 6.0 | 937 |
| SkyyClasses | IC_ANCHORRANGE | 20.0 | 938 |
| SkyyClasses | IC_ANCHORSTUN | 1.5 | 939 |
| SkyyClasses | IC_ANCHORROOT | 1.0 | 940 |
| SkyyClasses | IC_ANCHORPULL | 60.0 | 941 |
| SkyyClasses | IC_CHAINRANGE | 4.0 | 942 |
| SkyyClasses | IC_BARBED | 25.0 | 943 |
| SkyyClasses | IC_BARBEDTIME | 5.0 | 944 |
| SkyyClasses | CH_MANA | 5.0 | 946 |
| SkyyClasses | CH_STAM | 2.0 | 947 |
| SkyyClasses | CH_CD | 20.0 | 948 |
| SkyyClasses | CH_RANGE | 12.0 | 949 |
| SkyyClasses | CH_TIME | 8.0 | 950 |
| SkyyClasses | CH_CUT | 30.0 | 951 |
| SkyyClasses | CH_REFLECT | 20.0 | 952 |
| SkyyClasses | CH_STEP | 2.0 | 953 |
| SkyyClasses | CH_SPRINTTIME | 6.0 | 954 |
| SkyyClasses | CH_LANDRADIUS | 8.0 | 955 |
| SkyyClasses | CH_DUELTIME | 10.0 | 956 |
| SkyyClasses | CH_DUELCUT | 40.0 | 957 |
| SkyyClasses | CH_DUELREFLECT | 30.0 | 958 |
| SkyyClasses | CH_CHAINRANGE | 4.0 | 959 |
| SkyyClasses | GO_MANA | 5.0 | 961 |
| SkyyClasses | GO_STAM | 2.0 | 962 |
| SkyyClasses | GO_CD | 22.0 | 963 |
| SkyyClasses | GO_RANGE | 15.0 | 964 |
| SkyyClasses | GO_TIME | 8.0 | 965 |
| SkyyClasses | GO_SHARE | 40.0 | 966 |
| SkyyClasses | GO_CUT | 15.0 | 967 |
| SkyyClasses | GO_RUSHRANGE | 8.0 | 968 |
| SkyyClasses | GO_RUSHSPEED | 20.0 | 969 |
| SkyyClasses | GO_BURDENTIME | 10.0 | 970 |
| SkyyClasses | GO_BURDENSHARE | 50.0 | 971 |
| SkyyClasses | GO_BURDENCUT | 25.0 | 972 |
| SkyyClasses | GO_LEASH | 30.0 | 973 |
| SkyyClasses | EN_MANA | 3.0 | 975 |
| SkyyClasses | EN_STAM | 3.0 | 976 |
| SkyyClasses | EN_CD | 30.0 | 977 |
| SkyyClasses | EN_GROW | 10.0 | 978 |
| SkyyClasses | EN_HOLD | 5.0 | 979 |
| SkyyClasses | EN_START | 10.0 | 980 |
| SkyyClasses | EN_PEAK | 20.0 | 981 |
| SkyyClasses | EN_SELFMULT | 2.0 | 982 |
| SkyyClasses | EN_SELFCAP | 60.0 | 983 |
| SkyyClasses | EN_PLAYERS | 8.0 | 984 |
| SkyyClasses | EN_PARTY | 16.0 | 985 |
| SkyyClasses | EN_CHARGETIME | 2.0 | 986 |
| SkyyClasses | EN_CHARGERADIUS | 4.0 | 987 |
| SkyyClasses | EN_LEAPADD | 2.0 | 988 |
| SkyyClasses | EN_LONEBONUS | 10.0 | 989 |
| SkyyClasses | EN_LONEHOLD | 8.0 | 990 |
| SkyyClasses | EN_HORNDELAY | 3.0 | 991 |
| SkyyClasses | EN_HORNSTART | 15.0 | 992 |
| SkyyClasses | EN_RALLYSHIELD | 10.0 | 993 |
| SkyyClasses | EN_FADE | 3.0 | 994 |
| SkyyClasses | WW_MANA | 3.0 | 996 |
| SkyyClasses | WW_STAM | 2.0 | 997 |
| SkyyClasses | WW_CD | 14.0 | 998 |
| SkyyClasses | WW_TIME | 3.0 | 999 |
| SkyyClasses | WW_RADIUS | 3.0 | 1000 |
| SkyyClasses | WW_EVERY | 0.5 | 1001 |
| SkyyClasses | WW_POWER | 0.5 | 1002 |
| SkyyClasses | WW_HEAL | 10.0 | 1003 |
| SkyyClasses | WW_SPRINTTIME | 2.5 | 1004 |
| SkyyClasses | WW_SPRINTRADIUS | 2.5 | 1005 |
| SkyyClasses | WW_DROPPOWER | 1.0 | 1006 |
| SkyyClasses | WW_GRINDEVERY | 0.4 | 1007 |
| SkyyClasses | WW_GRINDRADIUS | 3.5 | 1008 |
| SkyyClasses | WW_BLEED | 0.2 | 1009 |
| SkyyClasses | WW_BLEEDTIME | 4.0 | 1010 |
| SkyyClasses | ES_MANA | 3.0 | 1012 |
| SkyyClasses | ES_STAM | 3.0 | 1013 |
| SkyyClasses | ES_CD | 12.0 | 1014 |
| SkyyClasses | ES_LENGTH | 12.0 | 1015 |
| SkyyClasses | ES_WIDTH | 2.0 | 1016 |
| SkyyClasses | ES_POWER | 2.0 | 1017 |
| SkyyClasses | ES_UP | 3.0 | 1018 |
| SkyyClasses | ES_MISSINGCAP | 50.0 | 1019 |
| SkyyClasses | ES_SPRINTLENGTH | 16.0 | 1020 |
| SkyyClasses | ES_SPRINTWIDTH | 1.4 | 1021 |
| SkyyClasses | ES_SPRINTPOWER | 1.8 | 1022 |
| SkyyClasses | ES_CRATERRADIUS | 5.0 | 1023 |
| SkyyClasses | ES_WIND | 1.0 | 1024 |
| SkyyClasses | ES_FISSURELENGTH | 8.0 | 1025 |
| SkyyClasses | ES_FISSUREPOWER | 2.4 | 1026 |
| SkyyClasses | ES_FISSURESLOW | 2.0 | 1027 |
| SkyyClasses | ES_SPLITANGLE | 20.0 | 1028 |
| SkyyClasses | ES_POUNDRADIUS | 2.5 | 1029 |
| SkyyClasses | ES_POUNDPOWER | 1.5 | 1030 |
| SkyyClasses | ES_PACTCOST | 10.0 | 1031 |
| SkyyClasses | ES_PACTBONUS | 30.0 | 1032 |
| SkyyClasses | BF_MANA | 1.0 | 1034 |
| SkyyClasses | BF_STAM | 1.0 | 1035 |
| SkyyClasses | BF_CD | 10.0 | 1036 |
| SkyyClasses | BF_HITMANA | 0.7 | 1037 |
| SkyyClasses | BF_HITSTAM | 0.6 | 1038 |
| SkyyClasses | BF_DRAINMANA | 0.15 | 1039 |
| SkyyClasses | BF_DRAINSTAM | 0.1 | 1040 |
| SkyyClasses | BF_MAX | 25.0 | 1041 |
| SkyyClasses | BF_DECAY | 6.0 | 1042 |
| SkyyClasses | BF_DMG | 1.5 | 1043 |
| SkyyClasses | BF_MOVE | 0.5 | 1044 |
| SkyyClasses | BF_ALLY | 50.0 | 1045 |
| SkyyClasses | BF_PLAYERS | 8.0 | 1046 |
| SkyyClasses | BF_PARTY | 16.0 | 1047 |
| SkyyClasses | BF_CHARGESTACKS | 3.0 | 1048 |
| SkyyClasses | BF_LANDSTACKS | 2.0 | 1049 |
| SkyyClasses | BF_BANKWINDOW | 20.0 | 1050 |
| SkyyClasses | BF_BANKSHARE | 50.0 | 1051 |
| SkyyClasses | BF_BANKPLAYERS | 6.0 | 1052 |
| SkyyClasses | BF_BANKPARTY | 12.0 | 1053 |
| SkyyClasses | BF_HASTEAT | 10.0 | 1054 |
| SkyyClasses | BF_HASTESPEED | 10.0 | 1055 |
| SkyyClasses | BF_COUNTAT | 10.0 | 1056 |
| SkyyClasses | WB_MANA | 9.0 | 1058 |
| SkyyClasses | WB_STAM | 8.0 | 1059 |
| SkyyClasses | WB_CD | 40.0 | 1060 |
| SkyyClasses | WB_TIME | 30.0 | 1061 |
| SkyyClasses | WB_RADIUS | 12.0 | 1062 |
| SkyyClasses | WB_PLAYERS | 8.0 | 1063 |
| SkyyClasses | WB_PARTY | 12.0 | 1064 |
| SkyyClasses | WB_SELF | 16.0 | 1065 |
| SkyyClasses | WB_KILLADD | 1.0 | 1066 |
| SkyyClasses | WB_MINIADD | 3.0 | 1067 |
| SkyyClasses | WB_BOSSADD | 5.0 | 1068 |
| SkyyClasses | WB_CAP | 60.0 | 1069 |
| SkyyClasses | WB_AHEAD | 6.0 | 1070 |
| SkyyClasses | WB_LANDADD | 2.0 | 1071 |
| SkyyClasses | WB_ROOTEDRADIUS | 10.0 | 1072 |
| SkyyClasses | WB_ROOTEDTIME | 40.0 | 1073 |
| SkyyClasses | WB_ECHOTIME | 4.0 | 1074 |
| SkyyClasses | WB_BEARERHEAL | 1.0 | 1075 |
| SkyyClasses | WB_BEARERTIME | 25.0 | 1076 |
| SkyyClasses | PN_MANA | 4.0 | 1078 |
| SkyyClasses | PN_STAM | 1.0 | 1079 |
| SkyyClasses | PN_CD | 12.0 | 1080 |
| SkyyClasses | PN_RANGE | 30.0 | 1081 |
| SkyyClasses | PN_PIERCE | 2.0 | 1082 |
| SkyyClasses | PN_POWER | 1.2 | 1083 |
| SkyyClasses | PN_ROOT | 2.0 | 1084 |
| SkyyClasses | PN_MARK | 15.0 | 1085 |
| SkyyClasses | PN_MARKCAP | 25.0 | 1086 |
| SkyyClasses | PN_MARKTIME | 6.0 | 1087 |
| SkyyClasses | PN_WIDTH | 0.8 | 1088 |
| SkyyClasses | PN_SPRINTRANGE | 24.0 | 1089 |
| SkyyClasses | PN_SPRINTROOT | 2.5 | 1090 |
| SkyyClasses | PN_RAINPOWER | 0.6 | 1091 |
| SkyyClasses | PN_RAINRADIUS | 3.0 | 1092 |
| SkyyClasses | PN_STEADYRANGE | 40.0 | 1093 |
| SkyyClasses | PN_STEADYMARK | 20.0 | 1094 |
| SkyyClasses | PN_STEADYSTILL | 0.5 | 1095 |
| SkyyClasses | PN_FARRANGE | 45.0 | 1096 |
| SkyyClasses | PN_TRAPROOT | 2.0 | 1097 |
| SkyyClasses | PN_TRAPLIFE | 8.0 | 1098 |
| SkyyClasses | RF_MANA | 6.0 | 1100 |
| SkyyClasses | RF_STAM | 2.0 | 1101 |
| SkyyClasses | RF_CD | 20.0 | 1102 |
| SkyyClasses | RF_TIME | 3.0 | 1104 |
| SkyyClasses | RF_POWER | 0.5 | 1105 |
| SkyyClasses | RF_RANGE | 30.0 | 1106 |
| SkyyClasses | RF_WIDTH | 0.6 | 1107 |
| SkyyClasses | RF_SPREAD | 8.0 | 1109 |
| SkyyClasses | RF_HOVERTIME | 2.5 | 1110 |
| SkyyClasses | RF_HOVERFALL | 1.0 | 1111 |
| SkyyClasses | RF_BRACEDTIME | 2.0 | 1112 |
| SkyyClasses | RF_BRACEDBONUS | 10.0 | 1113 |
| SkyyClasses | RF_BOUNCE | 6.0 | 1114 |
| SkyyClasses | RF_FOCUSEVERY | 0.4 | 1115 |
| SkyyClasses | RF_FOCUSBONUS | 25.0 | 1116 |
| SkyyClasses | EA_MANA | 5.0 | 1118 |
| SkyyClasses | EA_STAM | 2.0 | 1119 |
| SkyyClasses | EA_CD | 14.0 | 1120 |
| SkyyClasses | EA_WINDOW | 15.0 | 1121 |
| SkyyClasses | EA_MULT | 2.0 | 1122 |
| SkyyClasses | EA_RADIUS | 4.0 | 1123 |
| SkyyClasses | EA_QUICKMULT | 1.5 | 1124 |
| SkyyClasses | EA_QUICKRADIUS | 3.0 | 1125 |
| SkyyClasses | EA_MORTARRADIUS | 5.0 | 1126 |
| SkyyClasses | EA_MORTARUP | 4.0 | 1127 |
| SkyyClasses | EA_SETDELAY | 1.0 | 1128 |
| SkyyClasses | EA_SETMULT | 2.5 | 1129 |
| SkyyClasses | EA_BURNTIME | 3.0 | 1130 |
| SkyyClasses | EA_BURNPOWER | 0.2 | 1131 |
| SkyyClasses | AR_MANA | 7.0 | 1133 |
| SkyyClasses | AR_STAM | 2.0 | 1134 |
| SkyyClasses | AR_CD | 20.0 | 1135 |
| SkyyClasses | AR_RANGE | 25.0 | 1136 |
| SkyyClasses | AR_RADIUS | 6.0 | 1137 |
| SkyyClasses | AR_TIME | 3.0 | 1138 |
| SkyyClasses | AR_POWER | 2.0 | 1139 |
| SkyyClasses | AR_SLOW | 30.0 | 1140 |
| SkyyClasses | AR_ROOTAFTER | 2.0 | 1141 |
| SkyyClasses | AR_ROOT | 1.5 | 1142 |
| SkyyClasses | AR_MARK | 15.0 | 1143 |
| SkyyClasses | AR_MARKTIME | 6.0 | 1144 |
| SkyyClasses | AR_BEHIND | 4.0 | 1145 |
| SkyyClasses | AR_OVERRADIUS | 7.0 | 1146 |
| SkyyClasses | AR_DELAY | 0.5 | 1147 |
| SkyyClasses | AR_VOLLEYRADIUS | 8.0 | 1148 |
| SkyyClasses | AR_VOLLEYTIME | 4.0 | 1149 |
| SkyyClasses | AR_VOLLEYSLOW | 40.0 | 1150 |
| SkyyClasses | AR_VOLLEYWIND | 1.0 | 1151 |
| SkyyClasses | HN_MANA | 6.0 | 1153 |
| SkyyClasses | HN_STAM | 2.0 | 1154 |
| SkyyClasses | HN_CD | 18.0 | 1155 |
| SkyyClasses | HN_RANGE | 20.0 | 1156 |
| SkyyClasses | HN_RADIUS | 4.0 | 1157 |
| SkyyClasses | HN_TIME | 3.0 | 1158 |
| SkyyClasses | HN_POWER | 0.5 | 1159 |
| SkyyClasses | HN_MARK | 10.0 | 1160 |
| SkyyClasses | HN_MARKTIME | 8.0 | 1161 |
| SkyyClasses | HN_STRIPLENGTH | 6.0 | 1162 |
| SkyyClasses | HN_STRIPWIDTH | 2.0 | 1163 |
| SkyyClasses | HN_DROPRADIUS | 5.0 | 1164 |
| SkyyClasses | HN_DROPTIME | 3.5 | 1165 |
| SkyyClasses | HN_TRAPARM | 1.0 | 1166 |
| SkyyClasses | HN_TRAPLIFE | 20.0 | 1167 |
| SkyyClasses | HN_TRAPRADIUS | 3.0 | 1168 |
| SkyyClasses | HN_PULL | 4.0 | 1169 |
| SkyyClasses | AB_MANA | 8.0 | 1172 |
| SkyyClasses | AB_STAM | 1.0 | 1173 |
| SkyyClasses | AB_CD | 5.0 | 1174 |
| SkyyClasses | AB_RANGE | 6.5 | 1175 |
| SkyyClasses | AB_SPEED | 15.0 | 1176 |
| SkyyClasses | AB_WIDTH | 8.0 | 1177 |
| SkyyClasses | AB_KNOCK | 2.0 | 1178 |
| SkyyClasses | AB_POWER | 1.4 | 1179 |
| SkyyClasses | AB_BREACH | 15.0 | 1180 |
| SkyyClasses | AB_TIME | 8.0 | 1181 |
| SkyyClasses | AB_PERSTACK | 1.0 | 1182 |
| SkyyClasses | AB_STACKCAP | 10.0 | 1183 |
| SkyyClasses | AB_PERLEVEL | 0.5 | 1184 |
| SkyyClasses | AB_CAP | 30.0 | 1185 |
| SkyyClasses | AB_STEP | 2.0 | 1186 |
| SkyyClasses | AB_SPRINTTIME | 7.0 | 1187 |
| SkyyClasses | AB_AIRRADIUS | 4.0 | 1188 |
| SkyyClasses | AB_AIRPOWER | 1.0 | 1189 |
| SkyyClasses | AB_AIRUP | 1.5 | 1190 |
| SkyyClasses | AB_MARKRADIUS | 3.5 | 1191 |
| SkyyClasses | AB_MARKBREACH | 20.0 | 1192 |
| SkyyClasses | AB_GAIN | 3.0 | 1193 |
| SkyyClasses | AB_CHAINRANGE | 6.0 | 1194 |
| SkyyClasses | AB_DURMAX | 2.0 | 1195 |
| SkyyClasses | EI_MANA | 7.0 | 1197 |
| SkyyClasses | EI_STAM | 1.0 | 1198 |
| SkyyClasses | EI_CD | 18.0 | 1199 |
| SkyyClasses | EI_TIME | 12.0 | 1200 |
| SkyyClasses | EI_PCT | 30.0 | 1201 |
| SkyyClasses | EI_CRESCENT | 8.0 | 1202 |
| SkyyClasses | EI_CRESCENTPOWER | 0.8 | 1203 |
| SkyyClasses | EI_CRESCENTWIDTH | 1.5 | 1204 |
| SkyyClasses | EI_BURSTRADIUS | 4.0 | 1205 |
| SkyyClasses | EI_BURSTPOWER | 0.8 | 1206 |
| SkyyClasses | EI_DEEPTIME | 15.0 | 1207 |
| SkyyClasses | EI_DEEPSTATUS | 25.0 | 1208 |
| SkyyClasses | EI_DEEPSTILL | 0.5 | 1209 |
| SkyyClasses | EI_CHAINRANGE | 6.0 | 1210 |
| SkyyClasses | EI_TWINCUT | 2.0 | 1211 |
| SkyyClasses | SU_MANA | 9.0 | 1213 |
| SkyyClasses | SU_STAM | 2.0 | 1214 |
| SkyyClasses | SU_CD | 30.0 | 1215 |
| SkyyClasses | SU_RANGE | 4.0 | 1216 |
| SkyyClasses | SU_POWER | 2.0 | 1217 |
| SkyyClasses | SU_TIME | 12.0 | 1218 |
| SkyyClasses | SU_WEAKEN | 15.0 | 1219 |
| SkyyClasses | SU_EXPOSE | 20.0 | 1220 |
| SkyyClasses | SU_GAIN | 2.0 | 1221 |
| SkyyClasses | SU_STEP | 3.0 | 1222 |
| SkyyClasses | SU_LUNGEPOWER | 1.8 | 1223 |
| SkyyClasses | SU_AIRRADIUS | 3.0 | 1224 |
| SkyyClasses | SU_AIRPOWER | 2.4 | 1225 |
| SkyyClasses | SU_AIRSTAGGER | 0.5 | 1226 |
| SkyyClasses | SU_WIND | 1.0 | 1227 |
| SkyyClasses | SU_BREAKTIME | 15.0 | 1228 |
| SkyyClasses | SU_BREAKDEF | 10.0 | 1229 |
| SkyyClasses | SU_CHAINRANGE | 6.0 | 1230 |
| SkyyClasses | SU_CHAINPCT | 75.0 | 1231 |
| SkyyClasses | SU_DURMAX | 2.0 | 1232 |
| SkyyClasses | SU_SPLITDEF | 10.0 | 1233 |
| SkyyClasses | SU_SPLITCD | 4.0 | 1234 |
| SkyyClasses | RC_MANA | 10.0 | 1236 |
| SkyyClasses | RC_STAM | 2.0 | 1237 |
| SkyyClasses | RC_CD | 20.0 | 1238 |
| SkyyClasses | RC_RANGE | 5.0 | 1239 |
| SkyyClasses | RC_ANGLE | 80.0 | 1240 |
| SkyyClasses | RC_POWER | 1.2 | 1241 |
| SkyyClasses | RC_LENGTH | 8.0 | 1242 |
| SkyyClasses | RC_WIDTH | 2.0 | 1243 |
| SkyyClasses | RC_TIME | 3.0 | 1244 |
| SkyyClasses | RC_BREACH | 15.0 | 1245 |
| SkyyClasses | RC_SLOW | 20.0 | 1246 |
| SkyyClasses | RC_RUNLENGTH | 10.0 | 1247 |
| SkyyClasses | RC_DROPRADIUS | 5.0 | 1248 |
| SkyyClasses | RC_RINGRADIUS | 4.0 | 1249 |
| SkyyClasses | RC_RINGTIME | 4.0 | 1250 |
| SkyyClasses | RC_RINGBREACH | 18.0 | 1251 |
| SkyyClasses | RC_GAIN | 3.0 | 1252 |
| SkyyClasses | RC_PATCH | 1.5 | 1253 |
| SkyyClasses | RC_PATCHTIME | 2.0 | 1254 |
| SkyyClasses | SA_MANA | 9.0 | 1256 |
| SkyyClasses | SA_STAM | 2.0 | 1257 |
| SkyyClasses | SA_CD | 20.0 | 1258 |
| SkyyClasses | SA_RANGE | 6.0 | 1259 |
| SkyyClasses | SA_ANGLE | 100.0 | 1260 |
| SkyyClasses | SA_POWER | 1.2 | 1261 |
| SkyyClasses | SA_PERSTACK | 0.1 | 1262 |
| SkyyClasses | SA_BREACH | 15.0 | 1263 |
| SkyyClasses | SA_BREACHPERSTACK | 1.0 | 1264 |
| SkyyClasses | SA_BREACHCAP | 30.0 | 1265 |
| SkyyClasses | SA_TIME | 8.0 | 1266 |
| SkyyClasses | SA_TIMEPERSTACK | 0.25 | 1267 |
| SkyyClasses | SA_KEEP | 5.0 | 1268 |
| SkyyClasses | SA_STEP | 3.0 | 1269 |
| SkyyClasses | SA_AIRRADIUS | 5.0 | 1270 |
| SkyyClasses | SA_AIRPOWER | 1.0 | 1271 |
| SkyyClasses | SA_AIRUP | 3.0 | 1272 |
| SkyyClasses | SA_HALFANGLE | 80.0 | 1273 |
| SkyyClasses | MO_MAX | 20.0 | 1275 |
| SkyyClasses | MO_DECAY | 4.0 | 1276 |
| SkyyClasses | MO_PERHIT | 1.0 | 1277 |
| SkyyClasses | MO_MAXPERSWING | 2.0 | 1278 |
| SkyyClasses | MO_RHYTHM | 1.0 | 1279 |
| SkyyClasses | MO_FLOW | 0.4 | 1280 |
| SkyyClasses | MO_SWING | 0.15 | 1281 |
| SkyyClasses | MO_ROLLING | 7.0 | 1282 |
| SkyyClasses | MO_UNSTOPPABLE | 14.0 | 1283 |
| SkyyClasses | MO_PUSHROLLING | 5.0 | 1284 |
| SkyyClasses | MO_PUSHUNSTOPPABLE | 10.0 | 1285 |
| SkyyClasses | MO_PUSHRANGE | 8.0 | 1286 |
| SkyyClasses | MO_HEAVYHIT | 15.0 | 1287 |
| SkyyClasses | MO_HEAVYDROP | 3.0 | 1288 |
| SkyyClasses | MO_ELEMPERSTACK | 1.0 | 1289 |
| SkyyClasses | MO_STATUSUNSTOP | 50.0 | 1290 |
| SkyyClasses | MO_WINDKEEP | 5.0 | 1291 |
| SkyyClasses | MO_WINDEVERY | 60.0 | 1292 |
| SkyyClasses | MO_TEMPESTEVERY | 5.0 | 1293 |
| SkyyClasses | MO_TEMPESTRADIUS | 4.0 | 1294 |
| SkyyClasses | MO_TEMPESTPOWER | 1.0 | 1295 |
| SkyyClasses | MO_TEMPESTDECAY | 3.5 | 1296 |
| SkyyClasses | MO_VANGUARDCUT | 15.0 | 1297 |
| SkyyClasses | MO_VANGUARDMAX | 18.0 | 1298 |
| SkyyClasses | MO_PUSHRANGE3 | 12.0 | 1299 |
| SkyyClasses | MO_KEEN | 5.0 | 1300 |
| SkyyClasses | EL_BURNPCT | 10.0 | 1302 |
| SkyyClasses | EL_BURNTIME | 4.0 | 1303 |
| SkyyClasses | EL_BURNSTACKS | 3.0 | 1304 |
| SkyyClasses | EL_CHILLSLOW | 15.0 | 1305 |
| SkyyClasses | EL_CHILLTIME | 3.0 | 1306 |
| SkyyClasses | EL_FREEZEAT | 3.0 | 1307 |
| SkyyClasses | EL_FREEZEWINDOW | 3.0 | 1308 |
| SkyyClasses | EL_FREEZETIME | 1.5 | 1309 |
| SkyyClasses | EL_STAGGEREVERY | 3.0 | 1310 |
| SkyyClasses | EL_STAGGERTIME | 0.4 | 1311 |
| SkyyClasses | EL_STAGGERDEF | 10.0 | 1312 |
| SkyyClasses | EL_STAGGERDEFTIME | 4.0 | 1313 |
| SkyyClasses | EL_SHOCKPCT | 40.0 | 1314 |
| SkyyClasses | EL_SHOCKRANGE | 3.0 | 1315 |
| SkyyClasses | EL_SHOCKVULN | 5.0 | 1316 |
| SkyyClasses | EL_SHOCKTIME | 3.0 | 1317 |
| SkyyClasses | EL_GUSTUP | 3.0 | 1318 |
| SkyyClasses | EL_GUSTKB | 1.0 | 1319 |
| SkyyClasses | EL_POISONPCT | 8.0 | 1320 |
| SkyyClasses | EL_POISONTIME | 6.0 | 1321 |
| SkyyClasses | EL_BOSSCC | 50.0 | 1322 |
| SkyyClasses | EL_BOTHBONUS | 10.0 | 1324 |

## SkyyMobs 0.1.12

| system | key | value | line (approx) |
|---|---|---|---|
| strength | PRESETS.easy.health_pct | 4.0 | 106 |
| strength | PRESETS.easy.damage_pct | 2.0 | 106 |
| strength | PRESETS.normal.health_pct | 6.0 | 106 |
| strength | PRESETS.normal.damage_pct | 3.0 | 106 |
| strength | PRESETS.hard.health_pct | 8.0 | 106 |
| strength | PRESETS.hard.damage_pct | 4.0 | 106 |
| strength | CUSTOM.health_pct | 4.0 | 107 |
| strength | CUSTOM.damage_pct | 2.0 | 107 |
| strength | CAPS.health_cap | 6.0 | 107 |
| strength | CAPS.damage_cap | 3.5 | 107 |
| strength | LEVEL_TOP | 60 | 108 |
| strength | FLOOR_DEF | 50 | 175 |
| strength | FLOOR_MAX | 1000 | 175 |
| strength | HITCAP_DEF | 35 | 262 |
| strength | HITCAP_OLD | 0 | 263 |
| curve | CURVE_SPEC.hp.hard | 1=1.0, 20=2.52, 25=3.62, 30=5.6, 35=8.53, 40=13.18, 45=19.41, 49=24.52, 55=26.95, 60=28.98 | 201 |
| curve | CURVE_SPEC.hp.normal | 1=1.0, 20=2.14, 25=3.03, 30=4.62, 35=6.97, 40=10.69, 45=15.63, 49=19.66, 55=21.48, 60=23.0 | 202 |
| curve | CURVE_SPEC.hp.easy | 1=1.0, 20=1.76, 25=2.43, 30=3.65, 35=5.41, 40=8.19, 45=11.85, 49=14.79, 55=16.01, 60=17.02 | 203 |
| curve | CURVE_SPEC.dmg.hard | 1=1.0, 20=1.76, 25=2.32, 30=3.03, 35=3.89, 40=4.95, 45=6.41, 49=7.72, 55=8.31, 60=8.78 | 204 |
| curve | CURVE_SPEC.dmg.normal | 1=1.0, 20=1.57, 25=2.04, 30=2.62, 35=3.33, 40=4.2, 45=5.39, 49=6.45, 55=6.89, 60=7.24 | 205 |
| curve | CURVE_SPEC.dmg.easy | 1=1.0, 20=1.38, 25=1.75, 30=2.22, 35=2.77, 40=3.44, 45=4.36, 49=5.19, 55=5.47, 60=5.7 | 206 |
| curve | CURVES.hp.hard (stretched) | 1=1.0, 20=2.52, 30=3.62, 40=5.6, 47=8.53, 53=13.18, 60=19.41, 65=24.52, 73=26.95, 80=28.98, 100=35.07 | 238 |
| curve | CURVES.dmg.hard (stretched) | 1=1.0, 20=1.76, 30=2.32, 40=3.03, 47=3.89, 53=4.95, 60=6.41, 65=7.72, 73=8.31, 80=8.78, 100=10.19 | 238 |
| curve | HARD_STEP | 0.08 | 249 |
| gap | GAP_DEF.free | 5 | 250 |
| gap | GAP_DEF.dealtStep | 2.5 | 250 |
| gap | GAP_DEF.dealtMin | 40.0 | 250 |
| gap | GAP_DEF.takenStep | 1.5 | 250 |
| gap | GAP_DEF.takenMax | 1.5 | 250 |
| bands | ZONE_TOPS (0.1.12) | 20, 40, 60, 80, 100 | 283 |
| bands | ZONE_TOPS_V2 (0.1.11) | 20, 30, 45, 60, 75 | 283 |
| bands | ZONE_FLOORS | 1, 20, 40, 60 | 562 |
| bands | ZONE_TOPS | 20, 40, 60, 80 | 562 |
| bands | PASS_DEF | River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_* | 584 |
| bands | bands.islands | 0 | 584 |
| bands | bands.default | 0 | 584 |
| boss | BOSS_ROLES_DEF | Goblin_Duke*, Trork_Chieftain, Dragon_*, *_Boss* | 597 |
| boss | BOSS_ROLES_010 | Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss* | 594 |
| boss | BOSS_TOPS_DEF | 20 40 60 80 100 | 599 |
| boss | BOSS_TOPS_011 | 20 30 45 60 75 | 598 |
| boss | NOT_BOSSES | Skeleton_Elite* | 596 |
| mob | LEVELLED count | 280 | 638 |
| mob | MAX_LEVEL | 100 | 108, 415 |
| mob | DIFF_DEF | normal | 108 |
| mob | SHAPE_DEF | curve | 248 |
| mob | CURVE_ON default | true | 415 |
| mob | GAP_ON default | true | 415 |
| mob | HEAL_ON_LOAD default | false | 415 |
| mob | VOLCANIC default | true | 415 |
| mob | MARKUP default | tag | 415 |
| mob | PLATE_MODE default | all | 415 |
| mob | FORMAT_DEF | [Lv {level}] {name} | 415 |
| mob | STRIP_DEF | _Wander,_Patrol,_Surge,_Static,_Sleep | 415 |

