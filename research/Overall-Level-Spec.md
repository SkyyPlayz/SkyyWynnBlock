# Base Mana + Overall Level: engine research + SkyySkills 0.4.6 spec

*Written 2026-09-25. Read-only research: only this file was written. Scratch helpers lived under `tools/dev/scratch/r8-overall/`
(TEMP/TMP pointed there, JVM started with `-XX:-UsePerfData`) and were deleted afterwards. No build script, jar, doc or game file was
touched. Skyy uses they/them.*

*Skyy's answers (2026-09-25, `SkyWynn-Decisions.md` change notes 2026-09-25 #7 (b) and (c)): **Base Mana 10 for every player; magic
users (Mage, Priest) start at 20** (their base IS 20, not 10 + 20). **Overall Level = the average of all your skills; every Overall
Level gives a small amount of Health and Mana** (placeholder numbers, editable in Server Setup). This closes `OPEN-QUESTIONS.md`
"Mana" and the "amount per level" of Decisions rows 6.4 / 6.11 only as PLACEHOLDERS; Skyy still owns the real numbers.*

*Inputs: HANDOFF sections 1-3 (LIVE set = `tools/deploy_set.py` SET: SkyySkills 0.4.5, SkyyAccessories 0.4.4, SkyyClasses 0.1.6,
SkyyProfiles 0.1.2, SkyyGuilds 0.1.3, SkyyMenu 0.3.2), `tools/CONFIG-CONTRACT.md` (kit 1.1), `tools/PROFILES-CONTRACT.md`,
`research/Settings-Spec.md`, `research/Classes-Berserker-Priest-Spec.md`, `SkyySkills/build_skyyskills_0.4.5.py` +
`tools/skills_0_4_5_patch.py` (read only), `SkyyAccessories/build_skyyaccessories_0.4.4.py`, `SkyyClasses/build_skyyclasses_0.1.6.py`,
`SkyyGuilds/build_skyyguilds_0.1.3.py`, `SkyyMenu/build_skyymenu_0.3.2.py`, and my own checks against the release `HytaleServer.jar`
and `Assets.zip` (read in memory, never extracted). SkyyGear, SkyyAuctions, SkyyMenu and SkyyRolls are not touched by this spec.*

**VERIFIED** = seen directly in bytecode, asset JSON or our own source. **INFERRED** = strongly implied, not read literally.
**UNTESTED** = not seen in game yet (section 5 checks it). **[SKYY?]** = a choice made for Skyy, with its default.

---

## 0. Verdict (plain words)

**Both features fit in SkyySkills 0.4.6 with no new engine risk.** SkyySkills already puts three MAX modifiers on every player once a
second (`skyyskill_health / _stamina / _mana`, the per-skill perks) from `Perks.tick` on the world thread. 0.4.6 adds three more, each
with its OWN key, computed from scratch every second from the ACTIVE profile:

| Key (new) | Stat | Amount |
|---|---|---|
| `skyyskill_basemana` | Mana | 10, or 20 when the active profile's class is a magic user (Mage, Priest) |
| `skyyskill_overallhp` | Health | Overall Level x 0.5 (placeholder) |
| `skyyskill_overallmana` | Mana | Overall Level x 0.2 (placeholder) |

- **Overall Level** = floor(average level of the skills this profile can level): Mining, Foraging, Farming, Acrobatics, Alchemy,
  Smithing, Cooking, Exploration + **the profile's own class weapon skill** (9 skills). Other classes' skills never count. Shown with
  one decimal, rounded DOWN (e.g. "Overall Level 10 - average 10.2 of 9 skills").
- Shown on the **/skills header**, a new **Overall page** (button on /skills, and `/skills stats overall`), and published on the bridge
  as `skill:overall:<uuid>` (Integer) + `skill:fn:overall` (details). SkyyHud gets only the bridge key now.
- A chat line **"OVERALL LEVEL UP 10 -> 11 +0.5 max Health +0.2 max Mana"** when a skill level-up raises it, behind a new player
  switch `skills.overallUp` (default on) and an admin master switch.
- **Vanilla mana regen works** once max Mana is above 0: +1 Mana every 0.2 s (5 per second) while alive, not charging an attack, and
  only after 6 s without taking damage. 0 -> 10 takes 2 s, 0 -> 20 takes 4 s. Respawn refills Mana to max.
- **Flag for Skyy (important):** at base 20 a fresh Priest or Mage still cannot cast. The Wood Wand cast costs 25 Mana, the Wood
  Staff summon 50 and a spellbook cast 100 (VERIFIED in `Assets.zip`). A Priest reaches 25 only with +5 from somewhere else (Overall
  Level 25, Alchemy 25, one piece of Silk cloth armor, ...). See open question Q1.
- SkyyAccessories' Intelligence talisman (a percent of your flat max Mana) finally does something: its "flat" already sums every
  other ADDITIVE MAX modifier, so it picks up the new keys with no SkyyAccessories change.

---

## 1. Engine facts (all VERIFIED unless marked)

### 1.1 Stat modifiers (`HytaleServer.jar` bytecode, reflection)

| Fact | Evidence |
|---|---|
| `EntityStatMap.get(int) -> EntityStatValue`, `getModifier(int, String) -> Modifier`, `putModifier(int, String, Modifier) -> Modifier`, `removeModifier(int, String) -> Modifier`, `addStatValue(int, float) -> float`, static `getComponentType()` | reflection |
| `putModifier` / `removeModifier` log WARNING "No EntityStatValue found for index: %d" and do nothing when the stat is missing | bytecode (so we keep SkyySkills' `if (m.get(idx) == null) return;` guard) |
| `EntityStatValue.putModifier(key, mod)` = `modifiers.put(key, mod)` (one entry per key, a second put REPLACES) then `computeModifiers(type)` | bytecode |
| `computeModifiers`: max = `EntityStatType.getMax()`; + SUM of every ADDITIVE MAX amount; then x SUM of every MULTIPLICATIVE MAX amount; then **`value = clamp(value, min, max)`** | bytecode. So raising max never raises the current value; lowering max clamps the current value down |
| `EntityStatValue.get()`, `getMax()`, `getModifiers()` | reflection |
| `StaticModifier(ModifierTarget, CalculationType, float)` public; `getAmount()`, `getCalculationType()`, `getTarget()`, `equals()` | reflection |
| `Modifier$ModifierTarget` = {MIN, MAX}; `StaticModifier$CalculationType` = {ADDITIVE, MULTIPLICATIVE} | enum constants |
| `DefaultEntityStatTypes.getMana()`, `getHealth()` (static int) | reflection |
| `EntityStatType.getAssetMap()` (IndexedLookupTableAssetMap, `getAsset(int)`), `getMax()`, `getInitialValue()`, `getResetBehavior()` | reflection + computeModifiers bytecode |
| **Modifiers are SAVED with the player**: `EntityStatValue.CODEC` has fields `Id`, `Value`, `Modifiers` (MapCodec, getter + setter) | `<clinit>` bytecode |
| The engine only adds / removes its OWN keys: `StatModifiersManager.applyStatModifiers` / `applyEffectModifiers` use `CalculationType.createKey("Armor")` / `createKey("Effect")`, plus `*Weapon_` / `*Utility_` (`DefaultModifiers`) | bytecode + constant pool. A `skyyskill_*` key is never touched by the engine |
| Respawn: `RespawnSystems$ResetStatsRespawnSystem.onComponentRemoved(DeathComponent)` calls `resetStatValue(i)` for every stat; `resetStatValue` sets `InitialValue` or `getMax()` by `EntityStatResetBehavior` {InitialValue, MaxValue} | bytecode |
| `DeathComponent.getComponentType()` static | reflection |

### 1.2 Vanilla Mana (`Assets.zip`: `Server/Entity/Stats/Mana.json`) and how it regenerates

```
"InitialValue": 0, "Min": 0, "Max": 0, "Shared": false, "ResetType": "MaxValue",
"Regenerating": [ { "Interval": 0.2, "Amount": 1, "RegenType": "Additive",
                    "Conditions": [ {"Id": "Alive"}, {"Id": "NoDamageTaken", "Delay": 6}, {"Id": "Charging", "Inverse": true} ] } ]
```

- **Regen exists and is not scaled by max** (Additive): +1 Mana per 0.2 s = **5 Mana per second**. `RegeneratingValue.regenerate`
  counts down the interval, then checks every condition (`Condition.allConditionsMet`), then clamps (`Regenerating.clampAmount`).
- **Conditions** (bytecode): `NoDamageTakenCondition` compares `DamageDataComponent.getLastDamageTime()` with the 6 s delay (every hit
  you take pauses regen for 6 s). `ChargingCondition` (inverted) is true while any interaction is charging
  (`InteractionManager.forEachInteraction`) or shortly after `getLastChargeTime()`: holding a wand / staff / bow charge pauses regen.
- **0 -> 10: 2.0 s; 0 -> 20: 4.0 s** (plus the 6 s no-damage wait after a hit). Bigger pools refill proportionally slower (60 Mana =
  12 s). Today regen never shows because max is 0 (`clamp(value, 0, 0)`).
- **Raising max does not fill the bar** (1.1 clamp): the first time 0.4.6 runs, every player sits at 0 / 10 and fills up in 2 s.
- **Respawn** refills Mana to max (`ResetType: MaxValue`). Health.json is also MaxValue.
- **Where else Mana comes from in vanilla:** cloth armor adds max Mana as an ADDITIVE armor modifier: Silk 10-22 per piece (60 a set),
  Cindercloth head/hands/legs 20/16/28, Onyxium 13-29 (80 a set), Prisma 16-36 (100 a set). The `Effects/Mana/*` effects (Mana 12,
  Mana_High 25, regen ticks) exist but no vanilla item applies them (scan of `Server/Item/**`).
- **What casts cost** (`Server/Item/Items/Weapon/*`, `InteractionVars` `Costs`): wands (Wood, Tribal, Wood_Rotten) **25**, every staff
  summon **50**, spellbooks **100**, Blunderbuss 50. A cast is refused (StatsCondition) while current Mana is below the cost.
- **Client (UNTESTED):** the vanilla client has a Mana HUD bar (`Client/Data/Game/Interface/InGame/Hud/Mana/Mana.ui`) and a Mana line in
  the character panel. INFERRED: the bar is hidden at max 0 and appears once max > 0, so after 0.4.6 **every player sees a Mana bar**
  (base 10 for everyone is exactly Skyy's call). Test 5.3 step 1 checks it.

### 1.3 Health reminder

Players have **no survival Health regen** (`Health.json` regenerates NPCs and creative players only). So a bigger max Health from an
Overall level up leaves the player at, say, 100 / 100.5 until they eat or heal. 2.7 adds a one-time top-up for real level ups.

---

## 2. Design

### 2.1 Base Mana (per player, per profile)

- **Class source** (`Overall.classOf(u)`): `profile:class:<uuid>` when present and non-empty (SkyyProfiles, AUTHORITATIVE per the
  profile contract, flips in the same publish as the epoch), else `class:<uuid>` (SkyyClasses, `SkillClass.className`), else none.
  `profile:class` first on purpose: `class:<uuid>` can lag a second behind a switch, and a lag must never show the old class's Mana.
- **Magic user** = the class name (any case) is in `mana.magicClasses` (default `Mage,Priest`). Unknown or no class = not magic.
- **Target** = `mana.magicBase` (20) for a magic user, else `mana.base` (10); 0 when the part `mana.base.enabled` is off.
- **Amount posted** = `target - EntityStatType(Mana).getMax()`, never below 0, rounded to 2 decimals. With vanilla's type max 0 this is
  exactly 10 / 20. If a future Hytale gives players a base of its own, "base Mana 10" still means a TOTAL base of 10 instead of
  stacking on top. **[SKYY?] Q11** (default: total base).
- Posted as `StaticModifier(MAX, ADDITIVE, amount)` under **`skyyskill_basemana`**, via the existing `Perks.mod` (writes only when the
  value changed; amount 0 removes the key).
- Per profile automatically: the class is the ACTIVE profile's class, re-read every second. Warrior profile -> 10; switch to the Priest
  profile -> 20 within a second; `/profileadmin setclass` -> within a second.

### 2.2 Overall Level: exactly which skills count

**Default list (`overall.skills`):** `Mining,Foraging,Farming,Acrobatics,Alchemy,Smithing,Cooking,Exploration,Class`

| Slot | Skill | Counts? | Why |
|---|---|---|---|
| 0, 1, 2 | Mining, Foraging, Farming | yes | levelable by every profile |
| 4 | Acrobatics | yes | levelable by every profile |
| 10, 11, 12 | Alchemy, Smithing, Cooking | yes | levelable by every profile (Cooking XP comes from SkyyCooking, in the pack) |
| 13 | Exploration | yes | levelable by every profile (XP from SkyyExploration, in the pack) |
| `Class` | the ACTIVE profile's own class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity; Assassination / Shaman skill when those classes exist) | yes, exactly one | it is this profile's combat skill |
| other class slots (5-9, 14, 15 minus the own one) | the other classes' weapon skills | **never** | a profile's class is locked for life ("a new class is a new profile"), so they are 0 by design. Counting their 0s would cap everyone's average at 9/15 of their real progress. Counting non-zero leftovers (pre-profile files from the 0.1.1 paid class switch) would reward a class the player cannot play on this profile |
| 3 | legacy "Combat" (classless XP from 0.1/0.2) | **never** | no longer earned; `Perks.migrate` moves it into the class skill |

**The class row, precisely** (`Overall.sums`):
- Listed `Class` + SkyyClasses loaded (`SkillClass.allowedFn() != null`) + a class known to SkyySkills
  (`SkillClass.slotOfClass(classOf(u)) >= 0`) -> that slot's level, counted.
- SkyyClasses loaded but **no class yet** -> counts as **0** (9 skills). Otherwise a player could keep a higher Overall by never picking a
  class; with SkyyProfiles the class is picked at profile creation, so this only matters on servers without SkyyProfiles.
- **SkyyClasses not installed** -> the class row is **skipped** (8 skills): nobody can earn class XP there (`SkillClass.killSlot`
  refuses all combat XP without SkyyClasses), so it is not a skill anyone can level.
- A class name SkyySkills does not know (a future class added only in SkyyClasses) -> skipped, one WARN per class name per JVM.

**Why a config list and not "every skill that has a mod":** one predictable source of truth. A server without SkyyCooking or
SkyyExploration removes those entries in Server Setup. A skill whose SkyySkills part switch is off (e.g. `exploration.enabled=false`)
still counts until the owner removes it from the list: flipping a part for a moment must not shift everyone's Overall Level and max
Health. **[SKYY?] Q3 / Q4** (defaults as above).

### 2.3 Rounding

- `sum` = sum of the counted levels (`SkillDefs.levelOf(d[slot])`, so the `levels.max` cap applies), `n` = number counted.
- **Overall Level** = `sum / n` in integer arithmetic = floor (0 when `n == 0`). Max = `SkillDefs.MAX` (100).
- **Shown average** = `(sum * 10) / n` tenths, also floored, printed `t / 10 + "." + t % 10`. Floored on purpose: 116 / 9 = 12.89 shows
  "12.8", never "12.9" or "13.0" while the Overall Level is still 12.
- Example (Priest): Mining 14, Foraging 9, Farming 12, Acrobatics 20, Alchemy 3, Smithing 5, Cooking 0, Exploration 11, Divinity 18
  -> sum 92, n 9 -> **Overall Level 10, "average 10.2"** -> +5 max Health, +2 max Mana.

### 2.4 Health and Mana per Overall Level (PLACEHOLDERS, flagged)

| Row | Default | At Overall 10 / 50 / 100 | Compare |
|---|---|---|---|
| `overall.healthPerLevel` | **0.5** | +5 / +25 / +50 max Health | vanilla 100; iron armor set +46; today's perks at all-100: Farming 25 + Foraging 10 + class 10 |
| `overall.manaPerLevel` | **0.2** | +2 / +10 / +20 max Mana | base 10 / 20; Alchemy perk 0.2 per level (20 at 100); Silk set +60 |

Same rate for magic users and everyone else **[SKYY?] Q12**. Amounts are rounded to 2 decimals. Both are Server Setup rows, `live`.

### 2.5 Modifier rules (no stacking, clean removal)

- **One key per stat and source** (table in section 0). `putModifier` replaces the value under that key, and the amount is computed
  from scratch every second (never incremented), so nothing can stack: not across ticks, not across profiles, not across relogs.
- **ADDITIVE only, never computed from the current max** (only from levels, class and config). So no feedback loop with the percent
  layers of other mods (2.x / 3.1).
- The existing perk keys `skyyskill_health / _stamina / _mana` keep their meaning and amounts. The new keys add on top (different
  sources: per-skill perks vs the Overall Level vs the class base).
- **Removal:** a part switched off, a base of 0, a per-level of 0 or Overall Level 0 -> amount 0 -> `Perks.mod` calls `removeModifier`.
  Online players lose it within a second; offline players on their first second online.
- **Persistence (1.1):** the engine saves modifiers with the player, so a player joins with last session's values already in place (no
  dip, no flicker). The flip side: **uninstalling SkyySkills or downgrading to 0.4.5 leaves the three keys on every player who played
  0.4.6** (0.4.5 does not know them). Procedure (goes in the manifest notes and 4.14): switch both parts off, let players log in, then
  downgrade. Same caveat SkyyAccessories and the 0.3 perks already have.

### 2.6 When it recomputes

| Trigger | Path | Delay |
|---|---|---|
| any second | `Perks.tick` (AcroSys, world thread, runs whether or not Acrobatics is on) -> new `Perks.ovl` | <= 1 s |
| skill level up | `SkillXp.gain4` -> `Overall.levelUp` (bridge key + chat line + pending heal now), modifiers at the next `Perks.tick` | chat now, stats <= 1 s |
| profile switch / creation | `Perks.switched` (epoch change, before `Perks.tick` of the same second) -> `Overall.forget`; `Perks.tick` recomputes from the new pkey | <= 1 s |
| class change (admin setclass, first pick) | `profile:class` / `class:` read every second | <= 1 s |
| Server Setup / hand edit / `/skills reload` | `SkillCfg.load` -> `OverallCfg.read`; next `Perks.tick` | <= 1 s |

`skill:overall:<uuid>` is compared and re-put in the same second when it differs, so config changes also reach the bridge.

### 2.7 Heal the added Health on a real level up (`overall.healOnLevelUp`, default on) [SKYY?] Q5

Without it, every Overall level up looks like damage (100 / 100 -> 100 / 100.5) because players have no Health regen. Rule:
- Only `SkillXp.gain4` records a heal (`Overall.addHeal(u, levelsGained)`): a real XP level up of a counted skill that raised the
  Overall Level. Config changes, `levels.max` changes, profile switches and logins never heal.
- The next `Perks.tick` puts the new `skyyskill_overallhp` FIRST, then `addStatValue(Health, levelsGained x healthPerLevel)` (the engine
  clamps to the new max). Skipped when the player is dead (`DeathComponent` present) or at 0 Health; a skipped heal is dropped, not kept.
- Cleared by `Perks.switched` (epoch change) and pruned by `Acro.retainOnline`.
- Mana is not topped up: it refills by itself (1.2).

### 2.8 Where it shows

1. **/skills header** (`SkillsPage.build`): the 18 px "Skill average X.Y - every level up pays coins" label (0.4.5, computed over the
   /skills rows) is replaced by a 28 px row: Label `#SkyySkOv` (490 wide, FontSize 14, bold, `#ffe08a`) = "Overall Level 10  -  average
   10.2 of 9 skills" + TextButton `#SkyySkOvStat` "Overall" (110 x 26) -> payload `skstatov`. Content height 646 -> 656 of the 670 the
   640 x 690 root allows. The footer line gets "- level ups pay coins" appended (the coin hint moves there). Header and bonus use the
   SAME `Overall.sums`, so the page never disagrees with the stats.
2. **Overall page** (new `OverallPage`, same 960 x 795 frame and 24 / 20 / 18 / 15 pt fonts as `StatsPage`, BIG readable): title
   "Overall Level 10 of 100", sub line "Average of your skills 10.2 - Overall Level 11 at an average of 11.0", a 600 px bar (tenths into
   the level), "Skills that count (9)" with one wrapped line "Mining 14 - Foraging 9 - ... - Divinity 18 (your class)", "Boosts right
   now" (+5 max Health (0.5 per Overall Level) / +2 max Mana (0.2 per Overall Level) / "Base Mana 20 - Priest is a magic user" or "Base
   Mana 10 (magic users - Mage, Priest - start at 20)" / the "... is off on this server" lines), "Overall Level 11 adds" (+0.5 max
   Health, +0.2 max Mana) or "Max Overall Level reached", a how-to line, and a "< Back" button (payload `ovback`) to /skills.
   Opened from the /skills button and by **`/skills stats overall`** (StatsCmd, before `argSlot`).
3. **Bridge** (4.8): `skill:overall:<uuid>` = Integer; `skill:fn:overall` = details; `skill:fn:level` also answers the name "Overall".
   **Not** added to `skill:<uuid>`: SkyyGuilds' fallback sums every entry of that string into guild XP, and SkyyMenu lists every entry
   in the profile tooltip.
4. **SkyyHud:** nothing now. A later SkyyHud widget reads `skill:overall:<uuid>` (Integer) on its existing refresh (no periodic UI
   rule change: the HUD already refreshes its widgets).
5. Chat line (2.9).

### 2.9 Chat line and the player switch

- Text (one line per gain4 call that raised it, `#ffe08a`): `OVERALL LEVEL UP  10 -> 11   +0.5 max Health  +0.2 max Mana`. Several
  levels at once (admin `/skills xp`): `10 -> 12   +1 max Health  +0.4 max Mana`. With `overall.enabled` off or both rates 0 the bonus
  part is left out. Printed right after the SKILL LEVEL UP lines and their "next:" line.
- Sent only if `overall.chat` (admin master, default true) AND `SkillStore.notifyOn(u, "skills.overallUp")` (Settings-Spec 1.3 rule:
  gate only the send; the bridge key, the pending heal and the stats happen either way).
- New registered setting: `skills.overallUp`, label **"Overall Level ups"**, category `skills`, default ON, help **"OVERALL LEVEL UP 12
  -> 13 with the max Health and Mana it added"**. With SkyyMenu 0.3.2 it is the 8th key of the Skills tab (5 SkyySkills keys + the 2
  SkyyExploration 0.2.1 keys; a key missing from `SET_ORDER` ranks last), and 0.3.2 shows 8 rows per tab page (`SET_ROWS = 8`), so it
  still fits page 1 as the last row. No SkyyMenu change needed; a later SkyyMenu may add it to `SET_ORDER` after `skills.levelUp`.

### 2.10 Profile switch, relog, death, world change

- **Switch to a weaker profile:** max Health / Mana drop, current values clamp down (1.1). Switching back does NOT give them back (no
  free heal, no exploit). The 0.3 perks already behave this way. **[SKYY?] Q13**.
- **Relog:** saved modifiers are there at join; the first tick only confirms them.
- **Death:** respawn refills Health and Mana to the (modified) max. A heal pending at death is dropped.
- **World change** (PlayerReady fires again): nothing special; stats live on the player entity, the tick continues.
- **Momentary class lag after a switch:** avoided by reading `profile:class` first (2.1). Without SkyyProfiles `class:<uuid>` is the
  only source and there is no switch.

### 2.11 Known limits (documented, not bugs)

- An unreadable player file loads as zeros (existing SkyySkills follow-up) -> the Overall bonus drops for that session (clamp).
- Uninstall / downgrade leaves the saved keys (2.5).
- The first 0.4.6 second shows 100 / 105 Health for a player with Overall 10 (no heal on first sight, like the 0.3 perks).
- Up to 1 s between a level up and the new max; up to 1 s for SkyyAccessories' percent layer to follow (its own 1 s tick).

---

## 3. Interactions

### 3.1 SkyyAccessories 0.4.4 talismans (no change needed there)

`AccEffects.flatMax` = `EntityStatType.getMax()` + every OTHER ADDITIVE MAX modifier (skips only its own key), then posts
`round(flat x pct) / 100` under `skyyacc_mana / _health / _stamina` (VERIFIED in the 0.4.4 source). So:
- **Intelligence** (2 / 4 / 6 / 8 / 10 %) now has a base: the Priest example (base 20 + Overall 2 + Alchemy 0.6 = 22.6) with a
  Legendary talisman gets +2.26 -> 24.86 max Mana. Still under the wand's 25 (Q1). Common 2 % of a Warrior's 10 = +0.2: still tiny early.
  HANDOFF open decision 2 ("% of vanilla base Mana 0 is useless - make them flat?") becomes "small, but not zero" **[SKYY?] Q14**.
- **Vitality** now includes the Overall Health in its flat.
- Keys never collide (`skyyacc_*` vs `skyyskill_*`). No loop: our amounts never read max.

### 3.2 SkyyGear (being built now; untouched)

- SkyyGear adds its own MAX Health / Mana modifiers under its own keys. Ours all start with `skyyskill_` (build-asserted, 4.12); any
  key SkyyGear picks outside that prefix cannot collide. ADDITIVE amounts simply add up.
- Advice for SkyyGear, not a change here: if it adds a PERCENT Health / Mana stat, compute it as ADDITIVE from a flat that EXCLUDES
  other mods' percent keys (`skyyacc_*`), the SkyyAccessories 0.4 pattern. Engine MULTIPLICATIVE amounts are SUMMED into one factor
  (1.1), and two percent layers that each count the other as flat drift for several seconds before settling.
- The gear level gate (Decisions change note 6) reads skill levels by name; `skill:fn:level` with "Overall" (4.8) is ready if gear ever
  gates on the Overall Level.

### 3.3 SkyyGuilds 0.1.3

Guild XP sums `skill:fn:xp` over its configured skill names; the Overall Level creates no XP, so nothing is counted twice. Its
fallback parses `skill:<uuid>` and sums EVERY level in it, which is why "Overall" is never added to that string. An admin typing
"Overall" into the guild's skill list gets 0 (unknown name). A future guild feature (member list, join requirement) can read
`skill:overall:<uuid>`.

### 3.4 SkyyClasses 0.1.6 (Priest heal, weapons)

No change. The placeholder Priest heal is HP-based and unaffected. Magic-user Mana makes the wand's cast reachable sooner (Q1).

### 3.5 SkyyProfiles 0.1.2

Per the contract: per-player bridge keys stay UUID-keyed and describe the active profile (`skill:overall:<uuid>`); live effects are
recomputed after an epoch change (2.6); nothing new is stored, so there is no per-profile file change.

### 3.6 SkyyParty / SkyyHud party widget, SkyyMenu

The party widget's Mana column (`party:stats`) starts showing real values (10 / 20 / more). SkyyMenu's profile tooltip is unchanged.

### 3.7 SkyyExploration / SkyyTrees / SkyyCooking

Unaffected (they read `skill:fn:level`, `skill:fn:xp`, `skill:<uuid>` and the Exploration stamina row, all unchanged).

---

## 4. SkyySkills 0.4.6 build (patch on 0.4.5)

### 4.1 Files, version, anchors

- New `tools/skills_0_4_6_patch.py` (the `skills_0_4_5_patch.py` style: `rep(old, new)` with asserted single anchors, newline-agnostic)
  derives `SkyySkills/build_skyyskills_0.4.6.py` from 0.4.5. Edit the patch, never the generated script. 0.4.5 stays untouched.
- Run: `python tools/skills_0_4_6_patch.py` then `python SkyySkills/build_skyyskills_0.4.6.py` (must end `assembled ...jar`), then
  `python tools/ci/lint.py` (0 fails). NO `--deploy`; `tools/deploy_set.py --check` only; pinning is the coordinator's job.
- **Saved data:** nothing new in `players/<pkey>.properties`; one block appended once to `xp.properties`. 0.4.5 <-> 0.4.6 is safe both
  ways for files; for the saved stat keys see 2.5.
- Anchors (each must occur exactly once in 0.4.5, asserted like 0.4.5's list):
  1. the docstring header (`"""SkyySkills 0.4.5 - build script ...`) and `VERSION = "0.4.5"`;
  2. `xss  = pool.makeClass(PKG + ".XbowSlotSys", pool.get(EES))` -> after it: `ovc = OverallCfg`, `ovl = Overall`, `ofn = OverallFn`
     (plain class, `java.util.function.Function`), `opg = OverallPage` (`pool.get(PAGE)`);
  3. `XBOW_LIT = json.dumps(XBOW_DEFAULTS)` -> the `OVL_L` block after it (4.2);
  4. `# ================= BridgeCfg (0.4): bridge.* keys` -> the OverallCfg section right before it (4.3), i.e. after the XbowCfg
     section. `SkillCfg.load` (its caller) is compiled later in the script (0.4.5: after the BridgeCfg methods), and the helpers
     OverallCfg uses (`SkillCfg.bool / dbl / warn / info`, `SkillDefs`) are compiled earlier, so the order is javassist-safe;
  5. `{PKG}.XbowCfg.ensureDefaults(p);` -> `+ {PKG}.OverallCfg.ensureDefaults(p);`, `{PKG}.XbowCfg.read(p);` -> `+
     {PKG}.OverallCfg.read(p);`, and the load summary `", crossbows stay loaded " + {PKG}.XbowCfg.text()` -> `+ ", overall level " +
     {PKG}.OverallCfg.text()`;
  6. `# ================= SkillFn: bridge skill:fn:level =================` -> the Overall section BEFORE it (4.4: after SkillStore and
     SkillClass, before SkillFn / SkillXp / Perks / pages, which all call it);
  7. SkillFn.apply: before `int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));` the "Overall" alias (4.8);
  8. SkillXp.gain4: after the `if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " ...` line and before
     `{PKG}.SkillStore.publish(u);` -> `{PKG}.Overall.levelUp(pr, u, skill, r[0], r[1]);`;
  9. Perks: new field `OVL_FAILED_ONCE`, new method `ovl` added right before `public static void tick(`; in `tick`, after
     `mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));` -> `ovl(u, cb, ref, m);` (4.5);
 10. Perks.switched: after `{PKG}.Xbow.refresh(u);` -> `{PKG}.Overall.forget(u);`;
 11. Acro.retainOnline: after `{PKG}.Xbow.retain(online);` -> `{PKG}.Overall.retain(online);`;
 12. SkillsPage.build: the `int sum = 0; ... long avg10 = ...` lines and the "Skill average" label -> 4.7 (keep `cs` and `rows`); the
     footer label text;
 13. before `page.addMethod(CtNewMethod.make(f"""\npublic void handleDataEvent(` (SkillsPage) -> the OverallPage section (after
     StatsPage, so SkillsPage.handleDataEvent can construct it);
 14. SkillsPage.handleDataEvent: before the `skstat` loop -> the `skstatov` branch;
 15. StatsCmd.execute: before `int s = {PKG}.SkillClass.argSlot(...)` -> the `overall` branch;
 16. `CFG_CATS`, the parts rows (after the `perk.archery.keepLoaded.enabled` row), the new `overall` rows, `assert len(CFG_ROWS) == 159`
     -> 169, the per-key asserts (4.9);
 17. `setup()`: after `put("skill:fn:healxp", ...)` -> `put("skill:fn:overall", new {PKG}.OverallFn())`; after the `rewards.late`
     regSetting -> the `skills.overallUp` regSetting; the ready line; `shutdown()`: remove `skill:fn:overall`;
 18. the `writeFile` tuple (`..., xcf, xst, xbw, xss):`) -> `+ ovc, ovl, ofn, opg`; the manifest description;
 19. the API probe list and the new build checks (4.12).

javassist rules throughout: no lambdas, generics, varargs, autoboxing, enhanced-for, inner classes, String switch,
try-with-resources; methods before callers (also inside one class); f-string braces doubled in the patch (the Java below is shown
with single braces); a synchronized block holds one call.

### 4.2 `xp.properties` block (ASCII, no double quotes; in a fresh file; appended ONCE to a file without `overall.enabled`)

```
# ---------- Overall Level + base Mana (SkyySkills 0.4.6) - research/Overall-Level-Spec.md ----------
# Comments must stay on their own lines.
# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase
# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after
# 6 s without taking damage).
mana.base.enabled=true
mana.base=10
mana.magicBase=20
mana.magicClasses=Mage,Priest
# Overall Level = the average level of the listed skills, rounded down. Class = the profile's own class skill (other classes' skills
# never count). Each Overall Level adds healthPerLevel max Health and manaPerLevel max Mana (PLACEHOLDER numbers).
overall.enabled=true
overall.skills=Mining,Foraging,Farming,Acrobatics,Alchemy,Smithing,Cooking,Exploration,Class
overall.healthPerLevel=0.5
overall.manaPerLevel=0.2
# healOnLevelUp=true: an Overall level up also heals the max Health it added (players have no Health regen)
overall.healOnLevelUp=true
# chat=false: nobody gets the OVERALL LEVEL UP line (players can also hide it for themselves in /settings)
overall.chat=true
```

Python: `OVL_L` list, `L.append(""); L.extend(OVL_L)`, `OVL_DEFAULTS`, `assert all(ord(ch) < 128 ...) and '"' not in OVL_DEFAULTS`,
`OVL_LIT = json.dumps(OVL_DEFAULTS)`, `OVL_SKILLS_DEF = "Mining,Foraging,Farming,Acrobatics,Alchemy,Smithing,Cooking,Exploration,Class"`.

### 4.3 `OverallCfg` (new class, the `DivCfg` / `XbowCfg` pattern)

Fields (`public static volatile`, set only by `read`): `MANA_ON = true`, `BASE = 10.0`, `MAGIC_BASE = 20.0`, `String[] MAGIC = {
"Mage", "Priest" }`, `MAGIC_TEXT = "Mage,Priest"`, `ON = true`, `int[] SLOTS = { 0, 1, 2, 4, 10, 11, 12, 13 }`, `CLASS = true`,
`HP = 0.5`, `MANA = 0.2`, `HEAL = true`, `CHAT = true`; `public static final String DEFAULTS = OVL_LIT` (the DivCfg field name).

Methods (in this order):
- `ensureDefaults(java.util.Properties p)`: exactly the `DivCfg.ensureDefaults` code with the marker `overall.enabled`: when absent,
  append `"\n" + DEFAULTS` to `SkillCfg.FILE` (APPEND) and log "xp.properties: appended the Overall Level + base Mana section". It does
  not touch `p`; this one load then runs on the code defaults, which are the same numbers as the block.
- `static Object[] parseSkills(String v)` -> `{ int[] slots, Boolean cls }` or `null`. Split on `,`, trim, skip empty. `class` (any
  case) -> cls. Else an EXACT match (no prefix) of `SkillDefs.LABELS[i]` or `NAMES[i]` with `i` in {0, 1, 2, 4, 10, 11, 12, 13};
  anything else, a duplicate, or an empty list -> `null`.
- `static String[] parseClasses(String v)` -> names matched (any case) against `SkillDefs.CLASSES`, stored with the CLASSES spelling,
  duplicates dropped; unknown names dropped (the loader warns, the hook refuses). Empty text -> empty array (nobody is a magic user).
- `public static String checkSkills(String key, String value)` (check= hook): `null` when `parseSkills` accepts; else "Use a comma list
  of Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration and Class (the profile's own class skill), each
  once." A class skill name (Archery, Fury, ...) gets "Use Class - it means the profile's own class skill; other classes never count."
- `public static String checkClasses(String key, String value)`: every name must be one of `SkillDefs.CLASSES` -> else "Unknown class
  <name> - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman." Empty is fine.
- `read(java.util.Properties p)` (inside `SkillCfg.load`, after `XbowCfg.read`): bools via `SkillCfg.bool`, decimals via `SkillCfg.dbl`
  clamped to the row bounds (base / magicBase 0-10000, per-level 0-100, NaN -> default); `overall.skills` through `parseSkills`
  (invalid -> defaults + WARN); `mana.magicClasses` through `parseClasses`.
- `text()` -> e.g. `"on (9 skills, +0.5 health / +0.2 mana per level), base mana 10 / 20 for Mage,Priest"`.

### 4.4 `Overall` (new class; no locks except its own short synchronized methods; pure parts safe on any thread)

```java
public static final java.util.concurrent.ConcurrentHashMap HEAL = new java.util.concurrent.ConcurrentHashMap();   // UUID -> Integer levels to heal
public static final java.util.concurrent.ConcurrentHashMap BADCLS = new java.util.concurrent.ConcurrentHashMap(); // class names warned once
public static float round2(double v) { return (float) (Math.round(v * 100.0) / 100.0); }
public static String num(double v)   // copy of StatsPage.num (StatsPage is compiled later): 0.5 -> "0.5", 10.0 -> "10"
public static String classOf(java.util.UUID u) {
  try {
    Object o = {PKG}.SkillStore.bridge().get("profile:class:" + u.toString());
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  } catch (Throwable t) { }
  return {PKG}.SkillClass.className(u);
}
public static boolean magic(java.util.UUID u) {
  String c = classOf(u);
  if (c == null) return false;
  String[] m = {PKG}.OverallCfg.MAGIC;
  for (int i = 0; i < m.length; i++) if (m[i].equalsIgnoreCase(c)) return true;
  return false;
}
public static float typeMax(int idx) {
  try {
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset(idx);
    if (t != null) return t.getMax();
  } catch (Throwable e) { }
  return 0.0f;
}
public static float baseTarget(java.util.UUID u) {
  if (!{PKG}.OverallCfg.MANA_ON) return 0.0f;
  return round2(magic(u) ? {PKG}.OverallCfg.MAGIC_BASE : {PKG}.OverallCfg.BASE);
}
public static float baseMana(java.util.UUID u, float tmax) {
  float a = baseTarget(u) - tmax;
  return a > 0.0f ? round2(a) : 0.0f;
}
public static boolean classesOn() { return {PKG}.SkillClass.allowedFn() != null; }
// {sum, n}; see 2.2 for the class row
public static int[] sums(java.util.UUID u, long[] d) {
  int sum = 0;
  int n = 0;
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) {
    int s = sl[i];
    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += {PKG}.SkillDefs.levelOf(d[s]);
    n++;
  }
  if ({PKG}.OverallCfg.CLASS && classesOn()) {
    String c = classOf(u);
    if (c == null) n++;
    else {
      int cs = {PKG}.SkillClass.slotOfClass(c);
      if (cs >= 0) { sum += {PKG}.SkillDefs.levelOf(d[cs]); n++; }
      else if (BADCLS.putIfAbsent(c.toLowerCase(), Boolean.TRUE) == null) {PKG}.SkillCfg.warn("class " + c + " has no class skill in SkyySkills - it is left out of the Overall Level");
    }
  }
  return new int[] { sum, n };
}
public static int level(int[] sc)  { return sc[1] <= 0 ? 0 : sc[0] / sc[1]; }
public static int tenths(int[] sc) { return sc[1] <= 0 ? 0 : (int) (((long) sc[0] * 10L) / (long) sc[1]); }
public static String avg(int t)    { return (t / 10) + "." + (t % 10); }
public static float hp(int lv)   { return !{PKG}.OverallCfg.ON || lv <= 0 ? 0.0f : round2(lv * {PKG}.OverallCfg.HP); }
public static float mana(int lv) { return !{PKG}.OverallCfg.ON || lv <= 0 ? 0.0f : round2(lv * {PKG}.OverallCfg.MANA); }
public static int levelOf(java.util.UUID u) { return level(sums(u, {PKG}.SkillStore.data(u))); }
// does XP in this slot move the Overall Level?
public static boolean counts(java.util.UUID u, int skill) {
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) if (sl[i] == skill) return true;
  return {PKG}.OverallCfg.CLASS && classesOn() && skill >= 0 && skill == {PKG}.SkillClass.slotOfClass(classOf(u));
}
// skill:overall:<uuid> = Integer, re-put only when it differs
public static void publish(java.util.UUID u, int lv) {
  try {
    java.util.Map br = {PKG}.SkillStore.bridge();
    String k = "skill:overall:" + u.toString();
    Object o = br.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != lv) br.put(k, Integer.valueOf(lv));
  } catch (Throwable t) { }
}
public static synchronized void addHeal(java.util.UUID u, int n) {
  if (n <= 0) return;
  Integer c = (Integer) HEAL.get(u);
  HEAL.put(u, Integer.valueOf((c == null ? 0 : c.intValue()) + n));
}
public static synchronized int takeHeal(java.util.UUID u) {
  Integer c = (Integer) HEAL.remove(u);
  return c == null ? 0 : c.intValue();
}
public static void forget(java.util.UUID u) { HEAL.remove(u); }
public static void retain(java.util.Set online) { HEAL.keySet().retainAll(online); }
// world thread, SkillXp.gain4 after the SKILL LEVEL UP lines (r = the level before / after this award)
public static void levelUp({PR} pr, java.util.UUID u, int skill, long oldLv, long newLv) {
  try {
    if (newLv <= oldLv || !counts(u, skill)) return;
    int[] sc = sums(u, {PKG}.SkillStore.data(u));
    int after = level(sc);
    int before = sc[1] <= 0 ? 0 : (sc[0] - (int) (newLv - oldLv)) / sc[1];
    publish(u, after);
    if (after <= before) return;
    addHeal(u, after - before);
    if (!{PKG}.OverallCfg.CHAT || !{PKG}.SkillStore.notifyOn(u, "skills.overallUp")) return;
    int g = after - before;
    String bonus = "";
    float h = hp(g);
    float m = mana(g);
    if (h > 0.0f) bonus = bonus + "  +" + num(h) + " max Health";
    if (m > 0.0f) bonus = bonus + "  +" + num(m) + " max Mana";
    pr.sendMessage({MSG}.raw("OVERALL LEVEL UP  " + before + " -> " + after + (bonus.length() > 0 ? " " + bonus : "")).color("#ffe08a"));
  } catch (Throwable t) { {PKG}.SkillCfg.warn("overall level up failed: " + t); }
}
// Overall page helpers: listText(u, d) = "Mining 14 - Foraging 9 - ... - Divinity 18 (your class)" (class row "Class skill 0 -
// choose a class with /class" when counted as 0; SkillClass.skillName for the class label); nowLines(u, lv) / nextLines(lv) =
// java.util.ArrayList of String (the texts in 2.8)
```

(`hp(g)` / `mana(g)` return 0 when the part is off, so the bonus text disappears with it.)

### 4.5 `Perks` hooks (world thread, inside the existing 1 s `Perks.tick`)

```java
public static boolean OVL_FAILED_ONCE = false;
public static void ovl(java.util.UUID u, {CB} cb, {REF} ref, {ESM} m) {
  try {
    int[] sc = {PKG}.Overall.sums(u, {PKG}.SkillStore.data(u));
    int ol = {PKG}.Overall.level(sc);
    int mi = {DST}.getMana();
    int hi = {DST}.getHealth();
    mod(m, mi, "skyyskill_basemana", {PKG}.Overall.baseMana(u, {PKG}.Overall.typeMax(mi)));
    mod(m, hi, "skyyskill_overallhp", {PKG}.Overall.hp(ol));
    mod(m, mi, "skyyskill_overallmana", {PKG}.Overall.mana(ol));
    {PKG}.Overall.publish(u, ol);
    int g = {PKG}.Overall.takeHeal(u);
    if (g > 0 && {PKG}.OverallCfg.ON && {PKG}.OverallCfg.HEAL && cb.getComponent(ref, {DTH}.getComponentType()) == null) {
      {ESV} hv = m.get(hi);
      float amt = {PKG}.Overall.round2(g * {PKG}.OverallCfg.HP);
      if (hv != null && hv.get() > 0.0f && amt > 0.0f) m.addStatValue(hi, amt);
    }
  } catch (Throwable t) {
    if (!OVL_FAILED_ONCE) { OVL_FAILED_ONCE = true; {PKG}.SkillCfg.warn("overall level tick failed (logged once): " + t); }
  }
}
```

Called at the end of `tick` (after the three perk mods). Its own try, so an Overall failure never stops the existing perks. Not gated
by `perk.enabled` (that switch only turns off the per-skill perks). `mod` writes only on change, so no stat packet goes out in a
steady second.

### 4.6 `SkillXp.gain4`

One call, anchor 8 in 4.1: `{PKG}.Overall.levelUp(pr, u, skill, r[0], r[1]);`. It runs only inside the existing `if (r[1] > r[0])`
branch (a real level up), after the "next:" line and before `SkillStore.publish(u)`. Party shares (`PartyXp` -> gain4), bridge grants
(BridgeTask -> gain3) and the admin `/skills xp` all pass through it.

### 4.7 Pages (inline; ids without underscores; dynamic text only through `b.set`; no hover handlers; no periodic updates)

**SkillsPage.build** (replaces the average loop and the "Skill average" label; `cs` and `rows` stay for the row loop):

```java
int[] osc = {PKG}.Overall.sums(u, d);
b.appendInline("#SkyySkills", "Label { Anchor: (Height: 30); Text: \"Skills\"; ... }");          // unchanged title
b.appendInline("#SkyySkills", "Group #SkyySkOvRow { Anchor: (Height: 28); LayoutMode: Left; }");
b.appendInline("#SkyySkOvRow", "Label #SkyySkOv { Anchor: (Width: 490, Height: 28); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center); }");
b.set("#SkyySkOv.Text", "Overall Level " + {PKG}.Overall.level(osc) + "  -  average " + {PKG}.Overall.avg({PKG}.Overall.tenths(osc)) + " of " + osc[1] + " skills");
b.appendInline("#SkyySkOvRow", "TextButton #SkyySkOvStat { Anchor: (Width: 110, Height: 26); Text: \"Overall\"; " + bs + " }");
ev.addEventBinding({BT}.Activating, "#SkyySkOvStat", {EVD}.of("a", "skstatov"));
```

The 6 px spacer after it stays. Footer text: `... explore.  Stats shows every boost - level ups pay coins`.

**SkillsPage.handleDataEvent**, first branch: `if (data.indexOf("skstatov\"") >= 0) { open new OverallPage(this.playerRef); return; }`
(the trailing quote keeps it apart from `skstat<N>"`).

**OverallPage** (`CustomUIPage`, constructor `super(pr, {LIFE}.CanDismiss)`, `public void build(...)`, `handleDataEvent`): root
`Group #SkyySkOvPage { Anchor: (Width: 960, Height: 795); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 15);
LayoutMode: Top; }`, own `line` / `wrapLine` helpers (the StatsPage ones append into `#SkyySkStats`). Rows, top to bottom (heights):
accent 3; title `#SkyyOvTitle` 45 (24 bold `#ffe08a`); sub `#SkyyOvSub` 27 (17); bar row 24 (156 px spacer + `#SkyyOvBar` 600 x 18,
fill = 600 at max else `(tenths % 10) * 60`, colour `#ffe08a`); spacer 12; `#SkyyOvSkHd` 36 (20 bold) + `#SkyyOvSk` wrapLine 60 (17);
spacer 12; `#SkyyOvNowHd` 36 + up to 3 `#SkyyOvNow<i>` 28 (18); spacer 12; `#SkyyOvNextHd` 36 + up to 2 `#SkyyOvNext<i>` 28; spacer 12;
how-to `#SkyyOvHow` wrapLine 45 (15): "The Overall Level is the average of the skills above, rounded down - level any of them to raise it.
Other classes' skills never count (a new class is a new profile)."; nav 60 with `#SkyyOvBack` "< Back" 195 x 45 (payload `ovback`,
opens SkillsPage). Total 560 of the 765 px inside the padding. Button style = the StatsPage `bs` string (18 pt).

**StatsCmd.execute**, first lines: `String a = String.valueOf(ctx.get(this.skillArg)).trim(); if (a.equalsIgnoreCase("overall")) {
open OverallPage; return; }`. The unknown-skill text in `SkillClass.argSlot` gets "... or overall" appended.

### 4.8 Bridge

| Key | Value | Notes |
|---|---|---|
| `skill:overall:<uuid>` | `Integer` Overall Level of the ACTIVE profile | put by `Overall.publish` (gain4 level ups at once; `Perks.tick` every second when it differs); never removed (like `skill:<uuid>`) |
| `skill:fn:overall` | `Function` `apply(UUID)` or `apply(Object[]{UUID})` -> `Object[] { Integer level, Integer averageTenths, Integer skillsCounted, Float maxHealthBonus, Float maxManaBonus, Float baseMana }`; `null` on a bad argument or any error | `OverallFn`; put in `setup()`, removed in `shutdown()` like the other `skill:fn:*`. Reads `SkillStore.data(u)`, so like `skill:fn:level` it may load the player's file on the caller's thread; never throws, never touches ECS |
| `skill:fn:level` | now also answers the name `Overall` (any case) with `Integer` Overall Level | `SkillFn.apply`: `if ("overall".equalsIgnoreCase(String.valueOf(a[1]).trim())) return Integer.valueOf({PKG}.Overall.levelOf((java.util.UUID) a[0]));` before `indexOf`. No other name changes |
| `skill:<uuid>` | unchanged | never gets an Overall entry (3.3) |

### 4.9 Server Setup rows (`reload` binding to `xp.properties`, kit 1.1 build checks)

`CFG_CATS`: insert `("overall", "Overall and Mana")` after `("perks", "Perks")` (9 categories, label 16 characters).

```python
# parts (after the perk.archery.keepLoaded.enabled row); part switch = bool + live,part,danger; asks only when switched OFF
("mana.base.enabled", "Base Mana", "parts", "bool", "true", "", "", "", "", _LP,
 "Off: no base Mana from Skills (vanilla max Mana is 0). Alchemy and Overall Level Mana stay.", "reload"),
("overall.enabled", "Overall Level Health and Mana", "parts", "bool", "true", "", "", "", "", _LP,
 "Off: the Overall Level adds no max Health or Mana. It is still shown on /skills.", "reload"),
# overall (new category)
("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
 "Max Mana every player starts with (vanilla gives 0).", "reload"),
("mana.magicBase", "Base Mana for magic users", "overall", "dec", "20", "0", "10000", "", "", "live",
 "Replaces the base above for the classes below: their base is this, not base + this.", "reload"),
("mana.magicClasses", "Magic user classes", "overall", "text", "Mage,Priest", "", "200", "", "", "live",
 "Class names, comma separated (Mage, Priest, Archer, Warrior, Berserker, Assassin, Shaman).", "reload;check=OverallCfg.checkClasses"),
("overall.skills", "Skills in the Overall Level", "overall", "text", OVL_SKILLS_DEF, "", "300", "", "", "live",
 "Comma list. Class = the profile's own class skill; other classes' skills never count.", "reload;check=OverallCfg.checkSkills"),
("overall.healthPerLevel", "Max Health per Overall Level", "overall", "dec", "0.5", "0", "100", "", "", "live",
 "Placeholder. 0.5 = +50 max Health at Overall Level 100.", "reload"),
("overall.manaPerLevel", "Max Mana per Overall Level", "overall", "dec", "0.2", "0", "100", "", "", "live",
 "Placeholder. 0.2 = +20 max Mana at Overall Level 100.", "reload"),
("overall.healOnLevelUp", "Fill the new Health on level up", "overall", "bool", "true", "", "", "", "", "live,adv",
 "On: an Overall level up also heals the max Health it added (players have no Health regen).", "reload"),
("overall.chat", "Overall level-up chat line", "overall", "bool", "true", "", "", "", "", "live",
 "Off: nobody gets the line. On: each player can still hide theirs in /settings.", "reload"),
```

Checks to add next to 0.4.5's: `assert len(CFG_ROWS) == 169` ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows"); each new key
exactly once in `CFG_ROWS`, present in `_dp` and in `OVL_DEFAULTS`; `_absent` stays 21 (every new row's default is in the default file:
the existing default-equals-file check covers them). Labels <= 40, help <= 100 (the kit checks too).

### 4.10 Settings registration (`setup()`, after the `rewards.late` line)

`{PKG}.SkillStore.regSetting("skills.overallUp", "Overall Level ups", "skills", true, "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added");`

### 4.11 setup / shutdown / texts

- Ready line: `... crossbows stay loaded at Archery 5 (on); overall level " + {PKG}.OverallCfg.text() + "; ...` and
  `skill:fn:overall` in the bridge list.
- Manifest description: add "Base Mana for every player (magic users more) and an Overall Level - the average of your skills - that
  adds max Health and Mana (Server Setup). Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first."
- Docstring: a 0.4.6 paragraph on top (the 0.4.5 style: WHAT / WHO / HOW / CONFIG / TEXTS / BUILD CHECKS / CHECKED / UNVERIFIED).

### 4.12 Build checks (fail the build)

- API probes (`B.probe`): `(ESM, "addStatValue")`, `(ESM, "get")`, `(ESV, "getMax")`, `(ESV, "get")`, `(ESTT, "getMax")`,
  `(ESTT, "getAssetMap")`, `(DST, "getHealth")`, `(DST, "getMana")`, `(DTH, "getComponentType")`, `(SMO, "getAmount")`, `(MTG, "MAX")`,
  `(CAL, "ADDITIVE")`. (`ESTT` is SkyySkills' name for EntityStatType; `EST` there is EntityStore.)
- `Assets.zip` `Server/Entity/Stats/Mana.json` must exist; print its Max, ResetType and Regenerating (interval, amount, conditions). If
  `Max` is not 0, print a loud note (the base-Mana rule of 2.1 still holds, but Skyy should hear about it).
- Modifier keys: the 3 new keys start with `skyyskill_`, differ from each other and from `skyyskill_health / _stamina / _mana`, and none
  starts with `skyyacc_` or `skyygear`.
- `OVL_SKILLS_DEF` tokens are LABELS of slots {0, 1, 2, 4, 10, 11, 12, 13} plus `Class`; `mana.magicClasses` default names are in
  `CLASS_ROWS` names; `OverallCfg.SLOTS` default equals the parsed default text.

### 4.13 Threads and locks

- Stats, components and `addStatValue`: world thread only (`Perks.tick` inside AcroSys).
- Chat line: world thread (gain4).
- `OverallFn` / `skill:fn:level` "Overall": any thread, bridge reads + `SkillStore.data` (existing behaviour of `skill:fn:level`).
- `Overall.addHeal` / `takeHeal`: own class monitor, one map operation inside, nothing called under it. No other lock is added.

### 4.14 Compatibility, deploy, downgrade

- Every mix loads: without SkyyClasses the class row is skipped; without SkyyProfiles `class:<uuid>` decides the class; without
  SkyyMenu the rows are file-only and the chat switch is always on; SkyyAccessories 0.4.4 benefits with no change.
- **Downgrade to 0.4.5:** files are fine both ways, but the three saved stat keys would stay on players forever. Switch "Base Mana" and
  "Overall Level Health and Mana" off first (Server Setup, confirm), let players log in once, then downgrade. The coordinator should add
  this to the deploy notes next to the pin.

---

## 5. Test plan

### 5.1 Bare JVM harness (scratch under `tools/dev/scratch/r8-skills/`, deleted afterwards; `-Xverify:all`)

1. Every class loads and initialises; `OverallCfg.read` defaults; clamps (base -5 -> 0, 20000 -> 10000, per-level 200 -> 100, NaN ->
   default); `ensureDefaults` appends the block once to a 0.4.5 file (custom values kept, a second load adds nothing).
2. `parseSkills`: default -> 8 slots + class; `mining, CLASS` -> {0} + class; duplicates, `Archery`, `Combat`, `Min` (prefix), empty ->
   null. `checkSkills` / `checkClasses` texts; `parseClasses("priest, mage, Druid")` -> {Priest, Mage}.
3. `sums` with a mock bridge + data: the section 2.3 example -> 92 / 9, level 10, tenths 102; 116 / 9 -> 12 / 128; all 100 -> 100 / 1000;
   Archer with Divinity XP left over -> Divinity ignored; legacy Combat XP ignored; no class + SkyyClasses mock present -> n = 9, class 0;
   no `class:fn:allowed` -> n = 8; `profile:class` = Priest while `class:` = Archer -> the Priest slot; unknown class -> n = 8 + one WARN.
4. `baseMana`: no class 10; Mage / Priest / "priest" 20; Warrior 10; part off 0; `magicClasses` empty -> 10; typeMax 0 / 5 / 30 -> 10 /
   5 / 0. `hp` / `mana` rounding (level 3 x 0.2 = 0.6, never 0.6000001) and part off -> 0.
5. `levelUp` with a capturing PlayerRef mock: a counted skill crossing a boundary -> one line, `HEAL` += gain, bridge updated; not
   crossing -> no line; another class slot -> nothing; `overall.chat` off or the setting off -> no line but HEAL + bridge still set.
6. Kit: 169 rows; the 10 rows (category, type, default, bounds, flags, position); get; the parts ask only when switched OFF; the hooks
   refuse bad text; file lines change in place and `SkillKit.reload` applies them.

### 5.2 Build

`python tools/skills_0_4_6_patch.py`, `python SkyySkills/build_skyyskills_0.4.6.py` -> `assembled ...SkyySkills-0.4.6.jar`;
`python tools/ci/lint.py` -> 0 fails; `python tools/deploy_set.py --check` only after the coordinator pins it.

### 5.3 In game, one account (Skyy)

1. Join with 0.4.6 on the Priest profile: a vanilla Mana bar appears (UNTESTED client behaviour) and fills 0 -> 20 in about 4 s; take a
   hit -> regen stops for 6 s; hold a wand charge -> no regen while charging.
2. Warrior profile: max Mana 10. Switch Warrior <-> Priest: 10 <-> 20 within a second; switching down clamps, switching up does not
   refill.
3. `/skills`: the header shows "Overall Level N - average X.Y of 9 skills" and matches a hand count; the Overall button and `/skills
   stats overall` open the Overall page; its numbers match; Back returns.
4. `/skills xp <skill> <amount>` across an Overall boundary: "OVERALL LEVEL UP" after the SKILL LEVEL UP lines; max Health +0.5 within a
   second and current Health +0.5 (heal on); XP into another class's skill (e.g. `divinity` on an Archer) -> no line.
5. `/settings` -> Skills tab (last row): "Overall Level ups" off -> no line on the next Overall level up; on -> line.
6. Server Setup -> Skills -> "Overall and Mana": healthPerLevel 0.5 -> 1 -> max Health changes within a second, current Health unchanged;
   "Overall Level Health and Mana" off (asks to confirm) -> bonus gone; "Base Mana" off -> a Warrior's max Mana 0 (bar hides, UNTESTED);
   `mana.magicClasses` "Mage,Priest,Druid" is refused with the class list.
7. An Intelligence talisman in the Accessory Bag now adds Mana (Legendary: 10 % of the flat pool).
8. Die and respawn: Health and Mana full. Relog: the same max values immediately at join.
9. `/profileadmin setclass <you> Mage` on a Warrior profile -> max Mana 20 within a second.

### 5.4 Two accounts (A = Skyy Priest, B = Warrior)

Each sees only their own base Mana and Overall Level; A's level up line never reaches B; party widget Mana shows 20 / 10.

### 5.5 Compatibility

SkyyClasses removed (test world copy): class row skipped (n = 8), base Mana still 20 for a `profile:class` Priest. SkyyProfiles
removed: `class:<uuid>` decides. With SkyyGear once it lands: its Health / Mana keys add to ours (compare `/skills` Overall page
numbers with the character panel). Downgrade drill (4.14) on a copy.

---

## 6. Open questions for Skyy (each has a live default)

1. **Casting at base 20 [SKYY?]:** the Wood Wand cast needs 25 Mana, staff summons 50, spellbooks 100. At base 20 a new Priest or Mage
   swings but cannot cast until +5 more Mana (Overall Level 25, Alchemy 25, one Silk / Cindercloth / Onyxium / Prisma cloth piece, or an
   Intelligence talisman on top of about 23). Raise `mana.magicBase` to 25, or keep casts as a progress reward? [20, as you said]
2. **Health / Mana per Overall Level** [+0.5 Health, +0.2 Mana - placeholders; +50 / +20 at Overall 100].
3. **Class skill in the average:** only the profile's own class skill counts, a profile without a class yet counts it as 0, and without
   SkyyClasses it is left out. [yes, yes, yes]
4. **Cooking and Exploration** count by default (both mods are in the pack); a server without them removes them from the list. [count]
5. **Heal the added Health** on an Overall level up (players have no Health regen). [yes]
6. **Overall level-up chat line** default on, players can hide it in /settings. [on]
7. **Mana bar for everyone:** base 10 means every player (also Warriors) gets the vanilla Mana bar. [yes - your call]
8. **Magic users:** Mage and Priest. Shaman when it exists? [no - only Mage and Priest until you say]
9. **Keep the per-skill Health / Mana perks** (Farming +0.25 Health, Foraging and class +0.1, Alchemy +0.2 Mana per level) next to the
   Overall bonus? [keep]
10. **Overall leaderboard** (`/skills top overall`)? [not now]
11. **Base Mana = total base** (subtracts a future engine base) rather than extra on top of it. [total]
12. **Same Overall Mana rate for magic users** (not doubled). [same]
13. **Switching to a weaker profile** clamps Health / Mana down; switching back does not refill (no free heal). [as written]
14. **Talismans:** Intelligence now works on a base of 10-20 but Common 2 % is still about +0.2 Mana early. Make the low tiers flat in
    SkyyAccessories later? [leave SkyyAccessories as is]
15. **Staff bypass or clean-up action:** no admin button to strip the saved stat keys before an uninstall; the parts-off procedure
    (4.14) covers it. [no button]

---

## 7. Not in this spec

The refusing Settings switches (party.invites / tpa.requests / msg.private), the bag rarity restructure and the Mythic Omni Bag, the
Mining-bag-from-Iron change, SkyyGear / SkyyAuctions / SkyyMenu / SkyyRolls, SkyyHud widgets and any class skill tree. HANDOFF,
TEST-CHECKLIST, DESIGN-STATUS, OPEN-QUESTIONS and `tools/deploy_set.py` updates are the coordinator's.
