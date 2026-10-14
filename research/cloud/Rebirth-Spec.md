# Rebirth (New Game+) - build spec

Cloud draft 2026-10-13, FINAL after Skyy answered all 16 questions (`docs/answered/economy.md` "2026-10-13 REBIRTH" lines, which win
over anything below). Paper design; nothing built, nothing compiled. Research behind it: `research/cloud/Rebirth-Research.md`
(clicker games, formulas) and `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md` (the page). This spec adds the rules, the
data and the safety plan. Where an older draft says something different, Skyy's newest words win.

## 0. Decisions this follows (Skyy's words)

| # | Source line | What it fixes |
|---|---|---|
| D1 | `docs/answered/skills.md` line 114 | "some sort of rebirth system that gives a few permanent upgrades. but resets your level ... but your island stays the same" |
| D2 | `docs/answered/skills.md` line 115 | popups: RESETS = "Skill levels, Coins + bank"; "gear isnt lost or locked away, you just cant use it because of levels"; "you retain the knowledge from collections"; "more collection levels, and higher skill/class levels locked behind a rebirth"; REWARDS = "Stat boost per rebirth, Rebirth points shop, Cosmetics + title, New content" |
| D3 | `docs/answered/skills.md` line 117 | "1 rebirth menu with an upgrade tree"; "you can rebirth when you reach max class level. even if mining isnt max"; "your upgrade points are seprate per skill"; "it keeps tracking the xp gain even past max lvl"; "upgrades start cheap, and scale pretty quickly"; "you just need like 8 total levels in the first row to unlock the next row"; "the trees [...] radiate from the blackhole in the center (the nexus of the void.)" |
| D4 | `docs/answered/skills.md` line 118 | "the nexus of the void is the controller for the rebirth. so in /rebirth you hover over it to see what requirements you have to reach, and what you will get when you rebirth. you click it, then confirm to rebirth." |
| D5 | `docs/answered/skills.md` lines 119-120 | the fishing POLE is lifelong; "fishing gets its own skill, and skill tree" (own rebirth arm) |
| D6 | `docs/answered/skills.md` line 121 | "all T1 shards come from quests. (more can be crafter after rebirth 2." |
| D7 | `docs/answered/gear.md` line 168 | all skills rebirth together; fallback "one tree per skill around the Nexus"; tools get "a rebirth modifier which can be upgraded in the mining rebirth tree"; "unlock the multi tool after the first rebirth" |
| D8 | `docs/answered/gear.md` lines 170, 172 | lifelong = pickaxe, axe, hoe, sickle, fishing pole; the shovel is NOT lifelong; Multitool merge locked to rebirth 1 |
| D9 | `docs/answered/gear.md` line 175 | gathering armor sets "reset to T1 on rebirth keeping rarity" (+ rolls) |
| D10 | `docs/answered/gear.md` line 178 (G6) | "reset to crude level 1. all upgrade points are gone/ removed. BUT you get a REBIRTH modifier" (fallback: a base stat multiplier on all the tool's stats) |
| D11 | `docs/answered/economy.md` line 101 | "on rebirth the bank keeps all your money, in exchange they give you a better interest rate on your money, based on the balance at reset." |
| D12 | `docs/answered/economy.md` line 88 | interest: once per real day, account-wide brackets 2 % / 1 % / 0.5 % |
| D13 | `tools/PROFILES-CONTRACT.md` | one profile = one class = its own skills, coins, bank, collections...; data by `pkey` |
| D14 | `research/Architecture-Spec.md` "Requirement added 2026-10-13" | modules talk only through SkyyCore / the bridge, never by calling another module's classes |
| D15 | `docs/answered/economy.md` lines 103-117 (2026-10-13 REBIRTH) | the 16 answers + pets + ability levels - summarised in section 7 |

Older text replaced: tool level after rebirth = **level 1** (G6 beats gear.md 168 "level 0"); tool upgrade points **removed** (G6 beats
`research/Gathering-Shards-Spec.md` 3.3 - the local session fixes that file). Bank: purse + bank go to 0 and the balance at reset buys
a permanent rate bonus (D2 + D11 both apply).

### Existing mods checked

CurseForge Hytale 2026-10-13: no mod does prestige / rebirth (RPG Leveling, Endless Leveling, LevelingCore, MMO Skill Tree do levels
only); the installed pack has none either. We build our own and borrow the clicker-game lessons (`research/cloud/Rebirth-Research.md`
section 1): show the gain before the click, list "Resets / Stays" plainly, root-shaped point curve.

## 1. What resets and what stays (per profile)

"Run XP" = XP earned since the last rebirth, counted past the max level (D3).

| System (owner mod) | Resets | Stays | Source |
|---|---|---|---|
| Class level / class skill XP (SkyySkills) | level + XP to the start; run XP paid out as Class points | the class itself | D2, D3 |
| Mining, Foraging, Farming, Fishing, Alchemy, Smithing, Cooking, **Acrobatics** (SkyySkills) | level + XP; run XP paid out as that arm's points (Acrobatics: no arm, no points) | - | D3, Q2, Q3 |
| **Exploration** (SkyySkills / SkyyExploration) | - | level, XP, found spots | Q3 "exploration, no." |
| **Pets** (SkyyPets) | - | pets + their levels | Pets popup |
| Coins purse (SkyyCoins) | to **0** | - | Q8 |
| Bank balance (SkyyBank) | to 0 | permanent rate bonus from purse + bank at reset (3.3) | D11, Q7 |
| Island + co-op, shards + shard upgrades | - | everything | D1, D2 |
| Collections (SkyyCollections) | - | counts + recipes; +1 rank cap per rebirth | D2, Q12 |
| Combat gear, accessories, bags, Void, vault | - | all items; level gates idle them until you re-level | D2 |
| Lifelong tools: pickaxe, axe, hoe, sickle, fishing pole (SkyyGear) | tier to **Crude**, level to **1**, **all upgrade points removed** | rarity + rolls; GAINS / keeps the rebirth modifier | D10 (G6) |
| Shovel, fishing reels / hooks / line / sinkers | - (plain items) | everything | D5, D8 |
| Gathering armor sets (SkyyGear) | tier to T1; level follows the skill | rarity + rolls | D9 |
| **Dust skill trees** (SkyyTrees): Mining, Foraging, Farming, Fishing, Alchemy, Smithing, Cooking, Acrobatics | **every bought node, no dust refund**; Dust itself restarts (it comes from XP, which resets) | - | Q4 |
| **Class path tree** (SkyyTrees, AP from the class skill) | AP drop with the class level | **every pick, remembered in purchase order**; each switches back on when your AP cover it again | Q5 |
| **Ability levels + unlocked modifiers** (SkyyClasses) | - (soft-capped while the class level returns, 3.2) | saved levels, modifiers, modifier points, equips | Ability-levels line |
| **Quests** (SkyyQuests) | - | done flags; one-time rewards (T1 shards, gear) never paid twice | Q6 |
| Rebirth tree, points, count, titles, cosmetics, dust multiplier | - | everything, forever | D2, D3 |

## 2. Requirements and the controller

### 2.1 Requirements

- **Class at max class level** (D3). Other skills need not be max. The max rises +10 per rebirth (Q12), so rebirth N+1 needs the raised cap.
- All skills + the class rebirth together (D7). **Max 10 rebirths** at launch (Q13; a config value, raise later).
- Hard checks (Q9 "all three"), each shown as a line in the Nexus hover, met / not met:

| Check | If not met |
|---|---|
| No open Bazaar orders / AH listings | the confirm panel lists them and offers **Continue**: it auto-closes them all (items + coins refunded, see 2.4), then goes on |
| Not in combat (`skill:fn:combat` = 0) | blocked - wait |
| On your own island or at the hub | blocked - go there |

Silent checks (no player text unless they fail): player online, no profile switch running (`profile:busy`), no rebirth in flight.

### 2.2 The controller - Nexus of the Void (D3 + D4)

`/rebirth` opens ONE page, ONE tree radiating from the black hole in the centre. Hover the Nexus = requirements + what you gain;
click, then confirm = rebirth. Layout: `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md`. The confirm panel shows
"Resets / Stays / You gain" (section 1 in short) before the click.

### 2.3 Tree: 8 arms (Q2)

| Arm | Points from | Tool modifier node |
|---|---|---|
| Class | class run XP | - (class arm holds the stat / ability nodes) |
| Mining | Mining run XP | pickaxe (and the Multitool) |
| Foraging | Foraging run XP | axe |
| Farming | Farming run XP | hoe + sickle |
| Fishing | Fishing run XP | fishing pole |
| Alchemy | Alchemy run XP | - |
| Smithing | Smithing run XP | - |
| Cooking | Cooking run XP | - |

Acrobatics + Exploration: no arm. Each arm spends only its own points (D3). Costs "start cheap, and scale pretty quickly"; no unlock
point - 8 levels bought in a row open the next row. Every skill arm has a **Dust multiplier** node for its own Dust (3.4).
Fallback if the radiating tree can't be drawn: one tab per arm around the Nexus.

### 2.4 Continue: auto-close orders + listings

Runs BEFORE step 0 of the commit (5.2), as its own normal actions, not inside the rebirth transaction:
SkyyBazaar cancels every open buy / sell order (coins + items back), SkyyAuctions ends every listing with no bid (items back);
a listing WITH a bid cannot be pulled -> it stays a blocking line ("ends in 3 m"). Refunds land where each mod already returns them
(UNVERIFIED: claim stash vs inventory). Then the checks run again; refunded coins count in the bank-bonus balance. Moving coins into
Bazaar goods before a rebirth is **allowed** (Q15).

## 3. Rewards and formulas

### 3.1 Per rebirth

| Reward | Number (Skyy) |
|---|---|
| Stat boost | **+3 % all stats per rebirth, cap +30 %** (= 10 rebirths) (Q10) |
| Class + skill level caps | **+10 levels per rebirth** (Q12) |
| Collection rank cap | **+1 rank per rebirth** (Q12) |
| Max ability level | +1 per rebirth (15 -> 25 at rebirth 10) - proposal, 3.2 |
| Modifier max level | ONE modifier per ability gets +1 max level per rebirth (not all) |
| Modifier slots | **+1 every 5th rebirth** (2 -> 3 at rebirth 5 -> 4 at rebirth 10) |
| Title | every rebirth: Void-Touched I ... X (Q14) |
| Cosmetic | every 3rd rebirth (3, 6, 9) (Q14) |
| Dust | rebirth 1: **2x all Dust**, permanent; more from tree nodes (Q4) |
| Bank rate bonus | 3.3 |
| Content | rebirth 1: Multitool merge (D7, D8); rebirth 2: crafting extra T1 shards (D6) |

### 3.2 Ability levels after a rebirth (SkyyClasses)

Kept: saved ability level `S` (the highest reached), unlocked modifiers + their levels, equips. While the class level `L` climbs back,
each ability works at an **effective level**:

```
F(L)  = first-run ability cap at class level L = min(15, 1 + floor(14 x L / C0))     C0 = first-run class cap (100? UNVERIFIED)
half  = ceil(S / 2)
eff   = min(S, max(F(L), half + floor((S - half) x L / Lr)))                          Lr = class level when you rebirthed
```

So the ability starts at half its saved level (always at least what a first-run player has at that class level), rises in a straight
line with the class level, and is back to full `S` when `L` reaches `Lr`. Example S = 16, Lr = 110: L 1 -> 8, L 55 -> 12, L 110 -> 16
(a first-run player at L 55 has 8). Modifiers follow the same ratio: effective modifier level = min(saved, ceil(saved x eff / S)).
An ability works only once its class-tree pick is back on (Q5) - same as a first run.

Rises per rebirth: the ability level cap is 15 + n (proposal; use keeps levelling past 15 up to it); at each rebirth the player picks,
per ability, ONE modifier whose max level goes +1 (on the Abilities page, "1 upgrade to place"); a modifier slot every 5th rebirth.
Note: F(L) also gives the first run its own soft cap if Skyy ever wants one; today first-run abilities have no class-level cap, so
`F` is used only as this floor.

### 3.3 Bank bonus (Q7)

`balance = purse + bank` at reset (after the Continue refunds). `bonus = min(1, 0.25 x log10(1 + balance / 100,000))` percentage
points this rebirth; total capped at **+3**; added on top of the 2 / 1 / 0.5 % brackets (D12). About +0.25 at 1M, +0.5 at 10M,
+0.75 at 100M, +1 at 1B. Then purse and bank go to 0.

### 3.4 Dust (Q4)

Dust is SkyyTrees' (it computes Dust from `skill:fn:xp` total XP x `dust.xpPerDust.<Tree>`, never stored - `tools/skills_0_4_patch.py`
line 2091, `tools/trees_0_2_patch.py` 13-14). XP resets, so Dust restarts by itself; SkyyTrees clears the bought nodes. New:

`dust = floor(xp / xpPerDust.<Tree> x mult(tree))`, `mult = (n >= 1 ? 2 : 1) x (1 + 0.25 x node level of that arm's Dust node)`.
Proposal: the Dust node has 4 levels (2x -> 4x at max). Acrobatics' Dust (no arm) gets the 2x only. Exploration keeps its XP, so its
Dust stays; see 7.2 for its nodes.

### 3.5 Points per arm (Q11)

```
r      = run XP / XP from level 1 to that skill's current cap
points = 0 if r < 0.25, else floor(B x sqrt(min(r, 16)))       B = 12 Class, 8 each skill
```

r = 1 (exactly maxed) pays B. **XP past max keeps counting** on the same sqrt curve: 4x the cap's XP pays 2B, 9x pays 3B, capped at
16x = 4B (48 Class / 32 skill points) so a long grind pays well but never runs away. Class r is always >= 1 (the class must be max).

## 4. Data model

### 4.1 Who owns what

The rebirth is its own module `rebirth`: **a small new jar SkyyRebirth now** (Q1), a module inside SkyyCharacter after the SkyyCore
merge with no code change (it only talks through the bridge, D14). It owns the counter, points, tree, page, journal, titles and the
dust multiplier. It never writes another mod's files; each mod changes its own data when asked (section 5). Rebirth is **per profile** (Q16).

### 4.2 Files (per profile, by `pkey`)

| Owner | File | New fields |
|---|---|---|
| SkyyRebirth | `Skyy_SkyyRebirth/players/<pkey>.properties` | `n`, `pts.<Arm>`, `spent.<Arm>`, `node.<id>`, `title`, `cos.<n>`, `lastTx`, `hist.<n>` |
| SkyyRebirth | `Skyy_SkyyRebirth/journal/<pkey>.journal` | the two-phase journal (5.2) |
| SkyySkills | `players/<pkey>.properties` | `run.<Skill>` (UNVERIFIED if XP past max is stored today), `rb.lastTx`; Exploration untouched |
| SkyyGear | lifelong item docs + `lifelong/<pkey>.properties` | `rb` (modifier level from the tree), `tier`, `lvl`, `up.*` cleared; `rb.lastTx` |
| SkyyBank | account `<pkey>` | `rb.bonus`, `rb.hist.<n>` (balance at reset), `rb.lastTx` |
| SkyyCoins | purse `<pkey>` | `rb.lastTx` |
| SkyyTrees | `players/<pkey>.properties` | skill-tree nodes cleared (not Exploration, 7.2); `cls.order` = class picks in purchase order (kept; owned = the first k picks your AP cover); `rb.lastTx` |
| SkyyClasses | `Skyy_SkyyClasses/players/<pkey>.properties` | `rb.S.<ability>` (saved level), `rb.Lr`, `rb.modmax.<ability>.<mod>` (+levels), `rb.modPick.<ability>` (unplaced picks); `rb.lastTx` |

Every participant stores `rb.lastTx` in the SAME atomic write as its reset - that makes each reset idempotent (5.3).

### 4.3 Bridge keys (java.lang types only)

| Key | Type | Written by | Read by |
|---|---|---|---|
| `rebirth:n:<uuid>` | Integer, active profile; republished on `profile:epoch` | SkyyRebirth | HUD, Gear (Multitool n >= 1), Shards (n >= 2), Collections, Classes (slots, ability cap) |
| `rebirth:fn:count` | Function(String pkey) -> Integer | SkyyRebirth | offline readers, leaderboards |
| `rebirth:fn:cap` | Function(Object[]{pkey, skill}) -> Integer | SkyyRebirth | SkyySkills (level caps), SkyyCollections (rank cap) |
| `rebirth:fn:node` | Function(Object[]{UUID, nodeId}) -> Integer | SkyyRebirth | Gear (tool modifier), any tree effect |
| `rebirth:fn:dustmult` | Function(Object[]{pkey, tree}) -> Double | SkyyRebirth | SkyyTrees (3.4) |
| `rebirth:busy:<uuid>` / `rebirth:fn:busy` | Boolean / Function(pkey) -> Boolean | SkyyRebirth | Economy, Profiles, Skills, offline payouts |
| `rebirth:fn:decision` | Function(txid) -> `commit` / `abort` / `unknown` | SkyyRebirth | participants at start-up |
| `rebirth:part:<name>` | Function(Object[]{op, pkey, txid, newN}) -> String | each participant: `skills`, `coins`, `bank`, `gear`, `trees`, `classes` | SkyyRebirth only |
| `bazaar:fn:closeall` / `ah:fn:closeall` | Function(pkey) -> String `ok:<n closed>` / `err:<reason>` | SkyyBazaar / SkyyAuctions | SkyyRebirth (Continue, 2.4) |
| `skill:bonus` (existing) | source `rebirth` | SkyyRebirth | SkyySkills (+3 % stats - UNVERIFIED that it takes stat lines) |

Participant `op`: `prepare`, `commit`, `abort`, `status`. Answers `ok:<k=v;...>`, `done`, or `err:<reason>`; never throw, never call
another mod back. SkyyClasses' `prepare` reports `classLvl` (becomes `rb.Lr`) and stores `S` per ability; its `commit` adds the new
modifier pick and nothing else (ability data is kept).

## 5. Safety: a journaled two-phase commit

A rebirth changes 6-7 mods' files for one profile and cannot be undone by the player. A crash at ANY point must leave the profile
fully before or fully after - never half, never twice, nothing lost, nothing duplicated.

### 5.1 Principles

1. **Nothing is deleted, no item moves.** Items are kept (D2); tools change in place. Only numbers change. (The Continue auto-close
   in 2.4 runs before and outside the transaction, through each market's own normal cancel.)
2. **One pkey per rebirth**, fixed at the click; a profile switch is refused while `rebirth:busy` is set.
3. **Deltas, not absolutes**, for anything that can change meanwhile (`bank = bank - balanceAtPrepare`).
4. **Decide once, then only go forward.** Before the decision a crash aborts; after it a crash rolls forward.
5. **Backups first.** Each participant copies its `<pkey>` files to `<its data>/rebirth-backup/<pkey>/<txid>/` in `prepare`; keep the
   last 3 per profile; admins restore by hand (`/rebirthadmin backup list <player>`); no player undo.

### 5.2 The steps

| Step | Who | What | Journal |
|---|---|---|---|
| 0 | Rebirth | Click + confirm. Re-check 2.1. Create `txid`. Set `rebirth:busy:<uuid>`. | `BEGIN txid pkey newN` |
| 1 | each participant | `prepare`: back up, measure (run XP, levels, purse, balance, tool docs, class level), write a STAGED `<pkey>.rb-<txid>`, answer `ok:<facts>`. Live data untouched. | `PREPARED <part> <facts>` |
| 2 | Rebirth | All required ok: compute points (3.5), bank bonus (3.3), caps, write them into the journal = the decision. Else `abort` to all. | `DECIDED commit <rewards>` / `DECIDED abort` |
| 3 | each participant | `commit`: apply the staged state in ONE atomic write with `rb.lastTx=txid`; delete the staged file. Already applied: `done`. | `COMMITTED <part>` |
| 4 | Rebirth | n+1, points, title, cosmetic, dust multiplier (`lastTx`). Republish `rebirth:n`, clear busy, play the scene. | `DONE` |
| 5 | Rebirth | Move the journal to `journal/done/` (kept 30 days). | - |

Required: Skills, Coins, Bank, Trees, Classes, Gear (once lifelong tools exist), Rebirth. Optional: Collections (nothing to reset).
A missing required jar blocks the rebirth (the hover shows it).

### 5.3 Crash recovery

| Crash point | On restart / next join |
|---|---|
| Before `DECIDED` | `abort` to all: staged files deleted; profile exactly as before. |
| After `DECIDED commit` | re-send `commit` to parts not COMMITTED (done ones answer `done`), then step 4. |
| Inside a part's write | atomic rename: file fully old or fully new; `rb.lastTx` tells which. |
| A part's jar missing | journal stays DECIDED, busy stays set, "Rebirth finishing - waiting for <mod>", retried every start-up. |
| Staged file, no answer | ask `rebirth:fn:decision(txid)`: commit -> apply, abort -> delete, unknown -> keep staged, change nothing live. |

### 5.4 The busy window (under a second)

SkyyProfiles refuses a switch; coins / bank refuse spends, `/pay`, trades, Bazaar / AH actions (income still lands - deltas);
SkyySkills keeps adding XP. The page shows "the void is imprinting your soul" until `DONE`.

### 5.5 Tests (local test server)

`/rebirthadmin crashtest <step>` halts after steps 0-4; rejoin and check levels, purse, bank, tool docs, tree nodes, class picks,
ability levels, counter, points. Two rebirths in a row; one required jar removed; an interest payout forced between steps 1 and 3;
Continue with an open order, a listing with no bid, and a listing with a bid.

## 6. Build order (smallest first; the Balance Workbench refreshed when numbers change)

| Round | Mods | What | Visible |
|---|---|---|---|
| R1 | SkyySkills | Run XP per skill past max (`run.<Skill>`); caps from `rebirth:fn:cap`; Exploration excluded from resets. Check first whether XP already counts past max. | no |
| R2 | SkyyRebirth (new jar, off by default) | Counter, files, bridge keys, `/rebirth` page with the Nexus + hover checks, no button. Probe the radiating tree. | admins |
| R3 | SkyyRebirth + SkyySkills + SkyyCoins + SkyyBank + SkyyProfiles | Two-phase commit with the first parts; `/rebirthadmin` dry-run + crashtest; bank bonus (3.3); purse to 0. | admins |
| R4 | SkyyBazaar + SkyyAuctions | `bazaar:fn:closeall` / `ah:fn:closeall` + the Continue button. | admins |
| R5 | SkyyTrees | Participant: clear skill-tree nodes, keep `cls.order` (re-enable by AP in purchase order); Dust x `rebirth:fn:dustmult`. | yes, after switch-on |
| R6 | SkyyClasses (ability framework, engine E6+) | Participant: `rb.S`, `rb.Lr`; effective level (3.2) at every cast + modifier read; ability cap 15 + n; modifier +1 pick per ability; slot every 5th rebirth (UNVERIFIED: a 3rd / 4th modifier rune slot). Needs ability levels + modifiers built first. | yes |
| R7 | SkyyGear | Lifelong tools + gathering armor participant (Crude, Lv 1, points removed, rebirth modifier from `rebirth:fn:node`); Multitool gate n >= 1. Needs lifelong tools first. | yes |
| R8 | SkyyRebirth | The tree: 8 arms, rows (8 levels opens the next), costs, Dust nodes, tool modifier nodes, +3 % stats, titles, cosmetics, max 10. | yes |
| R9 | SkyyCollections, SkyyShards | +1 rank cap per rebirth; shard crafting gate n >= 2. | yes |
| R10 | all | Switch on; Skyy tests on a fresh profile pushed to class max by an admin command. | yes |

## 7. Decisions (2026-10-13)

### 7.1 Skyy's answers

| # | Question | Skyy's answer |
|---|---|---|
| 1 | SkyyRebirth own jar now, module after the merge? | "Yes (Recommended)" - own small jar now, module in the merged character mod at the SkyyCore merge |
| 2 | Which arms? | "+Alchemy, Smithing, Cooking (Recommended)" - 8 arms: Class, Mining, Foraging, Farming, Fishing, Alchemy, Smithing, Cooking |
| 3 | Acrobatics / Exploration reset? Pets? | "acrobatics yes, exploration, no." Pets: "Pets keep levels (Recommended)" |
| 4 | Dust tree nodes kept? | "no, instead, make rebirths give a dust multiplier. first rebirth gives 2x all dust. then they can be upgraded in the tree" - nodes reset, no refund |
| 5 | Class path picks? | "remember and come back" - re-enabled in purchase order as AP return |
| 5b | Ability levels + modifiers? | kept; soft cap while the class level returns - "more powerful than they would be on the first playthrough, but not full level"; "yes on the ability level cap"; "each rebirth like 1 modifier fore each ability gets a new cap"; "every 5th rebirth you get another modifier slot" |
| 6 | Quests? | "Stay done (Recommended)" |
| 7 | Bank bonus? | "Purse + bank, small cap (Recommended)" - 3.3 |
| 8 | Purse after? | "0 coins (Recommended)" |
| 9 | Safety checks? | "all three. can auto close all if you click continue." |
| 10 | Stat boost? | "+3% per rebirth, cap +30% (Recommended)" |
| 11 | Points formula? | "recommended curve. (tracks xp gained past max lvl, for bonus points.)" - 3.5 |
| 12 | Cap rise? | "+10 levels, +1 rank (Recommended)" |
| 13 | Max rebirths? | "10 (Recommended)" (raise later) |
| 14 | Titles / cosmetics? | "Title each, cosmetic every 3rd (Recommended)" |
| 15 | Bazaar dodge? | "Allow it (Recommended)" |
| 16 | Scope? | "Per profile (Recommended)" |

### 7.2 Still undecided (small; the default is what gets built unless Skyy says otherwise)

| # | Question | Default |
|---|---|---|
| U1 | Soft-cap formula (3.2): start at half the saved level, straight line back to full at the old class level? | yes |
| U2 | Max ability level +1 per rebirth (15 -> 25)? Each level above 15 also gives 1 modifier point? | yes / yes |
| U3 | Which modifier gets the +1 max: player picks one per ability each rebirth (vs a fixed one)? | player picks |
| U4 | Dust node per skill arm, 4 levels x +0.25 (2x -> 4x)? | yes |
| U5 | Exploration tree nodes: kept (its XP + Dust stay, so a reset would only be a free respec)? | kept |
| U6 | Skill level coin payouts after a rebirth: paid again, or only past the old highest level (today's "paid marker")? | only past the old highest |
| U7 | The +1 max level for 1 modifier: does the Class arm also sell more? | no - only the per-rebirth pick |

## For the local session (UNVERIFIED - needs the code or the game)

- Whether SkyySkills counts / stores XP past max level; the real class + skill caps today (`C0`, 100?) and XP to cap.
- Whether `skill:bonus` can carry the +3 % stat lines (source `rebirth`).
- SkyyTrees: does it store class picks in purchase order? If not, R5 adds `cls.order` (seed it from today's owned list).
- SkyyClasses: ability levels / modifier points are engine E6 (not built); whether the rune bar can show a 3rd / 4th modifier slot.
- SkyyBazaar / SkyyAuctions: where a cancel returns items + coins (claim stash vs inventory); whether a listing with bids can be pulled.
- Lifelong tools are not built; the "item is a view of its document" refresh must exist before R7.
- SkyyProfiles: refuse a switch while `rebirth:busy:<uuid>` is set.
- Fix `research/Gathering-Shards-Spec.md` section 3.3 to G6 (level 1, points removed) - outside `research/cloud/`.
- Page probes in `research/cloud/rebirth-page-1013/Rebirth-Page-Spec.md`; bank bonus vs `research/cloud/Bank-Tab-Calibration.md`.
