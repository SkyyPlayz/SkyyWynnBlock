# SkyWynn - ROADMAP (big picture, 2026-10-08)

Where the pack is going, in big steps.
This file changes rarely.

> **The to-do list is NOT here.**
> It lives in [RESUME.md](RESUME.md) ("Now" + "Next, in order").
> The builder keeps RESUME current every round (Skyy's rule).

## The goal

| When | Goal |
|---|---|
| **Now** | A pack that is 100% usable for solo and private multiplayer worlds. |
| **Also now** | Ready for server use: server features get their backbone (admin set-up, multiplayer-safe). Content comes later. |
| **Later** | Every mod in the pack is our own. Third-party mods get replaced one by one. |
| **Public** | Some mods also ship alone on CurseForge. Skyy's Pocket Dimension (the Magic Bags) goes first. |

Sources: `docs/handoff/design-locks.md` ("Pack goal", "Own content"),
`docs/answered/project.md` ("PUBLIC MODS on CurseForge").

## Phases

The phase names come from `docs/plans/SkyWynn-Master-Plan.md` part 2E.
Each phase is a playable step.

> **Status = estimate, Skyy to confirm.**
> Worked out from RESUME, HANDOFF and the log on 2026-10-08.
> Exact versions: [HANDOFF.md](HANDOFF.md) section 1.

| Phase | What it covers | Status (estimate) |
|---|---|---|
| P0 Foundation | private islands, coins, item stats that survive saves | Done (NPC shops are still a spec) |
| P1 Core loop | skills, collections, Magic Bags, profiles, party, guilds, accessories | Live - Skyy testing + tuning |
| P2 Island life | private island, co-op, island size upgrades, minions | Part done: islands + co-op live; upgrades + minions not built yet |
| P3 Economy | coins, bank, Bazaar, auction house | Live as 4 mods; SkyyEconomy merge waits for Skyy's tests |
| P4 Combat depth | 7 classes, class weapons, class trees, abilities, slayers | In progress: 7 classes playable, trees live; abilities wait for Hytale 0.7; slayers not started |
| P5 Gear game | levels, rarity, identify, reforge, armor types, gathering gear | In progress: SkyyGear live; gathering ladder + armor types next |
| P6 Island chain | zone islands, Zone 1 town (the hub), mob levels, quests | Started: test island + mob levels live; Zone 1 town being planned |
| P7 Capstone + side content | endgame dungeon, raids, events, guild territory | Not started (specs only) |

### What "next" looks like (summary only - RESUME has the real order)

| Track | Next big step | Where it is planned |
|---|---|---|
| Gathering | Gathering ladder phase A, then tool levels + locks | `research/Gathering-Progression-Spec.md` |
| Armor | Heavy / Light / Cloth armor types with the new models | `docs/answered/gear.md` (2026-10-05 lines) |
| Classes | Monk moves, then the class abilities after Hytale 0.7 | `docs/answered/classes.md` |
| World | Zone 1 town + WorldGen stage 2 | `research/Zone-1-Town-Build-Plan.md` |
| Fishing | Our own fishing mod (SkyyFishing) | `research/cloud/SkyyFishing-Spec-Draft.md` |
| Release | Pocket Dimension release kit (last) | `research/cloud/PocketDimension-Release-Kit.md` |

## Later (wanted, not scheduled)

- Class abilities on Hytale's runes - wait for the Hytale 0.7 release (`research/cloud/Hytale-0.7-Watch.md`).
- Slayers (`research/cloud/Slayers-Spec.md`).
- Quests (`research/cloud/SkyyQuests-Spec.md`).
- Pets and dragons (`research/cloud/Pets-Spec.md`).
- Minions on the private island (`docs/plans/SkyyMinions-Plan.md`).
- Dungeons + the endgame capstone (`docs/plans/SkyyDungeons-Plan.md`).
- Wynn elements and powders on gear.
- NPC shops (`research/cloud/NPC-Shops-Spec.md`).
- Shaman class (maybe; Monk took its slot).
- Replace the third-party mods in `PACK.md` with our own.

## Not doing (for now)

| Not doing | Why / since |
|---|---|
| The Garden farming island | parked 2026-09-24; farming stays on the islands |
| Custom UI on the vanilla inventory screen | Hytale will change that screen |
| A shared Combat skill | each class levels its own weapon skill (2026-09-23) |
| Void protection on traversal moves | "part of the fun" (Skyy, 2026-10-07) |
| A pre-release test pack for Hytale 0.7 | wait for the real 0.7 release (2026-10-02) |
| Advanced Farming in the pack | out of date; its ideas go into our own tools (2026-10-06) |

Sources for these lines: [DECISIONS.md](DECISIONS.md).

---

*Update this file only when a phase changes or Skyy makes a big direction call.*
*Day-to-day work goes in RESUME.md and the log, never here.*
