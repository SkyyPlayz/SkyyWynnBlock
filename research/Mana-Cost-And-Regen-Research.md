# Mana cost and Mana regen - research (2026-09-30)

Skyy play-tested SkyySkills 0.4.8 (verbatim): *"the wand spell only costs 5 mana. but you still have to be above 25 mana to actually
cast it. and it looks like your mana regen is different in and out of combat. so lets get the vanilla numbers on each of those. /
figure out how they work. cause we need to keep our new +mana regen perks balanced."*

Corrected after the SkyySkills 0.4.9 review (2026-09-30):
- 1.4 now names the plain Blunderbuss next to Crystal_Red and Crystal_Ice.
- 1.2 and 2.4 now say that `Weapon_Staff_Thorium` keeps the dead staff var in 0.7.
- 1.2 now says what a null `costs` map does.
- The 4.1 out-of-combat tallies are now labelled as estimates.

No fix number changed.

Everything below was read from the live `HytaleServer.jar` 0.6.8 (Implementation-Revision-Id d2feeb39...), the 0.7.0-pre.4 jar
(fab7fc95...), both `Assets.zip` files and the live `SkyySkills.jar` (byte-identical to `SkyySkills/SkyySkills-0.4.8.jar`), with the
tools/dev helpers (callers.py, bc.py, cpgrep.py) and small scratch scripts (javassist InstructionPrinter dumps, a JSON scan of every
`Server/Item`, `Server/Entity` and `Server/NPC` asset, a cast simulator). Nothing was built or deployed. The live world "HUD mod"
enables only Skyy mods plus `Serj:More Crossbow Tiers` and `Helios:Saplings From Trees`, and neither of those ships a caster or Mana
file (checked).

## 0. Answer in short

- **The 25 comes from the vanilla interaction asset `Wand_Cast_Left_Charged`** (`Server/Item/Interactions/Weapons/Wand/Attacks/`),
  a `StatsCondition` with its own `"Costs": {"Mana": 25}`. The wand's Charging step names that asset directly. **Item
  InteractionVars never change it.** A var is only read by a `Replace` interaction that names it, and no `Replace` anywhere names
  `Wand_Cast_Left_Charged`. So the item var that 0.4.8 cut from 25 to 5 is dead data. The drain var (`Wand_Cast_Left_Cost`) IS read
  by a `Replace`, and that is why the cast drains 5.
- The same bug hits every family. Spellbooks: the gate is 25 and the drain 20. Blunderbusses: the gate is 50 and the drain 10, so a
  30-Mana caster can never fire one. **Staffs (the Mage kit) have no Mana gate at all**, because `Staff_Cast_Summon_Charged` is a
  `Simple` interaction. Once Mana hits 0, a staff keeps casting for free.
- **Fix (0.4.9):** also generate overrides of the charged-cast interaction assets, so check = drain. Wand gate 25 -> **5**,
  spellbook 25 -> **20**, blunderbuss 50 -> **10**. For staffs, Skyy picks: add a gate of **10** (recommended) or keep vanilla's free
  cast. Optionally scale the four default drain interactions too. Details in 1.4.
- **Vanilla Mana regen:** +1 every 0.2 s = **5 Mana per second** (flat, not scaled by max). It only runs while you are alive,
  **6 s after you last took damage**, and **not while you hold a charge**. "In combat" for Mana means "took damage in the last 6 s".
  Dealing damage does not count. In combat the regen is **0**. Players have no natural Health regen. Stamina refills at 3 per second.
- **Balance:** vanilla already refills a 30-Mana pool in 6 s out of combat, so our perks only matter **in combat**. A %-of-vanilla
  perk is 0 in combat. So Mana Regen perks should be **flat "+N Mana every 5 s", on at all times**, with a total cap. Placeholders
  are in 4.4.

---

## 1. The cast gate

### 1.1 What blocked Skyy at 25 (the full chain, Weapon_Wand_Wood)

1. Item `Weapon_Wand_Wood` (also `_Tribal`, `_Wood_Rotten`): `"Interactions": {"Primary": "Wand_Primary", "Secondary": "Wand_Primary"}`
   = RootInteraction `Wand_Primary` -> Interaction `Wand_Primary`.
2. Interaction `Wand_Primary` = `Type: Charging`, `Next: {"0": <Chaining: Sword_Swing_Left_Fast / Right_Fast>, "0.35":
   "Wand_Cast_Left_Charged"}`. A tap is a melee swing. Holding 0.35 s or longer casts.
3. `"Wand_Cast_Left_Charged"` is a **plain string**. It resolves to the **Interaction asset** of that id:
   `Type: StatsCondition, Costs: {Mana: 25}, RunTime 0.167`. **This is the gate.** Same file in 0.6.8 and 0.7.0-pre.4.
4. Pass: a `Parallel` of three `Replace` interactions: var `Wand_Cast_Left_Cost` (default `Wand_Cast_Cost` = -25), var
   `Wand_Cast_Left_Launch`, var `Wand_Cast_Left_Effect`. The item defines `Wand_Cast_Left_Cost` as
   `{Parent: Wand_Cast_Cost, StatModifiers: {Mana: -25}}`, which 0.4.8 makes -5. **That is the 5 Skyy saw.**
5. Fail: `Replace` var `Wand_Cast_Left_Fail` -> `Wand_Cast_Fail` (the "no ammo" click, `SFX_Bow_No_Ammo`).
6. The item ALSO defines a var named `Wand_Cast_Left_Charged` = `{Parent: Wand_Cast_Left_Charged, Costs: {Mana: 25}}`, which 0.4.8
   makes 5. Nothing ever reads it (1.2). A search of every `Server/**` asset finds **no `"Var": "Wand_Cast_Left_Charged"`**, and the
   same is true for `Staff_Cast_Summon_Charged`, `Spellbook_Cast_Hurl_Charged` and `Gun_Shoot_Flintlock_Charged`.

So a Priest (base 30, kit `Weapon_Wand_Wood`) can cast at 30 (-> 25) and at 25 (-> 20), and is then blocked until regen brings them
back to 25. That is exactly the "above 25" Skyy felt. The check is `>=`, so 25 itself passes.

### 1.2 The engine rules (bytecode, 0.6.8)

- **StatsCondition** (`StatsConditionInteraction.firstRun` / `canAfford`): for each entry of the interaction's OWN `costs` map, it
  reads the stat and fails (`InteractionState.Failed`, which runs `Failed`) if `value < cost`. `costs` is the decoded `rawCosts`
  (stat id -> number) resolved to stat indexes after decoding (`EntityStatsModule.resolveEntityStats`). If nothing resolves, `costs`
  is null and `canAfford` returns false, so every cast fails. It never drains anything. The one
  exception is `canOverdraw`: `Lenient` true, value > 0 and the stat's **min < 0**. Mana's min is 0, so it never applies to Mana.
  `ValueType` Percent compares `asPercentage() * 100`. The costs are also copied into the client packet (`configurePacket`), so the
  client predicts the same gate. Among server interaction configs only `StatsConditionBaseInteraction` (+ its two subclasses)
  declares a `Costs` key (cpgrep; the other hit is the protocol packet `SpawnDeployableFromRaycastInteraction`). `Simple` has none,
  so a `Costs` key on a Simple interaction is ignored.
- **String references resolve through the global asset map, once.** `ChargingInteraction.compile` calls
  `Interaction.getInteractionOrUnknown(next.get(key)).compile(builder)`. `getInteractionOrUnknown` is `Interaction.getAssetMap()
  .getAsset(getInteractionIdOrUnknown(id))`. So the charged step is compiled INTO the root's operation list. The held item is never
  asked. The same goes for every other string `Next` / `Failed` / list entry.
- **Item InteractionVars are read by `Replace` only.** Every caller of `InteractionContext.getInteractionVars()` in the server
  (callers.py) is `ReplaceInteraction.doReplace` / `walk`. The default getter `InteractionContext.defaultGetVars` returns the held
  `Item.getInteractionVars()`. Two other places set their own getter: `WeaponDamageDataCollector` (tooltip damage math) and NPC
  `ActionAttack` (the Role's vars). `doReplace` does `vars.get(variable)`. If that is missing it uses `DefaultValue` (with a SEVERE log
  unless `DefaultOk`). It then runs `context.execute(RootInteraction.getRootInteractionOrUnknown(id))`. **The value is a
  RootInteraction id or an inline root. The var NAME only matters to a Replace with that `Var`.** A var named like an interaction
  asset overrides nothing.
- **ChangeStat never fails** (`ChangeStatInteraction.firstRun` -> `EntityStatMap.processStatChanges`). It adds the amount and the
  value clamps to [min, max]. A drain larger than your Mana still casts and leaves 0.
- **Hypixel's own evidence:** in 0.7.0-pre.4, 22 of the 23 staff items that carry the `Staff_Cast_Summon_Charged` var in 0.6.8
  **dropped** it and kept only the drain var. The two exceptions are `Weapon_Staff_Thorium`, which keeps it, and the new
  `Weapon_Staff_Scrap_Lightbulb`, which has it. So the dead var was mostly cleaned up. The new 0.7 Rune ability
  `Ability_ChargedShot_Release_1..4` puts the StatsCondition and the ChangeStat in **one chain with equal numbers** (10/20/30/50).
  That is the correct pattern.

### 1.3 Every caster family

| Family (items) | Charged step (Interaction asset) | Real gate, vanilla | Gate in 0.4.8 LIVE | Drain vanilla -> 0.4.8 | 30-Mana caster today |
|---|---|---|---|---|---|
| Wands: `Weapon_Wand_Wood`, `_Tribal`, `_Wood_Rotten` (Priest kit) | `Weapon/Wand/Attacks/Wand_Cast_Left_Charged` = StatsCondition | **25** | **25** (not changed) | 25 -> 5 | 2 casts, then needs 25 |
| Staffs: the 22 staffs on `Staff_Primary` (21 overridden by 0.4.8 + Crystal_Red) + `Halloween_Broomstick` (Mage kit `Weapon_Staff_Wood`) | `Weapon/Staff/Attacks/Staff_Cast_Summon_Charged` = **Simple, no Costs** | **none** | none | 50 -> 10 (Crystal_Red 0, not overridden) | 3 paid casts, then **free casts at 0 Mana forever** |
| Spellbooks: `Weapon_Spellbook_Demon`, `_Fire`, `_Frost`, `_Grimoire_Brown`, `_Grimoire_Purple` | `Weapon/Spellbook/Attacks/Spellbook_Cast_Hurl_Charged` = StatsCondition | **25** (vanilla drain is 100: mismatched in vanilla too) | 25 | 100 -> 20 | 1 cast (30 -> 10), then needs 25 |
| Blunderbusses: `Weapon_Gun_Blunderbuss`, `_Rusty` | `Weapon/Gun/Attacks/Shoot_Flintlock/Gun_Shoot_Flintlock_Charged` = StatsCondition | **50** | 50 | Rusty 50 -> 10; plain Blunderbuss drains 0 (vanilla) | **never fires** (30 < 50) |
| Not Mana: `Weapon_Staff_Crystal_Ice` (Stamina + Ice Essence; its Primary wrapper leads into `Staff_Primary`, drain var 0), `Weapon_Staff_Crystal_Flame` (`Root_Weapon_Stick_Fire_*`), `Weapon_Staff_Crystal_Red` (all 0), `Weapon_Wand_Root`, `Weapon_Wand_Stoneskin`, `Weapon_Spellbook_Rekindle_Embers`, `Weapon_Gun`, `Weapon_Deployable_Healing_Totem` | - | none | - | - | - |

Side facts. Staff casts also cost 5 Stamina and set `StaminaRegenDelay` -1.5 (the `DefaultOk` Replace defaults in
`Staff_Cast_Summon_Charged`; no staff item overrides them except Crystal_Ice). That does not stop a cast either (ChangeStat), but at 0
Stamina it applies `Stamina_Broken` (guard broken until Stamina is full). Separately, `Spellbook_Cast_Cost` chains `ModifyInventory
AdjustHeldItemQuantity -1`, and the item drain vars inherit it by `Parent`. So a spellbook cast may use up the book. That is vanilla
behaviour we do not touch (UNVERIFIED in game).

### 1.4 Fix list for SkyySkills 0.4.9 (so the check and the drain match everywhere)

This extends the 0.4.8 SPELL GEN block. It reads Assets.zip in memory at build time and ships generated overrides at the vanilla path
(same id, our pack wins, the 0.4.8 pack check pattern). Nothing is committed to git. **The whole list of Mana numbers in 0.6.8
assets** (scan of every `Server/Item`, `Server/Entity`, `Server/NPC` JSON; `RootInteractions` carry none):

| # | Asset (under `Server/Item/Interactions/`) | Mana now | New | Why |
|---|---|---|---|---|
| 1 | `Weapons/Wand/Attacks/Wand_Cast_Left_Charged.json` | Costs 25 | **5** | the wand gate (Skyy's blocker) |
| 2 | `Weapons/Spellbook/Attacks/Spellbook_Cast_Hurl_Charged.json` | Costs 25 | **20** | = the spellbooks' drain 100 / 5. A plain 25 / 5 = 5 would let a 5-Mana player spend 20 and sit at 0 |
| 3 | `Weapons/Gun/Attacks/Shoot_Flintlock/Gun_Shoot_Flintlock_Charged.json` | Costs 50 | **10** | the blunderbuss gate (drain 10 Rusty; the plain one stays drain 0 = vanilla). Catch: the plain `Weapon_Gun_Blunderbuss` then needs 10 Mana present to fire (not spent). Vanilla needed 50, so this is still easier than before |
| 4 | `Weapons/Staff/Attacks/Staff_Cast_Summon_Charged.json` | no gate (Simple) | **SKYY DECIDES**: `Type` Simple -> StatsCondition + `Costs: {Mana: 10}`, rest unchanged | closes the free-cast-at-0 hole. Same shape as #1 (StatsCondition also has RunTime / Next / Failed, and `Failed` -> `Staff_Cast_Fail` already exists). Catch: `Crystal_Red` (drain 0) and `Crystal_Ice`'s charged Primary would then need 10 Mana present (not spent). Keeping vanilla = staffs stay free at 0 Mana |
| 5 | `Weapons/Wand/Wand_Cast_Cost.json` | -25 | -5 | the default drain (Replace `DefaultValue`, and `Parent` of each item's drain var). No vanilla caster uses the default today (0.4.8 proves every caster defines its own drain var), but another mod's or a future item would. Recommended for "everything / 5" |
| 6 | `Weapons/Staff/Attacks/Staff_Cast_Cost.json` | -25 | -5 | same as #5 |
| 7 | `Weapons/Spellbook/Spellbook_Cast_Cost.json` | -25 | -5 | same as #5. Keep its `Next` (ModifyInventory) untouched |
| 8 | `Weapons/Gun/Attacks/Shoot/Gun_Shoot_Cost.json` | -75 | -15 | same as #5 |
| - | `Tests/StatsCondition.json` | Costs 25 | leave | test asset, referenced by nothing |
| - | the 32 item overrides of 0.4.8 | | keep | the drains are right. The `*_Charged` vars stay as dead data (the 0.4.8 "vanilla except the numbers" rule) |
| - | `Entity/Effects/Mana/*` (Mana 12, -100, 25, 5, Regen 1/1/1) | | leave | effects no vanilla item applies. Potion_Mana / Potion_Regen_Mana are decorative blocks (`Block_Primary`) in both versions |
| - | Armor `Armor.StatModifiers.Mana` (Silk set +60, Cindercloth +64, Onyxium +80, Prisma +100, 2 debug items) | | leave (see 4.5) | max-Mana bonuses, not costs |

**As built in SkyySkills 0.4.9 (Skyy can still reverse #4):** #1-#8 are all taken, with the staff check at 10. Three items then
check 10 Mana but spend 0:
- `Weapon_Staff_Crystal_Red` (#4).
- `Weapon_Staff_Crystal_Ice` (#4, Primary only). Its Secondary bolt checks Stamina, not Mana, and stays Mana-free.
- The plain `Weapon_Gun_Blunderbuss` (#3). Vanilla needed 50.

A 10-Mana non-caster needs a full bar to use them. The alternative is keeping vanilla's free staff cast at 0 Mana. Then a Mage casts
for free forever once out of Mana, and Mana Regen perks would mean nothing for staffs.

Also in 0.4.9:
- **ManaGuard / `ManaCost.COST`** holds the item var numbers (5/10/20/10), i.e. the dead var. Its WARN / INFO ("casts from full")
  reports 6 wand casts for a Priest while the game allows 2. With the fix the real gates equal these numbers. The staff entry must
  follow Skyy's #4 choice (10, or "no gate").
- **New self-checks** (the ones that would have caught this): for every caster item, walk Primary / Secondary -> RootInteraction ->
  Charging `Next` -> the charged Interaction, and assert its `Costs.Mana` (after the change) == that family's drain magnitude. Assert
  every Mana number found in `Server/Item/Interactions/**` and `RootInteractions/**` is in the table above (or allowlisted: the test
  asset). Assert each family's items share one drain value, since one gate serves the whole family. Items that spend 0 are the
  exception, and the build lists them (the three named above). The 0.4.8 generator scanned only
  `Server/Item/Items/**`, which is why it missed #1-#3.
- **NPC-only interactions: nothing to change.** No NPC interaction carries a Mana number (scan). The mages (Skeleton_Mage /
  Archmage, Sand / Frost / Burnt / Incandescent variants, Trork Shaman / Mage / Doctor_Witch, Outlander_Sorcerer, Feran_Windwalker,
  the gunners) hold a wand / staff / spellbook / gun item **only as a look**. They attack with their own `Interactions/NPCs/**`
  roots (for example `Skeleton_Mage_Wand_Corruption_Orb`), and `ActionAttack` uses the Role's vars, not the item's. No NPC file names
  `Wand_Primary`, `Staff_Primary`, `Spellbook_Primary`, `Gun_Shoot_Flintlock_*` or any `*_Cast_*` interaction. Our overrides of
  #1-#8 therefore cannot change a mob.
- 0.7.0-pre.4 note: the charged-cast interactions are byte-identical. The 0.4.8 build's shape check ("a changed item has exactly one
  check and one drain") will **fail on 0.7 assets**, because most 0.7 staffs have only a drain var (all but `Weapon_Staff_Thorium`
  and the new `Weapon_Staff_Scrap_Lightbulb`, 1.2). And `Ability_ChargedShot_Release_1..4`
  (10/20/30/50) would join the /5 list.

---

## 2. Vanilla regen: numbers and rules

### 2.1 Stat files, 0.6.8 (`Server/Entity/Stats/*.json`)

| Stat | Initial / Min / Max | Regen entries (Interval, Amount, type, conditions) |
|---|---|---|
| **Mana** | 0 / 0 / **0**, ResetType MaxValue (respawn refills to max) | **0.2 s, +1, Additive**: `Alive`, `NoDamageTaken` Delay **6**, `Charging` Inverse |
| Stamina | 10 / -4 / 10 | 0.1 s +0.3 Additive: `StaminaRegenDelay` at 0, Stamina >= 0, not `Wielding`, not `Sprinting`, not `Gliding`. The same +0.3 while overdrawn (Stamina < 0). Creative: 0.5 s +100% (Percentage). Sprinting: 0.1 s -0.1. Gliding: 0.1 s -0.1. At 0 (`TriggerAtZero`): `Stamina_Broken_Check` + set `StaminaRegenDelay` -0.5 |
| StaminaRegenDelay | 0 / -60 / 0 | 0.1 s +0.1 while not gliding (climbs back to 0 at 1 per second; actions set it negative, e.g. staff cast -1.5) |
| Health | 100 / 0 / 100, MaxValue | **Players: none** (survival). NPCs: 0.5 s +5% of max (Percentage) with `Alive`, not `IsPlayer`, `NoDamageTaken` Delay 15, `RegenHealth`. Creative: 0.5 s +100% |

How the engine runs it (`EntityStatsSystems$Regenerate` + `RegeneratingValue`): every tick the entry's countdown drops by dt. When
it reaches 0, it adds one Interval and **then** checks the conditions (`Condition.allConditionsMet`, with `TimeResource.getNow()`
as the clock). A failed check loses that pulse. Additive adds `Amount`. Percentage adds `Amount x (max - min)`. Then the amount is
multiplied by any `RegeneratingModifier` of the entry (none in vanilla) and added with `EntityStatMap.addStatValue`. Worn armor can add
its own regen entries (`ItemArmor.getRegeneratingValues`; only two `_Debug` armors use it). **There is no per-player regen modifier:**
`EntityStatMap` modifiers only target MIN / MAX (already proven in `research/Booster-Accessories-Spec.md` 5.4.1).

### 2.2 How "in combat" is decided (bytecode)

- **`NoDamageTaken` (what Mana uses):** true when `now - DamageDataComponent.lastDamageTime >= Delay`. `lastDamageTime` is written
  only by `DamageSystems$TrackLastDamage` (Inspect damage group) **on the entity that received** a Damage event, from any source
  (mob, player, fall, fire, drowning...). **Hitting something does not reset it.** So for Mana, "in combat" = took damage in the last 6 s.
- **`Charging` (Inverse):** true while any `ChargingInteraction` runs in the entity's interaction chains
  (`InteractionManager.forEachInteraction`, instanceof), or while `lastChargeTime` (set every tick by `ChargingInteraction.tick0`) is
  within `Delay` (default `Duration.ZERO`). Holding a wand / staff / spellbook / blunderbuss / bow charge pauses Mana regen. So does the
  first moment of a tap on those weapons, because their Primary IS a Charging interaction.
- `OutOfCombat` also exists (`lastCombatAction`, set on **both** the victim and the attacker by `DamageSystems$RecordLastCombat`,
  delay = `GameplayConfig.Combat.OutOfCombatDelay`, default **5 s**). **No vanilla stat uses it.** It is the condition to use if we
  ever want "attacking also counts as combat".
- `Alive`: not dead. `Wielding` (Stamina): the guard / block state (`DamageDataComponent.getCurrentWielding`).

### 2.3 Effective numbers (0.6.8)

| | Out of combat | In combat (hit in the last 6 s) | While holding a charge |
|---|---|---|---|
| **Mana** | **+5.0 per second** (flat, the same for any max) | **0** | **0** |
| Stamina | +3.0 per second (after `StaminaRegenDelay` is back to 0; not while blocking / sprinting / gliding) | same (no combat rule) | same (charging does not pause it) |
| Health (player) | 0 | 0 | 0 |

Mana time to full from 0, out of combat (add up to 6 s of waiting after the last hit):

| Pool | Who | Time |
|---|---|---|
| 10 | non-caster base (`mana.base`) | 2 s |
| 30 | Mage / Priest base | **6 s** |
| 50 | Mage + Overall 100 (+20) | 10 s |
| 90 | Mage + full Silk set (+60) | 18 s |
| 100 | 0.7 default for everyone | 20 s |
| 130 | Mage + full Prisma set (+100) | 26 s |

So Skyy's feel is right: out of combat the bar is full within seconds. After any hit it stops dead for 6 s, and it also stops while
you hold a cast.

### 2.4 0.7.0-pre.4 differences

- `Mana.json`: **InitialValue 100, Max 100** (every player spawns with 100 Mana). Same regen (0.2 s +1, `NoDamageTaken` 6, `Charging`
  Inverse), now with `UseIgnoreFlag` true on Charging. A Charging interaction flagged `IgnoreForFlaggedConditions` no longer pauses
  regen; only `Tool/Spyglass_Zoom_Wield` uses the flag. New Creative entry 0.5 s +100%. Full from 0 in **20 s**.
- `Stamina.json`: only `UseIgnoreFlag` on its two `Wielding` conditions. `Health.json`: identical.
- Charged-cast interactions: identical. 22 of the 23 staff items that had it dropped the dead `Staff_Cast_Summon_Charged` var.
  `Weapon_Staff_Thorium` kept it and the new `Weapon_Staff_Scrap_Lightbulb` has it (1.2). New Rune ability
  `Ability_ChargedShot` costs 10 / 20 / 30 / 50 Mana (check = drain).
- **Effect on our mods:** SkyySkills' base Mana is posted as `max(0, classBase - typeMax)`, so with type max 100 the whole "Base Mana
  by class" table does nothing (everyone has 100). With costs / 5, 100 Mana = 20 wand casts. On 0.7 we either keep vanilla costs or
  override `Mana.json`'s Max. This goes into `research/PreRelease-Compat-Report.md` when 0.7 lands.

---

## 3. Our Mana sources today (live set + planned)

| Mod / source | What it gives | How it is applied | In / out of combat |
|---|---|---|---|
| SkyySkills 0.4.8 Base Mana | max Mana = class table (Mage 30, Priest 30), others `mana.base` 10 | `StaticModifier(MAX, ADDITIVE)` key `skyyskill_basemana` = `max(0, base - typeMax)`, `Perks.tick` every 1 s. Current Mana is never written | max only, always |
| SkyySkills Overall Level | +0.2 max Mana per Overall Level (+20 at 100) | key `skyyskill_overallmana`, same tick. `healOnLevelUp` heals Health only | max only |
| SkyySkills per-skill perks | `perk.<skill>.manaPerLevel`: Alchemy 0.2 (+20 at 100), all others 0 (admin can set any) | key `skyyskill_mana` | max only |
| SkyySkills Alchemy duration perk | longer potion effects. Mana potions are decorative in vanilla, so no Mana effect today | EffectControllerComponent | - |
| SkyySkills ManaGuard | WARN / INFO only (uses the dead var numbers, 1.4) | - | - |
| **No Mana regen anywhere in SkyySkills** | | | |
| SkyyTrees 0.2.5 | **no Mana node** (only max Stamina / Health, speed, gathering) | - | - |
| SkyyGear 0.1 (live) | **Mana Steal** `msteal` (spell weapons, max 3 at full power): on a landed spell hit (damage > 0) you are owed `msteal` Mana, at most once per `steal.windowS` (3 s), paid by the next 1 s GearTick. So at most about **1 Mana per second** | `GearLeechSys` (Inspect) -> `GearFx.manaSteal` -> `GearFx.second` `add(Mana)` | **in combat only** (needs hits) - today the ONLY in-combat Mana source |
| SkyyGear armor lock | removes an under-level armor piece's own Mana (Silk etc.) | `skyygear_lock_<stat>` MAX modifier | max only |
| SkyyGear "Mana Regen" | **not in 0.1 / 0.1.1 / 0.1.2 at all**. Catalog: Equipment + accessories + magic-class trees ("Keep"); reforges Magical / Starter Magical / Arcane "flat mana and mana regen" | - | - |
| SkyyGear `hpr` / `stam` regen (for comparison) | flat Health / Stamina every `regen.periodMs` 2 s | `GearFx.second` | **ignores combat** (even while sprinting) |
| SkyyAccessories 0.4.5 Intelligence | +2 / 4 / 6 / 8 / 10 % of flat max Mana | key `skyyacc_mana`, `AccEffects.tick` 1 s | max only |
| SkyyAccessories Regeneration (for comparison) | Health % of max every 2 s | `addStatValue(Health)` | **ignores combat** ("out-of-combat-only Regeneration" is on the spec's wait list) |
| Booster spec 0.5 (`research/Booster-Accessories-Spec.md`) | Mana line +6 / 12 / 18 / 24 % of flat Mana (floor +1..+4), max only. **Mana Regen line = LATER** (4.2), planned as the Stamina Regen top-up (5.4.1) pointed at Mana | the top-up adds `pct` of vanilla's current regen rate, only while vanilla's own conditions pass | a %-of-vanilla top-up would be **out of combat only**, so **0 in combat** |
| SkyyClasses 0.1.9 Priest heal | **Health, not Mana**: a Priest's wand / spellbook hit heals party members within 16 blocks by 25 % of the damage (self 50 %), max 10 per hit / 10 per second | PriestHealSys (Inspect) | on hits (in combat by nature). Kits: Priest `Weapon_Wand_Wood` (gate 25 today), Mage `Weapon_Staff_Wood` (no gate today) |
| SkyyCooking 0.1.2 | no Mana food | - | - |
| Vanilla armor | Silk +60 (12 / 22 / 10 / 16), Cindercloth +64, Onyxium +80, Prisma +100 max Mana | engine armor modifiers | max only |

---

## 4. Balance

### 4.1 Casts per fight (simulated; base 30 Mana; non-stop casting for 30 s)

Cast cycle = hold time + the rest of the chain: wand 0.35 + 0.667 s, staff and spellbook 1.0 + 0.667 s, blunderbuss 2.0 + 0.25 s.
Vanilla regen ticks only outside the hold. With unlimited Mana, 30 s gives at most **30 wand / 18 staff / 18 spellbook / 13
blunderbuss** casts. "In combat" = hit at least every 6 s (vanilla regen 0 for the whole fight).

The **out-of-combat column is an estimate**. It depends on how a refused cast is modelled (how long the failed click takes and how
much regen falls into it). This simulator counts a refused cast as a full cycle. The 0.4.9 reviewer's separate simulator got **24 / 6
/ 3 / 4** for the four fixed rows, so read them as ranges. The in-combat column has no regen, so it is exact, and the reviewer
reproduced it. The regen-perk balance (4.2-4.4) uses only in-combat numbers.

| Weapon (gate / drain) | Out of combat, 30 s (estimate) | In combat, 30 s |
|---|---|---|
| Wand, **0.4.8 live** (25 / 5) | about 21 | **2** |
| Wand, fixed (5 / 5) | 24-25 (almost self-sustaining) | 6 |
| Staff, **0.4.8 live** (none / 10) | 18 (the cast-speed cap) | **18** (free at 0 Mana; costs Stamina and guard) |
| Staff, fixed (10 / 10) | 6-8 | 3 |
| Spellbook, 0.4.8 live (25 / 20) | about 4 | 1 |
| Spellbook, fixed (20 / 20) | 3-4 | 1 |
| Blunderbuss Rusty, **0.4.8 live** (50 / 10) | **0** | **0** |
| Blunderbuss Rusty, fixed (10 / 10) | 4 | 3 |

Spend rates while spamming: wand 4.9, staff 6.0, spellbook 12.0, blunderbuss 4.4 Mana per second. Vanilla regen while spamming out
of combat: wand 3.3, staff / spellbook 2.0, blunderbuss 0.6 per second.

### 4.2 What a flat in-combat trickle buys (in combat, 30 s, fixed costs)

| Mana Regen (flat, per 5 s) | Wand | Staff | Spellbook | Blunderbuss |
|---|---|---|---|---|
| 0 | 6 | 3 | 1 | 3 |
| +2 | 8 | 4 | 2 | 4 |
| +4 | 10 | 5 | 2 | 5 |
| +6 | 13 | 6 | 3 | 6 |
| +8 | 15 | 7 | 3 | 7 |
| +10 | 17 | 8 | 4 | 8 |
| +12 | 20 | 9 | 4 | 9 |
| +16 | 24 | 12 | 6 | 11 |

Pool 90 (Mage + Silk): +0 -> wand 18 / staff 9 / spellbook 4; +10 -> 29 / 14 / 7 (the wand is then capped by cast speed).

### 4.3 Percent of vanilla, or flat?

- **% of vanilla regen** (the 5.4.1 top-up pattern: `pct` of vanilla's rate, only while vanilla's conditions pass) respects the
  combat rule for free, and it can never make casting infinite. But it is **0 in combat**, where Mana matters. Out of combat vanilla
  already fills 30 in 6 s, so +20 % saves about 1 s. It only earns its place once pools pass about 100 (armor).
- **Flat "+N Mana every 5 s"** (Wynncraft's own unit for Mana Regen, which the catalog row copies) is the only kind that changes a
  fight. It is easy to read and easy to tune. Out of combat it is lost next to vanilla's 25 per 5 s, so it needs no combat check.
  Risk: stacked too high, casting becomes endless, so it needs a total cap.
- **Recommendation: flat per 5 s for every Mana Regen perk** (SkyyGear rolls and reforges, the booster Mana Regen line, magic-class
  tree nodes, a class-skill perk). It is on in and out of combat and also while charging; only alive, capped at max. One applier sums
  every source and clamps the total. Leave vanilla's 5 per second out-of-combat refill alone (no `Mana.json` override). A separate
  "Mana refill %" (out of combat only, the 5.4.1 pattern) can come later for big pools. The booster spec's planned "Mana Regen line =
  Stamina top-up pointed at Mana" should become the flat kind.

### 4.4 Placeholder numbers (Skyy tunes; all per 5 s, flat)

Target: typical endgame about **+10 per 5 s** (2 Mana per second, about 40 % of wand spam, 33 % of staff, 17 % of spellbook).
Mana Steal (up to about 1 per second) comes on top. The hard cap is **12 per 5 s**, with Mana Steal not counted.

| Source | Placeholder | Max from this source |
|---|---|---|
| SkyyGear Equipment roll "Mana Regen" (necklace, cloak, ring, belt; Equipment only per catalog) | max @100 % = **+1.5** per piece (low weight) | +6 |
| SkyyGear reforge Starter Magical / Magical / Arcane | +0.25 / +0.5 / +0.75 per piece ("flat mana and mana regen") | about +3 (4 armor pieces) |
| Booster accessory Mana Regen line (0.5 LATER), Normal / Unique / Rare / Legendary | **+0.5 / +1 / +1.5 / +2** | +2 |
| SkyyTrees magic-class node (Mage / Priest trees only, per catalog) | +0.5 per rank, 3 ranks | +1.5 |
| SkyySkills class-skill perk (`perk.<classSkill>.manaRegenPer5sPerLevel`) | 0.015 per level | +1.5 at level 100 |
| **Total cap** (`mana.regen.maxPer5s`) | **12** | |

What it feels like: a level-1 caster has +0 and gets 6 wand / 3 staff casts per fight (right for "a few shots at level 1"). Mid game
at about +4 gets 10 / 5. Endgame at +10 (and a bigger pool) gets 17 / 8 in a 30-s fight with no out-of-combat breaks.

### 4.5 Other balance levers to note

- **Vanilla cloth armor is now huge.** Silk +60 was worth 2.4 vanilla wand casts. With costs / 5 it is worth 12. If casters feel too
  strong with cloth armor, scale armor Mana / 5 too (same generated-override method), rather than cutting regen.
- If 3 staff casts per fight feels low for the Mage after the gate fix, raise the Mage's base Mana (Base Mana by class, e.g. 40-50)
  instead of lowering the staff cost below the drain.
- The 6 s no-damage delay is the real in-combat limiter. Overriding `Mana.json` (shorter delay or an in-combat entry) would hit every
  entity and clash on 0.7, so the flat applier is the safer knob.

---

## 5. UNVERIFIED (needs the game)

1. That the override of `Wand_Cast_Left_Charged` (and #2-#4) wins over vanilla for server and client. It is the same asset-pack
   mechanism as the 0.4.8 items. 0.4.8's pack check only looks at items, so the 0.4.9 check should also read
   `Interaction.getAssetMap()` for these ids.
2. Staff with #4: the charge -> StatsCondition -> Failed click works like the wand (Crystal_Red / Crystal_Ice need 10 Mana present,
   and so does the plain Blunderbuss behind #3).
3. Whether a cancelled or zero damage event also resets `lastDamageTime` (the system sits in the Inspect group; not traced).
4. Spellbook casts using up the book (inherited `ModifyInventory -1`, 1.3) - vanilla behaviour, not ours.
5. The cast-cycle timings in 4.1 are from the interaction RunTimes. Real client timing may differ slightly.

In-game check after 0.4.9: Priest with 30 Mana casts the Wood Wand 6 times in a row (30 -> 0), and the 7th clicks. Mage with the Wood
Staff casts 3 times, and the 4th clicks (if #4 is taken). A Rusty Blunderbuss fires at 10+ Mana. The plain Blunderbuss also needs
10+ Mana but spends none. Take a hit and watch the bar stop for
6 s. Hold a charge and watch it stop.

## 6. Files read

`Server/Entity/Stats/{Mana,Stamina,StaminaRegenDelay,Health,MagicCharges}.json` (both versions); `Server/Item/Interactions/Weapons/
{Wand,Staff,Spellbook,Gun}/**`, their `RootInteractions`, `Stamina_Broken_Check.json`; every caster item under `Server/Item/Items/
Weapon/{Wand,Staff,Spellbook,Gun}`; `Server/Entity/Effects/Mana/*`, `Effects/Stamina/Stamina_Broken*`, `Items/Potion/*Mana*`,
`NPC/Roles/**` caster roles; the live `SkyySkills.jar` asset list + JSON. Bytecode: `StatsConditionBaseInteraction`,
`StatsConditionInteraction`, `ReplaceInteraction`, `ChargingInteraction`, `ChangeStatInteraction`, `Interaction.getInteractionOrUnknown`,
`InteractionContext.defaultGetVars` / `getInteractionVars`, `RegeneratingValue`, `EntityStatType$Regenerating`, `RegeneratingModifier`,
`EntityStatsSystems$Regenerate`, `Condition`, `NoDamageTakenCondition`, `ChargingCondition` (+ its constructor default), `OutOfCombatCondition`,
`DamageSystems$TrackLastDamage`, `DamageSystems$RecordLastCombat`, `CombatConfig` (constructor: OutOfCombatDelay 5 s); pre-release
`ChargingCondition` / `WieldingCondition` / `ChargingInteraction` constant pools (`UseIgnoreFlag`). Scripts:
`SkyySkills/build_skyyskills_0.4.8.py` (SPELL GEN, ManaCost, Overall, perks), `tools/skills_0_4_8_patch.py` header,
`SkyyGear/build_skyygear_0.1.py` (STATS, GearFx, GearLeechSys), `SkyyAccessories/build_skyyaccessories_0.4.5.py`,
`SkyyClasses/build_skyyclasses_0.1.9.py` (kits, Priest heal), `SkyyTrees/build_skyytrees_0.2.5.py`, `SkyyCooking/build_skyycooking_0.1.2.py`,
`research/Booster-Accessories-Spec.md`, `research/Accessory-Pack-Inventory.md`, `research/Overall-Level-Spec.md`, `SkyyGear-Plan.md` /
`SkyyGear-Stat-Catalog.md` (read only).
