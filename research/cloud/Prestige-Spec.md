# Prestige - "go home anyway" (spec)

Cloud draft, 2026-10-06. Paper design; nothing built. Builds on `research/cloud/Tab-Economy.md` section 5 and the lore (`research/Isles-of-the-Void-Lore.md`, Skyy 2026-10-01: optional prestige, perks stay, a hiccup pulls you back, **"Welcome back! Your ticket number is #4,000,000,002."**, Skyy's favourite line, kept word for word). Contracts read from the repo docs: `tools/PROFILES-CONTRACT.md` (per-profile data), cross-mod calls only through `skyy.bridge` with plain `java.lang` types (PROJECT-RULES 4). Every number is a placeholder (Server Setup, section 9). No web research was needed. This is a **full round** build (saved data, resets, items, several mods: PROJECT-RULES 4).

## 0. The idea in one paragraph

After you have paid the Tab in full you may tell the clerk "go home anyway". A short scene plays, your **run progress** resets (levels, coins, zone and boss progress), your **identity** stays (titles, cosmetics, pets, Pocket Shards, learned recipes, every item), and a Void hiccup drops you back at the starter town with a new ticket number. Each prestige gives small permanent perks that save **time, not power**. It is optional, capped, and never loses an item.

Design rules (mine, for Skyy to change):

| Rule | Why |
|---|---|
| **No item is ever deleted or taken.** Gear stays in your bags; the level gate (a weapon above your level does nothing, SkyyGear rule) makes old gear sit idle until you level back up. | The "items could be lost" risk in PROJECT-RULES 4 goes away; no dupe or loss bugs |
| Perks are **time savers and cosmetics**, never combat stats | Prestige must not make PvP or bosses unfair; Accessory Power stays gear-driven |
| **Coins never carry over** (starter grant only) | R3 / economy: the Tab sink works because prestige does not undo it |
| Everything is **per profile** (SkyyProfiles) | A second profile on the same player starts at prestige 0 |
| Resets are **idempotent and journaled** | a crash in the middle can be finished on the next login |

## 1. Who can prestige, and when

| Prestige | Requirement |
|---|---|
| **1** | **Paid in Full** (the Receipt exists on the profile). The clerk offers "go home anyway" after the pay-off scene |
| **2 to 10** | **Re-Audit**: class level >= 75 (`prestige.reqLevel`) AND the Zone 5 guardian beaten **in this run** (the boss flags were reset). No Tab, because the Tab is rent-free forever after the first pay-off |
| Always | not in combat (`skill:fn:combat`), not in a party instance / capstone run / bounty arena, **no open Bazaar or AH orders** (the page lists them and asks to cancel first), mailbox empty or the page warns |
| Cooldown | `prestige.cooldownSeconds` 259,200 (3 real days) between two prestiges |
| Cap | `prestige.max` 10 |

## 2. What resets and what stays (per mod)

"Hook" = the bridge function each mod must offer (section 6). Defaults are my recommendation; **three questions at the end** let Skyy flip them.

| Area (mod) | Resets | Stays | Hook |
|---|---|---|---|
| Skills (SkyySkills) | every skill and the class skill to **level 1** (floor `prestige.skillFloor` 1; Skyy may want 10) and its XP | the Skill list, titles earned | `skill:fn:prestige` |
| Class (SkyyClasses) | class level (comes from class-skill XP), ability levels, modifier levels, tree points (= **free respec**) | **which class you picked**, which abilities you have unlocked, runes you own | `class:fn:prestige` |
| Collections (SkyyCollections) | **counts** go to 0 | **learned recipes and claimed tier flags** (so one-time rewards are never paid twice, and your crafting knowledge stays), the "ever reached" high mark for titles | `coll:fn:prestige` |
| Coins (SkyyCoins) | purse and bank -> the starter grant (10,000); Bazaar / AH balance must be 0 first | Receipt, Paid in Full flag, Tab milestones | `coins:fn:prestige` |
| Slayers | slayer XP, levels and bounty bars | titles, "first kill" flags (so story drops are not repeatable) | `slay:fn:prestige` |
| Zones and bosses (SkyyQuests, SkyyMobs) | **guardian-beaten flags** (you must beat each guardian again to cross islands), the zone-unlocked flags, active quests | story quests **done** stay done (the story is one-time; the return runs a small "Return Visit" quest line instead) | `quest:fn:prestige` |
| Exploration (SkyyExploration) | nothing | outposts found, stamps, warps (you still need the guardian flags to cross between islands: anti-skip) | none |
| Gear, bags, accessories, pets, items | **nothing is touched** | every item in inventory, bags, vault, Pocket Shard storage | none |
| Pocket Shards | nothing | shards, upgrades; **+slots** as a perk | none (reads `prest:n`) |
| Personal island, pets, cosmetics, titles | nothing | all | none |
| Tab | the Tab is **rent-free forever** (lore) | Paid in Full wall, statue | none |

**Why gear stays.** The earlier draft listed "gear resets". Deleting items is the most dangerous thing a prestige could do (and the most hated). The SkyyGear **level rule** already makes high-level gear useless until you level, so the run still starts from scratch and nothing is lost. If Skyy wants a harsher reset, the safe version is a "Lost Luggage" storage that returns the items a level at a time (a bigger build; Q1).

## 3. Perks (per prestige N, up to 10)

| Perk | Value | How it is applied |
|---|---|---|
| Skill XP | **+2% per prestige** (cap +20%) on every skill and the class skill | `skill:bonus:<uuid>` map, source `prestige`, key `xp.<skill>` (the wave-2 mechanism the Booster spec describes; SkyySkills clamps the sum) |
| Pocket Shard slots | **+1 at prestige 1, 3, 5, 7, 10** (5 total) | SkyyShards reads `prest:n:<pkey>` |
| Pet slot | +1 at prestige 5 and 10 | SkyyPets reads `prest:n:<pkey>` (Pets-Spec has a slot count) |
| **Express Pass** | +50% XP until class level 20 and **free** Zone 1 starter kit (a basic tool set, no gear above the starter tier) | applied for the first 20 levels of each new run |
| Title | "Returning Guest I" ... "Returning Guest X" (the Roman numeral = prestige count) | SkyyTitles |
| Ticket | the ticket number rises by one: prestige N shows **#4,000,000,001 + N** (so the first shows #4,000,000,002, as the line says) | displayed in chat, on the Stats page and the profile card |
| Cosmetic | ticket pin colour ladder; at 10, a tiny **suitcase** pet-follower; the Tab menu icon gains stars | cosmetic assets |

Check: leveling to 75 takes T hours; +20% XP shortens it by 1/1.2, about 17%. At 10 prestiges the total time saving stays modest, so no runaway. Express Pass only touches levels 1-20 (the quickest part).

**Not given:** combat stats, Accessory Power, coin income, drop rates, anything that skips collections (R3).

## 4. The scene (what the player sees)

| Step | What happens | Notes |
|---|---|---|
| 1 | At the clerk (Tab hall / waiting room): "Go home anyway?" opens a vanilla-look **Prestige page**: what resets, what stays, the perks you will get, the **requirements checklist** with ticks | no hover info (UI rule); click twice to confirm (like Bazaar Sell inventory) |
| 2 | 10-second **stamp** countdown with a Cancel button; the form text: "Please wait. Your departure is being processed." | cancel works until step 4 |
| 3 | Snapshot of the profile (the same History snapshot the migrations use), a **journal marker** is written `prestige.pending=<N>` | crash safety |
| 4 | The resets run (section 6); the player is held in the waiting room; a black fade and a short door scene | a few seconds, world thread |
| 5 | **A Void hiccup**: lights flicker, the player is pulled back | a title card: "Welcome back!" |
| 6 | Chat and title card: **"Welcome back! Your ticket number is #4,000,000,002."** (+1 per prestige) | exact text |
| 7 | Arrive in the Zone 1 starter town; the **Return Visit** quest starts (short, funny: re-file the arrival form) | story texts for the quest go in `research/cloud/Story-Script-*` later |

## 5. Exploit and edge-case check

| Risk | Handling |
|---|---|
| Prestige to farm coin faucets again (collections rewards, quest coins) | claimed tier flags stay, quest "done" flags stay; the starter grant is paid once per profile at creation (not again on prestige: **no coin on prestige**) |
| Dupe through a crash mid-reset | journal marker + idempotent hooks: each mod's reset is "set to the clean state", so running it twice is harmless; the marker is cleared only after all hooks report ok |
| Prestige with items in the Bazaar / AH / mailbox | blocked with a checklist (open orders must be cancelled first) |
| Prestige while in a party instance | blocked; the party is told nothing |
| Alt-profile farming of titles | each profile needs its own Paid in Full |
| An admin sets `prestige.max` lower after players reached it | existing counts are never reduced |
| Perk stacking above caps | caps in the perk table, clamped on read |
| XP perk used to skip the level-gated gear | the Express Pass ends at level 20 and perks are percentages, never levels |
| Disconnect during the scene | the hook journal finishes on the next join; the scene replays from step 5 |
| Wrong profile active | the page names the profile; prestige applies to that profile only |

## 6. Technical outline (for the local session)

- **Home:** the Tab mod (SkyyEconomy 0.1 per Tab-Economy 9.4) owns prestige: the clerk page, the requirement check, the journal and the orchestration. Storage in the profile data file: `prestige.n`, `prestige.pending`, `prestige.lastUnix`, `paidInFull`.
- **Bridge keys (plain java.lang types):** `prest:n:<pkey>` Integer, `prest:ticket:<pkey>` String (the ticket text), `prest:fn:status` Function(String pkey) -> String, and one reset function per mod: `skill:fn:prestige`, `class:fn:prestige`, `coll:fn:prestige`, `coins:fn:prestige`, `slay:fn:prestige`, `quest:fn:prestige`. Each is `Function<String pkey, String>` that returns `"ok"` or `"err:<reason>"`.
- **Order:** quests/zones -> slayers -> class -> skills -> collections -> coins (coins last so a failure before it never strands a poor player). If a hook is missing (that mod is not installed) it is skipped and the page shows "not installed".
- **Verification before commit:** each hook returns counts; the orchestrator re-reads them and only then writes `prest:n`. A failed step leaves the marker and shows "Come back to the desk" with the retry.
- **Respect of the profile contract:** every key uses `pkey(u)`; profile epoch republish after the reset (PROFILES-CONTRACT) so other mods drop cached values.
- **Perks:** `prestige.xpPerLevel` is published by the Tab mod into `skill:bonus:<uuid>` (source `prestige`); SkyyShards / SkyyPets read `prest:n`.
- **Existing profiles:** none have prestige, nothing to migrate; the page is hidden until Paid in Full exists, so no migration marker is needed. `prestige.enabled` default **off** until the Tab ships.

## 7. Build order

| # | Piece | Needs |
|---|---|---|
| 1 | The Tab (pay, milestones, Paid in Full) | economy measurement (Tab-Economy section 3) |
| 2 | The six `*:fn:prestige` hooks | each mod's small patch |
| 3 | Prestige page, requirement check, journal, scene | Tab mod |
| 4 | Perks (XP bonus, shard and pet slots, titles) | SkyySkills `skill:bonus` (exists), SkyyShards, SkyyPets, SkyyTitles |
| 5 | Return Visit quest | SkyyQuests |

## 8. Tests (to put in the harness / TEST-CHECKLIST)

1. Paid in Full profile, press go home anyway: page shows the checklist; Cancel leaves everything as it was.
2. Confirm: skills at level 1, coins 10,000, boss flags cleared, items all present (count before = after).
3. Recipes learned before the prestige still craft; collection counts are 0.
4. Crash test: kill the server between hooks; rejoin; the journal finishes the reset and the player gets the hiccup scene.
5. Second prestige blocked before level 75 and before the Zone 5 guardian; cooldown works.
6. Ticket text reads #4,000,000,002 then #4,000,000,003 ... and the Stats page matches.
7. +2% XP shows on the Skills page after prestige 1, +4% after prestige 2, capped at +20%.
8. Another profile of the same player is untouched.
9. Open Bazaar order blocks the prestige with a clear message.

## 9. Server Setup rows

`prestige.enabled` (off), `prestige.max` 10, `prestige.reqLevel` 75, `prestige.cooldownSeconds` 259200, `prestige.skillFloor` 1, `prestige.xpPercentPer` 2, `prestige.xpPercentMax` 20, `prestige.expressLevel` 20, `prestige.expressBonusPercent` 50, `prestige.shardSlotAt` "1,3,5,7,10", `prestige.petSlotAt` "5,10", `prestige.sceneSeconds` 10, `prestige.ticketBase` 4000000001.

## For the local session (UNVERIFIED)

- Whether SkyySkills' `skill:bonus` map already exists with source keys (the Booster spec calls it "wave 2"; SkyyTrees uses source `trees`).
- Whether each mod can reset a profile's data from a single call and whether the level gate for gear uses the **class level** or a different level.
- How SkyyProfiles snapshots and republishes (the migration rule mentions a "verified History snapshot").
- Whether a fade / door scene is possible with vanilla UI or only a title card plus a teleport.
- Where the starter grant is paid (profile creation) so prestige never pays it again.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Do items stay (gear, bags, accessories) and only the level gate resets you, or do you want the harder "Lost Luggage" reset where items return a level at a time? | **items stay** (safe, no loss) |
| 2 | Skill floor 1 or 10 after prestige? | 1 |
| 3 | Do collections count again from 0 (recipes kept), or do counts stay and only skills reset? | counts reset, recipes kept |
| 4 | Is 2% XP per prestige, cap 10 prestiges, a good size? | yes |
| 5 | Should prestige 2+ need the "Re-Audit" (level 75 + Zone 5 guardian) or just a cooldown? | Re-Audit + 3-day cooldown |
| 6 | Pocket Shard slots as a perk at 1, 3, 5, 7, 10: OK or cosmetics only? | OK |
