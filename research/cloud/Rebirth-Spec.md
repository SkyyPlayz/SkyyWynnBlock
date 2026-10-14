# Rebirth (New Game+) - build spec

Cloud draft, 2026-10-13. Paper design; nothing built, nothing compiled. It turns Skyy's rebirth decisions into a plan the local
session can build. Every number Skyy has not given is a **Question** (section 7), not a fact. The research behind it:
`research/cloud/Rebirth-Research.md` (clicker games, formulas) and `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md` (the page).
This spec only adds the rules, the data and the safety plan. Where an older draft says something different, Skyy's newest words win.

## 0. Decisions this follows (Skyy's words)

| # | Source line | What it fixes |
|---|---|---|
| D1 | `docs/answered/skills.md` line 114 | "some sort of rebirth system that gives a few permanent upgrades. but resets your level ... but your island stays the same" |
| D2 | `docs/answered/skills.md` line 115 | popups: RESETS = "Skill levels, Coins + bank"; "gear isnt lost or locked away, you just cant use it because of levels"; "you retain the knowledge from collections"; "more collection levels, and higher skill/class levels locked behind a rebirth"; REWARDS = "Stat boost per rebirth, Rebirth points shop, Cosmetics + title, New content"; WHEN / HOW MANY = "Decide in the spec" |
| D3 | `docs/answered/skills.md` line 117 | "1 rebirth menu with an upgrade tree"; "you can rebirth when you reach max class level. even if mining isnt max"; "your upgrade points are seprate per skill"; "it keeps tracking the xp gain even past max lvl"; "upgrades start cheap, and scale pretty quickly"; "you just need like 8 total levels in the first row to unlock the next row"; "the trees [...] radiate from the blackhole in the center (the nexus of the void.)" |
| D4 | `docs/answered/skills.md` line 118 | "the nexus of the void is the controller for the rebirth. so in /rebirth you hover over it to see what requirements you have to reach, and what you will get when you rebirth. you click it, then confirm to rebirth." |
| D5 | `docs/answered/skills.md` lines 119-120 | the fishing POLE is lifelong (rebirth rules like the other tools); "fishing gets its own skill, and skill tree" (own rebirth branch) |
| D6 | `docs/answered/skills.md` line 121 | "all T1 shards come from quests. (more can be crafter after rebirth 2." |
| D7 | `docs/answered/gear.md` line 168 | "should we allow each skill to rebirth individually? or all together?" -> popup "All together (Recommended)"; fallback "one tree per skill around the Nexus"; "when you rebirth, you pickaxe keeps its rarity, and stats, but reverts back to crude ... gets a rebirth modifier which can be upgraded in the mining rebirth tree"; "unlock the multi tool after the first rebirth" |
| D8 | `docs/answered/gear.md` lines 170, 172 | lifelong = pickaxe, axe, hoe, sickle, fishing pole; the shovel is NOT lifelong; Multitools pack mod folded in, merge locked to rebirth 1 |
| D9 | `docs/answered/gear.md` line 175 | gathering armor sets "reset to T1 on rebirth keeping rarity" (+ rolls) |
| D10 | `docs/answered/gear.md` line 178 (G6, 2026-10-13, newest) | "on rebirth your tools reset with you (keep rarity, and roll, but reset to crude level 1. all upgrade points are gone/ removed. BUT you get a REBIRTH modifier (what the rebirth modifier does to your pickaxe is controlled by the skill tree. (if we cant make that work, ittl be a base stat multiplier to all stats on the pickaxe.)" |
| D11 | `docs/answered/economy.md` line 101 | "on rebirth the bank keeps all your money, in exchange they give you a better interest rate on your money, based on the balance at reset." |
| D12 | `docs/answered/economy.md` line 88 | interest: once per real day, account-wide brackets 2 % / 1 % / 0.5 % |
| D13 | `tools/PROFILES-CONTRACT.md` | one profile = one class = its own skills, coins, bank, collections...; data by `pkey` |
| D14 | `research/Architecture-Spec.md` "Requirement added 2026-10-13" | "Modules talk only through SkyyCore (typed bridge handles, events, shared services) - never by calling another module's classes directly." |

**Conflicts found and how this spec reads them**

| Topic | Older text | Newer Skyy words | This spec |
|---|---|---|---|
| Tool level after rebirth | gear.md line 168: "its level resets to 0" | gear.md line 178 (G6): "reset to crude level 1" | **level 1** (a level-0 tool makes no sense once level = skill level, G2) |
| Tool upgrade points | `research/Gathering-Shards-Spec.md` section 3.3: "keep rarity, modifiers and points" | G6: "all upgrade points are gone/ removed" | **points removed**. The local session should fix section 3.3 of that spec (outside `research/cloud/`). |
| Bank: two lines | skills.md line 115 popup: RESETS = "Coins + bank" | economy.md line 101: "the bank keeps all your money, in exchange ... a better interest rate ... based on the balance at reset" | **Both apply, to the same money.** The player's purse and bank balance go to 0 (that is the "reset"); the bank "keeps" it (it is gone for the player); the balance at that moment sets a **permanent interest-rate bonus**. There is no line that says "you lose the money with nothing back" - the loss always comes with the rate bonus. Open: does the purse count toward "balance at reset" (Q7). |

`research/Gems-Ideas.md` and `research/Shard-Islands-Ideas.md` do not mention rebirth.

### Existing mods checked (PROJECT-RULES: check existing mods)

Web search 2026-10-13 (CurseForge Hytale): **no Hytale mod advertises prestige or rebirth.** The leveling mods (RPG Leveling,
Endless Leveling, LevelingCore, MMO Skill Tree) do levels, stats and skill XP, not resets. `research/Gathering-Shards-Spec.md`
reached the same result for the installed pack ("No installed or surveyed mod does ... rebirth"). So we build our own.
What to learn: from the clicker games in `research/cloud/Rebirth-Research.md` section 1 - show the gain BEFORE the click, list
"Resets / Stays" plainly (players hate surprise losses), use a root-shaped point formula so extra grinding pays but never runs away,
and keep the number of currencies readable. Sources: [CurseForge Hytale mods](https://www.curseforge.com/hytale/mods),
[CurseForge top RPG mods](https://blog.curseforge.com/top-10-hytale-rpg-mods-you-need-to-try-on-curseforge/).

## 1. What resets and what stays (per system)

"Run XP" = XP earned since the last rebirth, counted past the max level (D3). Everything is per profile (D13).

| System (mod today) | Resets | Stays | Source |
|---|---|---|---|
| Class level / class skill XP (SkyySkills, SkyyClasses) | level + XP to the start; run XP is paid out as Class points first | the class itself (locked to the profile) | D2, D3 |
| Every other skill: Mining, Foraging, Farming, Fishing, ... (SkyySkills) | level + XP; run XP paid out as that skill's points | - | D2, D3, D7 ("All together") |
| Coins purse (SkyyCoins) | to 0 (Q8: or a starter amount) | - | D2, D11 |
| Bank balance (SkyyBank) | to 0 | a permanent interest-rate bonus, scaled by the balance at reset | D11 |
| Island + co-op (SkyyIslands) | - | everything | D1 |
| Shards, shard islands, totems, shard upgrades (SkyyShards, planned) | - | everything ("it will not lose any upgrades") | D1, D2 |
| Collections (SkyyCollections) | - | counts + unlocked recipes ("retain the knowledge"); MORE ranks open behind rebirths | D2 |
| Combat gear, accessories, bags, Void contents, vault | - | all items ("gear isnt lost or locked away"); level gates make high gear idle until you re-level | D2 |
| Lifelong tools: pickaxe, axe, hoe, sickle, fishing pole (SkyyGear) | tier back to Crude, level to 1 (follows the skill), all upgrade points removed | rarity + rolls; GAINS a rebirth modifier | D7, D8, D10 |
| Shovel | - (normal item, no rebirth rule) | everything | D8 |
| Gathering armor sets (SkyyGear) | tier back to T1; level follows the skill | rarity + rolls | D9 |
| Fishing reels, hooks, line, sinkers | - (crafted parts, just items) | everything | D5 |
| Rebirth tree, rebirth points, rebirth count, titles | - | everything (never reset) | D2, D3 |
| Skill trees bought with dust (SkyyTrees) | not decided | not decided | **Q4** |
| Class path tree (Ability Points come from the class skill) | not decided | not decided | **Q5** |
| Quests (SkyyQuests) | not decided - but see the note | | **Q6** |
| Pets, Exploration spots, Acrobatics | not decided ("every skill" covers Exploration + Acrobatics XP if they are skills) | | **Q3** |

Note on quests: the T1 shards are quest rewards (D6). If quest "done" flags reset, a player could farm a second set of T1 shards
every rebirth, which breaks "more can be crafted after rebirth 2". So the default for Q6 is **quests stay done**.

## 2. Requirements and the controller

### 2.1 Requirement (from Skyy)

- **Class at max class level** (D3). Other skills do NOT need to be max ("even if mining isnt max").
- The max rises with each rebirth (D2), so the requirement for rebirth N+1 is the raised class cap.
- One rebirth resets every skill + the class together; there is no single-skill rebirth (D7).
- Safety requirements this spec adds (Q9 confirms): player online, on their own island or the hub, not in combat, no profile switch
  running (`profile:busy` absent), no Bazaar / Auction orders or listings open, no rebirth already in flight.

### 2.2 The controller - Nexus of the Void (Skyy, D3 + D4)

- `/rebirth` opens ONE page with ONE tree that radiates out from a black hole in the centre: the Nexus of the Void. Lore (Skyy): "by
  touching it, the void imprints your soul, altering you in strange ways."
- **Hover** the Nexus: the requirements (met / not met) and what this rebirth will give.
- **Click** it, then **confirm**: the rebirth runs.
- Layout, states and the confirm panel: `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md` (the confirm step needs a
  "Resets / Stays / You gain" list; the 3-second count there is its own Skyy question).

### 2.3 Tree: shared or per skill (Skyy, D3 + D7)

| Rule | Skyy |
|---|---|
| One menu, one tree | "there is 1 rebirth menu with an upgrade tree" |
| One branch (arm) per skill; each arm spends its own points | "your upgrade points are seprate per skill. so you get class rebirth upgrade points, mining rebirth upgrade points, farming, and so on." |
| Extra XP after max still counts | "it keeps tracking the xp gain even past max lvl. so you can stack up a ton of exta mining and farming xp while trying to max your class. then have a ton more points" |
| Costs | "upgrades start cheap, and scale pretty quickly" (like dust) |
| Rows | no unlock point; "like 8 total levels in the first row to unlock the next row" |
| Fallback | gear.md line 168: "if we cant do the one big tree, we can do a tree per skill" around the Nexus |
| Tool modifier | upgraded in that skill's arm (pickaxe -> Mining arm, axe -> Foraging, hoe + sickle -> Farming, pole -> Fishing); if that can't work: a base stat multiplier on all the tool's stats (D10) |

Which skills get an arm beyond Class, Mining, Foraging, Farming, Fishing: **Q2**.

## 3. Rewards per rebirth

Skyy's REWARDS popup picked all four: stat boost per rebirth, rebirth points shop (the tree), cosmetics + title, new content (D2).

| Rebirth # | Fixed by Skyy | Numbers still open |
|---|---|---|
| Every rebirth | stacking stat boost; points per skill from run XP; higher class + skill caps; more collection ranks; bank rate bonus from the balance at reset; tools gain / keep the rebirth modifier | stat boost size + cap (Q10); point formula (Q11); cap step (Q12); max rebirths (Q13); rate formula + cap (Q7) |
| 1 | the Multitool merge unlocks (pickaxe + axe, no stat loss, no downside) (D7, D8) | - |
| 2 | crafting extra shards unlocks (D6) | which shards / recipes (shard spec) |
| Titles / cosmetics | "Cosmetics + title" (D2) | names + which rebirths (Q14) |

## 4. Data model

### 4.1 Who owns what

The rebirth is its own module: **`rebirth`**. Today (31 jars) it ships as a small new jar **SkyyRebirth**; after the
architecture merge it becomes a module inside **SkyyCharacter** (`research/Architecture-Spec.md` 1.1 row 1) with no code change,
because it only talks through the bridge (D14). It owns: the rebirth counter, the points, the tree, the page, the journal.
It never writes another mod's files. Every other mod changes its own data when the rebirth module asks (section 5).

### 4.2 Files (all per profile, named by `pkey`, per `tools/PROFILES-CONTRACT.md` rule 1)

| Owner | File | New fields |
|---|---|---|
| SkyyRebirth | `Skyy_SkyyRebirth/players/<pkey>.properties` | `n` (rebirths done), `pts.<Arm>` (unspent), `spent.<Arm>`, `node.<id>` (level), `title`, `lastTx`, `hist.<n>` = time + summary line |
| SkyyRebirth | `Skyy_SkyyRebirth/journal/<pkey>.journal` | the two-phase journal (5.2) |
| SkyySkills | `players/<pkey>.properties` | `run.<Skill>` (run XP, counts past max - UNVERIFIED whether a field like this exists), `rb.lastTx` |
| SkyyGear | lifelong item documents + `lifelong/<pkey>.properties` (Gathering-Shards spec 5.1) | `rb` (rebirth modifier level, read from the tree), `tier`, `lvl`, `up.*` cleared; `rb.lastTx` |
| SkyyBank | account file `<pkey>` | `rb.bonus` (percentage points), `rb.hist.<n>` = balance at reset, `rb.lastTx` |
| SkyyCoins | purse file `<pkey>` | `rb.lastTx` |
| SkyyTrees | `players/<pkey>.properties` | per Q4 / Q5; `rb.lastTx` |

Every participant stores `rb.lastTx` in the SAME atomic write as its reset. That one field makes every reset idempotent (5.3).

### 4.3 Bridge keys (java.lang types only; `skyy.bridge` today, SkyyCore typed handles later - same names, Architecture 3.3 aliases)

| Key | Type | Written by | Read by |
|---|---|---|---|
| `rebirth:n:<uuid>` | Integer, active profile; republished on `profile:epoch` change | SkyyRebirth | HUD, Gear (Multitool gate, n >= 1), Shards (craft gate, n >= 2), Collections (extra ranks) |
| `rebirth:fn:count` | Function(String pkey) -> Integer | SkyyRebirth | offline readers, leaderboards |
| `rebirth:fn:cap` | Function(Object[]{String pkey, String skill}) -> Integer (current max level) | SkyyRebirth | SkyySkills (level cap), SkyyCollections (rank cap) |
| `rebirth:fn:node` | Function(Object[]{UUID, String nodeId}) -> Integer level | SkyyRebirth | Gear (tool modifier), Skills, any mod with a tree effect |
| `rebirth:busy:<uuid>` | Boolean.TRUE while a rebirth of that player is in flight | SkyyRebirth | Economy, Profiles, Skills (5.4) |
| `rebirth:fn:busy` | Function(String pkey) -> Boolean | SkyyRebirth | offline payouts (AH sales, interest) |
| `rebirth:fn:decision` | Function(String txid) -> String `commit` / `abort` / `unknown` | SkyyRebirth | participants on their own start-up |
| `rebirth:part:<name>` | Function(Object[]{String op, String pkey, String txid, Integer newN}) -> String | each participant (`skills`, `coins`, `bank`, `gear`, `trees`, ...) | SkyyRebirth only |
| `skill:bonus` (existing) | source `rebirth` | SkyyRebirth | SkyySkills (the stacking stat boost - UNVERIFIED that the map takes stat lines) |

Participant function `op` values: `prepare`, `commit`, `abort`, `status`. Answers: `ok:<k=v;k=v>` (the facts the coordinator needs,
e.g. `runxp.Mining=123456;balance=4800000`), `done` (this txid is already applied), or `err:<reason>`. They never throw, never call
another mod back, and run on the caller's thread (same rules as `class:fn:kitnew` in the contract).

## 5. Safety: a journaled two-phase commit

A rebirth changes 4-6 mods' files for one profile and cannot be undone by the player. A crash at ANY point must leave the profile
either fully before or fully after the rebirth - never half, never twice, nothing lost, nothing duplicated.

### 5.1 Principles

1. **Nothing is deleted, no item moves.** Items are kept by design (D2); tools change in place (the item is a view of its document).
   So there are no item moves to duplicate. Only numbers change: levels, XP, coins, tiers, points.
2. **One pkey per rebirth.** Resolved once at the click, written in the journal, used for every step (contract 4.1). A profile
   switch is refused while `rebirth:busy` is set.
3. **Deltas, not absolutes, for anything that can change meanwhile.** Commit subtracts what prepare measured (`bank = bank -
   balanceAtPrepare`, `run.Mining = run.Mining - runAtPrepare`) so an interest payout or an XP tick between the two phases survives.
4. **Decide once, then only go forward.** Before the decision a crash aborts (nothing changed). After the decision a crash rolls
   forward (every participant finishes). Never roll back after the decision.
5. **Backups first.** Each participant copies its `<pkey>` files to `<its data>/rebirth-backup/<pkey>/<txid>/` in `prepare`
   (tmp + fsync + rename + read back - the SkyyCore journaled IO). Keep the last 3 per profile. Admins can restore by hand
   (`/rebirthadmin backup list <player>`); there is no player undo.

### 5.2 The steps

| Step | Who | What | Journal after the step |
|---|---|---|---|
| 0 | Rebirth | Click + confirm. Check requirements (2.1). Create `txid` (UUID). Set `rebirth:busy:<uuid>`. | `BEGIN txid pkey newN` |
| 1 | each participant | `prepare`: back up its files, measure (run XP, levels, purse, balance, tool docs), write a STAGED file `<pkey>.rb-<txid>` with the planned new state, answer `ok:<facts>`. Live data is NOT touched. | `PREPARED <part> <facts>` per part |
| 2 | Rebirth | If every REQUIRED participant answered ok: compute the rewards from the facts (points per arm, bank bonus input, new caps) and write them INTO the journal. This write is the decision. Any err / missing required part: send `abort` to all. | `DECIDED commit <rewards>` or `DECIDED abort` |
| 3 | each participant | `commit`: apply the staged state in ONE atomic write that also sets `rb.lastTx=txid`; delete the staged file; answer `ok`. If `rb.lastTx` already equals txid: answer `done` and do nothing. | `COMMITTED <part>` per part |
| 4 | Rebirth | Apply its own state (n+1, points, title) the same way (`lastTx`). Republish `rebirth:n`, clear `rebirth:busy`, play the scene. | `DONE` |
| 5 | Rebirth | After `DONE`, the journal file is moved to `journal/done/` (kept 30 days, never deleted sooner). | - |

Required participants: Skills, Coins, Bank, Gear (when lifelong tools exist), Rebirth itself. Optional: Trees, Collections (nothing
to reset today). A missing optional participant is skipped and logged; a missing required one blocks the rebirth (hover shows it).

### 5.3 Crash recovery

| Crash point | On restart / next join (before the player can act) |
|---|---|
| Before `DECIDED` | Rebirth sends `abort` to every part: each deletes its staged file. The profile is exactly as before. Backups stay. |
| After `DECIDED commit`, some parts done | Rebirth re-sends `commit` to every part not marked COMMITTED. Parts already done answer `done` (thanks to `rb.lastTx`). Then step 4. |
| A part crashed inside its own write | The atomic rename means its file is either fully old or fully new; `rb.lastTx` tells which. |
| A part's jar is missing at recovery | The journal stays at DECIDED; `rebirth:busy` stays set; the player sees "Rebirth finishing - waiting for <mod>". Rebirth retries every start-up. |
| A part restarts with a staged file but no answer yet | It asks `rebirth:fn:decision(txid)`: `commit` -> apply; `abort` -> delete; `unknown` / Rebirth missing -> keep the staged file, change nothing live. |

### 5.4 The busy window (usually under a second)

While `rebirth:busy:<uuid>` is set: SkyyProfiles refuses a switch; coins and bank refuse spends, `/pay`, trades and Bazaar /
AH actions for that player (income still lands - principle 3 keeps it); SkyySkills keeps adding XP normally (deltas). Offline
payouts check `rebirth:fn:busy(pkey)` and simply land (deltas). The confirm page stays open as a "the void is imprinting your soul"
scene until `DONE`.

### 5.5 Tests (local session, test server)

Kill the server after each step 0-4 (a `/rebirthadmin crashtest <step>` op flag that halts after that step) and rejoin: check
levels, purse, bank, tool docs, counter and points against the expected before / after. Run two rebirths in a row; run with one
required jar removed; run with an interest payout forced between steps 1 and 3.

## 6. Build order (smallest first; each a normal local round, the Balance Workbench refreshed when numbers change)

| Round | Mods | What | Visible to players |
|---|---|---|---|
| R1 | SkyySkills | Run XP per skill counted past max (`run.<Skill>`) + read caps from `rebirth:fn:cap` when present. Check first whether XP already counts past max (UNVERIFIED). | no |
| R2 | SkyyRebirth (new, off by default) | Counter, files, bridge keys, `/rebirth` page with the Nexus and the hover requirements, no button yet. Probe the radiating tree layout (page spec, UNVERIFIED items). | admins only |
| R3 | SkyyRebirth + SkyySkills + SkyyCoins + SkyyBank + SkyyProfiles (switch lock) | The two-phase commit with the first required parts; `/rebirthadmin` dry-run + crashtest; bank rate bonus. | admins only |
| R4 | SkyyGear | Lifelong tool + gathering armor participant (needs the lifelong tools from the Gathering-Shards build first); Multitool merge gate `rebirth:n >= 1`; tool rebirth modifier read from `rebirth:fn:node`. | yes, after switch-on |
| R5 | SkyyRebirth | The tree: arms, rows (8 levels opens the next), costs, points spending, the stacking stat boost, titles. Fallback: one tab per arm. | yes |
| R6 | SkyyCollections, SkyyShards, SkyyTrees | Extra collection ranks behind rebirth; shard crafting gate `n >= 2`; dust / class tree handling per Q4 / Q5. | yes |
| R7 | all | Switch on for players; Skyy test with a fresh test profile pushed to class max by an admin command. | yes |

## 7. Questions for Skyy (only what the sources don't decide)

| # | Question | Recommended default |
|---|---|---|
| 1 | Is SkyyRebirth a new small jar now, then a module inside SkyyCharacter after the merge? | Yes |
| 2 | Which skills get a rebirth arm besides Class, Mining, Foraging, Farming, Fishing? (Alchemy, Smithing, Cooking, Acrobatics, Exploration) | Add Alchemy, Smithing, Cooking (8 arms, as in the page mockup); Acrobatics + Exploration no arm |
| 3 | Do Acrobatics and Exploration levels reset too ("every skill")? Do pet levels reset? | Acrobatics + Exploration reset; pets stay |
| 4 | Dust skill trees (Mining / Foraging / ... trees bought with dust): keep the bought nodes? | Keep (they are permanent upgrades, like shard upgrades) |
| 5 | Class path tree: Ability Points come from the class skill, so they drop at reset. What happens to your picks? | Picks are remembered and switch back on, in the order you bought them, as your AP return |
| 6 | Quests: stay done after a rebirth? (otherwise T1 shards could be farmed again) | Stay done |
| 7 | Bank bonus: does the purse count in "balance at reset", and what formula + cap? | Purse + bank both count; +0.25 x log10(1 + balance / 100,000) percentage points, max +1 per rebirth, max +3 total (Rebirth-Research 2.6) |
| 8 | Purse after rebirth: 0 or a small starter amount? | 0 (the island, shards and gear keep you going) |
| 9 | Extra safety requirements: no open Bazaar / AH orders or listings, not in combat, on island or hub? | Yes, all three (blocks with a checklist in the hover) |
| 10 | Stacking stat boost per rebirth: how much, any cap? | +3 % all stats per rebirth, cap +30 % |
| 11 | Points per skill from run XP: formula? | floor(B x sqrt(run XP / XP to that skill's cap)), B = 12 class / 8 skills; under 25 % pays 0 (Rebirth-Research 2.3) |
| 12 | How much do the caps rise per rebirth (class, skills, collection ranks)? | +10 levels per rebirth; +1 collection rank per rebirth |
| 13 | Max number of rebirths at launch? | 10 (raise later) |
| 14 | Titles / cosmetics: names and when? | A title each rebirth ("Void-Touched I" ...), a cosmetic every 3rd rebirth |
| 15 | Moving coins into items before rebirth (buy Bazaar goods, sell after) keeps money. Block it? | Allow - the bank bonus already rewards keeping money in the bank, and the Bazaar tax eats some |
| 16 | Profile scope: rebirth is per profile (each class profile rebirths on its own)? | Yes, per profile (contract) |

## For the local session (UNVERIFIED - needs the code or the game)

- Whether SkyySkills already counts XP past max level and stores it; the real max class / skill level today (100?) and the XP to cap.
- Whether `skill:bonus` can carry the rebirth stat boost (stat lines, source `rebirth`).
- Lifelong tools are not built yet: the "item is a view of its document" refresh (tool tier / level change in the live inventory)
  must exist before R4.
- SkyyProfiles needs a small patch: refuse a switch while `rebirth:busy:<uuid>` is set.
- Fix `research/Gathering-Shards-Spec.md` section 3.3 + line 32 to Skyy's G6 words (level 1, upgrade points removed) - a file
  outside `research/cloud/`, so a local edit or a PR.
- The page probes listed in `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md` (big page, many buttons, line images).
- Bank: check the rate bonus against `research/cloud/Bank-Tab-Calibration.md` (account-wide brackets).
