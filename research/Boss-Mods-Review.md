# Boss + mob mods review (2026-10-09)

Skyy: "these could help with the bosses later." / "this one looks really cool too"

## Adathan - AdathansBossLibrary 1.0.8, Void Asylum 1.1.4, Steamwrought Tomb 1.2.2
- LICENCE: all three "All Rights Reserved", no modpack terms -> ask Adathan (Discord on the page, X @AdathanHytale) before listing in PACK.md;
  never copy their JSON / numbers. Library bundles HStats telemetry (disable on our servers).
- Installed but DISABLED in the HUD mod world (never loaded); Steamwrought zip never registered. No 0.7 upper bound (untested on 0.7).
- Library = JSON interactions usable from our boss JSON: ExecuteInteraction (+AtPlayer / AtSelf / AroundPointRandomly), SetBlocksSquare,
  SetBlocksAroundCircle, RotateSelf (+Randomly), FireProjectilesSetIntervals (+WithRemoval), TeleportSelfRelative / Static /
  RandomlyAroundPoint, condition OwnStatPercentageAdathan (HP-% phases). Their bosses = vanilla CombatActionEvaluator JSON + these.
- Void Asylum: 6-boss rush (Forbidden Practitioner, Voidbreaker, Gilded Tyrant + Umbral Ravager duo, Void Dragon, Warden, Void Architect),
  weapons Voidbreaker's Lament, Gravity Staff, Abyssal Helix Spear, Repulsion Bow, Void Architect Staff (L100), Warden spear; portal key
  via Ancient Gateway. Steamwrought: Scalding Sentinel (5000 HP), Piston Lance.
- PLAN: build our zone bosses with vanilla CAE first; trial the library on one boss needing teleports / arena blocks after permission +
  0.7 test. The two dungeons = optional endgame side-dungeons (Zones 3-4) after permission; their DropLists bypass our UT / Mythic rules
  (overriding them = editing their data -> ask).

## DanBagh - Ancient Constructs 1.2.3
- LICENCE: "All Rights Reserved unless otherwise explicitly stated" -> ask DanBagh before listing. HStats bundled. Disabled in the HUD mod
  world (never loaded). ServerVersion ^0.6.0-pre.13.1 (0.7 untested).
- Ancient Titan Construct boss (900 HP, 7 attacks, Zone 4 jungle underground) + Minion (300 HP); Gardener Construct worker (waters,
  harvests into a chest around a Charging Station; 50 Copper Bars + Construct Core); Warrior Construct WIP.
- FIT: Titan = good mid-tier boss (SkyyMobs level + our loot on top). Gardener is not a pet; decide whether its harvests give farming XP.
- PLAN: Skyy tries it on a test world; then ask DanBagh for modpack permission.
