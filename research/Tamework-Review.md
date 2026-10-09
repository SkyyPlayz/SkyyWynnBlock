# Alec's Tamework! (alechilles) - review for SkyWynn pets, 2026-10-09

Skyy: "check into this one too, ive never used it, but its design might help us make our pets faster and easier."

- LICENCE: GPL v3 + attribution ("Alec's Tamework!" by Alechilles). Mods may depend on it (documented Public API 3.0; optional
  integration via Patchwork When.ModInstalled). Compiling against its Java API / copying code may make our mod GPL - JSON-only or runtime
  bridge keeps us clear. Bundles Beacon + HStats telemetry (opt-out /beacon consent). Docs: wiki.hytalemodding.dev/mod/alecs-tamework,
  source github.com/Alechilles/AlecsTamework.
- Jar 5.2.0 (already installed in Mods; 15.5 MB): ServerVersion covers 0.7. Taming, ownership, naming, Follow/Defend/Hold/Graze/Aggressive,
  companion panel + radial menu, bonded roster (MaximumOwned / MaximumActive, timed summon, auto-store on logout, revive cost + cooldown,
  cross-world recall), leveling / talents / needs / breeding, mounts, flight; data per player + world under universe/Tamework.
- FIT: it is a "tame a world animal" framework; ours are slot-based buff pets (slot 1 never fights, slot 2 summon) with rarity, eggs,
  Upgrade Stones and PER-PROFILE storage. No model-scale option (chibi / shrink stays ours), no profile concept, own UI (breaks our
  vanilla-look rule), own NPC XP / levels (clashes with SkyyMobs levels + SkyyClasses summons), extra items, hard dependency for every server.
- DECISION PROPOSAL: borrow the design, do not depend on it (now). Borrow for slot 2: MaximumActive vs Owned, summon duration +
  resummon cooldown, auto-store on logout, revive cost / cooldown, Follow / Defend / Hold states; build on the vanilla Hytale:NPC
  follow-owner role pieces it uses. Later (after launch): optional bridge so Tamework-tamed animals (Cats, Animal Husbandry) can bond to
  our pet slot.
