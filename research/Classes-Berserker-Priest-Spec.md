# Berserker, Priest and class kits: build spec (SkyyClasses 0.1.6, SkyySkills 0.4.4, SkyyProfiles 0.1.2)

*Written 2026-09-25 from Skyy's decisions of the same day (SkyWynn-Decisions.md "Change notes (2026-09-25)" 1-4, HANDOFF section 1
"Classes" row). Builds on the LIVE set (tools/deploy_set.py SET, live since 2026-09-25 04:11): SkyyClasses 0.1.5, SkyySkills 0.4.3,
SkyyProfiles 0.1.1. Every engine and asset fact below was checked on this machine (section 1 says how). Nothing here is built yet.*

Skyy's request, in their words: "we're bringing back berserker and adding a priest class. (make a kit per class you are automatically
given when you select the class that gives you the basic weapon of that class.)"

**LOCKED 2026-09-25 (Skyy), same voice call:**
- Priest heal numbers stay as written (25% of damage to party within 16 blocks; self-heal 50% of that; cap 10 HP per hit and 10 HP/s per player; party only) and are **TEMPORARY** until healing spells replace them.
- Divinity XP: healing others stays 0.2 XP per HP. Healing yourself pays **0.25 XP per HP** (was 0). Max 300 XP a minute unchanged. SkyySkills 0.4.5 still pays nothing for a self-heal.
- Heal chat lines stay on. Players can still turn theirs off. The rate cap is **every 10 s** (was 5 s). New files use `priestHeal.feedbackMs=10000`. A file already on 5000 keeps 5 s until that line is edited.
- The vanilla Healing Totem (AoE +5 HP/s, endgame recipe) is **Priest only** (was anyone). 0.1.6 still leaves every deployable unassigned.
- Root wands, Stoneskin wands, and the Rekindle Embers spellbook count as Priest weapons. That confirms the existing yes. No behavior change.
- The class kit drops **straight into the hotbar immediately** when a player selects or changes class. That replaces "into storage, about 31 s after a new profile arrives." What does not fit still waits on `/class kit`. 0.1.6 still uses storage and the 31 s wait.
- **To build:** a daily Archer arrow refill. Arrows only, once per day, so Archers do not have to craft every arrow. Not in 0.1.6.

---

## 0. Verdict (plain words)

- **Berserker** (weapon skill **Fury**) owns axes, battleaxes, maces and clubs: 62 vanilla items. Hatchets are `Tool_Hatchet_*`, not
  `Weapon_*`, so they stay free gathering tools for everyone with no extra rule.
- **Priest** (weapon skill **Divinity**) owns wands and spellbooks: 11 vanilla items. **None of them heals.** A wand is a fast melee
  swing (6 damage) plus a charged magic orb (25 damage) that needs 25 Mana; a spellbook is a weak swing (1) plus the same orb for 100
  Mana. Two wands (Root, Stoneskin) and one spellbook (Rekindle Embers) deal no damage at all. Vanilla players have **0 max Mana**, so a
  fresh Priest (or Mage) cannot cast; the melee swing works.
- **No wand and no spellbook can be crafted, and no wand drops from any monster** (one spellbook, Rekindle Embers, drops from a burnt
  skeleton). The Priest kit's Wood Wand is therefore the only vanilla way a Priest gets a weapon. That makes the kit essential, and
  "custom Priest weapons later" is a real need (open question Q7).
- **Priest placeholder heal (SkyyClasses):** when a Priest's wand or spellbook hit damages a monster, every party member within 16
  blocks of the Priest heals 25 % of that damage (the Priest themself 50 % of that), at most 10 HP per hit and 10 HP per second per
  player, never above max health. LOCKED 2026-09-25 as TEMPORARY until healing spells exist. It runs after the damage is applied
  (Inspect damage group), so it only ever heals for damage that really landed. The Healing Totem is a deployable and never triggers
  this heal: no double heal. LOCKED 2026-09-25: that totem is Priest only (0.1.6 still lets anyone throw it).
- **Divinity XP from healing (SkyySkills):** 0.2 XP per HP healed on OTHER party members, and LOCKED 2026-09-25 **0.25 XP per HP the
  Priest heals on themself** (was 0), at most 300 XP a minute for both together. Kills still pay Divinity like every class skill.
  0.4.5 still pays nothing for a self-heal.
- **Class kits (SkyyClasses):** every class has a kit (Server Setup rows, "Use my hotbar" like the island starter kit). LOCKED
  2026-09-25: it drops straight into the hotbar the moment the player selects or changes class. 0.1.6 still gives it once
  per profile, when the class is picked: SkyyProfiles' Create Profile tells SkyyClasses, SkyyClasses' own picker marks it itself. Existing
  profiles are marked "had a class before kits" at the first start, so nobody gets a surprise kit. Items go storage first; what does not
  fit waits as a claim (`/class kit`), never dropped on the ground.
- **SkyySkills save data is safe:** Fury and Divinity are two new storage slots APPENDED after Exploration (slots 14 and 15, keys
  `Combat.Berserker` / `Combat.Priest`). Every existing index and key stays. The catch: the class code assumes class slots are 5-9 in a
  row; 11 places must switch to a slot table (section 3.2), or Berserkers lose their perks (an array index crash inside a try).
- **SkyyProfiles 0.1.2:** the Create Profile page shows 7 class cards (5 playable + Assassin/Shaman greyed "coming later") with a one-line
  role each (Priest = "AoE healer / support"), on a bigger page (1000 x 900, fits 1080). 0.1.1 caps the picker at 6 cards: with SkyyClasses
  0.1.6 it would hide Priest. **Deploy the three together.**

---

## 1. Verified facts (engine + Assets.zip)

How: Assets.zip read with Python zipfile (scratch scripts under tools/dev/scratch/r6-classes, deleted afterwards);
tools/dev/reflect.py, bc.py, bcfull.py, clinit.py, cpgrep.py and callers.py on HytaleServer.jar. Existing live code patterns are cited by
script.

### 1.1 Weapon families (Server/Item/Items/Weapon/)

| Family | Ids | Count | Craftable | In drop tables |
|---|---|---|---|---|
| `Weapon_Axe_` | Adamantite, Bone, Cobalt, Copper, Crude, Doomed, Iron, Iron_Rusty, Mithril, Onyxium, Stone_Trork, Thorium, Tribal | 13 | 8 | Iron_Rusty |
| `Weapon_Battleaxe_` | Adamantite, Cobalt, Copper, Crude, Doomed, Iron, Mithril, Onyxium, Scarab, Scythe_Void, Steel_Rusty, Stone_Trork, Thorium, Tribal, Wood_Fence | 15 | 8 | 7 (Crude, Copper, Iron, Cobalt, Thorium, Steel_Rusty, Stone_Trork) |
| `Weapon_Mace_` | Adamantite, Cobalt, Copper, Crude, Iron, Mithril, Onyxium, Prisma, Scrap, Scrap_NPC, Stone_Trork, Thorium | 12 | 8 | 7 |
| `Weapon_Club_` | Adamantite, Cobalt, Copper, Crude, Doomed, Iron, Iron_Rusty, Mithril, Onyxium, Scrap, Steel_Flail_Rusty, Stone_Trork, Thorium, Tribal, 8 x Zombie arms/legs | 22 | 6 | Iron_Rusty |
| `Weapon_Wand_` | Root, Stoneskin, Tribal, Wood, Wood_Rotten | 5 | **0** | **none** |
| `Weapon_Spellbook_` | Demon, Fire, Frost, Grimoire_Brown, Grimoire_Purple, Rekindle_Embers | 6 | **0** | Rekindle_Embers only (Drop_Skeleton_Burnt_Praetorian) |
| `Tool_Hatchet_` | Adamantite, Cobalt, Copper, Crude, Iron, Mithril, Onyxium, Thorium, Wood | 9 | - | - |

Under the new rule table (section 2.1) the build will print: Archer 26, Warrior 58, Mage 25, **Berserker 62, Priest 11**, Assassin 17,
Shaman 0, unassigned 22 (bombs, guns, grenades, darts, claws, blowgun, flamethrower, the three deployables incl. both totems, 2 test rifles).
Today (0.1.5) the 62 Berserker items fall into the `Weapon_` catch-all and the 11 Priest items too: blocked for everyone with a class.

### 1.2 What wands and spellbooks do

| Item | Tap (melee) | Hold (cast) | Mana | Heals? |
|---|---|---|---|---|
| Wand Wood / Tribal / Wood_Rotten | `Wand_Primary` (Charging) -> `Sword_Swing_Left/Right_Fast`, `DamageEntityParent`, **Physical 6** per swing (~0.34 s a swing) | at 0.35 s `Wand_Cast_Left_Charged`: `StatsCondition` Costs Mana 25, `ChangeStat` Mana -25, `LaunchProjectile` **Skeleton_Mage_Corruption_Orb** (Damage 25, parent Staff_Wood_Rotten_Corruption_Orb: speed 30, gravity 0, 3.1 s) | 25 | no |
| Wand Root | none | `Root_Cast`: raycast, target gets Immunity +25 and the Root effect (plus a leftover debug `SendMessage "Adding stat!"`) | 0 | no, no damage |
| Wand Stoneskin | none | `Stoneskin_Cast`: raycast, target (else self) gets effect `Effects/Tests/Stoneskin` = 10 s tint + DisableSprint, no stat change | 0 | no, no damage |
| Spellbook Demon / Fire / Frost / Grimoire Brown / Purple | `Spellbook_Primary` -> `Block_Swing_*`, **Physical 1** | at 1 s `Spellbook_Cast_Hurl_Charged`, the item overrides Costs to **Mana 100**, launches the same orb (25) | 100 | no |
| Spellbook Rekindle Embers (Rare, MaxStack 5) | none | at 0.8 s: on up to 5 `Necromancy_Bones` blocks within 5, SpawnNPC Risen_Knight / Risen_Gunner, destroys the block, uses up 1 book | 0 | no (the risen fight as NPCs) |

Other facts that matter:
- Wands carry `"Utility": {"Compatible": true}`. Engine: the Utility slot only accepts `Usable` items (InventoryComponent$Utility
  ensureCapacity / afterDecode and InventoryUtils.getContainerForItemPickup call `ItemUtility.isUsable`); `Compatible` only means "a
  shield in the utility slot may take this main-hand item's Secondary" (InteractionContext.forInteraction: equal priorities + Secondary +
  main-hand `isCompatible` -> the off-hand slot). **So a wand or spellbook hit always comes from the main hand.** Spellbooks have no
  Utility block at all.
- The orb is a legacy `LaunchProjectile` shot: `ProjectileComponent.onProjectileHitEvent` (and `onProjectileDeath`) build
  `Damage$ProjectileSource(shooter, projectile)` (callers.py). SkyyClasses' ShotTrack already records these at launch (staves use the
  same path), so wand / spellbook orbs are attributed exactly like staff orbs today.
- **Mana:** `Server/Entity/Stats/Mana.json` InitialValue 0, Max 0 (regen +1 per 0.2 s after 6 s without damage, not while charging).
  Wand casts need 25, spellbooks 100, the Mage's Wood Staff summon 50. SkyySkills' Alchemy perk adds +0.2 max Mana per level; the
  SkyyAccessories Intelligence talisman is a percent of the flat max (0). A new Priest cannot cast (open question Q6).
- **Health:** players max 100, no survival regeneration (Health.json regenerates NPCs and creative players only). Heals matter.
- **The only vanilla heal "weapon":** `Weapon_Deployable_Healing_Totem` (Items.Debug category too): thrown deployable, effect
  `Healing_Totem_Heal` = +5 Health per 1 s tick in its area, 10 s cooldown, Arcanebench recipe (50 Life Essence, 20 Thorium bars,
  10 Greater Health potions). LOCKED 2026-09-25: Priest only. 0.1.6 still leaves it unassigned (anyone), because deployables are not
  judged by the class lock and the totem acts as its own entity. It never triggers the Priest weapon-hit heal, so there is no double heal.

### 1.3 Kit items (all exist in Assets.zip)

| Class | Default kit | Notes |
|---|---|---|
| Archer | `Weapon_Shortbow_Crude:1, Weapon_Arrow_Crude:64` | bow durability 80, craftable; arrows MaxStack 100, craftable (4 sticks + 1 rubble = 4) |
| Warrior | `Weapon_Sword_Crude:1` | durability 80, craftable (Fieldcraft) |
| Mage | `Weapon_Staff_Wood:1` | no durability, NOT craftable |
| Berserker | `Weapon_Battleaxe_Crude:1` | durability 80, Workbench recipe, also drops |
| Priest | `Weapon_Wand_Wood:1` | no durability, NOT craftable, drops nowhere |
| Assassin (later) | `Weapon_Daggers_Crude:1` | defined now, used once Assassin is enabled |
| Shaman (later) | empty | gets a custom weapon later (change note 4) |

### 1.4 Engine calls used (all verified)

| Need | Call | Evidence |
|---|---|---|
| after the damage is applied | `DamageModule.getInspectDamageGroup()` | reflect.py; `DamageSystems$ApplyDamage` clinit: AFTER gather, AFTER filter, BEFORE inspect; ApplyDamage cancels on a dead target, `setAmount(Math.round(amount))`, `EntityStatMap.subtractStatValue(health, amount)`. SkyySkills 0.4 `AcroFallSeenSys` uses the same group |
| add health | `EntityStatMap.addStatValue(int, float)`, `DefaultEntityStatTypes.getHealth()`, `EntityStatValue.get()/getMax()` | reflect.py; SkyyAccessories 0.4.4 `AccEffects` Regeneration (clamp to max - now, skip now <= 0) |
| party | bridge `party:fn:members` apply(UUID) -> String[] (leader first, self included; empty when not in a party) | SkyyParty 0.1.4 docstring + `PartyFn`; SkyySkills 0.4.2 `PartyXp.members / one` pattern (same store, ready, alive, creative, radius) |
| give items | `Player.getInventory().getCombinedStorageHotbarBackpack()` (storage first), `ItemContainer.addItemStack(ItemStack)` -> `ItemStackTransaction.getRemainder()`; quantities above MaxStack fill several slots | reflect.py; SkyySacks 0.6.5 / SkyyProfiles 0.1 storage-first rule; SkyyIslands 0.5.2 comment "add / canAddItemStacks work in getMaxStack units" |
| read a hotbar | `Player.getInventory().getHotbar()`, `getCapacity()`, `getItemStack(short)` | SkyyIslands 0.5.2 `KitHotbarTask.hotbarText` |
| ready / creative | `Player.isWaitingForClientReady()`, `Player.getGameMode() == GameMode.Creative` | reflect.py; SkyySkills `SkillXp.creative` |
| NPC target | `com.hypixel.hytale.server.npc.entities.NPCEntity.getComponentType()` | reflect.py; SkyySkills `KillSys` |
| popup | `NotificationUtil.sendNotification(handler, title, body, ItemWithAllMetadata icon, NotificationStyle.Success)`; styles Default, Danger, Warning, Success | reflect.py; SkyyClasses 0.1.4 popup |

---

## 2. SkyyClasses 0.1.6 (from 0.1.5)

**Toolchain:** 0.1.5 was derived by `tools/classes_0_1_5_patch.py`. Write **`tools/classes_0_1_6_patch.py`** (anchor `rep()` style, derives
`SkyyClasses/build_skyyclasses_0.1.6.py` from 0.1.5) and a bare-JVM check **`SkyyClasses/test_skyyclasses_0.1.6.py`** copied from the
0.1.5 one (section 7.1). Built with `tools/skyycfg.py` kit 1.1: build only after the kit 1.1 / SkyyMenu 0.3.1 workflow has landed
(`python tools/skyycfg_test.py` green first).

### 2.1 Roster and weapon rules

`CLASSES` becomes (display order = list order; indices are never persisted: files store `class=<Name>` and `played=<names>`,
`ClassDefs.indexOf` matches names, the page payload `clspick<i>` is transient):

| # | name | skill | color | enabled | weapons (prefix, noun) | weapon_text | icons |
|---|---|---|---|---|---|---|---|
| 0 | Archer | Archery | #8fd67a | yes | unchanged | unchanged | unchanged |
| 1 | Warrior | Swordsmanship | #e0b060 | yes | unchanged | unchanged | unchanged |
| 2 | Mage | Sorcery | #7fb0e0 | yes | unchanged | unchanged | unchanged |
| 3 | **Berserker** | **Fury** | #d9443f | yes | `Weapon_Axe_` axes, `Weapon_Battleaxe_` battleaxes, `Weapon_Mace_` maces, `Weapon_Club_` clubs | Axes / Battleaxes / Maces / Clubs | Weapon_Battleaxe_Iron, Weapon_Axe_Iron, Weapon_Mace_Iron, Weapon_Club_Iron |
| 4 | **Priest** | **Divinity** | #f2e6a0 | yes | `Weapon_Wand_` wands, `Weapon_Spellbook_` spellbooks | Wands / Spellbooks | Weapon_Wand_Wood, Weapon_Spellbook_Grimoire_Brown, Weapon_Spellbook_Frost |
| 5 | Assassin | Assassination | #b58cff | no | unchanged | unchanged | unchanged |
| 6 | Shaman | Shaman skill | #ff7a5c | no | none | Custom weapon later | **Weapon_Deployable_Slowness_Totem** (was Weapon_Wand_Wood, now a Priest weapon) |

New `role` field (one line, shown on /class and in SkyyProfiles): Archer "Ranged damage", Warrior "Melee fighter", Mage "Magic damage",
Berserker "Heavy melee damage", Priest "AoE healer / support", Assassin "Fast burst damage", Shaman "Designed later".
Descriptions (UI text rule: no `, : ; { } " ' _ \`):
- Berserker: "Heavy melee fighter. Axes and battleaxes cleave - maces and clubs crush. Hatchets stay gathering tools for everyone."
- Priest: "AoE healer and support. Your wand and spellbook hits on monsters heal party members near you. Spells come later."
- Shaman: "Coming later. The fifth Wynncraft class - it gets its own custom weapon."

`FREE_WEAPONS` and `UNASSIGNED` are unchanged: the longest prefix wins, so `Weapon_Axe_` etc. beat the `Weapon_` catch-all. The existing
build checks (every prefix matches an item, icons of classes with weapons classify to that class, BAD_UI) cover the new rows. New build
check: every default kit id exists, and for an enabled class every kit item is free or that class's own weapon (section 2.3).

Texts that name the roster: `ClassCmd` description ("Open the class page - Archer, Warrior, Mage, Berserker, Priest (Assassin and Shaman
later)"), `AdminSetCmd` class arg help ("archer | warrior | mage | berserker | priest"), manifest description, the `unassignedBlocked`
row help and its CFG_LINES comment: "(bombs, guns, darts, claws, deployables...)" instead of "(axes, maces, bombs, guns, wands...)".
`class:list` becomes `Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity` (listText, enabled only);
`class:weapons:Berserker` = `Weapon_Battleaxe_,Weapon_Axe_,Weapon_Club_,Weapon_Mace_`, `class:weapons:Priest` = `Weapon_Spellbook_,Weapon_Wand_`.

### 2.2 Weapon lock, attribution and popup texts

`DamageLock` needs no logic change: the new rules flow through `ClassRules.allowed / blockText`. Texts players will see (chat
"[Classes] ..." + popup title "You can't use this weapon", body = the same line, icon = the weapon):
- "Only Berserkers can use axes. You are an Archer - /class shows your weapons." (also battleaxes / maces / clubs)
- "Only Priests can use wands. You are a Warrior - /class shows your weapons." (also spellbooks)
Hatchets are never judged (they match no rule = free).

Attribution today, and what the heal needs:
- Melee (wand swing, spellbook swing): `Damage$EntitySource` = the attacker; judged by the attacker's main hand at the hit
  (`InventoryComponent.getItemInHand`) + the active utility item.
- Legacy projectiles (staff, wand and spellbook orbs, throws, guns): `Damage$ProjectileSource(shooter, projectile)`, judged by the
  `ShotTrack` launch record (keyed by the projectile's UUIDComponent). Wand and spellbook orbs already take this path.
- New-style projectiles (arrows, kunai): hands at landing + the `liveBad` window. Not Priest weapons.

**Change:** `ShotRec` gains `public String item;` = the main-hand item id at launch (null when empty), recorded for every tracked shot,
not only forbidden ones (`ShotTrack.onEntityAdded`: `item = idOf(InventoryComponent.getItemInHand(buf, sh))`, constructor gets the extra
argument). The lock keeps using `bad` / `util`; the heal uses `item`.

### 2.3 Class kits

LOCKED 2026-09-25 (Skyy) replaces the delivery below. When a player selects or changes class, the kit drops straight into the hotbar
immediately. 0.1.6 still writes it to storage about 31 s after a new profile arrives. What does not fit still waits on `/class kit`.

**Daily Archer arrow refill (to build, not in 0.1.6).** Arrows only, claimable once per day, so an Archer does not have to craft every
arrow. Separate from the one-time class kit (that kit still includes 64 arrows).

**Where the contents live:** `Skyy_SkyyClasses/config.properties`, one line per class (`kit.<Class>=id:amount,id:amount`, at most 9
stacks), edited in Server Setup (section 2.5) or by hand + `/classadmin reload`. Fields `KitCfg.K_<CLASS>` (public static volatile
String) parsed at use time like SkyyIslands' `IslandCfg.kitOf` (bad entries skipped with one warning; amount 1-9999).

**Kit state per profile** in the class file `players/<pkey>.properties` (written through ClassStore's atomic `saveKey`, so every other
key is kept):

| `kit=` | Meaning |
|---|---|
| (absent) | no decision yet |
| `pending` | a class was just picked: give the kit when the rules below allow |
| `given` | handed out (`kitGivenAt=<ms>`, `kitClass=<Class>`) |
| `owed` | handed out, but `kitOwed=id:qty,...` did not fit and waits as a claim |
| `old` | the profile had a class before class kits existed (0.1.6 migration): never automatic |
| `off` | picked while `kits.enabled` was off: never automatic |

**When a kit becomes pending** (only from an absent flag; any other state is left alone, so a profile gets at most one automatic kit):
1. **SkyyProfiles Create Profile** calls the new bridge function `class:fn:kitnew` right after the profile is created (section 4.3).
2. **SkyyClasses' own picker** (no SkyyProfiles): `ClassStore.setClassKey` sets `kit=pending` in the SAME write as the class when the file
   had no class and no kit flag (first choice, and `/classadmin set` on a classless file).
3. Never on `syncKey` (profile class copied into a file), `/profileadmin setclass`, `/classadmin reset` + a new choice after an `old` /
   `given` flag, or a class the profile already had.

`class:fn:kitnew` = `Function apply(Object[] { UUID player, String pkey, String className })` -> `Boolean`:
TRUE = recorded (`pending`, or `off` while kits are off) or the profile already has a kit state; FALSE = bad arguments, or that class
file cannot be read / written. Runs on the caller's thread (SkyyProfiles' world thread): one synchronized `ClassStore.markKitKey(k, cls)`
(loadKey, refuse an unread file, set `kit`, `kitClass`, `kitAt`, saveKey), no call into another mod (the pkey comes in as an argument),
then `KITQ.put(k, uuid)` and one chat line to the player if online: "[Classes] Your Priest kit is on its way - it lands in your inventory
shortly after the switch." Never throws.

**Migration (first start of 0.1.6), `KitMigrate.runOnce()` in `setup()` right after `ClassStore.DIR` is set:** if
`Skyy_SkyyClasses/kits.properties` is missing, scan `players/*.properties`; every file with a `class=` and no `kit=` gets `kit=old`
(read and written directly, not through the DATA cache, so a big server does not load every file into memory). Then write
`kits.properties` (`migratedAt`, `marked`, `version=0.1.6`) and log "class kits: N existing profiles marked as picked before kits - they
get no automatic kit". A failure logs a warning and leaves kits.properties unwritten (the next start retries; marking is idempotent).
Why it matters even with explicit triggers: a player whose class was reset by an admin and who picks again must not get a surprise kit.
Profiles that exist only in SkyyProfiles (no class file yet) are never pending either, because nothing calls `kitnew` for them.

**Delivery rules (all must hold):** `kits.enabled` on; the player online; `pkey(u)` = the pending key (kits belong to their profile);
`profile:busy:<uuid>` absent; the profile's class is known and playable; with SkyyProfiles, at least 31 s since the last
`profile:epoch` change SkyyClasses saw for that player (new map `KITEP`: UUID -> {epoch, seenAtMs}; the first sight after a join counts
as a change, which also covers a crash recovery at join. SkyyProfiles keeps its crash marker 30 s: a crash in that window rolls a new
profile back to its EMPTY snapshot and would eat the kit); the player has been in the same world for >= 3 s (so the `/island` transfer
right after a switch is over); on the world thread: valid ref, `Player` component, not `isWaitingForClientReady()`, health > 0.
Without SkyyProfiles (own picker) there is no epoch wait: `ClassPage` delivers at once on its world thread after "Confirm".

**Loop:** `ClassTick` (2 s, scheduler) no longer returns early without SkyyProfiles: it runs `Kit.tick()` first (returns at once while
`KITQ` is empty), then the 0.1.3 epoch check only when `profilesOn()`. `Kit.tick` iterates online players whose pkey is in `KITQ` with state
`pending`, applies the scheduler-side rules and hands a `KitTask` to the player's world (`w.execute`), which re-checks everything there.
`KITQ` (pkey -> state String `pending` / `owed`; the owner UUID is the first 36 characters of the pkey) is filled by `kitnew`, by
setClassKey and by `loadKey` when a file it reads says `pending` / `owed`, so the event and tick paths never read files.

**Give (world thread, `Kit.give`), crash-safe order (a lost kit is recoverable by an admin, a duplicated one is not):**
1. `ClassStore.kitBegin(k, cls, list)`: write `kit=given`, `kitClass`, `kitGivenAt`, `kitOwed=<the whole list>`. A failed write stops here
   (retried next tick).
2. For each stack: `new ItemStack(id, qty)` (unknown id: skipped + one warning) -> `getCombinedStorageHotbarBackpack().addItemStack(...)`;
   keep `getRemainder()`.
3. `ClassStore.kitEnd(k, remainder)`: no remainder -> remove `kitOwed`, `KITQ.remove(k)`; else `kit=owed`, `kitOwed=<remainder>`.
4. Messages (never toggleable: onboarding, like the SkyWynn Menu item): popup (NotificationStyle.Success, title "Class kit", body "Priest
   kit - Wand Wood", icon = the first kit item) and chat "[Classes] Your Priest kit is in your inventory: Wand Wood x1." Item names are the
   id without `Weapon_` / `_` (the SkyySkills `weaponsText` style). With a remainder: "[Classes] 14 items of your Archer kit did not fit -
   make room, then type /class kit to collect them."

**Overflow = a claim, not the ground.** Justification: a switched-to profile starts with an EMPTY inventory, so overflow is rare (it
happens on profile 1 created from a full inventory, or the own picker); dropping in the hub or on a void island can lose items or let
others take them; the claim is the rule of SkyyEssentials `/trade claim` and SkyyAuctions `/ah claim`. Owed items are retried at every
world arrival (`ClassReady`, before the once-per-session check, schedules a `KitTask` 3 s later when that profile has `kit=owed`) and by
`/class kit`. They are never retried by the 2 s tick (no per-tick world hops for a full inventory).

**Commands** (HANDOFF command rules; lint `perm_group_leaks`):
- `/class kit` (player subcommand of `/class`, `setPermissionGroups(new String[] { "hytale:Adventurer" })`): collects owed kit items of
  the active profile; with nothing owed it answers "Nothing is waiting. Your Priest kit (Wand Wood x1) was given on 2026-09-25."
- `/classadmin kit <player|uuid> [class]` (`requirePermission("skyyclasses.admin")` + `setPermissionGroups(new String[0])`): gives the
  kit of `[class]` (default: the target's current class; disabled classes allowed for testing, empty kits refused with where to edit
  them) to an ONLINE target now, ignoring the flag, on the target's world thread; the remainder becomes a claim on the target's active
  profile; a `pending` / absent flag becomes `given`. Replies to both players, logs one INFO line. Add `kit` to `ClassAdminCmd`'s usage.
  (lint `ADMIN_ONLY_OK` does not need `kit`: the constructor carries its own groups.)
- `/classadmin info` appends the kit state ("kit given 2026-09-25 (Priest)", "kit pending", "kit owed: Weapon_Arrow_Crude x14", "kit - class
  picked before kits").

### 2.4 Priest placeholder heal

**System:** new class `PriestHealSys extends DamageEventSystem` (one `registerSystem`), group `getInspectDamageGroup()`, `Query.any()`
(the NPC component type is read inside, like SkyySkills KillSys, so registration never depends on the NPC module's init order).

**Trigger (all must hold), in `handle`:** `priestHeal.enabled`; the Damage is not cancelled and `getAmount() >= 1` (ApplyDamage rounded
and applied it); the target has `NPCEntity` and no `PlayerRef` (**no PvP**); the attacker is a player: `ProjectileSource` -> `ShotTrack.find`
record -> shooter + `rec.item` (no record: the shooter's current main hand), else `EntitySource` -> attacker ref -> `PlayerRef` + main-hand
id; `ClassStore.classIndex(u)` is Priest and enabled; `ClassDefs.ownerOf(item)` is Priest (wand or spellbook); the attacker is not in
creative (their `Player` component, read with the command buffer). Then `dealt = d.getAmount()` (after armor, filters and the SkyySkills
class damage perk; overkill is included, the per-hit cap bounds it) and `world.execute(new HealTask(u, dealt, worldName))`. No stat write
inside the damage dispatch. Effect ticks (DoT) with the Priest as source count only if the Priest holds a Priest weapon at that moment -
same rule as melee, fine for a placeholder.

**HealTask (same world thread, next task):**
1. Priest `PlayerRef` valid, still in that world (ref store = this world's store), alive, not creative. Priest position = TransformComponent.
2. Targets = `party:fn:members(priest)` (String[]; empty or no SkyyParty = the Priest alone). For each: online, `ref.getStore() == store`
   (same world), not waiting for client ready, alive (health > 0), not creative, within `priestHeal.radius` of the PRIEST.
3. Amount per target: `want = min(dealt x sharePercent / 100, maxPerHit)`; the Priest themself: `want x selfPercent / 100`.
4. Per-target budget: `HealBudget.take(targetUuid, want, now)` (synchronized, one call): a fixed 1 s window per target, `maxPerSecond` for
   ALL Priests together.
5. Overheal ignored: `heal = min(budget, max - now)`; skip when <= 0.01. Then `m.addStatValue(DefaultEntityStatTypes.getHealth(), heal)`
   on `store.getComponent(ref, EntityStatMap.getComponentType())` (the SkyyAccessories Regeneration call).
6. `others` = sum healed on targets other than the Priest. If > 0: bridge `skill:fn:healxp` apply(Object[] { priestUuid,
   Double others, "classes:heal", ClassCfg.pkey(priestUuid) }) (absent = SkyySkills older than 0.4.4 = no XP, no error).
7. Feed the chat aggregator (below).

**Why the Priest is included (at 50 %):** Skyy wants the pack 100 % usable solo; a solo Priest (or a Priest not in a party) would
otherwise get nothing from their class on weak weapons. Wynncraft's healers heal themselves in their AoE too. The factor keeps the Priest
from being a lifesteal tank. LOCKED 2026-09-25: a self-heal pays 0.25 Divinity XP per HP (healing others stays 0.2). 0.4.5 still pays
nothing for a self-heal. The 300 XP a minute cap covers both.

**Feedback (chat, aggregated; admin master switch + two player Settings switches):**
- Priest, key `classes.healGiven`: at most one line every `priestHeal.feedbackMs` (LOCKED 2026-09-25: 10 s, was 5 s): "[Classes] Heals: +23 HP to your party (2
  players) and +6 HP to you" (only the parts that are > 0; "+6 HP to you" alone when solo).
- Healed member, key `classes.healTaken`: "[Classes] Skyy healed you +12 HP" ("Priests healed you +12 HP" with several healers).
- Flushed by `ClassTick` (`HealMsg.flushDue`), gated like Settings-Spec 1.3: `ClassCfg.HEAL_MSG` AND `notifyOn(u, key)`, checked before the
  line's own timestamp. The heal itself always happens. A popup was considered and rejected: a toast every 10 s in a fight is too loud.
- `setup()` registers (category `combat`): `classes.healGiven` "Priest heals - your heals" / "Your heals: +23 HP to 2 party members and
  +6 HP to you - one line every 10 s at most"; `classes.healTaken` "Priest heals - healed by others" / "Skyy healed you +12 HP - one line
  every 10 s at most. The heal happens either way".

### 2.5 Server Setup rows (config kit; file `Skyy_SkyyClasses/config.properties`, row key = file key)

Categories become `lock` "Weapon lock", `picker` "Class picker", **`kits` "Class kits"**, **`priest` "Priest heal"**. Existing rows unchanged
(help text of `unassignedBlocked` updated, section 2.1). Note (<= 100): "Players: /classadmin set, reset, info, kit <player>. Weapon rules
are code (rebuild)."

| Key | Label | Cat | Type | Default | Min-max | Opts / unit | Flags | Binding | Help (<= 100) |
|---|---|---|---|---|---|---|---|---|---|
| `kits.enabled` | Class kits | kits | bool | true | | | live,part,danger | field KitCfg.ON | Off: new classes get no kit. Kits still pending or owed wait until it is on again. |
| `kit.Archer` | Archer kit | kits | items | Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64 | 0-9 | qty | new | field KitCfg.K_ARCHER; check=KitHooks.checkKit | Given once when a profile picks this class (item:amount, at most 9 stacks). |
| `kit.Warrior` | Warrior kit | kits | items | Weapon_Sword_Crude:1 | 0-9 | qty | new | K_WARRIOR, same check | same |
| `kit.Mage` | Mage kit | kits | items | Weapon_Staff_Wood:1 | 0-9 | qty | new | K_MAGE | same |
| `kit.Berserker` | Berserker kit | kits | items | Weapon_Battleaxe_Crude:1 | 0-9 | qty | new | K_BERSERKER | same |
| `kit.Priest` | Priest kit | kits | items | Weapon_Wand_Wood:1 | 0-9 | qty | new | K_PRIEST | same |
| `kit.Assassin` | Assassin kit (coming later) | kits | items | Weapon_Daggers_Crude:1 | 0-9 | qty | new,adv | K_ASSASSIN | Used once Assassin is released. /classadmin kit can hand it out for testing. |
| `kit.Shaman` | Shaman kit (coming later) | kits | items | (empty) | 0-9 | qty | new,adv | K_SHAMAN | Empty until Shaman gets its custom weapon. |
| `kit.<Class>.fromHotbar` x7 | <Class> kit from my hotbar | kits | action | | | button "Use my hotbar" | new,danger (Assassin/Shaman + adv) | action:KitHooks.hb<Class> | Replaces the <Class> kit with what is in your 9 hotbar slots now (items and amounts). |
| `priestHeal.enabled` | Priest heal (placeholder) | priest | bool | true | | | live,part,danger | field ClassCfg.HEAL_ON | Off: Priest weapon hits heal nobody (and pay no Divinity heal XP). |
| `priestHeal.sharePercent` | Heal share of damage | priest | int | 25 | 0-500 | % | live | HEAL_SHARE_PCT | Party members near the Priest heal this % of the damage a Priest weapon hit did to a monster. |
| `priestHeal.selfPercent` | Priest heals self | priest | int | 50 | 0-100 | % | live | HEAL_SELF_PCT | The Priest heals this % of what one party member gets. 0 = never heals themself. |
| `priestHeal.radius` | Heal range | priest | dec | 16 | 1-64 | blocks | live | HEAL_RADIUS | Party members within this distance of the Priest are healed (same world only). |
| `priestHeal.maxPerHit` | Most HP per hit (each player) | priest | dec | 10 | 0.5-1000 | | live | HEAL_MAX_HIT | Cap for one hit and one player, before the per-second cap. |
| `priestHeal.maxPerSecond` | Most HP per second (each player) | priest | dec | 10 | 0.5-1000 | | live | HEAL_MAX_SEC | All Priest heals one player gets in one second, added up. |
| `priestHeal.messages` | Heal chat lines | priest | bool | true | | | live | HEAL_MSG | Off: no heal lines for anyone. Players can also hide theirs in /settings. |
| `priestHeal.feedbackMs` | Heal chat line interval | priest | int | 10000 | 1000-60000 | ms | live,adv | HEAL_MSG_MS | LOCKED 2026-09-25: at most one heal line per player this often (was 5000). A file already on 5000 keeps 5 s. |

Notes for the builder:
- One hook method per action row (`KitHooks.hbArcher(UUID who, String name)` ... `hbShaman`), each calling
  `hotbar(cls, who, name)` = SkyyIslands' `kitFromHotbar` + `KitHotbarTask` (admin's world thread, `hotbarText`, then
  `CfgFn.set("kit." + cls, text, who, name, "yes", "menu")`), answering "Reading your hotbar - the new <Class> kit is shown in the chat in a
  moment." Kit 1.1 value actions are not used (SkyyMenu 0.3 / 0.3.1 send no value).
- `KitHooks.checkKit(key, value)`: `null` fine; `?<question>` (the kit's confirm step) when an item is another class's weapon ("Weapon_Sword_Crude
  is a Warrior weapon - a Priest cannot fight with it. Save anyway?") or an unassigned weapon while `unassignedBlocked` is on.
- `ClassCfg.load()` (the kit's RELOAD) parses every new key with the row bounds as clamps; missing lines = the code defaults, so an
  existing config.properties keeps working untouched. `CFG_LINES` (written only when the file is missing) gains a commented "Class kits"
  block and a "Priest heal (placeholder until spells exist)" block with every default above; the build's default-vs-row check covers them.
- Unit rule: `HEAL_MSG_MS` is a long bound with unit `ms`, no scale. `KitCfg` and the heal fields must exist in the pool before `CFG.emit`.
- `/classadmin` (bare) and `ClassCfg.summary()` add `kits=on healShare=25% self=50% radius=16`.

### 2.6 /class page (fits 1080)

7 cards no longer fit 780 x 616 (7 x 92 + header/footer = ~790). New root **1000 x 900** (`PAGE_W, PAGE_H`), padding 16 / 14:
top bar 3, title 40 (22 pt bold), sub 28 (14 pt), 7 x (gap 6 + card 96) = 714, gap 8, info 26 (14 pt), confirm / footer 40
= 859 + 28 padding = 887 inside 900. Card: left 12, icons 4 x 56 (ItemIcon 48), text 548 (title 30 at 18 pt "Priest - AoE healer / support" or
"- your class" / "- coming soon"; line 2 22 at 14 pt bold "Combat skill Divinity - Wands / Spellbooks"; description 40 at 13 pt wrapped),
action 168 (button 160 x 40 at 15 pt). 952 of 968 px. Element ids unchanged (`#SkyyClsCard<i>` etc., no underscores).
The footer keeps "Shields and tools work for every class."; add "Hatchets are tools." to it.

### 2.7 Bridge (SkyyClasses publishes)

Unchanged keys keep their meaning, with the new classes: `class:<uuid>`, `class:skill:<uuid>` (Fury / Divinity), `class:list`,
`class:weapons:<Class>` (+ free, unassigned), `class:fn:allowed`, `class:fn:get`. **New:** `class:fn:kitnew` (section 2.3). Reads:
`party:fn:members`, `skill:fn:healxp`, `profile:*`, `settings:fn:*`, `config` kit keys.

### 2.8 setup() order

`ClassCfg.load` -> `KitMigrate.runOnce` -> bridge puts (incl. `class:fn:kitnew`) -> commands (`/class` with the `kit` subcommand,
`/classadmin` with `kit`) -> events (`ClassReady`, `ClassQuit`: also forget heal / kit maps) -> systems `ShotTrack`, `DamageLock`,
`PriestHealSys` (one registerSystem each) -> `ClassTick` -> `regSetting` x4 -> `CfgPub.start` last. `shutdown()` unchanged.

### 2.9 Build notes (javassist)

New classes, all top-level (no inner classes): `KitCfg` (fields + parse), `KitHooks` (check + 7 action hooks), `KitHotbarTask`, `KitMigrate`,
`Kit` (tick / consider / give helpers), `KitTask` (Runnable), `KitNewFn` (Function), `PriestHealSys` (DamageEventSystem), `HealTask`
(Runnable), `HealBudget`, `HealMsg`, `ClassKitCmd` (`/class kit`), `AdminKitCmd` (`/classadmin kit`). Add methods in dependency order
(helpers before callers, `ClassStore.markKitKey / kitBegin / kitEnd` before `Kit`), explicit arrays, no generics / lambdas / autoboxing /
enhanced-for / String switch; `KitCfg` and the heal fields exist before `CFG.emit`, the hooks may come after (contract). Probe every new
engine call with `B.probe` like 0.1.5 does (DamageModule.getInspectDamageGroup, EntityStatMap.addStatValue, DefaultEntityStatTypes.getHealth,
Inventory.getCombinedStorageHotbarBackpack / getHotbar, ItemContainer.addItemStack, ItemStackTransaction.getRemainder,
Player.isWaitingForClientReady / getGameMode / getInventory, NPCEntity.getComponentType, NotificationStyle.Success).

---

## 3. SkyySkills 0.4.4 (from 0.4.3)

**Toolchain:** `tools/skills_0_4_4_patch.py` derives `SkyySkills/build_skyyskills_0.4.4.py` from 0.4.3 (the 0.4.x patch chain; edit the
patch, never the generated file).

### 3.1 Two new slots, appended (saved data stays safe)

Player files store every slot by name (`<NAME>=<xp>`, `<NAME>.paid=<level>`) and `SkillStore.snap()` writes ONLY `SkillDefs.NAMES`, so a key
that is not in NAMES is dropped on the next save. Therefore:
- `SLOT_NAMES` += `"Combat.Berserker"` (slot 14), `"Combat.Priest"` (slot 15); `SLOT_LABELS` += `"Fury"`, `"Divinity"`; icons
  `Weapon_Battleaxe_Iron`, `Weapon_Wand_Wood` (both checked by `must()`); colors `#d9443f`, `#f2e6a0`. **N = 16**; the asserts become
  `== 16` and `SLOT_NAMES[10:14] == [Alchemy, Smithing, Cooking, Exploration]`, `SLOT_NAMES[14:] == ["Combat.Berserker", "Combat.Priest"]`.
- Slots 0-13 keep their index and key. The data array `long[2*N]` is in memory only (paid markers at N + slot); `SkillTop.AT / CACHE`,
  `BridgeCfg` boolean arrays are all sized by N already.
- The Shaman row icon changes to `Weapon_Deployable_Slowness_Totem` (the wand is Priest's now).
- Old `Combat.Berserker` lines from the SkyySkills 0.3 spike (2026-09-23): 0.3.1 renamed that slot to Shaman and every later save drops
  the key, so a file still holding one would have to be untouched since 0.3. If one exists, it becomes Fury XP. Accepted.
- **Downgrade rule:** never go back to SkyySkills 0.4.3 once 0.4.4 has saved Fury or Divinity XP (0.4.3's snap drops the two keys).

### 3.2 Class slots are no longer contiguous: the 11 sites to change

`CLASS_ROWS` gets `("Berserker", "Fury", ...)` and `("Priest", "Divinity", ...)`. `SkillDefs.CLASSES` = Archer, Warrior, Assassin, Shaman,
Mage, Berserker, Priest (keep this order: it is the slot order). Add `public static final int[] CLASS_SLOT = { 5, 6, 7, 8, 9, 14, 15 };` and:

```java
public static boolean isClass(int s) { for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return true; return false; }
public static int classIdx(int s)    { for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return i; return -1; }
public static int classSlot(int i)   { return i >= 0 && i < CLASS_SLOT.length ? CLASS_SLOT[i] : -1; }
```
(methods before callers; keep `CLASS0` / `CLASS_END` only if something else reads them - nothing may do arithmetic with them any more.)

| # | Where (0.4.3) | Today | Change |
|---|---|---|---|
| 1 | `SkillDefs.indexOf` (exact class name) | `return CLASS0 + i` | `return classSlot(i)` |
| 2 | `SkillDefs.indexOf` (3+ letter prefix) | `CLASS0 + i` | `classSlot(i)` |
| 3 | `SkillClass.slotOfClass` | `CLASS0 + i` | `classSlot(i)` |
| 4 | `SkillClass.skillName` | `s >= CLASS0 && s == slot(u)` | `isClass(s) && s == slot(u)` |
| 5 | `SkillClass.weaponOk` | `CLASSES[slot - CLASS0]` | `CLASSES[classIdx(slot)]` |
| 6 | `SkillClass.killSlot` (hint text) | `CLASSES[s - CLASS0]` | `CLASSES[classIdx(s)]` |
| 7 | `SkillStore.levelsOf` (skill:<uuid>) | `for s = CLASS0; s < CLASS_END` | loop over `CLASS_SLOT` |
| 8 | `SkillStore.moveLegacy` | same loop | loop over `CLASS_SLOT` (the legacy move needs ALL class slots at 0) |
| 9 | `Perks.tick` | `CLASSES[cs - CLASS0]` | `CLASSES[classIdx(cs)]` - **as is, a Berserker (cs 14) throws ArrayIndexOutOfBounds inside the try: no health / stamina / mana perks and no skill republish ("perk tick failed", logged once)** |
| 10 | `StatsPage.lines` (class damage line) | `CLASSES[s - CLASS0]` | `CLASSES[classIdx(s)]` |
| 11 | `StatsPage.how` and `StatsPage.build` ("You are not a ...") | `CLASSES[s - CLASS0]` (twice) | `CLASSES[classIdx(s)]` |

`perkRow` and every other `isClass` caller then work unchanged. Build assert: `SkillDefs.CLASSES` (Python list) has the same names as
SkyyClasses' roster and `len(CLASS_SLOT) == len(CLASS_ROWS)`.

Texts that list class skills (update all): `argSlot` unknown-skill message, the three `withRequiredArg("skill", ...)` helps of
/skills stats | top | xp, the /skills xp "You have no class" line, `how(COMBAT)` = "Your combat skill is your class skill - Archer Archery /
Warrior Swordsmanship / Mage Sorcery / Berserker Fury / Priest Divinity (Assassin and Shaman later)". Prefixes: "fur", "div", "ber",
"pri" resolve uniquely.

### 3.3 Combat XP, party share, perks: nothing new to write

With the slot table in place, everything class-based follows `class:<uuid>` exactly as for Archery today:
- **Kills:** `KillSys` -> `killSlot` -> `weaponOk` with `class:weapons:Berserker|Priest` (published by SkyyClasses 0.1.6); XP =
  `combat.*` (max health x 0.2, 1-500, roles table). A wand-orb kill is judged by the main hand at death (the staff rule).
- **Party share:** `PartyXp.share` pays other members into THEIR class slot (`slotFor` -> `SkillClass.slot`), so Berserkers and Priests
  give and get the 50 % share.
- **Perks:** the "combat" perk row (health per class level, `perk.combat.damagePerLevel` via `CombatDmgSys`) covers Fury and Divinity.
- **Guild XP:** follows the normal award path; see follow-up F1 for SkyyGuilds' skill list.

### 3.4 Divinity XP from healing (new)

Bridge **`skill:fn:healxp`** = `Function apply(Object[] { UUID healer, Number hpHealedOnOthers, String source [, String expectKey] })` ->
`Boolean` (TRUE = accepted / nothing to pay, FALSE = refused). `HealXp.offer`:
1. `divinity.healXp.enabled`, `hp > 0`, `SkillClass.slot(u) == 15` (Divinity) and `SkillClass.consistent(u)`, else FALSE.
2. `base = PartyXp.amount-style rounding of hp x divinity.healXpPerHp` (fraction paid by chance); 0 -> TRUE.
3. Own per-player ring (HWIN: 60 s window, `divinity.healXpMaxPerMinute`, 0 = no limit; not reset by a profile switch, like BridgeXp.WIN);
   over the cap -> FALSE (no log spam: one WARN per player per minute at most, BridgeXp.warnLimited style).
4. `BridgeXp.offer(u, 15, base, source, expectKey, null, 0, false)` >= 0 -> TRUE. That queues a `BridgeTask` on the player's world
   thread (profile key + creative re-check there), applies the xp multiplier and counts toward `bridge.maxXpPerMinute` like any bridge
   XP, and prints the normal "+2 Divinity XP" line (gated by `skills.xpGain`).
Never throws, no file I/O, any thread. Only SkyyClasses calls it ("classes:heal").

**Proposed defaults (marked for Skyy, Q2):** 0.2 XP per HP healed on others (a healed point is worth a damaged point: combat XP is monster
max health x 0.2), cap 300 XP a minute per Priest (normal support play stays well under it; it stops "friend stands in lava" farming).

### 3.5 Server Setup rows (xp.properties; `reload` binding like every 0.4.3 row)

| Key | Label | Cat | Type | Default | Min-max | Flags | Help |
|---|---|---|---|---|---|---|---|
| `divinity.healXp.enabled` | Divinity XP from healing | parts | bool | true | | live,part,danger | Off: Priest heals pay no Divinity XP (kills still do). Levels are kept. |
| `divinity.healXpPerHp` | Divinity XP per HP healed | combat | dec | 0.2 | 0-100 | live | XP per 1 HP a Priest heals on OTHER party members. LOCKED 2026-09-25: self-heals pay 0.25 XP per HP (0.4.5 still pays 0). |
| `divinity.healXpMaxPerMinute` | Divinity heal XP per minute | combat | int | 300 | 0-1000000000 | live | Most Divinity XP healing pays one Priest in 60 s (0 = no limit). Kills are not counted. |

Default xp.properties text gains a block `# ---------- Divinity (SkyySkills 0.4.4) - Priest heals from SkyyClasses 0.1.6 (skill:fn:healxp) ----------`
with the three lines; **`DivCfg.ensureDefaults`** appends it ONCE to an existing file without `divinity.healXp.enabled` (the
`PartyCfg.ensureDefaults` pattern, run inside `SkillCfg.load` before `CfgPub.start`). The build's row-default-vs-DEFAULTS assert covers it.
Fury and Divinity get no per-skill rows: `combat.*` and `perk.combat.*` already apply to every class skill.

### 3.6 Pages

- **/skills** (640 x 690, 9 rows) is unchanged: the class row already shows the ACTIVE class's skill (`rowSlot` -> `slot(u)`), so a
  Berserker sees "Fury" with the battleaxe icon, a Priest "Divinity" with the wand. No new row, still fits 1080.
- **Stats page** (960 x 795): Fury / Divinity show level, bar, class perks ("+X% damage with Berserker weapons (against monsters)"),
  next level, `how` = "Earn XP by defeating monsters with Priest weapons - Spellbook / Wand" + the party text. For slot 15 add one "Boosts right
  now" line while `DivCfg.ON`: "Healing party members pays 0.2 Divinity XP per HP (up to 300 a minute)"; while off: "Divinity XP from healing
  is off on this server". (A line, not the how-text: the how label is 45 px high and a longer text would overflow it.)

### 3.7 Bridge (SkyySkills publishes)

`skill:<uuid>` now carries `Fury:<lvl>` / `Divinity:<lvl>` for the current class skill or any class skill with XP; `skill:fn:level` and
`skill:fn:xp` answer "Fury", "Divinity", "Berserker", "Priest" and "Combat.Berserker" / "Combat.Priest" (all through `indexOf`); `Combat` still
means the current class skill. **New:** `skill:fn:healxp` (put in setup, removed in shutdown with the others).

---

## 4. SkyyProfiles 0.1.2 (from 0.1.1)

**Toolchain:** 0.1.1 was a copy + edit of 0.1 (no patch script). Start the chain now: **`tools/profiles_0_1_2_patch.py`** derives
`SkyyProfiles/build_skyyprofiles_0.1.2.py` from 0.1.1.

### 4.1 Roster (fallback table, used when SkyyClasses is absent; `class:list` decides what is playable when it is present)

Order and data: Archer, Warrior, Mage, **Berserker**, **Priest** (enabled), Assassin, Shaman (coming later). Name, skill, color, weapon_text,
description as SkyyClasses 2.1; icons 1-3 (Berserker: Battleaxe_Iron, Axe_Iron, Mace_Iron; Priest: Wand_Wood, Spellbook_Grimoire_Brown,
Spellbook_Frost; Shaman: Deployable_Slowness_Totem). New `role` field: Priest = **"AoE healer / support"**, others as 2.1. `ProfRoster` entries
grow to 8 fields (role at index 7); `roster()` keeps the 0.1.1 merge logic (extras from `class:list` get role "A class from SkyyClasses").
Mixed versions stay safe: with SkyyClasses 0.1.5 (no Berserker / Priest in `class:list`) both cards show greyed "coming later" and cannot be
picked.

### 4.2 Create Profile page (fits 1080)

0.1.1 draws at most 6 cards (`shown = r.size() < 6 ? r.size() : 6`) and handles `pfcls0..5`: with SkyyClasses 0.1.6 the roster has 7
entries and Priest would be invisible. Changes:
- `MAX_CARDS = 8` for drawing and for `handleDataEvent` (`i < MAX_CARDS`).
- One root size for BOTH views of `ProfilePage` (do not change the root size between rebuilds of one page): **1000 x 900**.
- Create view: top bar 2, title 36 (20 pt), name row 36, sub 34, 7 x (gap 4 + card 90) = 658, gap 8, make row 40, info 24 = 838 +
  padding 20. Card: left 8, icons 3 x 52, text 600 (title 24 at 16 pt "Priest" / "- selected" / "- coming later"; "Combat skill Divinity -
  Wands / Spellbooks" 18 at 12 pt bold; **role line** 18 at 12 pt in the class color "AoE healer / support"; description 26 at 11 pt wrapped),
  action 170. Greyed cards keep the grey colors and "Coming later".
- Sub text adds the kit: "Pick your class. It is locked to this profile forever. You get your class kit - its basic weapon - right after
  creating it." (first profile: "...Everything you already have stays on this first profile.")
- List view: same content, scaled ~1.2x (cards 76 high, fonts +2) to fill the bigger root. Element ids unchanged.

### 4.3 Telling SkyyClasses a class was picked

New `ProfKit.kitNew(UUID u, String key, String cls)`: looks up `class:fn:kitnew`, calls it with `Object[] { u, key, cls }`, logs one WARN
(once per JVM) when it answers anything but TRUE or throws; missing function = SkyyClasses absent = nothing. Called **outside every
SkyyProfiles monitor** (after `ProfStore.create` and `publish` returned):
- `createFirst`: after the create + publish, key = `u.toString()` (profile 1).
- `createAndSwitch`: after the create + publish and BEFORE `switchTo`, key = `ProfStore.keyFor(u, id)`. Before, so a failed switch still
  leaves the kit pending for the day the player switches to that profile; SkyyClasses only delivers to the ACTIVE key, after busy clears and
  31 s after the epoch change.
- Not called by `/profileadmin setclass` (a fix, not a pick; an admin uses `/classadmin kit`).

### 4.4 Texts

`/profileadmin setclass` class arg help "archer | warrior | mage | berserker | priest (assassin, shaman later)"; manifest description names
the five classes. `profile:class:<uuid>` values: `Archer`, `Warrior`, `Mage`, `Berserker`, `Priest` (later `Assassin`, `Shaman`), exactly as
tools/PROFILES-CONTRACT.md already lists. No new config rows, no new Settings switch, players files unchanged.

---

## 5. Contracts between the three mods

| Key | Type / call | Publisher | Readers | Thread / rules |
|---|---|---|---|---|
| `class:<uuid>`, `class:skill:<uuid>` | String (+ Berserker/Fury, Priest/Divinity) | SkyyClasses | SkyySkills | unchanged |
| `class:weapons:Berserker`, `class:weapons:Priest` | String prefix lists | SkyyClasses | SkyySkills (`weaponOk`, `weaponsText`) | setup |
| `class:list` | String, 5 entries | SkyyClasses | SkyyProfiles roster | setup |
| `class:fn:kitnew` | apply(Object[]{UUID, String pkey, String cls}) -> Boolean | SkyyClasses (setup, never removed) | SkyyProfiles 0.1.2 | caller's thread; synchronous small file write under ClassStore's lock; never calls another mod; never throws |
| `skill:fn:healxp` | apply(Object[]{UUID, Number hp, String source [, String expectKey]}) -> Boolean | SkyySkills (setup; removed in shutdown) | SkyyClasses 0.1.6 | any thread; no I/O; queues on the player's world thread |
| `party:fn:members` | apply(UUID) -> String[] | SkyyParty | SkyyClasses (heal), SkyySkills (share) | world thread callers |
| `profile:class:<uuid>`, `profile:epoch:<uuid>`, `profile:busy:<uuid>`, `profile:fn:key` | contract v1 | SkyyProfiles | SkyyClasses (kit rules), SkyySkills | unchanged |
| `settings:def:classes.healGiven` / `classes.healTaken` | Settings registry | SkyyClasses | SkyyMenu 0.2+ | setup |
| `config:def|fn|epoch:SkyyClasses`, `...:SkyySkills` | config kit | each mod | SkyyMenu 0.3+ | new rows only |

**Load order:** none needed. Every cross-mod value is looked up at call time, and every key is put in `setup()` and never removed while
the server runs (skill functions are removed only in shutdown, when nothing calls them).

**Mixed versions (what happens if only some are deployed):**

| Combination | Result |
|---|---|
| Classes 0.1.6 + Skills 0.4.3 | Berserker/Priest fight; SkyySkills tells them once "Your class Berserker has no combat skill in SkyySkills yet"; no Fury/Divinity XP, no class perks; heals work, `skill:fn:healxp` absent = no XP. Safe. |
| Classes 0.1.5 + Skills 0.4.4 | Fury/Divinity slots stay empty; `skill:fn:healxp` never called. Safe. |
| Classes 0.1.6 + Profiles 0.1.1 | Berserker appears as a generic extra card (sword icon, "A class from SkyyClasses"), **Priest is hidden** (6-card cap), no `kitnew` call = no automatic kit on new profiles. Works, wrong. |
| Classes 0.1.5 + Profiles 0.1.2 | Berserker/Priest cards greyed "coming later" (not in class:list). Safe. |
| All three new | intended. |

**Deploy as one round:** pin SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2 together in tools/deploy_set.py (coordinator), after
the kit 1.1 / SkyyMenu 0.3.1 round. Add to the SET comment: never go back to SkyySkills 0.4.3 once Fury/Divinity XP exists.

---

## 6. Migration and data

| Mod | On disk | What happens |
|---|---|---|
| SkyyClasses | `config.properties` | untouched; new keys read their code defaults until changed in game (then the kit adds one line each, line-preserving). New installs get the full default text. |
| SkyyClasses | `players/<pkey>.properties` | first start: files with a class and no kit flag get `kit=old`; new keys `kit`, `kitClass`, `kitAt`, `kitGivenAt`, `kitOwed` later. 0.1.5's `putAll` copies keep them on a downgrade. |
| SkyyClasses | `kits.properties` (new) | written once by the migration. |
| SkyySkills | `players/<pkey>.properties` | gain `Combat.Berserker` / `Combat.Priest` (+ `.paid`) on the next save (0 for everyone). |
| SkyySkills | `xp.properties` | the Divinity block is appended once. |
| SkyyProfiles | nothing | new class names only. |

Existing profiles keep their class and get no kit. Skyy's test profiles (Strawberry = Archer, Zucchini = Warrior) are marked `old`.
Downgrades: SkyySkills 0.4.3 = loses Fury/Divinity XP (forbidden); SkyyClasses 0.1.5 = Berserker/Priest profiles become classless there
(any weapon, no XP) until 0.1.6 is back; SkyyProfiles 0.1.1 = Priest hidden in the picker.

---

## 7. Test plan

### 7.1 Static and bare JVM (before any deploy)

- `python tools/classes_0_1_6_patch.py`, `python tools/skills_0_4_4_patch.py`, `python tools/profiles_0_1_2_patch.py`, then each build
  with plain python: must end "assembled ...jar". Build prints: Berserker 62, Priest 11, unassigned 22; config kit row counts
  (Classes: 5 + 15 kit rows + 8 heal rows = 28, Skills: 151 + 3 = 154).
- `python tools/ci/lint.py`: 0 fails (perm_group_leaks: `/class kit` Adventurer, `/classadmin kit` cleared groups).
- `SkyyClasses/test_skyyclasses_0.1.6.py` (copy of 0.1.5's harness, scratch under tools/dev/scratch/r6-skyyclasses, TEMP/TMP there,
  deleted after): A-K as in 0.1.5 with 0.1.5 defaults as the baseline, plus: L kit parse (bad entries, 9999, unknown id); M `kitnew`
  state table (absent -> pending, old/given/off/owed unchanged, kits off -> off, unreadable file -> FALSE, never throws); N migration
  (files with class -> old, without class untouched, second start no-op, kits.properties); O `setClassKey` first choice -> pending, admin
  set on a classless file -> pending, choice after reset of an `old` file -> stays old; P heal math as pure functions (share, self %, per-hit
  cap, 1 s budget across two Priests, overheal clamp, others sum); Q `checkKit` questions; R setup order (KitMigrate before bridge puts,
  CfgPub.start last), 4 settings registered; S permissions with the engine's AbstractCommand code: `/class kit` in Adventurer, `/classadmin`
  node in no group.
- SkyySkills bare-JVM harness (the 0.4.3 style, scratch r6-skyyskills): all classes under -Xverify:all; a 0.4.3 player file loads with
  Fury/Divinity 0 and saves every old key + the two new ones; `indexOf` fury/divinity/berserker/priest/"pri"; `levelsOf` with a Priest;
  `moveLegacy` refuses when slot 14 has XP; `Perks.tick` path for slot 14 (no exception); `healxp` (not Priest -> FALSE, cap, rounding,
  part off); DivCfg.ensureDefaults appends once; row defaults vs DEFAULTS.
- SkyyProfiles: roster with a fake `class:list` (0.1.5 list -> Berserker/Priest greyed; 0.1.6 list -> all five playable); create-page markup
  has 7 cards, unique ids without underscores, content <= 880 px; `kitNew` with a fake function (called after create, before switch, with
  the right key; absent function = no call).

### 7.2 In game, solo (Skyy)

1. Server log: all ready lines; SkyyClasses "class kits: N existing profiles marked"; no config-kit warnings. Existing profiles: no kit.
2. `/profiles` -> Create new: 7 cards fit on screen, Priest card says "AoE healer / support", Assassin/Shaman greyed. Create a Priest.
   After the switch and island arrival, within ~35 s: popup "Class kit" + chat "Your Priest kit is in your inventory: Wand Wood x1"; the
   wand is in storage. `/classadmin info <you>` = kit given.
3. `/class` on that profile: 7 cards, read-only, fits. Stats: `/skills` class row = Divinity with the wand icon.
4. Hit a monster with the wand (tap swings): damage lands, you heal (take some fall damage first), "[Classes] Heals: +N HP to you" at most
   every 10 s (LOCKED 2026-09-25, was 5 s); self-heal pays 0.25 Divinity XP per HP (0.4.5 still pays 0); kill -> "+N Divinity XP".
5. Swap to a sword: "Only Warriors can use swords" + popup, no damage, no heal. Hatchet chops logs and hits monsters (free).
6. Creative mode: hits heal nothing. Hit another player (if PvP on): no heal.
7. Create a Berserker profile: battleaxe kit; axes/maces/clubs deal damage; `/skills` shows Fury; `/skills stats fury` shows the class
   damage line; wands blocked ("Only Priests can use wands").
8. Server Setup -> Classes: tabs Weapon lock / Class picker / Class kits / Priest heal; edit the Priest kit (add a spellbook), "Use my
   hotbar" on the Archer kit (put a sword in the hotbar -> the Warrior-weapon question appears), set share to 50 %, part OFF (confirm) ->
   no heals; back ON. Server Setup -> Skills: Divinity rows present.
9. `/settings` -> Combat: the two heal switches hide their lines; heals still happen.
10. Full inventory test: `/classadmin kit <you> archer` with a full inventory -> "did not fit ... /class kit"; make room, `/class kit`.
11. Relog and restart: no second kit; owed items still claimable.

### 7.3 Two players (Skyy = Priest, friend = Warrior, the friend is NOT op)

1. Friend: `/class kit` works ("Nothing is waiting..."); `/classadmin kit`, `/classadmin info`, `/modconfig classes` refused / view only.
2. Party up (`/party invite`). Friend takes damage; Skyy hits a monster with the wand within 16 blocks: friend heals, sees "Skyy healed you
   +N HP" (<= every 10 s), Skyy sees "+N HP to your party (1 player)" and gets Divinity XP (~0.2 per HP on the friend, 0.25 per HP on Skyy once the next Skills build pays self-heals); friend at full health = no heal, no XP.
3. Friend walks 20+ blocks away or to another world: no heal. Friend leaves the party: no heal.
4. Two Priests (if a third account exists) on one hurt target: total heal per second never above 10 HP.
5. Party kill share still works both ways (Warrior kill -> Divinity share for Skyy; Priest kill -> Swordsmanship share for the friend).
6. Friend creates a new Berserker profile: gets the battleaxe kit on their own new island, not Skyy.

### 7.4 Only the game can prove

The Inspect-group system still finds the orb's `ShotTrack` record (the Filter-group lock relies on the same dispatch); `addStatValue` on
ANOTHER player from a `world.execute` task shows on their health bar and SkyyHud's party widget; the kit arriving after SkyyIslands' new-
island transfer; `NotificationStyle.Success` popups; both pages at 1000 x 900 on Skyy's client; a wand orb kill counted by SkyySkills
(hands at death).

---

## 8. Open questions for Skyy (each has a working default)

| # | Question | Default in this build |
|---|---|---|
| Q1 | ANSWERED 2026-09-25, TEMPORARY until healing spells: share 25 %, Priest self 50 % of that, range 16 blocks, 10 HP per hit, 10 HP per second per player, party only | current numbers, then replace |
| Q2 | ANSWERED 2026-09-25: Divinity XP 0.2 per HP healed on others, **0.25 per HP healed on yourself**, max 300 XP a minute | 0.4.5 still pays 0 for a self-heal |
| Q3 | ANSWERED 2026-09-25: the Priest heals themself, and that heal pays 0.25 XP per HP | was: yes, at 50 % of a member's heal, no XP |
| Q4 | ANSWERED 2026-09-25: kit straight into the hotbar | was: storage first. 0.1.6 still uses storage |
| Q5 | ANSWERED 2026-09-25: the kit lands immediately when the player selects or changes class | was: ~31 s. 0.1.6 still waits |
| Q6 | Vanilla max Mana is 0: wand casts (25), spellbook casts (100) and the Mage staff summon (50) never work for a fresh character. Give Priests/Mages base Mana (a class MAX Mana modifier like SkyyAccessories' `skyyacc_mana`)? | not in this round; melee swings heal and deal damage |
| Q7 | No wand/spellbook is craftable or drops (except Rekindle Embers). Add recipes / drops now, or wait for custom Priest weapons? | wait; the kit wand never breaks (no durability); admins can edit kits or use /classadmin kit |
| Q8 | ANSWERED 2026-09-25: the Healing Totem is Priest only | was: anyone. 0.1.6 still leaves deployables unassigned |
| Q9 | ANSWERED 2026-09-25: Root wands, Stoneskin wands, and Rekindle Embers count as Priest weapons | confirms the existing yes; no behavior change |
| Q10 | ANSWERED 2026-09-25: heal chat lines ON, at most one every 10 s | was: every 5 s. Players can still switch theirs off |
| Q11 | Heals reach party members only, not other players nearby? | party only |
| Q12 | Arrows in the Archer kit | 64 |
| Q13 | Kit overflow as a claim (/class kit) rather than dropped at the feet | claim |
| Q14 | A kit again when an admin changes a profile's class (/profileadmin setclass)? | no; /classadmin kit by hand |
| Q15 | Shaman's placeholder icon: Slowness Totem (a statue icon) instead of the wand | changed |

---

## 9. Follow-ups outside these three mods (not part of this build; for the coordinator)

- **F1 SkyyGuilds:** `xpSkills` default lacks Fury and Divinity, so Berserker/Priest XP adds no guild XP. An admin can add ",Fury,Divinity"
  today (Server Setup -> Guilds -> Skills that count; its check asks "not a SkyySkills skill name - save anyway?" because its known list is
  old; saving is correct with SkyySkills 0.4.4). Next SkyyGuilds version: add both to the default and to its known list.
- **F2 SkyyMenu:** its menu entry description still says "Classes: Archer, Warrior or Mage (Assassin and Shaman later)" - update at the next
  SkyyMenu version (after 0.3.1).
- **F3 Docs after the build:** HANDOFF section 3 + running log, TEST-CHECKLIST (section 7 here), DESIGN-STATUS, SkyyClasses-Plan / SkyySkills-Plan
  status lines, OPEN-QUESTIONS (section 8), tools/PROFILES-CONTRACT.md (add `class:fn:kitnew` and the kit rules to the SkyyClasses per-mod note).
- **F4 deploy_set.py:** pin the three versions together and add the SkyySkills 0.4.3 no-downgrade note.
